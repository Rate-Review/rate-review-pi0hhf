import React from 'react'; //  ^18.0.0
import { Route, Routes, Navigate } from 'react-router-dom'; //  ^6.4.0

import ProtectedRoute from './ProtectedRoute'; // Wrapper component for protected routes
import { ROUTES } from '../constants/routes'; // Route path constants
import UserManagementPage from '../pages/settings/UserManagementPage'; // Page for managing users
import OrganizationSettingsPage from '../pages/settings/OrganizationSettingsPage'; // Page for organization settings
import IntegrationsPage from '../pages/settings/IntegrationsPage'; // Page for managing integrations
import PeerGroupsPage from '../pages/settings/PeerGroupsPage'; // Page for managing peer groups
import RateRulesPage from '../pages/settings/RateRulesPage'; // Page for configuring rate rules
import NotificationSettingsPage from '../pages/settings/NotificationSettingsPage'; // Page for configuring notifications
import AIConfigurationPage from '../pages/settings/AIConfigurationPage'; // Page for configuring AI settings
import { usePermissions } from '../hooks/usePermissions'; // Hook for checking user permissions

/**
 * Functional component that defines routes accessible only to administrators
 */
const AdminRoutes: React.FC = () => {
  // Import required components, hooks, and route constants

  // Use the usePermissions hook to check if the current user has admin permissions
  const { checkPermission } = usePermissions();

  // Define a Routes component containing all admin-specific routes
  return (
    <Routes>
      {/* Wrap each admin page component with ProtectedRoute component, specifying admin-specific permission requirements */}
      <Route
        path={ROUTES.USER_MANAGEMENT}
        element={
          <ProtectedRoute
            component={UserManagementPage}
            permissionsRequired={['manage:users:organization']}
          />
        }
      />
      {/* Include routes for UserManagement, OrganizationSettings, Integrations, PeerGroups, RateRules, NotificationSettings, and AIConfiguration */}
      <Route
        path={ROUTES.ORGANIZATION_SETTINGS}
        element={
          <ProtectedRoute
            component={OrganizationSettingsPage}
            permissionsRequired={['manage:organizations:organization']}
          />
        }
      />
      <Route
        path={`${ROUTES.INTEGRATIONS}/*`}
        element={
          <ProtectedRoute
            component={IntegrationsPage}
            permissionsRequired={['manage:integrations:organization']}
          />
        }
      />
      <Route
        path={ROUTES.PEER_GROUPS}
        element={
          <ProtectedRoute
            component={PeerGroupsPage}
            permissionsRequired={['manage:peer_groups:organization']}
          />
        }
      />
      <Route
        path={ROUTES.RATE_RULES}
        element={
          <ProtectedRoute
            component={RateRulesPage}
            permissionsRequired={['manage:rate_rules:organization']}
          />
        }
      />
      <Route
        path={ROUTES.NOTIFICATION_SETTINGS}
        element={
          <ProtectedRoute
            component={NotificationSettingsPage}
            permissionsRequired={['manage:notification_settings:organization']}
          />
        }
      />
      <Route
        path={ROUTES.AI_CONFIGURATION}
        element={
          <ProtectedRoute
            component={AIConfigurationPage}
            permissionsRequired={['manage:ai:organization']}
          />
        }
      />
      {/* Add a fallback route to redirect unauthorized access attempts to the dashboard */}
      <Route
        path="*"
        element={<Navigate to={ROUTES.ADMIN_DASHBOARD} replace />}
      />
    </Routes>
  );
};

// Export the Routes component with all the defined admin routes
export default AdminRoutes;