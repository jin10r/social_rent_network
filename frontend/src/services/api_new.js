import axios from 'axios';

// Prefer environment variable, but safely fallback to '/api' so requests go through nginx proxy
// This ensures routes like '/users/secure' are proxied to backend as '/api/users/secure'
const API_BASE_URL = process.env.REACT_APP_BACKEND_URL || '/api';

// Axios instance
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: { 'Content-Type': 'application/json' },
});

// Get Telegram WebApp token (non-blocking)
// IMPORTANT: Send header ONLY when real initData is present; do not fabricate tokens
const getTelegramAuthToken = () => {
  try {
    if (window.Telegram?.WebApp?.initData) {
      const initData = window.Telegram.WebApp.initData;
      return `Bearer ${initData}`;
    }
  } catch (e) {
    // eslint-disable-next-line no-console
    console.warn('Failed to read Telegram WebApp data');
  }
  return null;
};

// Non-blocking wait for WebApp
const waitForTelegramWebApp = () => new Promise((resolve) => {
  if (window.Telegram?.WebApp) return resolve();
  const id = setInterval(() => {
    if (window.Telegram?.WebApp) {
      clearInterval(id);
      resolve();
    }
  }, 100);
  setTimeout(() => { clearInterval(id); resolve(); }, 5000);
});

waitForTelegramWebApp();

// Attach Authorization header when available
api.interceptors.request.use(
  (config) => {
    const token = getTelegramAuthToken();
    if (token) config.headers.Authorization = token;
    return config;
  },
  (error) => Promise.reject(error)
);

api.interceptors.response.use(
  (response) => response,
  (error) => {
    return Promise.reject(error);
  }
);

// NOTE: Since baseURL points to the "/api" gateway, all paths below MUST be without leading "/api"
export const metroAPI = {
  getStations: () => api.get('/metro/stations'),
  searchStations: (query) => api.get('/metro/search', { params: { query } }),
  getStationInfo: (stationName) => api.get(`/metro/station/${encodeURIComponent(stationName)}`),
};

export const userAPI = {
  createOrUpdateUser: async (userData) => api.post('/users/secure', userData),
  getCurrentUser: async () => api.get('/users/me/secure'),
  updateProfile: async (userData) => api.put('/users/profile/secure', userData),
  // legacy (unused on this screen):
  createUser: (userData) => api.post('/users/', userData),
  updateUser: (userData) => api.put('/users/profile', userData),
  getPotentialMatches: (limit = 10) => api.get('/users/potential-matches', { params: { limit } }),
  likeUser: (userId) => api.post(`/users/${userId}/like`),
  getMatches: () => api.get('/users/matches'),
  getUserLikedListings: (userId) => api.get(`/users/${userId}/liked-listings`),
};

export const listingAPI = {
  searchListings: (params) => api.get('/listings/', { params }),
  getUserListings: () => api.get('/listings/search'),
  likeListing: (listingId) => api.post(`/listings/${listingId}/like`),
  getLikedListings: () => api.get('/listings/liked'),
};

export const checkTelegramWebApp = () => ({
  isAvailable: !!window.Telegram?.WebApp,
  hasInitData: !!(window.Telegram?.WebApp?.initData),
  hasUser: !!(window.Telegram?.WebApp?.initDataUnsafe?.user),
  initDataLength: window.Telegram?.WebApp?.initData?.length || 0,
  user: window.Telegram?.WebApp?.initDataUnsafe?.user || null,
});

export default api;