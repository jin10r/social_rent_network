import React, { useState, useEffect } from 'react';
import { MapContainer, TileLayer, Marker, Popup, Circle } from 'react-leaflet';
import { MapPin, Home, DollarSign, Filter, RefreshCw, Users } from 'lucide-react';
import { listingAPI, userAPI } from '../services/api';
import { useUser } from '../context/UserContext';
import { useTelegram } from '../hooks/useTelegram';
import 'leaflet/dist/leaflet.css';

// Fix for default markers in react-leaflet
import L from 'leaflet';
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: require('leaflet/dist/images/marker-icon-2x.png'),
  iconUrl: require('leaflet/dist/images/marker-icon.png'),
  shadowUrl: require('leaflet/dist/images/marker-shadow.png'),
});

const Map = () => {
  const { currentUser } = useUser();
  const { hapticFeedback, showAlert } = useTelegram();
  const [listings, setListings] = useState([]);
  const [loading, setLoading] = useState(true);
  const [userLocation, setUserLocation] = useState(null);
  const [searchRadius, setSearchRadius] = useState(2000); // meters
  const [priceFilter, setPriceFilter] = useState({ min: '', max: '' });
  const [showFilters, setShowFilters] = useState(false);
  const [matches, setMatches] = useState([]);
  const [showMatches, setShowMatches] = useState(false);

  // Moscow center as fallback
  const moscowCenter = [55.7558, 37.6176];
  const mapCenter = userLocation ? [userLocation.lat, userLocation.lon] : moscowCenter;

  useEffect(() => {
    getUserLocation();
    loadListings();
    loadMatches();
  }, []);

  const getUserLocation = () => {
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        (position) => {
          setUserLocation({
            lat: position.coords.latitude,
            lon: position.coords.longitude
          });
          loadListingsAtLocation(position.coords.latitude, position.coords.longitude);
        },
        (error) => {
          console.log('Could not get user location:', error);
          // Use Moscow center
          setUserLocation({ lat: moscowCenter[0], lon: moscowCenter[1] });
          loadListingsAtLocation(moscowCenter[0], moscowCenter[1]);
        }
      );
    } else {
      setUserLocation({ lat: moscowCenter[0], lon: moscowCenter[1] });
      loadListingsAtLocation(moscowCenter[0], moscowCenter[1]);
    }
  };

  const loadMatches = async () => {
    try {
      const response = await userAPI.getMatches();
      setMatches(response.data);
    } catch (error) {
      console.error('Error loading matches:', error);
      // Не показываем ошибку, так как матчи не критичны для карты
    }
  };

  const loadListings = async () => {
    try {
      const response = await listingAPI.getUserListings();
      setListings(response.data);
    } catch (error) {
      console.error('Error loading listings:', error);
      // Fallback to general search
      try {
        const fallbackResponse = await listingAPI.searchListings({
          limit: 100
        });
        setListings(fallbackResponse.data);
      } catch (fallbackError) {
        showAlert('Ошибка при загрузке объявлений на карте');
      }
    }
    setLoading(false);
  };

  const loadListingsAtLocation = async (lat, lon) => {
    try {
      const params = {
        lat,
        lon,
        radius: searchRadius,
        limit: 100
      };

      if (priceFilter.min) params.price_min = parseInt(priceFilter.min);
      if (priceFilter.max) params.price_max = parseInt(priceFilter.max);

      const response = await listingAPI.searchListings(params);
      setListings(response.data);
    } catch (error) {
      console.error('Error loading listings at location:', error);
      showAlert('Ошибка при загрузке объявлений');
    }
  };

  const handleRadiusChange = (newRadius) => {
    setSearchRadius(newRadius);
    if (userLocation) {
      loadListingsAtLocation(userLocation.lat, userLocation.lon);
    }
  };

  const handlePriceFilterApply = () => {
    hapticFeedback('selection');
    if (userLocation) {
      loadListingsAtLocation(userLocation.lat, userLocation.lon);
    }
    setShowFilters(false);
  };

  const refreshListings = () => {
    hapticFeedback('impact', 'light');
    setLoading(true);
    if (userLocation) {
      loadListingsAtLocation(userLocation.lat, userLocation.lon);
    } else {
      loadListings();
    }
    loadMatches(); // Обновляем матчи тоже
  };

  const formatPrice = (price) => {
    return price.toLocaleString('ru-RU') + ' ₽';
  };

  return (
    <div className="tg-container">
      <div className="tg-header">
        <div className="flex justify-between items-center">
          <h1>Карта объявлений</h1>
          <div className="flex gap-2">
            <button
              className="tg-button tg-button-secondary"
              onClick={() => setShowMatches(!showMatches)}
              style={{ 
                width: 'auto', 
                minHeight: 'auto', 
                padding: '8px 12px',
                fontSize: '14px',
                backgroundColor: showMatches ? 'var(--tg-button-color)' : undefined,
                color: showMatches ? 'var(--tg-button-text-color)' : undefined
              }}
            >
              <Users size={14} />
            </button>
            <button
              className="tg-button tg-button-secondary"
              onClick={() => setShowFilters(!showFilters)}
              style={{ 
                width: 'auto', 
                minHeight: 'auto', 
                padding: '8px 12px',
                fontSize: '14px'
              }}
            >
              <Filter size={14} />
            </button>
            <button
              className="tg-button tg-button-secondary"
              onClick={refreshListings}
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
      </div>

      {/* Filters */}
      {showFilters && (
        <div className="tg-section">
          <div className="p-4">
            <h3 className="mb-3 font-semibold">Фильтры поиска</h3>
            
            <div className="mb-4">
              <label className="tg-text-hint mb-2 block">
                Радиус поиска: {Math.round(searchRadius / 1000)} км
              </label>
              <input
                type="range"
                min="500"
                max="10000"
                step="500"
                value={searchRadius}
                onChange={(e) => handleRadiusChange(parseInt(e.target.value))}
                className="w-full"
              />
            </div>

            <div className="mb-4">
              <label className="tg-text-hint mb-2 block">Цена (₽/месяц)</label>
              <div className="flex gap-2">
                <input
                  className="tg-input flex-1"
                  type="number"
                  placeholder="От"
                  value={priceFilter.min}
                  onChange={(e) => setPriceFilter(prev => ({ ...prev, min: e.target.value }))}
                />
                <input
                  className="tg-input flex-1"
                  type="number"
                  placeholder="До"
                  value={priceFilter.max}
                  onChange={(e) => setPriceFilter(prev => ({ ...prev, max: e.target.value }))}
                />
              </div>
            </div>

            <button
              className="tg-button"
              onClick={handlePriceFilterApply}
            >
              Применить фильтры
            </button>
          </div>
        </div>
      )}

      {/* Map */}
      <div className="tg-content" style={{ paddingBottom: '80px' }}>
        <div className="p-4">
          <div className="map-container" style={{ height: '400px' }}>
            {userLocation ? (
              <MapContainer
                center={mapCenter}
                zoom={13}
                style={{ height: '100%', width: '100%' }}
              >
                <TileLayer
                  attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
                  url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                />
                
                {/* User location */}
                <Marker position={[userLocation.lat, userLocation.lon]}>
                  <Popup>
                    <div>
                      <strong>📍 Ваше местоположение</strong>
                    </div>
                  </Popup>
                </Marker>

                {/* Search radius */}
                <Circle
                  center={[userLocation.lat, userLocation.lon]}
                  radius={searchRadius}
                  pathOptions={{
                    fillColor: 'var(--tg-button-color)',
                    fillOpacity: 0.1,
                    color: 'var(--tg-button-color)',
                    opacity: 0.3,
                    weight: 2
                  }}
                />

                {/* Matched users radii */}
                {showMatches && matches.map((match) => {
                  // Нужно получить координаты пользователя из его профиля
                  // Для демо будем использовать случайные координаты рядом с центром Москвы
                  const randomLat = 55.7558 + (Math.random() - 0.5) * 0.1;
                  const randomLon = 37.6176 + (Math.random() - 0.5) * 0.1;
                  const radius = match.user.search_radius || 2000;
                  
                  return (
                    <React.Fragment key={`match-${match.id}`}>
                      <Circle
                        center={[randomLat, randomLon]}
                        radius={radius}
                        pathOptions={{
                          fillColor: '#FF6B6B',
                          fillOpacity: 0.1,
                          color: '#FF6B6B',
                          opacity: 0.4,
                          weight: 2,
                          dashArray: '5, 5'
                        }}
                      />
                      <Marker position={[randomLat, randomLon]}>
                        <Popup>
                          <div style={{ minWidth: '200px' }}>
                            <div className="flex items-center gap-2 mb-2">
                              {match.user.photo_url ? (
                                <img
                                  src={match.user.photo_url}
                                  alt="Profile"
                                  className="tg-avatar"
                                  style={{ width: '40px', height: '40px' }}
                                />
                              ) : (
                                <div className="tg-avatar" style={{ width: '40px', height: '40px', fontSize: '18px' }}>
                                  {match.user.first_name ? match.user.first_name[0].toUpperCase() : '👤'}
                                </div>
                              )}
                              <div>
                                <h4 className="font-semibold">
                                  {match.user.first_name} {match.user.last_name || ''}
                                </h4>
                                <p className="text-sm text-gray-600">Ваш матч!</p>
                              </div>
                            </div>
                            
                            {match.user.bio && (
                              <p className="text-sm mb-2" style={{ lineHeight: '1.3' }}>
                                {match.user.bio.length > 100 
                                  ? match.user.bio.substring(0, 100) + '...'
                                  : match.user.bio
                                }
                              </p>
                            )}

                            {match.user.metro_station && (
                              <div className="text-sm mb-2">
                                🚇 {match.user.metro_station}
                              </div>
                            )}

                            <div className="text-sm mb-2">
                              📍 Радиус поиска: {Math.round(radius / 1000)} км
                            </div>

                            {(match.user.price_min || match.user.price_max) && (
                              <div className="text-sm mb-2">
                                💰 Бюджет: {match.user.price_min && match.user.price_max ? (
                                  `${match.user.price_min.toLocaleString()} - ${match.user.price_max.toLocaleString()} ₽`
                                ) : match.user.price_min ? (
                                  `от ${match.user.price_min.toLocaleString()} ₽`
                                ) : (
                                  `до ${match.user.price_max.toLocaleString()} ₽`
                                )}
                              </div>
                            )}

                            <button
                              className="tg-button w-full"
                              onClick={() => {
                                if (match.user.username) {
                                  window.open(`https://t.me/${match.user.username}`, '_blank');
                                } else {
                                  window.location.href = '/matches';
                                }
                              }}
                              style={{ fontSize: '14px', padding: '8px 12px' }}
                            >
                              💬 Связаться
                            </button>
                          </div>
                        </Popup>
                      </Marker>
                    </React.Fragment>
                  );
                })}

                {/* Listings */}
                {listings.map((listing) => (
                  <Marker
                    key={listing.id}
                    position={[listing.lat, listing.lon]}
                  >
                    <Popup>
                      <div style={{ minWidth: '200px' }}>
                        <h4 className="font-semibold mb-2">{listing.title}</h4>
                        
                        <div className="flex items-center gap-2 mb-2">
                          <DollarSign size={14} />
                          <span className="font-semibold">{formatPrice(listing.price)}</span>
                        </div>

                        {listing.description && (
                          <p className="text-sm mb-2" style={{ lineHeight: '1.3' }}>
                            {listing.description.length > 100 
                              ? listing.description.substring(0, 100) + '...'
                              : listing.description
                            }
                          </p>
                        )}

                        <div className="flex flex-wrap gap-1 mb-2">
                          {listing.rooms && (
                            <span className="bg-gray-200 px-2 py-1 rounded text-xs">
                              {listing.rooms} комн.
                            </span>
                          )}
                          {listing.area && (
                            <span className="bg-gray-200 px-2 py-1 rounded text-xs">
                              {listing.area} м²
                            </span>
                          )}
                        </div>

                        {listing.address && (
                          <div className="flex items-center gap-1 mb-2 text-sm">
                            <MapPin size={12} />
                            <span>{listing.address}</span>
                          </div>
                        )}

                        {listing.metro_station && (
                          <div className="text-sm mb-2">
                            🚇 {listing.metro_station}
                          </div>
                        )}

                        {listing.distance && (
                          <div className="text-sm text-gray-500">
                            📍 ~{Math.round(listing.distance)} км от вас
                          </div>
                        )}
                      </div>
                    </Popup>
                  </Marker>
                ))}
              </MapContainer>
            ) : (
              <div className="flex items-center justify-center h-full">
                <div className="loading-spinner"></div>
              </div>
            )}
          </div>

          {/* Map Stats */}
          <div className="mt-4 p-3 tg-card">
            <div className="flex justify-between items-center">
              <div className="flex items-center gap-2">
                <Home size={16} className="tg-text-hint" />
                <span className="tg-text-hint">Найдено объявлений:</span>
              </div>
              <span className="font-semibold">{listings.length}</span>
            </div>
            
            {showMatches && (
              <div className="flex justify-between items-center mt-2">
                <div className="flex items-center gap-2">
                  <Users size={16} className="tg-text-hint" />
                  <span className="tg-text-hint">Ваши матчи на карте:</span>
                </div>
                <span className="font-semibold">{matches.length}</span>
              </div>
            )}
            
            {userLocation && (
              <div className="flex justify-between items-center mt-2">
                <div className="flex items-center gap-2">
                  <MapPin size={16} className="tg-text-hint" />
                  <span className="tg-text-hint">Радиус поиска:</span>
                </div>
                <span className="font-semibold">{Math.round(searchRadius / 1000)} км</span>
              </div>
            )}

            {loading && (
              <div className="flex items-center justify-center mt-2">
                <div className="loading-spinner" style={{ width: '20px', height: '20px' }}></div>
                <span className="ml-2 tg-text-hint">Загрузка...</span>
              </div>
            )}
          </div>

          {showMatches && matches.length > 0 && (
            <div className="mt-4 p-3 tg-secondary-bg-color rounded">
              <p className="tg-text-hint text-sm text-center">
                💡 Красные пунктирные круги показывают радиусы поиска ваших матчей
              </p>
            </div>
          )}

          <div className="mt-4 p-3 tg-secondary-bg-color rounded">
            <p className="tg-text-hint text-sm text-center">
              💡 Нажмите на маркеры, чтобы увидеть детали объявлений {matches.length > 0 && showMatches ? 'и связаться с матчами' : ''}
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Map;