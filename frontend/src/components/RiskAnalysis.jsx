import React, { useState, useMemo } from 'react';
import Plot from 'react-plotly.js';
import { downloadFile } from '../api';
import Icon from './Icon';

const DARK_LAYOUT = {
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

      <div className="data-table-wrapper risk-table-wrapper">
        <table className="data-table risk-table">
          <thead>
            <tr>
              <th>Account</th><th>Score</th><th>Level</th>
              <th>Behavioral</th><th>Graph</th><th>Device</th><th>Temporal</th>
              <th>ML</th><th>Signals</th><th>Action</th>
            </tr>
          </thead>
          <tbody>
            {filtered.map(s => (
              <React.Fragment key={s.account}>
                <tr
                  className={`clickable-row ${selectedAccount === s.account ? 'row-active' : ''}`}
                  onClick={() => setSelectedAccount(selectedAccount === s.account ? '' : s.account)}
                  title="Click to view forensic report"
                >
                  <td>{s.account}</td>
                  <td><strong>{s.risk_score}</strong></td>
                  <td><span className={`risk-badge ${s.risk_level}`}>{s.risk_level}</span></td>
                  <td>{s.behavioral_score}</td>
                  <td>{s.graph_score}</td>
                  <td>{s.device_score}</td>
                  <td>{s.temporal_score}</td>
                  <td>{s.ml_anomaly_score}</td>
                  <td>{s.signal_count}</td>
                  <td className="action-cell">{s.recommended_action}</td>
                </tr>
                {selectedAccount === s.account && (
                  <tr className="inline-forensic-row">
                    <td colSpan={10}>
                      <div className="inline-forensic">
                        <div className="inline-forensic-grid">
                          <div className="inline-overview-card">
                            <h4 className="inline-section-title">Overview</h4>
                            <div className={`inline-overview-body ${s.risk_level.toLowerCase()}`}>
                              <div className="inline-overview-row">
                                <span className="inline-overview-label">Risk Level:</span>
                                <span className="inline-overview-value">{s.risk_level}</span>
                              </div>
                              <div className="inline-overview-row">
                                <span className="inline-overview-label">Confidence:</span>
                                <span className="inline-overview-value">{s.confidence}</span>
                              </div>
                              <div className="inline-overview-row">
                                <span className="inline-overview-label">Action:</span>
                                <span className="inline-overview-value">{s.recommended_action}</span>
                              </div>
                              <div className="inline-overview-row">
                                <span className="inline-overview-label">Signals:</span>
                                <span className="inline-overview-value">{s.signal_count} active</span>
                              </div>
                              {s.reasons && s.reasons.length > 0 && (
                                <div className="inline-overview-reasons">
                                  <span className="inline-overview-label">Reasons:</span>
                                  <ul className="inline-reasons-list">
                                    {s.reasons.map((r, i) => (
                                      <li key={i}>{r}</li>
                                    ))}
                                  </ul>
                                </div>
                              )}
                            </div>
                          </div>

                          <div className="inline-radar-card">
                            <h4 className="inline-section-title">Signal Breakdown — {s.account}</h4>
                            <Plot
                              data={[{
                                type: 'scatterpolar',
                                r: [
                                  s.behavioral_score, s.graph_score,
                                  s.device_score, s.temporal_score,
                                  s.ml_anomaly_score, s.behavioral_score,
                                ],
                                theta: ['Behavioral', 'Graph', 'Device', 'Temporal', 'ML Anomaly', 'Behavioral'],
                                fill: 'toself',
                                fillcolor: s.risk_level === 'CRITICAL' ? 'rgba(199,80,80,0.25)' :
                                           s.risk_level === 'HIGH' ? 'rgba(212,138,90,0.25)' :
                                           s.risk_level === 'MEDIUM' ? 'rgba(184,160,64,0.25)' :
                                           'rgba(74,158,106,0.25)',
                                line: {
                                  color: s.risk_level === 'CRITICAL' ? '#c75050' :
                                         s.risk_level === 'HIGH' ? '#d48a5a' :
                                         s.risk_level === 'MEDIUM' ? '#b8a040' : '#4a9e6a',
                                  width: 2,
                                },
                                name: s.account,
                              }]}
                              layout={{
                                ...DARK_LAYOUT,
                                height: 320,
                                margin: { l: 60, r: 60, t: 30, b: 30 },
                                polar: {
                                  radialaxis: { visible: true, range: [0, 100], tickfont: { size: 10 } },
                                  angularaxis: { tickfont: { size: 12 } },
                                  bgcolor: 'rgba(0,0,0,0)',
                                },
                                showlegend: false,
                              }}
                              config={{ responsive: true, displayModeBar: false }}
                              style={{ width: '100%' }}
                            />
                          </div>
                        </div>
                      </div>
                    </td>
                  </tr>
                )}
              </React.Fragment>
            ))}
          </tbody>
        </table>
      </div>

      <hr className="divider" />
      <button className="btn btn-download" onClick={handleExport}>
        <Icon name="download" size={18} style={{ marginRight: 6 }} /> Export Results (CSV)
      </button>
    </div>
  );
}
