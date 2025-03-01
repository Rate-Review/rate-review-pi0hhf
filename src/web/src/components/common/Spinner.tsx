import React from 'react';
import styled, { keyframes } from 'styled-components';
import theme from '../../../theme';

/**
 * Keyframe animation for the spinning effect
 */
const spinAnimation = keyframes`
  0% {
    transform: rotate(0deg);
  }
  100% {
    transform: rotate(360deg);
  }
`;

/**
 * Styled component for the spinner container
 */
const SpinnerContainer = styled.div<{ size: string }>`
  display: inline-block;
  position: relative;
  width: ${props => props.size};
  height: ${props => props.size};
  margin: 0 8px;
`;

/**
 * Styled component for the spinning circle element
 */
const SpinnerCircle = styled.div<{ color: string; thickness: string }>`
  position: absolute;
  width: 100%;
  height: 100%;
  border-style: solid;
  border-width: ${props => props.thickness};
  border-color: ${props => props.color};
  border-top-color: transparent;
  border-radius: 50%;
  animation: ${spinAnimation} 0.8s linear infinite;
`;

/**
 * Interface for Spinner component props
 */
interface SpinnerProps {
  /** Width and height of the spinner */
  size?: string;
  /** Color of the spinner (theme color name or direct CSS color) */
  color?: string;
  /** Border thickness of the spinner */
  thickness?: string;
  /** Optional class name for additional styling */
  className?: string;
  /** Accessibility label for screen readers */
  ariaLabel?: string;
}

/**
 * Spinner component that provides visual feedback during loading states
 * 
 * Used for indicating loading states during asynchronous operations like
 * data fetching, form submissions, and processing tasks.
 * 
 * @example
 * // Basic usage
 * <Spinner />
 * 
 * @example
 * // Custom size, color and thickness
 * <Spinner size="32px" color="secondary" thickness="3px" />
 * 
 * @example
 * // Custom CSS color
 * <Spinner color="#DD6B20" />
 */
const Spinner: React.FC<SpinnerProps> = ({
  size = '24px',
  color = 'primary',
  thickness = '2px',
  className = '',
  ariaLabel = 'Loading'
}) => {
  // Get the actual color from theme if it's a theme color name
  let themeColor = color;
  
  if (theme.colors && color in theme.colors) {
    if (typeof theme.colors[color] === 'object' && 'main' in theme.colors[color]) {
      themeColor = theme.colors[color].main;
    } else {
      themeColor = theme.colors[color];
    }
  }

  return (
    <SpinnerContainer 
      size={size} 
      className={className} 
      role="status" 
      aria-label={ariaLabel}
    >
      <SpinnerCircle color={themeColor} thickness={thickness} />
    </SpinnerContainer>
  );
};

export default Spinner;