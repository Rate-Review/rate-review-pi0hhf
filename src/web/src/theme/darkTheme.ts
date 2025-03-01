/**
 * Dark theme configuration for the Justice Bid Rate Negotiation System
 * Implements a professional dark mode that maintains brand identity while meeting accessibility standards
 */

import { createTheme, ThemeOptions, PaletteOptions } from '@mui/material';
import { primary, secondary, accent, neutral } from './colors';
import spacing from './spacing';
import typography from './typography';
import shadows from './shadows';
import breakpoints from './breakpoints';
import transitions from './transitions';
import { getComponentOverrides } from './components';

/**
 * Creates the dark theme palette configuration
 * Adjusts colors for dark mode while maintaining brand identity and ensuring accessibility
 */
function createDarkThemePalette(): PaletteOptions {
  return {
    mode: 'dark',
    primary: {
      main: primary.light, // Lighter version for better visibility on dark backgrounds
      light: '#7B9CD2', // Lightened further for contrast
      dark: primary.main, // Original primary as dark in dark mode
      contrastText: '#FFFFFF',
    },
    secondary: {
      main: secondary.light, // Lighter version for better visibility
      light: '#78C79A', // Lightened further
      dark: secondary.main, // Original secondary as dark in dark mode
      contrastText: '#FFFFFF',
    },
    accent: {
      main: accent.main, // Keep accent color similar for brand recognition
      light: accent.light,
      dark: accent.dark,
      contrastText: '#FFFFFF',
    },
    neutral: {
      main: '#9DB2C8', // Lightened neutral color for dark mode
      light: '#B9C9D9',
      dark: '#7991AC',
      contrastText: '#000000',
    },
    error: {
      main: '#F45B5B', // Brightened error for dark mode
      light: '#F78282',
      dark: '#D13F3F',
      contrastText: '#FFFFFF',
    },
    warning: {
      main: '#FFA726', // Brightened warning for dark mode
      light: '#FFB851',
      dark: '#F57C00',
      contrastText: '#000000',
    },
    info: {
      main: '#64B5F6', // Brightened info for dark mode
      light: '#90CAF9',
      dark: '#42A5F5',
      contrastText: '#000000',
    },
    success: {
      main: '#66BB6A', // Brightened success for dark mode
      light: '#81C784',
      dark: '#4CAF50',
      contrastText: '#000000',
    },
    background: {
      default: '#121212', // Material dark theme standard
      paper: '#1E1E1E', // Slightly lighter than default
      light: '#2C2C2C', // For subtle variations
    },
    text: {
      primary: '#FFFFFF',
      secondary: '#B0B0B0',
      disabled: '#6C6C6C',
    },
    divider: 'rgba(255, 255, 255, 0.12)',
  };
}

// Create the dark theme by combining all theme elements
const darkTheme = createTheme({
  palette: createDarkThemePalette(),
  typography,
  spacing: spacing.spacing,
  shadows,
  breakpoints,
  components: getComponentOverrides({
    palette: createDarkThemePalette() as any,
    spacing: spacing.spacing as any,
    shape: { borderRadius: spacing.sm } as any,
  }),
  shape: {
    borderRadius: spacing.sm,
  },
  transitions: {
    easing: {
      easeInOut: transitions.easing.easeInOut,
      easeOut: transitions.easing.easeOut,
      easeIn: transitions.easing.easeIn,
      sharp: transitions.easing.sharp,
    },
    duration: {
      shortest: parseInt(transitions.transitions.fast),
      shorter: parseInt(transitions.transitions.fast),
      short: parseInt(transitions.transitions.normal),
      standard: parseInt(transitions.transitions.normal),
      complex: parseInt(transitions.transitions.slow),
      enteringScreen: parseInt(transitions.transitions.normal),
      leavingScreen: parseInt(transitions.transitions.normal),
    },
  },
} as ThemeOptions);

export default darkTheme;