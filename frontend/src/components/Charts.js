import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import { BarChart, Bar, PieChart, Pie, Cell, Line, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, Radar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, } from 'recharts';
const COLORS = {
    CRITICAL: '#ff1744',
    HIGH: '#ff5722',
    MEDIUM: '#ff9800',
    LOW: '#4caf50',
};
export const RiskDistributionChart = ({ scores }) => {
    const data = [
        { range: '0-20', count: scores.filter(s => s.risk_score < 20).length },
        { range: '20-40', count: scores.filter(s => s.risk_score >= 20 && s.risk_score < 40).length },
        { range: '40-60', count: scores.filter(s => s.risk_score >= 40 && s.risk_score < 60).length },
        { range: '60-80', count: scores.filter(s => s.risk_score >= 60 && s.risk_score < 80).length },
        { range: '80-100', count: scores.filter(s => s.risk_score >= 80).length },
    ];
    return (_jsxs("div", { className: "h-80 bg-slate-800 rounded-lg p-4", children: [_jsx("h3", { className: "text-white font-semibold mb-4", children: "Risk Score Distribution" }), _jsx(ResponsiveContainer, { width: "100%", height: "100%", children: _jsxs(BarChart, { data: data, margin: { top: 20, right: 30, left: 0, bottom: 20 }, children: [_jsx(CartesianGrid, { strokeDasharray: "3 3", stroke: "#374151" }), _jsx(XAxis, { dataKey: "range", stroke: "#9ca3af" }), _jsx(YAxis, { stroke: "#9ca3af" }), _jsx(Tooltip, { contentStyle: { backgroundColor: '#1f2937', border: '1px solid #374151' } }), _jsx(Bar, { dataKey: "count", fill: "#3b82f6", radius: [8, 8, 0, 0] })] }) })] }));
};
export const RiskBreakdownChart = ({ critical, high, medium, low, }) => {
    const data = [
        { name: 'CRITICAL', value: critical, fill: COLORS.CRITICAL },
        { name: 'HIGH', value: high, fill: COLORS.HIGH },
        { name: 'MEDIUM', value: medium, fill: COLORS.MEDIUM },
        { name: 'LOW', value: low, fill: COLORS.LOW },
    ];
    return (_jsxs("div", { className: "h-80 bg-slate-800 rounded-lg p-4", children: [_jsx("h3", { className: "text-white font-semibold mb-4", children: "Risk Level Breakdown" }), _jsx(ResponsiveContainer, { width: "100%", height: "100%", children: _jsxs(PieChart, { children: [_jsx(Pie, { data: data, cx: "50%", cy: "50%", innerRadius: 80, outerRadius: 120, paddingAngle: 2, dataKey: "value", label: ({ name, value }) => `${name}: ${value}`, children: data.map((entry, index) => (_jsx(Cell, { fill: entry.fill }, `cell-${index}`))) }), _jsx(Tooltip, { contentStyle: { backgroundColor: '#1f2937', border: '1px solid #374151' } })] }) })] }));
};
export const SignalHeatmap = ({ scores, limit = 20 }) => {
    const topScores = scores.slice(0, limit);
    return (_jsxs("div", { className: "bg-slate-800 rounded-lg p-4 overflow-x-auto", children: [_jsxs("h3", { className: "text-white font-semibold mb-4", children: ["Signal Heatmap \u2014 Top ", limit, " Risky Accounts"] }), _jsxs("table", { className: "w-full text-sm text-gray-300", children: [_jsx("thead", { children: _jsxs("tr", { className: "border-b border-slate-700", children: [_jsx("th", { className: "text-left py-2 px-4", children: "Account" }), _jsx("th", { className: "text-right py-2 px-4", children: "Behavioral" }), _jsx("th", { className: "text-right py-2 px-4", children: "Graph" }), _jsx("th", { className: "text-right py-2 px-4", children: "Device" }), _jsx("th", { className: "text-right py-2 px-4", children: "Temporal" }), _jsx("th", { className: "text-right py-2 px-4", children: "ML Anomaly" }), _jsx("th", { className: "text-right py-2 px-4", children: "Total" })] }) }), _jsx("tbody", { children: topScores.map((score) => (_jsxs("tr", { className: "border-b border-slate-700 hover:bg-slate-700", children: [_jsx("td", { className: "py-2 px-4 font-mono text-xs", children: score.account_id }), _jsx("td", { className: "text-right py-2 px-4", children: _jsx(ScoreCell, { value: score.behavioral_score }) }), _jsx("td", { className: "text-right py-2 px-4", children: _jsx(ScoreCell, { value: score.graph_score }) }), _jsx("td", { className: "text-right py-2 px-4", children: _jsx(ScoreCell, { value: score.device_score }) }), _jsx("td", { className: "text-right py-2 px-4", children: _jsx(ScoreCell, { value: score.temporal_score }) }), _jsx("td", { className: "text-right py-2 px-4", children: _jsx(ScoreCell, { value: score.ml_anomaly_score }) }), _jsx("td", { className: "text-right py-2 px-4 font-bold text-blue-400", children: Math.round(score.risk_score) })] }, score.account_id))) })] })] }));
};
const ScoreCell = ({ value }) => {
    let bgColor = 'bg-slate-700';
    if (value >= 70)
        bgColor = 'bg-critical';
    else if (value >= 50)
        bgColor = 'bg-high';
    else if (value >= 30)
        bgColor = 'bg-medium';
    else if (value > 0)
        bgColor = 'bg-yellow-700';
    return (_jsx("div", { className: `inline-block px-2 py-1 rounded text-white font-medium ${bgColor}`, children: Math.round(value) }));
};
export const SignalRadar = ({ accountId, behavioral, graph, device, temporal, ml, }) => {
    const data = [
        { signal: 'Behavioral', value: behavioral },
        { signal: 'Graph', value: graph },
        { signal: 'Device', value: device },
        { signal: 'Temporal', value: temporal },
        { signal: 'ML Anomaly', value: ml },
    ];
    return (_jsxs("div", { className: "h-80 bg-slate-800 rounded-lg p-4", children: [_jsxs("h3", { className: "text-white font-semibold mb-4", children: ["Signal Breakdown \u2014 ", accountId] }), _jsx(ResponsiveContainer, { width: "100%", height: "100%", children: _jsxs(RadarChart, { data: data, margin: { top: 20, right: 80, bottom: 20, left: 80 }, children: [_jsx(PolarGrid, { stroke: "#374151" }), _jsx(PolarAngleAxis, { dataKey: "signal", stroke: "#9ca3af" }), _jsx(PolarRadiusAxis, { angle: 90, domain: [0, 100], stroke: "#9ca3af" }), _jsx(Radar, { name: accountId, dataKey: "value", stroke: "#ff1744", fill: "#ff1744", fillOpacity: 0.3 }), _jsx(Tooltip, { contentStyle: { backgroundColor: '#1f2937', border: '1px solid #374151' } })] }) })] }));
};
export const MLAnomalyChart = ({ scores }) => {
    const data = scores.map((score, idx) => ({
        index: idx,
        score: score.ml_anomaly_score,
        label: score.ml_anomaly_label,
    }));
    return (_jsxs("div", { className: "h-80 bg-slate-800 rounded-lg p-4", children: [_jsx("h3", { className: "text-white font-semibold mb-4", children: "ML Anomaly Scores" }), _jsx(ResponsiveContainer, { width: "100%", height: "100%", children: _jsxs(BarChart, { data: data, margin: { top: 20, right: 30, left: 0, bottom: 20 }, children: [_jsx(CartesianGrid, { strokeDasharray: "3 3", stroke: "#374151" }), _jsx(XAxis, { dataKey: "index", stroke: "#9ca3af" }), _jsx(YAxis, { stroke: "#9ca3af" }), _jsx(Tooltip, { contentStyle: { backgroundColor: '#1f2937', border: '1px solid #374151' }, formatter: (value) => Math.round(value) }), _jsx(Bar, { dataKey: "score", fill: "#8b5cf6", radius: [8, 8, 0, 0] }), _jsx(Line, { type: "monotone", dataKey: (d) => d.label === 'ANOMALOUS' ? 70 : d.label === 'SUSPICIOUS' ? 45 : 0, stroke: "#ff1744", strokeDasharray: "5 5" })] }) })] }));
};
