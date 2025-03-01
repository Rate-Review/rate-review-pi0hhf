import React from 'react';
import { Typography, Box, SvgIcon } from '@mui/material';
import Button from './Button';

/**
 * Interface defining the properties for EmptyState component
 */
interface EmptyStateProps {
  /**
   * The main heading to display
   */
  title: string;
  
  /**
   * Icon element to display above the title
   */
  icon: React.ReactNode;
  
  /**
   * Optional additional description text
   */
  message?: string;
  
  /**
   * Optional text for the action button
   */
  actionText?: string;
  
  /**
   * Optional callback function for when the action button is clicked
   */
  onAction?: () => void;
  
  /**
   * Optional sx prop for additional styling
   */
  sx?: object;
}

/**
 * Renders an empty state component with optional title, message, icon, and action button.
 * Provides a consistent way to communicate to users that a container or section is empty.
 */
const EmptyState: React.FC<EmptyStateProps> = ({
  icon,
  title,
  message,
  actionText,
  onAction,
  sx = {},
}) => {
  return (
    <Box
      sx={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        textAlign: 'center',
        padding: 3,
        minHeight: '200px',
        ...sx,
      }}
    >
      {icon && (
        <Box sx={{ mb: 2, color: 'text.secondary', fontSize: '3rem' }}>
          {icon}
        </Box>
      )}
      
      <Typography variant="h6" component="h2" gutterBottom>
        {title}
      </Typography>
      
      {message && (
        <Typography variant="body2" color="text.secondary" sx={{ mb: 3, maxWidth: '80%' }}>
          {message}
        </Typography>
      )}
      
      {actionText && onAction && (
        <Button 
          variant="primary" 
          onClick={onAction}
          size="medium"
        >
          {actionText}
        </Button>
      )}
    </Box>
  );
};

export default EmptyState;