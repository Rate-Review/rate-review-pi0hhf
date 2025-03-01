import React from 'react';
import { styled } from '@mui/material/styles';
import { Badge as MuiBadge } from '@mui/material';
import { primary, secondary, success, warning, error, info, neutral } from '../../../theme/colors';

interface BadgeProps {
  /**
   * The content to display inside the badge
   */
  content?: React.ReactNode;
  
  /**
   * The visual style variant of the badge
   * @default 'primary'
   */
  variant?: 'primary' | 'secondary' | 'success' | 'warning' | 'error' | 'info' | 'neutral';
  
  /**
   * The size of the badge
   * @default 'medium'
   */
  size?: 'small' | 'medium' | 'large';
  
  /**
   * Numeric value to display inside the badge
   */
  count?: number;
  
  /**
   * Whether to display the badge as a small dot indicator
   * @default false
   */
  dot?: boolean;
  
  /**
   * Additional class name to apply to the badge
   */
  className?: string;
  
  /**
   * Optional children to wrap with the badge
   */
  children?: React.ReactNode;
}

/**
 * StyledBadge - A styled version of Material UI's Badge component
 * with custom styling for different variants and sizes
 */
const StyledBadge = styled(MuiBadge)(({ theme, color, size }: any) => {
  // Get the theme's spacing function for consistent spacing
  const spacing = theme.spacing;
  
  // Base styles for all badge variants
  const baseStyles = {
    display: 'inline-flex',
    alignItems: 'center',
    justifyContent: 'center',
    fontWeight: 500,
    borderRadius: '16px',
    textTransform: 'none',
    letterSpacing: '0.02em',
    whiteSpace: 'nowrap',
    transition: 'all 250ms ease-in-out',
  };
  
  // Size-specific styles
  const sizeStyles = {
    small: {
      fontSize: '0.75rem',
      height: spacing(2),
      minWidth: spacing(2),
      padding: `0 ${spacing(0.75)}`,
    },
    medium: {
      fontSize: '0.875rem',
      height: spacing(2.5),
      minWidth: spacing(2.5),
      padding: `0 ${spacing(1)}`,
    },
    large: {
      fontSize: '1rem',
      height: spacing(3),
      minWidth: spacing(3),
      padding: `0 ${spacing(1.5)}`,
    },
  };
  
  // Color-specific styles
  const getColorStyles = (colorValue: any) => ({
    backgroundColor: colorValue.main,
    color: colorValue.contrastText,
    '&:hover': {
      backgroundColor: colorValue.dark,
    },
  });
  
  // Get the appropriate color based on the variant
  const getColorByVariant = () => {
    switch (color) {
      case 'primary':
        return getColorStyles(primary);
      case 'secondary':
        return getColorStyles(secondary);
      case 'success':
        return getColorStyles(success);
      case 'warning':
        return getColorStyles(warning);
      case 'error':
        return getColorStyles(error);
      case 'info':
        return getColorStyles(info);
      case 'neutral':
        return getColorStyles(neutral);
      default:
        return getColorStyles(primary);
    }
  };
  
  // Get the appropriate size styles
  const getSizeStyles = () => {
    switch (size) {
      case 'small':
        return sizeStyles.small;
      case 'large':
        return sizeStyles.large;
      case 'medium':
      default:
        return sizeStyles.medium;
    }
  };
  
  // Combine all styles
  return {
    ...baseStyles,
    ...getSizeStyles(),
    ...getColorByVariant(),
    
    // Dot specific styling
    '& .MuiBadge-dot': {
      minWidth: spacing(1),
      height: spacing(1),
      borderRadius: '50%',
    },
    
    // Make sure the badge is properly positioned when used as a wrapper
    '& .MuiBadge-badge': {
      position: 'relative',
      transform: 'none',
    },
    
    // Responsive adjustments
    [theme.breakpoints.down('sm')]: {
      fontSize: size === 'large' ? '0.875rem' : size === 'medium' ? '0.75rem' : '0.65rem',
      padding: `0 ${spacing(size === 'large' ? 1 : size === 'medium' ? 0.75 : 0.5)}`,
    },
  };
});

/**
 * Badge component for displaying status indicators, counts, or short informational text
 * 
 * @example
 * // Status badge
 * <Badge variant="success" content="Active" />
 * 
 * @example
 * // Count badge
 * <Badge variant="primary" count={5} />
 * 
 * @example
 * // Dot indicator
 * <Badge variant="error" dot />
 */
const Badge: React.FC<BadgeProps> = ({ 
  content, 
  variant = 'primary', 
  size = 'medium', 
  count, 
  dot = false, 
  className,
  children,
  ...rest 
}) => {
  // Determine what to display inside the badge
  const badgeContent = () => {
    if (dot) {
      return <span className="MuiBadge-dot" aria-hidden="true" />;
    }
    
    if (count !== undefined) {
      return count;
    }
    
    return content;
  };
  
  // If children are provided, badge wraps them, otherwise it's standalone
  if (children) {
    return (
      <StyledBadge
        badgeContent={badgeContent()}
        color={variant}
        size={size}
        className={className}
        {...rest}
      >
        {children}
      </StyledBadge>
    );
  }
  
  // Standalone badge
  return (
    <StyledBadge
      component="span"
      className={className}
      color={variant}
      size={size}
      {...rest}
    >
      {badgeContent()}
    </StyledBadge>
  );
};

export default Badge;