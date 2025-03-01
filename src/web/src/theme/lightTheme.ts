/**
 * Light theme configuration for the Justice Bid Rate Negotiation System.
 * Combines colors, typography, spacing, shadows, and component overrides
 * to create a consistent light theme across the application.
 * 
 * @version 1.0.0
 */

import { createTheme } from '@mui/material';
import colors from '../theme/colors';
import typography from '../theme/typography';
import spacing from '../theme/spacing';
import shadows from '../theme/shadows';
import breakpoints from '../theme/breakpoints';
import { transitions } from '../theme/transitions';
import getComponentOverrides from '../theme/components';

// Create the light theme by combining all theme elements
const lightTheme = createTheme({
  // Color palette configuration
  palette: {
    mode: 'light',
    primary: {
      main: colors.primary.main,
      light: colors.primary.light,
      dark: colors.primary.dark,
      contrastText: colors.primary.contrastText,
    },
    secondary: {
      main: colors.secondary.main,
      light: colors.secondary.light,
      dark: colors.secondary.dark,
      contrastText: colors.secondary.contrastText,
    },
    error: {
      main: colors.error.main,
      light: colors.error.light,
      dark: colors.error.dark,
      contrastText: colors.error.contrastText,
    },
    warning: {
      main: colors.warning.main,
      light: colors.warning.light,
      dark: colors.warning.dark,
      contrastText: colors.warning.contrastText,
    },
    info: {
      main: colors.info.main,
      light: colors.info.light,
      dark: colors.info.dark,
      contrastText: colors.info.contrastText,
    },
    success: {
      main: colors.success.main,
      light: colors.success.light,
      dark: colors.success.dark,
      contrastText: colors.success.contrastText,
    },
    background: {
      default: colors.background.default,
      paper: colors.background.paper,
    },
    text: {
      primary: colors.text.primary,
      secondary: colors.text.secondary,
      disabled: colors.text.disabled,
    },
    divider: colors.divider,
    // Custom accent color (not part of default Material UI palette)
    accent: {
      main: colors.accent.main,
      light: colors.accent.light,
      dark: colors.accent.dark,
      contrastText: colors.accent.contrastText,
    } as any,
    // Custom neutral color (not part of default Material UI palette)
    neutral: {
      main: colors.neutral.main,
      light: colors.neutral.light,
      dark: colors.neutral.dark,
      contrastText: colors.neutral.contrastText,
    } as any,
  },
  
  // Typography configuration
  typography: typography,
  
  // Spacing configuration (using the spacing function)
  spacing: spacing.spacing,
  
  // Shadow definitions
  shadows: shadows,
  
  // Responsive breakpoints
  breakpoints: {
    values: {
      xs: breakpoints.xs,
      sm: breakpoints.sm,
      md: breakpoints.md,
      lg: breakpoints.lg,
      xl: breakpoints.xl,
    },
  },
  
  // Animation transitions
  transitions: {
    easing: {
      easeInOut: transitions.easeInOut,
      easeOut: transitions.easeOut,
      easeIn: transitions.easeIn,
      sharp: transitions.sharp,
    },
    duration: {
      shortest: 150,
      shorter: 200,
      short: 250,
      standard: 300,
      complex: 375,
      enteringScreen: 225,
      leavingScreen: 195,
    },
  },
});

// Apply component-specific style overrides
lightTheme.components = getComponentOverrides(lightTheme);

export default lightTheme;