import React from 'react';
import { useTheme } from '../context/ThemeContext';
import './Header.css';

const Header = () => {
  const { isDarkMode, toggleTheme } = useTheme();

  return (
    <header className="header">
      <div className="container header-content">
        <div className="header-left">
          <h1>📈 Run-Rate Forecaster</h1>
          <p>Advanced time-series forecasting with classical statistical models</p>
        </div>
        <button className="theme-toggle" onClick={toggleTheme} title={isDarkMode ? 'Light Mode' : 'Dark Mode'}>
          {isDarkMode ? '☀️' : '🌙'}
        </button>
      </div>
    </header>
  );
};

export default Header;