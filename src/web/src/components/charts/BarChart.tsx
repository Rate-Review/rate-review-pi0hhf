/**
 * BarChart Component
 *
 * A customizable bar chart component using Chart.js for visualizing comparative data
 * in the Justice Bid Rate Negotiation System. Provides a visually appealing way to
 * display rate impact analysis, peer comparisons, and other bar-based visualizations
 * with consistent styling throughout the application.
 *
 * Requirements Addressed:
 *   - Rate Analytics Dashboard (F-004)
 *   - Rate Impact Analysis (F-025)
 *   - Peer Group Configuration (F-009)
 *
 * @version 1.0.0
 */

import React, { useRef, useEffect, useState, useMemo } from 'react'; // React v18.0.0
import {
  Chart,
  BarController,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
  ChartData,
  ChartOptions,
} from 'chart.js'; // chart.js v4.0.0
import styled from 'styled-components'; // styled-components v5.3.6
import {
  createBarChartConfig,
} from '../../utils/charts';
import { ChartDataPoint, ChartDataSeries } from '../../types/common';
import Skeleton from '../common/Skeleton';
import colors from '../../theme/colors';

// Register required Chart.js components
Chart.register(
  BarController,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend
);

/**
 * Interface defining the props for the BarChart component
 */
export interface BarChartProps {
  data: ChartData | ChartDataSeries[] | ChartDataPoint[];
  options?: object;
  height?: string | number;
  width?: string | number;
  loading?: boolean;
  dataType?: string;
  stacked?: boolean;
  horizontal?: boolean;
  title?: string;
  className?: string;
  onBarClick?: (event: any) => void;
}

/**
 * Styled component for chart container with responsive sizing
 */
interface ContainerProps {
  width?: string | number;
  height?: string | number;
  maxHeight?: string;
}

const ChartContainer = styled.div<ContainerProps>`
  width: ${props => props.width || '100%'};
  height: ${props => props.height || 'auto'};
  max-height: ${props => props.maxHeight || 'none'};
  position: relative;
  display: flex;
`;

/**
 * A customizable bar chart component using Chart.js
 *
 * @param {BarChartProps} props - Component props
 * @returns {ReactNode} Rendered bar chart component
 */
const BarChart: React.FC<BarChartProps> = (props) => {
  // 1. Initialize a reference to the canvas element using useRef
  const chartRef = useRef<HTMLCanvasElement>(null);
  // 2. Create state for tracking chart instance and loading state
  const [chartInstance, setChartInstance] = useState<Chart | null>(null);
  // 3. Use useMemo to prepare chart data and options based on props
  const { data, options, height, width, loading, dataType, stacked, horizontal, title, className, onBarClick } = props;

  const chartConfig = useMemo(() => {
    if (!data) return null;

    const chartData = data as ChartData;
    const barChartConfig = createBarChartConfig(chartData, options);
    return barChartConfig;
  }, [data, options]);

  // 4. Use useEffect to initialize Chart.js and register required components when the component mounts
  useEffect(() => {
    if (!chartRef.current || !chartConfig) return;

    // 5. Use useEffect to initialize the chart instance with the configured options
    const initializeChart = () => {
      const ctx = chartRef.current!.getContext('2d');
      if (!ctx) return;

      const newChartInstance = new Chart(ctx, chartConfig);
      setChartInstance(newChartInstance);

      if (onBarClick) {
        chartRef.current.onclick = (evt: any) => {
          const points = newChartInstance.getElementsAtEventForMode(evt, 'nearest', { intersect: true }, true);
          if (points.length) {
            onBarClick(points[0]);
          }
        };
      }
    };

    initializeChart();

    // 6. Use useEffect to update chart when data or options change
    // 7. Use useEffect to handle component cleanup by destroying chart instance on unmount
    return () => {
      if (chartInstance) {
        chartInstance.destroy();
        setChartInstance(null);
      }
    };
  }, [chartConfig, onBarClick]);

  // 8. Render a loading skeleton if data is not yet available or loading state is true
  if (loading) {
    return (
      <ChartContainer width={width} height={height} className={className}>
        <Skeleton width="100%" height="100%" />
      </ChartContainer>
    );
  }

  // 9. Render the canvas element with appropriate dimensions, accessibility attributes, and event handlers
  return (
    // 10. Apply responsive container styling to ensure proper chart display
    <ChartContainer width={width} height={height} className={className}>
      <canvas
        ref={chartRef}
        width={width}
        height={height}
        aria-label={title}
        role="img"
      />
    </ChartContainer>
  );
};

export default BarChart;