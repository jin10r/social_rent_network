import React, { useState, useEffect } from 'react';
import { MessageCircle, MapPin, Calendar, Heart, DollarSign, ExternalLink, Map as MapIcon } from 'lucide-react';
import { userAPI } from '../services/api';
import { useTelegram } from '../hooks/useTelegram';

const Matches = () => {
  const { hapticFeedback, showAlert, openTelegramLink } = useTelegram();
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

  const handleContactUser = (user) => {
    hapticFeedback('impact', 'medium');
    
    if (user.username) {
      // Открываем Telegram напрямую
      window.open(`https://t.me/${user.username}`, '_blank');
    } else {
      // Показать контактную информацию
      const contactInfo = `Свяжитесь с пользователем:\n\n👤 ${user.first_name} ${user.last_name || ''}\n${user.age ? `🎂 ${user.age} лет\n` : ''}${user.metro_station ? `🚇 ${user.metro_station}\n` : ''}${user.bio ? `💬 ${user.bio}` : ''}`;
      showAlert(contactInfo);
    }
  };

  const backToMatches = () => {
    setSelectedMatch(null);
    setLikedListings([]);
  };

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('ru-RU', {
      day: 'numeric',
      month: 'short',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  if (loading) {
    return (
      <div className="tg-container flex items-center justify-center" style={{ height: '100vh' }}>
        <div className="loading-spinner"></div>
      </div>
    );
  }

  // Viewing specific match's liked listings
  if (selectedMatch) {
    return (
      <div className="tg-container">
        <div className="tg-header">
          <div className="flex items-center gap-3">
            <button 
              className="tg-button tg-button-secondary"
              onClick={backToMatches}
              style={{ 
                width: 'auto', 
                minHeight: 'auto', 
                padding: '8px 12px',
                fontSize: '14px'
              }}
            >
              ← Назад
            </button>
            <div>
              <h1>Понравившиеся объявления</h1>
              <div className="tg-text-hint" style={{ fontSize: '14px' }}>
                {selectedMatch.user.first_name} {selectedMatch.user.last_name || ''}
              </div>
            </div>
          </div>
        </div>

        <div className="tg-content" style={{ paddingBottom: '80px' }}>
          {loadingListings ? (
            <div className="flex items-center justify-center" style={{ height: '200px' }}>
              <div className="loading-spinner"></div>
            </div>
          ) : likedListings.length === 0 ? (
            <div className="text-center p-5">
              <Heart size={64} className="tg-text-hint" style={{ margin: '0 auto 16px' }} />
              <h2 className="mb-2">Пока нет понравившихся объявлений</h2>
              <p className="tg-text-hint">
                {selectedMatch.user.first_name} еще не лайкал(а) объявления
              </p>
            </div>
          ) : (
            <div className="p-4">
              {likedListings.map((listing) => (
                <div key={listing.id} className="tg-card mb-4">
                  <div className="mb-3">
                    <h3 className="font-semibold mb-2">{listing.title}</h3>
                    <div className="flex items-center gap-2 mb-2">
                      <DollarSign size={16} className="tg-text-hint" />
                      <span className="font-semibold">{listing.price.toLocaleString()} ₽/мес</span>
                    </div>
                  </div>

                  {listing.description && (
                    <p className="tg-text-hint mb-3" style={{ lineHeight: '1.4' }}>
                      {listing.description}
                    </p>
                  )}

                  <div className="flex flex-wrap gap-2 mb-3">
                    {listing.rooms && (
                      <div className="tg-badge" style={{ fontSize: '12px' }}>
                        {listing.rooms} комн.
                      </div>
                    )}
                    {listing.area && (
                      <div className="tg-badge" style={{ fontSize: '12px' }}>
                        {listing.area} м²
                      </div>
                    )}
                    {listing.floor && listing.total_floors && (
                      <div className="tg-badge" style={{ fontSize: '12px' }}>
                        {listing.floor}/{listing.total_floors} эт.
                      </div>
                    )}
                  </div>

                  {listing.address && (
                    <div className="flex items-center gap-2 mb-2">
                      <MapPin size={14} className="tg-text-hint" />
                      <span className="tg-text-hint text-sm">{listing.address}</span>
                    </div>
                  )}

                  {listing.metro_station && (
                    <div className="flex items-center gap-2 mb-2">
                      <div className="tg-text-hint text-sm">
                        🚇 {listing.metro_station}
                        {listing.metro_distance && (
                          <span> • {Math.round(listing.metro_distance / 1000 * 10) / 10} км</span>
                        )}
                      </div>
                    </div>
                  )}

                  {listing.distance && (
                    <div className="tg-text-hint text-sm">
                      📍 ~{Math.round(listing.distance)} км от вас
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    );
  }

  // Main matches list
  return (
    <div className="tg-container">
      <div className="tg-header">
        <h1>Ваши матчи</h1>
      </div>

      <div className="tg-content" style={{ paddingBottom: '80px' }}>
        {matches.length === 0 ? (
          <div className="text-center p-5">
            <MessageCircle size={64} className="tg-text-hint" style={{ margin: '0 auto 16px' }} />
            <h2 className="mb-2">У вас пока нет матчей</h2>
            <p className="tg-text-hint mb-4">
              Лайкайте профили в разделе "Поиск", чтобы найти соседей!
            </p>
            <button 
              className="tg-button"
              onClick={() => window.location.href = '/matching'}
            >
              Начать поиск
            </button>
          </div>
        ) : (
          <div className="tg-section">
            {matches.map((match) => (
              <div
                key={match.id}
                className="tg-list-item"
                onClick={() => handleMatchClick(match)}
              >
                <div className="flex items-center gap-3">
                  {/* Avatar */}
                  {match.user.photo_url ? (
                    <img
                      src={match.user.photo_url}
                      alt="Profile"
                      className="tg-avatar"
                    />
                  ) : (
                    <div className="tg-avatar">
                      {match.user.first_name ? match.user.first_name[0].toUpperCase() : '👤'}
                    </div>
                  )}

                  {/* User Info */}
                  <div className="flex-1">
                    <div className="flex items-center justify-between mb-1">
                      <div className="font-semibold">
                        {match.user.first_name} {match.user.last_name || ''}
                      </div>
                      <div className="tg-text-hint text-sm">
                        {formatDate(match.created_at)}
                      </div>
                    </div>

                    <div className="flex items-center gap-4 text-sm tg-text-hint">
                      {match.user.age && (
                        <div className="flex items-center gap-1">
                          <Calendar size={12} />
                          {match.user.age} лет
                        </div>
                      )}
                      {match.user.metro_station && (
                        <div className="flex items-center gap-1">
                          <MapPin size={12} />
                          {match.user.metro_station}
                        </div>
                      )}
                    </div>

                    <div className="flex items-center justify-between mt-2">
                      <div className="flex gap-2">
                        <button
                          className="tg-button tg-button-secondary"
                          onClick={(e) => {
                            e.stopPropagation();
                            handleContactUser(match.user);
                          }}
                          style={{ 
                            width: 'auto', 
                            minHeight: 'auto', 
                            padding: '6px 12px',
                            fontSize: '14px'
                          }}
                        >
                          <MessageCircle size={14} />
                          <span style={{ marginLeft: '6px' }}>Написать</span>
                        </button>
                        
                        <button
                          className="tg-button tg-button-secondary"
                          onClick={(e) => {
                            e.stopPropagation();
                            hapticFeedback('selection');
                            window.location.href = '/map';
                          }}
                          style={{ 
                            width: 'auto', 
                            minHeight: 'auto', 
                            padding: '6px 12px',
                            fontSize: '14px'
                          }}
                        >
                          <MapIcon size={14} />
                          <span style={{ marginLeft: '6px' }}>На карте</span>
                        </button>
                      </div>
                      
                      <div className="flex items-center gap-1 tg-text-hint text-sm">
                        <Heart size={12} />
                        <span>Посмотреть лайки</span>
                        <ExternalLink size={12} />
                      </div>
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