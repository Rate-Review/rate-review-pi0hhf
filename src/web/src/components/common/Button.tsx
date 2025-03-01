import React from 'react';
import styled from 'styled-components';
import theme from '../../theme';

// Define types for button variants, sizes, colors, and HTML button types
type ButtonVariant = 'primary' | 'secondary' | 'outline' | 'text';
type ButtonSize = 'small' | 'medium' | 'large';
type ButtonColor = 'primary' | 'secondary' | 'success' | 'warning' | 'error' | 'info';
type ButtonType = 'button' | 'submit' | 'reset';

/**
 * Props for the Button component
 */
interface ButtonProps {
  children: React.ReactNode;
  onClick?: (event: React.MouseEvent<HTMLButtonElement>) => void;
  variant?: ButtonVariant;
  size?: ButtonSize;
  color?: ButtonColor;
  disabled?: boolean;
  fullWidth?: boolean;
  type?: ButtonType;
  className?: string;
  'aria-label'?: string;
  aria?: Record<string, string>;
}

/**
 * Styled button component with different variants, sizes, and states
 * Implements the Justice Bid design system's button styles
 */
const StyledButton = styled.button<ButtonProps>`
  display: inline-flex;
  align-items: center;
  justify-content: center;
  font-weight: ${props => props.theme.typography.fontWeight.medium};
  border-radius: ${props => props.theme.spacing.sm};
  cursor: pointer;
  transition: all ${props => props.theme.transitions.normal};
  outline: none;
  border: none;
  position: relative;
  overflow: hidden;
  font-family: ${props => props.theme.typography.fontFamily.primary};
  text-transform: none;
  letter-spacing: 0.5px;
  line-height: 1.75;
  white-space: nowrap;

  /* Variant styles */
  ${props => {
    switch (props.variant) {
      case 'primary':
        return `
          background-color: ${props.theme.colors[props.color || 'primary'].main};
          color: ${props.theme.colors[props.color || 'primary'].contrastText};
          
          &:hover {
            background-color: ${props.theme.colors[props.color || 'primary'].dark};
          }
          
          &:focus {
            box-shadow: 0 0 0 2px ${props.theme.colors[props.color || 'primary'].light};
          }
        `;
      case 'secondary':
        return `
          background-color: ${props.theme.colors[props.color || 'secondary'].main};
          color: ${props.theme.colors[props.color || 'secondary'].contrastText};
          
          &:hover {
            background-color: ${props.theme.colors[props.color || 'secondary'].dark};
          }
          
          &:focus {
            box-shadow: 0 0 0 2px ${props.theme.colors[props.color || 'secondary'].light};
          }
        `;
      case 'outline':
        return `
          background-color: transparent;
          color: ${props.theme.colors[props.color || 'primary'].main};
          border: 1px solid ${props.theme.colors[props.color || 'primary'].main};
          
          &:hover {
            background-color: ${props.theme.colors[props.color || 'primary'].light};
            opacity: 0.1;
          }
          
          &:focus {
            box-shadow: 0 0 0 2px ${props.theme.colors[props.color || 'primary'].light};
          }
        `;
      case 'text':
        return `
          background-color: transparent;
          color: ${props.theme.colors[props.color || 'primary'].main};
          padding-left: ${props.theme.spacing(1)};
          padding-right: ${props.theme.spacing(1)};
          
          &:hover {
            background-color: ${props.theme.colors[props.color || 'primary'].light};
            opacity: 0.1;
          }
          
          &:focus {
            box-shadow: 0 0 0 2px ${props.theme.colors[props.color || 'primary'].light};
          }
        `;
      default:
        return '';
    }
  }}

  /* Size styles */
  ${props => {
    switch (props.size) {
      case 'small':
        return `
          padding: ${props.theme.spacing(0.5)} ${props.theme.spacing(2)};
          font-size: ${props.theme.typography.fontSize.sm};
        `;
      case 'large':
        return `
          padding: ${props.theme.spacing(1.5)} ${props.theme.spacing(4)};
          font-size: ${props.theme.typography.fontSize.lg};
        `;
      default: // medium
        return `
          padding: ${props.theme.spacing(1)} ${props.theme.spacing(3)};
          font-size: ${props.theme.typography.fontSize.md};
        `;
    }
  }}

  /* Full width style */
  ${props =>
    props.fullWidth &&
    `
      width: 100%;
    `}

  /* Disabled state */
  ${props =>
    props.disabled &&
    `
      opacity: 0.6;
      cursor: not-allowed;
      pointer-events: none;
    `}

  /* Focus styles for keyboard navigation accessibility */
  &:focus-visible {
    outline: 2px solid ${props => props.theme.colors.primary.light};
    outline-offset: 2px;
  }
  
  /* Animation for button press effect */
  &:active {
    transform: translateY(1px);
  }
`;

/**
 * A customizable button component that supports various styling options and states
 * while ensuring proper accessibility features.
 */
const Button: React.FC<ButtonProps> = ({
  children,
  onClick,
  variant = 'primary',
  size = 'medium',
  color = 'primary',
  disabled = false,
  fullWidth = false,
  type = 'button',
  className = '',
  'aria-label': ariaLabel,
  aria = {},
  ...rest
}) => {
  return (
    <StyledButton
      onClick={onClick}
      variant={variant}
      size={size}
      color={color}
      disabled={disabled}
      fullWidth={fullWidth}
      type={type}
      className={className}
      aria-label={ariaLabel}
      aria-disabled={disabled}
      {...aria}
      {...rest}
    >
      {children}
    </StyledButton>
  );
};

export default Button;