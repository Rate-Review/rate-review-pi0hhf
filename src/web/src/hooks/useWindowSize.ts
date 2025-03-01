import { useState, useEffect, useCallback } from 'react';
import useDebounce from './useDebounce';

/**
 * Interface representing window dimensions
 */
export interface WindowSize {
  width: number;
  height: number;
}

/**
 * A custom React hook that tracks and returns the current browser window dimensions.
 * This hook enables responsive behavior throughout the application by providing 
 * access to the current viewport width and height.
 *
 * The hook uses debouncing to optimize performance by limiting how often the 
 * component re-renders during window resize events.
 *
 * @returns An object containing the current window width and height
 * 
 * @example
 * // Using the hook in a component to implement responsive behavior
 * function ResponsiveComponent() {
 *   const { width, height } = useWindowSize();
 *   
 *   return (
 *     <div>
 *       {width < 768 ? <MobileView /> : <DesktopView />}
 *       <p>Current viewport dimensions: {width} x {height}</p>
 *     </div>
 *   );
 * }
 */
export function useWindowSize(): WindowSize {
  // Initialize state with default dimensions or actual window size if available
  // This handles SSR (Server-Side Rendering) where window is not available
  const [windowSize, setWindowSize] = useState<WindowSize>(() => {
    if (typeof window !== 'undefined') {
      return {
        width: window.innerWidth,
        height: window.innerHeight
      };
    }
    
    // Default values for SSR
    return {
      width: 0,
      height: 0
    };
  });
  
  // Create a memoized function to get the current window dimensions
  // This prevents unnecessary function recreations on each render
  const getWindowSize = useCallback((): WindowSize => {
    if (typeof window !== 'undefined') {
      return {
        width: window.innerWidth,
        height: window.innerHeight
      };
    }
    
    // Default values for SSR
    return {
      width: 0,
      height: 0
    };
  }, []);
  
  // Create a debounced version of the window size
  // This ensures components using this hook don't re-render too frequently during resizing
  const debouncedWindowSize = useDebounce(windowSize, 250);

  useEffect(() => {
    // Skip setup if running in SSR environment
    if (typeof window === 'undefined') {
      return;
    }

    // Handler to call on window resize
    const handleResize = () => {
      setWindowSize(getWindowSize());
    };
    
    // Add event listener
    window.addEventListener('resize', handleResize);
    
    // Call handler right away so state gets updated with initial window size
    handleResize();
    
    // Remove event listener on cleanup
    return () => {
      window.removeEventListener('resize', handleResize);
    };
  }, [getWindowSize]); // Re-run effect only if getWindowSize changes

  // Return the debounced window size
  return debouncedWindowSize;
}