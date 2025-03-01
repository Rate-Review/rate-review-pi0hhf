import React from 'react';
import { Chart as ChartJS, CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend } from 'chart.js';
import { Bar } from 'react-chartjs-2';
import { PeerComparisonData } from '../../types/analytics';
import { formatPercentage } from '../../utils/formatting';
import { COLORS } from '../../theme/colors';

// Register Chart.js components
ChartJS.register(CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend);

// Default chart options for consistent styling across charts
const chartDefaultOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      display: false,
    },
  },
  scales: {
    y: {
      beginAtZero: true,
      ticks: {
        callback: (value: any) => formatPercentage(Number(value) / 100),
      },
    },
  },
};

interface PeerComparisonChartProps {
  data: PeerComparisonData;
  height?: number;
  showLegend?: boolean;
  highlightFirm?: string;
  title?: string;
}

/**
 * Formats the tooltip content for the chart
 */
const formatTooltip = (tooltipItem: any) => {
  const label = tooltipItem.label;
  const value = tooltipItem.parsed.y;
  return `${label}: ${formatPercentage(value / 100)}`;
};

/**
 * Processes raw peer comparison data into Chart.js compatible format
 */
const processChartData = (data: PeerComparisonData, highlightFirm?: string) => {
  // Extract labels (firm names) from the data
  const labels = data.items.map(item => item.name);
  
  // Extract values (rate increase percentages) from the data
  // Convert decimal values (e.g., 0.045) to percentages (e.g., 4.5)
  const values = data.items.map(item => item.rateIncrease * 100);

  // Create backgroundColor array with highlight color for the specified firm
  const backgroundColor = data.items.map(item => 
    item.name === highlightFirm 
      ? COLORS.accent.main 
      : COLORS.primary.main
  );

  return {
    labels,
    datasets: [
      {
        data: values,
        backgroundColor,
        borderColor: 'transparent',
        borderWidth: 1,
        borderRadius: 4,
        barThickness: 30,
        maxBarThickness: 50,
      },
    ],
  };
};

/**
 * Component that renders a bar chart comparing rate data across peer groups
 */
const PeerComparisonChart: React.FC<PeerComparisonChartProps> = ({
  data,
  height = 300,
  showLegend = false,
  highlightFirm,
  title,
}) => {
  // Process the input data into Chart.js compatible format
  const chartData = processChartData(data, highlightFirm);

  // Set up chart options with custom tooltip formatting
  const options = {
    ...chartDefaultOptions,
    plugins: {
      ...chartDefaultOptions.plugins,
      legend: {
        display: showLegend,
      },
      tooltip: {
        callbacks: {
          label: formatTooltip,
        },
      },
      title: {
        display: !!title,
        text: title || '',
        font: {
          size: 16,
          weight: 'bold',
        },
      },
    },
  };

  return (
    <div style={{ height, position: 'relative' }}>
      <Bar data={chartData} options={options} />
    </div>
  );
};

export default PeerComparisonChart;