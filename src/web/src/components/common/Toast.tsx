import React from 'react';
import { Alert, Snackbar } from '@mui/material';
import { styled, keyframes } from '@mui/material/styles';
import { useTheme } from '../../context/ThemeContext';
import { ToastDuration as TOAST_DURATION, ToastPosition as TOAST_POSITIONS } from '../../constants/toast';

// Define fade-in animation
const fadeIn = keyframes`
  from {
    opacity: 0;
    transform: translateY(-20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
`;

// Styled Alert component with animation
const StyledAlert = styled(Alert)(({ theme }) => ({
  borderRadius: theme.borderRadius.md,
  boxShadow: theme.shadows.md,
  width: '100%',
  maxWidth: '400px',
  fontWeight: theme.fontWeights.medium,
  animation: `${fadeIn} ${theme.transitions.normal}`
}));

/**
 * Interface for Toast component props
 */
export interface ToastProps {
  open: boolean;
  message: string;
  severity?: 'success' | 'error' | 'warning' | 'info';
  duration?: number;
  position?: {
    vertical: 'top' | 'bottom';
    horizontal: 'left' | 'center' | 'right';
  };
  onClose: () => void;
  action?: React.ReactNode;
}

/**
 * A toast notification component that displays messages with different severity levels
 * and supports customizable duration, position, and actions
 */
const Toast: React.FC<ToastProps> = ({
  open,
  message,
  severity = 'info',
  duration = TOAST_DURATION.MEDIUM,
  position = { vertical: 'top', horizontal: 'right' },
  onClose,
  action
}) => {
  const { theme } = useTheme();

  /**
   * Handles the closing of the toast notification
   * Ignores 'clickaway' events to prevent accidental dismissal
   * when clicking elsewhere on the screen
   */
  const handleClose = (event: React.SyntheticEvent | Event, reason?: string) => {
    if (reason === 'clickaway') {
      return;
    }
    onClose();
  };

  return (
    <Snackbar
      open={open}
      autoHideDuration={duration}
      onClose={handleClose}
      anchorOrigin={position}
    >
      <StyledAlert
        severity={severity}
        onClose={handleClose}
        variant="filled"
        elevation={6}
        action={action}
      >
        {message}
      </StyledAlert>
    </Snackbar>
  );
};

export default Toast;