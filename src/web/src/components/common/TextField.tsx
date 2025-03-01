import React, { useState, ChangeEvent, FocusEvent } from 'react'; //  ^18.0.0
import styled from 'styled-components'; //  ^5.3.10
import theme from '../../theme'; // Import theme configuration for styling
import { isRequired } from '../../utils/validation'; // Import validation utility for required field validation

/**
 * Available text field size options
 */
type TextFieldSize = 'small' | 'medium' | 'large';

/**
 * Available input type options
 */
type TextFieldType =
  | 'text'
  | 'password'
  | 'email'
  | 'number'
  | 'tel'
  | 'url'
  | 'date'
  | 'time'
  | 'datetime-local'
  | 'search';

/**
 * Props for the TextField component
 */
interface TextFieldProps {
  id?: string;
  name?: string;
  label?: string;
  value?: string;
  onChange?: (event: ChangeEvent<HTMLInputElement>) => void;
  onBlur?: (event: FocusEvent<HTMLInputElement>) => void;
  type?: TextFieldType;
  placeholder?: string;
  required?: boolean;
  disabled?: boolean;
  readOnly?: boolean;
  error?: string;
  fullWidth?: boolean;
  size?: TextFieldSize;
  className?: string;
  validateOnBlur?: boolean;
  validate?: (value: string) => string | null;
  helpText?: string;
  maxLength?: number;
  minLength?: number;
  pattern?: string;
  autoFocus?: boolean;
  autoComplete?: string;
  'aria-label'?: string;
  'aria-describedby'?: string;
  inputProps?: React.InputHTMLAttributes<HTMLInputElement>;
}

/**
 * A customizable text input component that supports validation and different input types
 */
const TextField: React.FC<TextFieldProps> = ({
  id: propsId,
  name,
  label,
  value: propsValue,
  onChange,
  onBlur,
  type = 'text',
  placeholder,
  required = false,
  disabled = false,
  readOnly = false,
  error: propsError,
  fullWidth = true,
  size = 'medium',
  className,
  validateOnBlur = true,
  validate,
  helpText,
  maxLength,
  minLength,
  pattern,
  autoFocus,
  autoComplete,
  'aria-label': ariaLabel,
  'aria-describedby': ariaDescribedby,
  inputProps,
}) => {
  // Generate a unique ID for the input if not provided
  const id = propsId || `text-field-${Math.random().toString(36).substring(7)}`;

  // Track touched state using React.useState
  const [touched, setTouched] = useState(false);

  // Track error state using React.useState
  const [error, setError] = useState<string | null>(propsError || null);

  // Handle uncontrolled component value using React.useState if value prop is not provided
  const [internalValue, setInternalValue] = useState<string>(propsValue || '');
  const isControlled = propsValue !== undefined;
  const value = isControlled ? propsValue : internalValue;

  // Determine if component has validation (required, validate function, or HTML validation attributes)
  const hasValidation = required || validate || maxLength || minLength || pattern;

  /**
   * Handles the change event for the text input
   * @param {React.ChangeEvent<HTMLInputElement>} event
   * @returns {void} No return value
   */
  const handleInputChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    // Extract value from the event target
    const newValue = event.target.value;

    // Run validation on the new value if hasValidation is true
    if (hasValidation) {
      let validationError: string | null = null;

      if (required && !isRequired(newValue)) {
        validationError = `${label || 'This field'} is required`;
      } else if (validate) {
        validationError = validate(newValue);
      }

      setError(validationError);
    }

    // Call the onChange callback with the new value
    onChange?.(event);

    // Update the internal value state if component is uncontrolled
    if (!isControlled) {
      setInternalValue(newValue);
    }
  };

  /**
   * Handles the blur event for the text input
   * @param {React.FocusEvent<HTMLInputElement>} event
   * @returns {void} No return value
   */
  const handleBlur = (event: React.FocusEvent<HTMLInputElement>) => {
    // Extract value from the event target
    const newValue = event.target.value;

    // Run validation on the value if hasValidation is true and validateOnBlur is true
    if (hasValidation && validateOnBlur) {
      let validationError: string | null = null;

      if (required && !isRequired(newValue)) {
        validationError = `${label || 'This field'} is required`;
      } else if (validate) {
        validationError = validate(newValue);
      }

      setError(validationError);
    }

    // Call the onBlur callback if provided
    onBlur?.(event);

    // Set touched state to true
    setTouched(true);
  };

  // Apply proper ARIA attributes for accessibility
  const ariaInvalid = error && touched ? 'true' : undefined;

  return (
    <TextFieldContainer fullWidth={fullWidth}>
      {label && (
        <TextFieldLabel htmlFor={id} required={required} disabled={disabled}>
          {label}
        </TextFieldLabel>
      )}
      <StyledInput
        id={id}
        name={name}
        type={type}
        placeholder={placeholder}
        value={value}
        onChange={handleInputChange}
        onBlur={handleBlur}
        disabled={disabled}
        readOnly={readOnly}
        hasError={!!error && touched}
        size={size}
        className={className}
        maxLength={maxLength}
        minLength={minLength}
        pattern={pattern}
        autoFocus={autoFocus}
        autoComplete={autoComplete}
        aria-label={ariaLabel}
        aria-describedby={ariaDescribedby}
        aria-invalid={ariaInvalid}
        {...inputProps}
      />
      {error && touched && <ErrorMessage>{error}</ErrorMessage>}
      {helpText && !error && <HelpText>{helpText}</HelpText>}
    </TextFieldContainer>
  );
};

