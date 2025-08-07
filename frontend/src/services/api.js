import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_BACKEND_URL || 'http://localhost';

// Create axios instance
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Mock auth token for development
const getMockToken = () => {
  // Return JSON string directly (second option that backend supports)
  return JSON.stringify({
    id: 123456789,
    first_name: 'Test',
    last_name: 'User',
    username: 'testuser'
  });
};

// Get auth token from Telegram or use mock
const getAuthToken = () => {
  if (window.Telegram?.WebApp?.initData) {
    return window.Telegram.WebApp.initData;
  }
  return getMockToken();
};

// Add auth header to requests
api.interceptors.request.use(
  (config) => {
    const token = getAuthToken();
    if (token) {
      // For Telegram Web Apps, send initData directly without Bearer prefix
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
      // Handle unauthorized
      console.error('Unauthorized access');
    }
    return Promise.reject(error);
  }
);

// Metro stations API
export const metroAPI = {
  // Get all metro stations
  getStations: () => api.get('/api/metro/stations'),
  
  // Search metro stations
  searchStations: (query) => api.get('/api/metro/search', { params: { query } }),
  
  // Get station info
  getStationInfo: (stationName) => api.get(`/api/metro/station/${encodeURIComponent(stationName)}`),
};

// API functions
export const userAPI = {
  // Create or update user
  createUser: (userData) => api.post('/api/users/', userData),
  
  // Get current user
  getCurrentUser: () => api.get('/api/users/me'),
  
  // Update user profile
  updateUser: (userData) => api.put('/api/users/me', userData),
  
  // Get potential matches
  getPotentialMatches: (limit = 10) => 
    api.get('/api/users/potential-matches', { params: { limit } }),
  
  // Like a user
  likeUser: (userId) => api.post(`/api/users/${userId}/like`),
  
  // Get matches
  getMatches: () => api.get('/api/users/matches'),
  
  // Get user's liked listings
  getUserLikedListings: (userId) => 
    api.get(`/api/users/${userId}/liked-listings`),
};

export const listingAPI = {
  // Search listings
  searchListings: (params) => api.get('/api/listings/', { params }),
  
  // Get listings for current user
  getUserListings: () => api.get('/api/listings/search'),
  
  // Like a listing
  likeListing: (listingId) => api.post(`/api/listings/${listingId}/like`),
  
  // Get liked listings
  getLikedListings: () => api.get('/api/listings/liked'),
};

export default api;