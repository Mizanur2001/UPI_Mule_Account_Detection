import React, { useState, useEffect } from 'react';
import { RiskScore, HealthStats } from './types/api';
import { apiService } from '@services/api';
import { DashboardLayout } from '@components/DashboardLayout';
import { ErrorBoundary } from '@components/ErrorBoundary';
import { Toast } from '@components/Toast';
import { ThemeProvider } from '@contexts/ThemeContext';
import { ToastProvider } from '@contexts/ToastContext';
import { CommandCenter } from '@pages/CommandCenter';
import { RiskAnalysis } from '@pages/RiskAnalysis';
import { AboutPage } from '@pages/About';
import {
  RealTimeAPIPage,
  NetworkGraphPage,
} from '@pages/StubPages';
import { ErrorAlert } from '@components/UI';

const App: React.FC = () => {
  const [activeTab, setActiveTab] = useState('command-center');
  const [scores, setScores] = useState<RiskScore[]>([]);
  const [stats, setStats] = useState<HealthStats | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  // Single unified effect to load all data
  useEffect(() => {
    const loadAllData = async () => {
      try {
        setIsLoading(true);
        setError(null);
        console.log('[App] Starting data load...');

        // Step 1: Fetch health stats
        console.log('[App] Fetching health stats...');
        const health = await apiService.getHealth();
        setStats(health);
        console.log('[App] Health stats loaded:', { accounts: health.total_accounts, txns: health.total_transactions });

        // Step 2: Fetch all account IDs
        console.log('[App] Fetching accounts list...');
        const accountsResponse = await fetch('http://localhost:8000/accounts');
        if (!accountsResponse.ok) {
          throw new Error(`Failed to fetch accounts: ${accountsResponse.status}`);
        }
        const accountsData = await accountsResponse.json();
        const allAccountIds: string[] = accountsData.accounts || [];
        console.log(`[App] Account list retrieved: ${allAccountIds.length} accounts`);

        if (allAccountIds.length === 0) {
          throw new Error('No accounts found from backend');
        }

        // Step 3: Batch score all accounts (with retry logic)
        console.log(`[App] Batch scoring ${allAccountIds.length} accounts...`);
        let batchResponse;
        let retries = 0;
        while (retries < 3) {
          try {
            batchResponse = await apiService.batchScore(allAccountIds);
            break;
          } catch (err) {
            retries++;
            console.warn(`[App] Batch score attempt ${retries} failed, retrying...`);
            if (retries >= 3) throw err;
            await new Promise(r => setTimeout(r, 1000)); // Wait 1s before retry
          }
        }

        if (!batchResponse || typeof batchResponse !== 'object') {
          throw new Error(`Invalid batch response type: ${typeof batchResponse}`);
        }

        const scoreArray = Object.values(batchResponse) as RiskScore[];
        console.log(`[App] Batch score returned: ${scoreArray.length} scores`);
        
        // Filter valid scores
        const validScores = scoreArray.filter(
          s => s && s.account_id && s.risk_level && typeof s.risk_score === 'number'
        );
        console.log(`[App] Valid scores after filtering: ${validScores.length}/${scoreArray.length}`);
        
        if (validScores.length === 0) {
          throw new Error('No valid scores returned from batch score');
        }

        // Sort by risk (highest first)
        const sortedScores = validScores.sort((a, b) => b.risk_score - a.risk_score);
        console.log(`[App] Data load complete. Top risk accounts:`, sortedScores.slice(0, 3));
        
        setScores(sortedScores);
        setIsLoading(false);
      } catch (err) {
        const error = err instanceof Error ? err : new Error(String(err));
        console.error('[App] Data load failed:', error);
        setError(error);
        setIsLoading(false);
      }
    };

    loadAllData();
  }, []);

  const renderTabContent = () => {
    switch (activeTab) {
      case 'command-center':
        return (
          <CommandCenter
            scores={scores}
            stats={stats}
            loading={isLoading}
            error={error}
          />
        );
      case 'risk-analysis':
        return (
          <RiskAnalysis
            scores={scores}
            loading={isLoading}
            error={error}
          />
        );
      case 'network':
        return <NetworkGraphPage />;
      case 'real-time':
        return <RealTimeAPIPage />;
      case 'about':
        return <AboutPage />;
      default:
        return null;
    }
  };

  return (
    <ErrorBoundary>
      <ThemeProvider>
        <ToastProvider>
          <DashboardLayout activeTab={activeTab} onTabChange={setActiveTab}>
            {error && !isLoading && (
              <ErrorAlert
                title="Connection Error"
                message={`Failed to load data: ${error.message}`}
              />
            )}
            {renderTabContent()}
          </DashboardLayout>
          <Toast />
        </ToastProvider>
      </ThemeProvider>
    </ErrorBoundary>
  );
};

export default App;
