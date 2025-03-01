import React from 'react'; //  ^18.0.0
import { Navigate, useLocation, Outlet } from 'react-router-dom'; //  ^6.4.0
import { useAuth } from '../hooks/useAuth';
import { usePermissionContext } from '../context/PermissionContext';
import Spinner from '../components/common/Spinner';

/**
 * @interface ProtectedRouteProps
 * @description Props for the ProtectedRoute component
 */
interface ProtectedRouteProps {
  /**
   * @property {React.ComponentType<any>} component - The component to render if the user is authenticated and authorized.
   * @optional
   */
  component?: React.ComponentType<any>;
  /**
   * @property {string} roleRequired - The role required to access the route.
   * @optional
   */
  roleRequired?: string;
  /**
   * @property {string[]} permissionsRequired - An array of permissions required to access the route.
   * @optional
   */
  permissionsRequired?: string[];
  /**
   * @property {any} rest - Additional props to pass to the component.
   * @optional
   */
  rest?: any;
}

/**
 * @function ProtectedRoute
 * @description A functional component that renders a route accessible only to authenticated users with proper permissions
 * @param {ProtectedRouteProps} props - The props for the component
 * @returns {JSX.Element} Protected content or redirect component
 */
const ProtectedRoute: React.FC<ProtectedRouteProps> = ({
  component: Component,
  roleRequired,
  permissionsRequired,
  ...rest
}) => {
  // IE1: Get authentication state (isAuthenticated, user) from useAuth hook
  const { isAuthenticated, user } = useAuth();

  // IE2: Get permission state (hasPermission, userRole, isLoading) from usePermissions hook
  const { hasPermission, isLoading } = usePermissionContext();

  // IE3: Get current location using useLocation hook to preserve redirect location
  const location = useLocation();

  // 5. If permissions are still loading, render a Spinner component
  if (isLoading) {
    return <Spinner />;
  }

  // 6. If user is not authenticated, redirect to login with current location in state
  if (!isAuthenticated) {
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  // 7. If roleRequired is provided and user's role doesn't match, redirect to error page with unauthorized message
  if (roleRequired && user?.role !== roleRequired) {
    return (
      <Navigate
        to="/error"
        state={{ message: 'Unauthorized: Insufficient role.' }}
        replace
      />
    );
  }

  // 8. If permissionsRequired is provided, check if user has all required permissions
  if (permissionsRequired) {
    const hasAllPermissions = permissionsRequired.every((permission) =>
      hasPermission(permission)
    );

    // 9. If permissions check fails, redirect to error page with insufficient permissions message
    if (!hasAllPermissions) {
      return (
        <Navigate
          to="/error"
          state={{ message: 'Unauthorized: Insufficient permissions.' }}
          replace
        />
      );
    }
  }

  // 10. If all checks pass, render either the Component or Outlet (for nested routes) with props
  return Component ? <Component {...rest} /> : <Outlet />;
};

export default ProtectedRoute;