export default TextField;

const TextFieldContainer = styled.div<{ fullWidth?: boolean }>`
  position: relative;
  width: ${(props) => (props.fullWidth ? '100%' : 'auto')};
  margin-bottom: ${(props) => props.theme.spacing(2)}px;
`;

const TextFieldLabel = styled.label<{ required?: boolean; disabled?: boolean }>`
  display: block;
  margin-bottom: ${(props) => props.theme.spacing(1)}px;
  font-weight: 500;
  color: ${(props) => theme.colors.primary.main};
  font-size: 14px;

  ${(props) =>
    props.required &&
    `
    &::after {
      content: '*';
      color: ${theme.colors.error.main};
      margin-left: 4px;
    }
  `}

  ${(props) =>
    props.disabled &&
    `
    opacity: 0.6;
  `}
`;

const StyledInput = styled.input<{
  size?: TextFieldSize;
  hasError?: boolean;
  readOnly?: boolean;
  disabled?: boolean;
}>`
  width: 100%;
  padding: 8px 16px;
  font-size: 16px;
  line-height: 1.5;
  color: ${(props) => theme.colors.text.primary};
  background-color: ${(props) => theme.colors.background.paper};
  border: 1px solid
    ${(props) => (props.hasError ? theme.colors.error.main : '#CBD5E0')};
  border-radius: 4px;
  transition: border-color ${theme.transitions.normal},
    box-shadow ${theme.transitions.normal};

  &:focus {
    outline: none;
    border-color: ${(props) => theme.colors.primary.main};
    box-shadow: 0 0 0 3px rgba(49, 130, 206, 0.25);
  }

  &::placeholder {
    color: ${(props) => theme.colors.text.secondary};
    opacity: 0.7;
  }

  ${(props) =>
    props.size === 'small' &&
    `
    padding: 6px 12px;
    font-size: 14px;
  `}

  ${(props) =>
    props.size === 'medium' &&
    `
    padding: 8px 16px;
    font-size: 16px;
  `}

  ${(props) =>
    props.size === 'large' &&
    `
    padding: 10px 20px;
    font-size: 18px;
  `}

  ${(props) =>
    props.disabled &&
    `
    opacity: 0.6;
    cursor: not-allowed;
    background-color: ${theme.colors.background.light};
  `}

  ${(props) =>
    props.hasError &&
    `
    border-color: ${theme.colors.error.main};
    &:focus {
      box-shadow: 0 0 0 3px rgba(229, 62, 62, 0.25);
    }
  `}

  ${(props) =>
    props.readOnly &&
    `
    background-color: ${theme.colors.background.light};
    cursor: default;
  `}
`;

const ErrorMessage = styled.div`
  color: ${(props) => theme.colors.error.main};
  font-size: 14px;
  margin-top: 4px;
`;

const HelpText = styled.div`
  color: ${(props) => theme.colors.text.secondary};
  font-size: 14px;
  margin-top: 4px;
`;