import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_BACKEND_URL || 'http://localhost';

// Создаем instance axios
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

/**
 * Получение правильного токена аутентификации Telegram WebApp
 */
const getTelegramAuthToken = () => {
  // Проверяем наличие Telegram WebApp
  if (window.Telegram?.WebApp?.initData) {
    const initData = window.Telegram.WebApp.initData;
    
    console.log('Using Telegram WebApp initData for authentication');
    console.log('InitData length:', initData.length);
    
    // Возвращаем initData как Bearer token
    return `Bearer ${initData}`;
  }
  
  // Fallback для режима разработки
  if (process.env.NODE_ENV === 'development') {
    console.log('Development mode: using mock authentication');
    
    // Проверяем есть ли мок данные в Telegram WebApp
    const mockUser = window.Telegram?.WebApp?.initDataUnsafe?.user;
    if (mockUser) {
      return `Bearer ${JSON.stringify(mockUser)}`;
    }
    
    // Полный fallback с мок данными
    const mockData = {
      id: 123456789,
      first_name: 'Test',
      last_name: 'User',
      username: 'testuser',
      photo_url: null
    };
    
    return `Bearer ${JSON.stringify(mockData)}`;
  }
  
  console.error('No Telegram WebApp data available and not in development mode');
  throw new Error('Authentication not available');
};

/**
 * Проверка готовности Telegram WebApp
 */
const waitForTelegramWebApp = () => {
  return new Promise((resolve) => {
    if (window.Telegram?.WebApp) {
      // WebApp уже доступен
      resolve();
      return;
    }
    
    // Ждем загрузки WebApp
    const checkInterval = setInterval(() => {
      if (window.Telegram?.WebApp) {
        clearInterval(checkInterval);
        resolve();
      }
    }, 100);
    
    // Timeout через 5 секунд
    setTimeout(() => {
      clearInterval(checkInterval);
      resolve(); // Продолжаем даже без WebApp для режима разработки
    }, 5000);
  });
};

// Инициализируем WebApp при загрузке
waitForTelegramWebApp();

// Добавляем заголовок авторизации к запросам
api.interceptors.request.use(
  async (config) => {
    try {
      const token = getTelegramAuthToken();
      if (token) {
        config.headers.Authorization = token;
        console.log('Added authorization header to request:', config.url);
      }
    } catch (error) {
      console.error('Failed to get auth token:', error);
      // В режиме разработки продолжаем без токена
      if (process.env.NODE_ENV !== 'development') {
        throw error;
      }
    }
    return config;
  },
  (error) => {
    console.error('Request interceptor error:', error);
    return Promise.reject(error);
  }
);

// Обработка ошибок ответов
api.interceptors.response.use(
  (response) => {
    console.log('API Response:', {
      url: response.config.url,
      status: response.status,
      method: response.config.method
    });
    return response;
  },
  (error) => {
    console.error('API Error:', {
      url: error.config?.url,
      status: error.response?.status,
      method: error.config?.method,
      message: error.message,
      data: error.response?.data
    });
    
    if (error.response?.status === 401) {
      console.error('Authentication failed - user needs to authorize');
      // Можно показать пользователю сообщение об ошибке аутентификации
    }
    
    return Promise.reject(error);
  }
);

// API функции для работы со станциями метро
export const metroAPI = {
  // Получить все станции метро
  getStations: () => api.get('/api/metro/stations'),
  
  // Поиск станций метро
  searchStations: (query) => api.get('/api/metro/search', { params: { query } }),
  
  // Получить информацию о станции
  getStationInfo: (stationName) => 
    api.get(`/api/metro/station/${encodeURIComponent(stationName)}`),
};

// API функции для работы с пользователями
export const userAPI = {
  // Создать или обновить пользователя (надежная версия)
  createOrUpdateUser: async (userData) => {
    console.log('Creating/updating user with data:', userData);
    try {
      const response = await api.post('/api/users/secure', userData);
      console.log('User create/update successful:', response.data);
      return response;
    } catch (error) {
      console.error('User create/update failed:', error.response?.data || error.message);
      throw error;
    }
  },
  
  // Получить текущего пользователя
  getCurrentUser: async () => {
    console.log('Getting current user');
    try {
      const response = await api.get('/api/users/me/secure');
      console.log('Get current user successful:', response.data);
      return response;
    } catch (error) {
      console.error('Get current user failed:', error.response?.data || error.message);
      throw error;
    }
  },
  
  // Обновить профиль пользователя (надежная версия)
  updateProfile: async (userData) => {
    console.log('Updating user profile with data:', userData);
    try {
      const response = await api.put('/api/users/profile/secure', userData);
      console.log('Profile update successful:', response.data);
      return response;
    } catch (error) {
      console.error('Profile update failed:', error.response?.data || error.message);
      throw error;
    }
  },
  
  // Получить потенциальные совпадения
  getPotentialMatches: (limit = 10) => 
    api.get('/api/users/potential-matches', { params: { limit } }),
  
  // Лайкнуть пользователя
  likeUser: (userId) => api.post(`/api/users/${userId}/like`),
  
  // Получить совпадения
  getMatches: () => api.get('/api/users/matches'),
  
  // Получить понравившиеся объявления пользователя
  getUserLikedListings: (userId) => 
    api.get(`/api/users/${userId}/liked-listings`),
};

// API функции для работы с объявлениями
export const listingAPI = {
  // Поиск объявлений
  searchListings: (params) => api.get('/api/listings/', { params }),
  
  // Получить объявления для текущего пользователя
  getUserListings: () => api.get('/api/listings/search'),
  
  // Лайкнуть объявление
  likeListing: (listingId) => api.post(`/api/listings/${listingId}/like`),
  
  // Получить понравившиеся объявления
  getLikedListings: () => api.get('/api/listings/liked'),
};

// Функция для проверки готовности Telegram WebApp
export const checkTelegramWebApp = () => {
  return {
    isAvailable: !!window.Telegram?.WebApp,
    hasInitData: !!(window.Telegram?.WebApp?.initData),
    hasUser: !!(window.Telegram?.WebApp?.initDataUnsafe?.user),
    initDataLength: window.Telegram?.WebApp?.initData?.length || 0,
    user: window.Telegram?.WebApp?.initDataUnsafe?.user || null
  };
};

export default api;