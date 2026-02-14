import React from 'react';
import { RiskScore } from '../types/api';
import { LoadingSpinner, ErrorAlert } from '../components/UI';
import { MLAnomalyChart } from '../components/Charts';

interface MLInsightsProps {
  scores: RiskScore[];
  loading: boolean;
  error: Error | null;
}

export const MLInsights: React.FC<MLInsightsProps> = ({
  scores,
  loading,
  error,
}) => {
  if (loading) return <LoadingSpinner message="Loading ML analysis..." />;
  if (error) return <ErrorAlert title="Error Loading Data" message={error.message} />;

  const anomalousCount = scores.filter((s) => s.ml_anomaly_label === 'ANOMALOUS').length;
  const suspiciousCount = scores.filter((s) => s.ml_anomaly_label === 'SUSPICIOUS').length;
  const normalCount = scores.filter((s) => s.ml_anomaly_label === 'NORMAL').length;

  return (
    <div className="space-y-6">
      <div className="bg-slate-800 rounded-lg p-4">
        <h2 className="text-white font-semibold mb-2">🧠 Machine Learning Anomaly Detection</h2>
        <p className="text-gray-400 text-sm">
          Our system uses an <strong>ensemble approach</strong> combining a custom-built <strong>Isolation Forest</strong> 
          (unsupervised) with <strong>Z-score statistical outlier detection</strong> — requiring <strong>zero labeled fraud data</strong>. 
          This makes it fully autonomous and deployable from day one.
        </p>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="bg-slate-800 rounded-lg p-4">
          <h3 className="text-red-400 font-semibold mb-1">Anomalous</h3>
          <p className="text-3xl font-bold text-white">{anomalousCount}</p>
          <p className="text-xs text-gray-400 mt-1">ML Score ≥ 70</p>
        </div>
        <div className="bg-slate-800 rounded-lg p-4">
          <h3 className="text-yellow-400 font-semibold mb-1">Suspicious</h3>
          <p className="text-3xl font-bold text-white">{suspiciousCount}</p>
          <p className="text-xs text-gray-400 mt-1">ML Score 45-69</p>
        </div>
        <div className="bg-slate-800 rounded-lg p-4">
          <h3 className="text-green-400 font-semibold mb-1">Normal</h3>
          <p className="text-3xl font-bold text-white">{normalCount}</p>
          <p className="text-xs text-gray-400 mt-1">ML Score &lt; 45</p>
        </div>
      </div>

      {/* Chart */}
      <div>
        <MLAnomalyChart scores={scores} />
      </div>

      {/* Explanation */}
      <div className="bg-slate-800 rounded-lg p-6 space-y-4">
        <h3 className="text-white font-semibold">How It Works</h3>
        
        <div className="space-y-3">
          <div>
            <h4 className="text-blue-400 font-semibold text-sm">Isolation Forest (70% weight)</h4>
            <p className="text-gray-400 text-sm">
              An unsupervised ML algorithm that identifies anomalies by their isolation properties. 
              Pathological transactions are easier to isolate than normal ones.
            </p>
          </div>

          <div>
            <h4 className="text-blue-400 font-semibold text-sm">Z-Score Statistical Analysis (30% weight)</h4>
            <p className="text-gray-400 text-sm">
              Identifies transactions that deviate statistically from normal patterns. 
              Any account with extreme velocity, amounts, or device behavior gets flagged.
            </p>
          </div>

          <div>
            <h4 className="text-blue-400 font-semibold text-sm">Key Features</h4>
            <ul className="text-gray-400 text-sm space-y-1 list-disc list-inside">
              <li>No training data needed — fully unsupervised</li>
              <li>Works on behavioral features (velocity, amounts, timing, patterns)</li>
              <li>Adapts to new fraud types automatically</li>
              <li>Interpretable results with evidence trails</li>
            </ul>
          </div>
        </div>
      </div>

      {/* Top ML Anomalies */}
      <div className="bg-slate-800 rounded-lg p-4">
        <h3 className="text-white font-semibold mb-4">Top ML Anomalies</h3>
        <div className="space-y-2">
          {scores
            .filter((s) => s.ml_anomaly_label === 'ANOMALOUS')
            .slice(0, 5)
            .map((score) => (
              <div key={score.account_id} className="flex items-center justify-between bg-slate-900 p-3 rounded">
                <span className="font-mono text-xs text-gray-400">{score.account_id}</span>
                <div className="text-right">
                  <div className="text-red-400 font-bold">{Math.round(score.ml_anomaly_score)}</div>
                  <div className="text-gray-500 text-xs">{score.ml_anomaly_label}</div>
                </div>
              </div>
            ))}
        </div>
      </div>
    </div>
  );
};
