import React, { createContext, useContext, useState, useEffect } from 'react';
import { useColorScheme } from 'react-native';

// Theme colors
export const lightTheme = {
  primary: '#4CAF50',
  primaryLight: '#E8F5E9',
  secondary: '#9C27B0',
  secondaryLight: '#F3E5F5',
  accent: '#FF9800',
  accentLight: '#FFF3E0',
  success: '#2E7D32',
  successLight: '#E8F5E9',
  warning: '#FF9800',
  warningLight: '#FFF3E0',
  error: '#D32F2F',
  errorLight: '#FFEBEE',
  background: '#F5F5F5',
  card: '#FFFFFF',
  text: '#212121',
  textSecondary: '#757575',
  border: '#E0E0E0',
  white: '#FFFFFF',
};

export const darkTheme = {
  primary: '#81C784',
  primaryLight: '#1B5E20',
  secondary: '#CE93D8',
  secondaryLight: '#4A148C',
  accent: '#FFB74D',
  accentLight: '#E65100',
  success: '#66BB6A',
  successLight: '#1B5E20',
  warning: '#FFA726',
  warningLight: '#E65100',
  error: '#EF5350',
  errorLight: '#B71C1C',
  background: '#121212',
  card: '#1E1E1E',
  text: '#FFFFFF',
  textSecondary: '#B0B0B0',
  border: '#2C2C2C',
  white: '#FFFFFF',
};

type Theme = typeof lightTheme;

interface ThemeContextType {
  colors: Theme;
  isDark: boolean;
  toggleTheme: () => void;
}

const ThemeContext = createContext<ThemeContextType>({
  colors: lightTheme,
  isDark: false,
  toggleTheme: () => {},
});

export const useTheme = () => useContext(ThemeContext);

export const ThemeProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const colorScheme = useColorScheme();
  const [isDark, setIsDark] = useState(colorScheme === 'dark');
  const colors = isDark ? darkTheme : lightTheme;

  // Update theme when system theme changes
  useEffect(() => {
    setIsDark(colorScheme === 'dark');
  }, [colorScheme]);

  const toggleTheme = () => {
    setIsDark(prev => !prev);
  };

  return (
    <ThemeContext.Provider value={{ colors, isDark, toggleTheme }}>
      {children}
    </ThemeContext.Provider>
  );
};