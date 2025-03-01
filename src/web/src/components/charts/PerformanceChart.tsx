/**
 * PerformanceChart Component
 * 
 * A React component that visualizes attorney performance metrics using Chart.js,
 * displaying data from UniCourt API and internal billing systems. It supports 
 * multiple visualization types with radar charts as the primary view for 
 * multi-dimensional performance data.
 * 
 * @version 1.0.0
 */

import React from 'react';
import { 
  Chart, 
  register,
  RadarController,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  RadialLinearScale,
  Tooltip,
  Legend
} from 'chart.js';
import { Radar, Bar } from 'react-chartjs-2';
import { useTheme } from '@mui/material';
import { AttorneyPerformance } from '../../../types/analytics';
import { formatNumber } from '../../../utils/formatting';
import Skeleton from '../../common/Skeleton';
import EmptyState from '../../common/EmptyState';

// Register Chart.js components required for the charts
register(
  RadarController,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  RadialLinearScale,
  Tooltip,
  Legend
);

/**
 * Props interface for the PerformanceChart component
 */
interface PerformanceChartProps {
  /** Performance data for one or more attorneys */
  performanceData: AttorneyPerformance | AttorneyPerformance[];
  /** Loading state indicator */
  isLoading?: boolean;
  /** Type of chart to display */
  chartType?: 'radar' | 'bar';
  /** Optional CSS class */
  className?: string;
  /** Chart height (string or number) */
  height?: string | number;
  /** Specific metric to visualize (for bar charts) */
  metricType?: string;
  /** Optional click handler for chart interactions */
  onChartClick?: (event: any, elements: any) => void;
}

/**
 * Transforms attorney performance data into the format required by Chart.js for radar charts
 * 
 * @param performanceData - Attorney performance data to visualize
 * @param colors - Theme colors for chart styling
 * @returns Formatted data object ready for Chart.js radar chart
 */
const generateRadarChartData = (
  performanceData: AttorneyPerformance | AttorneyPerformance[],
  colors: any
) => {
  const datasets = [];
  const performanceArray = Array.isArray(performanceData) ? performanceData : [performanceData];
  
  // Define consistent labels for the radar chart axes
  const labels = [
    'Win Rate',
    'Case Load',
    'Client Satisfaction',
    'Efficiency',
    'Court Experience',
    'Timeliness'
  ];
  
  // Create datasets for each attorney
  performanceArray.forEach((attorney, index) => {
    // Create color schemes for different attorneys
    const color = index === 0 ? colors.primary.main : 
                index === 1 ? colors.secondary.main : 
                index === 2 ? colors.accent.main : 
                colors.info.main;
    
    const backgroundColor = `${color}33`; // 20% opacity
    const borderColor = color;
    
    datasets.push({
      label: attorney.attorneyName,
      data: [
        // Normalize all values to a 0-100 scale
        attorney.winRate * 100, // Convert from decimal to percentage
        Math.min(attorney.caseLoad / 10 * 100, 100), // Normalize caseload
        attorney.clientSatisfaction,
        attorney.efficiency,
        attorney.courtExperience,
        attorney.timelinessScore
      ],
      backgroundColor,
      borderColor,
      borderWidth: 2,
      pointBackgroundColor: borderColor,
      pointBorderColor: '#fff',
      pointHoverBackgroundColor: '#fff',
      pointHoverBorderColor: borderColor,
      pointLabelFontSize: 14
    });
  });
  
  return {
    labels,
    datasets
  };
};

/**
 * Transforms attorney performance data into the format required by Chart.js for bar charts
 * 
 * @param performanceData - Attorney performance data to visualize
 * @param colors - Theme colors for chart styling
 * @param metricType - Specific metric to display in the bar chart
 * @returns Formatted data object ready for Chart.js bar chart
 */
