/**
 * Colors.ts
 * 
 * Defines the color palette for the Justice Bid application.
 * These colors are used throughout the application to ensure a consistent visual identity.
 * Based on the design principles specified in the requirements.
 */

/**
 * Applies transparency to a hex color
 * @param color Hex color string
 * @param value Alpha value between 0 and 1
 * @returns RGBA color string with applied alpha
 */
const alpha = (color: string, value: number): string => {
  // Parse the hex color to extract RGB values
  const hex = color.startsWith('#') ? color.substring(1) : color;
  
  let r: number, g: number, b: number;
  
  if (hex.length === 3) {
    // If hex is 3 characters, duplicate each character
    r = parseInt(`${hex[0]}${hex[0]}`, 16);
    g = parseInt(`${hex[1]}${hex[1]}`, 16);
    b = parseInt(`${hex[2]}${hex[2]}`, 16);
  } else {
    // Standard 6 character hex
    r = parseInt(hex.substring(0, 2), 16);
    g = parseInt(hex.substring(2, 4), 16);
    b = parseInt(hex.substring(4, 6), 16);
  }
  
  // Create an RGBA string with the provided alpha value
  return `rgba(${r}, ${g}, ${b}, ${value})`;
};

/**
 * Type definitions for the color palette
 */
type ColorVariant = {
  main: string;
  light: string;
  dark: string;
  contrastText: string;
};

type BackgroundColors = {
  default: string;
  paper: string;
  light: string;
};

type TextColors = {
  primary: string;
  secondary: string;
  disabled: string;
};

type ColorPalette = {
  primary: ColorVariant;
  secondary: ColorVariant;
  accent: ColorVariant;
  neutral: ColorVariant;
  background: BackgroundColors;
  success: ColorVariant;
  warning: ColorVariant;
  error: ColorVariant;
  info: ColorVariant;
  text: TextColors;
  divider: string;
  alpha: (color: string, value: number) => string;
};

/**
 * Color palette for the Justice Bid application
 */
const colors: ColorPalette = {
  primary: {
    main: '#2C5282', // deep blue
    light: '#4A69A2',
    dark: '#1E3A5F',
    contrastText: '#FFFFFF',
  },
  secondary: {
    main: '#38A169', // green
    light: '#52B583',
    dark: '#2C8556',
    contrastText: '#FFFFFF',
  },
  accent: {
    main: '#DD6B20', // orange
    light: '#E48347',
    dark: '#B85618',
    contrastText: '#FFFFFF',
  },
  neutral: {
    main: '#718096', // slate
    light: '#8D99AC',
    dark: '#5A677A',
    contrastText: '#FFFFFF',
  },
  background: {
    default: '#F7FAFC', // off-white
    paper: '#FFFFFF',
    light: '#EDF2F7',
  },
  success: {
    main: '#38A169', // green
    light: '#52B583',
    dark: '#2C8556',
    contrastText: '#FFFFFF',
  },
  warning: {
    main: '#DD6B20', // orange
    light: '#E48347',
    dark: '#B85618',
    contrastText: '#FFFFFF',
  },
  error: {
    main: '#E53E3E', // red
    light: '#EA6868',
    dark: '#C53030',
    contrastText: '#FFFFFF',
  },
  info: {
    main: '#3182CE', // blue
    light: '#5A9AD8',
    dark: '#2B6CB0',
    contrastText: '#FFFFFF',
  },
  text: {
    primary: '#1A202C',
    secondary: '#4A5568',
    disabled: '#A0AEC0',
  },
  divider: '#E2E8F0',
  alpha,
};

export default colors;