import React, { useState, useEffect, useRef } from 'react';
import { Network } from 'vis-network/standalone';
import 'vis-network/styles/vis-network.css';
import { apiService } from '../services/api';
import { RiskScore } from '../types/api';
import { Button, LoadingSpinner, RiskBadge } from '../components/UI';
import { useToast } from '../hooks/useToast';
import { API_ENDPOINTS } from '@config/env';
import {
  AlertTriangle,
  ZoomIn,
  ZoomOut,
  Maximize2,
  Copy,
  Send,
  Code,
  CheckCircle,
  XCircle,
} from 'lucide-react';

// Production-ready Real-time API page with interactive testing
export const RealTimeAPIPage: React.FC = () => {
  const [testAccountId, setTestAccountId] = useState('mule_aggregator@upi');
  const [testResponse, setTestResponse] = useState<any>(null);
  const [testLoading, setTestLoading] = useState(false);
  const [testError, setTestError] = useState<string | null>(null);
  const [responseTime, setResponseTime] = useState<number | null>(null);
  const { addToast } = useToast();

  const handleTestScore = async () => {
    setTestLoading(true);
    setTestError(null);
    setTestResponse(null);

    const startTime = performance.now();
    try {
      const scoreUrl = API_ENDPOINTS.SCORE(testAccountId);
      const response = await fetch(scoreUrl);
      const endTime = performance.now();
      setResponseTime(endTime - startTime);

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const data = await response.json();
      setTestResponse(data);
      addToast('Account analysis complete!', 'success');
    } catch (err) {
      const errorMsg = err instanceof Error ? err.message : 'Unknown error occurred';
      setTestError(errorMsg);
      addToast(`Error: ${errorMsg}`, 'error');
    } finally {
      setTestLoading(false);
    }
  };

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text);
  };

  return (
    <div className="space-y-4">
      {/* Quick Tester */}
      <div className="bg-slate-800 rounded-lg p-6 border border-slate-700">
        <h2 className="text-white text-2xl font-bold mb-4">⚡ Test Score API</h2>

        {/* Input Section */}
        <div className="space-y-4 mb-6">
          <div>
            <label className="block text-sm text-gray-300 mb-2">Account ID</label>
            <div className="flex gap-2 mb-3">
              <input
                type="text"
                value={testAccountId}
                onChange={(e) => setTestAccountId(e.target.value)}
                placeholder="e.g., mule_aggregator@upi"
                className="flex-1 bg-slate-900 border border-slate-700 text-white px-4 py-2 rounded font-mono text-sm"
              />
              <Button
                onClick={handleTestScore}
                disabled={testLoading || !testAccountId.trim()}
                variant="primary"
              >
                <Send size={16} /> Test
              </Button>
            </div>

            {/* Quick Presets */}
            <div className="flex flex-wrap gap-2">
              {['mule_aggregator@upi', 'circle_node_1@upi', 'device_ring_1@upi', 'benign_user@upi'].map(
                (account) => (
                  <button
                    key={account}
                    onClick={() => setTestAccountId(account)}
                    className="text-xs bg-slate-700 hover:bg-slate-600 text-gray-300 px-3 py-1 rounded transition"
                  >
                    {account.split('@')[0]}
                  </button>
                )
              )}
            </div>
          </div>
        </div>

        {/* Loading State */}
        {testLoading && (
          <div className="flex items-center justify-center py-8">
            <LoadingSpinner message="Analyzing account..." />
          </div>
        )}

        {/* Error State */}
        {testError && (
          <div className="bg-red-900/30 border border-red-700 rounded p-4 mb-6">
            <div className="flex items-start gap-3">
              <XCircle className="text-red-400 flex-shrink-0 mt-0.5" size={20} />
              <div>
                <p className="text-red-300 font-semibold">Error</p>
                <p className="text-red-200 text-sm">{testError}</p>
              </div>
            </div>
          </div>
        )}

        {/* Success State */}
        {testResponse && !testError && (
          <div className="space-y-4">
            {/* Status Header */}
            <div className="bg-green-900/30 border border-green-700 rounded p-3 flex items-center justify-between">
              <div className="flex items-center gap-2">
                <CheckCircle className="text-green-400" size={20} />
                <div>
                  <p className="text-green-300 font-semibold text-sm">Success</p>
                  <p className="text-green-200 text-xs">{responseTime?.toFixed(0)}ms</p>
                </div>
              </div>
            </div>

            {/* Score Summary Grid */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
              <div className="bg-slate-900 rounded p-3 border border-slate-700">
                <p className="text-gray-400 text-xs mb-1">Risk Score</p>
                <p className="text-2xl font-bold text-white">{testResponse.risk_score.toFixed(1)}</p>
              </div>
              <div className="bg-slate-900 rounded p-3 border border-slate-700">
                <p className="text-gray-400 text-xs mb-1">Level</p>
                <RiskBadge level={testResponse.risk_level} />
              </div>
              <div className="bg-slate-900 rounded p-3 border border-slate-700">
                <p className="text-gray-400 text-xs mb-1">Confidence</p>
                <p className="text-2xl font-bold text-blue-400">
                  {(testResponse.confidence * 100).toFixed(0)}%
                </p>
              </div>
              <div className="bg-slate-900 rounded p-3 border border-slate-700">
                <p className="text-gray-400 text-xs mb-1">Action</p>
                <p className="text-sm font-semibold text-yellow-400">{testResponse.recommended_action}</p>
              </div>
            </div>

            {/* Score Breakdown */}
            <div className="grid grid-cols-2 md:grid-cols-5 gap-2 pt-2">
              {[
                { label: 'Behavioral', value: testResponse.behavioral_score },
                { label: 'Temporal', value: testResponse.temporal_score },
                { label: 'Graph', value: testResponse.graph_score },
                { label: 'Device', value: testResponse.device_score },
                { label: 'ML Anomaly', value: testResponse.ml_anomaly_score },
              ].map((item) => (
                <div key={item.label} className="bg-slate-900 rounded p-2 border border-slate-700">
                  <p className="text-gray-400 text-xs">{item.label}</p>
                  <p className="text-lg font-bold text-white">{item.value.toFixed(0)}</p>
                </div>
              ))}
            </div>

            {/* Full JSON Response (Collapsible) */}
            <details className="bg-slate-900 rounded p-3 border border-slate-700">
              <summary className="cursor-pointer text-gray-300 font-semibold text-sm hover:text-gray-200">
                📋 Full Response JSON
              </summary>
              <div className="mt-3 flex items-center justify-between mb-2">
                <span className="text-gray-400 text-xs">Click to copy</span>
                <button
                  onClick={() => copyToClipboard(JSON.stringify(testResponse, null, 2))}
                  className="text-gray-400 hover:text-gray-200 transition"
                >
                  <Copy size={16} />
                </button>
              </div>
              <pre className="text-gray-300 text-xs font-mono overflow-x-auto max-h-48 bg-slate-800 p-2 rounded">
                {JSON.stringify(testResponse, null, 2)}
              </pre>
            </details>
          </div>
        )}
      </div>

      {/* Quick Reference Card */}
      <div className="bg-slate-800 rounded-lg p-4 border border-slate-700">
        <details>
          <summary className="cursor-pointer text-white font-semibold text-sm hover:text-blue-400">
            📚 API Reference
          </summary>
          <div className="mt-4 space-y-2 text-xs text-gray-300">
            <div>
              <p className="text-blue-400 font-mono mb-1">GET /score/{'{account_id}'}</p>
              <p className="text-gray-400">Score a single account in real-time</p>
            </div>
            <div>
              <p className="text-green-400 font-mono mb-1">POST /batch_score</p>
              <p className="text-gray-400">Score multiple accounts efficiently</p>
            </div>
            <div>
              <p className="text-purple-400 font-mono mb-1">GET /stats</p>
              <p className="text-gray-400">Get system health (10 req/min limit)</p>
            </div>
          </div>
        </details>
      </div>

      {/* Code Snippet */}
      <details className="bg-slate-800 rounded-lg p-4 border border-slate-700">
        <summary className="cursor-pointer text-white font-semibold text-sm hover:text-blue-400">
          💻 Quick Code Examples
        </summary>
        <div className="mt-4 space-y-3 text-xs">
          <div>
            <p className="text-blue-400 font-semibold mb-1">Python</p>
            <pre className="bg-slate-900 p-2 rounded text-gray-300 font-mono overflow-x-auto">
{`import requests
r = requests.get("http://localhost:8000/score/mule_aggregator@upi")
print(r.json())`}
            </pre>
          </div>
          <div>
            <p className="text-green-400 font-semibold mb-1">JavaScript</p>
            <pre className="bg-slate-900 p-2 rounded text-gray-300 font-mono overflow-x-auto">
{`const r = await fetch("http://localhost:8000/score/mule_aggregator@upi");
console.log(await r.json());`}
            </pre>
          </div>
        </div>
      </details>
    </div>
  );
};

