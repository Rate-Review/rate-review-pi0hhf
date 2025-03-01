import React, { useState, useEffect, useCallback } from 'react'; // React library for building UI components //  ^18.2.0
import { useNavigate, useLocation } from 'react-router-dom'; // React Router hooks for navigation and location //  ^6.4.0
import styled from 'styled-components'; // CSS-in-JS styling library
import MainLayout from '../../components/layout/MainLayout'; // Main layout wrapper for all authenticated pages
import PageHeader from '../../components/layout/PageHeader'; // Header component for page title and actions
import ImpactAnalysisPanel from '../../components/analytics/ImpactAnalysisPanel'; // Main component for displaying impact analysis data and visualizations
import Card from '../../components/common/Card'; // Wrapper component for content sections
import Button from '../../components/common/Button'; // Button component for user actions
import RecommendationCard from '../../components/ai/RecommendationCard'; // Component for displaying AI-driven recommendations
import AnalyticsFilters from '../../components/analytics/AnalyticsFilters'; // Filter component for analytics data
import useAnalytics from '../../hooks/useAnalytics'; // Custom hook for accessing analytics functionality
import { FilterOptions, ImpactViewType, AnalyticsDimension } from '../../types/analytics'; // Type definition for filter options

// LD1: Styled component for the page container
const PageContainer = styled.div`
  padding: 24px;
  display: flex;
  flex-direction: column;
  gap: 24px;
`;

// LD1: Styled component for the filters container
const FiltersContainer = styled.div`
  margin-bottom: 24px;
`;

// LD1: Styled component for the content grid
const ContentGrid = styled.div`
  display: grid;
  grid-template-columns: 1fr;
  gap: 24px;

  @media (min-width: 1200px) {
    grid-template-columns: 3fr 1fr;
  }
`;

// LD1: Styled component for the main content area
const MainContent = styled.div`
  display: flex;
  flex-direction: column;
  gap: 24px;
`;

// LD1: Styled component for the side content area
const SideContent = styled.div`
  display: flex;
  flex-direction: column;
  gap: 24px;
`;

// LD1: Main page component for rate impact analysis
const ImpactAnalysisPage: React.FC = () => {
  // LD1: Initialize navigation and location hooks
  const navigate = useNavigate();
  const location = useLocation();

  // LD1: Initialize analytics hook to access impact analysis data and functions
  const {
    impactAnalysis,
    fetchImpactAnalysis,
    setFilters,
    isLoading,
    error,
  } = useAnalytics();

  // LD1: Set up state for active tab and filter visibility
  const [activeTab, setActiveTab] = useState('summary');
  const [showFilters, setShowFilters] = useState(true);

  // LD1: Initialize filter state management
  const [filters, setLocalFilters] = useState<FilterOptions>({});

  // LD1: Define filter change handler to update analytics filters
  const handleFilterChange = (newFilters: FilterOptions) => {
    setLocalFilters(newFilters);
    setFilters(newFilters);
  };

  // LD1: Define export handler to export impact analysis data
  const handleExport = (format: string) => {
    // TODO: Implement export functionality
    console.log(`Exporting data in ${format} format`);
  };

  // LD1: Define breadcrumb navigation for the page
  const breadcrumbs = [
    { label: 'Analytics', path: '/analytics' },
    { label: 'Rate Impact Analysis', path: location.pathname },
  ];

  // LD1: Use useEffect to load initial data when page loads or filters change
  useEffect(() => {
    fetchImpactAnalysis({
      filters: filters,
      viewType: 'TOTAL' as ImpactViewType,
      groupBy: 'FIRM' as AnalyticsDimension,
    });
  }, [fetchImpactAnalysis, filters]);

  // LD1: Render the page with MainLayout
  return (
    <MainLayout>
      <PageContainer>
        {/* LD1: Include PageHeader with title and actions */}
        <PageHeader
          title="Rate Impact Analysis"
          breadcrumbs={breadcrumbs}
          actions={
            <Button variant="contained" onClick={() => setShowFilters(!showFilters)}>
              {showFilters ? 'Hide Filters' : 'Show Filters'}
            </Button>
          }
        />

        {/* LD1: Render filter section with AnalyticsFilters component */}
        {showFilters && (
          <FiltersContainer>
            <AnalyticsFilters
              initialFilters={filters}
              onFilterChange={handleFilterChange}
            />
          </FiltersContainer>
        )}

        {/* LD1: Render main content area with ImpactAnalysisPanel and AI recommendation */}
        <ContentGrid>
          <MainContent>
            {/* LD1: Render ImpactAnalysisPanel as the main content */}
            <ImpactAnalysisPanel
              filters={filters}
              onFilterChange={handleFilterChange}
              showFilters={false}
              showExport={true}
            />
          </MainContent>

          {/* LD1: Conditionally render AI recommendation card with insights */}
          <SideContent>
            {impactAnalysis && impactAnalysis.totalImpact > 10000 && (
              <RecommendationCard
                recommendation={{
                  id: '1',
                  type: 'APPROVE',
                  value: 0.05,
                  rationale: 'The rate increase is within acceptable limits.',
                  confidence: 0.8,
                  relatedRates: [],
                }}
                onApply={() => console.log('Applying recommendation')}
                onDismiss={() => console.log('Dismissing recommendation')}
                onViewExplanation={() => console.log('Viewing explanation')}
              />
            )}
          </SideContent>
        </ContentGrid>
      </PageContainer>
    </MainLayout>
  );
};

export default ImpactAnalysisPage;