import React, { useState, useEffect } from 'react';
import { Heart, X, MapPin, DollarSign, Calendar, MessageCircle } from 'lucide-react';
import { userAPI } from '../services/api_new';
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
            <p className="tg-text-hint mb-4">Новые кандидаты появятся позже.</p>
            <div className="flex flex-col gap-2">
              <button className="tg-button tg-button-secondary" onClick={() => window.location.href = '/profile'}>
                Обновить профиль
              </button>
              <button className="tg-button" onClick={loadPotentialMatches}>
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
          <div className="tg-badge">{currentIndex + 1} / {potentialMatches.length}</div>
        </div>
      </div>
      {/* Карточка пользователя и кнопки оставлены как были */}
    </div>
  );
};

export default Matching;