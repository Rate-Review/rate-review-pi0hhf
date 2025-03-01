import React, { useEffect, useState } from 'react'; // React v18.2.0
import { Box, Typography, Skeleton } from '@mui/material'; // @mui/material v5.14.0
import ArrowForwardIcon from '@mui/icons-material/ArrowForward'; // @mui/icons-material v5.14.0
import { Link } from 'react-router-dom'; // react-router-dom v6.14.0

import DashboardCard from './DashboardCard';
import RateImpactChart from '../charts/RateImpactChart';
import useAnalytics from '../../hooks/useAnalytics';
import { ImpactAnalysisResult, AnalyticsDimension } from '../../types/analytics';

/**
 * @AnalyticsSummaryCardProps
 */
interface AnalyticsSummaryCardProps {
  height?: number;
}

/**
 * A dashboard card component that displays a summary of analytics data, including rate impact information and a visualization of rate impact by firm
 */
const AnalyticsSummaryCard: React.FC<AnalyticsSummaryCardProps> = (props) => {
  // LD1: Destructure props to get height (optional)
  const { height } = props;

  // LD1: Use useAnalytics hook to access impact analysis data, loading state, and analytics functions
  const { impactAnalysis, isLoading, fetchImpactAnalysis, getFormattedCurrency } = useAnalytics();

  // LD1: Use useState hook to manage local state for chart data
  const [chartHeight, setChartHeight] = useState(height || 300);

  // LD1: Use useEffect to fetch impact analysis data on component mount with FIRM dimension grouping
  useEffect(() => {
    fetchImpactAnalysis({
      filters: {},
      groupBy: AnalyticsDimension.FIRM,
      viewType: 'TOTAL',
      includePeerComparison: false,
      baseYear: new Date().getFullYear() - 1,
    });
  }, [fetchImpactAnalysis]);

  // LD1: Calculate chart height based on provided height prop or default value
  useEffect(() => {
    setChartHeight(height || 300);
  }, [height]);

  // LD1: Format total impact value with proper currency formatting
  const totalImpact = impactAnalysis?.totalImpact
    ? getFormattedCurrency(impactAnalysis.totalImpact, impactAnalysis.currency)
    : 'N/A';

  return (
    // LD1: Render DashboardCard with 'ANALYTICS SUMMARY' title
    <DashboardCard title="ANALYTICS SUMMARY">
      {isLoading ? (
        // LD1: Display loading skeleton when data is being fetched
        <Skeleton variant="rectangular" width="100%" height={chartHeight} />
      ) : impactAnalysis ? (
        <Box>
          {/* LD1: Display total rate impact as a formatted currency value with projected increase text */}
          <Typography variant="subtitle1" color="textSecondary" gutterBottom>
            Total Rate Impact: {totalImpact} ({impactAnalysis.percentageChange > 0 ? '+' : ''}
            {(impactAnalysis.percentageChange * 100).toFixed(2)}%)
          </Typography>

          {/* LD1: Render RateImpactChart component with impact analysis data grouped by firm */}
          <RateImpactChart
            data={impactAnalysis.items}
            groupBy="label"
            currency={impactAnalysis.currency}
            height={chartHeight}
          />
        </Box>
      ) : (
        // LD1: Handle empty state when no data is available
        <Typography variant="body2" color="textSecondary">
          No analytics data available.
        </Typography>
      )}

      {/* LD1: Include a 'View All' link that navigates to detailed analytics page */}
      <Box mt={2} display="flex" justifyContent="flex-end">
        <Link to="/analytics" style={{ display: 'flex', alignItems: 'center', textDecoration: 'none' }}>
          <Typography variant="body2" color="primary" mr={1}>
            View All
          </Typography>
          <ArrowForwardIcon fontSize="small" color="primary" />
        </Link>
      </Box>
    </DashboardCard>
  );
};

export default AnalyticsSummaryCard;