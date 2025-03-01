import React from 'react'; // React: ^18.0.0
import { useState, useEffect, useMemo } from 'react'; // React: ^18.0.0
import styled from 'styled-components'; // styled-components: ^5.3.6
import { Grid, Box, Typography, Tabs, Tab, CircularProgress, Alert, Rating } from '@mui/material'; // @mui/material: ^5.14.0

import Card from '../common/Card';
import PerformanceChart from '../charts/PerformanceChart';
import MetricDisplay from './MetricDisplay';
import useAnalytics from '../../hooks/useAnalytics';
import { 
  AttorneyPerformanceResult, 
  AttorneyPerformanceMetricType,
  AttorneyPerformanceParams 
} from '../../types/analytics';
import { formatCurrency } from '../../utils/currency';

// Define props for the AttorneyPerformancePanel component
interface AttorneyPerformancePanelProps {
  attorneyId: string;
  initialFilters?: object;
  height?: number | string;
  title?: string;
  className?: string;
  onMetricClick?: (metricType: AttorneyPerformanceMetricType) => void;
}

// Styled components for layout and styling
const PanelContainer = styled.div`
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
`;

const MetricsContainer = styled.div`
  display: flex;
  flex-wrap: wrap;
  gap: 16px;
  margin-bottom: 20px;
`;

const ChartContainer = styled.div`
  flex: 1;
  min-height: 300px;
  position: relative;
`;

const SectionContainer = styled.div`
  margin-bottom: 24px;
`;

const TabsContainer = styled.div`
  margin-bottom: 20px;
`;

const LoadingContainer = styled.div`
  display: flex;
  justify-content: center;
  align-items: center;
  height: 400px;
`;

const RatingContainer = styled.div`
  display: flex;
  align-items: center;
  gap: 8px;
`;

/**
 * Formats a percentile value for display, including a textual description
 * @param value The percentile value
 * @returns An object containing the formatted value and description
 */
const formatPercentile = (value: number) => {
  const formattedValue = `${value.toFixed(0)}%`;
  let description = 'Average';

  if (value >= 75) {
    description = 'High';
  } else if (value <= 25) {
    description = 'Low';
  }

  return {
    value: formattedValue,
    description: description,
  };
};

/**
 * Prepares parameters for the attorney performance API request
 * @param attorneyId The ID of the attorney
 * @param filters Additional filters for the request
 * @returns An object containing the formatted parameters
 */
const preparePerformanceParams = (attorneyId: string, filters: object): AttorneyPerformanceParams => {
  return {
    attorneyId: attorneyId,
    filters: filters,
    metricTypes: [], // Include all metric types
    includeUniCourtData: true, // Always include UniCourt data
  };
};

/**
 * A component that displays detailed performance metrics for a selected attorney, 
 * including billing data, court performance, and client ratings
 * @param props - The component props
 * @returns The rendered component
 */
