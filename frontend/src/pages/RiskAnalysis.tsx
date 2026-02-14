import React, { useState, useMemo } from 'react';
import { RiskScore } from '../types/api';
import { RiskBadge, Button, LoadingSpinner, ErrorAlert } from '../components/UI';
import { SignalRadar } from '../components/Charts';
import { ChevronDown, Download } from 'lucide-react';

interface RiskAnalysisProps {
  scores: RiskScore[];
  loading: boolean;
  error: Error | null;
}

type SortField = 'risk_score' | 'behavioral_score' | 'graph_score' | 'device_score' | 'temporal_score' | 'ml_anomaly_score';

export const RiskAnalysis: React.FC<RiskAnalysisProps> = ({
  scores,
  loading,
  error,
}) => {
  const [selectedRiskLevels, setSelectedRiskLevels] = useState<string[]>([
    'CRITICAL',
    'HIGH',
    'MEDIUM',
    'LOW',
  ]);
  const [minScore, setMinScore] = useState(0);
  const [sortField, setSortField] = useState<SortField>('risk_score');
  const [selectedAccount, setSelectedAccount] = useState<string | null>(null);

  const filtered = useMemo(() => {
    return scores
      .filter((s) =>
        selectedRiskLevels.includes(s.risk_level) && s.risk_score >= minScore
      )
      .sort((a, b) => b[sortField] - a[sortField]);
  }, [scores, selectedRiskLevels, minScore, sortField]);

  const handleExport = () => {
    const csv = [
      ['Account', 'Risk Score', 'Risk Level', 'Behavioral', 'Graph', 'Device', 'Temporal', 'ML Anomaly', 'Signals', 'Top Reason'],
      ...filtered.map((s) => [
        s.account_id,
        s.risk_score,
        s.risk_level,
        s.behavioral_score,
        s.graph_score,
        s.device_score,
        s.temporal_score,
        s.ml_anomaly_score,
        s.signal_count,
        s.reasons[0] || 'No flags',
      ]),
    ]
      .map((row) => row.map((cell) => `"${cell}"`).join(','))
      .join('\n');

    const blob = new Blob([csv], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `mule_risk_${new Date().toISOString().slice(0, 10)}.csv`;
    link.click();
  };

  if (loading) return <LoadingSpinner message="Loading risk analysis..." />;
  if (error) return <ErrorAlert title="Error Loading Data" message={error.message} />;

  return (
    <div className="space-y-6">
      {/* Filters */}
      <div className="bg-slate-800 rounded-lg p-4">
        <h2 className="text-white font-semibold mb-4">Filters</h2>
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div>
            <label className="block text-sm text-gray-400 mb-2">Risk Level</label>
            <div className="space-y-2">
              {['CRITICAL', 'HIGH', 'MEDIUM', 'LOW'].map((level) => (
                <label key={level} className="flex items-center gap-2 text-gray-300 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={selectedRiskLevels.includes(level)}
                    onChange={(e) => {
                      if (e.target.checked) {
                        setSelectedRiskLevels([...selectedRiskLevels, level]);
                      } else {
                        setSelectedRiskLevels(selectedRiskLevels.filter((l) => l !== level));
                      }
                    }}
                    className="w-4 h-4"
                  />
                  {level}
                </label>
              ))}
            </div>
          </div>

          <div>
            <label className="block text-sm text-gray-400 mb-2">Minimum Score</label>
            <input
              type="range"
              min="0"
              max="100"
              value={minScore}
              onChange={(e) => setMinScore(Number(e.target.value))}
              className="w-full"
            />
            <p className="text-xs text-gray-500 mt-1">{minScore}/100</p>
          </div>

          <div>
            <label className="block text-sm text-gray-400 mb-2">Sort By</label>
            <select
              value={sortField}
              onChange={(e) => setSortField(e.target.value as SortField)}
              className="w-full bg-slate-700 text-white rounded px-3 py-2 text-sm"
            >
              <option value="risk_score">Risk Score</option>
              <option value="behavioral_score">Behavioral</option>
              <option value="graph_score">Graph</option>
              <option value="device_score">Device</option>
              <option value="temporal_score">Temporal</option>
              <option value="ml_anomaly_score">ML Anomaly</option>
            </select>
          </div>

          <div className="flex items-end">
            <Button
              variant="success"
              size="md"
              onClick={handleExport}
              className="w-full flex items-center justify-center gap-2"
            >
              <Download size={16} />
              Export CSV
            </Button>
          </div>
        </div>
      </div>

      <p className="text-gray-400 text-sm">
        Showing {filtered.length} of {scores.length} accounts
      </p>

      {/* Table */}
      <div className="bg-slate-800 rounded-lg overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-sm text-gray-300">
            <thead>
              <tr className="border-b border-slate-700 bg-slate-900">
                <th className="text-left py-3 px-4">Account</th>
                <th className="text-right py-3 px-4">Score</th>
                <th className="text-center py-3 px-4">Level</th>
                <th className="text-right py-3 px-4">Behavioral</th>
                <th className="text-right py-3 px-4">Graph</th>
                <th className="text-right py-3 px-4">Device</th>
                <th className="text-right py-3 px-4">Temporal</th>
                <th className="text-right py-3 px-4">ML</th>
                <th className="text-right py-3 px-4">Signals</th>
                <th className="text-left py-3 px-4">Action</th>
              </tr>
            </thead>
            <tbody>
              {filtered.map((score) => (
                <React.Fragment key={score.account_id}>
                  <tr
                    onClick={() =>
                      setSelectedAccount(
                        selectedAccount === score.account_id ? null : score.account_id
                      )
                    }
                    className="border-b border-slate-700 hover:bg-slate-700 cursor-pointer transition"
                  >
                    <td className="py-3 px-4 font-mono text-xs">{score.account_id}</td>
                    <td className="text-right py-3 px-4 font-bold text-blue-400">
                      {Math.round(score.risk_score)}
                    </td>
                    <td className="text-center py-3 px-4">
                      <RiskBadge level={score.risk_level} />
                    </td>
                    <td className="text-right py-3 px-4">{Math.round(score.behavioral_score)}</td>
                    <td className="text-right py-3 px-4">{Math.round(score.graph_score)}</td>
                    <td className="text-right py-3 px-4">{Math.round(score.device_score)}</td>
                    <td className="text-right py-3 px-4">{Math.round(score.temporal_score)}</td>
                    <td className="text-right py-3 px-4">{Math.round(score.ml_anomaly_score)}</td>
                    <td className="text-right py-3 px-4 font-semibold">{score.signal_count}</td>
                    <td className="text-left py-3 px-4">
                      <span className="text-xs px-2 py-1 rounded bg-slate-700 text-gray-300">
                        {score.recommended_action}
                      </span>
                    </td>
                  </tr>
                  {selectedAccount === score.account_id && (
                    <tr className="bg-slate-900 border-b border-slate-700">
                      <td colSpan={10} className="py-4 px-4">
                        <DrillDownPanel score={score} />
                      </td>
                    </tr>
                  )}
                </React.Fragment>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

interface DrillDownPanelProps {
  score: RiskScore;
}

const DrillDownPanel: React.FC<DrillDownPanelProps> = ({ score }) => {
  return (
    <div className="space-y-4">
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {/* Metrics */}
        <div className="space-y-2">
          <h3 className="text-white font-semibold text-sm">Overview</h3>
          <div className="bg-slate-800 rounded p-3 space-y-1 text-xs">
            <p className="text-gray-400">
              <span className="text-gray-300 font-semibold">Risk Level:</span> {score.risk_level}
            </p>
            <p className="text-gray-400">
              <span className="text-gray-300 font-semibold">Confidence:</span> {score.confidence}
            </p>
            <p className="text-gray-400">
              <span className="text-gray-300 font-semibold">Action:</span> {score.recommended_action}
            </p>
            <p className="text-gray-400">
              <span className="text-gray-300 font-semibold">Signals:</span> {score.signal_count} active
            </p>
          </div>
        </div>

        {/* Radar Chart */}
        <div className="md:col-span-2">
          <div style={{ height: '350px' }}>
            <SignalRadar
              accountId={score.account_id}
              behavioral={score.behavioral_score}
              graph={score.graph_score}
              device={score.device_score}
              temporal={score.temporal_score}
              ml={score.ml_anomaly_score}
            />
          </div>
        </div>
      </div>

      {/* Evidence */}
      <div>
        <h3 className="text-white font-semibold text-sm mb-2">Evidence Trail</h3>
        <div className="space-y-2">
          {score.reasons.map((reason, idx) => (
            <div key={idx} className="bg-slate-800 border-l-4 border-orange-400 p-3 rounded-r">
              <p className="text-gray-300 text-xs">🔸 {reason}</p>
            </div>
          ))}
          {score.reasons.length === 0 && (
            <div className="bg-slate-800 border-l-4 border-green-400 p-3 rounded-r">
              <p className="text-gray-300 text-xs">✓ No risk factors identified</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
