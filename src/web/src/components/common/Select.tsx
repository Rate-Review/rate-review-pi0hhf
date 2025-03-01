import React, { useState, useEffect, useId } from 'react';
import styled from 'styled-components';
import colors from '../../theme/colors';
import spacing from '../../theme/spacing';
import { isRequired } from '../../utils/validation';

// Define available select sizes
export type SelectSize = 'small' | 'medium' | 'large';

// Define option structure for the Select component
export interface SelectOption {
  value: string | number;
  label: string;
  disabled?: boolean;
}

// Define option group structure for grouping related options
export interface OptionGroup {
  label: string;
  options: SelectOption[];
}

// Props for the Select component
export interface SelectProps {
  id?: string;
  name: string;
  label?: string;
  value?: string | string[];
  onChange?: (value: string | string[]) => void;
  onBlur?: (event: React.FocusEvent<HTMLSelectElement>) => void;
  options: SelectOption[];
  required?: boolean;
  disabled?: boolean;
  multiple?: boolean;
  placeholder?: string;
  error?: string;
  fullWidth?: boolean;
  size?: SelectSize;
  className?: string;
  validateOnBlur?: boolean;
  validate?: (value: string | string[]) => string | null;
  helpText?: string;
  groups?: OptionGroup[];
}

// Styled components for the Select
const SelectContainer = styled.div<{ fullWidth?: boolean }>`
  position: relative;
  width: ${props => props.fullWidth ? '100%' : 'auto'};
  margin-bottom: ${props => props.theme.spacing.md}px;
`;

const SelectLabel = styled.label<{ required?: boolean; disabled?: boolean }>`
  display: block;
  margin-bottom: ${props => props.theme.spacing.sm}px;
  font-weight: 500;
  color: ${props => props.theme.colors.primary.main};
  font-size: 14px;
  
  ${props => props.required && `
    &::after {
      content: '*';
      color: ${props.theme.colors.error.main};
      margin-left: 4px;
    }
  `}
  
  ${props => props.disabled && `
    opacity: 0.6;
  `}
`;

const StyledSelect = styled.select<{
  size?: SelectSize;
  disabled?: boolean;
  hasError?: boolean;
}>`
  width: 100%;
  padding: 8px 16px;
  font-size: 16px;
  line-height: 1.5;
  color: ${props => props.theme.colors.text.primary};
  background-color: ${props => props.theme.colors.background.paper};
  border: 1px solid ${props => props.hasError ? props.theme.colors.error.main : '#CBD5E0'};
  border-radius: 4px;
  appearance: none;
  background-image: url('data:image/svg+xml;utf8,<svg fill="%23718096" viewBox="0 0 20 20" xmlns="http://www.w3.org/2000/svg"><path d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z"></path></svg>');
  background-repeat: no-repeat;
  background-position: right 16px center;
  background-size: 16px 16px;
  transition: border-color 0.15s ease-in-out, box-shadow 0.15s ease-in-out;

  &:focus {
    outline: none;
    border-color: ${props => props.theme.colors.primary.main};
    box-shadow: 0 0 0 3px rgba(49, 130, 206, 0.25);
  }
  
  /* Size variants */
  ${props => props.size === 'small' && `
    padding: 6px 12px;
    font-size: 14px;
  `}
  
  ${props => props.size === 'medium' && `
    padding: 8px 16px;
    font-size: 16px;
  `}
  
  ${props => props.size === 'large' && `
    padding: 10px 20px;
    font-size: 18px;
  `}
  
  /* Disabled state */
  ${props => props.disabled && `
    opacity: 0.6;
    cursor: not-allowed;
    background-color: ${props.theme.colors.background.light};
  `}
  
  /* Error state */
  ${props => props.hasError && `
    border-color: ${props.theme.colors.error.main};
    &:focus {
      box-shadow: 0 0 0 3px rgba(229, 62, 62, 0.25);
    }
  `}
`;

const ErrorMessage = styled.div`
  color: ${props => props.theme.colors.error.main};
  font-size: 14px;
  margin-top: 4px;
`;

const HelpText = styled.div`
  color: ${props => props.theme.colors.text.secondary};
  font-size: 14px;
  margin-top: 4px;
`;

/**
 * A customizable select dropdown component that supports validation, grouping, and multiple selection
 */
