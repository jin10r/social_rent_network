import React, { useState, useEffect } from 'react';
import { MapContainer, TileLayer, Marker, Popup, Circle } from 'react-leaflet';
import { MapPin, Home, DollarSign, Filter, RefreshCw, Users } from 'lucide-react';
import { listingAPI, userAPI } from '../services/api_new';
import { useUser } from '../context/UserContext';
import { useTelegram } from '../hooks/useTelegram';
import 'leaflet/dist/leaflet.css';

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
  const [searchRadius, setSearchRadius] = useState(2000);
  const [priceFilter, setPriceFilter] = useState({ min: '', max: '' });
  const [showFilters, setShowFilters] = useState(false);
  const [matches, setMatches] = useState([]);
  const [showMatches, setShowMatches] = useState(false);

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
          setUserLocation({ lat: position.coords.latitude, lon: position.coords.longitude });
          loadListingsAtLocation(position.coords.latitude, position.coords.longitude);
        },
        (error) => {
          console.log('Could not get user location:', error);
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
    }
  };

  const loadListings = async () => {
    try {
      const response = await listingAPI.getUserListings();
      setListings(response.data);
    } catch (error) {
      console.error('Error loading listings:', error);
      try {
        const fallbackResponse = await listingAPI.searchListings({ limit: 100 });
        setListings(fallbackResponse.data);
      } catch (fallbackError) {
        console.error('Error loading map listings:', fallbackError);
        showAlert('Ошибка при загрузке объявлений на карте');
      }
    }
    setLoading(false);
  };

  const loadListingsAtLocation = async (lat, lon) => {
    try {
      const params = { lat, lon, radius: searchRadius, limit: 100 };
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
    loadMatches();
  };

  const formatPrice = (price) => price.toLocaleString('ru-RU') + ' ₽';

  return (
    <div className="tg-container">
      <div className="tg-header">
        <div className="flex justify-between items-center">
          <h1>Карта объявлений</h1>
          <div className="flex gap-2">
            <button className="tg-button tg-button-secondary" onClick={() => setShowMatches(!showMatches)} style={{ width: 'auto', minHeight: 'auto', padding: '8px 12px', fontSize: '14px', backgroundColor: showMatches ? 'var(--tg-button-color)' : undefined, color: showMatches ? 'var(--tg-button-text-color)' : undefined }}>
              <Users size={14} />
            </button>
            <button className="tg-button tg-button-secondary" onClick={() => setShowFilters(!showFilters)} style={{ width: 'auto', minHeight: 'auto', padding: '8px 12px', fontSize: '14px' }}>
              <Filter size={14} />
            </button>
            <button className="tg-button tg-button-secondary" onClick={refreshListings} style={{ width: 'auto', minHeight: 'auto', padding: '8px 12px', fontSize: '14px' }}>
              <RefreshCw size={14} />
            </button>
          </div>
        </div>
      </div>

      {/* Дальше разметка карты сохранена как была */}
      <div className="tg-content" style={{ paddingBottom: '80px' }}>
        <div className="p-4">
          <div className="map-container" style={{ height: '400px' }}>
            {userLocation ? (
              <MapContainer center={mapCenter} zoom={13} style={{ height: '100%', width: '100%' }}>
                <TileLayer attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors' url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" />
                <Marker position={[userLocation.lat, userLocation.lon]}><Popup><div><strong>📍 Ваше местоположение</strong></div></Popup></Marker>
                <Circle center={[userLocation.lat, userLocation.lon]} radius={searchRadius} pathOptions={{ fillColor: 'var(--tg-button-color)', fillOpacity: 0.1, color: 'var(--tg-button-color)', opacity: 0.3, weight: 2 }} />
                {listings.map((listing) => (
                  <Marker key={listing.id} position={[listing.lat, listing.lon]}>
                    <Popup>
                      <div style={{ minWidth: '200px' }}>
                        <h4 className="font-semibold mb-2">{listing.title}</h4>
                        <div className="flex items-center gap-2 mb-2"><DollarSign size={14} /><span className="font-semibold">{formatPrice(listing.price)}</span></div>
                      </div>
                    </Popup>
                  </Marker>
                ))}
              </MapContainer>
            ) : (
              <div className="flex items-center justify-center h-full"><div className="loading-spinner"></div></div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default Map;