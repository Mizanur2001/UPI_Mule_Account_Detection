import React, { useState, useMemo } from 'react';
import Plot from 'react-plotly.js';
import { downloadFile } from '../api';
import Icon from './Icon';

const DARK_LAYOUT = {
  // template: 'plotly_white',
  paper_bgcolor: 'rgba(0,0,0,0)',
  plot_bgcolor: 'rgba(0,0,0,0)',
  margin: { l: 40, r: 40, t: 40, b: 40 },
  font: { color: '#1f2937', family: 'Inter, sans-serif', size: 12 },
};

const SORT_OPTIONS = [
  { label: 'Risk Score (H→L)', col: 'risk_score', asc: false },
  { label: 'Risk Score (L→H)', col: 'risk_score', asc: true },
  { label: 'Behavioral',       col: 'behavioral_score', asc: false },
  { label: 'Graph',            col: 'graph_score', asc: false },
  { label: 'Device',           col: 'device_score', asc: false },
  { label: 'Temporal',         col: 'temporal_score', asc: false },
  { label: 'ML Anomaly',       col: 'ml_anomaly_score', asc: false },
];

export default function RiskAnalysis({ data }) {
  const [selectedLevels, setSelectedLevels] = useState(['CRITICAL', 'HIGH', 'MEDIUM', 'LOW']);
  const [minScore, setMinScore] = useState(0);
  const [sortIndex, setSortIndex] = useState(0);
  const [selectedAccount, setSelectedAccount] = useState('');
  const [searchQuery, setSearchQuery] = useState('');

  const filtered = useMemo(() => {
    const sort = SORT_OPTIONS[sortIndex];
    return data.scores
      .filter(s => selectedLevels.includes(s.risk_level) && s.risk_score >= minScore)
      .filter(s => !searchQuery || s.account.toLowerCase().includes(searchQuery.toLowerCase()))
      .sort((a, b) => sort.asc ? a[sort.col] - b[sort.col] : b[sort.col] - a[sort.col]);
  }, [data.scores, selectedLevels, minScore, sortIndex, searchQuery]);

  const drillAccount = selectedAccount || (filtered.length > 0 ? filtered[0].account : null);
  const drillData = drillAccount ? data.scores.find(s => s.account === drillAccount) : null;

  const toggleLevel = (lvl) => {
    setSelectedLevels(prev =>
      prev.includes(lvl) ? prev.filter(l => l !== lvl) : [...prev, lvl]
    );
  };

  const handleExport = () => {
    const header = 'Account,Risk Score,Risk Level,Confidence,Behavioral,Graph,Device,Temporal,ML Anomaly,Signals,Top Reason';
    const rows = filtered.map(s =>
      `${s.account},${s.risk_score},${s.risk_level},${s.confidence},${s.behavioral_score},${s.graph_score},${s.device_score},${s.temporal_score},${s.ml_anomaly_score},${s.signal_count},"${s.top_reason}"`
    );
    const csv = [header, ...rows].join('\n');
    const now = new Date().toISOString().slice(0, 16).replace(/[-:T]/g, '');
    downloadFile(csv, `mule_risk_${now}.csv`, 'text/csv');
  };

  return (
    <div>
      <h2><Icon name="crisis_alert" size={24} style={{ marginRight: 8 }} />Account Risk Scoring &amp; Investigation</h2>

      {/* Filters */}
      <div className="grid-row cols-2" style={{ gap: '1rem', marginBottom: '0.5rem' }}>
        <div className="form-group">
          <label><Icon name="search" size={16} style={{ marginRight: 4 }} />Search Account</label>
          <input
            type="text"
            placeholder="Type to search accounts..."
            value={searchQuery}
            onChange={e => setSearchQuery(e.target.value)}
            style={{
              width: '100%', padding: '0.55rem 0.8rem',
              border: '1px solid var(--border-subtle)',
              borderRadius: 'var(--radius-sm)',
              fontSize: '0.9rem', fontFamily: 'inherit',
            }}
          />
        </div>
        <div className="form-group">
          <label>Filter by Risk Level</label>
          <div className="multiselect">
            {['CRITICAL', 'HIGH', 'MEDIUM', 'LOW'].map(lvl => (
              <label key={lvl}>
                <input
                  type="checkbox"
                  checked={selectedLevels.includes(lvl)}
                  onChange={() => toggleLevel(lvl)}
                />
                {lvl}
              </label>
            ))}
          </div>
        </div>
      </div>
      <div className="grid-row cols-2" style={{ gap: '1rem' }}>
        <div className="form-group">
          <label>Minimum Risk Score: {minScore}</label>
          <input type="range" min={0} max={100} value={minScore}
                 onChange={e => setMinScore(Number(e.target.value))} />
        </div>
        <div className="form-group">
          <label>Sort by</label>
          <select value={sortIndex} onChange={e => setSortIndex(Number(e.target.value))}>
            {SORT_OPTIONS.map((opt, i) => (
              <option key={i} value={i}>{opt.label}</option>
            ))}
          </select>
        </div>
      </div>

      <p style={{ margin: '0.8rem 0 0.4rem', color: '#6b7280' }}>
        <strong>Showing {filtered.length} of {data.scores.length} accounts</strong>
      </p>

      {/* Data Table */}
      <div className="data-table-wrapper">
        <table className="data-table">
          <thead>
            <tr>
              <th>Account</th><th>Risk Score</th><th>Risk Level</th><th>Confidence</th>
              <th>Behavioral</th><th>Graph</th><th>Device</th><th>Temporal</th>
              <th>ML Anomaly</th><th>Signals</th><th>Top Reason</th>
            </tr>
          </thead>
          <tbody>
            {filtered.map(s => (
              <tr key={s.account}>
                <td>{s.account}</td>
                <td>{s.risk_score}</td>
                <td><span className={`risk-badge ${s.risk_level}`}>{s.risk_level}</span></td>
                <td>{s.confidence}</td>
                <td>{s.behavioral_score}</td>
                <td>{s.graph_score}</td>
                <td>{s.device_score}</td>
                <td>{s.temporal_score}</td>
                <td>{s.ml_anomaly_score}</td>
                <td>{s.signal_count}</td>
                <td>{s.top_reason}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Drill-down */}
      <hr className="divider" />
      <h2><Icon name="search" size={24} style={{ marginRight: 8 }} />Forensic Drill-Down</h2>

      <div className="form-group" style={{ maxWidth: 400 }}>
        <label>Select account</label>
        <select value={drillAccount || ''} onChange={e => setSelectedAccount(e.target.value)}>
          {filtered.map(s => (
            <option key={s.account} value={s.account}>{s.account}</option>
          ))}
        </select>
      </div>

      {drillData && (
        <div className="grid-row cols-2-3" style={{ marginTop: '1rem' }}>
          {/* Left: metrics */}
          <div>
            <div className="metric-grid cols-2" style={{ gap: '0.8rem' }}>
              <div className="metric-card info">
                <div className="value">{drillData.risk_score}/100</div>
                <div className="label">Risk Score</div>
              </div>
              <div className="metric-card info">
                <div className="value">
                  {{'CRITICAL':<Icon name="circle" size={14} color="#ef4444" />,'HIGH':<Icon name="circle" size={14} color="#f97316" />,'MEDIUM':<Icon name="circle" size={14} color="#eab308" />,'LOW':<Icon name="circle" size={14} color="#22c55e" />}[drillData.risk_level]} {drillData.risk_level}
                </div>
                <div className="label">Risk Level</div>
              </div>
              <div className="metric-card info">
                <div className="value">{drillData.confidence}</div>
                <div className="label">Confidence</div>
              </div>
              <div className="metric-card info">
                <div className="value">{drillData.signal_count}</div>
                <div className="label">Active Signals</div>
              </div>
            </div>
            <div className="info-box info" style={{ marginTop: '0.8rem' }}>
              <strong>Action:</strong> {drillData.recommended_action}
            </div>
          </div>

          {/* Right: radar chart */}
          <div className="chart-container">
            <Plot
              data={[{
                type: 'scatterpolar',
                r: [
                  drillData.behavioral_score, drillData.graph_score,
                  drillData.device_score, drillData.temporal_score,
                  drillData.ml_anomaly_score, drillData.behavioral_score,
                ],
                theta: ['Behavioral', 'Graph', 'Device', 'Temporal', 'ML Anomaly', 'Behavioral'],
                fill: 'toself',
                fillcolor: 'rgba(99,102,241,0.2)',
                line: { color: '#6366f1', width: 2 },
                name: drillData.account,
              }]}
              layout={{
                ...DARK_LAYOUT,
                height: 350,
                polar: {
                  radialaxis: { visible: true, range: [0, 100] },
                  bgcolor: 'rgba(0,0,0,0)',
                },
                title: { text: `Signal Breakdown — ${drillData.account}`, font: { size: 13, color: '#e0e0e0' } },
              }}
              config={{ responsive: true, displayModeBar: false }}
              style={{ width: '100%' }}
            />
          </div>
        </div>
      )}

      {/* Evidence */}
      {drillData && (
        <>
          <h3 style={{ marginTop: '1.2rem' }}><Icon name="assignment" size={20} style={{ marginRight: 6 }} />Evidence Trail</h3>
          {drillData.reasons.length > 0 ? (
            drillData.reasons.map((r, i) => (
              <div className="evidence-item" key={i}><Icon name="arrow_right" size={16} color="#f97316" /> {r}</div>
            ))
          ) : (
            <div className="info-box success">
              No risk factors identified — account appears legitimate.
            </div>
          )}
        </>
      )}

      {/* Export */}
      <hr className="divider" />
      <button className="btn btn-download" onClick={handleExport}>
        <Icon name="download" size={18} style={{ marginRight: 6 }} /> Export Results (CSV)
      </button>
    </div>
  );
}
