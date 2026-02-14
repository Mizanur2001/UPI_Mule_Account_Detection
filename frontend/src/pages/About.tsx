import React from 'react';

export const AboutPage: React.FC = () => {
  return (
    <div className="space-y-6 max-w-4xl">
      <div className="bg-slate-800 rounded-lg p-6">
        <h2 className="text-white text-2xl font-bold mb-4">About UPI Mule Detection</h2>
        <p className="text-gray-400 mb-4">
          A production-ready MVP for detecting mule accounts using a 5-factor risk model that combines behavioral 
          analysis, graph pattern detection, device correlation, temporal anomaly detection, and ML-based anomaly scoring.
        </p>
        <p className="text-gray-400">
          Developed for the Cyber Security Innovation Challenge (CSIC) 1.0 – Stage III
        </p>
      </div>

      <div className="bg-slate-800 rounded-lg p-6">
        <h3 className="text-white font-semibold text-lg mb-4">🎯 Detection Algorithm</h3>
        
        <div className="space-y-4">
          <div>
            <h4 className="text-blue-400 font-semibold mb-2">Behavioral Analysis (25%)</h4>
            <ul className="text-gray-400 text-sm space-y-1 list-disc list-inside">
              <li>Velocity spikes (5-10+ transactions)</li>
              <li>New account rapid activity (0-7 days)</li>
              <li>Pass-through ratio (80-120% inflow→outflow)</li>
              <li>Amount anomalies (avg &gt; ₹5K)</li>
              <li>Pure sender pattern (no receiving txns)</li>
            </ul>
          </div>

          <div>
            <h4 className="text-green-400 font-semibold mb-2">Graph Analysis (40%) – STRONGEST SIGNAL</h4>
            <ul className="text-gray-400 text-sm space-y-1 list-disc list-inside">
              <li>Star patterns: 3-5+ inflows → 1 outflow</li>
              <li>Distributors: 1 inflow → 3-5+ outflows</li>
              <li>Relay nodes: High in/out degree processing</li>
              <li>Chains: Linear laundering paths A→B→C→D</li>
              <li>Circular: Fund rotation loops A→B→C→A</li>
            </ul>
          </div>

          <div>
            <h4 className="text-purple-400 font-semibold mb-2">Device Correlation (15%)</h4>
            <ul className="text-gray-400 text-sm space-y-1 list-disc list-inside">
              <li>Device shared across 3-10+ accounts</li>
              <li>Multi-device control / spoofing</li>
            </ul>
          </div>

          <div>
            <h4 className="text-yellow-400 font-semibold mb-2">Temporal Analysis (10%)</h4>
            <ul className="text-gray-400 text-sm space-y-1 list-disc list-inside">
              <li>Rapid-fire bursts (&lt; 60s between txns)</li>
              <li>Odd-hour activity (12AM-5AM concentration)</li>
              <li>Velocity spikes (3x+ rate increase)</li>
              <li>Uniform timing / bot signature</li>
            </ul>
          </div>

          <div>
            <h4 className="text-red-400 font-semibold mb-2">ML Anomaly Detection (10%)</h4>
            <ul className="text-gray-400 text-sm space-y-1 list-disc list-inside">
              <li>Isolation Forest (unsupervised, pure NumPy)</li>
              <li>Z-score statistical outlier detection</li>
              <li>Ensemble: 70% IF + 30% Z-score</li>
            </ul>
          </div>
        </div>
      </div>

      <div className="bg-slate-800 rounded-lg p-6">
        <h3 className="text-white font-semibold text-lg mb-4">📊 Risk Scoring Formula</h3>
        <div className="bg-slate-900 rounded p-4 font-mono text-sm text-gray-300 mb-4">
          <div>Base = (0.25 × Behavioral) + (0.40 × Graph) + (0.15 × Device)</div>
          <div className="mt-2">     + (0.10 × Temporal) + (0.10 × ML Anomaly)</div>
          <div className="mt-2">Boost: +8 (2 signals) / +15 (3 signals) / +20 (4+ signals)</div>
          <div>       +10 (graph & device) / +8 (behavioral & graph)</div>
          <div>       +12 (extreme triple correlation)</div>
          <div className="mt-2">Score = min(Base + Boost, 100)</div>
        </div>
      </div>

      <div className="bg-slate-800 rounded-lg p-6">
        <h3 className="text-white font-semibold text-lg mb-4">🚨 Risk Levels & Actions</h3>
        
        <div className="space-y-3">
          <div className="border-l-4 border-critical pl-4">
            <h4 className="text-critical font-semibold">CRITICAL (85+)</h4>
            <p className="text-gray-400 text-sm">Block immediately — freeze account, alert compliance, file SAR</p>
          </div>

          <div className="border-l-4 border-high pl-4">
            <h4 className="text-high font-semibold">HIGH (70-84)</h4>
            <p className="text-gray-400 text-sm">Investigate — manual review within 24h, enhanced monitoring</p>
          </div>

          <div className="border-l-4 border-medium pl-4">
            <h4 className="text-medium font-semibold">MEDIUM (40-69)</h4>
            <p className="text-gray-400 text-sm">Monitor — add to watchlist, periodic review</p>
          </div>

          <div className="border-l-4 border-low pl-4">
            <h4 className="text-low font-semibold">LOW (&lt;40)</h4>
            <p className="text-gray-400 text-sm">Allow — normal operations, routine monitoring</p>
          </div>
        </div>
      </div>

      <div className="bg-slate-800 rounded-lg p-6">
        <h3 className="text-white font-semibold text-lg mb-4">📁 Architecture</h3>
        <div className="text-gray-400 text-sm space-y-2">
          <p>
            <strong className="text-blue-400">Frontend:</strong> React + TypeScript + Tailwind CSS + Recharts
          </p>
          <p>
            <strong className="text-blue-400">Backend:</strong> FastAPI 2.0 with 6 REST endpoints
          </p>
          <p>
            <strong className="text-blue-400">Detection Engine:</strong> 5 independent risk signal modules
          </p>
          <p>
            <strong className="text-blue-400">Graph Processing:</strong> NetworkX with O(V·depth) complexity
          </p>
          <p>
            <strong className="text-blue-400">ML:</strong> Isolation Forest + Z-score ensemble (pure NumPy)
          </p>
        </div>
      </div>

      <div className="bg-slate-900 rounded-lg p-4 border border-slate-700">
        <p className="text-gray-400 text-sm text-center">
          UPI Mule Detection v2.0 · CSIC 1.0 Stage III · 2026
        </p>
      </div>
    </div>
  );
};
