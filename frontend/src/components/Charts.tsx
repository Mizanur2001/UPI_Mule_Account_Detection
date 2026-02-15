import React from 'react';
import {
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
  LineChart,
  Line,
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  Radar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';
import { RiskScore } from '../types/api';

const COLORS = {
  CRITICAL: '#ff1744',
  HIGH: '#ff5722',
  MEDIUM: '#ff9800',
  LOW: '#4caf50',
};

interface RiskDistributionChartProps {
  scores: RiskScore[];
}

export const RiskDistributionChart: React.FC<RiskDistributionChartProps> = ({ scores }) => {
  const data = [
    { range: '0-20', count: scores.filter(s => s.risk_score < 20).length },
    { range: '20-40', count: scores.filter(s => s.risk_score >= 20 && s.risk_score < 40).length },
    { range: '40-60', count: scores.filter(s => s.risk_score >= 40 && s.risk_score < 60).length },
    { range: '60-80', count: scores.filter(s => s.risk_score >= 60 && s.risk_score < 80).length },
    { range: '80-100', count: scores.filter(s => s.risk_score >= 80).length },
  ];

  return (
    <div className="h-80 dark:bg-slate-800 dark:text-white bg-slate-100 text-slate-900 rounded-lg p-4">
      <h3 className="font-semibold mb-4">Risk Score Distribution</h3>
      <ResponsiveContainer width="100%" height="100%">
        <BarChart data={data} margin={{ top: 20, right: 30, left: 0, bottom: 20 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
          <XAxis dataKey="range" stroke="#9ca3af" />
          <YAxis stroke="#9ca3af" />
          <Tooltip contentStyle={{ backgroundColor: '#1f2937', border: '1px solid #374151' }} />
          <Bar dataKey="count" fill="#3b82f6" radius={[8, 8, 0, 0]} />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
};

interface RiskBreakdownChartProps {
  critical: number;
  high: number;
  medium: number;
  low: number;
}

export const RiskBreakdownChart: React.FC<RiskBreakdownChartProps> = ({
  critical,
  high,
  medium,
  low,
}) => {
  const data = [
    { name: 'CRITICAL', value: critical, fill: COLORS.CRITICAL },
    { name: 'HIGH', value: high, fill: COLORS.HIGH },
    { name: 'MEDIUM', value: medium, fill: COLORS.MEDIUM },
    { name: 'LOW', value: low, fill: COLORS.LOW },
  ];

  return (
    <div className="h-80 dark:bg-slate-800 dark:text-white bg-slate-100 text-slate-900 rounded-lg p-4">
      <h3 className="font-semibold mb-4">Risk Level Breakdown</h3>
      <ResponsiveContainer width="100%" height="100%">
        <PieChart>
          <Pie
            data={data}
            cx="50%"
            cy="50%"
            innerRadius={80}
            outerRadius={120}
            paddingAngle={2}
            dataKey="value"
            label={({ name, value }) => `${name}: ${value}`}
          >
            {data.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={entry.fill} />
            ))}
          </Pie>
          <Tooltip contentStyle={{ backgroundColor: '#1f2937', border: '1px solid #374151' }} />
        </PieChart>
      </ResponsiveContainer>
    </div>
  );
};

interface SignalHeatmapProps {
  scores: RiskScore[];
  limit?: number;
}

export const SignalHeatmap: React.FC<SignalHeatmapProps> = ({ scores, limit = 20 }) => {
  const topScores = scores.slice(0, limit);

  return (
    <div className="dark:bg-slate-800 dark:text-gray-300 bg-slate-100 text-slate-700 rounded-lg p-4 overflow-x-auto">
      <h3 className="dark:text-white text-slate-900 font-semibold mb-4">Signal Heatmap — Top {limit} Risky Accounts</h3>
      <table className="w-full text-sm">
        <thead>
          <tr className="dark:border-slate-700 border-slate-300 border-b">
            <th className="text-left py-2 px-4">Account</th>
            <th className="text-right py-2 px-4">Behavioral</th>
            <th className="text-right py-2 px-4">Graph</th>
            <th className="text-right py-2 px-4">Device</th>
            <th className="text-right py-2 px-4">Temporal</th>
            <th className="text-right py-2 px-4">ML Anomaly</th>
            <th className="text-right py-2 px-4">Total</th>
          </tr>
        </thead>
        <tbody>
          {topScores.map((score) => (
            <tr key={score.account_id} className="dark:border-slate-700 dark:hover:bg-slate-700 border-slate-300 dark:text-gray-300 border-b hover:bg-slate-200">
              <td className="py-2 px-4 font-mono text-xs">{score.account_id}</td>
              <td className="text-right py-2 px-4">
                <ScoreCell value={score.behavioral_score} />
              </td>
              <td className="text-right py-2 px-4">
                <ScoreCell value={score.graph_score} />
              </td>
              <td className="text-right py-2 px-4">
                <ScoreCell value={score.device_score} />
              </td>
              <td className="text-right py-2 px-4">
                <ScoreCell value={score.temporal_score} />
              </td>
              <td className="text-right py-2 px-4">
                <ScoreCell value={score.ml_anomaly_score} />
              </td>
              <td className="text-right py-2 px-4 font-bold dark:text-blue-400 text-blue-600">
                {Math.round(score.risk_score)}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

const ScoreCell: React.FC<{ value: number }> = ({ value }) => {
  let bgColor = 'bg-slate-700';
  if (value >= 70) bgColor = 'bg-critical';
  else if (value >= 50) bgColor = 'bg-high';
  else if (value >= 30) bgColor = 'bg-medium';
  else if (value > 0) bgColor = 'bg-yellow-700';

  return (
    <div className={`inline-block px-2 py-1 rounded text-white font-medium ${bgColor}`}>
      {Math.round(value)}
    </div>
  );
};

interface SignalRadarProps {
  accountId: string;
  behavioral: number;
  graph: number;
  device: number;
  temporal: number;
  ml: number;
}

export const SignalRadar: React.FC<SignalRadarProps> = ({
  accountId,
  behavioral,
  graph,
  device,
  temporal,
  ml,
}) => {
  const data = [
    { signal: 'Behavioral', value: behavioral },
    { signal: 'Graph', value: graph },
    { signal: 'Device', value: device },
    { signal: 'Temporal', value: temporal },
    { signal: 'ML Anomaly', value: ml },
  ];

  return (
    <div className="h-80 bg-slate-800 rounded-lg p-4">
      <h3 className="text-white font-semibold mb-4">Signal Breakdown — {accountId}</h3>
      <ResponsiveContainer width="100%" height="100%">
        <RadarChart data={data} margin={{ top: 20, right: 80, bottom: 20, left: 80 }}>
          <PolarGrid stroke="#374151" />
          <PolarAngleAxis dataKey="signal" stroke="#9ca3af" />
          <PolarRadiusAxis angle={90} domain={[0, 100]} stroke="#9ca3af" />
          <Radar
            name={accountId}
            dataKey="value"
            stroke="#ff1744"
            fill="#ff1744"
            fillOpacity={0.3}
          />
          <Tooltip contentStyle={{ backgroundColor: '#1f2937', border: '1px solid #374151' }} />
        </RadarChart>
      </ResponsiveContainer>
    </div>
  );
};

interface MLAnomalyChartProps {
  scores: RiskScore[];
}

export const MLAnomalyChart: React.FC<MLAnomalyChartProps> = ({ scores }) => {
  const data = scores.map((score, idx) => ({
    index: idx,
    score: score.ml_anomaly_score,
    label: score.ml_anomaly_label,
  }));

  return (
    <div className="h-80 bg-slate-800 rounded-lg p-4">
      <h3 className="text-white font-semibold mb-4">ML Anomaly Scores</h3>
      <ResponsiveContainer width="100%" height="100%">
        <BarChart data={data} margin={{ top: 20, right: 30, left: 0, bottom: 20 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
          <XAxis dataKey="index" stroke="#9ca3af" />
          <YAxis stroke="#9ca3af" />
          <Tooltip
            contentStyle={{ backgroundColor: '#1f2937', border: '1px solid #374151' }}
            formatter={(value) => Math.round(value as number)}
          />
          <Bar dataKey="score" fill="#8b5cf6" radius={[8, 8, 0, 0]} />
          <Line type="monotone" dataKey={(d) => d.label === 'ANOMALOUS' ? 70 : d.label === 'SUSPICIOUS' ? 45 : 0} stroke="#ff1744" strokeDasharray="5 5" />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
};
