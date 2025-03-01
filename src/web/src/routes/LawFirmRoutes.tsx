import React from 'react'; // React library for building UI components //  ^18.0.0
import { Route, Routes, Navigate } from 'react-router-dom'; // React Router components for defining navigation //  ^6.4.0
import MainLayout from '../components/layout/MainLayout'; // Main layout component for authenticated pages
import DashboardPage from '../pages/dashboard/DashboardPage'; // Dashboard page component
import RateSubmissionsPage from '../pages/rates/RateSubmissionsPage'; // Rate submissions page component
import RateRequestsPage from '../pages/rates/RateRequestsPage'; // Rate requests page component
import RateHistoryPage from '../pages/rates/RateHistoryPage'; // Rate history page component
import RateAnalyticsPage from '../pages/rates/RateAnalyticsPage'; // Rate analytics page component
import ActiveNegotiationsPage from '../pages/negotiations/ActiveNegotiationsPage'; // Active negotiations page component
import CompletedNegotiationsPage from '../pages/negotiations/CompletedNegotiationsPage'; // Completed negotiations page component
import NegotiationDetailPage from '../pages/negotiations/NegotiationDetailPage'; // Negotiation detail page component
import AllMessagesPage from '../pages/messages/AllMessagesPage'; // All messages page component
import MessagesByNegotiationPage from '../pages/messages/MessagesByNegotiationPage'; // Messages by negotiation page component
import ThreadDetailPage from '../pages/messages/ThreadDetailPage'; // Thread detail page component
import AttorneyListPage from '../pages/attorneys/AttorneyListPage'; // Attorney list page component
import AttorneyDetailPage from '../pages/attorneys/AttorneyDetailPage'; // Attorney detail page component
import StaffClassPage from '../pages/attorneys/StaffClassPage'; // Staff class page component
import OCGListPage from '../pages/ocg/OCGListPage'; // OCG list page component
import OCGDetailPage from '../pages/ocg/OCGDetailPage'; // OCG detail page component
import OCGNegotiationPage from '../pages/ocg/OCGNegotiationPage'; // OCG negotiation page component
import PeerComparisonPage from '../pages/analytics/PeerComparisonPage'; // Peer comparison analytics page component
import HistoricalTrendsPage from '../pages/analytics/HistoricalTrendsPage'; // Historical trends analytics page component
import ImpactAnalysisPage from '../pages/analytics/ImpactAnalysisPage'; // Rate impact analysis page component
import CustomReportsPage from '../pages/analytics/CustomReportsPage'; // Custom reports page component
import OrganizationSettingsPage from '../pages/settings/OrganizationSettingsPage'; // Organization settings page component
import UserManagementPage from '../pages/settings/UserManagementPage'; // User management page component
import IntegrationsPage from '../pages/settings/IntegrationsPage'; // Integrations page component
import NotificationSettingsPage from '../pages/settings/NotificationSettingsPage'; // Notification settings page component
import usePermissions, { hasPermission } from '../hooks/usePermissions'; // Hook for checking user permissions
import ErrorPage from '../pages/ErrorPage'; // Error page component
import ProtectedRoute from './ProtectedRoute'; // Protected route component for authenticated routes

/**
 * Component that defines all routes accessible to law firm users in the Justice Bid application
 */
const LawFirmRoutes: React.FC = () => {
  // LD1: Define a Route element with path '/' that renders the MainLayout component
  return (
    <Routes>
      <Route element={<MainLayout />}>
        {/* LD2: Within the MainLayout, define nested routes for all law firm accessible pages */}
        {/* LD3: Add route for dashboard at index path */}
        <Route index element={<DashboardPage />} />

        {/* LD4: Add routes for rate management (submissions, requests, history, analytics) */}
        <Route path="rate-submissions" element={<RateSubmissionsPage />} />
        <Route path="rate-requests" element={<RateRequestsPage />} />
        <Route path="rate-history" element={<RateHistoryPage />} />
        <Route path="rate-analytics" element={<RateAnalyticsPage />} />

        {/* LD5: Add routes for negotiations (active, completed, detail) */}
        <Route path="negotiations" element={<ActiveNegotiationsPage />} />
        <Route path="negotiations/active" element={<ActiveNegotiationsPage />} />
        <Route path="negotiations/completed" element={<CompletedNegotiationsPage />} />
        <Route path="negotiations/:negotiationId" element={<NegotiationDetailPage />} />

        {/* LD6: Add routes for messages (all, by negotiation, thread detail) */}
        <Route path="messages" element={<AllMessagesPage />} />
        <Route path="messages/negotiation" element={<MessagesByNegotiationPage />} />
        <Route path="messages/thread/:threadId" element={<ThreadDetailPage />} />

        {/* LD7: Add routes for attorneys (list, detail, staff classes) */}
        <Route path="attorneys" element={<AttorneyListPage />} />
        <Route path="attorneys/list" element={<AttorneyListPage />} />
        <Route path="attorneys/:id" element={<AttorneyDetailPage />} />
        <Route path="attorneys/staff-class" element={<StaffClassPage />} />

        {/* LD8: Add routes for OCG (list, detail, negotiation) */}
        <Route path="ocg" element={<OCGListPage />} />
        <Route path="ocg/list" element={<OCGListPage />} />
        <Route path="ocg/:id" element={<OCGDetailPage />} />
        <Route path="ocg/:id/negotiation" element={<OCGNegotiationPage />} />

        {/* LD9: Add routes for analytics (peer comparison, historical trends, impact analysis, custom reports) */}
        <Route path="analytics" element={<RateAnalyticsPage />} />
        <Route path="analytics/peer-comparison" element={<PeerComparisonPage />} />
        <Route path="analytics/historical-trends" element={<HistoricalTrendsPage />} />
        <Route path="analytics/impact-analysis" element={<ImpactAnalysisPage />} />
        <Route path="analytics/custom-reports" element={<CustomReportsPage />} />

        {/* LD10: Add routes for settings (organization, users, integrations, notifications) */}
        <Route path="settings" element={<OrganizationSettingsPage />} />
        <Route path="settings/organization" element={<OrganizationSettingsPage />} />
        <Route path="settings/users" element={<UserManagementPage />} />
        <Route path="settings/integrations" element={<IntegrationsPage />} />
        <Route path="settings/notifications" element={<NotificationSettingsPage />} />

        {/* LD11: Add redirect from unknown paths to dashboard */}
        <Route path="*" element={<Navigate to="/law-firm" />} />
      </Route>
    </Routes>
  );
};

// IE3: Be generous about your exports so long as it doesn't create a security risk.
export default LawFirmRoutes;