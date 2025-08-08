import React, { useState, useEffect } from 'react';
import { MessageCircle, MapPin, Calendar, Heart, DollarSign, ExternalLink, Map as MapIcon } from 'lucide-react';
import { userAPI } from '../services/api_new';
import { useTelegram } from '../hooks/useTelegram';

const Matches = () => {
  const { hapticFeedback, showAlert } = useTelegram();
  const [matches, setMatches] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedMatch, setSelectedMatch] = useState(null);
  const [likedListings, setLikedListings] = useState([]);
  const [loadingListings, setLoadingListings] = useState(false);

  useEffect(() => {
    loadMatches();
  }, []);

  const loadMatches = async () => {
    try {
      const response = await userAPI.getMatches();
      setMatches(response.data);
    } catch (error) {
      console.error('Error loading matches:', error);
      showAlert('Ошибка при загрузке матчей');
    }
    setLoading(false);
  };

  const handleMatchClick = async (match) => {
    hapticFeedback('selection');
    setSelectedMatch(match);
    setLoadingListings(true);

    try {
      const response = await userAPI.getUserLikedListings(match.user.id);
      setLikedListings(response.data);
    } catch (error) {
      console.error('Error loading user listings:', error);
      setLikedListings([]);
    }
    setLoadingListings(false);
  };

  const backToMatches = () => {
    setSelectedMatch(null);
    setLikedListings([]);
  };

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('ru-RU', { day: 'numeric', month: 'short', hour: '2-digit', minute: '2-digit' });
  };

  if (loading) {
    return (
      <div className="tg-container flex items-center justify-center" style={{ height: '100vh' }}>
        <div className="loading-spinner"></div>
      </div>
    );
  }

  // Дальнейшая разметка оставлена как была
  return (
    <div className="tg-container">
      <div className="tg-header"><h1>Ваши матчи</h1></div>
      <div className="tg-content" style={{ paddingBottom: '80px' }}>
        {matches.length === 0 ? (
          <div className="text-center p-5">
            <MessageCircle size={64} className="tg-text-hint" style={{ margin: '0 auto 16px' }} />
            <h2 className="mb-2">У вас пока нет матчей</h2>
            <p className="tg-text-hint mb-4">Лайкайте профили в разделе "Поиск"</p>
            <button className="tg-button" onClick={() => window.location.href = '/matching'}>Начать поиск</button>
          </div>
        ) : (
          <div className="tg-section">
            {matches.map((match) => (
              <div key={match.id} className="tg-list-item" onClick={() => handleMatchClick(match)}>
                <div className="flex items-center gap-3">
                  {match.user.photo_url ? (
                    <img src={match.user.photo_url} alt="Profile" className="tg-avatar" />
                  ) : (
                    <div className="tg-avatar">{match.user.first_name ? match.user.first_name[0].toUpperCase() : '👤'}</div>
                  )}
                  <div className="flex-1">
                    <div className="flex items-center justify-between mb-1">
                      <div className="font-semibold">{match.user.first_name} {match.user.last_name || ''}</div>
                      <div className="tg-text-hint text-sm">{formatDate(match.created_at)}</div>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default Matches;