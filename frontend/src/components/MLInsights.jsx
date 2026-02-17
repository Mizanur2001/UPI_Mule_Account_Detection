import React, { useMemo } from 'react';
import Plot from 'react-plotly.js';
import Icon from './Icon';

const DARK_LAYOUT = {
  // template: 'plotly_white',
  paper_bgcolor: 'rgba(0,0,0,0)',
  plot_bgcolor: 'rgba(0,0,0,0)',
  margin: { l: 50, r: 20, t: 40, b: 50 },
  font: { color: '#1f2937', family: 'Inter, sans-serif', size: 12 },
};

const ML_COLORS = { ANOMALOUS: '#ef4444', SUSPICIOUS: '#f97316', NORMAL: '#22c55e' };

export default function MLInsights({ data }) {
  const scores = data.scores;

  /* ── ML scatter (by label, preserving index) ── */
  const mlTraces = useMemo(() => {
    const indexed = scores.map((s, i) => ({ ...s, idx: i }));
    return ['ANOMALOUS', 'SUSPICIOUS', 'NORMAL'].map(label => {
      const pts = indexed.filter(s => s.ml_anomaly_label === label);
      return {
        type: 'scatter', mode: 'markers',
        x: pts.map(p => p.idx),
        y: pts.map(p => p.ml_anomaly_score),
        name: label,
        marker: { color: ML_COLORS[label] },
        text: pts.map(p => `${p.account}<br>Risk: ${p.risk_level}`),
        hoverinfo: 'text+y',
      };
    });
  }, [scores]);

  /* ── ML vs Rule-Based correlation ── */
  const corrTrace = {
    type: 'scatter', mode: 'markers',
    x: scores.map(s => s.risk_score),
    y: scores.map(s => s.ml_anomaly_score),
    marker: { color: '#6366f1', opacity: 0.7 },
    hovertext: scores.map(s => s.account),
    hoverinfo: 'text+x+y',
  };

  /* ── Feature contribution bar ── */
  const avgVals = {
    'Behavioral (25%)': avg(scores, 'behavioral_score'),
    'Graph (40%)':      avg(scores, 'graph_score'),
    'Device (15%)':     avg(scores, 'device_score'),
    'Temporal (10%)':   avg(scores, 'temporal_score'),
    'ML Anomaly (10%)': avg(scores, 'ml_anomaly_score'),
  };
  const barTrace = {
    type: 'bar',
    x: Object.keys(avgVals),
    y: Object.values(avgVals),
    marker: { color: ['#f97316', '#3b82f6', '#eab308', '#22c55e', '#8b5cf6'] },
  };

  return (
    <div>
      <h2><Icon name="psychology" size={24} style={{ marginRight: 8 }} />Machine Learning Anomaly Detection</h2>
      <p style={{ color: '#4b5563', marginBottom: '1rem', lineHeight: 1.7 }}>
        Our system uses an <strong>ensemble approach</strong> combining a custom-built{' '}
        <strong>Isolation Forest</strong> (unsupervised) with <strong>Z-score statistical
        outlier detection</strong> — requiring <strong>zero labeled fraud data</strong>.
        This makes it deployable from day one in any UPI ecosystem.
      </p>

      <div className="grid-row cols-2">
        <div className="chart-container">
          <h3>Isolation Forest vs Z-Score</h3>
          <Plot
            data={mlTraces}
            layout={{
              ...DARK_LAYOUT, height: 400,
              xaxis: { title: 'Account Index' },
              yaxis: { title: 'ML Anomaly Score' },
              shapes: [
                { type: 'line', x0: 0, x1: scores.length, y0: 70, y1: 70,
                  line: { color: '#ef4444', dash: 'dash', width: 1 } },
                { type: 'line', x0: 0, x1: scores.length, y0: 45, y1: 45,
                  line: { color: '#f97316', dash: 'dash', width: 1 } },
              ],
              annotations: [
                { x: scores.length * 0.85, y: 72, text: 'Anomalous Threshold',
                  showarrow: false, font: { color: '#ef4444', size: 10 } },
                { x: scores.length * 0.85, y: 47, text: 'Suspicious Threshold',
                  showarrow: false, font: { color: '#f97316', size: 10 } },
              ],
            }}
            config={{ responsive: true, displayModeBar: false }}
            style={{ width: '100%' }}
          />
        </div>

        <div className="chart-container">
          <h3>ML vs Rule-Based Correlation</h3>
          <Plot
            data={[corrTrace]}
            layout={{
              ...DARK_LAYOUT, height: 400,
              xaxis: { title: 'Rule-Based Score' },
              yaxis: { title: 'ML Score' },
              showlegend: false,
            }}
            config={{ responsive: true, displayModeBar: false }}
            style={{ width: '100%' }}
          />
        </div>
      </div>

      {/* Feature contribution */}
      <div className="chart-container" style={{ marginTop: '1.2rem' }}>
        <h3>Feature Contribution Analysis</h3>
        <Plot
          data={[barTrace]}
          layout={{
            ...DARK_LAYOUT, height: 350,
            xaxis: { title: 'Detection Signal' },
            yaxis: { title: 'Average Score' },
            showlegend: false,
          }}
          config={{ responsive: true, displayModeBar: false }}
          style={{ width: '100%' }}
        />
      </div>

      <div className="info-box info" style={{ marginTop: '1rem' }}>
        <strong>Innovation:</strong> Our Isolation Forest is implemented from scratch in pure NumPy —
        no scikit-learn dependency. This makes the model portable, lightweight (~200 lines),
        and production-ready for edge deployment on payment gateways.
      </div>
    </div>
  );
}

function avg(arr, key) {
  if (arr.length === 0) return 0;
  return arr.reduce((sum, item) => sum + (item[key] || 0), 0) / arr.length;
}
