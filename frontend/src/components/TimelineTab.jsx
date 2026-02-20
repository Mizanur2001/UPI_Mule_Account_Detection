import React, { useState, useEffect } from 'react';
import Plot from 'react-plotly.js';
import { fetchTimelineData } from '../api';
import Icon from './Icon';

const DARK_LAYOUT = {
  paper_bgcolor: 'rgba(0,0,0,0)',
  plot_bgcolor: 'rgba(0,0,0,0)',
  margin: { l: 50, r: 50, t: 40, b: 50 },
  font: { color: '#1f2937', family: 'Inter, sans-serif', size: 12 },
};

const RISK_COLORS = {
  CRITICAL: '#ef4444', HIGH: '#f97316', MEDIUM: '#eab308',
  LOW: '#22c55e', UNKNOWN: '#475569',
};

export default function TimelineTab() {
  const [timeline, setTimeline] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchTimelineData()
      .then(d => { setTimeline(d); setLoading(false); })
      .catch(() => setLoading(false));
  }, []);

  if (loading) return <p style={{ color: '#6b7280' }}>Loading timeline data...</p>;
  if (!timeline || timeline.error) return (
    <div className="info-box warning">No timestamp data available in transactions.</div>
  );

  const { transactions, hourly, heatmap } = timeline;

  const volumeTraces = [
    {
      type: 'bar',
      x: hourly.map(h => h.hour),
      y: hourly.map(h => h.count),
      name: 'Transaction Count',
      marker: { color: '#6366f1', opacity: 0.7 },
    },
    {
      type: 'scatter', mode: 'lines',
      x: hourly.map(h => h.hour),
      y: hourly.map(h => h.volume),
      name: 'Volume (₹)',
      line: { color: '#ff9800', width: 2 },
      yaxis: 'y2',
    },
  ];

  const riskScatterTraces = ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW', 'UNKNOWN'].map(lvl => {
    const pts = transactions.filter(t => t.sender_risk === lvl);
    return {
      type: 'scatter', mode: 'markers',
      x: pts.map(t => t.timestamp),
      y: pts.map(t => t.amount),
      name: lvl,
      marker: {
        color: RISK_COLORS[lvl],
        size: pts.map(t => Math.min(Math.max(t.amount / 500, 4), 15)),
      },
      text: pts.map(t => `${t.sender} → ${t.receiver}`),
      hoverinfo: 'text+x+y',
    };
  }).filter(t => t.x.length > 0);

  const heatmapTrace = {
    type: 'heatmap',
    z: heatmap.values,
    x: heatmap.hours,
    y: heatmap.days,
    colorscale: 'RdYlBu',
    reversescale: true,
  };

  return (
    <div>
      <h2><Icon name="schedule" size={24} style={{ marginRight: 8 }} />Transaction Timeline &amp; Temporal Analysis</h2>

      <div className="grid-row cols-2">
        <div className="chart-container">
          <h3>Transaction Volume Over Time</h3>
          <Plot
            data={volumeTraces}
            layout={{
              ...DARK_LAYOUT, height: 380,
              yaxis: { title: 'Count' },
              yaxis2: { title: 'Volume (₹)', overlaying: 'y', side: 'right' },
              legend: { orientation: 'h', y: 1.1 },
            }}
            config={{ responsive: true, displayModeBar: false }}
            style={{ width: '100%' }}
          />
        </div>

        <div className="chart-container">
          <h3>Risk-Level Transaction Breakdown</h3>
          <Plot
            data={riskScatterTraces}
            layout={{
              ...DARK_LAYOUT, height: 380,
              legend: { orientation: 'h', y: 1.1 },
            }}
            config={{ responsive: true, displayModeBar: false }}
            style={{ width: '100%' }}
          />
        </div>
      </div>

      <div className="chart-container" style={{ marginTop: '1.2rem' }}>
        <h3>Hour-of-Day Activity Heatmap</h3>
        <Plot
          data={[heatmapTrace]}
          layout={{
            ...DARK_LAYOUT, height: 300,
            xaxis: { title: 'Hour of Day' },
            yaxis: { title: 'Day of Week' },
          }}
          config={{ responsive: true, displayModeBar: false }}
          style={{ width: '100%' }}
        />
      </div>
    </div>
  );
}
