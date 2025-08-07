import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import Navigation from './components/Navigation';
import Profile from './components/Profile';
import Matching from './components/Matching';
import Matches from './components/Matches';
import Listings from './components/Listings';
import Map from './components/Map';
import { TelegramProvider, useTelegram } from './hooks/useTelegram';
import { UserProvider } from './context/UserContext';
import './index.css';

function AppContent() {
  const { user: tgUser, webApp } = useTelegram();
  const [currentUser, setCurrentUser] = useState(null);
  const [loading, setLoading] = useState(true);

  console.log('AppContent rendered, tgUser:', tgUser, 'webApp:', webApp);

  useEffect(() => {
    console.log('AppContent useEffect called, tgUser:', tgUser, 'webApp:', webApp);
    // Configure Telegram Web App
    if (webApp) {
      webApp.ready();
      webApp.expand();
      
      // Set header color
      if (webApp.setHeaderColor) {
        webApp.setHeaderColor('#17212b');
      }
      
      // Set background color
      if (webApp.setBackgroundColor) {
        webApp.setBackgroundColor('#17212b');
      }
    }

    // Load user data
    if (tgUser) {
      console.log('Setting currentUser from tgUser:', tgUser);
      setCurrentUser({
        telegram_id: tgUser.id,
        username: tgUser.username,
        first_name: tgUser.first_name,
        last_name: tgUser.last_name,
        photo_url: tgUser.photo_url
      });
    }
    
    setLoading(false);
  }, [tgUser, webApp]);

  if (loading) {
    return (
      <div className="tg-container flex items-center justify-center" style={{ height: '100vh' }}>
        <div className="loading-spinner"></div>
      </div>
    );
  }

  return (
    <UserProvider value={{ currentUser, setCurrentUser }}>
      <div className="tg-container">
        <Router>
          <Routes>
            <Route path="/" element={<Navigate to="/profile" replace />} />
            <Route path="/profile" element={<Profile />} />
            <Route path="/matching" element={<Matching />} />
            <Route path="/matches" element={<Matches />} />
            <Route path="/listings" element={<Listings />} />
            <Route path="/map" element={<Map />} />
          </Routes>
          <Navigation />
        </Router>
      </div>
    </UserProvider>
  );
}

function App() {
  console.log('App component rendered');
  return (
    <TelegramProvider>
      <AppContent />
    </TelegramProvider>
  );
}

export default App;