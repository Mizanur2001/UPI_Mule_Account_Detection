import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import clsx from 'clsx';
export const MetricCard = ({ label, value, icon, riskLevel, className }) => {
    const riskColors = {
        CRITICAL: 'border-critical bg-red-950',
        HIGH: 'border-high bg-orange-950',
        MEDIUM: 'border-medium bg-yellow-950',
        LOW: 'border-low bg-green-950',
    };
    const borderColor = riskLevel ? riskColors[riskLevel] : 'border-blue-600 bg-slate-800';
    return (_jsx("div", { className: clsx('bg-slate-900 border-l-4 rounded-lg p-4 text-white', borderColor, className), children: _jsxs("div", { className: "flex items-center justify-between", children: [_jsxs("div", { children: [_jsx("p", { className: "text-sm text-gray-300 mb-1", children: label }), _jsx("p", { className: "text-2xl font-bold", children: value })] }), icon && _jsx("div", { className: "text-3xl opacity-50", children: icon })] }) }));
};
export const RiskBadge = ({ level, className }) => {
    const colors = {
        CRITICAL: 'bg-critical text-white',
        HIGH: 'bg-high text-white',
        MEDIUM: 'bg-medium text-white',
        LOW: 'bg-low text-white',
    };
    const color = colors[level] || 'bg-gray-600 text-white';
    return (_jsx("span", { className: clsx('px-3 py-1 rounded-full text-xs font-semibold', color, className), children: level }));
};
export const Button = ({ variant = 'primary', size = 'md', isLoading = false, children, className, ...props }) => {
    const variantStyles = {
        primary: 'bg-blue-600 hover:bg-blue-700 text-white',
        secondary: 'bg-slate-700 hover:bg-slate-600 text-white',
        danger: 'bg-critical hover:bg-red-700 text-white',
        success: 'bg-low hover:bg-green-700 text-white',
    };
    const sizeStyles = {
        sm: 'px-3 py-1 text-sm',
        md: 'px-4 py-2 text-base',
        lg: 'px-6 py-3 text-lg',
    };
    return (_jsx("button", { ...props, disabled: isLoading || props.disabled, className: clsx('rounded-lg font-medium transition disabled:opacity-50', variantStyles[variant], sizeStyles[size], className), children: isLoading ? '⏳ Loading...' : children }));
};
export const LoadingSpinner = ({ size = 'md', message = 'Loading...' }) => {
    const sizeClass = {
        sm: 'w-6 h-6',
        md: 'w-12 h-12',
        lg: 'w-16 h-16',
    };
    return (_jsxs("div", { className: "flex flex-col items-center justify-center py-8", children: [_jsx("div", { className: clsx('border-4 border-slate-600 border-t-blue-500 rounded-full animate-spin', sizeClass[size]) }), message && _jsx("p", { className: "mt-4 text-gray-300", children: message })] }));
};
export const ErrorAlert = ({ title = 'Error', message, onDismiss }) => {
    return (_jsxs("div", { className: "bg-red-900 border border-red-700 rounded-lg p-4 mb-4 flex justify-between items-start", children: [_jsxs("div", { children: [_jsx("h3", { className: "text-red-200 font-semibold", children: title }), _jsx("p", { className: "text-red-100 text-sm mt-1", children: message })] }), onDismiss && (_jsx("button", { onClick: onDismiss, className: "text-red-300 hover:text-red-100 ml-4", children: "\u2715" }))] }));
};
export const SuccessAlert = ({ title = 'Success', message, onDismiss }) => {
    return (_jsxs("div", { className: "bg-green-900 border border-green-700 rounded-lg p-4 mb-4 flex justify-between items-start", children: [_jsxs("div", { children: [_jsx("h3", { className: "text-green-200 font-semibold", children: title }), _jsx("p", { className: "text-green-100 text-sm mt-1", children: message })] }), onDismiss && (_jsx("button", { onClick: onDismiss, className: "text-green-300 hover:text-green-100 ml-4", children: "\u2715" }))] }));
};
