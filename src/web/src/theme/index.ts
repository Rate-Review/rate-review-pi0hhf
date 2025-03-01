/**
 * Main theme configuration file for the Justice Bid Rate Negotiation System
 * Exports theme objects and utilities that can be used throughout the application
 * Implements design principles: Modern & Professional UI Design and Responsive Design
 * 
 * @version 1.0.0
 */

// External imports from Material UI
import { Theme } from '@mui/material';

// Import pre-configured theme objects
import lightTheme from './lightTheme';
import darkTheme from './darkTheme';

/**
 * Returns the appropriate theme based on the specified mode
 * 
 * @param mode - The theme mode ('light' or 'dark')
 * @returns The corresponding theme object
 */
export const getTheme = (mode: string): Theme => {
  return mode === 'dark' ? darkTheme : lightTheme;
};

// Export named themes
export { lightTheme, darkTheme };

// Default export is the light theme (standard mode)
export default lightTheme;