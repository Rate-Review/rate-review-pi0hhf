/**
 * Skeleton Component
 * 
 * A flexible loading placeholder component that displays animated skeletons
 * to indicate content loading states throughout the Justice Bid application.
 * 
 * Implements design principles:
 * - Modern & Professional UI with consistent loading states
 * - Responsive Design with adaptable sizing
 * - Subtle animations for loading state feedback
 */

import React from 'react';
import styled, { keyframes } from 'styled-components'; // styled-components v5.3.10
import theme from '../../theme'; // Import theme configuration for consistent styling

// Define skeleton variant types
type SkeletonVariant = 'rectangle' | 'circle' | 'text';

// Props interface for the Skeleton component
interface SkeletonProps {
  width?: string;
  height?: string;
  variant?: SkeletonVariant;
  animation?: boolean;
  borderRadius?: string;
  className?: string;
  margin?: string;
}

// Keyframes for the skeleton pulse animation
const pulse = keyframes`
  0% {
    opacity: 0.6;
  }
  50% {
    opacity: 0.8;
  }
  100% {
    opacity: 0.6;
  }
`;

// Shimmer effect animation
const shimmer = keyframes`
  0% {
    transform: translateX(-100%);
  }
  100% {
    transform: translateX(100%);
  }
`;

// Styled component for the skeleton
const StyledSkeleton = styled.div<SkeletonProps & { theme: any }>`
  position: relative;
  overflow: hidden;
  background-color: ${props => props.theme.colors.background.paper};
  opacity: 0.7;
  width: ${props => props.width || '100%'};
  height: ${props => props.height || (props.variant === 'text' ? '1rem' : props.variant === 'circle' ? '2.5rem' : '1.25rem')};
  margin: ${props => props.margin || '0'};
  border-radius: ${props => props.borderRadius || (props.variant === 'circle' ? '50%' : '4px')};
  animation: ${props => props.animation !== false ? `${pulse} 1.5s ease-in-out infinite` : 'none'};

  &::after {
    content: '';
    position: absolute;
    top: 0;
    right: 0;
    bottom: 0;
    left: 0;
    transform: translateX(-100%);
    background-image: linear-gradient(
      90deg,
      rgba(255, 255, 255, 0) 0,
      rgba(255, 255, 255, 0.2) 20%,
      rgba(255, 255, 255, 0.5) 60%,
      rgba(255, 255, 255, 0)
    );
    animation: ${shimmer} 2s infinite;
  }
`;

/**
 * A component that displays animated skeletons to indicate content loading states.
 * 
 * @param props - Component props
 * @returns The skeleton component with styling based on provided props
 */
const Skeleton: React.FC<SkeletonProps> = ({
  width,
  height,
  variant = 'rectangle',
  animation = true,
  borderRadius,
  className,
  margin,
  ...rest
}) => {
  return (
    <StyledSkeleton
      width={width}
      height={height}
      variant={variant}
      animation={animation}
      borderRadius={borderRadius}
      className={className}
      margin={margin}
      {...rest}
    />
  );
};

export default Skeleton;