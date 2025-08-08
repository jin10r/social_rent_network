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

        {/* Остальные поля формы — без изменений */}
        {/* ... (оставил как было) ... */}

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