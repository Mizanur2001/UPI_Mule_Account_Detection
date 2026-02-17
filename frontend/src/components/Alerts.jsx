import React, { useState, useEffect } from 'react';
import { fetchReport, downloadFile } from '../api';
import Icon from './Icon';

export default function Alerts({ data }) {
  const [expandedAccounts, setExpandedAccounts] = useState({});
  const [report, setReport] = useState(null);
  const [reportLoading, setReportLoading] = useState(false);

  const alerts = data.scores.filter(s => ['CRITICAL', 'HIGH'].includes(s.risk_level));

  const toggleExpanded = (acc) => {
    setExpandedAccounts(prev => ({ ...prev, [acc]: !prev[acc] }));
  };

  // Auto-expand CRITICAL accounts
  useEffect(() => {
    const expanded = {};
    alerts.forEach(a => {
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

      {alerts.length > 0 ? (
        <div className="info-box error">
          <strong>{alerts.length} active alerts</strong> requiring immediate attention
        </div>
      ) : (
        <div className="info-box success">
          <Icon name="check_circle" size={16} color="#22c55e" /> No critical or high-risk alerts at this time.
        </div>
      )}

      {alerts.map(a => (
        <div key={a.account}
             className={`expander ${a.risk_level === 'CRITICAL' ? 'critical-border' : 'high-border'}`}>
          <div className="expander-header" onClick={() => toggleExpanded(a.account)}>
            <span><Icon name="warning" size={16} color="#f97316" /> {a.account} — Score: {a.risk_score}/100</span>
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
              <p style={{ color: '#e0e0e0', marginBottom: '0.5rem' }}>
                <strong>Recommended Action:</strong> {a.recommended_action}
              </p>
              <p style={{ color: '#ccc', fontWeight: 600, marginBottom: '0.3rem' }}>Evidence:</p>
              <ul style={{ paddingLeft: '1.2rem', color: '#bbb' }}>
                {a.reasons.map((r, i) => <li key={i} style={{ marginBottom: '0.2rem' }}>{r}</li>)}
              </ul>
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
            <pre style={{ whiteSpace: 'pre-wrap', color: '#ccc', fontFamily: 'inherit', margin: 0 }}>
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
