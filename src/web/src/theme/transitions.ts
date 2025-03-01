/**
 * Transition animations and durations for the Justice Bid UI components.
 * These values ensure consistent and subtle animations throughout the application,
 * enhancing the user experience without being distracting.
 * 
 * Animation durations are kept short (150-350ms) to maintain a responsive feel.
 */

/**
 * Easing functions for animations
 */
export const easing = {
  // Standard easing with smoothing at both start and end
  easeInOut: 'cubic-bezier(0.4, 0, 0.2, 1)',
  // Deceleration curve - faster at beginning, slower at end
  easeOut: 'cubic-bezier(0.0, 0, 0.2, 1)',
  // Acceleration curve - slower at beginning, faster at end
  easeIn: 'cubic-bezier(0.4, 0, 1, 1)',
  // Sharp curve for more immediate transitions
  sharp: 'cubic-bezier(0.4, 0, 0.6, 1)',
};

/**
 * Standard transition durations
 */
export const transitions = {
  // Quick transitions for subtle feedback (e.g., button hover)
  fast: '150ms',
  // Standard transitions for most UI elements
  normal: '250ms',
  // Slower transitions for larger UI changes
  slow: '350ms',
};

/**
 * Creates a transition string with specified properties
 * 
 * @param property - CSS property to animate (e.g., 'all', 'opacity', 'transform')
 * @param duration - Duration of the transition (defaults to 'normal')
 * @param easing - Easing function to use (defaults to 'easeInOut')
 * @param delay - Delay before transition begins (defaults to '0ms')
 * @returns CSS transition string that can be used in styled components
 */
export function createTransition(
  property: string = 'all',
  duration: string = transitions.normal,
  easingFunction: string = easing.easeInOut,
  delay: string = '0ms'
): string {
  // Validate inputs
  if (!property) {
    property = 'all';
  }
  
  // Return formatted transition string
  return `${property} ${duration} ${easingFunction} ${delay}`;
}