const generateBarChartData = (
  performanceData: AttorneyPerformance | AttorneyPerformance[],
  colors: any,
  metricType: string
) => {
  const performanceArray = Array.isArray(performanceData) ? performanceData : [performanceData];
  const labels = performanceArray.map(attorney => attorney.attorneyName);
  const datasets = [];
  
  // Determine which metric to display based on the metricType parameter
  let dataPoints;
  let label;
  
  switch (metricType) {
    case 'winRate':
      dataPoints = performanceArray.map(attorney => attorney.winRate * 100);
      label = 'Win Rate (%)';
      break;
    case 'caseLoad':
      dataPoints = performanceArray.map(attorney => attorney.caseLoad);
      label = 'Case Load';
      break;
    case 'clientSatisfaction':
      dataPoints = performanceArray.map(attorney => attorney.clientSatisfaction);
      label = 'Client Satisfaction';
      break;
    case 'efficiency':
      dataPoints = performanceArray.map(attorney => attorney.efficiency);
      label = 'Efficiency';
      break;
    case 'courtExperience':
      dataPoints = performanceArray.map(attorney => attorney.courtExperience);
      label = 'Court Experience';
      break;
    case 'timelinessScore':
      dataPoints = performanceArray.map(attorney => attorney.timelinessScore);
      label = 'Timeliness';
      break;
    default:
      // Default to overall performance percentile
      dataPoints = performanceArray.map(attorney => 
        parseFloat(attorney.performancePercentile || '0'));
      label = 'Overall Performance';
  }
  
  // Create a single dataset for the bar chart
  datasets.push({
    label,
    data: dataPoints,
    backgroundColor: performanceArray.map((_, index) => {
      const color = index === 0 ? colors.primary.main : 
                  index === 1 ? colors.secondary.main : 
                  index === 2 ? colors.accent.main : 
                  colors.info.main;
      return color;
    }),
    borderColor: 'transparent',
    borderWidth: 1,
    borderRadius: 4
  });
  
  return {
    labels,
    datasets
  };
};

/**
 * Generates Chart.js options for radar chart configuration
 * 
 * @param theme - Theme object for styling
 * @returns Chart.js options object
 */
const getRadarChartOptions = (theme: any) => {
  return {
    scales: {
      r: {
        min: 0,
        max: 100,
        ticks: {
          backdropColor: 'transparent',
          color: theme.palette.text.secondary,
          showLabelBackdrop: false,
          font: {
            size: 11
          }
        },
        pointLabels: {
          color: theme.palette.text.primary,
          font: {
            size: 12,
            family: theme.typography.fontFamily
          }
        },
        angleLines: {
          color: theme.palette.divider
        },
        grid: {
          color: theme.palette.divider
        }
      }
    },
    plugins: {
      legend: {
        position: 'bottom',
        labels: {
          usePointStyle: true,
          color: theme.palette.text.primary,
          font: {
            family: theme.typography.fontFamily,
            size: 12
          },
          padding: 15
        }
      },
      tooltip: {
        backgroundColor: theme.palette.background.paper,
        borderColor: theme.palette.divider,
        borderWidth: 1,
        titleColor: theme.palette.text.primary,
        bodyColor: theme.palette.text.secondary,
        titleFont: {
          size: 14,
          family: theme.typography.fontFamily,
          weight: 'bold'
        },
        bodyFont: {
          size: 13,
          family: theme.typography.fontFamily
        },
        padding: 10,
        boxPadding: 5,
        callbacks: {
          label: function(context: any) {
            let label = context.dataset.label || '';
            if (label) {
              label += ': ';
            }
            label += formatNumber(context.raw as number, { decimalPlaces: 1 });
            return label;
          }
        }
      }
    },
    maintainAspectRatio: false,
    responsive: true,
    devicePixelRatio: 2
  };
};

/**
 * Generates Chart.js options for bar chart configuration
 * 
 * @param theme - Theme object for styling
 * @param metricType - Specific metric being displayed
 * @returns Chart.js options object
 */
