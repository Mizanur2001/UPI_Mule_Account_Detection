import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import { CheckCircle, AlertCircle, AlertTriangle, Info, X } from 'lucide-react';
import { useToast } from '../hooks/useToast';
export const Toast = () => {
    const { toasts, removeToast } = useToast();
    const getIcon = (type) => {
        switch (type) {
            case 'success':
                return _jsx(CheckCircle, { size: 20, className: "text-green-400" });
            case 'error':
                return _jsx(AlertCircle, { size: 20, className: "text-red-400" });
            case 'warning':
                return _jsx(AlertTriangle, { size: 20, className: "text-yellow-400" });
            case 'info':
                return _jsx(Info, { size: 20, className: "text-blue-400" });
            default:
                return null;
        }
    };
    const getBgColor = (type) => {
        switch (type) {
            case 'success':
                return 'bg-green-900/30 border-green-700';
            case 'error':
                return 'bg-red-900/30 border-red-700';
            case 'warning':
                return 'bg-yellow-900/30 border-yellow-700';
            case 'info':
                return 'bg-blue-900/30 border-blue-700';
            default:
                return 'bg-slate-800 border-slate-700';
        }
    };
    return (_jsx("div", { className: "fixed bottom-4 right-4 space-y-2 z-50 max-w-sm", children: toasts.map((toast) => (_jsxs("div", { className: `${getBgColor(toast.type)} border rounded-lg p-4 flex items-start gap-3 animate-slideIn`, children: [getIcon(toast.type), _jsx("div", { className: "flex-1 min-w-0", children: _jsx("p", { className: "text-white text-sm font-medium", children: toast.message }) }), _jsx("button", { onClick: () => removeToast(toast.id), className: "text-gray-400 hover:text-gray-200 flex-shrink-0", children: _jsx(X, { size: 16 }) })] }, toast.id))) }));
};
