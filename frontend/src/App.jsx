import React, { useState, useEffect } from 'react';
import Sidebar from './components/Sidebar';
import CommandCenter from './components/CommandCenter';
import RiskAnalysis from './components/RiskAnalysis';
import MLInsights from './components/MLInsights';
import NetworkGraph from './components/NetworkGraph';
import TimelineTab from './components/TimelineTab';
// import Alerts from './components/Alerts';
import RealTimeAPI from './components/RealTimeAPI';
import About from './components/About';
import Icon from './components/Icon';
import { fetchDashboardData } from './api';

const TABS = [
  { id: 'command',  label: 'Command Center', icon: 'monitoring' },
  { id: 'risk',     label: 'Risk Analysis',  icon: 'crisis_alert' },
  { id: 'ml',       label: 'ML Insights',     icon: 'psychology' },
  { id: 'network',  label: 'Network Graph',   icon: 'hub' },
  { id: 'timeline', label: 'Timeline',        icon: 'schedule' },
  // { id: 'alerts',   label: 'Alerts',          icon: 'notifications_active' },
  { id: 'api',      label: 'Real-Time API',   icon: 'bolt' },
  { id: 'about',    label: 'About',           icon: 'menu_book' },
];

export default function App() {
  const [activeTab, setActiveTab] = useState('command');
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [darkMode, setDarkMode] = useState(() => {
    const saved = localStorage.getItem('darkMode');
    return saved ? JSON.parse(saved) : false;
  });
  const [sidebarOpen, setSidebarOpen] = useState(true);

  useEffect(() => {
    document.documentElement.setAttribute('data-theme', darkMode ? 'dark' : 'light');
    localStorage.setItem('darkMode', JSON.stringify(darkMode));
  }, [darkMode]);

  useEffect(() => {
    fetchDashboardData()
      .then(d => { setData(d); setLoading(false); })
      .catch(err => { setError(err.message); setLoading(false); });
  }, []);

  if (loading) {
    return (
      <div className="loading-screen">
        <div className="loading-spinner" />
        <p><Icon name="sync" size={18} style={{ marginRight: 6 }} /> Loading detection engine...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="loading-screen">
        <p><Icon name="error" size={18} color="#ef4444" style={{ marginRight: 6 }} /> Error loading data: {error}</p>
        <p style={{ fontSize: '0.9rem', color: '#6b7280' }}>
          Make sure the backend is running:&nbsp;
          <code>uvicorn backend.app:app --reload --port 8000</code>
        </p>
      </div>
    );
  }

  const renderTab = () => {
    switch (activeTab) {
      case 'command':  return <CommandCenter data={data} />;
      case 'risk':     return <RiskAnalysis data={data} />;
      case 'ml':       return <MLInsights data={data} />;
      case 'network':  return <NetworkGraph data={data} />;
      case 'timeline': return <TimelineTab />;
      case 'alerts':   return <Alerts data={data} />;
      case 'api':      return <RealTimeAPI data={data} />;
      case 'about':    return <About />;
      default:         return <CommandCenter data={data} />;
    }
  };

  return (
    <div className={`app-container ${sidebarOpen ? '' : 'sidebar-collapsed'}`}>
      {sidebarOpen && <Sidebar data={data} onToggle={() => setSidebarOpen(false)} />}
      {!sidebarOpen && (
        <button
          className="sidebar-open-btn"
          onClick={() => setSidebarOpen(true)}
          title="Show Sidebar"
          aria-label="Show Sidebar"
        >
          <Icon name="menu" size={22} />
        </button>
      )}
      <div className="main-content">
        <div className="header-bar">
          <div className="header-bar-top">
            <div>
              <h1><Icon name="shield" size={28} style={{ marginRight: 8 }} /> UPI Mule Account Detection Platform</h1>
              <p>Real-time detection of mule accounts &amp; collusive fraud networks in UPI transactions</p>
            </div>
            <button
              className="dark-mode-toggle"
              onClick={() => setDarkMode(prev => !prev)}
              title={darkMode ? 'Switch to Light Mode' : 'Switch to Dark Mode'}
              aria-label="Toggle dark mode"
            >
              <Icon name={darkMode ? 'light_mode' : 'dark_mode'} size={20} />
              <span>{darkMode ? 'Light' : 'Dark'}</span>
            </button>
          </div>
        </div>

        <div className="tab-bar">
          {TABS.map(tab => (
            <button
              key={tab.id}
              className={`tab-btn ${activeTab === tab.id ? 'active' : ''}`}
              onClick={() => setActiveTab(tab.id)}
            >
              <Icon name={tab.icon} size={18} style={{ marginRight: 6 }} />
              {tab.label}
            </button>
          ))}
        </div>

        <div className="tab-content">
          {renderTab()}
        </div>
      </div>
    </div>
  );
}
