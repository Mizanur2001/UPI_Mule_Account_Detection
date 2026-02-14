import { jsx as _jsx } from "react/jsx-runtime";
import { createContext, useState, useEffect, useCallback } from 'react';
export const ThemeContext = createContext(undefined);
export const ThemeProvider = ({ children }) => {
    const [theme, setTheme] = useState(() => {
        // Get from localStorage or default to 'dark'
        const stored = localStorage.getItem('theme');
        return stored || 'dark';
    });
    const toggleTheme = useCallback(() => {
        setTheme((prev) => (prev === 'dark' ? 'light' : 'dark'));
    }, []);
    // Apply theme to document
    useEffect(() => {
        localStorage.setItem('theme', theme);
        if (theme === 'dark') {
            document.documentElement.classList.add('dark');
        }
        else {
            document.documentElement.classList.remove('dark');
        }
    }, [theme]);
    return (_jsx(ThemeContext.Provider, { value: { theme, toggleTheme }, children: children }));
};
