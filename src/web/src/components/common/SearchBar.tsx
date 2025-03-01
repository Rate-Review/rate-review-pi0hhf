import React, { useState, useEffect, useCallback } from 'react'; //  ^18.0.0
import { TextField } from '../common/TextField';
import { useDebounce } from '../../hooks/useDebounce';
import { Search as SearchIcon, Clear as ClearIcon } from '@mui/icons-material'; //  ^5.14.0
import { InputAdornment, IconButton } from '@mui/material'; //  ^5.14.0

/**
 * Interface defining the props for the SearchBar component.
 * It includes properties for placeholder text, search callback, initial value,
 * debounce time, clear button visibility, start adornment, and custom styling.
 */
interface SearchBarProps {
  placeholder?: string;
  onSearch?: (value: string) => void;
  value?: string;
  debounceTime?: number;
  showClearButton?: boolean;
  startAdornment?: React.ReactNode;
  className?: string;
  ariaLabel?: string;
}

/**
 * A reusable search component with debounced input handling, clear button, and customizable styling.
 * It provides a consistent search experience across the application and enables users to search and filter data in tables and lists.
 *
 * @param {SearchBarProps} props - The props for the SearchBar component.
 * @returns {JSX.Element} Rendered search bar component.
 */
const SearchBar: React.FC<SearchBarProps> = (props) => {
  // LD1: Destructure props for placeholder, onSearch, value, debounceTime, etc. with defaults
  const {
    placeholder = 'Search',
    onSearch,
    value: controlledValue,
    debounceTime = 300,
    showClearButton = true,
    startAdornment,
    className,
    ariaLabel = 'Search'
  } = props;

  // LD1: Initialize inputValue state with the provided value or empty string using useState
  const [inputValue, setInputValue] = useState<string>(controlledValue || '');

  // LD1: Apply useDebounce hook to inputValue with specified debounceTime (default 300ms)
  const debouncedValue = useDebounce<string>(inputValue, debounceTime);

  // LD1: Create useEffect to call onSearch when debouncedValue changes
  useEffect(() => {
    if (onSearch) {
      onSearch(debouncedValue);
    }
  }, [debouncedValue, onSearch]);

  // LD1: Create useEffect to update inputValue when controlled value prop changes
  useEffect(() => {
    if (controlledValue !== undefined) {
      setInputValue(controlledValue);
    }
  }, [controlledValue]);

  // LD1: Define handleChange function to update inputValue on input changes
  const handleChange = useCallback((event: React.ChangeEvent<HTMLInputElement>) => {
    setInputValue(event.target.value);
  }, []);

  // LD1: Define handleClear function to clear the input and trigger search with empty string
  const handleClear = useCallback(() => {
    setInputValue('');
    if (onSearch) {
      onSearch('');
    }
  }, [onSearch]);

  // LD1: Render TextField with search icon as startAdornment
  // LD1: Add clear button as endAdornment when showClearButton is true and inputValue exists
  // LD1: Apply proper aria attributes for accessibility
  return (
    <TextField
      aria-label={ariaLabel}
      className={className}
      placeholder={placeholder}
      value={inputValue}
      onChange={handleChange}
      InputProps={{
        startAdornment: (
          <InputAdornment position="start">
            {startAdornment || <SearchIcon />}
          </InputAdornment>
        ),
        endAdornment: showClearButton && inputValue ? (
          <InputAdornment position="end">
            <IconButton
              aria-label="clear"
              onClick={handleClear}
              edge="end"
            >
              <ClearIcon />
            </IconButton>
          </InputAdornment>
        ) : null,
      }}
    />
  );
};

// IE3: Be generous about your exports so long as it doesn't create a security risk.
export default SearchBar;