const Select: React.FC<SelectProps> = ({
  id,
  name,
  label,
  value,
  onChange,
  onBlur,
  options = [],
  required = false,
  disabled = false,
  multiple = false,
  placeholder,
  error,
  fullWidth = true,
  size = 'medium',
  className,
  validateOnBlur = true,
  validate,
  helpText,
  groups
}) => {
  // Generate a unique ID for the select if not provided
  const uniqueId = useId();
  const selectId = id || `select-${uniqueId}`;
  
  // Track touched state to show validation errors at the right time
  const [touched, setTouched] = useState(false);
  
  // State for error message
  const [errorMessage, setErrorMessage] = useState(error || '');
  
  // State for uncontrolled component
  const [internalValue, setInternalValue] = useState<string | string[]>(
    value !== undefined ? value : multiple ? [] : ''
  );
  
  // Update internal state when controlled value changes
  useEffect(() => {
    if (value !== undefined) {
      setInternalValue(value);
    }
  }, [value]);
  
  // Update error message when prop changes
  useEffect(() => {
    setErrorMessage(error || '');
  }, [error]);
  
  // Determine if we're controlled or uncontrolled
  const isControlled = value !== undefined;
  const currentValue = isControlled ? value : internalValue;
  
  // Determine if we have validation
  const hasValidation = required || !!validate;
  
  // Validation function
  const validateValue = (val: string | string[]): string | null => {
    // Required validation
    if (required) {
      if (Array.isArray(val)) {
        if (val.length === 0) return 'This field is required';
      } else if (!isRequired(val)) {
        return 'This field is required';
      }
    }
    
    // Custom validation if provided
    if (validate) {
      return validate(val);
    }
    
    return null;
  };
  
  // Handle change event
  const handleSelectChange = (event: React.ChangeEvent<HTMLSelectElement>) => {
    let newValue: string | string[];
    
    if (multiple) {
      // For multi-select, get all selected options
      const selectedOptions = Array.from(event.target.selectedOptions, option => option.value);
      newValue = selectedOptions;
    } else {
      // For single select, get the selected value
      newValue = event.target.value;
    }
    
    // Run validation if applicable
    if (hasValidation) {
      const validationError = validateValue(newValue);
      setErrorMessage(validationError || '');
    }
    
    // Call onChange callback if provided
    if (onChange) {
      onChange(newValue);
    }
    
    // Update internal state if uncontrolled
    if (!isControlled) {
      setInternalValue(newValue);
    }
  };
  
  // Handle blur event
  const handleBlur = (event: React.FocusEvent<HTMLSelectElement>) => {
    // Mark as touched
    setTouched(true);
    
    // Validate on blur if requested
    if (hasValidation && validateOnBlur) {
      let valueToValidate: string | string[];
      
      if (multiple) {
        // For multi-select, get all selected options
        valueToValidate = Array.from(event.target.selectedOptions, option => option.value);
      } else {
        // For single select, get the selected value
        valueToValidate = event.target.value;
      }
      
      const validationError = validateValue(valueToValidate);
      setErrorMessage(validationError || '');
    }
    
    // Call onBlur callback if provided
    if (onBlur) {
      onBlur(event);
    }
  };
  
  // Determine if we should show an error message
  const showError = touched && errorMessage;
  
  return (
    <SelectContainer fullWidth={fullWidth} className={className}>
      {label && (
        <SelectLabel 
          htmlFor={selectId}
          required={required}
          disabled={disabled}
        >
          {label}
        </SelectLabel>
      )}
      
      <StyledSelect
        id={selectId}
        name={name}
        value={currentValue}
        onChange={handleSelectChange}
        onBlur={handleBlur}
        disabled={disabled}
        multiple={multiple}
        size={multiple ? 5 : undefined}
        hasError={!!showError}
        aria-invalid={!!showError}
        aria-describedby={showError ? `${selectId}-error` : helpText ? `${selectId}-help` : undefined}
        required={required}
        aria-required={required}
      >
        {/* Add placeholder option if provided */}
        {placeholder && !multiple && (
          <option value="" disabled>
            {placeholder}
          </option>
        )}
        
        {/* Render option groups if provided */}
        {groups && groups.length > 0 ? (
          groups.map((group, groupIndex) => (
            <optgroup key={`group-${groupIndex}`} label={group.label}>
              {group.options.map((option, optionIndex) => (
                <option
                  key={`group-${groupIndex}-option-${optionIndex}`}
                  value={option.value.toString()}
                  disabled={option.disabled}
                >
                  {option.label}
                </option>
              ))}
            </optgroup>
          ))
        ) : (
          /* Render flat options list */
          options.map((option, index) => (
            <option
              key={`option-${index}`}
              value={option.value.toString()}
              disabled={option.disabled}
            >
              {option.label}
            </option>
          ))
        )}
      </StyledSelect>
      
      {/* Show error message if there is one and the field has been touched */}
      {showError && (
        <ErrorMessage id={`${selectId}-error`} role="alert">
          {errorMessage}
        </ErrorMessage>
      )}
      
      {/* Show help text if provided and no error is showing */}
      {helpText && !showError && (
        <HelpText id={`${selectId}-help`}>
          {helpText}
        </HelpText>
      )}
    </SelectContainer>
  );
};

export default Select;