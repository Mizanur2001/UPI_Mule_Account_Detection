import React, { useState } from 'react';
import { scoreAccount, simulateTransaction } from '../api';
import Icon from './Icon';

export default function RealTimeAPI({ data }) {
  const accounts = data.unique_accounts;
  const [selAccount, setSelAccount] = useState(accounts[0] || '');
  const [scoreResult, setScoreResult] = useState(null);
  const [scoreLoading, setScoreLoading] = useState(false);

  const [simSender, setSimSender] = useState(accounts[0] || '');
  const [simReceiver, setSimReceiver] = useState(accounts[1] || '');
  const [simAmount, setSimAmount] = useState(5000);
  const [simResult, setSimResult] = useState(null);
  const [simLoading, setSimLoading] = useState(false);

  const handleScore = () => {
    setScoreLoading(true);
    setScoreResult(null);
    scoreAccount(selAccount)
      .then(r => { setScoreResult(r); setScoreLoading(false); })
      .catch(() => setScoreLoading(false));
  };

  const handleSimulate = () => {
    setSimLoading(true);
    setSimResult(null);
    simulateTransaction(simSender, simReceiver, simAmount)
      .then(r => { setSimResult(r); setSimLoading(false); })
      .catch(() => setSimLoading(false));
  };

  return (
    <div>
      <h2><Icon name="bolt" size={24} style={{ marginRight: 8 }} />Real-Time API &amp; Transaction Simulation</h2>
      <p style={{ color: '#4b5563', marginBottom: '1rem', lineHeight: 1.7 }}>
        In production, the scoring engine runs as a <strong>FastAPI microservice</strong> called by
        UPI payment gateways in real-time (&lt;50ms latency). Below you can simulate the API.
      </p>

      <hr className="divider" />

      <div className="grid-row cols-3-2">
        {/* Live API simulation */}
        <div>
          <h3><Icon name="science" size={20} style={{ marginRight: 6 }} />Live API Simulation</h3>
          <div className="form-group" style={{ marginBottom: '0.8rem' }}>
            <label>Select Account</label>
            <select value={selAccount} onChange={e => setSelAccount(e.target.value)}>
              {accounts.map(a => <option key={a} value={a}>{a}</option>)}
            </select>
          </div>
          <button className="btn btn-primary btn-block" onClick={handleScore} disabled={scoreLoading}>
            {scoreLoading ? 'Scoring...' : <><Icon name="search" size={16} style={{ marginRight: 4 }} /> Score Account</>}
          </button>

          {scoreResult && (
            <>
              <div className="info-box success" style={{ marginTop: '0.8rem' }}>
                <Icon name="check_circle" size={16} color="#22c55e" /> Response in {scoreResult.response_time_ms}ms
              </div>
              <div className="json-viewer" style={{ marginTop: '0.5rem' }}>
                {JSON.stringify(scoreResult, null, 2)}
              </div>
            </>
          )}
        </div>

        {/* Architecture */}
        <div>
          <h3><Icon name="architecture" size={20} style={{ marginRight: 6 }} />Architecture</h3>
          <pre className="code-block">{`UPI App / Payment Gateway
        │
        ▼
┌──────────────────────┐
│  FastAPI Backend     │
│  /score/{account_id} │
│  Response: <50ms     │
├──────────────────────┤
│  5-Signal Engine:    │
│  • Behavioral  (25%) │
│  • Graph       (40%) │
│  • Device      (15%) │
│  • Temporal    (10%) │
│  • ML Anomaly  (10%) │
├──────────────────────┤
│  Decision:           │
│ BLOCK / FLAG / ALLOW │
└──────────────────────┘`}</pre>
        </div>
      </div>

      <hr className="divider" />
      <h3><Icon name="cell_tower" size={20} style={{ marginRight: 6 }} />Transaction Simulation</h3>
      <p style={{ color: '#aaa', marginBottom: '0.8rem' }}>
        Simulate a UPI transaction and get real-time risk assessment for both parties.
      </p>

      <div className="grid-row cols-3">
        <div className="form-group">
          <label>Sender</label>
          <select value={simSender} onChange={e => setSimSender(e.target.value)}>
            {accounts.map(a => <option key={a} value={a}>{a}</option>)}
          </select>
        </div>
        <div className="form-group">
          <label>Receiver</label>
          <select value={simReceiver} onChange={e => setSimReceiver(e.target.value)}>
            {accounts.filter(a => a !== simSender).map(a => (
              <option key={a} value={a}>{a}</option>
            ))}
          </select>
        </div>
        <div className="form-group">
          <label>Amount (₹)</label>
          <input type="number" min={100} max={100000} value={simAmount}
                 onChange={e => setSimAmount(Number(e.target.value))} />
        </div>
      </div>

      <button className="btn btn-primary btn-block" onClick={handleSimulate}
              disabled={simLoading} style={{ marginTop: '0.8rem' }}>
        {simLoading ? 'Simulating...' : <><Icon name="bolt" size={16} style={{ marginRight: 4 }} /> Simulate Transaction</>}
      </button>

      {simResult && (
        <div style={{ marginTop: '1rem' }}>
          {simResult.decision === 'BLOCK' && (
            <div className="info-box error">
              <Icon name="block" size={16} color="#ef4444" /> <strong>TRANSACTION BLOCKED</strong> — {simResult.decision_reason}
            </div>
          )}
          {simResult.decision === 'FLAG' && (
            <div className="info-box warning">
              <Icon name="warning" size={16} color="#f97316" /> <strong>TRANSACTION FLAGGED</strong> — {simResult.decision_reason}
            </div>
          )}
          {simResult.decision === 'ALLOW' && (
            <div className="info-box success">
              <Icon name="check_circle" size={16} color="#22c55e" /> <strong>TRANSACTION ALLOWED</strong> — {simResult.decision_reason}
            </div>
          )}

          <div className="grid-row cols-2" style={{ marginTop: '0.8rem' }}>
            <div>
              <p style={{ fontWeight: 600, color: '#e0e0e0' }}>Sender: {simResult.transaction.sender}</p>
              <div className="metric-grid cols-2" style={{ gap: '0.6rem', marginTop: '0.5rem' }}>
                <div className="metric-card info">
                  <div className="value">{simResult.sender_risk.risk_score}</div>
                  <div className="label">Risk Score</div>
                </div>
                <div className="metric-card info">
                  <div className="value">{simResult.sender_risk.risk_level}</div>
                  <div className="label">Risk Level</div>
                </div>
              </div>
            </div>
            <div>
              <p style={{ fontWeight: 600, color: '#e0e0e0' }}>Receiver: {simResult.transaction.receiver}</p>
              <div className="metric-grid cols-2" style={{ gap: '0.6rem', marginTop: '0.5rem' }}>
                <div className="metric-card info">
                  <div className="value">{simResult.receiver_risk.risk_score}</div>
                  <div className="label">Risk Score</div>
                </div>
                <div className="metric-card info">
                  <div className="value">{simResult.receiver_risk.risk_level}</div>
                  <div className="label">Risk Level</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* API Endpoints table */}
      <hr className="divider" />
      <h3><Icon name="assignment" size={20} style={{ marginRight: 6 }} />API Endpoints</h3>
      <div className="data-table-wrapper" style={{ maxHeight: 'none' }}>
        <table className="data-table">
          <thead>
            <tr><th>Endpoint</th><th>Description</th><th>Latency</th></tr>
          </thead>
          <tbody>
            <tr><td>GET /score/&#123;account_id&#125;</td><td>Score a single account in real-time</td><td>&lt;50ms</td></tr>
            <tr><td>POST /batch_score</td><td>Batch score multiple accounts</td><td>&lt;500ms</td></tr>
            <tr><td>POST /simulate</td><td>Simulate a transaction and get risk decision</td><td>&lt;100ms</td></tr>
            <tr><td>GET /stats</td><td>System-wide risk statistics</td><td>&lt;1s</td></tr>
            <tr><td>GET /health</td><td>Health check and system status</td><td>&lt;10ms</td></tr>
          </tbody>
        </table>
      </div>

      <pre className="code-block" style={{ marginTop: '1rem' }}>{`# Start the API server
python -m uvicorn backend.app:app --reload --port 8000

# Score an account
curl http://127.0.0.1:8000/score/mule_aggregator@upi

# Simulate a transaction
curl -X POST http://127.0.0.1:8000/simulate \\
  -H "Content-Type: application/json" \\
  -d '{"sender": "customer_1@upi", "receiver": "mule_aggregator@upi", "amount": 5000}'`}</pre>
    </div>
  );
}
