import React, { useState, useEffect, useMemo } from 'react';
import { fetchReport, downloadFile } from '../api';
import Icon from './Icon';

export default function Alerts({ data }) {
  const [expandedAccounts, setExpandedAccounts] = useState({});
  const [report, setReport] = useState(null);
  const [reportLoading, setReportLoading] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [levelFilter, setLevelFilter] = useState('ALL');

  const allAlerts = data.scores.filter(s => ['CRITICAL', 'HIGH'].includes(s.risk_level));

  const alerts = useMemo(() => {
    return allAlerts
      .filter(a => levelFilter === 'ALL' || a.risk_level === levelFilter)
      .filter(a => !searchQuery || a.account.toLowerCase().includes(searchQuery.toLowerCase())
        || a.recommended_action.toLowerCase().includes(searchQuery.toLowerCase())
        || a.reasons.some(r => r.toLowerCase().includes(searchQuery.toLowerCase()))
      );
  }, [allAlerts, searchQuery, levelFilter]);

  const critCount = allAlerts.filter(a => a.risk_level === 'CRITICAL').length;
  const highCount = allAlerts.filter(a => a.risk_level === 'HIGH').length;

  const toggleExpanded = (acc) => {
    setExpandedAccounts(prev => ({ ...prev, [acc]: !prev[acc] }));
  };

  useEffect(() => {
    const expanded = {};
    allAlerts.forEach(a => {
      if (a.risk_level === 'CRITICAL') expanded[a.account] = true;
    });
    setExpandedAccounts(expanded);
  }, []);

  const handleGenerateReport = () => {
    setReportLoading(true);
    fetchReport()
      .then(d => { setReport(d.report); setReportLoading(false); })
      .catch(() => setReportLoading(false));
  };

  const handleDownloadReport = () => {
    if (!report) return;
    const now = new Date().toISOString().slice(0, 10);
    downloadFile(report, `investigation_report_${now}.md`, 'text/markdown');
  };

  return (
    <div>
      <h2><Icon name="notifications_active" size={24} style={{ marginRight: 8 }} />Alert Management Console</h2>

      {/* Summary counters */}
      <div className="alert-summary-bar">
        <div className="alert-summary-stat critical">
          <Icon name="error" size={20} />
          <div>
            <span className="alert-summary-count">{critCount}</span>
            <span className="alert-summary-label">Critical</span>
          </div>
        </div>
        <div className="alert-summary-stat high">
          <Icon name="warning" size={20} />
          <div>
            <span className="alert-summary-count">{highCount}</span>
            <span className="alert-summary-label">High</span>
          </div>
        </div>
        <div className="alert-summary-stat total">
          <Icon name="notifications" size={20} />
          <div>
            <span className="alert-summary-count">{allAlerts.length}</span>
            <span className="alert-summary-label">Total Alerts</span>
          </div>
        </div>
      </div>

      {/* Search + filter bar */}
      <div className="alert-toolbar">
        <div className="alert-search">
          <Icon name="search" size={18} />
          <input
            type="text"
            placeholder="Search alerts by account, action, or evidence..."
            value={searchQuery}
            onChange={e => setSearchQuery(e.target.value)}
          />
          {searchQuery && (
            <button className="alert-search-clear" onClick={() => setSearchQuery('')}>
              <Icon name="close" size={16} />
            </button>
          )}
        </div>
        <div className="alert-filter-group">
          {['ALL', 'CRITICAL', 'HIGH'].map(lvl => (
            <button
              key={lvl}
              className={`alert-filter-btn ${levelFilter === lvl ? 'active' : ''} ${lvl.toLowerCase()}`}
              onClick={() => setLevelFilter(lvl)}
            >
              {lvl === 'ALL' ? 'All' : lvl}
              {lvl !== 'ALL' && <span className="alert-filter-count">{lvl === 'CRITICAL' ? critCount : highCount}</span>}
            </button>
          ))}
        </div>
      </div>

      {/* Results info */}
      <p style={{ margin: '0.6rem 0 0.4rem', color: 'var(--text-muted)', fontSize: '0.82rem' }}>
        Showing <strong>{alerts.length}</strong> of {allAlerts.length} alerts
        {searchQuery && <> matching “<em>{searchQuery}</em>”</>}
      </p>

      {/* Alert cards */}
      {alerts.length === 0 && searchQuery && (
        <div className="info-box info">
          <Icon name="search_off" size={16} style={{ marginRight: 6 }} /> No alerts match your search.
        </div>
      )}

      {alerts.map(a => (
        <div key={a.account}
             className={`expander ${a.risk_level === 'CRITICAL' ? 'critical-border' : 'high-border'}`}>
          <div className="expander-header" onClick={() => toggleExpanded(a.account)}>
            <div className="alert-expander-left">
              <span className={`risk-badge ${a.risk_level}`}>{a.risk_level}</span>
              <span className="alert-expander-account">{a.account}</span>
              <span className="alert-expander-score">Score: {a.risk_score}/100</span>
            </div>
            <span className={`arrow ${expandedAccounts[a.account] ? 'open' : ''}`}>▸</span>
          </div>
          {expandedAccounts[a.account] && (
            <div className="expander-body">
              <div className="metric-grid cols-4" style={{ marginBottom: '0.8rem' }}>
                <div className="metric-card info">
                  <div className="value">{a.risk_score}</div>
                  <div className="label">Risk Score</div>
                </div>
                <div className="metric-card info">
                  <div className="value">{a.confidence}</div>
                  <div className="label">Confidence</div>
                </div>
                <div className="metric-card info">
                  <div className="value">{a.signal_count}</div>
                  <div className="label">Signals</div>
                </div>
                <div className="metric-card info">
                  <div className="value">{Math.round(a.ml_anomaly_score)}</div>
                  <div className="label">ML Anomaly</div>
                </div>
              </div>
              <div className="alert-detail-action">
                <Icon name={a.risk_level === 'CRITICAL' ? 'block' : 'report'} size={16} />
                <div>
                  <span className="alert-detail-action-label">Recommended Action</span>
                  <span className="alert-detail-action-text">{a.recommended_action}</span>
                </div>
              </div>
              <div className="alert-detail-evidence">
                <span className="alert-detail-evidence-title">
                  <Icon name="description" size={14} /> Evidence ({a.reasons.length})
                </span>
                <ul>
                  {a.reasons.map((r, i) => (
                    <li key={i}>
                      <span className="alert-evidence-num">{i + 1}</span>
                      {r}
                    </li>
                  ))}
                </ul>
              </div>
            </div>
          )}
        </div>
      ))}

      {/* Report generation */}
      <hr className="divider" />
      <h2><Icon name="assignment" size={24} style={{ marginRight: 8 }} />Generate Investigation Report</h2>

      <button className="btn btn-primary" onClick={handleGenerateReport}
              disabled={reportLoading} style={{ marginBottom: '1rem' }}>
        {reportLoading ? 'Generating...' : <><Icon name="assignment" size={16} style={{ marginRight: 4 }} /> Generate Report</>}
      </button>

      {report && (
        <>
          <div className="report-container">
            <pre style={{ whiteSpace: 'pre-wrap', color: 'var(--text-secondary)', fontFamily: 'inherit', margin: 0 }}>
              {report}
            </pre>
          </div>
          <button className="btn btn-download" onClick={handleDownloadReport}
                  style={{ marginTop: '0.8rem' }}>
            <Icon name="download" size={16} style={{ marginRight: 4 }} /> Download Report (MD)
          </button>
        </>
      )}
    </div>
  );
}
