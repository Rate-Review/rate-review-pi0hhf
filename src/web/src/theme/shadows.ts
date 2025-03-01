/**
 * Shadow definitions for the Justice Bid application theme.
 * Compatible with Material UI theming system which requires an array of shadow values
 * for different elevation levels (0-24).
 */

// Shadow values that can be used directly in components
export const shadowSm = '0 1px 2px rgba(0, 0, 0, 0.05)';
export const shadowMd = '0 4px 6px rgba(0, 0, 0, 0.1)';
export const shadowLg = '0 10px 15px rgba(0, 0, 0, 0.1)';

// Array of shadow definitions for Material UI theme
// Index 0 represents no elevation (no shadow)
// Remaining indexes represent increasing elevation levels
const shadows = [
  'none',
  // Small shadows (subtle)
  '0 1px 1px rgba(0, 0, 0, 0.03), 0 1px 2px rgba(0, 0, 0, 0.05)',
  '0 1px 2px rgba(0, 0, 0, 0.05), 0 1px 4px rgba(0, 0, 0, 0.08)',
  shadowSm,
  '0 2px 4px rgba(0, 0, 0, 0.06), 0 1px 5px rgba(0, 0, 0, 0.08)',
  '0 3px 5px rgba(0, 0, 0, 0.07), 0 1px 7px rgba(0, 0, 0, 0.08)',
  // Medium shadows
  '0 3px 5px rgba(0, 0, 0, 0.08), 0 2px 8px rgba(0, 0, 0, 0.09)',
  '0 3px 6px rgba(0, 0, 0, 0.08), 0 3px 9px rgba(0, 0, 0, 0.09)',
  shadowMd,
  '0 5px 8px rgba(0, 0, 0, 0.09), 0 4px 10px rgba(0, 0, 0, 0.10)',
  '0 6px 10px rgba(0, 0, 0, 0.09), 0 4px 12px rgba(0, 0, 0, 0.10)',
  // Large shadows (pronounced)
  '0 7px 12px rgba(0, 0, 0, 0.09), 0 5px 14px rgba(0, 0, 0, 0.10)',
  '0 8px 14px rgba(0, 0, 0, 0.09), 0 6px 16px rgba(0, 0, 0, 0.10)',
  shadowLg,
  '0 10px 16px rgba(0, 0, 0, 0.10), 0 8px 18px rgba(0, 0, 0, 0.11)',
  '0 11px 18px rgba(0, 0, 0, 0.10), 0 9px 20px rgba(0, 0, 0, 0.11)',
  // Extra large shadows (dramatic)
  '0 12px 20px rgba(0, 0, 0, 0.11), 0 10px 22px rgba(0, 0, 0, 0.12)',
  '0 13px 22px rgba(0, 0, 0, 0.11), 0 11px 24px rgba(0, 0, 0, 0.12)',
  '0 14px 24px rgba(0, 0, 0, 0.12), 0 12px 26px rgba(0, 0, 0, 0.13)',
  '0 15px 26px rgba(0, 0, 0, 0.12), 0 13px 28px rgba(0, 0, 0, 0.13)',
  '0 16px 28px rgba(0, 0, 0, 0.13), 0 14px 30px rgba(0, 0, 0, 0.14)',
  // Maximum shadows (very dramatic)
  '0 17px 30px rgba(0, 0, 0, 0.13), 0 15px 32px rgba(0, 0, 0, 0.14)',
  '0 18px 32px rgba(0, 0, 0, 0.14), 0 16px 34px rgba(0, 0, 0, 0.15)',
  '0 19px 34px rgba(0, 0, 0, 0.14), 0 17px 36px rgba(0, 0, 0, 0.15)',
  '0 20px 36px rgba(0, 0, 0, 0.15), 0 18px 38px rgba(0, 0, 0, 0.16)',
];

export default shadows;