// Network graph visualization page with enhanced details panel
export const NetworkGraphPage: React.FC = () => {
  const [selectedNode, setSelectedNode] = useState<string | null>(null);
  const [graphData, setGraphData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [accountDetails, setAccountDetails] = useState<any>(null);
  const [detailsLoading, setDetailsLoading] = useState(false);
  const [detailsError, setDetailsError] = useState<string | null>(null);
  const { addToast } = useToast();
  const networkContainer = useRef<HTMLDivElement>(null);
  const networkRef = useRef<any>(null);

  const selectedNodeData = selectedNode && graphData
    ? graphData.nodes.find((node: any) => (node.id || node.name) === selectedNode)
    : null;

  const handleZoomIn = () => {
    if (networkRef.current) networkRef.current.zoomIn();
  };

  const handleZoomOut = () => {
    if (networkRef.current) networkRef.current.zoomOut();
  };

  const handleFitView = () => {
    if (networkRef.current) networkRef.current.fit({ animation: { duration: 500 } });
  };

  // Fetch account details when node is selected
  useEffect(() => {
    if (!selectedNode) {
      setAccountDetails(null);
      setDetailsError(null);
      return;
    }

    const fetchDetails = async () => {
      try {
        setDetailsLoading(true);
        setDetailsError(null);
        const response = await fetch(API_ENDPOINTS.SCORE(selectedNode));
        if (!response.ok) throw new Error('Failed to fetch details');
        const details = await response.json();
        setAccountDetails(details);
      } catch (err) {
        const errorMsg = err instanceof Error ? err.message : 'Unknown error';
        setDetailsError(errorMsg);
        addToast(`Failed to load account details: ${errorMsg}`, 'error');
        console.error('Failed to fetch account details:', err);
      } finally {
        setDetailsLoading(false);
      }
    };

    fetchDetails();
  }, [selectedNode, addToast]);

  useEffect(() => {
    const initializeNetwork = async () => {
      try {
        setLoading(true);
        const response = await fetch(API_ENDPOINTS.TRANSACTION_GRAPH);
        const data = await response.json();
        setGraphData(data);

        const nodes = data.nodes.map((node: any) => {
          const riskColor = node.risk_level === 'CRITICAL'
            ? '#ef4444'
            : node.risk_level === 'HIGH'
            ? '#f97316'
            : node.risk_level === 'MEDIUM'
            ? '#eab308'
            : '#22c55e';
          return {
            id: node.id || node.name,
            label: (node.id || node.name)?.split('@')[0],
            title: `${node.id || node.name}\nRisk: ${node.risk_score || 0}/100`,
            color: riskColor,
            size: Math.max(20, Math.min(40, (node.risk_score || 20) / 2)),
          };
        });

        const edges = data.edges.map((edge: any) => ({
          from: edge.source,
          to: edge.target,
          width: 2,
          arrows: 'to',
          color: '#94a3b8',
        }));

        const container = networkContainer.current;
        if (!container) return;

        const visData = { nodes, edges };
        const options = {
          physics: { enabled: true, stabilization: { iterations: 200 } },
          nodes: { font: { color: '#fff', size: 14 }, borderWidth: 2 },
        };

        networkRef.current = new Network(container, visData, options);
        networkRef.current.on('selectNode', (params: any) => {
          if (params.nodes.length > 0) setSelectedNode(params.nodes[0]);
        });
        networkRef.current.on('deselectNode', () => setSelectedNode(null));
        addToast(`Network loaded: ${data.nodes.length} accounts, ${data.edges.length} transactions`, 'success');
      } catch (err) {
        console.error('Failed to load network:', err);
        addToast('Failed to load network graph', 'error');
      } finally {
        setLoading(false);
      }
    };
    initializeNetwork();
  }, [addToast]);

  const ScoreBar = ({ label, value, max = 100 }: { label: string; value: number; max?: number }) => (
    <div className="space-y-1">
      <div className="flex justify-between items-center">
        <span className="text-xs text-gray-400">{label}</span>
        <span className="text-xs font-semibold text-white">{Math.round(value)}</span>
      </div>
      <div className="h-1.5 bg-slate-900 rounded-full overflow-hidden">
        <div
          className="h-full bg-gradient-to-r from-orange-500 to-red-500 rounded-full"
          style={{ width: `${Math.min(100, (value / max) * 100)}%` }}
        />
      </div>
    </div>
  );

  return (
    <>
      <div className="space-y-6">
        <div className="bg-slate-800 rounded-lg p-6">
          <h2 className="text-white text-2xl font-bold mb-2">🕸️ Transaction Network</h2>
          <p className="text-gray-400">
            Interactive visualization of transaction flows. Click on nodes to view account details.
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
          <div className="lg:col-span-3">
            <div className="bg-slate-800 rounded-lg overflow-hidden border border-slate-700">
              {loading && (
                <div className="flex items-center justify-center h-96">
                  <LoadingSpinner message="Loading network..." />
                </div>
              )}
              {!loading && (
                <>
                  <div
                    ref={networkContainer}
                    style={{ width: '100%', height: '500px', backgroundColor: '#1e293b' }}
                  />
                  <div className="bg-slate-900 p-4 flex gap-2 border-t border-slate-700">
                    <Button variant="secondary" size="sm" onClick={handleZoomIn}>
                      <ZoomIn size={16} /> Zoom In
                    </Button>
                    <Button variant="secondary" size="sm" onClick={handleZoomOut}>
                      <ZoomOut size={16} /> Zoom Out
                    </Button>
                    <Button variant="secondary" size="sm" onClick={handleFitView}>
                      <Maximize2 size={16} /> Fit View
                    </Button>
                  </div>
                </>
              )}
            </div>
          </div>

          <div className="lg:col-span-1">
            {selectedNode ? (
              <div className="bg-slate-800 rounded-lg border border-slate-700 sticky top-6 overflow-y-auto max-h-[600px]">
                {detailsLoading ? (
                  <div className="p-4 flex items-center justify-center">
                    <LoadingSpinner message="Loading..." />
                  </div>
                ) : detailsError ? (
                  <div className="p-4">
                    <p className="text-red-400 text-xs">{detailsError}</p>
                  </div>
                ) : accountDetails ? (
                  <div className="space-y-4 p-4">
                    {/* Header */}
                    <div>
                      <h3 className="text-white font-semibold mb-2">📊 Account Details</h3>
                      <p className="text-gray-400 text-xs break-all">{accountDetails.account_id}</p>
                    </div>

                    {/* Risk Overview */}
                    <div className="bg-slate-900 rounded p-3 space-y-2">
                      <div className="flex items-baseline justify-between">
                        <span className="text-gray-400 text-xs">Risk Score</span>
                        <span className="text-2xl font-bold text-white">
                          {Math.round(accountDetails.risk_score)}
                        </span>
                      </div>
                      <div className="flex items-center gap-2">
                        <RiskBadge level={accountDetails.risk_level} />
                        <span className="text-xs text-gray-400">
                          {accountDetails.confidence}% confidence
                        </span>
                      </div>
                    </div>

                    {/* Score Breakdown */}
                    <div className="bg-slate-900 rounded p-3 space-y-2">
                      <p className="text-gray-300 text-xs font-semibold">Score Breakdown</p>
                      <ScoreBar label="Behavioral" value={accountDetails.behavioral_score} />
                      <ScoreBar label="Graph Analysis" value={accountDetails.graph_score} />
                      <ScoreBar label="Device Risk" value={accountDetails.device_score} />
                      <ScoreBar label="Temporal" value={accountDetails.temporal_score} />
                      <ScoreBar label="ML Anomaly" value={accountDetails.ml_anomaly_score} max={100} />
                    </div>

                    {/* Signal Count */}
                    <div className="bg-slate-900 rounded p-3">
                      <div className="flex items-baseline justify-between">
                        <span className="text-gray-400 text-xs">Risk Signals</span>
                        <span className="text-lg font-bold text-orange-400">
                          {accountDetails.signal_count}/5
                        </span>
                      </div>
                      <p className="text-gray-500 text-xs mt-1">
                        Multiple indicators triggered
                      </p>
                    </div>

                    {/* Recommended Action */}
                    <div className="bg-slate-900 rounded p-3">
                      <p className="text-gray-400 text-xs mb-1">Recommended Action</p>
                      <p className="text-white font-semibold text-sm">{accountDetails.recommended_action}</p>
                    </div>

                    {/* ML Anomaly Label */}
                    {accountDetails.ml_anomaly_label && accountDetails.ml_anomaly_label !== 'N/A' && (
                      <div className="bg-slate-700 rounded p-3">
                        <p className="text-gray-300 text-xs font-semibold mb-1">Anomaly Classification</p>
                        <p className="text-white text-sm">{accountDetails.ml_anomaly_label}</p>
                      </div>
                    )}

                    {/* Top Reasons */}
                    {accountDetails.reasons && accountDetails.reasons.length > 0 && (
                      <div className="bg-slate-900 rounded p-3">
                        <p className="text-gray-300 text-xs font-semibold mb-2">Risk Indicators</p>
                        <ul className="space-y-1">
                          {accountDetails.reasons.slice(0, 3).map((reason: string, idx: number) => (
                            <li key={idx} className="text-gray-300 text-xs flex gap-2">
                              <span className="text-orange-400">•</span>
                              <span>{reason}</span>
                            </li>
                          ))}
                        </ul>
                        {accountDetails.reasons.length > 3 && (
                          <p className="text-gray-500 text-xs mt-1">
                            +{accountDetails.reasons.length - 3} more signals
                          </p>
                        )}
                      </div>
                    )}
                  </div>
                ) : null}
              </div>
            ) : (
              <div className="bg-slate-800 rounded-lg p-4 border border-slate-700 text-center">
                <AlertTriangle className="text-gray-500 mx-auto mb-2" size={24} />
                <p className="text-gray-400 text-sm">Click on a node to view details</p>
              </div>
            )}
          </div>
        </div>
      </div>
    </>
  );
};

// Timeline page (placeholder)
export const TimelinePageComponent: React.FC = () => (
  <div className="bg-slate-800 rounded-lg p-6 text-gray-400">
    <p>⏱️ Temporal analysis timeline coming soon</p>
  </div>
);
