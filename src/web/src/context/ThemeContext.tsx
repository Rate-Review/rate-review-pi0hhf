import { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import lightTheme from '../theme/lightTheme';
import darkTheme from '../theme/darkTheme';

/**
 * Type definition for theme context values
 */
interface ThemeContextType {
  theme: typeof lightTheme;
  themeMode: string;
  toggleTheme: () => void;
}

/**
 * Props interface for ThemeProvider component
 */
interface ThemeProviderProps {
  children: ReactNode;
  initialTheme?: string;
}

/**
 * Context for theme-related data and functions
 */
const ThemeContext = createContext<ThemeContextType | undefined>(undefined);

/**
 * Provider component that makes theme available to child components
 * 
 * @param {ReactNode} children - Child components that will have access to the theme context
 * @param {string} [initialTheme] - Optional initial theme mode ('light' or 'dark')
 */
const ThemeProvider: React.FC<ThemeProviderProps> = ({ children, initialTheme }) => {
  // Initialize theme from props, localStorage or system preference
  const getInitialTheme = (): string => {
    if (initialTheme) return initialTheme;
    
    if (typeof window !== 'undefined') {
      const savedTheme = localStorage.getItem('theme');
      if (savedTheme) return savedTheme;
      
      // Check for system preference
      if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
        return 'dark';
      }
    }
    
    return 'light'; // Default to light theme
  };

  const [themeMode, setThemeMode] = useState<string>(getInitialTheme());
  
  // Set the active theme object based on themeMode
  const theme = themeMode === 'dark' ? darkTheme : lightTheme;

  // Toggle between light and dark themes
  const toggleTheme = () => {
    setThemeMode(prevMode => prevMode === 'light' ? 'dark' : 'light');
  };

  // Store theme preference in localStorage when it changes
  useEffect(() => {
    if (typeof window !== 'undefined') {
      localStorage.setItem('theme', themeMode);
    }
  }, [themeMode]);

  // Apply theme to document body by setting a data-theme attribute
  useEffect(() => {
    if (typeof document !== 'undefined') {
      document.body.setAttribute('data-theme', themeMode);
    }
  }, [themeMode]);

  const value = {
    theme,
    themeMode,
    toggleTheme
  };

  return (
    <ThemeContext.Provider value={value}>
      {children}
    </ThemeContext.Provider>
  );
};

/**
 * Custom hook to access theme context values
 * 
 * @returns {ThemeContextType} Theme context object with theme, themeMode, and toggleTheme function
 * @throws {Error} If used outside of a ThemeProvider
 */
const useTheme = (): ThemeContextType => {
  const context = useContext(ThemeContext);
  
  if (context === undefined) {
    throw new Error('useTheme must be used within a ThemeProvider');
  }
  
  return context;
};

export { ThemeContext, ThemeProvider, useTheme };