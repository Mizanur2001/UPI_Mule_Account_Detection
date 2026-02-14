import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import React, { useState, useMemo } from 'react';
import { RiskBadge, Button, LoadingSpinner, ErrorAlert } from '../components/UI';
import { SignalRadar } from '../components/Charts';
import { Download } from 'lucide-react';
export const RiskAnalysis = ({ scores, loading, error, }) => {
    const [selectedRiskLevels, setSelectedRiskLevels] = useState([
        'CRITICAL',
        'HIGH',
        'MEDIUM',
        'LOW',
    ]);
    const [minScore, setMinScore] = useState(0);
    const [sortField, setSortField] = useState('risk_score');
    const [selectedAccount, setSelectedAccount] = useState(null);
    const filtered = useMemo(() => {
        return scores
            .filter((s) => selectedRiskLevels.includes(s.risk_level) && s.risk_score >= minScore)
            .sort((a, b) => b[sortField] - a[sortField]);
    }, [scores, selectedRiskLevels, minScore, sortField]);
    const handleExport = () => {
        const csv = [
            ['Account', 'Risk Score', 'Risk Level', 'Behavioral', 'Graph', 'Device', 'Temporal', 'ML Anomaly', 'Signals', 'Top Reason'],
            ...filtered.map((s) => [
                s.account_id,
                s.risk_score,
                s.risk_level,
                s.behavioral_score,
                s.graph_score,
                s.device_score,
                s.temporal_score,
                s.ml_anomaly_score,
                s.signal_count,
                s.reasons[0] || 'No flags',
            ]),
        ]
            .map((row) => row.map((cell) => `"${cell}"`).join(','))
            .join('\n');
        const blob = new Blob([csv], { type: 'text/csv' });
        const url = window.URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.download = `mule_risk_${new Date().toISOString().slice(0, 10)}.csv`;
        link.click();
    };
    if (loading)
        return _jsx(LoadingSpinner, { message: "Loading risk analysis..." });
    if (error)
        return _jsx(ErrorAlert, { title: "Error Loading Data", message: error.message });
    return (_jsxs("div", { className: "space-y-6", children: [_jsxs("div", { className: "bg-slate-800 rounded-lg p-4", children: [_jsx("h2", { className: "text-white font-semibold mb-4", children: "Filters" }), _jsxs("div", { className: "grid grid-cols-1 md:grid-cols-4 gap-4", children: [_jsxs("div", { children: [_jsx("label", { className: "block text-sm text-gray-400 mb-2", children: "Risk Level" }), _jsx("div", { className: "space-y-2", children: ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW'].map((level) => (_jsxs("label", { className: "flex items-center gap-2 text-gray-300 cursor-pointer", children: [_jsx("input", { type: "checkbox", checked: selectedRiskLevels.includes(level), onChange: (e) => {
                                                        if (e.target.checked) {
                                                            setSelectedRiskLevels([...selectedRiskLevels, level]);
                                                        }
                                                        else {
                                                            setSelectedRiskLevels(selectedRiskLevels.filter((l) => l !== level));
                                                        }
                                                    }, className: "w-4 h-4" }), level] }, level))) })] }), _jsxs("div", { children: [_jsx("label", { className: "block text-sm text-gray-400 mb-2", children: "Minimum Score" }), _jsx("input", { type: "range", min: "0", max: "100", value: minScore, onChange: (e) => setMinScore(Number(e.target.value)), className: "w-full" }), _jsxs("p", { className: "text-xs text-gray-500 mt-1", children: [minScore, "/100"] })] }), _jsxs("div", { children: [_jsx("label", { className: "block text-sm text-gray-400 mb-2", children: "Sort By" }), _jsxs("select", { value: sortField, onChange: (e) => setSortField(e.target.value), className: "w-full bg-slate-700 text-white rounded px-3 py-2 text-sm", children: [_jsx("option", { value: "risk_score", children: "Risk Score" }), _jsx("option", { value: "behavioral_score", children: "Behavioral" }), _jsx("option", { value: "graph_score", children: "Graph" }), _jsx("option", { value: "device_score", children: "Device" }), _jsx("option", { value: "temporal_score", children: "Temporal" }), _jsx("option", { value: "ml_anomaly_score", children: "ML Anomaly" })] })] }), _jsx("div", { className: "flex items-end", children: _jsxs(Button, { variant: "success", size: "md", onClick: handleExport, className: "w-full flex items-center justify-center gap-2", children: [_jsx(Download, { size: 16 }), "Export CSV"] }) })] })] }), _jsxs("p", { className: "text-gray-400 text-sm", children: ["Showing ", filtered.length, " of ", scores.length, " accounts"] }), _jsx("div", { className: "bg-slate-800 rounded-lg overflow-hidden", children: _jsx("div", { className: "overflow-x-auto", children: _jsxs("table", { className: "w-full text-sm text-gray-300", children: [_jsx("thead", { children: _jsxs("tr", { className: "border-b border-slate-700 bg-slate-900", children: [_jsx("th", { className: "text-left py-3 px-4", children: "Account" }), _jsx("th", { className: "text-right py-3 px-4", children: "Score" }), _jsx("th", { className: "text-center py-3 px-4", children: "Level" }), _jsx("th", { className: "text-right py-3 px-4", children: "Behavioral" }), _jsx("th", { className: "text-right py-3 px-4", children: "Graph" }), _jsx("th", { className: "text-right py-3 px-4", children: "Device" }), _jsx("th", { className: "text-right py-3 px-4", children: "Temporal" }), _jsx("th", { className: "text-right py-3 px-4", children: "ML" }), _jsx("th", { className: "text-right py-3 px-4", children: "Signals" }), _jsx("th", { className: "text-left py-3 px-4", children: "Action" })] }) }), _jsx("tbody", { children: filtered.map((score) => (_jsxs(React.Fragment, { children: [_jsxs("tr", { onClick: () => setSelectedAccount(selectedAccount === score.account_id ? null : score.account_id), className: "border-b border-slate-700 hover:bg-slate-700 cursor-pointer transition", children: [_jsx("td", { className: "py-3 px-4 font-mono text-xs", children: score.account_id }), _jsx("td", { className: "text-right py-3 px-4 font-bold text-blue-400", children: Math.round(score.risk_score) }), _jsx("td", { className: "text-center py-3 px-4", children: _jsx(RiskBadge, { level: score.risk_level }) }), _jsx("td", { className: "text-right py-3 px-4", children: Math.round(score.behavioral_score) }), _jsx("td", { className: "text-right py-3 px-4", children: Math.round(score.graph_score) }), _jsx("td", { className: "text-right py-3 px-4", children: Math.round(score.device_score) }), _jsx("td", { className: "text-right py-3 px-4", children: Math.round(score.temporal_score) }), _jsx("td", { className: "text-right py-3 px-4", children: Math.round(score.ml_anomaly_score) }), _jsx("td", { className: "text-right py-3 px-4 font-semibold", children: score.signal_count }), _jsx("td", { className: "text-left py-3 px-4", children: _jsx("span", { className: "text-xs px-2 py-1 rounded bg-slate-700 text-gray-300", children: score.recommended_action }) })] }), selectedAccount === score.account_id && (_jsx("tr", { className: "bg-slate-900 border-b border-slate-700", children: _jsx("td", { colSpan: 10, className: "py-4 px-4", children: _jsx(DrillDownPanel, { score: score }) }) }))] }, score.account_id))) })] }) }) })] }));
};
const DrillDownPanel = ({ score }) => {
    return (_jsxs("div", { className: "space-y-4", children: [_jsxs("div", { className: "grid grid-cols-1 md:grid-cols-3 gap-4", children: [_jsxs("div", { className: "space-y-2", children: [_jsx("h3", { className: "text-white font-semibold text-sm", children: "Overview" }), _jsxs("div", { className: "bg-slate-800 rounded p-3 space-y-1 text-xs", children: [_jsxs("p", { className: "text-gray-400", children: [_jsx("span", { className: "text-gray-300 font-semibold", children: "Risk Level:" }), " ", score.risk_level] }), _jsxs("p", { className: "text-gray-400", children: [_jsx("span", { className: "text-gray-300 font-semibold", children: "Confidence:" }), " ", score.confidence] }), _jsxs("p", { className: "text-gray-400", children: [_jsx("span", { className: "text-gray-300 font-semibold", children: "Action:" }), " ", score.recommended_action] }), _jsxs("p", { className: "text-gray-400", children: [_jsx("span", { className: "text-gray-300 font-semibold", children: "Signals:" }), " ", score.signal_count, " active"] })] })] }), _jsx("div", { className: "md:col-span-2", children: _jsx("div", { style: { height: '350px' }, children: _jsx(SignalRadar, { accountId: score.account_id, behavioral: score.behavioral_score, graph: score.graph_score, device: score.device_score, temporal: score.temporal_score, ml: score.ml_anomaly_score }) }) })] }), _jsxs("div", { children: [_jsx("h3", { className: "text-white font-semibold text-sm mb-2", children: "Evidence Trail" }), _jsxs("div", { className: "space-y-2", children: [score.reasons.map((reason, idx) => (_jsx("div", { className: "bg-slate-800 border-l-4 border-orange-400 p-3 rounded-r", children: _jsxs("p", { className: "text-gray-300 text-xs", children: ["\uD83D\uDD38 ", reason] }) }, idx))), score.reasons.length === 0 && (_jsx("div", { className: "bg-slate-800 border-l-4 border-green-400 p-3 rounded-r", children: _jsx("p", { className: "text-gray-300 text-xs", children: "\u2713 No risk factors identified" }) }))] })] })] }));
};
