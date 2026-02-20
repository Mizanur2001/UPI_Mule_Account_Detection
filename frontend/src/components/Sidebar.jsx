import React from 'react';
import Icon from './Icon';

export default function Sidebar({ data, onToggle }) {
  const s = data.summary;
  const signals = [
    { name: 'Behavioral', weight: '25%', status: <Icon name="check_circle" size={16} color="#22c55e" /> },
    { name: 'Graph',      weight: '40%', status: <Icon name="check_circle" size={16} color="#22c55e" /> },
    { name: 'Device',     weight: '15%', status: <Icon name="check_circle" size={16} color="#22c55e" /> },
    { name: 'Temporal',   weight: '10%', status: <Icon name="check_circle" size={16} color="#22c55e" /> },
    { name: 'ML Anomaly', weight: '10%', status: <Icon name="check_circle" size={16} color="#22c55e" /> },
  ];

  return (
    <aside className="sidebar">
      <div className="sidebar-logo">
        <div className="logo-icon"><Icon name="shield" size={32} /></div>
        <h3>Control Panel</h3>
        <button
          className="sidebar-collapse-btn"
          onClick={onToggle}
          title="Hide Sidebar"
          aria-label="Hide Sidebar"
        >
          <Icon name="chevron_left" size={20} />
        </button>
      </div>
      <div className="divider" />

      <div className="section-label">System Status</div>
      <div className="status-badge success">● Detection Engine: Online</div>
      <div className="status-badge info"><Icon name="monitoring" size={16} /> {s.total_accounts} accounts monitored</div>
      <div className="status-badge info"><Icon name="credit_card" size={16} /> {s.total_transactions} transactions analyzed</div>
      <div className="status-badge info"><Icon name="hub" size={16} /> {s.graph_nodes} nodes · {s.graph_edges} edges</div>

      <div className="divider" />

      <div className="section-label">Active Alerts</div>
      {s.critical_count > 0 && (
        <div className="status-badge error"><Icon name="circle" size={12} color="#ef4444" /> {s.critical_count} CRITICAL accounts</div>
      )}
      {s.high_count > 0 && (
        <div className="status-badge warning"><Icon name="circle" size={12} color="#f97316" /> {s.high_count} HIGH risk accounts</div>
      )}
      <span className="caption"><Icon name="circle" size={12} color="#eab308" /> {s.medium_count} MEDIUM · <Icon name="circle" size={12} color="#22c55e" /> {s.low_count} LOW</span>

      <div className="divider" />

      <div className="version-label">UPI Mule Detection v2.0 · CSIC 1.0</div>
    </aside>
  );
}
