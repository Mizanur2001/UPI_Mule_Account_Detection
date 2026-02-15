import React, { createContext, useState, useEffect, useCallback } from 'react';

type Theme = 'dark' | 'light';

interface ThemeContextType {
  theme: Theme;
  toggleTheme: () => void;
}

export const ThemeContext = createContext<ThemeContextType | undefined>(undefined);

const applyTheme = (theme: Theme) => {
  console.log('[Theme] Applying theme:', theme);
  const html = document.documentElement;
  
  // Remove any old theme class first
  html.classList.remove('dark', 'light');
  
  // Add new theme class
  if (theme === 'dark') {
    html.classList.add('dark');
    html.style.colorScheme = 'dark';
  } else {
    html.classList.add('light');
    html.style.colorScheme = 'light';
  }
  
  // Force repaint by requesting animation frame
  requestAnimationFrame(() => {
    console.log('[Theme] Current classes:', html.className);
    console.log('[Theme] Colors:', { bg: getComputedStyle(document.body).backgroundColor });
  });
};

export const ThemeProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [theme, setTheme] = useState<Theme>(() => {
    const stored = localStorage.getItem('theme') as Theme | null;
    const initialTheme = stored || 'dark';
    // Delay application to ensure DOM is ready
    setTimeout(() => applyTheme(initialTheme), 0);
    return initialTheme;
  });

  const toggleTheme = useCallback(() => {
    setTheme((prev) => {
      const newTheme = prev === 'dark' ? 'light' : 'dark';
      console.log('[Theme] Toggle detected:', { from: prev, to: newTheme });
      
      // Save immediately
      localStorage.setItem('theme', newTheme);
      
      // Apply with a slight delay to ensure React state update first
      setTimeout(() => {
        applyTheme(newTheme);
      }, 10);
      
      return newTheme;
    });
  }, []);

  useEffect(() => {
    applyTheme(theme);
  }, [theme]);

  return (
    <ThemeContext.Provider value={{ theme, toggleTheme }}>
      {children}
    </ThemeContext.Provider>
  );
};
