import React from 'react'; // Core React library for component creation //  ^18.0.0
import { Route, Routes } from 'react-router-dom'; // React Router library for navigation //  ^6.0.0
import ProtectedRoute from './ProtectedRoute'; // Component for protecting routes based on authentication and roles
import MainLayout from '../components/layout/MainLayout'; // Layout component for consistent page structure
import DashboardPage from '../pages/dashboard/DashboardPage'; // Dashboard page component
import RateRequestsPage from '../pages/rates/RateRequestsPage'; // Page for managing rate requests
import RateRequestReviewPage from '../pages/rates/RateRequestReviewPage'; // Page for reviewing a specific rate request
import RateHistoryPage from '../pages/rates/RateHistoryPage'; // Page for viewing historical rate data
import ActiveNegotiationsPage from '../pages/negotiations/ActiveNegotiationsPage'; // Page for viewing active negotiations
import NegotiationDetailPage from '../pages/negotiations/NegotiationDetailPage'; // Page for viewing a specific negotiation's details
import ImpactAnalysisPage from '../pages/analytics/ImpactAnalysisPage'; // Page for rate impact analysis
import PeerComparisonPage from '../pages/analytics/PeerComparisonPage'; // Page for peer comparison analytics
import CustomReportsPage from '../pages/analytics/CustomReportsPage'; // Page for creating and managing custom reports
import AllMessagesPage from '../pages/messages/AllMessagesPage'; // Page for viewing all messages
import OCGListPage from '../pages/ocg/OCGListPage'; // Page for managing Outside Counsel Guidelines
import OCGEditorPage from '../pages/ocg/OCGEditorPage'; // Page for creating and editing OCGs
import OCGDetailPage from '../pages/ocg/OCGDetailPage'; // Page for viewing OCG details
import IntegrationsPage from '../pages/settings/IntegrationsPage'; // Page for managing system integrations
import UserManagementPage from '../pages/settings/UserManagementPage'; // Page for managing user accounts
import OrganizationSettingsPage from '../pages/settings/OrganizationSettingsPage'; // Page for managing organization-level settings
import RateRulesPage from '../pages/settings/RateRulesPage'; // Page for configuring rate rules
import NotFoundPage from '../pages/NotFoundPage'; // 404 page for unmatched routes
import { ROUTES } from '../constants/routes'; // Route path constants

/**
 * Component that defines all routes available to client users, wrapped in ProtectedRoute component with client role check.
 */
const ClientRoutes: React.FC = () => {
  return (
    <Routes>
      {/* Wrap all routes in ProtectedRoute component with role='client' to enforce access control */}
      <Route element={<ProtectedRoute roleRequired="OrganizationAdministrator" />}>
        {/* Use MainLayout as the layout component for all routes */}
        <Route element={<MainLayout />}>
          {/* Define index route pointing to DashboardPage */}
          <Route index element={<DashboardPage />} />

          {/* Define routes for rate management (requests, review, history) */}
          <Route path={ROUTES.RATE_REQUESTS} element={<RateRequestsPage />} />
          <Route path={`${ROUTES.RATE_REQUESTS}/:requestId`} element={<RateRequestReviewPage />} />
          <Route path={ROUTES.RATE_HISTORY} element={<RateHistoryPage />} />

          {/* Define routes for negotiations (active, detail) */}
          <Route path={ROUTES.NEGOTIATIONS} element={<ActiveNegotiationsPage />} />
          <Route path={`${ROUTES.NEGOTIATIONS}/:negotiationId`} element={<NegotiationDetailPage />} />

          {/* Define routes for analytics (impact, peer comparison, custom reports) */}
          <Route path={ROUTES.ANALYTICS} element={<ImpactAnalysisPage />} />
          <Route path={ROUTES.IMPACT_ANALYSIS} element={<ImpactAnalysisPage />} />
          <Route path={ROUTES.PEER_COMPARISON} element={<PeerComparisonPage />} />
          <Route path={ROUTES.CUSTOM_REPORTS} element={<CustomReportsPage />} />

          {/* Define routes for messages */}
          <Route path={ROUTES.MESSAGES} element={<AllMessagesPage />} />

          {/* Define routes for OCG management (list, editor, detail) */}
          <Route path={ROUTES.OCG} element={<OCGListPage />} />
          <Route path={ROUTES.OCG_LIST} element={<OCGListPage />} />
          <Route path={ROUTES.OCG_EDITOR} element={<OCGEditorPage />} />
          <Route path={`${ROUTES.OCG}/:id`} element={<OCGDetailPage />} />

          {/* Define routes for settings (integrations, users, organization, rate rules) */}
          <Route path={ROUTES.SETTINGS} element={<OrganizationSettingsPage />} />
          <Route path={ROUTES.ORGANIZATION_SETTINGS} element={<OrganizationSettingsPage />} />
          <Route path={ROUTES.USER_MANAGEMENT} element={<UserManagementPage />} />
          <Route path={ROUTES.RATE_RULES} element={<RateRulesPage />} />
          <Route path={ROUTES.INTEGRATIONS} element={<IntegrationsPage />} />

          {/* Include catch-all route for NotFoundPage */}
          <Route path="*" element={<NotFoundPage />} />
        </Route>
      </Route>
    </Routes>
  );
};

export default ClientRoutes;