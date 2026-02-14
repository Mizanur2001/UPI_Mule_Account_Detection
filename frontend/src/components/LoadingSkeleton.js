import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
export const LoadingSkeleton = ({ count = 3, className = '' }) => {
    return (_jsx("div", { className: `space-y-4 ${className}`, children: Array.from({ length: count }).map((_, i) => (_jsxs("div", { className: "animate-pulse space-y-2", children: [_jsx("div", { className: "h-4 bg-slate-700 rounded w-3/4" }), _jsx("div", { className: "h-4 bg-slate-700 rounded w-1/2" })] }, i))) }));
};
export const SkeletonCard = () => (_jsxs("div", { className: "bg-slate-800 rounded-lg p-4 border border-slate-700 animate-pulse", children: [_jsx("div", { className: "h-6 bg-slate-700 rounded mb-4 w-1/2" }), _jsxs("div", { className: "space-y-3", children: [_jsx("div", { className: "h-4 bg-slate-700 rounded" }), _jsx("div", { className: "h-4 bg-slate-700 rounded w-5/6" }), _jsx("div", { className: "h-4 bg-slate-700 rounded w-4/6" })] })] }));
export const SkeletonLine = ({ width = 'w-full' }) => (_jsx("div", { className: `h-2 bg-slate-700 rounded animate-pulse ${width}` }));
