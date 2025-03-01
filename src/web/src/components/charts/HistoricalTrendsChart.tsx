import React, { useRef, useEffect, useState } from 'react';
import Chart from 'chart.js/auto';
import { 
  CategoryScale, 
  LinearScale, 
  PointElement, 
  LineElement, 
  BarElement, 
  Title, 
  Tooltip, 
  Legend 
} from 'chart.js';
import { useTheme } from '../../context/ThemeContext';
import { formatPercentage } from '../../utils/formatting';
import { formatCurrency } from '../../utils/currency';

// Register Chart.js components
Chart.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend
);

/**
 * Interface defining the props for the HistoricalTrendsChart component
 */
interface HistoricalTrendsChartProps {
  /** Array of historical rate data points with year and value properties */
  data: Array<{year: number, value: number}>;
  /** Type of view to display ('rateIncreases' or 'absoluteRates') */
  viewType?: 'rateIncreases' | 'absoluteRates';
  /** Optional height of the chart in pixels */
  height?: number;
  /** Optional width of the chart (can be pixels or percentage) */
  width?: string | number;
  /** Optional boolean to show/hide metrics section */
  showMetrics?: boolean;
  /** Optional current inflation rate for comparison */
  inflationRate?: number;
  /** Optional additional CSS class names */
  className?: string;
}

/**
 * Calculates the Compound Annual Growth Rate (CAGR) based on an array of rate values
 * 
 * @param data - Array of historical rate data points
 * @returns The calculated CAGR as a decimal
 */
const calculateCAGR = (data: Array<{year: number, value: number}>): number => {
  if (!data || data.length < 2) {
    return 0;
  }

  // Sort data by year in ascending order
  const sortedData = [...data].sort((a, b) => a.year - b.year);
  
  // Get start and end values
  const startValue = sortedData[0].value;
  const endValue = sortedData[sortedData.length - 1].value;
  
  // Calculate number of years
  const years = sortedData[sortedData.length - 1].year - sortedData[0].year;
  
  if (years <= 0 || startValue <= 0) {
    return 0;
  }
  
  // Calculate CAGR: (endValue / startValue)^(1/years) - 1
  const cagr = Math.pow(endValue / startValue, 1 / years) - 1;
  
  return cagr;
};

/**
 * A React component that renders a chart visualizing historical rate trends
 * over multiple years with additional analytical metrics like CAGR and
 * comparison to inflation.
 * 
 * @param props - Component props
 * @returns Rendered chart component
 */
