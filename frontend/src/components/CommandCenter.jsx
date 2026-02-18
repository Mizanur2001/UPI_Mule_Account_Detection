import React from 'react';
import Plot from 'react-plotly.js';
import Icon from './Icon';

const COLOR_MAP = { CRITICAL: '#ef4444', HIGH: '#f97316', MEDIUM: '#eab308', LOW: '#22c55e' };
const DARK_LAYOUT = {
  // template: 'plotly_white', // Default is fine
  paper_bgcolor: 'rgba(0,0,0,0)',
  plot_bgcolor: 'rgba(0,0,0,0)',
  margin: { l: 20, r: 20, t: 30, b: 20 },
  font: { color: '#1f2937', family: 'Inter, sans-serif', size: 12 },
};

export default function CommandCenter({ data }) {
  const s = data.summary;
  const scores = data.scores;

  /* ── Histogram traces (one per risk level) ── */
  const levels = ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW'];
  const histTraces = levels.map(lvl => ({
    type: 'histogram',
    x: scores.filter(sc => sc.risk_level === lvl).map(sc => sc.risk_score),
    name: lvl,
    marker: { color: COLOR_MAP[lvl] },
    nbinsx: 20,
  }));

  /* ── Donut chart ── */
  const pieTrace = {
    type: 'pie',
    values: [s.critical_count, s.high_count, s.medium_count, s.low_count],
    labels: ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW'],
    marker: { colors: ['#ef4444', '#f97316', '#eab308', '#22c55e'] },
    hole: 0.45,
    textinfo: 'percent+value',
  };

  /* ── Heatmap (top 20) ── */
  const top20 = scores.slice(0, 20);
  const heatZ = top20.map(sc => [
    sc.behavioral_score, sc.graph_score, sc.device_score,
    sc.temporal_score, sc.ml_anomaly_score,
  ]);
  const heatY = top20.map(sc => sc.account);
  const heatX = ['Behavioral', 'Graph', 'Device', 'Temporal', 'ML Anomaly'];

  return (
    <div>
      {/* Metric cards */}
      <div className="metric-grid cols-5">
        <div className="metric-card critical">
          <div className="value">{s.critical_count}</div>
          <div className="label"> CRITICAL</div>
        </div>
        <div className="metric-card high">
          <div className="value">{s.high_count}</div>
          <div className="label"> HIGH RISK</div>
        </div>
        <div className="metric-card medium">
          <div className="value">{s.medium_count}</div>
          <div className="label"> MEDIUM</div>
        </div>
        <div className="metric-card low">
          <div className="value">{s.low_count}</div>
          <div className="label"> LOW</div>
        </div>
        <div className="metric-card info">
          <div className="value">{s.max_score}</div>
          <div className="label"> HIGHEST SCORE</div>
        </div>
      </div>

      {/* Charts row */}
      <div className="grid-row cols-3-2">
        <div className="chart-container">
          <h3>Risk Score Distribution</h3>
          <Plot
            data={histTraces}
            layout={{
              ...DARK_LAYOUT,
              height: 350,
              bargap: 0.05,
              barmode: 'stack',
              showlegend: true,
              legend: { orientation: 'h', y: 1.12 },
            }}
            config={{ responsive: true, displayModeBar: false }}
            style={{ width: '100%' }}
          />
        </div>
        <div className="chart-container">
          <h3>Risk Level Breakdown</h3>
          <Plot
            data={[pieTrace]}
            layout={{
              ...DARK_LAYOUT,
              height: 350,
              legend: { orientation: 'h', y: -0.1 },
            }}
            config={{ responsive: true, displayModeBar: false }}
            style={{ width: '100%' }}
          />
        </div>
      </div>

      {/* Signal heatmap */}
      <div className="chart-container" style={{ marginTop: '1.2rem' }}>
        <h3>Detection Signal Heatmap — Top 20 Risky Accounts</h3>
        <Plot
          data={[{
            type: 'heatmap',
            z: heatZ,
            x: heatX,
            y: heatY,
            colorscale: 'YlOrRd',
            hovertemplate: '%{y}<br>%{x}: %{z}<extra></extra>',
          }]}
          layout={{ ...DARK_LAYOUT, height: 450, yaxis: { autorange: 'reversed' } }}
          config={{ responsive: true, displayModeBar: false }}
          style={{ width: '100%' }}
        />
      </div>

      {/* Key stats */}
      {/* <h3 style={{ marginTop: '1.5rem' }}>Key Statistics</h3>
      <div className="metric-grid cols-4" style={{ marginTop: '0.6rem' }}>
        <div className="metric-card info">
          <div className="value">{s.total_accounts}</div>
          <div className="label">Total Accounts</div>
        </div>
        <div className="metric-card info">
          <div className="value">{s.total_transactions}</div>
          <div className="label">Total Transactions</div>
        </div>
        <div className="metric-card info">
          <div className="value">{s.max_score}</div>
          <div className="label">Max Risk Score</div>
        </div>
        <div className="metric-card info">
          <div className="value">{s.median_score}</div>
          <div className="label">Median Score</div>
        </div>
      </div> */}
    </div>
  );
}
