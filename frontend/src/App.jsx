import React, { useState } from 'react';
import './App.css';
import Header from './components/Header';
import ForecastForm from './components/ForecastForm';
import CSVUpload from './components/CSVUpload';
import ForecastResults from './components/ForecastResults';

function App() {
  const [forecastResult, setForecastResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState('manual'); // 'manual' or 'csv'

  return (
    <div className="App">
      <Header />
      <main className="main-content">
        <div className="container">
          <div className="tabs">
            <button 
              className={`tab ${activeTab === 'manual' ? 'active' : ''}`}
              onClick={() => setActiveTab('manual')}
            >
              ✏️ Manual Entry
            </button>
            <button 
              className={`tab ${activeTab === 'csv' ? 'active' : ''}`}
              onClick={() => setActiveTab('csv')}
            >
              📂 Upload CSV
            </button>
          </div>
          
          {activeTab === 'manual' ? (
            <ForecastForm 
              setForecastResult={setForecastResult} 
              setLoading={setLoading}
              loading={loading}
            />
          ) : (
            <CSVUpload 
              setForecastResult={setForecastResult} 
              setLoading={setLoading}
              loading={loading}
            />
          )}
          
          {forecastResult && (
            <ForecastResults 
              result={forecastResult} 
              loading={loading}
            />
          )}
        </div>
      </main>
    </div>
  );
}

export default App;