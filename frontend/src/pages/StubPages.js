import { jsx as _jsx, jsxs as _jsxs, Fragment as _Fragment } from "react/jsx-runtime";
import { useState, useEffect, useRef } from 'react';
import { Network } from 'vis-network/standalone';
import 'vis-network/styles/vis-network.css';
import { Button, LoadingSpinner, RiskBadge } from '../components/UI';
import { useToast } from '../hooks/useToast';
import { API_ENDPOINTS } from '@config/env';
import { AlertTriangle, ZoomIn, ZoomOut, Maximize2, Copy, Send, CheckCircle, XCircle, } from 'lucide-react';
// Production-ready Real-time API page with interactive testing
export const RealTimeAPIPage = () => {
    const [testAccountId, setTestAccountId] = useState('mule_aggregator@upi');
    const [testResponse, setTestResponse] = useState(null);
    const [testLoading, setTestLoading] = useState(false);
    const [testError, setTestError] = useState(null);
    const [responseTime, setResponseTime] = useState(null);
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
        }
        catch (err) {
            const errorMsg = err instanceof Error ? err.message : 'Unknown error occurred';
            setTestError(errorMsg);
            addToast(`Error: ${errorMsg}`, 'error');
        }
        finally {
            setTestLoading(false);
        }
    };
    const copyToClipboard = (text) => {
        navigator.clipboard.writeText(text);
    };
    return (_jsxs("div", { className: "space-y-4", children: [_jsxs("div", { className: "bg-slate-800 rounded-lg p-6 border border-slate-700", children: [_jsx("h2", { className: "text-white text-2xl font-bold mb-4", children: "\u26A1 Test Score API" }), _jsx("div", { className: "space-y-4 mb-6", children: _jsxs("div", { children: [_jsx("label", { className: "block text-sm text-gray-300 mb-2", children: "Account ID" }), _jsxs("div", { className: "flex gap-2 mb-3", children: [_jsx("input", { type: "text", value: testAccountId, onChange: (e) => setTestAccountId(e.target.value), placeholder: "e.g., mule_aggregator@upi", className: "flex-1 bg-slate-900 border border-slate-700 text-white px-4 py-2 rounded font-mono text-sm" }), _jsxs(Button, { onClick: handleTestScore, disabled: testLoading || !testAccountId.trim(), variant: "primary", children: [_jsx(Send, { size: 16 }), " Test"] })] }), _jsx("div", { className: "flex flex-wrap gap-2", children: ['mule_aggregator@upi', 'circle_node_1@upi', 'device_ring_1@upi', 'benign_user@upi'].map((account) => (_jsx("button", { onClick: () => setTestAccountId(account), className: "text-xs bg-slate-700 hover:bg-slate-600 text-gray-300 px-3 py-1 rounded transition", children: account.split('@')[0] }, account))) })] }) }), testLoading && (_jsx("div", { className: "flex items-center justify-center py-8", children: _jsx(LoadingSpinner, { message: "Analyzing account..." }) })), testError && (_jsx("div", { className: "bg-red-900/30 border border-red-700 rounded p-4 mb-6", children: _jsxs("div", { className: "flex items-start gap-3", children: [_jsx(XCircle, { className: "text-red-400 flex-shrink-0 mt-0.5", size: 20 }), _jsxs("div", { children: [_jsx("p", { className: "text-red-300 font-semibold", children: "Error" }), _jsx("p", { className: "text-red-200 text-sm", children: testError })] })] }) })), testResponse && !testError && (_jsxs("div", { className: "space-y-4", children: [_jsx("div", { className: "bg-green-900/30 border border-green-700 rounded p-3 flex items-center justify-between", children: _jsxs("div", { className: "flex items-center gap-2", children: [_jsx(CheckCircle, { className: "text-green-400", size: 20 }), _jsxs("div", { children: [_jsx("p", { className: "text-green-300 font-semibold text-sm", children: "Success" }), _jsxs("p", { className: "text-green-200 text-xs", children: [responseTime?.toFixed(0), "ms"] })] })] }) }), _jsxs("div", { className: "grid grid-cols-2 md:grid-cols-4 gap-3", children: [_jsxs("div", { className: "bg-slate-900 rounded p-3 border border-slate-700", children: [_jsx("p", { className: "text-gray-400 text-xs mb-1", children: "Risk Score" }), _jsx("p", { className: "text-2xl font-bold text-white", children: testResponse.risk_score.toFixed(1) })] }), _jsxs("div", { className: "bg-slate-900 rounded p-3 border border-slate-700", children: [_jsx("p", { className: "text-gray-400 text-xs mb-1", children: "Level" }), _jsx(RiskBadge, { level: testResponse.risk_level })] }), _jsxs("div", { className: "bg-slate-900 rounded p-3 border border-slate-700", children: [_jsx("p", { className: "text-gray-400 text-xs mb-1", children: "Confidence" }), _jsxs("p", { className: "text-2xl font-bold text-blue-400", children: [(testResponse.confidence * 100).toFixed(0), "%"] })] }), _jsxs("div", { className: "bg-slate-900 rounded p-3 border border-slate-700", children: [_jsx("p", { className: "text-gray-400 text-xs mb-1", children: "Action" }), _jsx("p", { className: "text-sm font-semibold text-yellow-400", children: testResponse.recommended_action })] })] }), _jsx("div", { className: "grid grid-cols-2 md:grid-cols-5 gap-2 pt-2", children: [
                                    { label: 'Behavioral', value: testResponse.behavioral_score },
                                    { label: 'Temporal', value: testResponse.temporal_score },
                                    { label: 'Graph', value: testResponse.graph_score },
                                    { label: 'Device', value: testResponse.device_score },
                                    { label: 'ML Anomaly', value: testResponse.ml_anomaly_score },
                                ].map((item) => (_jsxs("div", { className: "bg-slate-900 rounded p-2 border border-slate-700", children: [_jsx("p", { className: "text-gray-400 text-xs", children: item.label }), _jsx("p", { className: "text-lg font-bold text-white", children: item.value.toFixed(0) })] }, item.label))) }), _jsxs("details", { className: "bg-slate-900 rounded p-3 border border-slate-700", children: [_jsx("summary", { className: "cursor-pointer text-gray-300 font-semibold text-sm hover:text-gray-200", children: "\uD83D\uDCCB Full Response JSON" }), _jsxs("div", { className: "mt-3 flex items-center justify-between mb-2", children: [_jsx("span", { className: "text-gray-400 text-xs", children: "Click to copy" }), _jsx("button", { onClick: () => copyToClipboard(JSON.stringify(testResponse, null, 2)), className: "text-gray-400 hover:text-gray-200 transition", children: _jsx(Copy, { size: 16 }) })] }), _jsx("pre", { className: "text-gray-300 text-xs font-mono overflow-x-auto max-h-48 bg-slate-800 p-2 rounded", children: JSON.stringify(testResponse, null, 2) })] })] }))] }), _jsx("div", { className: "bg-slate-800 rounded-lg p-4 border border-slate-700", children: _jsxs("details", { children: [_jsx("summary", { className: "cursor-pointer text-white font-semibold text-sm hover:text-blue-400", children: "\uD83D\uDCDA API Reference" }), _jsxs("div", { className: "mt-4 space-y-2 text-xs text-gray-300", children: [_jsxs("div", { children: [_jsxs("p", { className: "text-blue-400 font-mono mb-1", children: ["GET /score/", '{account_id}'] }), _jsx("p", { className: "text-gray-400", children: "Score a single account in real-time" })] }), _jsxs("div", { children: [_jsx("p", { className: "text-green-400 font-mono mb-1", children: "POST /batch_score" }), _jsx("p", { className: "text-gray-400", children: "Score multiple accounts efficiently" })] }), _jsxs("div", { children: [_jsx("p", { className: "text-purple-400 font-mono mb-1", children: "GET /stats" }), _jsx("p", { className: "text-gray-400", children: "Get system health (10 req/min limit)" })] })] })] }) }), _jsxs("details", { className: "bg-slate-800 rounded-lg p-4 border border-slate-700", children: [_jsx("summary", { className: "cursor-pointer text-white font-semibold text-sm hover:text-blue-400", children: "\uD83D\uDCBB Quick Code Examples" }), _jsxs("div", { className: "mt-4 space-y-3 text-xs", children: [_jsxs("div", { children: [_jsx("p", { className: "text-blue-400 font-semibold mb-1", children: "Python" }), _jsx("pre", { className: "bg-slate-900 p-2 rounded text-gray-300 font-mono overflow-x-auto", children: `import requests
r = requests.get("http://localhost:8000/score/mule_aggregator@upi")
print(r.json())` })] }), _jsxs("div", { children: [_jsx("p", { className: "text-green-400 font-semibold mb-1", children: "JavaScript" }), _jsx("pre", { className: "bg-slate-900 p-2 rounded text-gray-300 font-mono overflow-x-auto", children: `const r = await fetch("http://localhost:8000/score/mule_aggregator@upi");
console.log(await r.json());` })] })] })] })] }));
};
// Network graph visualization page with enhanced details panel
export const NetworkGraphPage = () => {
    const [selectedNode, setSelectedNode] = useState(null);
    const [graphData, setGraphData] = useState(null);
    const [loading, setLoading] = useState(true);
    const [accountDetails, setAccountDetails] = useState(null);
    const [detailsLoading, setDetailsLoading] = useState(false);
    const [detailsError, setDetailsError] = useState(null);
    const { addToast } = useToast();
    const networkContainer = useRef(null);
    const networkRef = useRef(null);
    const selectedNodeData = selectedNode && graphData
        ? graphData.nodes.find((node) => (node.id || node.name) === selectedNode)
        : null;
    const handleZoomIn = () => {
        if (networkRef.current)
            networkRef.current.zoomIn();
    };
    const handleZoomOut = () => {
        if (networkRef.current)
            networkRef.current.zoomOut();
    };
    const handleFitView = () => {
        if (networkRef.current)
            networkRef.current.fit({ animation: { duration: 500 } });
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
                if (!response.ok)
                    throw new Error('Failed to fetch details');
                const details = await response.json();
                setAccountDetails(details);
            }
            catch (err) {
                const errorMsg = err instanceof Error ? err.message : 'Unknown error';
                setDetailsError(errorMsg);
                addToast(`Failed to load account details: ${errorMsg}`, 'error');
                console.error('Failed to fetch account details:', err);
            }
            finally {
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
                const nodes = data.nodes.map((node) => {
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
                const edges = data.edges.map((edge) => ({
                    from: edge.source,
                    to: edge.target,
                    width: 2,
                    arrows: 'to',
                    color: '#94a3b8',
                }));
                const container = networkContainer.current;
                if (!container)
                    return;
                const visData = { nodes, edges };
                const options = {
                    physics: { enabled: true, stabilization: { iterations: 200 } },
                    nodes: { font: { color: '#fff', size: 14 }, borderWidth: 2 },
                };
                networkRef.current = new Network(container, visData, options);
                networkRef.current.on('selectNode', (params) => {
                    if (params.nodes.length > 0)
                        setSelectedNode(params.nodes[0]);
                });
                networkRef.current.on('deselectNode', () => setSelectedNode(null));
                addToast(`Network loaded: ${data.nodes.length} accounts, ${data.edges.length} transactions`, 'success');
            }
            catch (err) {
                console.error('Failed to load network:', err);
                addToast('Failed to load network graph', 'error');
            }
            finally {
                setLoading(false);
            }
        };
        initializeNetwork();
    }, [addToast]);
    const ScoreBar = ({ label, value, max = 100 }) => (_jsxs("div", { className: "space-y-1", children: [_jsxs("div", { className: "flex justify-between items-center", children: [_jsx("span", { className: "text-xs text-gray-400", children: label }), _jsx("span", { className: "text-xs font-semibold text-white", children: Math.round(value) })] }), _jsx("div", { className: "h-1.5 bg-slate-900 rounded-full overflow-hidden", children: _jsx("div", { className: "h-full bg-gradient-to-r from-orange-500 to-red-500 rounded-full", style: { width: `${Math.min(100, (value / max) * 100)}%` } }) })] }));
    return (_jsx(_Fragment, { children: _jsxs("div", { className: "space-y-6", children: [_jsxs("div", { className: "bg-slate-800 rounded-lg p-6", children: [_jsx("h2", { className: "text-white text-2xl font-bold mb-2", children: "\uD83D\uDD78\uFE0F Transaction Network" }), _jsx("p", { className: "text-gray-400", children: "Interactive visualization of transaction flows. Click on nodes to view account details." })] }), _jsxs("div", { className: "grid grid-cols-1 lg:grid-cols-4 gap-6", children: [_jsx("div", { className: "lg:col-span-3", children: _jsxs("div", { className: "bg-slate-800 rounded-lg overflow-hidden border border-slate-700", children: [loading && (_jsx("div", { className: "flex items-center justify-center h-96", children: _jsx(LoadingSpinner, { message: "Loading network..." }) })), !loading && (_jsxs(_Fragment, { children: [_jsx("div", { ref: networkContainer, style: { width: '100%', height: '500px', backgroundColor: '#1e293b' } }), _jsxs("div", { className: "bg-slate-900 p-4 flex gap-2 border-t border-slate-700", children: [_jsxs(Button, { variant: "secondary", size: "sm", onClick: handleZoomIn, children: [_jsx(ZoomIn, { size: 16 }), " Zoom In"] }), _jsxs(Button, { variant: "secondary", size: "sm", onClick: handleZoomOut, children: [_jsx(ZoomOut, { size: 16 }), " Zoom Out"] }), _jsxs(Button, { variant: "secondary", size: "sm", onClick: handleFitView, children: [_jsx(Maximize2, { size: 16 }), " Fit View"] })] })] }))] }) }), _jsx("div", { className: "lg:col-span-1", children: selectedNode ? (_jsx("div", { className: "bg-slate-800 rounded-lg border border-slate-700 sticky top-6 overflow-y-auto max-h-[600px]", children: detailsLoading ? (_jsx("div", { className: "p-4 flex items-center justify-center", children: _jsx(LoadingSpinner, { message: "Loading..." }) })) : detailsError ? (_jsx("div", { className: "p-4", children: _jsx("p", { className: "text-red-400 text-xs", children: detailsError }) })) : accountDetails ? (_jsxs("div", { className: "space-y-4 p-4", children: [_jsxs("div", { children: [_jsx("h3", { className: "text-white font-semibold mb-2", children: "\uD83D\uDCCA Account Details" }), _jsx("p", { className: "text-gray-400 text-xs break-all", children: accountDetails.account_id })] }), _jsxs("div", { className: "bg-slate-900 rounded p-3 space-y-2", children: [_jsxs("div", { className: "flex items-baseline justify-between", children: [_jsx("span", { className: "text-gray-400 text-xs", children: "Risk Score" }), _jsx("span", { className: "text-2xl font-bold text-white", children: Math.round(accountDetails.risk_score) })] }), _jsxs("div", { className: "flex items-center gap-2", children: [_jsx(RiskBadge, { level: accountDetails.risk_level }), _jsxs("span", { className: "text-xs text-gray-400", children: [accountDetails.confidence, "% confidence"] })] })] }), _jsxs("div", { className: "bg-slate-900 rounded p-3 space-y-2", children: [_jsx("p", { className: "text-gray-300 text-xs font-semibold", children: "Score Breakdown" }), _jsx(ScoreBar, { label: "Behavioral", value: accountDetails.behavioral_score }), _jsx(ScoreBar, { label: "Graph Analysis", value: accountDetails.graph_score }), _jsx(ScoreBar, { label: "Device Risk", value: accountDetails.device_score }), _jsx(ScoreBar, { label: "Temporal", value: accountDetails.temporal_score }), _jsx(ScoreBar, { label: "ML Anomaly", value: accountDetails.ml_anomaly_score, max: 100 })] }), _jsxs("div", { className: "bg-slate-900 rounded p-3", children: [_jsxs("div", { className: "flex items-baseline justify-between", children: [_jsx("span", { className: "text-gray-400 text-xs", children: "Risk Signals" }), _jsxs("span", { className: "text-lg font-bold text-orange-400", children: [accountDetails.signal_count, "/5"] })] }), _jsx("p", { className: "text-gray-500 text-xs mt-1", children: "Multiple indicators triggered" })] }), _jsxs("div", { className: "bg-slate-900 rounded p-3", children: [_jsx("p", { className: "text-gray-400 text-xs mb-1", children: "Recommended Action" }), _jsx("p", { className: "text-white font-semibold text-sm", children: accountDetails.recommended_action })] }), accountDetails.ml_anomaly_label && accountDetails.ml_anomaly_label !== 'N/A' && (_jsxs("div", { className: "bg-slate-700 rounded p-3", children: [_jsx("p", { className: "text-gray-300 text-xs font-semibold mb-1", children: "Anomaly Classification" }), _jsx("p", { className: "text-white text-sm", children: accountDetails.ml_anomaly_label })] })), accountDetails.reasons && accountDetails.reasons.length > 0 && (_jsxs("div", { className: "bg-slate-900 rounded p-3", children: [_jsx("p", { className: "text-gray-300 text-xs font-semibold mb-2", children: "Risk Indicators" }), _jsx("ul", { className: "space-y-1", children: accountDetails.reasons.slice(0, 3).map((reason, idx) => (_jsxs("li", { className: "text-gray-300 text-xs flex gap-2", children: [_jsx("span", { className: "text-orange-400", children: "\u2022" }), _jsx("span", { children: reason })] }, idx))) }), accountDetails.reasons.length > 3 && (_jsxs("p", { className: "text-gray-500 text-xs mt-1", children: ["+", accountDetails.reasons.length - 3, " more signals"] }))] }))] })) : null })) : (_jsxs("div", { className: "bg-slate-800 rounded-lg p-4 border border-slate-700 text-center", children: [_jsx(AlertTriangle, { className: "text-gray-500 mx-auto mb-2", size: 24 }), _jsx("p", { className: "text-gray-400 text-sm", children: "Click on a node to view details" })] })) })] })] }) }));
};
// Timeline page (placeholder)
export const TimelinePageComponent = () => (_jsx("div", { className: "bg-slate-800 rounded-lg p-6 text-gray-400", children: _jsx("p", { children: "\u23F1\uFE0F Temporal analysis timeline coming soon" }) }));
