import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import React from 'react';
import { AlertTriangle, RefreshCw } from 'lucide-react';
export class ErrorBoundary extends React.Component {
    constructor(props) {
        super(props);
        this.state = { hasError: false, error: null };
    }
    static getDerivedStateFromError(error) {
        return { hasError: true, error };
    }
    componentDidCatch(error, errorInfo) {
        console.error('Error caught by boundary:', error, errorInfo);
    }
    render() {
        if (this.state.hasError) {
            return (this.props.fallback || (_jsx("div", { className: "flex items-center justify-center min-h-screen bg-slate-900", children: _jsxs("div", { className: "bg-slate-800 rounded-lg p-8 max-w-md border border-slate-700 text-center", children: [_jsx("div", { className: "flex justify-center mb-4", children: _jsx("div", { className: "bg-red-900/30 rounded-full p-4", children: _jsx(AlertTriangle, { className: "text-red-400", size: 32 }) }) }), _jsx("h1", { className: "text-white text-2xl font-bold mb-2", children: "Oops! Something went wrong" }), _jsx("p", { className: "text-gray-400 text-sm mb-4", children: this.state.error?.message || 'An unexpected error occurred' }), _jsxs("button", { onClick: () => window.location.reload(), className: "inline-flex items-center gap-2 bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg transition", children: [_jsx(RefreshCw, { size: 16 }), "Reload Page"] })] }) })));
        }
        return this.props.children;
    }
}
