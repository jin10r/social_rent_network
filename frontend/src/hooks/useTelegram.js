import React, { createContext, useContext, useEffect, useState } from 'react';

const TelegramContext = createContext({});

export const TelegramProvider = ({ children }) => {
  const [webApp, setWebApp] = useState(null);
  const [user, setUser] = useState(null);

  useEffect(() => {
    const app = window.Telegram?.WebApp;
    
    if (app) {
      setWebApp(app);
      setUser(app.initDataUnsafe?.user);
      
      // Initialize web app
      app.ready();
      app.expand();
      
      // Set theme
      if (app.colorScheme === 'dark') {
        document.body.classList.add('telegram-web-app--dark');
      } else {
        document.body.classList.add('telegram-web-app--light');
      }
    } else {
      // Fallback for development
      console.log('Telegram WebApp not available, using mock data');
      setUser({
        id: 123456789,
        first_name: 'Test',
        last_name: 'User',
        username: 'testuser',
        photo_url: null
      });
    }
  }, []);

  const sendData = (data) => {
    if (webApp) {
      webApp.sendData(JSON.stringify(data));
    }
  };

  const showAlert = (message) => {
    if (webApp) {
      webApp.showAlert(message);
    } else {
      alert(message);
    }
  };

  const showConfirm = (message) => {
    return new Promise((resolve) => {
      if (webApp) {
        webApp.showConfirm(message, resolve);
      } else {
        resolve(window.confirm(message));
      }
    });
  };

  const hapticFeedback = (type = 'impact', style = 'medium') => {
    if (webApp && webApp.HapticFeedback) {
      if (type === 'impact') {
        webApp.HapticFeedback.impactOccurred(style);
      } else if (type === 'notification') {
        webApp.HapticFeedback.notificationOccurred(style);
      } else if (type === 'selection') {
        webApp.HapticFeedback.selectionChanged();
      }
    }
  };

  const openLink = (url) => {
    if (webApp) {
      webApp.openLink(url);
    } else {
      window.open(url, '_blank');
    }
  };

  const openTelegramLink = (url) => {
    if (webApp) {
      webApp.openTelegramLink(url);
    } else {
      window.open(`https://t.me/${url}`, '_blank');
    }
  };

  const value = {
    webApp,
    user,
    sendData,
    showAlert,
    showConfirm,
    hapticFeedback,
    openLink,
    openTelegramLink
  };

  return (
    <TelegramContext.Provider value={value}>
      {children}
    </TelegramContext.Provider>
  );
};

export const useTelegram = () => {
  const context = useContext(TelegramContext);
  if (!context) {
    throw new Error('useTelegram must be used within TelegramProvider');
  }
  return context;
};