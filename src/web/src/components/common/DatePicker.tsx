import React, { useState, useCallback, useRef, useEffect } from 'react'; // React v18.0+
import { TextField, Popover, IconButton } from '@mui/material'; // MUI v5.14.0+
import CalendarIcon from '@mui/icons-material/CalendarMonth'; // MUI v5.14.0+
import { DatePicker as MuiDatePicker, LocalizationProvider } from '@mui/x-date-pickers'; // MUI X Date Pickers v6.0.0+
import { AdapterDateFns } from '@mui/x-date-pickers/AdapterDateFns'; // MUI X Date Pickers v6.0.0+
import { useTheme } from '../context/ThemeContext';
import { formatDate } from '../utils/date';
import { isValidDate } from '../utils/validation';

/**
 * Props for the DatePicker component
 */
interface DatePickerProps {
  value: string | null;
  onChange: (value: string | null) => void;
  onBlur?: (event: React.FocusEvent<HTMLInputElement>) => void;
  format?: string;
  placeholder?: string;
  label?: string;
  error?: boolean;
  helperText?: string;
  disabled?: boolean;
  readOnly?: boolean;
  allowClear?: boolean;
  minDate?: Date | string;
  maxDate?: Date | string;
  disablePast?: boolean;
  disableFuture?: boolean;
  fullWidth?: boolean;
  className?: string;
  inputProps?: React.InputHTMLAttributes<HTMLInputElement>;
  id?: string;
  name?: string;
}

/**
 * A customizable date picker component for selecting dates in the application
 */
const DatePicker: React.FC<DatePickerProps> = ({
  value,
  onChange,
  onBlur,
  format = 'MM/dd/yyyy', // Default date format
  placeholder,
  label,
  error = false,
  helperText,
  disabled = false,
  readOnly = false,
  allowClear = true,
  minDate,
  maxDate,
  disablePast = false,
  disableFuture = false,
  fullWidth = false,
  className,
  inputProps,
  id,
  name,
}) => {
  const [date, setDate] = useState<Date | null>(null); // Internal date state
  const [inputValue, setInputValue] = useState<string>(''); // Input field value state
  const [isCalendarOpen, setIsCalendarOpen] = useState<boolean>(false); // Calendar popover visibility state
  const [anchorEl, setAnchorEl] = useState<HTMLElement | null>(null); // Element to anchor the calendar popover to
  const [hasError, setHasError] = useState<boolean>(false); // Whether the input has a validation error

  const inputRef = useRef<HTMLInputElement>(null); // Reference to the input element
  const buttonRef = useRef<HTMLButtonElement>(null); // Reference to the calendar button element

  const { theme } = useTheme(); // Access theme context for styling

  // Update internal date state when value prop changes
  useEffect(() => {
    if (value) {
      const parsedDate = new Date(value);
      if (isValidDate(parsedDate)) {
        setDate(parsedDate);
      } else {
        setDate(null);
      }
    } else {
      setDate(null);
    }
  }, [value]);

  // Reset input value when date state changes
  useEffect(() => {
    if (date) {
      setInputValue(formatDate(date, format));
    } else {
      setInputValue('');
    }
  }, [date, format]);

  /**
   * Handles changes to the date value from the calendar picker
   * @param {Date | null} newDate - The new date value
   */
  const handleDateChange = useCallback((newDate: Date | null) => {
    if (newDate === null && allowClear) {
      onChange(null);
    } else if (newDate) {
      const formattedDate = formatDate(newDate, format);
      onChange(formattedDate);
      setInputValue(formattedDate);
    }
    setDate(newDate);
    setIsCalendarOpen(false);
  }, [allowClear, format, onChange]);

  /**
   * Handles manual text input changes to the date field
   * @param {React.ChangeEvent<HTMLInputElement>} event - The input change event
   */
  const handleInputChange = useCallback((event: React.ChangeEvent<HTMLInputElement>) => {
    const { value: newValue } = event.target;
    setInputValue(newValue);

    if (newValue === '' && allowClear) {
      setDate(null);
      onChange(null);
      setHasError(false);
    } else {
      const parsedDate = new Date(newValue);
      if (isValidDate(parsedDate)) {
        setDate(parsedDate);
        onChange(formatDate(parsedDate, format));
        setHasError(false);
      } else {
        setHasError(true);
      }
    }
  }, [allowClear, format, onChange]);

  /**
   * Handles the blur event on the input field
   * @param {React.FocusEvent<HTMLInputElement>} event - The focus event
   */
  const handleBlur = useCallback((event: React.FocusEvent<HTMLInputElement>) => {
    const { value: currentValue } = event.target;

    if (currentValue === '' && allowClear) {
      setDate(null);
      onChange(null);
      setInputValue('');
      setHasError(false);
    } else {
      const parsedDate = new Date(currentValue);
      if (isValidDate(parsedDate)) {
        setDate(parsedDate);
        onChange(formatDate(parsedDate, format));
        setInputValue(formatDate(parsedDate, format));
        setHasError(false);
      } else {
        if (date) {
          setInputValue(formatDate(date, format));
        } else {
          setInputValue('');
        }
        setHasError(true);
      }
    }
    if (onBlur) {
      onBlur(event);
    }
  }, [allowClear, format, onChange, date, onBlur]);

  /**
   * Toggles the visibility of the calendar popover
   */
  const toggleCalendar = useCallback(() => {
    if (disabled || readOnly) {
      return;
    }
    setIsCalendarOpen((prev) => !prev);
    setAnchorEl(buttonRef.current);
  }, [disabled, readOnly]);

  /**
   * Handles keyboard navigation and accessibility
   * @param {React.KeyboardEvent} event - The keyboard event
   */
  const handleKeyDown = useCallback((event: React.KeyboardEvent) => {
    if (event.key === 'Enter' && event.target === buttonRef.current) {
      toggleCalendar();
    }
    if (event.key === 'Escape' && isCalendarOpen) {
      setIsCalendarOpen(false);
    }
  }, [isCalendarOpen, toggleCalendar]);

  return (
    <LocalizationProvider dateAdapter={AdapterDateFns}>
      <TextField
        id={id}
        name={name}
        label={label}
        placeholder={placeholder}
        value={inputValue}
        onChange={handleInputChange}
        onBlur={handleBlur}
        error={error || hasError}
        helperText={helperText}
        disabled={disabled}
        readOnly={readOnly}
        fullWidth={fullWidth}
        className={className}
        inputProps={{
          ...inputProps,
          'aria-label': label || 'Date',
        }}
        InputProps={{
          endAdornment: (
            <IconButton
              aria-label="toggle calendar"
              onClick={toggleCalendar}
              onKeyDown={handleKeyDown}
              edge="end"
              ref={buttonRef}
              disabled={disabled || readOnly}
            >
              <CalendarIcon />
            </IconButton>
          ),
        }}
        inputRef={inputRef}
      />
      <Popover
        open={isCalendarOpen}
        anchorEl={anchorEl}
        onClose={toggleCalendar}
        anchorOrigin={{
          vertical: 'bottom',
          horizontal: 'left',
        }}
        transformOrigin={{
          vertical: 'top',
          horizontal: 'left',
        }}
      >
        <MuiDatePicker
          value={date}
          onChange={handleDateChange}
          minDate={minDate}
          maxDate={maxDate}
          disablePast={disablePast}
          disableFuture={disableFuture}
          format={format}
        />
      </Popover>
    </LocalizationProvider>
  );
};

export default DatePicker;