const AttorneyPerformancePanel: React.FC<AttorneyPerformancePanelProps> = (props) => {
  // LD1: Extract attorneyId, initialFilters, and other props
  const { attorneyId, initialFilters, height = 400, title = "Attorney Performance", className, onMetricClick } = props;

  // LD1: Initialize state for active metric tab and chart type
  const [activeTab, setActiveTab] = useState<AttorneyPerformanceMetricType>("HOURS");
  const [chartType, setChartType] = useState<'radar' | 'bar'>('radar');

  // LD1: Import attorney performance data and methods from useAnalytics hook
  const { 
    fetchAttorneyPerformance, 
    attorneyPerformance, 
    isLoading, 
    error 
  } = useAnalytics();

  // LD1: Use useEffect to fetch attorney performance data when attorneyId changes
  useEffect(() => {
    if (attorneyId) {
      const params = preparePerformanceParams(attorneyId, initialFilters || {});
      fetchAttorneyPerformance(params);
    }
  }, [attorneyId, fetchAttorneyPerformance, initialFilters]);

  // LD1: Create handleTabChange function to switch between performance metric views
  const handleTabChange = (event: React.SyntheticEvent, newValue: AttorneyPerformanceMetricType) => {
    setActiveTab(newValue);
    setChartType('bar'); // Switch to bar chart when a specific metric is selected
    if (onMetricClick) {
      onMetricClick(newValue);
    }
  };

  // LD1: Define renderMetrics function to display key performance indicators
  const renderMetrics = () => {
    if (!attorneyPerformance || !attorneyPerformance.metrics) return null;

    return (
      <MetricsContainer>
        {attorneyPerformance.metrics.map((metric) => (
          <MetricDisplay
            key={metric.type}
            label={metric.label}
            value={metric.value}
            format="number"
            showTrend={true}
            previousValue={metric.historicalData[0]?.value}
            tooltipText={`Historical data for ${metric.label}`}
          />
        ))}
      </MetricsContainer>
    );
  };

  // LD1: Define renderUniCourtData function to display court performance data from UniCourt
  const renderUniCourtData = () => {
    if (!attorneyPerformance || !attorneyPerformance.unicourtData) return null;

    const { winRate, caseCount, overallPercentile } = attorneyPerformance.unicourtData;
    const formattedPercentile = formatPercentile(overallPercentile);

    return (
      <MetricsContainer>
        <MetricDisplay label="Win Rate" value={winRate} format="percentage" />
        <MetricDisplay label="Case Count" value={caseCount} format="number" />
        <MetricDisplay label="Overall Percentile" value={parseFloat(formattedPercentile.value)} format="number" tooltipText={formattedPercentile.description} />
      </MetricsContainer>
    );
  };

  // LD1: Define renderHistoricalData function to display billing history trends
  const renderHistoricalData = () => {
    // Implement historical data rendering logic here
    return <Typography>Historical Data Coming Soon</Typography>;
  };

  // LD1: Define renderRatingSection function to display client ratings
  const renderRatingSection = () => {
    if (!attorneyPerformance) return null;

    return (
      <RatingContainer>
        <Typography component="legend">Client Rating:</Typography>
        <Rating name="client-rating" value={attorneyPerformance.overallRating} readOnly />
      </RatingContainer>
    );
  };

  // LD1: Define renderPerformanceChart function to render the appropriate visualization
  const renderPerformanceChart = () => {
    if (!attorneyPerformance) return null;

    return (
      <ChartContainer>
        <PerformanceChart
          performanceData={attorneyPerformance}
          isLoading={isLoading}
          chartType={chartType}
          metricType={activeTab}
          height={300}
        />
      </ChartContainer>
    );
  };

  // LD1: Define renderContent function to handle different view states (loading, error, content)
  const renderContent = () => {
    if (isLoading) {
      return (
        <LoadingContainer>
          <CircularProgress />
        </LoadingContainer>
      );
    }

    if (error) {
      return (
        <LoadingContainer>
          <Alert severity="error">{error}</Alert>
        </LoadingContainer>
      );
    }

    return (
      <>
        <SectionContainer>
          <Typography variant="h6">Key Metrics</Typography>
          {renderMetrics()}
        </SectionContainer>

        <SectionContainer>
          <Typography variant="h6">UniCourt Performance</Typography>
          {renderUniCourtData()}
        </SectionContainer>

        <SectionContainer>
          <Typography variant="h6">Performance Chart</Typography>
          <TabsContainer>
            <Tabs
              value={activeTab}
              onChange={handleTabChange}
              aria-label="performance metric tabs"
            >
              <Tab label="Hours" value="HOURS" />
              <Tab label="Matters" value="MATTERS" />
              <Tab label="Client Rating" value="CLIENT_RATING" />
              <Tab label="Efficiency" value="EFFICIENCY" />
            </Tabs>
          </TabsContainer>
          {renderPerformanceChart()}
        </SectionContainer>

        <SectionContainer>
          <Typography variant="h6">Billing History</Typography>
          {renderHistoricalData()}
        </SectionContainer>

        <SectionContainer>
          {renderRatingSection()}
        </SectionContainer>
      </>
    );
  };

  // LD1: Return the component JSX with Card layout containing all performance sections
  return (
    <Card className={className} height={height} title={title}>
      <PanelContainer>
        {renderContent()}
      </PanelContainer>
    </Card>
  );
};

export default AttorneyPerformancePanel;