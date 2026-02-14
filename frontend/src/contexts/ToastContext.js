import { jsx as _jsx } from "react/jsx-runtime";
import { createContext, useState, useCallback } from 'react';
export const ToastContext = createContext(undefined);
export const ToastProvider = ({ children }) => {
    const [toasts, setToasts] = useState([]);
    const addToast = useCallback((message, type, duration = 3000) => {
        const id = `toast-${Date.now()}-${Math.random()}`;
        const newToast = { id, message, type, duration };
        setToasts((prev) => [...prev, newToast]);
        if (duration > 0) {
            setTimeout(() => {
                removeToast(id);
            }, duration);
        }
        return id;
    }, []);
    const removeToast = useCallback((id) => {
        setToasts((prev) => prev.filter((toast) => toast.id !== id));
    }, []);
    return (_jsx(ToastContext.Provider, { value: { toasts, addToast, removeToast }, children: children }));
};
