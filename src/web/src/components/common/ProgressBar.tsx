/**
 * A reusable progress bar component that visualizes completion percentage 
 * or loading state for operations like file imports/exports, data processing,
 * and integration tasks throughout the Justice Bid application.
 * 
 * @version 1.0.0
 */

import React from 'react';
import { Box, LinearProgress, Typography, styled } from '@mui/material'; // ^5.14.0
import { colors } from '../../../theme';

/**
 * Props for the ProgressBar component
 */
interface ProgressBarProps {
  /**
   * Current progress value (0-100)
   */
  value: number;
  /**
   * Optional label to display above the progress bar
   */
  label?: string;
  /**
   * Progress bar variant - determinate shows specific progress, indeterminate shows animation
   * @default 'determinate'
   */
  variant?: 'determinate' | 'indeterminate';
  /**
   * Whether to display the percentage text
   * @default true
   */
  showPercentage?: boolean;
  /**
   * Size of the progress bar
   * @default 'medium'
   */
  size?: 'small' | 'medium' | 'large';
  /**
   * Optional custom color (defaults to theme primary color)
   */
  color?: string;
  /**
   * Optional CSS styles
   */
  style?: React.CSSProperties;
  /**
   * Optional CSS class
   */
  className?: string;
}

// Styled component for the progress bar with customizable height and color
const StyledLinearProgress = styled(LinearProgress, {
  shouldForwardProp: (prop) => prop !== 'barHeight' && prop !== 'barColor',
})<{ barHeight: number; barColor?: string }>(({ theme, barHeight, barColor }) => ({
  height: barHeight,
  borderRadius: barHeight / 2,
  backgroundColor: theme.palette.mode === 'light' 
    ? theme.palette.grey[200] 
    : theme.palette.grey[700],
  '& .MuiLinearProgress-bar': {
    borderRadius: barHeight / 2,
    backgroundColor: barColor || colors.primary.main,
  },
}));

/**
 * A customizable progress bar component that visualizes operation progress 
 * with optional label and percentage display.
 * 
 * Used in file imports/exports, data processing, and integration tasks throughout
 * the Justice Bid application.
 */
const ProgressBar: React.FC<ProgressBarProps> = ({
  value,
  label,
  variant = 'determinate',
  showPercentage = true,
  size = 'medium',
  color,
  style,
  className,
}) => {
  // Calculate height based on size prop
  const getHeight = (): number => {
    switch (size) {
      case 'small':
        return 4;
      case 'large':
        return 12;
      case 'medium':
      default:
        return 8;
    }
  };

  const barHeight = getHeight();
  
  // Clamp value between 0 and 100 for safety
  const clampedValue = Math.min(Math.max(0, value), 100);

  return (
    <Box sx={{ width: '100%', mt: 2, mb: 2 }} style={style} className={className}>
      {/* Display label if provided */}
      {label && (
        <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
          <Typography variant="body2" color="text.secondary">
            {label}
          </Typography>
          {/* Show percentage next to label if requested and determinate */}
          {showPercentage && variant === 'determinate' && (
            <Typography 
              variant="body2" 
              color="text.secondary" 
              sx={{ ml: 'auto' }}
              aria-live="polite"
            >
              {`${Math.round(clampedValue)}%`}
            </Typography>
          )}
        </Box>
      )}

      {/* Progress bar with proper ARIA attributes for accessibility */}
      <StyledLinearProgress
        variant={variant}
        value={clampedValue}
        barHeight={barHeight}
        barColor={color}
        aria-label={label || "Progress indicator"}
        aria-valuenow={variant === 'determinate' ? clampedValue : undefined}
        aria-valuemin={0}
        aria-valuemax={100}
      />

      {/* Show percentage below if requested and no label is provided */}
      {showPercentage && variant === 'determinate' && !label && (
        <Box sx={{ display: 'flex', justifyContent: 'flex-end', mt: 0.5 }}>
          <Typography 
            variant="body2" 
            color="text.secondary"
            aria-live="polite"
          >
            {`${Math.round(clampedValue)}%`}
          </Typography>
        </Box>
      )}
    </Box>
  );
};

export default ProgressBar;