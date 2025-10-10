import React, { createContext, useContext, ReactNode } from 'react';
import theme, { Theme } from './index';

const ThemeContext = createContext<Theme>(theme);

export const useTheme = () => useContext(ThemeContext);

interface ThemeProviderProps {
  children: ReactNode;
}

export const ThemeProvider = ({ children }: ThemeProviderProps) => {
  return <ThemeContext.Provider value={theme}>{children}</ThemeContext.Provider>;
};