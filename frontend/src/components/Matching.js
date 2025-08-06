import React, { useState, useEffect } from 'react';
import { Heart, X, MapPin, DollarSign, Calendar, MessageCircle } from 'lucide-react';
import { userAPI } from '../services/api';
import { useTelegram } from '../hooks/useTelegram';

const Matching = () => {
  const { hapticFeedback, showAlert } = useTelegram();
  const [potentialMatches, setPotentialMatches] = useState([]);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [loading, setLoading] = useState(true);
  const [actionLoading, setActionLoading] = useState(false);

  useEffect(() => {
    loadPotentialMatches();
  }, []);

  const loadPotentialMatches = async () => {
    try {
      const response = await userAPI.getPotentialMatches(20);
      setPotentialMatches(response.data);
      setCurrentIndex(0);
    } catch (error) {
      console.error('Error loading matches:', error);
      showAlert('Ошибка при загрузке кандидатов');
    }
    setLoading(false);
  };

  const handleLike = async () => {
    if (currentIndex >= potentialMatches.length) return;
    
    setActionLoading(true);
    hapticFeedback('impact', 'light');

    const currentUser = potentialMatches[currentIndex];
    
    try {
      const response = await userAPI.likeUser(currentUser.id);
      
      if (response.data.match) {
        hapticFeedback('notification', 'success');
        showAlert(`🎉 ${response.data.message}`);
      }
      
      nextUser();
    } catch (error) {
      console.error('Error liking user:', error);
      showAlert('Ошибка при отправке лайка');
      hapticFeedback('notification', 'error');
    }
    
    setActionLoading(false);
  };

  const handlePass = () => {
    hapticFeedback('selection');
    nextUser();
  };

  const nextUser = () => {
    const newIndex = currentIndex + 1;
    setCurrentIndex(newIndex);
    
    // Load more users if running low
    if (newIndex >= potentialMatches.length - 3) {
      loadPotentialMatches();
    }
  };

  if (loading) {
    return (
      <div className="tg-container flex items-center justify-center" style={{ height: '100vh' }}>
        <div className="loading-spinner"></div>
      </div>
    );
  }

  if (potentialMatches.length === 0 || currentIndex >= potentialMatches.length) {
    return (
      <div className="tg-container">
        <div className="tg-header">
          <h1>Поиск соседей</h1>
        </div>
        
        <div className="tg-content flex flex-col items-center justify-center" style={{ height: 'calc(100vh - 140px)' }}>
          <div className="text-center p-5">
            <MessageCircle size={64} className="tg-text-hint" style={{ margin: '0 auto 16px' }} />
            <h2 className="mb-2">Пока что никого нет</h2>
            <p className="tg-text-hint mb-4">
              Новые кандидаты появятся позже. Пока что вы можете:
            </p>
            <div className="flex flex-col gap-2">
              <button 
                className="tg-button tg-button-secondary"
                onClick={() => window.location.href = '/profile'}
              >
                Обновить профиль
              </button>
              <button 
                className="tg-button"
                onClick={loadPotentialMatches}
              >
                Обновить список
              </button>
            </div>
          </div>
        </div>
      </div>
    );
  }

  const currentUser = potentialMatches[currentIndex];

  return (
    <div className="tg-container">
      <div className="tg-header">
        <div className="flex justify-between items-center">
          <h1>Поиск соседей</h1>
          <div className="tg-badge">
            {currentIndex + 1} / {potentialMatches.length}
          </div>
        </div>
      </div>

      <div className="tg-content" style={{ paddingBottom: '120px' }}>
        <div className="p-4">
          <div className="tg-card" style={{ minHeight: '500px' }}>
            {/* Profile Photo */}
            <div className="text-center mb-4">
              {currentUser.photo_url ? (
                <img
                  src={currentUser.photo_url}
                  alt="Profile"
                  className="tg-avatar"
                  style={{ 
                    width: '120px', 
                    height: '120px', 
                    fontSize: '48px',
                    margin: '0 auto'
                  }}
                />
              ) : (
                <div
                  className="tg-avatar"
                  style={{ 
                    width: '120px', 
                    height: '120px', 
                    fontSize: '48px',
                    margin: '0 auto'
                  }}
                >
                  {currentUser.first_name ? currentUser.first_name[0].toUpperCase() : '👤'}
                </div>
              )}
            </div>

            {/* Name and Age */}
            <div className="text-center mb-4">
              <h2 className="font-semibold text-xl mb-1">
                {currentUser.first_name} {currentUser.last_name || ''}
              </h2>
              {currentUser.age && (
                <div className="flex items-center justify-center gap-1 tg-text-hint">
                  <Calendar size={16} />
                  {currentUser.age} лет
                </div>
              )}
              {currentUser.distance && (
                <div className="flex items-center justify-center gap-1 tg-text-hint">
                  <MapPin size={16} />
                  ~{Math.round(currentUser.distance)} км от вас
                </div>
              )}
            </div>

            {/* Bio */}
            {currentUser.bio && (
              <div className="mb-4 p-3 tg-secondary-bg-color rounded-lg">
                <h4 className="tg-text-hint mb-2 font-semibold">О себе:</h4>
                <p style={{ lineHeight: '1.4' }}>{currentUser.bio}</p>
              </div>
            )}

            {/* Budget */}
            {(currentUser.price_min || currentUser.price_max) && (
              <div className="mb-3">
                <div className="flex items-center gap-2 mb-2">
                  <DollarSign size={16} className="tg-text-hint" />
                  <span className="tg-text-hint font-semibold">Бюджет:</span>
                </div>
                <div>
                  {currentUser.price_min && currentUser.price_max ? (
                    `${currentUser.price_min.toLocaleString()} - ${currentUser.price_max.toLocaleString()} ₽`
                  ) : currentUser.price_min ? (
                    `от ${currentUser.price_min.toLocaleString()} ₽`
                  ) : (
                    `до ${currentUser.price_max.toLocaleString()} ₽`
                  )}
                </div>
              </div>
            )}

            {/* Metro Station */}
            {currentUser.metro_station && (
              <div className="mb-3">
                <div className="flex items-center gap-2 mb-2">
                  <MapPin size={16} className="tg-text-hint" />
                  <span className="tg-text-hint font-semibold">Станция метро:</span>
                </div>
                <div>{currentUser.metro_station}</div>
              </div>
            )}

            {/* Search Radius */}
            {currentUser.search_radius && (
              <div className="mb-4">
                <div className="flex items-center gap-2 mb-2">
                  <MapPin size={16} className="tg-text-hint" />
                  <span className="tg-text-hint font-semibold">Радиус поиска:</span>
                </div>
                <div>{Math.round(currentUser.search_radius / 1000)} км</div>
              </div>
            )}
          </div>

          {/* Action Buttons */}
          <div className="flex gap-4 mt-4">
            <button
              className="tg-button tg-button-secondary flex-1"
              onClick={handlePass}
              disabled={actionLoading}
              style={{ 
                backgroundColor: 'rgba(255, 59, 48, 0.1)',
                color: '#ff3b30',
                border: '1px solid rgba(255, 59, 48, 0.3)'
              }}
            >
              <X size={20} />
              <span style={{ marginLeft: '8px' }}>Пропустить</span>
            </button>
            
            <button
              className="tg-button flex-1"
              onClick={handleLike}
              disabled={actionLoading}
              style={{
                backgroundColor: '#34C759',
                background: 'linear-gradient(135deg, #34C759 0%, #30D158 100%)'
              }}
            >
              {actionLoading ? (
                <div className="loading-spinner" style={{ width: '20px', height: '20px' }}></div>
              ) : (
                <>
                  <Heart size={20} />
                  <span style={{ marginLeft: '8px' }}>Лайк</span>
                </>
              )}
            </button>
          </div>

          <div className="text-center mt-4">
            <p className="tg-text-hint text-sm">
              💡 При взаимном лайке откроется контакт для общения
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Matching;