const HistoricalTrendsChart: React.FC<HistoricalTrendsChartProps> = ({
  data,
  viewType = 'rateIncreases',
  height = 300,
  width = '100%',
  showMetrics = true,
  inflationRate = 0.032, // Default inflation rate (3.2%)
  className = ''
}) => {
  const chartRef = useRef<HTMLCanvasElement | null>(null);
  const [chartInstance, setChartInstance] = useState<Chart | null>(null);
  const [metrics, setMetrics] = useState({
    cagr: 0,
    inflation: inflationRate,
    difference: 0
  });
  
  // Get theme colors for consistent styling
  const { theme } = useTheme();
  
  // Calculate CAGR and metrics when data changes
  useEffect(() => {
    if (data && data.length >= 2) {
      const calculatedCagr = calculateCAGR(data);
      const difference = calculatedCagr - inflationRate;
      
      setMetrics({
        cagr: calculatedCagr,
        inflation: inflationRate,
        difference
      });
    }
  }, [data, inflationRate]);
  
  // Initialize and update chart when data or viewType changes
  useEffect(() => {
    if (chartRef.current && data && data.length > 0) {
      // Destroy existing chart instance if it exists
      if (chartInstance) {
        chartInstance.destroy();
      }
      
      // Sort data by year for proper chronological display
      const sortedData = [...data].sort((a, b) => a.year - b.year);
      const years = sortedData.map(item => item.year.toString());
      
      // Create datasets based on viewType
      let chartData;
      let chartOptions;
      
      if (viewType === 'rateIncreases') {
        // For rate increases, calculate year-over-year percentage changes
        const percentChanges = sortedData.map((item, index) => {
          if (index === 0) return { year: item.year, value: 0 };
          const prevValue = sortedData[index - 1].value;
          const percentChange = prevValue > 0 ? (item.value - prevValue) / prevValue : 0;
          return { year: item.year, value: percentChange };
        }).slice(1); // Remove the first item (which has no previous value to compare)
        
        chartData = {
          labels: percentChanges.map(item => item.year.toString()),
          datasets: [
            {
              label: 'Rate Increases',
              data: percentChanges.map(item => item.value * 100), // Convert to percentage
              backgroundColor: theme.palette.primary.main,
              borderColor: theme.palette.primary.main,
              borderWidth: 2,
              tension: 0.3,
              fill: false
            },
            {
              label: 'Inflation (CPI)',
              data: new Array(percentChanges.length).fill(inflationRate * 100), // Convert to percentage
              backgroundColor: theme.palette.accent.main,
              borderColor: theme.palette.accent.main,
              borderWidth: 2,
              borderDash: [5, 5],
              tension: 0,
              fill: false
            }
          ]
        };
        
        chartOptions = {
          responsive: true,
          maintainAspectRatio: false,
          scales: {
            y: {
              beginAtZero: true,
              title: {
                display: true,
                text: 'Percentage Increase (%)'
              },
              ticks: {
                callback: (value: number) => `${value.toFixed(1)}%`
              }
            },
            x: {
              title: {
                display: true,
                text: 'Year'
              }
            }
          },
          plugins: {
            tooltip: {
              callbacks: {
                label: (context: any) => {
                  const value = context.raw;
                  return `${context.dataset.label}: ${formatPercentage(value / 100)}`;
                }
              }
            },
            legend: {
              position: 'top'
            }
          }
        };
      } else {
        // For absolute rates, show the actual rate values
        chartData = {
          labels: years,
          datasets: [
            {
              label: 'Rate Value',
              data: sortedData.map(item => item.value),
              backgroundColor: theme.palette.primary.main,
              borderColor: theme.palette.primary.main,
              borderWidth: 2,
              tension: 0.3,
              fill: false
            }
          ]
        };
        
        chartOptions = {
          responsive: true,
          maintainAspectRatio: false,
          scales: {
            y: {
              beginAtZero: false,
              title: {
                display: true,
                text: 'Rate Amount'
              },
              ticks: {
                callback: (value: number) => formatCurrency(value, 'USD', { includeSymbol: true })
              }
            },
            x: {
              title: {
                display: true,
                text: 'Year'
              }
            }
          },
          plugins: {
            tooltip: {
              callbacks: {
                label: (context: any) => {
                  const value = context.raw;
                  return `${context.dataset.label}: ${formatCurrency(value, 'USD', { includeSymbol: true })}`;
                }
              }
            },
            legend: {
              position: 'top'
            }
          }
        };
      }
      
      // Create chart instance
      const newChartInstance = new Chart(chartRef.current, {
        type: viewType === 'rateIncreases' ? 'line' : 'bar',
        data: chartData,
        options: chartOptions
      });
      
      // Store chart instance in state
      setChartInstance(newChartInstance);
      
      // Clean up function to destroy chart on unmount
      return () => {
        if (newChartInstance) {
          newChartInstance.destroy();
        }
      };
    }
  }, [data, viewType, theme, inflationRate]);
  
  return (
    <div className={`historical-trends-chart ${className}`} style={{ width }}>
      <div style={{ height, width: '100%' }}>
        <canvas ref={chartRef}></canvas>
      </div>
      
      {showMetrics && data && data.length >= 2 && (
        <div className="metrics-container" style={{ 
          marginTop: '16px', 
          padding: '12px', 
          backgroundColor: theme.palette.background.light,
          borderRadius: '4px',
          display: 'flex',
          justifyContent: 'space-around',
          flexWrap: 'wrap'
        }}>
          <div className="metric">
            <span className="metric-label">5-Year CAGR: </span>
            <span className="metric-value" style={{ 
              fontWeight: 500, 
              color: metrics.cagr > 0 ? theme.palette.success.main : theme.palette.error.main 
            }}>
              {formatPercentage(metrics.cagr)}
            </span>
          </div>
          
          <div className="metric">
            <span className="metric-label">Inflation (CPI): </span>
            <span className="metric-value">{formatPercentage(metrics.inflation)}</span>
          </div>
          
          <div className="metric">
            <span className="metric-label">Difference: </span>
            <span className="metric-value" style={{ 
              fontWeight: 500, 
              color: metrics.difference > 0 ? theme.palette.success.main : theme.palette.error.main 
            }}>
              {formatPercentage(metrics.difference)}
            </span>
          </div>
        </div>
      )}
    </div>
  );
};

export default HistoricalTrendsChart;