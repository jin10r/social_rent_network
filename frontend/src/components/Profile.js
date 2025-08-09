import React, { useState, useEffect, useCallback } from 'react';
import { Camera, MapPin, DollarSign, Calendar, Edit3, Search, CheckCircle, AlertCircle } from 'lucide-react';
import { useUser } from '../context/UserContext';
import { useTelegram } from '../hooks/useTelegram';
import { userAPI, metroAPI } from '../services/api_new';

// Простая проверка Telegram WebApp
const checkTelegramWebApp = () => {
  const webApp = window.Telegram?.WebApp;
  return {
    isAvailable: !!webApp,
    hasInitData: !!(webApp?.initData),
    hasUser: !!(webApp?.initDataUnsafe?.user),
    initDataLength: webApp?.initData?.length || 0,
    user: webApp?.initDataUnsafe?.user || null
  };
};

const Profile = () => {
  const { currentUser, setCurrentUser } = useUser();
  const { showAlert, hapticFeedback } = useTelegram();
  const [editing, setEditing] = useState(false);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [authStatus, setAuthStatus] = useState(null);
  const [metroStations, setMetroStations] = useState([]);
  const [metroQuery, setMetroQuery] = useState('');
  const [showMetroSuggestions, setShowMetroSuggestions] = useState(false);
  const [filteredStations, setFilteredStations] = useState([]);
  const [profile, setProfile] = useState({
    first_name: '',
    last_name: '',
    age: '',
    bio: '',
    price_min: '',
    price_max: '',
    metro_station: '',
    search_radius: '1000'
  });

  // Проверка статуса Telegram WebApp (одноразово, без интервалов)
  useEffect(() => {
    setAuthStatus(checkTelegramWebApp());
  }, []);

  const loadProfile = useCallback(async () => {
    try {
      setLoading(true);
      const response = await userAPI.getCurrentUser();
      const userData = response.data;
      setProfile({
        first_name: userData.first_name || '',
        last_name: userData.last_name || '',
        age: userData.age || '',
        bio: userData.bio || '',
        price_min: userData.price_min || '',
        price_max: userData.price_max || '',
        metro_station: userData.metro_station || '',
        search_radius: userData.search_radius || '1000',
        photo_url: userData.photo_url
      });
      setMetroQuery(userData.metro_station || '');
      setCurrentUser(userData);
    } catch (error) {
      if (error.response?.status === 404) {
        const tgUser = window.Telegram?.WebApp?.initDataUnsafe?.user;
        if (tgUser) {
          setProfile(prev => ({
            ...prev,
            first_name: tgUser.first_name || '',
            last_name: tgUser.last_name || '',
            photo_url: tgUser.photo_url
          }));
        }
      } else if (error.code === 'ERR_NETWORK' || error.message === 'Network Error') {
        showAlert('Ошибка сети. Проверьте подключение к интернету и попробуйте снова.');
      } else {
        const errorMessage = error.response?.data?.detail || error.message || 'Неизвестная ошибка';
        showAlert(`Ошибка загрузки профиля: ${errorMessage}`);
      }
    } finally {
      setLoading(false);
    }
  }, [setCurrentUser, showAlert]);

  const loadMetroStations = useCallback(async () => {
    try {
      const response = await metroAPI.getStations();
      setMetroStations(response.data || []);
    } catch (error) {
      console.error('Error loading metro stations:', error);
    }
  }, []);

  useEffect(() => {
    loadProfile();
    loadMetroStations();
  }, [loadProfile, loadMetroStations]);

  useEffect(() => {
    if (currentUser) {
      setProfile(prev => ({
        ...prev,
        first_name: currentUser.first_name || '',
        last_name: currentUser.last_name || '',
        photo_url: currentUser.photo_url
      }));
    }
  }, [currentUser]);

  useEffect(() => {
    // Фильтрация станций метро
    if (metroQuery.trim() === '') {
      setFilteredStations(metroStations.map(name => ({ name })).slice(0, 10));
    } else {
      const filtered = metroStations.filter(stationName =>
        stationName.toLowerCase().includes(metroQuery.toLowerCase())
      ).slice(0, 10);
      setFilteredStations(filtered.map(name => ({ name })));
    }
  }, [metroQuery, metroStations]);

  const handleSave = async () => {
    // Блокируем сохранение, если нет Telegram initData (вебапп не дал токен)
    const hasInitData = !!window.Telegram?.WebApp?.initData;
    if (!hasInitData) {
      showAlert('Ошибка аутентификации. Откройте приложение через Telegram и попробуйте снова.');
      return;
    }

    // Валидация
    if (!profile.first_name || !profile.first_name.trim()) {
      showAlert('Пожалуйста, введите имя');
      return;
    }
    if (!profile.age) {
      showAlert('Пожалуйста, укажите возраст');
      return;
    }
    if (!profile.metro_station) {
      showAlert('Пожалуйста, выберите станцию метро');
      return;
    }

    // Проверяем, что выбранная станция есть в списке
    if (!metroStations.includes(profile.metro_station)) {
      showAlert('Пожалуйста, выберите станцию метро из списка');
      return;
    }

    setSaving(true);
    hapticFeedback('impact', 'light');

    try {
      const userData = {
        first_name: profile.first_name.trim(),
        last_name: profile.last_name?.trim() || '',
        age: parseInt(profile.age, 10),
        bio: profile.bio?.trim() || '',
        price_min: profile.price_min ? parseInt(profile.price_min, 10) : null,
        price_max: profile.price_max ? parseInt(profile.price_max, 10) : null,
        metro_station: profile.metro_station.trim(),
        search_radius: profile.search_radius ? parseInt(profile.search_radius, 10) : null,
      };

      // Защита от «is not a function»: имеем несколько стратегий сохранения
      const hasUpdateProfile = userAPI && typeof userAPI.updateProfile === 'function';
      const hasCreateOrUpdate = userAPI && typeof userAPI.createOrUpdateUser === 'function';
      let response;
      if (hasUpdateProfile) {
        response = await userAPI.updateProfile(userData);
      } else if (hasCreateOrUpdate) {
        response = await userAPI.createOrUpdateUser(userData);
      } else if (typeof userAPI.updateUser === 'function') {
        // Последний резервный (несекьюрный) путь, если обе функции недоступны
        response = await userAPI.updateUser(userData);
      } else {
        throw new Error('Нет доступного метода сохранения профиля в userAPI');
      }

      setCurrentUser(response.data);
      setEditing(false);
      setShowMetroSuggestions(false);
      showAlert('✅ Профиль успешно сохранен!');
      hapticFeedback('notification', 'success');

      if (window.Telegram?.WebApp?.sendData) {
        window.Telegram.WebApp.sendData(JSON.stringify({
          type: 'profile_updated',
          user: response.data,
        }));
      }
    } catch (error) {
      let errorMessage = 'Ошибка при сохранении профиля';
      if (error.response?.status === 401 || error.response?.status === 403) {
        errorMessage = 'Ошибка авторизации. Пожалуйста, перезапустите приложение через Telegram.';
      } else if (error.response?.status === 400) {
        errorMessage = `Неверные данные: ${error.response.data.detail || 'проверьте поля'}`;
      } else if (error.code === 'ERR_NETWORK' || error.message === 'Network Error') {
        errorMessage = 'Ошибка сети. Проверьте подключение к интернету и попробуйте снова.';
      } else if (error.response?.data?.detail) {
        errorMessage = error.response.data.detail;
      } else if (error.message) {
        errorMessage = `Ошибка: ${error.message}`;
      }
      showAlert(errorMessage);
      hapticFeedback('notification', 'error');
    } finally {
      setSaving(false);
    }
  };

  const handleMetroStationSelect = (station) => {
    const stationName = typeof station === 'string' ? station : station.name;
    setProfile(prev => ({ ...prev, metro_station: stationName }));
    setMetroQuery(stationName);
    setShowMetroSuggestions(false);
    hapticFeedback('selection');
    
    // Показываем уведомление о выборе
    showAlert(`✅ Выбрана станция: ${stationName}`);
  };

  const handleMetroInputChange = (e) => {
    const value = e.target.value;
    setMetroQuery(value);
    // Не устанавливаем metro_station сразу, только при выборе из списка
    setShowMetroSuggestions(true);
  };

  if (loading) {
    return (
      <div className="tg-container flex items-center justify-center" style={{ height: '100vh' }}>
        <div className="loading-spinner"></div>
        <div style={{ marginTop: '20px', textAlign: 'center' }}>
          <div>Загрузка профиля...</div>
          {authStatus && (
            <div style={{ fontSize: '12px', color: 'var(--tg-theme-hint-color)', marginTop: '10px' }}>
              <div>WebApp: {authStatus.isAvailable ? '✅' : '❌'}</div>
              <div>InitData: {authStatus.hasInitData ? '✅' : '❌'}</div>
              <div>User: {authStatus.hasUser ? '✅' : '❌'}</div>
            </div>
          )}
        </div>
      </div>
    );
  }

  return (
    <div className="tg-container">
      <div className="tg-header">
        <div className="flex justify-between items-center">
          <h1>Мой профиль</h1>
          <div className="flex items-center gap-2">
            {authStatus && (
              <div style={{ fontSize: '12px' }}>
                {authStatus.hasInitData ? (
                  <CheckCircle size={16} color="green" />
                ) : (
                  <AlertCircle size={16} color="orange" />
                )}
              </div>
            )}
            <button
              className={`tg-button ${editing ? 'tg-button-secondary' : ''}`}
              style={{ width: 'auto', minHeight: 'auto', padding: '8px 16px', fontSize: '14px' }}
              onClick={() => {
                setEditing(!editing);
                if (editing) setShowMetroSuggestions(false);
                hapticFeedback('impact', 'light');
              }}
            >
              <Edit3 size={16} />
              <span style={{ marginLeft: '8px' }}>{editing ? 'Отмена' : 'Редактировать'}</span>
            </button>
          </div>
        </div>
      </div>

      <div className="tg-content" style={{ paddingBottom: '80px' }}>
        {/* Profile Photo */}
        <div className="tg-section">
          <div className="p-5 text-center">
            <div className="profile-image-upload">
              {profile.photo_url ? (
                <img src={profile.photo_url} alt="Profile" className="tg-avatar" style={{ width: '100px', height: '100px', fontSize: '40px' }} />
              ) : (
                <div className="tg-avatar" style={{ width: '100px', height: '100px', fontSize: '40px' }}>
                  {profile.first_name ? profile.first_name[0].toUpperCase() : '👤'}
                </div>
              )}
              {editing && (
                <div className="upload-overlay">
                  <Camera size={24} color="white" />
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Basic Info */}
        <div className="tg-section">
          <div className="tg-section-header">Основная информация</div>
          
          <div className="tg-list-item">
            <div className="mb-2">
              <label className="tg-text-hint">Имя *</label>
            </div>
            {editing ? (
              <input
                className="tg-input"
                type="text"
                value={profile.first_name}
                onChange={(e) => setProfile(prev => ({ ...prev, first_name: e.target.value }))}
                placeholder="Введите ваше имя"
                autoComplete="given-name"
              />
            ) : (
              <div>{profile.first_name || 'Не указано'}</div>
            )}
          </div>

          <div className="tg-list-item">
            <div className="mb-2">
              <label className="tg-text-hint">Фамилия</label>
            </div>
            {editing ? (
              <input
                className="tg-input"
                type="text"
                value={profile.last_name}
                onChange={(e) => setProfile(prev => ({ ...prev, last_name: e.target.value }))}
                placeholder="Введите вашу фамилию"
                autoComplete="family-name"
              />
            ) : (
              <div>{profile.last_name || 'Не указано'}</div>
            )}
          </div>

          <div className="tg-list-item">
            <div className="mb-2 flex items-center gap-2">
              <Calendar size={16} />
              <label className="tg-text-hint">Возраст *</label>
            </div>
            {editing ? (
              <input
                className="tg-input"
                type="number"
                min="18"
                max="100"
                value={profile.age}
                onChange={(e) => setProfile(prev => ({ ...prev, age: e.target.value }))}
                placeholder="Введите ваш возраст"
              />
            ) : (
              <div>{profile.age ? `${profile.age} лет` : 'Не указано'}</div>
            )}
          </div>

          <div className="tg-list-item">
            <div className="mb-2">
              <label className="tg-text-hint">О себе</label>
            </div>
            {editing ? (
              <textarea
                className="tg-textarea"
                value={profile.bio}
                onChange={(e) => setProfile(prev => ({ ...prev, bio: e.target.value }))}
                placeholder="Расскажите о себе..."
                rows="3"
              />
            ) : (
              <div className="tg-text-hint" style={{ lineHeight: '1.4' }}>
                {profile.bio || 'Не указано'}
              </div>
            )}
          </div>
        </div>

        {/* Search Preferences */}
        <div className="tg-section">
          <div className="tg-section-header">Предпочтения по жилью</div>
          
          <div className="tg-list-item">
            <div className="mb-2 flex items-center gap-2">
              <DollarSign size={16} />
              <label className="tg-text-hint">Бюджет (₽/месяц)</label>
            </div>
            <div className="flex gap-2">
              {editing ? (
                <>
                  <input
                    className="tg-input"
                    type="number"
                    min="0"
                    value={profile.price_min}
                    onChange={(e) => setProfile(prev => ({ ...prev, price_min: e.target.value }))}
                    placeholder="От"
                  />
                  <input
                    className="tg-input"
                    type="number"
                    min="0"
                    value={profile.price_max}
                    onChange={(e) => setProfile(prev => ({ ...prev, price_max: e.target.value }))}
                    placeholder="До"
                  />
                </>
              ) : (
                <div>
                  {profile.price_min || profile.price_max ? (
                    `${profile.price_min ? profile.price_min.toLocaleString() : '0'} - ${profile.price_max ? profile.price_max.toLocaleString() : '∞'} ₽`
                  ) : (
                    'Не указано'
                  )}
                </div>
              )}
            </div>
          </div>

          <div className="tg-list-item" style={{ position: 'relative' }}>
            <div className="mb-2 flex items-center gap-2">
              <MapPin size={16} />
              <label className="tg-text-hint">Станция метро *</label>
            </div>
            {editing ? (
              <>
                <div style={{ position: 'relative' }}>
                  <input
                    className={`tg-input ${profile.metro_station && metroStations.includes(profile.metro_station) ? '' : 'border-red-300'}`}
                    type="text"
                    value={metroQuery}
                    onChange={handleMetroInputChange}
                    onFocus={() => setShowMetroSuggestions(true)}
                    onBlur={() => {
                      // Закрываем список через небольшую задержку, чтобы успеть кликнуть
                      setTimeout(() => setShowMetroSuggestions(false), 200);
                    }}
                    placeholder="Выберите станцию из списка..."
                    autoComplete="off"
                  />
                  <Search 
                    size={16} 
                    style={{ 
                      position: 'absolute', 
                      right: '12px', 
                      top: '50%', 
                      transform: 'translateY(-50%)', 
                      color: '#999' 
                    }} 
                  />
                </div>
                
                {/* Показываем текущую выбранную станцию */}
                {profile.metro_station && (
                  <div style={{ 
                    marginTop: '8px', 
                    padding: '8px 12px', 
                    backgroundColor: 'var(--tg-theme-section-bg-color, #f5f5f5)', 
                    borderRadius: '6px',
                    fontSize: '14px',
                    color: 'var(--tg-theme-text-color, #000)',
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'center'
                  }}>
                    <div>
                      <strong>Выбрано:</strong> {profile.metro_station}
                    </div>
                    <button
                      onClick={() => {
                        setProfile(prev => ({ ...prev, metro_station: '' }));
                        setMetroQuery('');
                        showAlert('Станция метро очищена');
                      }}
                      style={{
                        background: 'none',
                        border: 'none',
                        color: 'var(--tg-theme-destructive-text-color, #dc3545)',
                        cursor: 'pointer',
                        fontSize: '12px',
                        padding: '4px 8px',
                        borderRadius: '4px'
                      }}
                    >
                      Очистить
                    </button>
                  </div>
                )}
                
                {/* Предупреждение если станция не выбрана из списка */}
                {metroQuery && !metroStations.includes(metroQuery) && (
                  <div style={{ 
                    marginTop: '8px', 
                    padding: '8px 12px', 
                    backgroundColor: '#fff3cd', 
                    border: '1px solid #ffeaa7',
                    borderRadius: '6px',
                    fontSize: '14px',
                    color: '#856404'
                  }}>
                    ⚠️ Выберите станцию из списка ниже
                  </div>
                )}
                
                {showMetroSuggestions && filteredStations.length > 0 && (
                  <div 
                    style={{
                      position: 'absolute',
                      top: '100%',
                      left: '0',
                      right: '0',
                      backgroundColor: 'var(--tg-theme-bg-color, #ffffff)',
                      border: '1px solid var(--tg-theme-hint-color, #ccc)',
                      borderRadius: '8px',
                      zIndex: 1000,
                      maxHeight: '200px',
                      overflowY: 'auto',
                      boxShadow: '0 4px 12px rgba(0,0,0,0.1)'
                    }}
                  >
                    <div style={{
                      padding: '8px 16px',
                      fontSize: '12px',
                      color: 'var(--tg-theme-hint-color, #999)',
                      borderBottom: '1px solid var(--tg-theme-hint-color, #eee)',
                      backgroundColor: 'var(--tg-theme-section-bg-color, #f5f5f5)'
                    }}>
                      Выберите станцию из списка:
                    </div>
                    {filteredStations.map((station, index) => (
                      <div
                        key={index}
                        style={{
                          padding: '12px 16px',
                          cursor: 'pointer',
                          borderBottom: index < filteredStations.length - 1 ? '1px solid var(--tg-theme-hint-color, #eee)' : 'none',
                          backgroundColor: 'transparent'
                        }}
                        onMouseEnter={(e) => {
                          e.target.style.backgroundColor = 'var(--tg-theme-section-bg-color, #f5f5f5)';
                        }}
                        onMouseLeave={(e) => {
                          e.target.style.backgroundColor = 'transparent';
                        }}
                        onClick={() => handleMetroStationSelect(station)}
                      >
                        <div style={{ fontWeight: '500' }}>{station.name || station}</div>
                      </div>
                    ))}
                  </div>
                )}
              </>
            ) : (
              <div>
                {profile.metro_station ? (
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <span>{profile.metro_station}</span>
                    {metroStations.includes(profile.metro_station) && (
                      <span style={{ 
                        fontSize: '12px', 
                        backgroundColor: 'var(--tg-theme-button-color, #007bff)',
                        color: 'white',
                        padding: '2px 6px',
                        borderRadius: '4px'
                      }}>
                        ✓
                      </span>
                    )}
                  </div>
                ) : (
                  'Не указано'
                )}
              </div>
            )}
          </div>

          <div className="tg-list-item">
            <div className="mb-2">
              <label className="tg-text-hint">
                Радиус поиска: {Math.round(profile.search_radius / 1000)} км
              </label>
            </div>
            {editing ? (
              <input
                className="tg-input"
                type="range"
                min="500"
                max="10000"
                step="500"
                value={profile.search_radius}
                onChange={(e) => setProfile(prev => ({ ...prev, search_radius: e.target.value }))}
              />
            ) : (
              <div>{Math.round(profile.search_radius / 1000)} км</div>
            )}
          </div>
        </div>

        {editing && (
          <div className="p-5">
            <button className="tg-button" onClick={handleSave} disabled={saving}>
              {saving ? 'Сохранение...' : 'Сохранить профиль'}
            </button>
          </div>
        )}
      </div>
    </div>
  );
};

export default Profile;