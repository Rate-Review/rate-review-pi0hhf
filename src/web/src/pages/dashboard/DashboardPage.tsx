import React, { useEffect } from 'react'; // React library for building UI components //  ^18.2.0
import { Grid, Box, Typography } from '@mui/material'; // Material UI components for layout and typography //  ^5.14.0
import MainLayout from '../../components/layout/MainLayout'; // Main layout wrapper with header, sidebar, and footer
import ActionCenterCard from '../../components/dashboard/ActionCenterCard'; // Card component displaying prioritized action items
import ActiveNegotiationsCard from '../../components/dashboard/ActiveNegotiationsCard'; // Card component displaying active negotiations
import AnalyticsSummaryCard from '../../components/dashboard/AnalyticsSummaryCard'; // Card component displaying analytics summary data
import RecentMessagesCard from '../../components/dashboard/RecentMessagesCard'; // Card component displaying recent messages
import PageHeader from '../../components/layout/PageHeader'; // Header component for page title and actions
import useAuth from '../../hooks/useAuth'; // Custom hook for authentication and user information
import { useOrganizationContext } from '../../context/OrganizationContext'; // Custom hook for accessing organization context
import useWindowSize from '../../hooks/useWindowSize'; // Custom hook for responsive layout adjustments

/**
 * Main dashboard page component that displays a comprehensive overview of the system's current state and provides quick access to key features
 */
const DashboardPage: React.FC = () => {
  // LD1: Get authenticated user information using useAuth hook
  const { currentUser } = useAuth();

  // LD1: Get current organization information using useOrganizationContext hook
  const { currentOrganization } = useOrganizationContext();

  // LD1: Get window width using useWindowSize hook for responsive adjustments
  const windowSize = useWindowSize();

  // LD1: Determine if organization is a law firm or client based on organization type
  const isLawFirm = currentOrganization?.type === 'LawFirm';
  const isClient = currentOrganization?.type === 'Client';

  // LD1: Define a responsive grid layout based on screen width
  const gridSpacing = windowSize.width < 600 ? 2 : 3;

  // LD1: Render MainLayout wrapper component
  return (
    <MainLayout>
      {/* LD1: Render PageHeader with welcome message and user/organization name */}
      <PageHeader
        title={`Welcome, ${currentUser?.name || 'User'}!`}
        breadcrumbs={[
          { label: 'Dashboard', path: '/' },
        ]}
      />

      {/* LD1: Render Grid container with responsive spacing */}
      <Grid container spacing={gridSpacing}>
        {/* LD1: Render ActionCenterCard in a Grid item */}
        <Grid item xs={12} md={6}>
          <ActionCenterCard />
        </Grid>

        {/* LD1: Render ActiveNegotiationsCard in a Grid item */}
        <Grid item xs={12} md={6}>
          <ActiveNegotiationsCard />
        </Grid>

        {/* LD1: Render AnalyticsSummaryCard in a Grid item */}
        <Grid item xs={12} md={6}>
          <AnalyticsSummaryCard />
        </Grid>

        {/* LD1: Render RecentMessagesCard in a Grid item */}
        <Grid item xs={12} md={6}>
          <RecentMessagesCard />
        </Grid>
      </Grid>
    </MainLayout>
  );
};

// IE3: Be generous about your exports so long as it doesn't create a security risk.
export default DashboardPage;