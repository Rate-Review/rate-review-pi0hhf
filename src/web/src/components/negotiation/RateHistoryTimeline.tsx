import React, { useState, useEffect, useMemo } from 'react'; //  ^18.0.0
import { formatDate, formatDisplayDate } from '../../utils/date';
import { formatCurrency } from '../../utils/currency';
import useRates from '../../hooks/useRates';
import { LineChart } from '../charts/LineChart';
import { Card } from '../common/Card';
import { Skeleton } from '../common/Skeleton';
import { RateHistoryItem } from '../../types/rate';
import { StatusIndicator } from '../common/StatusIndicator';

/**
 * @interface RateHistoryTimelineProps
 * @description Interface defining the props for the RateHistoryTimeline component
 */
interface RateHistoryTimelineProps {
  attorneyId?: string;
  staffClassId?: string;
  showChart?: boolean;
  onRateClick?: (rateId: string) => void;
}

/**
 * @function formatTimelineData
 * @description Helper function to format rate history data for the timeline visualization
 * @param {RateHistoryItem[]} rateHistory - Rate history data
 * @returns {object} Formatted timeline data for visualization
 */
const formatTimelineData = (rateHistory: RateHistoryItem[]) => {
  // LD1: Sort rate history items by date in ascending order
  const sortedHistory = [...rateHistory].sort((a, b) => new Date(a.timestamp).getTime() - new Date(b.timestamp).getTime());

  // LD1: Format each rate item with proper date and currency format
  const formattedHistory = sortedHistory.map((item, index, array) => {
    const amount = parseFloat(item.amount.toString());
    const formattedAmount = formatCurrency(amount, item.currency);
    const formattedDate = formatDisplayDate(item.timestamp);
    let percentageChange = 0;

    // LD1: Calculate rate change percentages between consecutive rates
    if (index > 0) {
      const previousAmount = parseFloat(array[index - 1].amount.toString());
      percentageChange = ((amount - previousAmount) / previousAmount) * 100;
    }

    return {
      ...item,
      amount: formattedAmount,
      effectiveDate: formattedDate,
      percentageChange: percentageChange.toFixed(2),
    };
  });

  return formattedHistory;
};

/**
 * @function RateHistoryTimeline
 * @description A functional component that displays the history of rate changes for an attorney or staff class in a timeline format
 * @param {object} props - Component props
 * @returns {JSX.Element} The rendered component
 */
const RateHistoryTimeline: React.FC<RateHistoryTimelineProps> = ({
  attorneyId,
  staffClassId,
  showChart = true,
  onRateClick,
}) => {
  // LD1: Use useState hook to manage loading state and error state
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // LD1: Use useState hook to store rate history data
  const [rateHistory, setRateHistory] = useState<any[]>([]);

  // LD1: Use useRates hook to fetch rate history data when attorneyId or staffClassId changes
  const { loadRates } = useRates();

  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      setError(null);
      try {
        const filters: any = {};
        if (attorneyId) filters.attorneyId = attorneyId;
        if (staffClassId) filters.staffClassId = staffClassId;
        const data = await loadRates(filters);
        setRateHistory(data);
      } catch (e: any) {
        setError(e.message);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [attorneyId, staffClassId, loadRates]);

  // LD1: Use useMemo to process rate history data into a format suitable for the timeline and chart
  const timelineData = useMemo(() => {
    return formatTimelineData(rateHistory);
  }, [rateHistory]);

  // LD1: Format data points for the line chart with proper date formatting and currency formatting
  const chartData = useMemo(() => {
    return [
      {
        label: 'Rate',
        data: timelineData.map((item: any) => parseFloat(item.amount.replace(/[^0-9.-]+/g, ''))),
        borderColor: theme.palette.primary.main,
        backgroundColor: theme.palette.primary.light,
        borderWidth: 2,
        fill: true,
        tension: 0.4,
      },
    ];
  }, [timelineData]);

  const chartLabels = useMemo(() => {
    return timelineData.map((item: any) => formatDate(item.effectiveDate, 'MMM yyyy'));
  }, [timelineData]);

  // LD1: Handle loading state with Skeleton component
  if (loading) {
    return (
      <Card>
        <Skeleton height="300px" />
      </Card>
    );
  }

  // LD1: Handle error state with an error message
  if (error) {
    return <Card>Error: {error}</Card>;
  }

  return (
    <Card>
      {timelineData.map((item: any) => (
        <div key={item.id}>
          <StatusIndicator status={item.status} />
          <span>{item.amount}</span>
          <span>{item.effectiveDate}</span>
          <span>{item.percentageChange}%</span>
        </div>
      ))}

      {showChart && (
        <LineChart
          data={chartData}
          labels={chartLabels}
          title="Rate History"
          xAxisTitle="Date"
          yAxisTitle="Rate"
        />
      )}
    </Card>
  );
};

export default RateHistoryTimeline;