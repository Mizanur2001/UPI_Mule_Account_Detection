import axios, { AxiosInstance } from 'axios';
import { RiskScore, HealthStats, SystemStats, SimulationRequest, SimulationResponse } from '../types/api';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';
const API_TIMEOUT = parseInt(import.meta.env.VITE_API_TIMEOUT || '30000');

const api: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  timeout: API_TIMEOUT,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const apiService = {
  // Get service info
  getInfo: async () => {
    const response = await api.get('/');
    return response.data;
  },

  // Health check
  getHealth: async (): Promise<HealthStats> => {
    const response = await api.get('/health');
    const data = response.data.data;
    return {
      total_accounts: data.accounts,
      total_transactions: data.transactions,
      total_devices: data.devices,
      network_nodes: data.graph_nodes,
      network_edges: data.graph_edges,
      timestamp: response.data.timestamp,
    };
  },

  // Score single account
  scoreAccount: async (accountId: string): Promise<RiskScore> => {
    const response = await api.get(`/score/${accountId}`);
    return response.data;
  },

  // Batch score accounts
  batchScore: async (accountIds: string[]): Promise<Record<string, RiskScore>> => {
    const response = await api.post('/batch_score', { account_ids: accountIds });
    return response.data.results;
  },

  // Get system stats
  getStats: async (): Promise<SystemStats> => {
    const response = await api.get('/stats');
    return response.data;
  },

  // Simulate transaction
  simulateTransaction: async (request: SimulationRequest): Promise<SimulationResponse> => {
    const response = await api.post('/simulate', request);
    return response.data;
  },
};

export default api;
