import React, { useState, useEffect, useMemo } from 'react'; //  ^18.0.0
import styled from 'styled-components'; //  ^5.3.0
import LineChart from './LineChart';
import { formatDisplayDate } from '../../utils/date';
import { calculateHistoricalTrend } from '../../utils/calculations';
import theme from '../../theme';
import { Rate, RateHistory } from '../../types/rate';
import { getRateHistory } from '../../services/rates';

// Define the RateTrendChartProps interface
interface RateTrendChartProps {
  attorneyId?: string;
  clientId?: string;
  firmId?: string;
  staffClassId?: string;
  timeRange?: 'past-1-year' | 'past-3-years' | 'past-5-years' | 'custom';
  startDate?: string;
  endDate?: string;
  showPeerComparison?: boolean;
  peerGroupId?: string;
  height?: number;
  width?: string;
  showProposedRates?: boolean;
  onPointClick?: (date: string, rate: number) => void;
  className?: string;
  title?: string;
  subtitle?: string;
  showLegend?: boolean;
  customColors?: string[];
  isCurrency?: boolean;
}

// Define the RateTrendData interface
interface RateTrendData {
  labels: string[];
  datasets: Array<{
    label: string;
    data: number[];
    borderColor: string;
    backgroundColor: string;
    borderWidth: number;
    fill: boolean;
    tension: number;
  }>;
}

// Styled components for the chart
const ChartContainer = styled.div<{ width?: string }>`
  width: ${props => props.width || '100%'};
  position: relative;
  margin-bottom: 24px;
`;

const ChartHeader = styled.div`
  display: flex;
  flex-direction: column;
  margin-bottom: 16px;
`;

const ChartTitle = styled.h4`
  font-size: 18px;
  margin: 0 0 4px 0;
  color: ${theme.colors.primary.main};
`;

const ChartSubtitle = styled.p`
  font-size: 14px;
  margin: 0;
  color: ${theme.colors.neutral.main};
`;

const LoadingOverlay = styled.div`
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  display: flex;
  justify-content: center;
  align-items: center;
  background-color: rgba(255, 255, 255, 0.8);
  z-index: 10;
`;

const ErrorMessage = styled.div`
  color: ${theme.colors.error.main};
  text-align: center;
  padding: 16px;
`;

/**
 * Transforms rate history data into a format suitable for the LineChart component
 * @param rateHistory - Array of rate history data
 * @param showProposedRates - Boolean to indicate whether to show proposed rates
 * @param customColors - Array of custom colors for the chart
 * @returns Formatted data for the LineChart component
 */
const transformHistoryToChartData = (
  rateHistory: RateHistory[],
  showProposedRates: boolean,
  customColors?: string[]
): RateTrendData => {
  // Sort rate history by date
  const sortedHistory = [...rateHistory].sort(
    (a, b) => new Date(a.effectiveDate).getTime() - new Date(b.effectiveDate).getTime()
  );

  // Group rates by type (e.g., standard, approved, proposed)
  const groupedRates: { [key: string]: { date: string; rate: number }[] } = {};
  sortedHistory.forEach(item => {
    const key = item.type;
    if (!groupedRates[key]) {
      groupedRates[key] = [];
    }
    groupedRates[key].push({ date: item.effectiveDate, rate: item.amount });
  });

  // Extract unique dates for chart labels
  const uniqueDates = Array.from(new Set(sortedHistory.map(item => item.effectiveDate)));

  // Format dates for display using formatDisplayDate
  const labels = uniqueDates.map(date => formatDisplayDate(date));

  // Create datasets for each rate type with appropriate colors
  const datasets = Object.entries(groupedRates).map(([type, rates], index) => ({
    label: type,
    data: uniqueDates.map(date => {
      const rateForDate = rates.find(r => r.date === date);
      return rateForDate ? rateForDate.rate : null;
    }),
    borderColor: customColors?.[index] || theme.colors.primary.main,
    backgroundColor: customColors?.[index] ? `${customColors[index]}33` : `${theme.colors.primary.main}33`,
    borderWidth: 2,
    fill: false,
    tension: 0.4,
  }));

  // Filter out proposed rates if showProposedRates is false
  const filteredDatasets = showProposedRates
    ? datasets
    : datasets.filter(dataset => dataset.label !== 'proposed');

  return {
    labels,
    datasets: filteredDatasets,
  };
};

/**
 * A component that displays historical rate trends over time with optional peer comparison
 * @param props - Component props including data, labels, and customization options
 * @returns JSX.Element - Rendered chart component
 */
const RateTrendChart: React.FC<RateTrendChartProps> = (props) => {
  // Initialize state variables for loading, error, and rate history data
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [rateHistory, setRateHistory] = useState<RateHistory[]>([]);

  // Destructure props
  const {
    attorneyId,
    clientId,
    firmId,
    staffClassId,
    timeRange,
    startDate,
    endDate,
    showPeerComparison,
    peerGroupId,
    height,
    width,
    showProposedRates = true,
    onPointClick,
    className,
    title = 'Rate Trend',
    subtitle,
    showLegend,
    customColors,
    isCurrency
  } = props;

  // Use useEffect to fetch rate history when component mounts or dependencies change
  useEffect(() => {
    const fetchRateData = async () => {
      setLoading(true);
      setError(null);
      try {
        // Call getRateHistory with appropriate parameters (attorneyId, clientId, etc.)
        const data = await getRateHistory(attorneyId, clientId);
        setRateHistory(data);
      } catch (e: any) {
        setError(e.message || 'Failed to fetch rate history.');
      } finally {
        setLoading(false);
      }
    };

    fetchRateData();
  }, [attorneyId, clientId, firmId, staffClassId, timeRange, startDate, endDate, showPeerComparison, peerGroupId]);

  // Transform fetched rate history into chart data using transformHistoryToChartData
  const chartData = useMemo(() => {
    return transformHistoryToChartData(rateHistory, showProposedRates, customColors);
  }, [rateHistory, showProposedRates, customColors]);

  // Calculate and display CAGR (Compound Annual Growth Rate) in the subtitle if available
  const cagr = useMemo(() => {
    if (rateHistory.length < 2) return null;
    const firstRate = rateHistory[0].amount;
    const lastRate = rateHistory[rateHistory.length - 1].amount;
    const years = rateHistory.length - 1;
    return (Math.pow(lastRate / firstRate, 1 / years) - 1) * 100;
  }, [rateHistory]);

  return (
    <ChartContainer width={width} className={className}>
      {/* Display chart header with title and subtitle */}
      <ChartHeader>
        {title && <ChartTitle>{title}</ChartTitle>}
        {subtitle && <ChartSubtitle>
          {subtitle}
          {cagr !== null && ` (CAGR: ${cagr.toFixed(2)}%)`}
        </ChartSubtitle>}
      </ChartHeader>

      {/* Handle loading states with a loading overlay */}
      {loading && <LoadingOverlay>Loading...</LoadingOverlay>}

      {/* Handle error states with an error message */}
      {error && <ErrorMessage>{error}</ErrorMessage>}

      {/* Render LineChart component with formatted data */}
      {!loading && !error && chartData.labels.length > 0 && (
        <LineChart
          data={chartData.datasets}
          labels={chartData.labels}
          options={{}}
          height={height}
          showLegend={showLegend}
          onPointClick={onPointClick}
          isCurrency={isCurrency}
        />
      )}
    </ChartContainer>
  );
};

export default RateTrendChart;