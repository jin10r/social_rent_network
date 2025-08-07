import React, { useState, useEffect } from 'react';
import { Camera, MapPin, DollarSign, Calendar, Edit3, Search, CheckCircle, AlertCircle } from 'lucide-react';
import { useUser } from '../context/UserContext';
import { userAPI, metroAPI, checkTelegramWebApp } from '../services/api_new';
import { useTelegram } from '../hooks/useTelegram';

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

  // Проверка статуса Telegram WebApp
  useEffect(() => {
    const checkAuth = () => {
      const status = checkTelegramWebApp();
      setAuthStatus(status);
      console.log('Telegram WebApp Status:', status);
    };

    checkAuth();
    
    // Периодически проверяем статус
    const interval = setInterval(checkAuth, 1000);
    setTimeout(() => clearInterval(interval), 5000); // Останавливаем через 5 секунд
    
    return () => clearInterval(interval);
  }, []);

  const loadProfile = async () => {
    console.log('Loading profile...');
    try {
      const response = await userAPI.getCurrentUser();
      console.log('Profile response:', response);
      const userData = response.data;
      console.log('User data:', userData);
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
    } catch (error) {
      console.log('Profile not found, will create new one', error);
      if (currentUser) {
        setProfile(prev => ({
          ...prev,
          first_name: currentUser.first_name || '',
          last_name: currentUser.last_name || '',
          photo_url: currentUser.photo_url
        }));
      }
    } finally {
      setLoading(false);
    }
  };

  const loadMetroStations = async () => {
    try {
      const response = await metroAPI.getStations();
      setMetroStations(response.data || []);
    } catch (error) {
      console.error('Error loading metro stations:', error);
    }
  };

  useEffect(() => {
    console.log('Profile component mounted, calling loadProfile and loadMetroStations');
    loadProfile();
    loadMetroStations();
  }, []);

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
    // Filter metro stations based on query
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
    console.log('handleSave called');
    console.log('Profile data:', profile);
    if (!profile.first_name.trim()) {
      console.log('First name is empty');
      showAlert('Пожалуйста, введите имя');
      return;
    }

    if (!profile.age) {
      console.log('Age is empty');
      showAlert('Пожалуйста, заполните обязательные поля (имя и возраст)');
      return;
    }

    if (!profile.metro_station) {
      console.log('Metro station is empty');
      showAlert('Пожалуйста, выберите станцию метро');
      return;
    }

    console.log('Calling saveProfile...');
    setSaving(true);
    hapticFeedback('impact', 'light');

    try {
      const userData = {
        ...profile,
        telegram_id: currentUser?.telegram_id,
        age: parseInt(profile.age),
        price_min: profile.price_min ? parseInt(profile.price_min) : null,
        price_max: profile.price_max ? parseInt(profile.price_max) : null,
        search_radius: parseInt(profile.search_radius)
      };
      
      console.log('Sending user data:', userData);
      const response = await userAPI.updateUser(userData);
      setCurrentUser(response.data);
      setEditing(false);
      setShowMetroSuggestions(false);
      showAlert('Профиль сохранен!');
      hapticFeedback('notification', 'success');
    } catch (error) {
      console.error('Error saving profile:', error);
      console.error('Error details:', {
        message: error.message,
        status: error.response?.status,
        statusText: error.response?.statusText,
        data: error.response?.data,
        config: {
          url: error.config?.url,
          method: error.config?.method,
          data: error.config?.data
        }
      });
      showAlert('Ошибка при сохранении профиля');
      hapticFeedback('notification', 'error');
    }
    setSaving(false);
  };

  const handleMetroStationSelect = (station) => {
    const stationName = typeof station === 'string' ? station : station.name;
    setProfile(prev => ({ ...prev, metro_station: stationName }));
    setMetroQuery(stationName);
    setShowMetroSuggestions(false);
  };

  const handleMetroInputChange = (e) => {
    const value = e.target.value;
    setMetroQuery(value);
    setProfile(prev => ({ ...prev, metro_station: value }));
    setShowMetroSuggestions(true);
  };

  if (loading) {
    return (
      <div className="tg-container flex items-center justify-center" style={{ height: '100vh' }}>
        <div className="loading-spinner"></div>
      </div>
    );
  }

  return (
    <div className="tg-container">
      <div className="tg-header">
        <div className="flex justify-between items-center">
          <h1>Мой профиль</h1>
          <button
            className={`tg-button ${editing ? 'tg-button-secondary' : ''}`}
            style={{ 
              width: 'auto', 
              minHeight: 'auto', 
              padding: '8px 16px',
              fontSize: '14px'
            }}
            onClick={() => {
              console.log('Edit button clicked, editing:', !editing);
              setEditing(!editing);
              if (editing) {
                setShowMetroSuggestions(false);
              }
            }}
          >
            <Edit3 size={16} />
            <span style={{ marginLeft: '8px' }}>
              {editing ? 'Отмена' : 'Редактировать'}
            </span>
          </button>
        </div>
      </div>

      <div className="tg-content" style={{ paddingBottom: '80px' }}>
        {/* Profile Photo */}
        <div className="tg-section">
          <div className="p-5 text-center">
            <div className="profile-image-upload">
              {profile.photo_url ? (
                <img
                  src={profile.photo_url}
                  alt="Profile"
                  className="tg-avatar"
                  style={{ width: '100px', height: '100px', fontSize: '40px' }}
                />
              ) : (
                <div
                  className="tg-avatar"
                  style={{ width: '100px', height: '100px', fontSize: '40px' }}
                >
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
                    className="tg-input"
                    type="text"
                    value={metroQuery}
                    onChange={handleMetroInputChange}
                    onFocus={() => setShowMetroSuggestions(true)}
                    placeholder="Начните вводить название станции..."
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
                        {station.line && (
                          <div style={{ fontSize: '12px', color: 'var(--tg-theme-hint-color, #999)', marginTop: '2px' }}>
                            {station.line} линия
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                )}
              </>
            ) : (
              <div>{profile.metro_station || 'Не указано'}</div>
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
            <button
              className="tg-button"
              onClick={handleSave}
              disabled={saving}
            >
              {saving ? 'Сохранение...' : 'Сохранить профиль'}
            </button>
          </div>
        )}
      </div>
    </div>
  );
};

export default Profile;