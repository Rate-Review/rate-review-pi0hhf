import React, { useState, useEffect, useMemo } from 'react'; // React v18.2.0
import styled from 'styled-components'; // styled-components v5.3.6
import { Grid, Paper } from '@mui/material'; // @mui/material v5.14.0
import FileDownload from '@mui/icons-material/FileDownload'; // @mui/icons-material v5.14.0

import useAnalytics from '../../hooks/useAnalytics';
import PeerComparisonPanel from '../../components/analytics/PeerComparisonPanel';
import AnalyticsFilters from '../../components/analytics/AnalyticsFilters';
import PageHeader from '../../components/layout/PageHeader';
import Alert from '../../components/common/Alert';
import Button from '../../components/common/Button';
import { ReportExportFormat, PeerComparisonViewType, AnalyticsDimension } from '../../types/analytics';

// Styled components for layout and styling
const PageContainer = styled.div`
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
  min-height: 100%;
  padding: 1.5rem;
`;

const ContentContainer = styled.div`
  display: flex;
  flex: 1;
  gap: 1.5rem;
`;

const FiltersContainer = styled(Paper)`
  padding: 1.5rem;
  min-width: 250px;
  height: fit-content;
`;

const MainContentContainer = styled.div`
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
`;

/**
 * Component that renders the Peer Comparison analytics page
 */
export const PeerComparisonPage: React.FC = () => {
  // LD1: Initialize analytics hooks using useAnalytics to access peer comparison data and functions
  const { peerComparison, isLoading, error, filters, fetchPeerComparison, setFilters, exportData } = useAnalytics();

  // LD1: Define state for managing view type and dimension with useState
  const [viewType, setViewType] = useState<PeerComparisonViewType>(PeerComparisonViewType.AVERAGE);
  const [dimension, setDimension] = useState<AnalyticsDimension>(AnalyticsDimension.FIRM);

  // LD1: Use useEffect to fetch peer comparison data when filters, viewType, or dimension changes
  useEffect(() => {
    fetchPeerComparison({ ...filters, viewType, groupBy: dimension });
  }, [filters, viewType, dimension, fetchPeerComparison]);

  /**
   * Handles changes to the analytics filters
   * @param {object} newFilters - The new filter values
   * @returns {void} No return value
   */
  const handleFilterChange = (newFilters: object): void => {
    // Update the filters state with the new values
    setFilters(newFilters);
  };

  /**
   * Handles changes to the peer comparison view type
   * @param {PeerComparisonViewType} newViewType - The new view type
   * @returns {void} No return value
   */
  const handleViewTypeChange = (newViewType: PeerComparisonViewType): void => {
    // Update the view type state with the new value
    setViewType(newViewType);
  };

  /**
   * Handles changes to the analytics dimension
   * @param {AnalyticsDimension} newDimension - The new dimension
   * @returns {void} No return value
   */
  const handleDimensionChange = (newDimension: AnalyticsDimension): void => {
    // Update the dimension state with the new value
    setDimension(newDimension);
  };

  /**
   * Handles the export action
   * @param {ReportExportFormat} format - The export format
   * @returns {void} No return value
   */
  const handleExport = (format: ReportExportFormat): void => {
    // Call the exportData function with the selected format
    exportData(format);
  };

  // LD1: Set up breadcrumbs array for navigation context
  const breadcrumbs = [
    { label: 'Dashboard', path: '/dashboard' },
    { label: 'Analytics', path: '/analytics' },
    { label: 'Peer Comparison', path: '/analytics/peer-comparison' },
  ];

  // LD1: Create export button for the PageHeader actions
  const exportButton = (
    <Button variant="outlined" color="primary" onClick={() => handleExport(ReportExportFormat.CSV)}>
      Export <FileDownload />
    </Button>
  );

  // LD1: Render PageHeader with title 'Peer Comparison' and export button
  return (
    <PageContainer>
      <PageHeader title="Peer Comparison" breadcrumbs={breadcrumbs} actions={exportButton} />

      <ContentContainer>
        {/* LD1: Render Grid layout with AnalyticsFilters in left column */}
        <Grid container spacing={2}>
          <Grid item xs={12} md={4}>
            <FiltersContainer>
              <AnalyticsFilters initialFilters={filters} onFilterChange={handleFilterChange} />
            </FiltersContainer>
          </Grid>

          {/* LD1: Render error Alert if there is an error fetching data */}
          <Grid item xs={12} md={8}>
            <MainContentContainer>
              {error && <Alert severity="error" message={error} />}

              {/* LD1: Render PeerComparisonPanel in main content area */}
              {/* LD1: Pass view controls and data to PeerComparisonPanel component */}
              <PeerComparisonPanel
                title="Peer Group Comparison"
                filters={filters}
                onExport={handleExport}
              />
            </MainContentContainer>
          </Grid>
        </Grid>
      </ContentContainer>
    </PageContainer>
  );
};

export default PeerComparisonPage;