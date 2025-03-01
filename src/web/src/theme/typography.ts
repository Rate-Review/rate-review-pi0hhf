/**
 * Typography configuration for Justice Bid application
 * Implements design system typography specifications with Roboto font family
 * for headings and body text, and Roboto Mono for code/technical elements
 * 
 * @version 1.0.0
 */

// Base font size used throughout the application
const BASE_FONT_SIZE = '16px';

// Font families
const fontFamily = {
  primary: '"Roboto", "Helvetica", "Arial", sans-serif',
  secondary: '"Roboto", "Helvetica", "Arial", sans-serif',
  mono: '"Roboto Mono", monospace',
};

// Font size scale in rem units
const fontSize = {
  xs: '0.75rem',     // 12px
  sm: '0.875rem',    // 14px
  md: '1rem',        // 16px (base)
  lg: '1.125rem',    // 18px
  xl: '1.25rem',     // 20px
  '2xl': '1.5rem',   // 24px
  '3xl': '1.875rem', // 30px
  '4xl': '2.25rem',  // 36px
  '5xl': '3rem',     // 48px
  '6xl': '3.75rem',  // 60px
};

// Font weights as defined in the design system
const fontWeight = {
  light: 300,
  regular: 400,
  medium: 500,
  semibold: 600,
  bold: 700,
};

// Line height scale
const lineHeight = {
  none: 1,
  tight: 1.25,
  snug: 1.375,
  normal: 1.5,
  relaxed: 1.625,
  loose: 2,
};

// Typography configuration
const typography = {
  fontFamily,
  fontSize,
  fontWeight,
  lineHeight,
  
  // Heading styles
  h1: {
    fontFamily: fontFamily.primary,
    fontWeight: fontWeight.light,
    fontSize: fontSize['5xl'],
    lineHeight: lineHeight.tight,
    letterSpacing: '-0.01562em',
  },
  h2: {
    fontFamily: fontFamily.primary,
    fontWeight: fontWeight.light,
    fontSize: fontSize['4xl'],
    lineHeight: lineHeight.tight,
    letterSpacing: '-0.00833em',
  },
  h3: {
    fontFamily: fontFamily.primary,
    fontWeight: fontWeight.regular,
    fontSize: fontSize['3xl'],
    lineHeight: lineHeight.tight,
    letterSpacing: '0em',
  },
  h4: {
    fontFamily: fontFamily.primary,
    fontWeight: fontWeight.regular,
    fontSize: fontSize['2xl'],
    lineHeight: lineHeight.tight,
    letterSpacing: '0.00735em',
  },
  h5: {
    fontFamily: fontFamily.primary,
    fontWeight: fontWeight.medium,
    fontSize: fontSize.xl,
    lineHeight: lineHeight.tight,
    letterSpacing: '0em',
  },
  h6: {
    fontFamily: fontFamily.primary,
    fontWeight: fontWeight.medium,
    fontSize: fontSize.lg,
    lineHeight: lineHeight.tight,
    letterSpacing: '0.0075em',
  },
  
  // Body text styles
  body1: {
    fontFamily: fontFamily.primary,
    fontWeight: fontWeight.regular,
    fontSize: fontSize.md,
    lineHeight: lineHeight.normal,
    letterSpacing: '0.00938em',
  },
  body2: {
    fontFamily: fontFamily.primary,
    fontWeight: fontWeight.regular,
    fontSize: fontSize.sm,
    lineHeight: lineHeight.normal,
    letterSpacing: '0.01071em',
  },
  
  // Other text variants
  button: {
    fontFamily: fontFamily.primary,
    fontWeight: fontWeight.medium,
    fontSize: fontSize.sm,
    lineHeight: lineHeight.normal,
    letterSpacing: '0.02857em',
    textTransform: 'uppercase' as const,
  },
  caption: {
    fontFamily: fontFamily.primary,
    fontWeight: fontWeight.regular,
    fontSize: fontSize.xs,
    lineHeight: lineHeight.normal,
    letterSpacing: '0.03333em',
  },
  overline: {
    fontFamily: fontFamily.primary,
    fontWeight: fontWeight.regular,
    fontSize: fontSize.xs,
    lineHeight: lineHeight.normal,
    letterSpacing: '0.08333em',
    textTransform: 'uppercase' as const,
  },
  subtitle1: {
    fontFamily: fontFamily.primary,
    fontWeight: fontWeight.medium,
    fontSize: fontSize.md,
    lineHeight: lineHeight.normal,
    letterSpacing: '0.00938em',
  },
  subtitle2: {
    fontFamily: fontFamily.primary,
    fontWeight: fontWeight.medium,
    fontSize: fontSize.sm,
    lineHeight: lineHeight.normal,
    letterSpacing: '0.00714em',
  },
  
  // Monospace style for code and technical elements
  mono: {
    fontFamily: fontFamily.mono,
    fontWeight: fontWeight.regular,
    fontSize: fontSize.sm,
    lineHeight: lineHeight.normal,
    letterSpacing: '0em',
  },
};

export default typography;