/**
 * Spacing system for the Justice Bid Rate Negotiation System
 * Based on a 4px base unit with standardized increments for consistent UI spacing
 */

// Base unit for the spacing system (4px)
const SPACING_UNIT = 4;

/**
 * Spacing utility function
 * Multiplies the base unit (4px) by a given factor to create custom spacing values
 * 
 * @param factor - Multiplication factor for the base unit
 * @returns The calculated spacing value in pixels
 */
function spacing(factor: number): number {
  return SPACING_UNIT * factor;
}

/**
 * Spacing system with named constants and utility function
 * Provides standardized spacing values following the design principles
 */
const spacingSystem = {
  // Base unit value (4px)
  unit: SPACING_UNIT,
  
  // Named spacing constants
  xs: spacing(1),     // 4px  - Extra small spacing
  sm: spacing(2),     // 8px  - Small spacing
  md: spacing(4),     // 16px - Medium spacing
  lg: spacing(6),     // 24px - Large spacing
  xl: spacing(8),     // 32px - Extra large spacing
  xxl: spacing(12),   // 48px - Extra extra large spacing
  xxxl: spacing(16),  // 64px - Extra extra extra large spacing
  xxxxl: spacing(24), // 96px - Maximum spacing
  
  // Utility function for custom spacing values
  spacing,
};

export default spacingSystem;