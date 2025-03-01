import React, { FC } from 'react'; //  ^18.2.0
import { Navigate, Outlet, useLocation } from 'react-router-dom'; //  ^6.4.0
import { useAuth } from '../hooks/useAuth'; // src/web/src/hooks/useAuth.ts

/**
 * @description Defines the properties for the PublicRoute component
 */
interface PublicRouteProps {
  redirectPath?: string;
}

/**
 * @description A route component that only allows access to unauthenticated users and redirects authenticated users to the dashboard.
 * @param {PublicRouteProps} props - The properties passed to the component, including an optional redirectPath.
 * @returns {JSX.Element} Either a Navigate component for redirection or an Outlet component for child routes
 */
const PublicRoute: FC<PublicRouteProps> = ({ redirectPath = '/dashboard' }) => {
  // LD1: Destructure props to get redirectPath (default to '/dashboard')
  // LD2: Get authentication status from useAuth hook
  const { isAuthenticated } = useAuth();

  // LD3: Get current location using useLocation hook
  const location = useLocation();

  // LD4: If user is authenticated, return Navigate component pointing to redirectPath, preserving the current location in state
  if (isAuthenticated) {
    return <Navigate to={redirectPath} state={{ from: location }} replace />;
  }

  // LD5: If user is not authenticated, return the Outlet component for the child routes
  return <Outlet />;
};

// IE3: Export the PublicRoute component for use in the application
export default PublicRoute;