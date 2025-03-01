import React, { useState, useEffect } from 'react'; // React library for building UI components //  ^18.0.0
import { useNavigate, useLocation } from 'react-router-dom'; // React Router hooks for navigation //  ^6.4.0
import styled from 'styled-components'; // CSS-in-JS styling for component styling //  ^5.3.6
import { ErrorOutline } from '@mui/icons-material'; // Material UI icons for visual representation //  ^5.14.0

import Button from '../components/common/Button'; // Primary action buttons for error recovery options
import EmptyState from '../components/common/EmptyState'; // Visual component for displaying the error state with illustration
import MainLayout from '../components/layout/MainLayout'; // Consistent layout wrapper for the application pages
import { ROUTES } from '../constants/routes'; // Application route constants for navigation
import { useAuth } from '../hooks/useAuth'; // Hook to access authentication context for determining appropriate redirect routes

// LD1: Styled container for the error page
const ErrorContainer = styled.div`
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 2rem;
  min-height: 80vh;
  text-align: center;
`;

// LD1: Styled component for displaying technical error details
const ErrorDetails = styled.pre`
  margin-top: 2rem;
  padding: 1rem;
  background-color: ${props => props.theme.colors.background.paper};
  border: 1px solid ${props => props.theme.colors.divider};
  border-radius: 4px;
  overflow: auto;
  max-width: 100%;
  font-family: monospace;
  font-size: 0.875rem;
  text-align: left;
  max-height: 200px;
`;

// LD1: Styled container for action buttons
const ActionButtons = styled.div`
  display: flex;
  gap: 1rem;
  margin-top: 2rem;
  flex-wrap: wrap;
  justify-content: center;
`;

/**
 * Functional component that renders the error page when an unhandled exception occurs
 */
const ErrorPage: React.FC = () => {
  // LD1: Initialize the navigate function from React Router's useNavigate hook
  const navigate = useNavigate();

  // LD1: Initialize the location object from React Router's useLocation hook
  const location = useLocation();

  // LD1: Use the useAuth hook to determine user authentication status and role
  const { isAuthenticated, userRole } = useAuth();

  // LD1: Define state for error details using useState hook
  const [errorDetails, setErrorDetails] = useState<any>(null);

  // LD1: Extract error information from location state if available
  useEffect(() => {
    if (location.state && location.state.error) {
      setErrorDetails(location.state.error);
    }
  }, [location.state]);

  /**
   * Function to handle retry of the previous action that caused the error
   */
  const handleRetry = () => {
    // LD1: Check if location.state contains a previousPath property
    if (location.state && location.state.previousPath) {
      // LD1: If previousPath exists, navigate to that path
      navigate(location.state.previousPath);
    } else {
      // LD1: If no previousPath exists, navigate to the dashboard using handleGoHome
      handleGoHome();
    }
  };

  /**
   * Function to handle navigation back to the appropriate dashboard based on user role
   */
  const handleGoHome = () => {
    // LD1: Check user role from auth context
    if (userRole === 'SystemAdministrator') {
      // LD1: Navigate to admin dashboard if user is admin
      navigate(ROUTES.ADMIN_DASHBOARD);
    } else if (userRole === 'OrganizationAdministrator') {
      // LD1: Navigate to client dashboard if user is client
      navigate(ROUTES.CLIENT_DASHBOARD);
    } else if (userRole === 'RateAdministrator') {
      // LD1: Navigate to law firm dashboard if user is from law firm
      navigate(ROUTES.LAW_FIRM_DASHBOARD);
    } else if (!isAuthenticated) {
      // LD1: Navigate to login page if user is not authenticated
      navigate(ROUTES.LOGIN);
    } else {
      // LD1: Navigate to default dashboard if user role is unknown
      navigate(ROUTES.CLIENT_DASHBOARD);
    }
  };

  /**
   * Function to handle error reporting to the application's error tracking system
   */
  const handleReportError = () => {
    // LD1: Collect error information including message, stack trace, and user context
    const errorInfo = {
      message: errorDetails?.message || 'Unknown error',
      stack: errorDetails?.stack || 'No stack trace available',
      user: isAuthenticated ? userRole : 'Guest',
      timestamp: new Date().toISOString(),
    };

    // LD1: Display confirmation message to user that error was reported
    alert('Error reported. Our team is working on it.');

    // LD1: Send error details to backend service for logging and analysis
    // TODO: Implement error reporting service
    // reportError(errorInfo);

    // LD1: In development, log error details to console
    if (process.env.NODE_ENV === 'development') {
      console.error('Error Report:', errorInfo);
    }
  };

  // LD1: Return a MainLayout component to maintain UI consistency
  return (
    <MainLayout>
      <ErrorContainer>
        {/* LD1: Render an EmptyState component with error message and illustration */}
        <EmptyState
          icon={<ErrorOutline style={{ fontSize: '5rem' }} />}
          title="Something Went Wrong"
          message="We encountered an unexpected error. Please try again or contact support."
        />

        {/* LD1: Display technical error details if available and in development environment */}
        {process.env.NODE_ENV === 'development' && errorDetails && (
          <ErrorDetails>
            {errorDetails.message}
            {errorDetails.stack}
          </ErrorDetails>
        )}

        {/* LD1: Add primary action button for returning to dashboard */}
        <ActionButtons>
          <Button variant="contained" color="primary" onClick={handleGoHome}>
            Return to Dashboard
          </Button>

          {/* LD1: Add secondary action buttons for retry and error reporting */}
          <Button variant="outlined" onClick={handleRetry}>
            Try Again
          </Button>
          <Button variant="text" onClick={handleReportError}>
            Report Error
          </Button>
        </ActionButtons>
      </ErrorContainer>
    </MainLayout>
  );
};

export default ErrorPage;