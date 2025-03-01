import React from 'react';
import { Radio, FormControlLabel, FormControl, FormHelperText } from '@mui/material';
import { styled, useTheme } from '@mui/material/styles';

interface RadioButtonProps {
  id?: string;
  name?: string;
  value?: string | number;
  checked?: boolean;
  onChange?: (event: React.ChangeEvent<HTMLInputElement>) => void;
  label?: string;
  disabled?: boolean;
  error?: boolean;
  helperText?: string;
  required?: boolean;
  className?: string;
}

// Styled FormControlLabel for custom appearance
const StyledFormControlLabel = styled(FormControlLabel)(({ theme, disabled }) => ({
  marginLeft: -11,
  marginRight: 16,
  '& .MuiFormControlLabel-label': {
    fontSize: theme.typography.body1.fontSize,
    fontFamily: theme.typography.fontFamily,
    fontWeight: theme.typography.fontWeightRegular,
    color: disabled 
      ? theme.palette.text.disabled 
      : theme.palette.text.primary,
  },
  '& .MuiRadio-root': {
    padding: theme.spacing(1),
    color: disabled 
      ? theme.palette.action.disabled 
      : theme.palette.primary.main,
    '&.Mui-checked': {
      color: disabled 
        ? theme.palette.action.disabled 
        : theme.palette.primary.main,
    },
    '&:hover': {
      backgroundColor: disabled
        ? 'transparent'
        : theme.palette.action.hover,
    },
  },
}));

// Styled FormHelperText for error messages and hints
const StyledFormHelperText = styled(FormHelperText)(({ theme, error }) => ({
  marginLeft: theme.spacing(1),
  marginTop: 0,
  fontSize: theme.typography.caption.fontSize,
  color: error 
    ? theme.palette.error.main 
    : theme.palette.text.secondary,
}));

/**
 * RadioButton component that provides a styled radio input with label.
 * Follows the design system's styling guidelines and provides standard radio button functionality.
 */
const RadioButton: React.FC<RadioButtonProps> = ({
  id,
  name,
  value,
  checked,
  onChange,
  label,
  disabled = false,
  error = false,
  helperText,
  required = false,
  className,
}) => {
  const theme = useTheme();

  // Generate ID if not provided for accessibility
  const radioId = id || `radio-${name}-${value}`;

  return (
    <FormControl error={error} className={className} component="fieldset">
      <StyledFormControlLabel
        disabled={disabled}
        control={
          <Radio
            id={radioId}
            name={name}
            value={value}
            checked={checked}
            onChange={onChange}
            disabled={disabled}
            required={required}
            color="primary"
            size="medium"
            inputProps={{
              'aria-describedby': helperText ? `${radioId}-helper-text` : undefined,
            }}
          />
        }
        label={required && label ? `${label} *` : label}
      />
      {helperText && (
        <StyledFormHelperText 
          id={`${radioId}-helper-text`}
          error={error}
        >
          {helperText}
        </StyledFormHelperText>
      )}
    </FormControl>
  );
};

export default RadioButton;