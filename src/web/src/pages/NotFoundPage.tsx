import React from 'react'; // Core React library //  ^18.0.0
import styled from 'styled-components'; // CSS-in-JS styling library //  ^5.3.6
import { Link, useNavigate } from 'react-router-dom'; // React Router library for navigation //  ^6.4.0
import MainLayout from '../components/layout/MainLayout'; // Layout wrapper for consistent page structure
import Button from '../components/common/Button'; // UI button component for navigation actions
import { ROUTES } from '../constants/routes'; // Application route constants for navigation
import { useAuth } from '../hooks/useAuth'; // Hook to access authentication context for determining appropriate redirect routes

// LD1: Styled container for the 404 page content
const NotFoundContainer = styled.div`
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 2rem;
  min-height: 80vh;
  text-align: center;
`;

// LD1: Styled component for the error code
const ErrorCode = styled.div`
  font-size: 6rem;
  font-weight: 700;
  color: ${props => props.theme.colors.error.main};
  margin-bottom: 1rem;
`;

// LD1: Styled component for the error title
const ErrorTitle = styled.h1`
  font-size: 2rem;
  font-weight: 500;
  margin-bottom: 1rem;
`;

// LD1: Styled component for the error message
const ErrorMessage = styled.p`
  font-size: 1.1rem;
  color: ${props => props.theme.colors.text.secondary};
  margin-bottom: 2rem;
  max-width: 600px;
`;

// LD1: Styled component for the action buttons container
const ActionButtons = styled.div`
  display: flex;
  gap: 1rem;
  flex-wrap: wrap;
  justify-content: center;
`;

/**
 * A React functional component that renders a 404 not found page
 */
const NotFoundPage: React.FC = () => {
  // Get the navigate function from React Router's useNavigate hook
  const navigate = useNavigate();

  // Get user authentication status and role using the useAuth hook
  const { isAuthenticated, userRole } = useAuth();

  /**
   * Function to navigate user back to the previous page
   */
  const handleGoBack = () => {
    navigate(-1);
  };

  /**
   * Function to navigate user to the appropriate dashboard based on their role
   */
  const handleGoHome = () => {
    if (userRole === 'SystemAdministrator') {
      navigate(ROUTES.ADMIN_DASHBOARD);
    } else if (userRole === 'OrganizationAdministrator') {
      navigate(ROUTES.CLIENT_DASHBOARD);
    } else {
      navigate(ROUTES.LAW_FIRM_DASHBOARD);
    }
  };

  // Render the component inside the MainLayout component for consistent UI
  return (
    <MainLayout>
      <NotFoundContainer>
        {/* Display a 404 error code in large, bold text */}
        <ErrorCode>404</ErrorCode>

        {/* Show an error title "Page Not Found" */}
        <ErrorTitle>Page Not Found</ErrorTitle>

        {/* Display an explanatory message about the requested page not existing */}
        <ErrorMessage>
          The page you are looking for does not exist or has been moved.
        </ErrorMessage>

        {/* Provide a primary action button to return to the dashboard */}
        <ActionButtons>
          <Button variant="primary" onClick={handleGoHome}>
            Go to Dashboard
          </Button>

          {/* Provide a secondary action button to go back to the previous page */}
          <Button variant="outline" onClick={handleGoBack}>
            Go Back
          </Button>
        </ActionButtons>
      </NotFoundContainer>
    </MainLayout>
  );
};

// Export the component for use in application routing
export default NotFoundPage;