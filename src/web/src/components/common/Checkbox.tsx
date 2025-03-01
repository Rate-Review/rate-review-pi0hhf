import React, { useRef, useEffect } from 'react';
import styled from 'styled-components';
import theme from '../../theme';

// Interface for Checkbox props
interface CheckboxProps {
  id?: string;
  name?: string;
  label?: string;
  checked?: boolean;
  onChange?: (checked: boolean) => void;
  disabled?: boolean;
  error?: boolean;
  errorMessage?: string;
  helperText?: string;
  indeterminate?: boolean;
  className?: string;
  labelClassName?: string;
}

// Styled components
const CheckboxContainer = styled.div<{ disabled?: boolean }>`
  display: flex;
  align-items: center;
  position: relative;
  cursor: ${props => props.disabled ? 'not-allowed' : 'pointer'};
`;

const HiddenCheckbox = styled.input`
  position: absolute;
  opacity: 0;
  height: 0;
  width: 0;
  pointer-events: none;
`;

const StyledCheckbox = styled.div<{ checked?: boolean; disabled?: boolean; error?: boolean }>`
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 18px;
  height: 18px;
  background-color: ${props => props.checked ? theme.colors.primary.main : 'white'};
  border: 1px solid ${props => 
    props.error ? theme.colors.error.main : 
    props.checked ? theme.colors.primary.main : 
    '#CBD5E0'
  };
  border-radius: 4px;
  transition: all ${theme.transitions.normal};
  opacity: ${props => props.disabled ? 0.6 : 1};
  
  &:hover {
    border-color: ${props => 
      !props.disabled && !props.checked && !props.error ? 
      theme.colors.primary.main : 
      null
    };
  }
  
  &:focus {
    outline: none;
    box-shadow: 0 0 0 2px ${theme.colors.primary.light};
  }
`;

const CheckboxIcon = styled.svg<{ checked?: boolean }>`
  fill: none;
  stroke: white;
  stroke-width: 2px;
  visibility: ${props => props.checked ? 'visible' : 'hidden'};
`;

const IndeterminateIcon = styled.div<{ indeterminate?: boolean }>`
  width: 10px;
  height: 2px;
  background-color: white;
  visibility: ${props => props.indeterminate ? 'visible' : 'hidden'};
`;

const Label = styled.label<{ disabled?: boolean }>`
  margin-left: 8px;
  font-size: 16px;
  color: ${props => props.disabled ? theme.colors.text.disabled : theme.colors.text.primary};
  cursor: ${props => props.disabled ? 'not-allowed' : 'pointer'};
`;

const ErrorText = styled.div`
  color: ${theme.colors.error.main};
  font-size: 14px;
  margin-top: 4px;
  margin-left: 26px;
`;

const HelperText = styled.div`
  color: ${theme.colors.text.secondary};
  font-size: 14px;
  margin-top: 4px;
  margin-left: 26px;
`;

/**
 * A customizable checkbox component that supports various states and accessibility features
 * Implements the Justice Bid design system's checkbox styling and behaviors
 */
const Checkbox: React.FC<CheckboxProps> = ({
  id,
  name,
  label,
  checked = false,
  onChange,
  disabled = false,
  error = false,
  errorMessage,
  helperText,
  indeterminate = false,
  className,
  labelClassName,
}) => {
  const checkboxRef = useRef<HTMLInputElement>(null);
  
  // Set indeterminate property (not controllable via React props)
  useEffect(() => {
    if (checkboxRef.current) {
      checkboxRef.current.indeterminate = indeterminate;
    }
  }, [indeterminate]);
  
  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (!disabled && onChange) {
      onChange(e.target.checked);
    }
  };
  
  const handleContainerClick = () => {
    if (!disabled && checkboxRef.current && onChange) {
      const newChecked = !checked;
      onChange(newChecked);
    }
  };

  return (
    <div>
      <CheckboxContainer 
        onClick={handleContainerClick}
        disabled={disabled}
        className={className}
      >
        <HiddenCheckbox
          ref={checkboxRef}
          type="checkbox"
          id={id}
          name={name}
          checked={checked}
          onChange={handleChange}
          disabled={disabled}
          aria-checked={indeterminate ? 'mixed' : checked}
        />
        <StyledCheckbox 
          checked={checked} 
          disabled={disabled}
          error={error}
          role="presentation"
        >
          {indeterminate ? (
            <IndeterminateIcon indeterminate={indeterminate} />
          ) : (
            <CheckboxIcon checked={checked} viewBox="0 0 24 24">
              <polyline points="20 6 9 17 4 12" />
            </CheckboxIcon>
          )}
        </StyledCheckbox>
        {label && (
          <Label 
            htmlFor={id}
            disabled={disabled}
            className={labelClassName}
          >
            {label}
          </Label>
        )}
      </CheckboxContainer>
      
      {error && errorMessage && (
        <ErrorText>{errorMessage}</ErrorText>
      )}
      
      {!error && helperText && (
        <HelperText>{helperText}</HelperText>
      )}
    </div>
  );
};

export default Checkbox;