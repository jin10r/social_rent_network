import axios from 'axios';

// IMPORTANT: Use ONLY environment variable. No hardcoded fallbacks.
// REACT_APP_BACKEND_URL is configured by the platform and already points to the backend with the /api prefix
const API_BASE_URL = process.env.REACT_APP_BACKEND_URL;

if (!API_BASE_URL) {
  // Fail fast in console to surface misconfiguration in CI/dev
  // Do NOT fallback to localhost to avoid CORS and routing issues in Kubernetes
  // eslint-disable-next-line no-console
  console.error('REACT_APP_BACKEND_URL is not defined. Please set it in frontend/.env');
}

// Axios instance
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: { 'Content-Type': 'application/json' },
});

// Get Telegram WebApp token (non-blocking)
const getTelegramAuthToken = () => {
  try {
    if (window.Telegram?.WebApp?.initData) {
      const initData = window.Telegram.WebApp.initData;
      return `Bearer ${initData}`;
    }
    const user = window.Telegram?.WebApp?.initDataUnsafe?.user;
    if (user) {
      const mockInitData = `user=${encodeURIComponent(JSON.stringify(user))}&auth_date=${Math.floor(Date.now() / 1000)}`;
      return `Bearer ${mockInitData}`;
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

// NOTE: Since baseURL already points to the "/api" gateway, all paths below MUST be without leading "/api"
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