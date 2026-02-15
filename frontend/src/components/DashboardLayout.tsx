import React, { useState } from 'react';
import { Shield, AlertTriangle, TrendingUp, Activity, Network, Clock, Bell, HelpCircle, Moon, Sun } from 'lucide-react';
import { useTheme } from '../hooks/useTheme';
import { Breadcrumb } from './Breadcrumb';

interface Tab {
  id: string;
  label: string;
  icon: React.ReactNode;
}

const TABS: Tab[] = [
  { id: 'command-center', label: 'Command Center', icon: <Shield size={18} /> },
  { id: 'risk-analysis', label: 'Risk Analysis', icon: <AlertTriangle size={18} /> },
  { id: 'network', label: 'Network Graph', icon: <Network size={18} /> },
  { id: 'real-time', label: 'Real-Time API', icon: <Activity size={18} /> },
  { id: 'about', label: 'About', icon: <HelpCircle size={18} /> },
];

interface DashboardLayoutProps {
  activeTab: string;
  onTabChange: (tabId: string) => void;
  children: React.ReactNode;
}

export const DashboardLayout: React.FC<DashboardLayoutProps> = ({
  activeTab,
  onTabChange,
  children,
}) => {
  const { theme, toggleTheme } = useTheme();
  const activeTabLabel = TABS.find(t => t.id === activeTab)?.label || '';

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 dark:from-white dark:via-blue-50 dark:to-white transition-colors duration-500">
      {/* Header */}
      <header className="bg-gradient-dark dark:bg-gradient-light border-b border-slate-700 dark:border-slate-200 sticky top-0 z-40 transition-colors duration-500">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between flex-wrap gap-4">
            <div className="flex items-center gap-3">
              <Shield className="text-blue-400 dark:text-blue-600" size={32} />
              <div>
                <h1 className="text-2xl font-bold text-white dark:text-slate-900">UPI Mule Detection</h1>
                <p className="text-sm text-gray-400 dark:text-gray-600">Real-time fraud detection platform</p>
              </div>
            </div>
            <div className="flex items-center gap-4">
              <button
                onClick={toggleTheme}
                className="p-2 rounded-lg transition-all duration-300 transform hover:scale-110 bg-slate-700 dark:bg-slate-200 hover:bg-slate-600 dark:hover:bg-slate-300 text-yellow-400 dark:text-yellow-600"
                title={`Switch to ${theme === 'dark' ? 'light' : 'dark'} mode`}
                aria-label="Toggle theme"
              >
                {theme === 'dark' ? <Sun size={20} /> : <Moon size={20} />}
              </button>
              <div className="text-right hidden sm:block transition-colors duration-300">
                <p className="text-sm text-gray-400 dark:text-gray-600">Status: <span className="text-green-400 dark:text-green-600 font-semibold">● Online</span></p>
                <p className="text-xs text-gray-500 dark:text-gray-400">{new Date().toLocaleString()}</p>
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* Tabs */}
      <div className="bg-slate-800 dark:bg-slate-100 border-b border-slate-700 dark:border-slate-300 overflow-x-auto transition-colors duration-500">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex gap-2 overflow-x-auto scroll-smooth">
            {TABS.map((tab) => (
              <button
                key={tab.id}
                onClick={() => onTabChange(tab.id)}
                className={`flex items-center gap-2 px-4 py-3 text-sm font-medium border-b-2 transition whitespace-nowrap ${
                  activeTab === tab.id
                    ? 'border-blue-500 dark:border-blue-600 text-blue-400 dark:text-blue-600'
                    : 'border-transparent text-gray-400 dark:text-gray-600 hover:text-gray-300 dark:hover:text-gray-700'
                }`}
              >
                {tab.icon}
                <span className="hidden sm:inline">{tab.label}</span>
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <Breadcrumb 
          items={[
            { label: 'Dashboard' },
            { label: activeTabLabel, active: true }
          ]} 
        />
        {children}
      </main>

      {/* Footer */}
      <footer className="border-t border-slate-700 dark:border-slate-300 bg-slate-900 dark:bg-white mt-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <p className="text-center text-sm text-gray-500">
            UPI Mule Detection v2.0 · CSIC 1.0 Stage III
          </p>
        </div>
      </footer>
    </div>
  );
};
