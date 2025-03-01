import React, { useState, useEffect, useMemo } from 'react'; // React v18.0+
import { Bar } from 'react-chartjs-2'; // react-chartjs-2 v4.0+
import { Chart, registerables } from 'chart.js'; // chart.js v3.9+
import { useTheme } from '../../context/ThemeContext'; // internal import
import { formatCurrency } from '../../utils/currency'; // internal import
import { calculatePercentChange } from '../../utils/calculations'; // internal import
import { RateImpactData } from '../../types/analytics'; // internal import

Chart.register(...registerables);

interface RateImpactChartProps {
  data: RateImpactData[];
  groupBy: string;
  currency: string;
  height?: number;
  showGrid?: boolean;
  chartTitle?: string;
}

/**
 * Component that renders a bar chart showing the financial impact of rate changes
 * @param {object} props
 * @returns {JSX.Element} Rendered chart component
 */
const RateImpactChart: React.FC<RateImpactChartProps> = ({
  data,
  groupBy,
  currency,
  height = 300,
  showGrid = true,
  chartTitle
}) => {
  // Access theme colors using useTheme hook
  const { theme } = useTheme();

  // Set up state for chart data and options
  const [chartData, setChartData] = useState(null);
  const [chartOptions, setChartOptions] = useState(null);

  // Process the input data based on groupBy parameter
  useEffect(() => {
    if (data && data.length > 0) {
      const preparedData = prepareChartData(data, groupBy, theme, currency);
      setChartData(preparedData);

      const preparedOptions = prepareChartOptions(currency, theme, showGrid, chartTitle);
      setChartOptions(preparedOptions);
    }
  }, [data, groupBy, theme, currency, showGrid, chartTitle]);

  // Render the Bar component with the prepared data and options
  if (!chartData || !chartOptions) {
    return <div>Loading...</div>;
  }

  if (data.length === 0) {
    return <div>No data available.</div>;
  }

  return (
    <Bar data={chartData} options={chartOptions} height={height} />
  );
};

/**
 * Processes raw rate data into a format suitable for Chart.js
 * @param {RateImpactData[]} data
 * @param {string} groupBy
 * @param {object} theme
 * @param {string} currency
 * @returns {object} Formatted chart data for Chart.js
 */
const prepareChartData = (
  data: RateImpactData[],
  groupBy: string,
  theme: any,
  currency: string
) => {
  // Group the data based on the groupBy parameter (firm, staffClass, practice)
  const groupedData: { [key: string]: RateImpactData } = {};

  data.forEach((item) => {
    const key = item[groupBy as keyof RateImpactData] as string;
    if (!groupedData[key]) {
      groupedData[key] = {
        [groupBy]: key,
        currentRate: 0,
        proposedRate: 0,
        impact: 0,
        percentageChange: 0,
      } as RateImpactData;
    }

    groupedData[key].currentRate += item.currentRate;
    groupedData[key].proposedRate += item.proposedRate;
    groupedData[key].impact += item.impact;
  });

  // Create labels based on the grouped entities
  const labels = Object.keys(groupedData);

  // Create three datasets: current rates, proposed rates, and impact difference
  const datasets = [
    {
      label: 'Current Rates',
      data: labels.map((label) => groupedData[label].currentRate),
      backgroundColor: theme.palette.primary.main,
    },
    {
      label: 'Proposed Rates',
      data: labels.map((label) => groupedData[label].proposedRate),
      backgroundColor: theme.palette.secondary.main,
    },
    {
      label: 'Impact Difference',
      data: labels.map((label) => groupedData[label].impact),
      backgroundColor: theme.palette.accent.main,
    },
  ];

  // Format all currency values with proper currency symbol
  const formattedDatasets = datasets.map((dataset) => ({
    ...dataset,
    data: dataset.data.map((value) => formatCurrency(value, currency)),
  }));

  return {
    labels: labels,
    datasets: formattedDatasets,
  };
};

/**
 * Creates Chart.js options configuration for the rate impact chart
 * @param {string} currency
 * @param {object} theme
 * @param {boolean} showGrid
 * @param {string} chartTitle
 * @returns {object} Chart.js options configuration
 */
const prepareChartOptions = (
  currency: string,
  theme: any,
  showGrid: boolean,
  chartTitle: string | undefined
) => {
  return {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'bottom' as const,
        labels: {
          color: theme.palette.text.primary,
        },
      },
      title: {
        display: !!chartTitle,
        text: chartTitle || '',
        color: theme.palette.text.primary,
        font: {
          size: 18,
        },
      },
      tooltip: {
        callbacks: {
          label: (context: any) => {
            const datasetLabel = context.dataset.label || '';
            const value = context.dataset.data[context.dataIndex] as number;
            const label = context.label || '';
            const formattedValue = formatCurrency(value, currency);
            return `${datasetLabel}: ${formattedValue}`;
          },
          footer: (context: any) => {
            if (context.length > 1) {
              const currentRate = context[0].dataset.data[context[0].dataIndex] as number;
              const proposedRate = context[1].dataset.data[context[1].dataIndex] as number;
              const percentageChange = calculatePercentChange(currentRate, proposedRate);
              return `Change: ${percentageChange.toFixed(2)}%`;
            }
            return null;
          },
        },
        backgroundColor: theme.palette.background.paper,
        titleColor: theme.palette.text.primary,
        bodyColor: theme.palette.text.secondary,
        footerColor: theme.palette.text.primary,
        borderColor: theme.palette.divider,
        borderWidth: 1,
      },
    },
    scales: {
      x: {
        stacked: true,
        ticks: {
          color: theme.palette.text.secondary,
        },
        grid: {
          display: showGrid,
          color: theme.palette.divider,
        },
      },
      y: {
        stacked: true,
        ticks: {
          color: theme.palette.text.secondary,
          callback: (value: number) => formatCurrency(value, currency),
        },
        grid: {
          display: showGrid,
          color: theme.palette.divider,
        },
      },
    },
  };
};

export default RateImpactChart;