/**
 * Responsive utilities for Justice Bid application
 * 
 * Provides functions to handle responsive design across different screen sizes:
 * - Mobile View (< 768px)
 * - Tablet View (768px - 1199px)
 * - Desktop View (1200px+)
 * 
 * @version 1.0.0
 */

import { useWindowSize } from '../hooks/useWindowSize';
import theme from '../theme';

/**
 * Determines if the current screen width is within mobile breakpoint range
 * 
 * @returns {boolean} True if current screen width is less than the tablet breakpoint (md)
 */
export const isMobile = (): boolean => {
  const { width } = useWindowSize();
  return width < theme.breakpoints.values.md;
};

/**
 * Determines if the current screen width is within tablet breakpoint range
 * 
 * @returns {boolean} True if current screen width is between tablet (md) and desktop (lg) breakpoints
 */
export const isTablet = (): boolean => {
  const { width } = useWindowSize();
  return width >= theme.breakpoints.values.md && width < theme.breakpoints.values.lg;
};

/**
 * Determines if the current screen width is within desktop breakpoint range
 * 
 * @returns {boolean} True if current screen width is greater than or equal to desktop breakpoint (lg)
 */
export const isDesktop = (): boolean => {
  const { width } = useWindowSize();
  return width >= theme.breakpoints.values.lg;
};

/**
 * Returns the current device type based on screen width
 * 
 * @returns {string} Device type: 'mobile', 'tablet', or 'desktop'
 */
export const getDeviceType = (): 'mobile' | 'tablet' | 'desktop' => {
  if (isMobile()) return 'mobile';
  if (isTablet()) return 'tablet';
  return 'desktop';
};

/**
 * Determines if a component should be rendered on mobile devices
 * 
 * @param {boolean} hiddenOnMobile - Whether the component should be hidden on mobile
 * @returns {boolean} False if on mobile and hiddenOnMobile is true, otherwise true
 */
export const shouldRenderOnMobile = (hiddenOnMobile: boolean): boolean => {
  return !(hiddenOnMobile && isMobile());
};

/**
 * Determines if a component should be rendered on tablet devices
 * 
 * @param {boolean} hiddenOnTablet - Whether the component should be hidden on tablet
 * @returns {boolean} False if on tablet and hiddenOnTablet is true, otherwise true
 */
export const shouldRenderOnTablet = (hiddenOnTablet: boolean): boolean => {
  return !(hiddenOnTablet && isTablet());
};

/**
 * Determines if a component should be rendered on desktop devices
 * 
 * @param {boolean} hiddenOnDesktop - Whether the component should be hidden on desktop
 * @returns {boolean} False if on desktop and hiddenOnDesktop is true, otherwise true
 */
export const shouldRenderOnDesktop = (hiddenOnDesktop: boolean): boolean => {
  return !(hiddenOnDesktop && isDesktop());
};

/**
 * Returns a value based on current device type
 * 
 * @param {Object} values - Object containing values for different device types
 * @param {any} values.mobile - Value for mobile devices
 * @param {any} values.tablet - Value for tablet devices
 * @param {any} values.desktop - Value for desktop devices
 * @returns {any} The appropriate value for the current device type
 * 
 * @example
 * // Returns '100%' on mobile, '50%' on tablet, '33.33%' on desktop
 * const width = getResponsiveValue({ mobile: '100%', tablet: '50%', desktop: '33.33%' });
 */
export const getResponsiveValue = <T>(values: {
  mobile?: T;
  tablet?: T;
  desktop: T;
}): T => {
  const deviceType = getDeviceType();
  
  if (deviceType === 'mobile' && values.mobile !== undefined) {
    return values.mobile;
  }
  
  if (deviceType === 'tablet' && values.tablet !== undefined) {
    return values.tablet;
  }
  
  return values.desktop;
};

/**
 * Generates a className string based on device type
 * 
 * @param {string} baseClass - Base class to be applied to all device types
 * @param {Object} modifiers - Object containing additional classes for different device types
 * @param {string} modifiers.mobile - Additional class for mobile devices
 * @param {string} modifiers.tablet - Additional class for tablet devices
 * @param {string} modifiers.desktop - Additional class for desktop devices
 * @returns {string} Combined className string with appropriate device-specific modifiers
 * 
 * @example
 * // Returns 'card card--fullwidth' on mobile, 'card card--half' on tablet, 'card' on desktop
 * const className = getResponsiveClassName('card', { 
 *   mobile: 'card--fullwidth', 
 *   tablet: 'card--half' 
 * });
 */
export const getResponsiveClassName = (
  baseClass: string,
  modifiers?: {
    mobile?: string;
    tablet?: string;
    desktop?: string;
  }
): string => {
  if (!modifiers) return baseClass;
  
  const deviceType = getDeviceType();
  let additionalClass = '';
  
  if (deviceType === 'mobile' && modifiers.mobile) {
    additionalClass = modifiers.mobile;
  } else if (deviceType === 'tablet' && modifiers.tablet) {
    additionalClass = modifiers.tablet;
  } else if (deviceType === 'desktop' && modifiers.desktop) {
    additionalClass = modifiers.desktop;
  }
  
  return additionalClass ? `${baseClass} ${additionalClass}` : baseClass;
};

/**
 * Returns the appropriate number of columns for grid layouts based on current device type
 * 
 * @param {number} desktopColumns - Number of columns for desktop view (default: 4)
 * @param {number} tabletColumns - Number of columns for tablet view (default: 2)
 * @param {number} mobileColumns - Number of columns for mobile view (default: 1)
 * @returns {number} Number of columns appropriate for current device
 * 
 * @example
 * // Returns 1 on mobile, 2 on tablet, 3 on desktop
 * const columns = getColumnCount(3, 2, 1);
 */
export const getColumnCount = (
  desktopColumns: number = 4,
  tabletColumns: number = 2,
  mobileColumns: number = 1
): number => {
  const deviceType = getDeviceType();
  
  switch (deviceType) {
    case 'mobile':
      return mobileColumns;
    case 'tablet':
      return tabletColumns;
    default:
      return desktopColumns;
  }
};