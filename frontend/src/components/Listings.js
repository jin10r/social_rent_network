import React, { useState, useEffect } from 'react';
import { Heart, MapPin, DollarSign, Home, RefreshCw } from 'lucide-react';
import { listingAPI } from '../services/api_new';
import { useTelegram } from '../hooks/useTelegram';
import { useUser } from '../context/UserContext';

const Listings = () => {
  const { hapticFeedback, showAlert } = useTelegram();
  const { currentUser } = useUser();
  const [listings, setListings] = useState([]);
  const [likedListings, setLikedListings] = useState([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('search'); // 'search' | 'liked'

  useEffect(() => {
    loadListings();
    loadLikedListings();
  }, []);

  const loadListings = async () => {
    try {
      const response = await listingAPI.getUserListings();
      setListings(response.data);
    } catch (error) {
      console.error('Error loading listings:', error);
      // Fallback to general search if user listings fail
      try {
        const fallbackResponse = await listingAPI.searchListings({
          limit: 50
        });
        setListings(fallbackResponse.data);
      } catch (fallbackError) {
        console.error('Error loading listings:', fallbackError);
        console.error('Error details:', {
          message: fallbackError.message,
          status: fallbackError.response?.status,
          statusText: fallbackError.response?.statusText,
          data: fallbackError.response?.data,
          config: {
            url: fallbackError.config?.url,
            method: fallbackError.config?.method
          }
        });
        showAlert('Ошибка при загрузке объявлений');
      }
    }
    setLoading(false);
  };

  const loadLikedListings = async () => {
    try {
      const response = await listingAPI.getLikedListings();
      setLikedListings(response.data);
    } catch (error) {
      console.error('Error loading liked listings:', error);
    }
  };

  const handleLikeListing = async (listingId) => {
    hapticFeedback('impact', 'light');
    
    try {
      await listingAPI.likeListing(listingId);
      
      // Update listings to reflect like status
      setListings(prev => prev.map(listing => 
        listing.id === listingId 
          ? { ...listing, is_liked: true }
          : listing
      ));
      
      // Reload liked listings
      loadLikedListings();
      
      hapticFeedback('notification', 'success');
    } catch (error) {
      console.error('Error liking listing:', error);
      console.error('Error details:', {
        message: error.message,
        status: error.response?.status,
        statusText: error.response?.statusText,
        data: error.response?.data,
        config: {
          url: error.config?.url,
          method: error.config?.method
        }
      });
      showAlert('Ошибка при добавлении в избранное');
    }
  };

  const formatPrice = (price) => {
    return price.toLocaleString('ru-RU') + ' ₽/мес';
  };

  const ListingCard = ({ listing, showLikeButton = true }) => (
    <div className="tg-card mb-4">
      <div className="mb-3">
        <div className="flex justify-between items-start mb-2">
          <h3 className="font-semibold flex-1">{listing.title}</h3>
          {showLikeButton && !listing.is_liked && (
            <button
              className="tg-button tg-button-secondary"
              onClick={() => handleLikeListing(listing.id)}
              style={{ 
                width: 'auto', 
                minHeight: 'auto', 
                padding: '8px 12px',
                fontSize: '12px',
                marginLeft: '8px'
              }}
            >
              <Heart size={14} />
            </button>
          )}
        </div>
        
        <div className="flex items-center gap-2 mb-2">
          <DollarSign size={16} className="tg-text-hint" />
          <span className="font-semibold text-lg">{formatPrice(listing.price)}</span>
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
              <span> • {Math.round(listing.metro_distance / 1000 * 10) / 10} км от метро</span>
            )}
          </div>
        </div>
      )}

      {listing.distance && (
        <div className="tg-text-hint text-sm">
          📍 ~{Math.round(listing.distance)} км от вас
        </div>
      )}

      {listing.is_liked && (
        <div className="flex items-center gap-2 mt-3 p-2 rounded" 
             style={{ backgroundColor: 'rgba(52, 199, 89, 0.1)' }}>
          <Heart size={14} style={{ color: '#34C759' }} fill="#34C759" />
          <span className="text-sm" style={{ color: '#34C759' }}>
            В избранном
          </span>
        </div>
      )}
    </div>
  );

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
          <h1>Объявления</h1>
          <button
            className="tg-button tg-button-secondary"
            onClick={() => {
              setLoading(true);
              loadListings();
              loadLikedListings();
            }}
            style={{ 
              width: 'auto', 
              minHeight: 'auto', 
              padding: '8px 12px',
              fontSize: '14px'
            }}
          >
            <RefreshCw size={14} />
          </button>
        </div>
      </div>

      {/* Tab Navigation */}
      <div className="tg-section">
        <div className="flex">
          <button
            className={`flex-1 p-3 text-center ${activeTab === 'search' ? 'tg-button-color' : 'tg-text-hint'}`}
            onClick={() => setActiveTab('search')}
            style={{
              backgroundColor: activeTab === 'search' ? 'var(--tg-button-color)' : 'transparent',
              color: activeTab === 'search' ? 'var(--tg-button-text-color)' : 'var(--tg-text-color)',
              border: 'none',
              borderBottom: activeTab === 'search' ? '2px solid var(--tg-button-color)' : 'none'
            }}
          >
            <Home size={16} style={{ marginBottom: '4px', display: 'block', margin: '0 auto 4px' }} />
            Поиск ({listings.length})
          </button>
          <button
            className={`flex-1 p-3 text-center ${activeTab === 'liked' ? 'tg-button-color' : 'tg-text-hint'}`}
            onClick={() => setActiveTab('liked')}
            style={{
              backgroundColor: activeTab === 'liked' ? 'var(--tg-button-color)' : 'transparent',
              color: activeTab === 'liked' ? 'var(--tg-button-text-color)' : 'var(--tg-text-color)',
              border: 'none',
              borderBottom: activeTab === 'liked' ? '2px solid var(--tg-button-color)' : 'none'
            }}
          >
            <Heart size={16} style={{ marginBottom: '4px', display: 'block', margin: '0 auto 4px' }} />
            Избранное ({likedListings.length})
          </button>
        </div>
      </div>

      <div className="tg-content" style={{ paddingBottom: '80px' }}>
        {activeTab === 'search' ? (
          <div className="p-4">
            {listings.length === 0 ? (
              <div className="text-center p-5">
                <Home size={64} className="tg-text-hint" style={{ margin: '0 auto 16px' }} />
                <h2 className="mb-2">Нет доступных объявлений</h2>
                <p className="tg-text-hint mb-4">
                  Попробуйте обновить список или изменить настройки поиска в профиле
                </p>
                <button 
                  className="tg-button"
                  onClick={() => window.location.href = '/profile'}
                >
                  Настроить поиск
                </button>
              </div>
            ) : (
              <>
                <div className="mb-4 p-3 tg-secondary-bg-color rounded">
                  <p className="tg-text-hint text-sm text-center">
                    💡 Лайкайте объявления, чтобы добавить их в избранное
                  </p>
                </div>
                {listings.map((listing) => (
                  <ListingCard 
                    key={listing.id} 
                    listing={listing} 
                    showLikeButton={true}
                  />
                ))}
              </>
            )}
          </div>
        ) : (
          <div className="p-4">
            {likedListings.length === 0 ? (
              <div className="text-center p-5">
                <Heart size={64} className="tg-text-hint" style={{ margin: '0 auto 16px' }} />
                <h2 className="mb-2">Пока нет избранных объявлений</h2>
                <p className="tg-text-hint mb-4">
                  Лайкайте объявления на вкладке "Поиск", чтобы они появились здесь
                </p>
                <button 
                  className="tg-button"
                  onClick={() => setActiveTab('search')}
                >
                  Перейти к поиску
                </button>
              </div>
            ) : (
              <>
                <div className="mb-4 p-3 tg-secondary-bg-color rounded">
                  <p className="tg-text-hint text-sm text-center">
                    ❤️ Ваши избранные объявления. Матчи могут их видеть!
                  </p>
                </div>
                {likedListings.map((listing) => (
                  <ListingCard 
                    key={listing.id} 
                    listing={listing} 
                    showLikeButton={false}
                  />
                ))}
              </>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default Listings;