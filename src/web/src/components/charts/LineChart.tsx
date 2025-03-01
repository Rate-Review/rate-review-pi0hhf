import React, { useRef, useEffect } from 'react';
import styled from 'styled-components';
import { Chart as ChartJS, CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend, ChartOptions } from 'chart.js';
import { Line } from 'react-chartjs-2';
import { colors, spacing } from '../../../theme';

// Props interface for the LineChart component
interface LineChartProps {
  data: Array<{label: string, data: number[], borderColor?: string, backgroundColor?: string, borderWidth?: number, fill?: boolean, tension?: number}>;
  labels: string[];
  options?: object;
  title?: string;
  height?: number;
  showLegend?: boolean;
  colors?: string[];
  onPointClick?: (index: number, datasetIndex: number) => void;
  tooltipFormat?: string;
  xAxisTitle?: string;
  yAxisTitle?: string;
  isCurrency?: boolean;
}

// Styled components for the chart
const ChartContainer = styled.div`
  width: 100%;
  position: relative;
  margin-bottom: ${props => props.theme.spacing.md}px;
  height: ${props => props.height || 300}px;
`;

const ChartTitle = styled.h4`
  text-align: center;
  margin-bottom: ${props => props.theme.spacing.sm}px;
  color: ${props => props.theme.colors.primary};
`;

const LegendContainer = styled.div`
  display: flex;
  justify-content: center;
  flex-wrap: wrap;
  margin-top: ${props => props.theme.spacing.sm}px;
`;

const LegendItem = styled.div`
  display: flex;
  align-items: center;
  margin: 0 ${props => props.theme.spacing.sm}px;
  font-size: 14px;
`;

const LegendColor = styled.div<{ color: string }>`
  width: 12px;
  height: 12px;
  margin-right: ${props => props.theme.spacing.xs}px;
  background-color: ${props => props.color};
  border-radius: 2px;
`;

/**
 * Formats the tooltip displayed when hovering over chart points
 * 
 * @param tooltipItem - The tooltip item data
 * @param isCurrency - Whether to format the value as currency
 * @returns Formatted tooltip text
 */
function formatTooltip(tooltipItem: any, isCurrency: boolean): string {
  const label = tooltipItem.dataset.label || '';
  let value = tooltipItem.formattedValue;
  
  if (isCurrency) {
    value = new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(Number(value));
  }
  
  return `${label}: ${value}`;
}

/**
 * Creates the chart configuration using the provided props
 * 
 * @param props - The LineChart component props
 * @returns Chart configuration object
 */
function createChartConfig(props: LineChartProps): object {
  const { labels, data, colors: customColors, onPointClick, tooltipFormat, xAxisTitle, yAxisTitle, isCurrency } = props;
  
  // Default colors if none provided
  const defaultColors = [
    '#2C5282', // Primary color (deep blue)
    '#38A169', // Secondary color (green)
    '#DD6B20', // Accent color (orange)
    '#718096', // Neutral color (slate)
    '#3182CE', // Info color (blue)
    '#E53E3E', // Error color (red)
    '#DD6B20', // Warning color (orange)
  ];
  
  // Apply colors to datasets if not explicitly defined
  const datasets = data.map((dataset, index) => ({
    ...dataset,
    borderColor: dataset.borderColor || customColors?.[index] || defaultColors[index % defaultColors.length],
    backgroundColor: dataset.backgroundColor || 
      (customColors?.[index] ? `${customColors[index]}33` : `${defaultColors[index % defaultColors.length]}33`),
    borderWidth: dataset.borderWidth || 2,
    fill: dataset.fill !== undefined ? dataset.fill : false,
    tension: dataset.tension !== undefined ? dataset.tension : 0.4,
  }));
  
  return {
    data: {
      labels,
      datasets,
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          display: false, // We'll implement a custom legend
        },
        tooltip: {
          callbacks: {
            label: (tooltipItem: any) => formatTooltip(tooltipItem, !!isCurrency),
            // Use tooltipFormat if provided
            ...(tooltipFormat && {
              title: (tooltipItems: any) => {
                return tooltipFormat.replace('{x}', tooltipItems[0].label);
              },
            }),
          },
        },
      },
      scales: {
        x: {
          grid: {
            color: 'rgba(0, 0, 0, 0.05)',
          },
          title: xAxisTitle ? {
            display: true,
            text: xAxisTitle,
            font: {
              size: 14,
            },
          } : undefined,
        },
        y: {
          grid: {
            color: 'rgba(0, 0, 0, 0.05)',
          },
          title: yAxisTitle ? {
            display: true,
            text: yAxisTitle,
            font: {
              size: 14,
            },
          } : undefined,
          ticks: {
            // Format Y-axis labels as currency if needed
            ...(isCurrency && {
              callback: (value: any) => {
                return new Intl.NumberFormat('en-US', { 
                  style: 'currency', 
                  currency: 'USD',
                  maximumFractionDigits: 0,
                }).format(value);
              },
            }),
          },
        },
      },
      onClick: onPointClick ? (_, elements) => {
        if (elements.length > 0) {
          const { datasetIndex, index } = elements[0];
          onPointClick(index, datasetIndex);
        }
      } : undefined,
      ...props.options,
    },
  };
}

/**
 * Renders a custom legend for the chart
 * 
 * @param datasets - Array of dataset objects containing label and color information
 * @returns JSX.Element - Legend component with color indicators
 */
function renderLegend(datasets: Array<{label: string, borderColor: string}>): JSX.Element {
  return (
    <LegendContainer>
      {datasets.map((dataset, index) => (
        <LegendItem key={index}>
          <LegendColor color={dataset.borderColor} />
          <span>{dataset.label}</span>
        </LegendItem>
      ))}
    </LegendContainer>
  );
}

/**
 * A reusable line chart component using Chart.js
 * 
 * This component visualizes trend data such as historical rate changes,
 * impact analysis, and other time-series data throughout the Justice Bid system.
 * It supports customization of colors, labels, and interaction handling.
 * 
 * @param props - Component props including data, labels, and customization options
 * @returns JSX.Element - Rendered line chart component
 */
const LineChart: React.FC<LineChartProps> = (props) => {
  const chartRef = useRef<ChartJS>(null);
  
  // Register required Chart.js plugins
  ChartJS.register(
    CategoryScale,
    LinearScale,
    PointElement,
    LineElement,
    Title,
    Tooltip,
    Legend
  );
  
  const { title, showLegend = true, height = 300 } = props;
  const chartConfig = createChartConfig(props);
  
  // Clean up chart instance on unmount
  useEffect(() => {
    return () => {
      if (chartRef.current) {
        chartRef.current.destroy();
      }
    };
  }, []);
  
  return (
    <>
      <ChartContainer height={height}>
        {title && <ChartTitle>{title}</ChartTitle>}
        <Line
          ref={chartRef}
          data={(chartConfig as any).data}
          options={(chartConfig as any).options}
        />
      </ChartContainer>
      {showLegend && renderLegend(props.data)}
    </>
  );
};

export default LineChart;