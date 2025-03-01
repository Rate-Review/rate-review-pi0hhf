import React, { useState, useEffect, useCallback } from 'react'; // React v18.0+
import { useSelector, useDispatch } from 'react-redux'; // Redux hooks for accessing and updating state //  ^8.1.0
import { Grid, Paper, Typography, Box, CircularProgress } from '@mui/material'; // Material UI components for layout and styling //  ^5.14.0

import MainLayout from '../components/layout/MainLayout'; // Page layout wrapper component
import PageHeader from '../components/layout/PageHeader'; // Header component for the page title and actions
import AnalyticsFilters from '../components/analytics/AnalyticsFilters'; // Filtering component for analytics data
import ImpactAnalysisPanel from '../components/analytics/ImpactAnalysisPanel'; // Component for displaying rate impact analysis
import PeerComparisonPanel from '../components/analytics/PeerComparisonPanel'; // Component for displaying peer comparison analysis
import HistoricalTrendsPanel from '../components/analytics/HistoricalTrendsPanel'; // Component for displaying historical rate trends
import ExportControls from '../components/analytics/ExportControls'; // Component for exporting analytics data
import Button from '../components/common/Button'; // Reusable button component
import Tabs from '../components/common/Tabs'; // Tab navigation component
import AIChatInterface from '../components/ai/AIChatInterface'; // AI chat interface component for analytics assistance
import { usePermissions } from '../hooks/usePermissions'; // Custom hook for permission checking
import { fetchRateImpact, fetchPeerComparison, fetchHistoricalTrends } from '../store/analytics/analyticsThunks'; // Redux thunks for fetching analytics data
import { AnalyticsFilter, PeriodOption } from '../types/analytics'; // TypeScript types for analytics data

/**
 * Main component that renders the rate analytics page with different analysis panels
 */
const RateAnalyticsPage: React.FC = () => {
  // LD1: Initialize state for filters using useState
  const [filters, setFilters] = useState<AnalyticsFilter>({
    view: 'netImpact',
    period: '2023-2024',
    firm: 'all',
    practice: 'all',
    geography: 'all',
  });

  // LD1: Initialize state for selected tab using useState
  const [selectedTab, setSelectedTab] = useState<number>(0);

  // LD1: Check user permissions using usePermissions hook
  const { can } = usePermissions();

  // LD1: Access analytics data from Redux store using useSelector
  const rateImpact = useSelector((state: any) => state.analytics.rateImpact);
  const peerComparison = useSelector((state: any) => state.analytics.peerComparison);
  const historicalTrends = useSelector((state: any) => state.analytics.historicalTrends);
  const loading = useSelector((state: any) => state.analytics.loading);
  const error = useSelector((state: any) => state.analytics.error);

  // LD1: Get dispatch function using useDispatch
  const dispatch = useDispatch();

  // LD1: Fetch analytics data on component mount and when filters change using useEffect
  useEffect(() => {
    dispatch(fetchRateImpact(filters));
    dispatch(fetchPeerComparison(filters));
    dispatch(fetchHistoricalTrends(filters));
  }, [dispatch, filters]);

  // LD1: Handle filter changes with updateFilters function
  const updateFilters = (newFilters: object) => {
    setFilters({
      ...filters,
      ...newFilters,
    });
  };

  // LD1: Handle tab changes with handleTabChange function
  const handleTabChange = (newTabIndex: number) => {
    setSelectedTab(newTabIndex);
  };

  // LD1: Handle navigation to the custom report builder
  const handleCreateCustomReport = () => {
    // TODO: Implement navigation logic
    console.log('Navigating to custom report builder with filters:', filters);
  };

  // LD1: Handle sharing the current analytics view
  const handleShare = () => {
    // TODO: Implement sharing logic
    console.log('Sharing analytics view with filters:', filters);
  };

  // LD1: Render the page layout with MainLayout component
  return (
    <MainLayout>
      {/* LD1: Render PageHeader with title and export buttons */}
      <PageHeader
        title="Rate Analytics"
        actions={
          <Box>
            {can('create', 'reports', 'organization') && (
              <Button variant="contained" onClick={handleCreateCustomReport}>
                Create Custom Report
              </Button>
            )}
            {can('share', 'reports', 'organization') && (
              <Button variant="outlined" onClick={handleShare}>
                Share
              </Button>
            )}
            <ExportControls data={{}} title="Rate Analytics" onExport={() => {}} isLoading={loading} />
          </Box>
        }
      />

      {/* LD1: Render AnalyticsFilters component for filtering data */}
      <AnalyticsFilters initialFilters={filters} onFilterChange={updateFilters} />

      {/* LD1: Render TabNavigation for switching between analysis views */}
      <Tabs
        tabs={[
          { id: 0, label: 'Impact Analysis' },
          { id: 1, label: 'Peer Comparison' },
          { id: 2, label: 'Historical Trends' },
        ]}
        activeTab={selectedTab}
        onChange={handleTabChange}
      />

      {/* LD1: Render the selected analysis panel based on tab state */}
      {loading && <CircularProgress />}
      {error && <Typography color="error">{error}</Typography>}
      {!loading && !error && (
        <>
          {selectedTab === 0 && <ImpactAnalysisPanel filters={filters} />}
          {selectedTab === 1 && <PeerComparisonPanel filters={filters} />}
          {selectedTab === 2 && <HistoricalTrendsPanel filters={filters} />}
        </>
      )}

      {/* LD1: Render the AI chat interface component at the bottom of the page */}
      <AIChatInterface />
    </MainLayout>
  );
};

// IE3: Be generous about your exports so long as it doesn't create a security risk.
export default RateAnalyticsPage;