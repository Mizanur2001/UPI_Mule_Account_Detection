import React from 'react';
import { RiskScore, HealthStats } from '../types/api';
import { MetricCard, LoadingSpinner, ErrorAlert } from '../components/UI';
import {
  RiskDistributionChart,
  RiskBreakdownChart,
  SignalHeatmap,
} from '../components/Charts';
import { AlertTriangle, Activity, Database } from 'lucide-react';

interface CommandCenterProps {
  scores: RiskScore[];
  stats: HealthStats | null;
  loading: boolean;
  error: Error | null;
}

export const CommandCenter: React.FC<CommandCenterProps> = ({
  scores,
  stats,
  loading,
  error,
}) => {
  if (loading) return <LoadingSpinner message="Loading detection engine..." />;
  if (error) return <ErrorAlert title="Error Loading Data" message={error.message} />;
  if (!scores.length) return <ErrorAlert title="No Data" message="No accounts to display" />;

  const criticalCount = scores.filter((s) => s.risk_level === 'CRITICAL').length;
  const highCount = scores.filter((s) => s.risk_level === 'HIGH').length;
  const mediumCount = scores.filter((s) => s.risk_level === 'MEDIUM').length;
  const lowCount = scores.filter((s) => s.risk_level === 'LOW').length;
  const avgScore = scores.reduce((sum, s) => sum + s.risk_score, 0) / scores.length;

  return (
    <div className="space-y-6">
      {/* Metric Cards */}
      <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
        <MetricCard
          label="🔴 CRITICAL"
          value={criticalCount}
          riskLevel="CRITICAL"
        />
        <MetricCard
          label="🟠 HIGH RISK"
          value={highCount}
          riskLevel="HIGH"
        />
        <MetricCard
          label="🟡 MEDIUM"
          value={mediumCount}
          riskLevel="MEDIUM"
        />
        <MetricCard
          label="🟢 LOW"
          value={lowCount}
          riskLevel="LOW"
        />
        <MetricCard
          label="📈 AVG SCORE"
          value={avgScore.toFixed(0)}
          className="border-blue-600 bg-blue-950"
        />
      </div>

      {/* System Stats */}
      {stats && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="bg-slate-800 rounded-lg p-4">
            <div className="flex items-center gap-3">
              <Database className="text-blue-400" size={24} />
              <div>
                <p className="text-gray-400 text-sm">Total Accounts</p>
                <p className="text-2xl font-bold text-white">{stats.total_accounts}</p>
              </div>
            </div>
          </div>
          <div className="bg-slate-800 rounded-lg p-4">
            <div className="flex items-center gap-3">
              <Activity className="text-green-400" size={24} />
              <div>
                <p className="text-gray-400 text-sm">Transactions</p>
                <p className="text-2xl font-bold text-white">{stats.total_transactions}</p>
              </div>
            </div>
          </div>
          <div className="bg-slate-800 rounded-lg p-4">
            <div className="flex items-center gap-3">
              <AlertTriangle className="text-yellow-400" size={24} />
              <div>
                <p className="text-gray-400 text-sm">Devices</p>
                <p className="text-2xl font-bold text-white">{stats.total_devices}</p>
              </div>
            </div>
          </div>
          <div className="bg-slate-800 rounded-lg p-4">
            <div className="flex items-center gap-3">
              <Activity className="text-purple-400" size={24} />
              <div>
                <p className="text-gray-400 text-sm">Network</p>
                <p className="text-lg font-bold text-white">{stats.network_nodes} nodes</p>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2">
          <RiskDistributionChart scores={scores} />
        </div>
        <div>
          <RiskBreakdownChart
            critical={criticalCount}
            high={highCount}
            medium={mediumCount}
            low={lowCount}
          />
        </div>
      </div>

      {/* Signal Heatmap */}
      <div>
        <SignalHeatmap scores={scores} limit={20} />
      </div>
    </div>
  );
};
