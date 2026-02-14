import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import { Shield, AlertTriangle, Activity, Network, HelpCircle, Moon, Sun } from 'lucide-react';
import { useTheme } from '../hooks/useTheme';
import { Breadcrumb } from './Breadcrumb';
const TABS = [
    { id: 'command-center', label: 'Command Center', icon: _jsx(Shield, { size: 18 }) },
    { id: 'risk-analysis', label: 'Risk Analysis', icon: _jsx(AlertTriangle, { size: 18 }) },
    { id: 'network', label: 'Network Graph', icon: _jsx(Network, { size: 18 }) },
    { id: 'real-time', label: 'Real-Time API', icon: _jsx(Activity, { size: 18 }) },
    { id: 'about', label: 'About', icon: _jsx(HelpCircle, { size: 18 }) },
];
export const DashboardLayout = ({ activeTab, onTabChange, children, }) => {
    const { theme, toggleTheme } = useTheme();
    const activeTabLabel = TABS.find(t => t.id === activeTab)?.label || '';
    return (_jsxs("div", { className: "min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900", children: [_jsx("header", { className: "bg-gradient-dark border-b border-slate-700 sticky top-0 z-40", children: _jsx("div", { className: "max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4", children: _jsxs("div", { className: "flex items-center justify-between flex-wrap gap-4", children: [_jsxs("div", { className: "flex items-center gap-3", children: [_jsx(Shield, { className: "text-blue-400", size: 32 }), _jsxs("div", { children: [_jsx("h1", { className: "text-2xl font-bold text-white", children: "UPI Mule Detection" }), _jsx("p", { className: "text-sm text-gray-400", children: "Real-time fraud detection platform" })] })] }), _jsxs("div", { className: "flex items-center gap-4", children: [_jsx("button", { onClick: toggleTheme, className: "p-2 rounded-lg bg-slate-700 hover:bg-slate-600 transition text-yellow-400", title: `Switch to ${theme === 'dark' ? 'light' : 'dark'} mode`, children: theme === 'dark' ? _jsx(Sun, { size: 20 }) : _jsx(Moon, { size: 20 }) }), _jsxs("div", { className: "text-right hidden sm:block", children: [_jsxs("p", { className: "text-sm text-gray-400", children: ["Status: ", _jsx("span", { className: "text-green-400 font-semibold", children: "\u25CF Online" })] }), _jsx("p", { className: "text-xs text-gray-500", children: new Date().toLocaleString() })] })] })] }) }) }), _jsx("div", { className: "bg-slate-800 border-b border-slate-700 overflow-x-auto", children: _jsx("div", { className: "max-w-7xl mx-auto px-4 sm:px-6 lg:px-8", children: _jsx("div", { className: "flex gap-2 overflow-x-auto scroll-smooth", children: TABS.map((tab) => (_jsxs("button", { onClick: () => onTabChange(tab.id), className: `flex items-center gap-2 px-4 py-3 text-sm font-medium border-b-2 transition whitespace-nowrap ${activeTab === tab.id
                                ? 'border-blue-500 text-blue-400'
                                : 'border-transparent text-gray-400 hover:text-gray-300'}`, children: [tab.icon, _jsx("span", { className: "hidden sm:inline", children: tab.label })] }, tab.id))) }) }) }), _jsxs("main", { className: "max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8", children: [_jsx(Breadcrumb, { items: [
                            { label: 'Dashboard' },
                            { label: activeTabLabel, active: true }
                        ] }), children] }), _jsx("footer", { className: "border-t border-slate-700 bg-slate-900 mt-12", children: _jsx("div", { className: "max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4", children: _jsx("p", { className: "text-center text-sm text-gray-500", children: "UPI Mule Detection v2.0 \u00B7 CSIC 1.0 Stage III" }) }) })] }));
};
