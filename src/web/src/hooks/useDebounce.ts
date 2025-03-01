import { useState, useEffect } from 'react'; // ^18.0.0

/**
 * A custom hook that returns a debounced version of the provided value,
 * which only updates after the specified delay has passed without the original value changing.
 * This hook is useful for optimizing performance when dealing with rapidly changing values
 * like search inputs or API calls in rate negotiation interfaces.
 *
 * @template T The type of the value being debounced
 * @param value The value to be debounced
 * @param delay The delay in milliseconds before the value updates
 * @returns The debounced value
 * 
 * @example
 * // Debouncing search input in rate table filter
 * const [searchTerm, setSearchTerm] = useState('');
 * const debouncedSearchTerm = useDebounce(searchTerm, 500);
 * 
 * // Only trigger API calls when debouncedSearchTerm changes
 * useEffect(() => {
 *   if (debouncedSearchTerm) {
 *     fetchRates(debouncedSearchTerm);
 *   }
 * }, [debouncedSearchTerm]);
 */
function useDebounce<T>(value: T, delay: number): T {
  // Store the debounced value in state, initially set to the provided value
  const [debouncedValue, setDebouncedValue] = useState<T>(value);

  useEffect(() => {
    // Create a timeout that will update the debounced value after the specified delay
    const timer = setTimeout(() => {
      setDebouncedValue(value);
    }, delay);

    // Clean up function to clear the timeout if the value changes before the delay expires
    // or if the component unmounts
    return () => {
      clearTimeout(timer);
    };
  }, [value, delay]); // Re-run effect when value or delay changes

  // Return the debounced value
  return debouncedValue;
}

export default useDebounce;