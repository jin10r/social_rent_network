import React from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { 
  User, 
  Heart, 
  MessageCircle, 
  Home, 
  Map,
  Search
} from 'lucide-react';

const Navigation = () => {
  const location = useLocation();
  const navigate = useNavigate();

  const tabs = [
    { id: 'profile', path: '/profile', icon: User, label: 'Профиль' },
    { id: 'matching', path: '/matching', icon: Search, label: 'Поиск' },
    { id: 'matches', path: '/matches', icon: MessageCircle, label: 'Матчи' },
    { id: 'listings', path: '/listings', icon: Home, label: 'Объявления' },
    { id: 'map', path: '/map', icon: Map, label: 'Карта' },
  ];

  return (
    <nav className="tab-navigation">
      {tabs.map((tab) => {
        const Icon = tab.icon;
        const isActive = location.pathname === tab.path;
        
        return (
          <div
            key={tab.id}
            className={`tab-item ${isActive ? 'active' : ''}`}
            onClick={() => navigate(tab.path)}
          >
            <Icon size={20} />
            <span>{tab.label}</span>
          </div>
        );
      })}
    </nav>
  );
};

export default Navigation;