const getBarChartOptions = (theme: any, metricType: string) => {
  // Determine if the metric is a percentage
  const isPercentage = metricType === 'winRate' || 
                      metricType === 'clientSatisfaction' ||
                      metricType === 'efficiency' ||
                      metricType === 'timelinessScore';
  
  return {
    scales: {
      y: {
        beginAtZero: true,
        max: isPercentage ? 100 : undefined,
        grid: {
          color: theme.palette.divider
        },
        ticks: {
          color: theme.palette.text.secondary,
          font: {
            size: 11,
            family: theme.typography.fontFamily
          },
          callback: function(value: any) {
            return isPercentage ? `${value}%` : value;
          }
        }
      },
      x: {
        grid: {
          display: false
        },
        ticks: {
          color: theme.palette.text.secondary,
          font: {
            size: 11,
            family: theme.typography.fontFamily
          }
        }
      }
    },
    plugins: {
      legend: {
        display: false
      },
      tooltip: {
        backgroundColor: theme.palette.background.paper,
        borderColor: theme.palette.divider,
        borderWidth: 1,
        titleColor: theme.palette.text.primary,
        bodyColor: theme.palette.text.secondary,
        titleFont: {
          size: 14,
          family: theme.typography.fontFamily,
          weight: 'bold'
        },
        bodyFont: {
          size: 13,
          family: theme.typography.fontFamily
        },
        padding: 10,
        callbacks: {
          label: function(context: any) {
            let label = context.dataset.label || '';
            if (label) {
              label += ': ';
            }
            if (isPercentage) {
              label += formatNumber(context.raw as number, { decimalPlaces: 1 }) + '%';
            } else {
              label += formatNumber(context.raw as number, { decimalPlaces: 0 });
            }
            return label;
          }
        }
      }
    },
    maintainAspectRatio: false,
    responsive: true,
    devicePixelRatio: 2,
    indexAxis: 'x',
    barThickness: 'flex',
    maxBarThickness: 40
  };
};

/**
 * A component that visualizes attorney performance metrics using radar charts and other visualizations
 * 
 * @param props - Component props
 * @returns Rendered chart component
 */
const PerformanceChart: React.FC<PerformanceChartProps> = ({
  performanceData,
  isLoading = false,
  chartType = 'radar',
  className = '',
  height = 300,
  metricType = 'overall',
  onChartClick
}) => {
  // Get theme for styling
  const theme = useTheme();
  
  // Handle empty data state
  if (!isLoading && (!performanceData || (Array.isArray(performanceData) && performanceData.length === 0))) {
    return (
      <EmptyState
        title="No performance data available"
        message="There is no performance data available for the selected attorney(s)."
        icon={<span role="img" aria-label="No data">📊</span>}
        sx={{ height }}
      />
    );
  }
  
  // Handle loading state
  if (isLoading) {
    return (
      <div style={{ height, width: '100%' }} className={className}>
        <Skeleton height={height} variant="rectangle" />
      </div>
    );
  }
  
  // Generate chart data based on chart type
  const chartData = chartType === 'radar'
    ? generateRadarChartData(performanceData, theme.palette)
    : generateBarChartData(performanceData, theme.palette, metricType);
  
  // Get appropriate chart options
  const chartOptions = chartType === 'radar'
    ? getRadarChartOptions(theme)
    : getBarChartOptions(theme, metricType);
  
  // Add click handler if provided
  if (onChartClick) {
    chartOptions.onClick = onChartClick;
  }
  
  return (
    <div 
      style={{ height: typeof height === 'number' ? `${height}px` : height, width: '100%' }} 
      className={className}
      role="img"
      aria-label={`Performance chart showing ${Array.isArray(performanceData) 
        ? `data for ${performanceData.length} attorneys` 
        : `data for ${performanceData.attorneyName}`}`}
    >
      {chartType === 'radar' ? (
        <Radar data={chartData} options={chartOptions} />
      ) : (
        <Bar data={chartData} options={chartOptions} />
      )}
    </div>
  );
};

export default PerformanceChart;