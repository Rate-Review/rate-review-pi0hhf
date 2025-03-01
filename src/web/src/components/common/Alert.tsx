import React from 'react';
import Paper from '@mui/material/Paper';
import Typography from '@mui/material/Typography';
import IconButton from '@mui/material/IconButton';
import Box from '@mui/material/Box';
import CheckCircleOutlined from '@mui/icons-material/CheckCircleOutlined';
import ErrorOutlined from '@mui/icons-material/ErrorOutlined';
import WarningAmberOutlined from '@mui/icons-material/WarningAmberOutlined';
import InfoOutlined from '@mui/icons-material/InfoOutlined';
import CloseRounded from '@mui/icons-material/CloseRounded';
import { useTheme } from '../../context/ThemeContext';

// Define the props interface for the Alert component
interface AlertProps {
  severity?: "success" | "error" | "warning" | "info";
  title?: string;
  message: string;
  onClose?: () => void;
  action?: React.ReactNode;
  variant?: "standard" | "outlined" | "filled";
  elevation?: number;
  className?: string;
  fullWidth?: boolean;
}

/**
 * Alert component that displays important messages, warnings, errors, or success notifications to users.
 * Unlike Toast components which show temporary notifications, this Alert component remains visible until explicitly dismissed or handled programmatically.
 */
const Alert: React.FC<AlertProps> = ({
  severity = 'info',
  title,
  message,
  onClose,
  action,
  variant = 'outlined',
  elevation = 1,
  className,
  fullWidth = false,
}) => {
  const { theme } = useTheme();
  
  // Handle close button click
  const handleClose = (event: React.MouseEvent<HTMLButtonElement>) => {
    if (onClose) {
      onClose();
    }
  };

  // Get the appropriate icon based on severity
  const getAlertIcon = (severity: string): React.ReactNode => {
    switch (severity) {
      case 'success':
        return <CheckCircleOutlined />;
      case 'error':
        return <ErrorOutlined />;
      case 'warning':
        return <WarningAmberOutlined />;
      default: // 'info' or default
        return <InfoOutlined />;
    }
  };

  // Helper function to get the appropriate color based on severity
  const getSeverityColor = (severity: string): string => {
    switch (severity) {
      case 'success':
        return theme.palette.success.main;
      case 'error':
        return theme.palette.error.main;
      case 'warning':
        return theme.palette.warning.main;
      default: // 'info' or default
        return theme.palette.info.main;
    }
  };

  // Helper function to get the appropriate light color based on severity for filled variant
  const getSeverityLightColor = (severity: string): string => {
    switch (severity) {
      case 'success':
        return theme.palette.success.light;
      case 'error':
        return theme.palette.error.light;
      case 'warning':
        return theme.palette.warning.light;
      default: // 'info' or default
        return theme.palette.info.light;
    }
  };

  return (
    <Paper
      elevation={elevation}
      variant={variant}
      className={className}
      sx={{
        display: 'flex',
        width: fullWidth ? '100%' : 'auto',
        borderRadius: theme.shape.borderRadius,
        borderLeft: variant === 'outlined' ? `4px solid ${getSeverityColor(severity)}` : 'none',
        backgroundColor: variant === 'filled' ? getSeverityLightColor(severity) : theme.palette.background.paper,
        overflow: 'hidden',
        transition: 'all 250ms ease-in-out',
      }}
      role="alert"
      aria-live="polite"
    >
      <Box display="flex" alignItems="center" px={2} py={1.5}>
        <Box display="flex" sx={{ color: getSeverityColor(severity) }}>
          {getAlertIcon(severity)}
        </Box>
        <Box flex="1" ml={1.5}>
          {title ? (
            <>
              <Typography variant="subtitle1" fontWeight="medium" component="div">
                {title}
              </Typography>
              <Typography variant="body2" color="text.secondary" component="div">
                {message}
              </Typography>
            </>
          ) : (
            <Typography variant="body1" component="div">
              {message}
            </Typography>
          )}
        </Box>
        <Box ml={1} display="flex">
          {action}
          {onClose && (
            <IconButton size="small" aria-label="close" onClick={handleClose}>
              <CloseRounded fontSize="small" />
            </IconButton>
          )}
        </Box>
      </Box>
    </Paper>
  );
};

export default Alert;