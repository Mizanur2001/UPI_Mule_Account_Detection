import React from 'react';
import { CheckCircle, AlertCircle, AlertTriangle, Info, X } from 'lucide-react';
import { useToast } from '../hooks/useToast';

export const Toast: React.FC = () => {
  const { toasts, removeToast } = useToast();

  const getIcon = (type: string) => {
    switch (type) {
      case 'success':
        return <CheckCircle size={20} className="text-green-400" />;
      case 'error':
        return <AlertCircle size={20} className="text-red-400" />;
      case 'warning':
        return <AlertTriangle size={20} className="text-yellow-400" />;
      case 'info':
        return <Info size={20} className="text-blue-400" />;
      default:
        return null;
    }
  };

  const getBgColor = (type: string) => {
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

  return (
    <div className="fixed bottom-4 right-4 space-y-2 z-50 max-w-sm">
      {toasts.map((toast) => (
        <div
          key={toast.id}
          className={`${getBgColor(toast.type)} border rounded-lg p-4 flex items-start gap-3 animate-slideIn`}
        >
          {getIcon(toast.type)}
          <div className="flex-1 min-w-0">
            <p className="text-white text-sm font-medium">{toast.message}</p>
          </div>
          <button
            onClick={() => removeToast(toast.id)}
            className="text-gray-400 hover:text-gray-200 flex-shrink-0"
          >
            <X size={16} />
          </button>
        </div>
      ))}
    </div>
  );
};
