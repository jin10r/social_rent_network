import axios from 'axios';

// Use relative '/api' by default so all calls go through nginx proxy
const API_BASE_URL = process.env.REACT_APP_BACKEND_URL || '/api';

// Create axios instance
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Build proper Telegram WebApp Bearer token (secure mode)
const getTelegramAuthToken = () => {
  // Prefer real initData from Telegram WebApp
  if (window.Telegram?.WebApp?.initData) {
    return `Bearer ${window.Telegram.WebApp.initData}`;
  }
  // Fallbacks for development
  const user = window.Telegram?.WebApp?.initDataUnsafe?.user;
  if (user) {
    const mockInitData = `user=${encodeURIComponent(JSON.stringify(user))}&auth_date=${Math.floor(Date.now() / 1000)}`;
    return `Bearer ${mockInitData}`;
  }
  // Legacy local dev JSON fallback (not secure, but helps CI/dev)
  return `Bearer ${JSON.stringify({
    id: 123456789,
    first_name: 'Test',
    last_name: 'User',
    username: 'testuser'
  })}`;
};

// Add auth header to requests
api.interceptors.request.use(
  (config) => {
    const token = getTelegramAuthToken();
    if (token) {
      config.headers.Authorization = token;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      console.error('Unauthorized access');
    }
    return Promise.reject(error);
  }
);

// Metro stations API
export const metroAPI = {
  getStations: () => api.get('/metro/stations'),
  searchStations: (query) => api.get('/metro/search', { params: { query } }),
  getStationInfo: (stationName) => api.get(`/metro/station/${encodeURIComponent(stationName)}`),
};

// User API (add secure endpoints compatibility)
export const userAPI = {
  // Create or update user (secure)
  createOrUpdateUser: (userData) => api.post('/users/secure', userData),

  // Get current user (secure)
  getCurrentUser: () => api.get('/users/me/secure'),

  // Update user profile (secure) — this fixes "updateProfile is not a function"
  updateProfile: (userData) => api.put('/users/profile/secure', userData),

  // Backward-compatible older endpoints (still available if needed)
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

export default api;