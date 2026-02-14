/**
 * Environment configuration
 * Centralize all API URLs and environment variables
 */
export const ENV_CONFIG = {
    API_BASE_URL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000',
    API_TIMEOUT: import.meta.env.VITE_API_TIMEOUT || 30000,
    ENABLE_ANALYTICS: import.meta.env.VITE_ENABLE_ANALYTICS === 'true',
    ENABLE_WEBSOCKET: import.meta.env.VITE_ENABLE_WEBSOCKET === 'true',
    WEBSOCKET_URL: import.meta.env.VITE_WEBSOCKET_URL || 'ws://localhost:8000/ws',
};
export const API_ENDPOINTS = {
    HEALTH: `${ENV_CONFIG.API_BASE_URL}/health`,
    SCORE: (accountId) => `${ENV_CONFIG.API_BASE_URL}/score/${accountId}`,
    BATCH_SCORE: `${ENV_CONFIG.API_BASE_URL}/batch_score`,
    STATS: `${ENV_CONFIG.API_BASE_URL}/stats`,
    TRANSACTION_GRAPH: `${ENV_CONFIG.API_BASE_URL}/transaction_graph`,
};
export const RISK_COLORS = {
    CRITICAL: '#ef4444',
    HIGH: '#f97316',
    MEDIUM: '#eab308',
    LOW: '#22c55e',
};
export const RISK_LABELS = {
    CRITICAL: '🔴 Critical',
    HIGH: '🟠 High',
    MEDIUM: '🟡 Medium',
    LOW: '🟢 Low',
};
