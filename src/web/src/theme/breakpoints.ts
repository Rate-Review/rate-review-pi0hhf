/**
 * Breakpoints for responsive design
 * 
 * Defines breakpoint values and utility functions for creating responsive designs
 * across different screen sizes in the Justice Bid application:
 * - Mobile View (< 768px)
 * - Tablet View (768px - 1199px)
 * - Desktop View (1200px+)
 */

// Breakpoint values in pixels
const BREAKPOINTS = { xs: 0, sm: 600, md: 768, lg: 1200, xl: 1536 };

/**
 * Returns a media query string for screens larger than the specified breakpoint
 * 
 * @param key - Breakpoint key ('xs', 'sm', 'md', 'lg', 'xl')
 * @returns Media query string for use in styled-components
 * @example
 * // Returns '@media (min-width: 768px)'
 * up('md')
 */
const up = (key: string): string => {
  const value = BREAKPOINTS[key as keyof typeof BREAKPOINTS];
  return `@media (min-width: ${value}px)`;
};

/**
 * Returns a media query string for screens smaller than the specified breakpoint
 * 
 * @param key - Breakpoint key ('xs', 'sm', 'md', 'lg', 'xl')
 * @returns Media query string for use in styled-components
 * @example
 * // Returns '@media (max-width: 1199.95px)'
 * down('lg')
 */
const down = (key: string): string => {
  const value = BREAKPOINTS[key as keyof typeof BREAKPOINTS];
  // Subtract 0.05px to avoid overlap with exact breakpoint values
  return `@media (max-width: ${value - 0.05}px)`;
};

/**
 * Returns a media query string for screens between two specified breakpoints
 * 
 * @param start - Starting breakpoint key ('xs', 'sm', 'md', 'lg', 'xl')
 * @param end - Ending breakpoint key ('xs', 'sm', 'md', 'lg', 'xl')
 * @returns Media query string for use in styled-components
 * @example
 * // Returns '@media (min-width: 768px) and (max-width: 1199.95px)'
 * between('md', 'lg')
 */
const between = (start: string, end: string): string => {
  const startValue = BREAKPOINTS[start as keyof typeof BREAKPOINTS];
  const endValue = BREAKPOINTS[end as keyof typeof BREAKPOINTS];
  return `@media (min-width: ${startValue}px) and (max-width: ${endValue - 0.05}px)`;
};

// Export breakpoints and utility functions
export default {
  xs: BREAKPOINTS.xs,
  sm: BREAKPOINTS.sm,
  md: BREAKPOINTS.md,
  lg: BREAKPOINTS.lg,
  xl: BREAKPOINTS.xl,
  up,
  down,
  between,
};