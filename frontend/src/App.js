import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import { useState, useEffect } from 'react';
import { apiService } from '@services/api';
import { useAsync, usePoll } from '@hooks/useAsync';
import { DashboardLayout } from '@components/DashboardLayout';
import { ErrorBoundary } from '@components/ErrorBoundary';
import { Toast } from '@components/Toast';
import { ThemeProvider } from '@contexts/ThemeContext';
import { ToastProvider } from '@contexts/ToastContext';
import { CommandCenter } from '@pages/CommandCenter';
import { RiskAnalysis } from '@pages/RiskAnalysis';
import { AboutPage } from '@pages/About';
import { RealTimeAPIPage, NetworkGraphPage, } from '@pages/StubPages';
import { ErrorAlert } from '@components/UI';
const App = () => {
    const [activeTab, setActiveTab] = useState('command-center');
    const [scores, setScores] = useState([]);
    const [stats, setStats] = useState(null);
    // Fetch all accounts and score them
    const { data, loading: scoresLoading, error: scoresError } = useAsync(async () => {
        try {
            const health = await apiService.getHealth();
            setStats(health);
            // Get all unique account IDs
            const accounts = [];
            // For now, we'll fetch stats which should give us an overview
            // In production, you'd have an endpoint to list all accounts
            return [];
        }
        catch (err) {
            throw err;
        }
    });
    // Poll for updates every 30 seconds
    const pollStats = usePoll(async () => {
        try {
            const health = await apiService.getHealth();
            setStats(health);
            // For demo, generate sample scores if not available
            if (scores.length === 0) {
                // Try to batch score some demo accounts
                const demoAccounts = [
                    'mule_aggregator@upi',
                    'circle_node_1@upi',
                    'chain_node_1@upi',
                    'device_ring_1@upi',
                    'new_mule_account@upi',
                    'user_1@upi',
                    'user_2@upi',
                    'user_3@upi',
                ];
                try {
                    const batchScores = await apiService.batchScore(demoAccounts);
                    const scoreArray = Object.values(batchScores);
                    setScores(scoreArray);
                }
                catch (err) {
                    console.log('Demo scores not available, using empty state');
                }
            }
            return health;
        }
        catch (err) {
            console.error('Poll error:', err);
            throw err;
        }
    }, 30000, scores.length === 0);
    // Initialize scores on mount
    useEffect(() => {
        const initializeScores = async () => {
            try {
                // Get all accounts from backend
                const response = await fetch('http://localhost:8000/accounts');
                const data = await response.json();
                const allAccountIds = data.accounts || [];
                if (allAccountIds.length === 0) {
                    console.warn('No accounts found from backend');
                    return;
                }
                console.log(`Loading ${allAccountIds.length} accounts...`);
                // Batch score all accounts
                const batchScores = await apiService.batchScore(allAccountIds);
                const scoreArray = Object.values(batchScores);
                setScores(scoreArray.sort((a, b) => b.risk_score - a.risk_score));
            }
            catch (err) {
                console.error('Failed to initialize scores:', err);
            }
        };
        initializeScores();
    }, []);
    const renderTabContent = () => {
        switch (activeTab) {
            case 'command-center':
                return (_jsx(CommandCenter, { scores: scores, stats: stats, loading: scoresLoading, error: scoresError }));
            case 'risk-analysis':
                return (_jsx(RiskAnalysis, { scores: scores, loading: scoresLoading, error: scoresError }));
            case 'network':
                return _jsx(NetworkGraphPage, {});
            case 'real-time':
                return _jsx(RealTimeAPIPage, {});
            case 'about':
                return _jsx(AboutPage, {});
            default:
                return null;
        }
    };
    return (_jsx(ErrorBoundary, { children: _jsx(ThemeProvider, { children: _jsxs(ToastProvider, { children: [_jsxs(DashboardLayout, { activeTab: activeTab, onTabChange: setActiveTab, children: [scoresError && (_jsx(ErrorAlert, { title: "Connection Error", message: "Failed to connect to backend. Ensure the FastAPI server is running." })), renderTabContent()] }), _jsx(Toast, {})] }) }) }));
};
export default App;
