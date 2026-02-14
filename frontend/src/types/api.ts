/* Risk and Account Types */
export type RiskLevel = 'CRITICAL' | 'HIGH' | 'MEDIUM' | 'LOW';
export type ConfidenceLevel = 'VERY HIGH' | 'HIGH' | 'MODERATE' | 'LOW' | 'MINIMAL';
export type RecommendedAction = 'BLOCK' | 'INVESTIGATE' | 'MONITOR' | 'ALLOW';
export type MLLabel = 'ANOMALOUS' | 'SUSPICIOUS' | 'NORMAL';

export interface RiskScore {
  account_id: string;
  risk_score: number;
  risk_level: RiskLevel;
  confidence: ConfidenceLevel;
  recommended_action: RecommendedAction;
  behavioral_score: number;
  graph_score: number;
  device_score: number;
  temporal_score: number;
  ml_anomaly_score: number;
  ml_anomaly_label: MLLabel;
  signal_count: number;
  reasons: string[];
  timestamp: string;
}

export interface Account {
  account_id: string;
  created_date: string;
  account_type: string;
}

export interface Device {
  account_id: string;
  device_id: string;
  first_seen: string;
  last_seen: string;
}

export interface Transaction {
  transaction_id: string;
  sender: string;
  receiver: string;
  amount: number;
  timestamp: string;
  status: string;
}

export interface HealthStats {
  total_accounts: number;
  total_transactions: number;
  total_devices: number;
  network_nodes: number;
  network_edges: number;
  timestamp: string;
}

export interface SystemStats {
  critical_count: number;
  high_count: number;
  medium_count: number;
  low_count: number;
  average_score: number;
  total_accounts: number;
}

export interface SimulationRequest {
  sender: string;
  receiver: string;
  amount: number;
}

export interface SimulationResponse {
  sender_risk: RiskScore;
  receiver_risk: RiskScore;
  recommendation: 'BLOCK' | 'FLAG' | 'ALLOW';
  reason: string;
}
