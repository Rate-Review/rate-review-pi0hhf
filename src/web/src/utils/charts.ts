/**
 * Utility functions for chart creation, configuration, and data formatting
 * using Chart.js. Provides consistent styling and behavior for all charts
 * in the application with a focus on rate analytics visualizations.
 * 
 * @version 1.0.0
 */

import { Chart, ChartOptions, ChartData, ChartConfiguration } from 'chart.js';
import colors from '../theme/colors';
import { formatCurrency } from './currency';
import { formatPercentage } from './formatting';

/**
 * Returns an array of colors for chart data points based on the current theme
 * 
 * @param count - Number of colors needed
 * @param variant - Color scheme variant ('primary', 'sequential', or 'diverse')
 * @returns Array of color hex codes
 */
export function getChartColors(count: number, variant: string = 'diverse'): string[] {
  // Get base colors from theme
  const baseColors = [
    colors.primary.main,
    colors.secondary.main,
    colors.accent.main,
    colors.info.main,
    colors.success.main,
    colors.warning.main,
    colors.error.main,
    colors.neutral.main,
  ];

  // Create variants of colors based on the requested variant
  if (variant === 'primary') {
    // Primary color with varying opacity
    return Array(count).fill(0).map((_, i) => 
      colors.alpha(colors.primary.main, 0.4 + (0.6 * i / Math.max(1, count - 1)))
    );
  } else if (variant === 'sequential') {
    // Sequential color scheme based on primary color
    const result = [colors.primary.main];
    for (let i = 1; i < count; i++) {
      const ratio = i / count;
      result.push(interpolateColor(colors.primary.main, colors.primary.light, ratio));
    }
    return result;
  } else {
    // Diverse colors for categorical data
    if (count <= baseColors.length) {
      return baseColors.slice(0, count);
    }
    
    // If we need more colors than available, generate them by interpolating
    const result = [...baseColors];
    for (let i = baseColors.length; i < count; i++) {
      const index = i % baseColors.length;
      const color1 = baseColors[index];
      const color2 = baseColors[(index + 1) % baseColors.length];
      const ratio = (i - baseColors.length) / (count - baseColors.length);
      result.push(interpolateColor(color1, color2, ratio));
    }
    return result;
  }
}

/**
 * Helper function to interpolate between two colors
 * @private
 */
function interpolateColor(color1: string, color2: string, ratio: number): string {
  // Convert hex to RGB
  const parseColor = (hex: string) => {
    hex = hex.replace('#', '');
    return {
      r: parseInt(hex.substring(0, 2), 16),
      g: parseInt(hex.substring(2, 4), 16),
      b: parseInt(hex.substring(4, 6), 16)
    };
  };
  
  const c1 = parseColor(color1);
  const c2 = parseColor(color2);
  
  // Interpolate RGB values
  const r = Math.round(c1.r + (c2.r - c1.r) * ratio);
  const g = Math.round(c1.g + (c2.g - c1.g) * ratio);
  const b = Math.round(c1.b + (c2.b - c1.b) * ratio);
  
  // Convert back to hex
  const toHex = (v: number) => {
    const hex = v.toString(16);
    return hex.length === 1 ? '0' + hex : hex;
  };
  
  return `#${toHex(r)}${toHex(g)}${toHex(b)}`;
}

/**
 * Creates a configuration object for bar charts with Justice Bid styling
 * 
 * @param data - Chart data
 * @param options - Additional chart options
 * @returns Chart.js configuration object for bar charts
 */
export function createBarChartConfig(
  data: ChartData,
  options: Partial<ChartOptions> = {}
): ChartConfiguration {
  // Get default options for bar charts
  const defaultOptions = getDefaultChartOptions('bar');
  
  // Merge with provided options
  const chartOptions = {
    ...defaultOptions,
    ...options,
  };
  
  return {
    type: 'bar',
    data,
    options: chartOptions
  };
}

/**
 * Creates a configuration object for line charts with Justice Bid styling
 * 
 * @param data - Chart data
 * @param options - Additional chart options
 * @returns Chart.js configuration object for line charts
 */
export function createLineChartConfig(
  data: ChartData,
  options: Partial<ChartOptions> = {}
): ChartConfiguration {
  // Get default options for line charts
  const defaultOptions = getDefaultChartOptions('line');
  
  // Merge with provided options
  const chartOptions = {
    ...defaultOptions,
    ...options,
  };
  
  return {
    type: 'line',
    data,
    options: chartOptions
  };
}

/**
 * Creates a configuration object for pie/doughnut charts with Justice Bid styling
 * 
 * @param data - Chart data
 * @param options - Additional chart options
 * @returns Chart.js configuration object for pie charts
 */
export function createPieChartConfig(
  data: ChartData,
  options: Partial<ChartOptions> = {}
): ChartConfiguration {
  // Get default options for pie charts
  const defaultOptions = getDefaultChartOptions('pie');
  
  // Pie charts have specific defaults
  const pieDefaults = {
    cutout: '50%', // Makes it a doughnut chart by default
    plugins: {
      legend: {
        position: 'right' as const,
        align: 'center' as const,
      }
    }
  };
  
  // Merge with provided options
  const chartOptions = {
    ...defaultOptions,
    ...pieDefaults,
    ...options,
  };
  
  return {
    type: 'pie',
    data,
    options: chartOptions
  };
}

/**
 * Creates a tooltip configuration with proper formatting based on data type
 * 
 * @param dataType - Type of data ('currency', 'percentage', 'number')
 * @param additionalOptions - Additional tooltip options
 * @returns Tooltip configuration object for Chart.js
 */
export function formatChartTooltip(
  dataType: string,
  additionalOptions: Record<string, any> = {}
): object {
  const baseTooltipConfig = {
    backgroundColor: colors.alpha(colors.neutral.dark, 0.8),
    titleColor: '#ffffff',
    bodyColor: '#ffffff',
    cornerRadius: 4,
    padding: 8,
    titleFont: {
      family: "'Roboto', sans-serif",
      size: 14,
      weight: 'bold'
    },
    bodyFont: {
      family: "'Roboto', sans-serif",
      size: 12,
    },
    callbacks: {}
  };
  
  // Add data type specific formatting
  const callbacks: Record<string, any> = {};
  
  if (dataType === 'currency') {
    callbacks.label = (context: any) => {
      const label = context.dataset.label || '';
      const value = context.parsed.y !== undefined ? context.parsed.y : context.parsed;
      return `${label}: ${formatCurrency(value)}`;
    };
  } else if (dataType === 'percentage') {
    callbacks.label = (context: any) => {
      const label = context.dataset.label || '';
      const value = context.parsed.y !== undefined ? context.parsed.y : context.parsed;
      return `${label}: ${formatPercentage(value)}`;
    };
  } else if (dataType === 'number') {
    callbacks.label = (context: any) => {
      const label = context.dataset.label || '';
      const value = context.parsed.y !== undefined ? context.parsed.y : context.parsed;
      return `${label}: ${value.toLocaleString()}`;
    };
  }
  
  return {
    ...baseTooltipConfig,
    callbacks,
    ...additionalOptions
  };
}

/**
 * Returns default chart options with Justice Bid styling
 * 
 * @param chartType - Type of chart ('bar', 'line', 'pie', etc.)
 * @returns Default Chart.js options based on chart type
 */
export function getDefaultChartOptions(chartType: string): ChartOptions {
  // Base options that apply to all chart types
  const baseOptions: ChartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    animation: {
      duration: 1000,
      easing: 'easeOutQuart'
    },
    font: {
      family: "'Roboto', sans-serif",
      size: 12
    },
    plugins: {
      legend: {
        display: true,
        position: 'top',
        align: 'center',
        labels: {
          usePointStyle: true,
          boxWidth: 10,
          padding: 16,
          font: {
            family: "'Roboto', sans-serif",
            size: 12
          }
        }
      },
      tooltip: formatChartTooltip('number')
    }
  };
  
  // Chart-type specific options
  const typeSpecificOptions: Record<string, ChartOptions> = {
    'bar': {
      scales: {
        x: {
          grid: {
            display: false,
            drawBorder: false
          },
          ticks: {
            padding: 8,
            font: {
              family: "'Roboto', sans-serif",
              size: 12
            }
          }
        },
        y: {
          beginAtZero: true,
          grid: {
            color: colors.alpha(colors.neutral.main, 0.1),
            drawBorder: false
          },
          ticks: {
            padding: 8,
            font: {
              family: "'Roboto', sans-serif",
              size: 12
            }
          }
        }
      },
      plugins: {
        legend: {
          display: true
        }
      },
      borderRadius: 4,
      maxBarThickness: 40
    },
    'line': {
      scales: {
        x: {
          grid: {
            display: false,
            drawBorder: false
          },
          ticks: {
            padding: 8,
            font: {
              family: "'Roboto', sans-serif",
              size: 12
            }
          }
        },
        y: {
          beginAtZero: true,
          grid: {
            color: colors.alpha(colors.neutral.main, 0.1),
            drawBorder: false
          },
          ticks: {
            padding: 8,
            font: {
              family: "'Roboto', sans-serif",
              size: 12
            }
          }
        }
      },
      elements: {
        line: {
          tension: 0.3, // Slight curve to lines
          borderWidth: 3
        },
        point: {
          radius: 4,
          hoverRadius: 6,
          borderWidth: 2,
          backgroundColor: '#ffffff'
        }
      }
    },
    'pie': {
      plugins: {
        legend: {
          position: 'right',
          align: 'center'
        }
      }
    }
  };
  
  // Merge base options with chart-type specific options
  return {
    ...baseOptions,
    ...(typeSpecificOptions[chartType] || {})
  };
}

/**
 * Creates a configuration for stacked bar charts commonly used for comparison analysis
 * 
 * @param data - Chart data
 * @param options - Additional chart options
 * @returns Chart.js configuration for stacked bar charts
 */
export function createStackedBarChartConfig(
  data: ChartData,
  options: Partial<ChartOptions> = {}
): ChartConfiguration {
  // Get default options for bar charts
  const defaultOptions = getDefaultChartOptions('bar');
  
  // Configure stacking
  const stackedOptions: Partial<ChartOptions> = {
    scales: {
      x: {
        stacked: true
      },
      y: {
        stacked: true
      }
    }
  };
  
  // Merge options
  const chartOptions = {
    ...defaultOptions,
    ...stackedOptions,
    ...options
  };
  
  return {
    type: 'bar',
    data,
    options: chartOptions
  };
}

/**
 * Creates a specialized chart configuration for rate impact analysis
 * 
 * @param impactData - Rate impact data to visualize
 * @param options - Additional chart options
 * @returns Chart.js configuration for rate impact visualization
 */
export function createRateImpactChartConfig(
  impactData: any,
  options: Partial<ChartOptions> = {}
): ChartConfiguration {
  // Extract data from the impact data object
  const labels = impactData.items.map((item: any) => item.label);
  const currentAmounts = impactData.items.map((item: any) => item.currentAmount);
  const proposedAmounts = impactData.items.map((item: any) => item.proposedAmount);
  const percentChanges = impactData.items.map((item: any) => item.percentageChange);
  
  // Create a dataset for current rates
  const currentRatesDataset = {
    label: 'Current Rates',
    data: currentAmounts,
    backgroundColor: colors.alpha(colors.info.main, 0.6),
    borderColor: colors.info.main,
    borderWidth: 1
  };
  
  // Create a dataset for proposed rates
  const proposedRatesDataset = {
    label: 'Proposed Rates',
    data: proposedAmounts,
    backgroundColor: colors.alpha(colors.primary.main, 0.6),
    borderColor: colors.primary.main,
    borderWidth: 1
  };
  
  // Create the chart data
  const data: ChartData = {
    labels,
    datasets: [currentRatesDataset, proposedRatesDataset]
  };
  
  // Configure chart options
  const defaultOptions = getDefaultChartOptions('bar');
  
  // Configure y-axis to use currency format
  const impactOptions: Partial<ChartOptions> = {
    plugins: {
      tooltip: formatChartTooltip('currency'),
      legend: {
        display: true
      }
    },
    scales: {
      y: {
        beginAtZero: true,
        ticks: {
          callback: (value: any) => formatCurrency(value)
        }
      }
    }
  };
  
  // Merge options
  const chartOptions = {
    ...defaultOptions,
    ...impactOptions,
    ...options
  };
  
  return {
    type: 'bar',
    data,
    options: chartOptions
  };
}

/**
 * Creates a configuration for time series charts used in historical trend analysis
 * 
 * @param timeSeriesData - Time series data to visualize
 * @param options - Additional chart options
 * @returns Chart.js configuration for time series visualization
 */
export function createTimeSeriesConfig(
  timeSeriesData: any,
  options: Partial<ChartOptions> = {}
): ChartConfiguration {
  // Extract data based on the provided structure
  let datasets = [];
  let labels = [];
  
  if (timeSeriesData.series) {
    // Multiple series format
    labels = timeSeriesData.series[0]?.data.map((point: any) => point.year.toString()) || [];
    
    datasets = timeSeriesData.series.map((series: any, index: number) => {
      const color = getChartColors(timeSeriesData.series.length)[index];
      return {
        label: series.name,
        data: series.data.map((point: any) => point.value),
        borderColor: color,
        backgroundColor: colors.alpha(color, 0.1),
        fill: options.fill === true,
        tension: 0.3
      };
    });
    
    // Add inflation data if present
    if (timeSeriesData.inflationData) {
      datasets.push({
        label: 'Inflation',
        data: timeSeriesData.inflationData.map((point: any) => point.value),
        borderColor: colors.neutral.main,
        backgroundColor: 'transparent',
        borderDash: [5, 5],
        fill: false,
        tension: 0
      });
    }
  } else if (Array.isArray(timeSeriesData)) {
    // Simple array format
    labels = timeSeriesData.map((point: any) => point.label || point.year.toString());
    datasets = [{
      label: 'Value',
      data: timeSeriesData.map((point: any) => point.value),
      borderColor: colors.primary.main,
      backgroundColor: colors.alpha(colors.primary.main, 0.1),
      fill: options.fill === true,
      tension: 0.3
    }];
  }
  
  // Create chart data
  const data: ChartData = {
    labels,
    datasets
  };
  
  // Configure options
  const defaultOptions = getDefaultChartOptions('line');
  
  // Specific options for time series
  const timeSeriesOptions: Partial<ChartOptions> = {
    scales: {
      x: {
        type: 'category',
        title: {
          display: true,
          text: 'Year'
        }
      },
      y: {
        beginAtZero: options.beginAtZero !== false,
        ticks: {
          callback: (value: any) => {
            // Format based on data type
            const dataType = options.dataType || 'number';
            if (dataType === 'currency') {
              return formatCurrency(value);
            } else if (dataType === 'percentage') {
              return formatPercentage(value);
            }
            return value;
          }
        },
        title: {
          display: true,
          text: options.yAxisTitle || ''
        }
      }
    },
    plugins: {
      tooltip: formatChartTooltip(options.dataType || 'number')
    }
  };
  
  // Merge options
  const chartOptions = {
    ...defaultOptions,
    ...timeSeriesOptions,
    ...options
  };
  
  // Determine chart type (line or bar)
  const chartType = options.chartType || 'line';
  
  return {
    type: chartType,
    data,
    options: chartOptions
  };
}

/**
 * Applies responsive breakpoints to chart options for better mobile display
 * 
 * @param baseOptions - Base chart options
 * @returns Chart options with responsive configurations
 */
export function applyResponsiveOptions(baseOptions: ChartOptions): ChartOptions {
  const responsiveOptions: ChartOptions = {
    ...baseOptions,
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      ...(baseOptions.plugins || {}),
      legend: {
        ...(baseOptions.plugins?.legend || {}),
      }
    },
    interaction: {
      mode: 'nearest',
      axis: 'xy',
      intersect: false
    }
  };
  
  // Add responsive breakpoints
  responsiveOptions.responsive = true;
  responsiveOptions.maintainAspectRatio = false;
  
  // @ts-ignore - Type does not include the `scales` prop directly but it's valid
  if (responsiveOptions.scales) {
    return {
      ...responsiveOptions,
      scales: {
        // @ts-ignore - Type safety for scales options
        ...(responsiveOptions.scales || {}),
      }
    };
  }
  
  return responsiveOptions;
}

/**
 * Formats axis tick values based on data type (currency, percentage, number)
 * 
 * @param dataType - Type of data ('currency', 'percentage', 'number')
 * @param options - Additional axis configuration options
 * @returns Axis tick configuration
 */
export function formatAxisTicks(
  dataType: string,
  options: Record<string, any> = {}
): object {
  const baseConfig = {
    beginAtZero: true,
    padding: 8,
    font: {
      family: "'Roboto', sans-serif",
      size: 12
    },
    grid: {
      color: colors.alpha(colors.neutral.main, 0.1),
      drawBorder: false
    }
  };
  
  // Configure tick callback based on data type
  let callback;
  
  if (dataType === 'currency') {
    callback = (value: any) => formatCurrency(value);
  } else if (dataType === 'percentage') {
    callback = (value: any) => formatPercentage(value);
  } else if (dataType === 'number') {
    callback = (value: any) => value.toLocaleString();
  }
  
  return {
    ...baseConfig,
    ticks: {
      ...baseConfig.font,
      callback
    },
    ...options
  };
}

/**
 * Transforms rate data into a format suitable for charts
 * 
 * @param rateData - Array of rate data objects
 * @param groupBy - Dimension to group by ('firm', 'attorney', 'staffClass', etc.)
 * @returns Transformed data ready for charting
 */
export function transformRateDataForChart(
  rateData: any[],
  groupBy: string = 'firm'
): ChartData {
  // Group data by the specified dimension
  const groupedData: Record<string, any[]> = {};
  
  rateData.forEach(rate => {
    let key;
    
    // Determine grouping key based on the groupBy parameter
    switch (groupBy) {
      case 'firm':
        key = rate.firmName || rate.firm?.name || 'Unknown Firm';
        break;
      case 'attorney':
        key = rate.attorneyName || rate.attorney?.name || 'Unknown Attorney';
        break;
      case 'staffClass':
        key = rate.staffClassName || rate.staffClass?.name || 'Unknown Staff Class';
        break;
      case 'practice':
        key = rate.practiceArea || 'Unknown Practice';
        break;
      case 'office':
        key = rate.officeName || rate.office?.name || 'Unknown Office';
        break;
      default:
        key = 'Default Group';
    }
    
    if (!groupedData[key]) {
      groupedData[key] = [];
    }
    
    groupedData[key].push(rate);
  });
  
  // Calculate current vs proposed values
  const labels = Object.keys(groupedData);
  const currentValues = labels.map(label => {
    const rates = groupedData[label];
    return rates.reduce((sum, rate) => sum + (rate.currentRate || 0), 0) / rates.length;
  });
  
  const proposedValues = labels.map(label => {
    const rates = groupedData[label];
    return rates.reduce((sum, rate) => sum + (rate.amount || 0), 0) / rates.length;
  });
  
  // Calculate percentage changes
  const percentageChanges = labels.map((label, index) => {
    const current = currentValues[index];
    const proposed = proposedValues[index];
    
    if (current === 0) return 0;
    return ((proposed - current) / current) * 100;
  });
  
  // Create chart datasets
  return {
    labels,
    datasets: [
      {
        label: 'Current',
        data: currentValues,
        backgroundColor: colors.alpha(colors.info.main, 0.6),
        borderColor: colors.info.main,
        borderWidth: 1
      },
      {
        label: 'Proposed',
        data: proposedValues,
        backgroundColor: colors.alpha(colors.primary.main, 0.6),
        borderColor: colors.primary.main,
        borderWidth: 1
      }
    ]
  };
}

/**
 * Creates a chart configuration for comparing rates against peer groups
 * 
 * @param peerData - Peer comparison data
 * @param options - Additional chart options
 * @returns Chart.js configuration for peer comparison
 */
export function createPeerComparisonChartConfig(
  peerData: any,
  options: Partial<ChartOptions> = {}
): ChartConfiguration {
  // Extract data from the peer comparison object
  const labels = peerData.items.map((item: any) => item.name);
  const rateValues = peerData.items.map((item: any) => item.rateAmount);
  const percentiles = peerData.items.map((item: any) => item.percentile);
  
  // Determine color based on percentile
  const barColors = percentiles.map((percentile: number) => {
    if (percentile > 75) return colors.error.main;
    if (percentile > 50) return colors.warning.main;
    if (percentile > 25) return colors.success.main;
    return colors.info.main;
  });
  
  // Create the chart data
  const data: ChartData = {
    labels,
    datasets: [
      {
        label: 'Rate Amount',
        data: rateValues,
        backgroundColor: barColors,
        borderColor: barColors.map(color => colors.alpha(color, 0.8)),
        borderWidth: 1
      }
    ]
  };
  
  // If we have peer average, add a horizontal line
  if (peerData.peerGroup?.averageRate) {
    const peerAverage = peerData.peerGroup.averageRate;
    
    // @ts-ignore - Chart.js annotation plugin
    data.datasets.push({
      label: 'Peer Average',
      data: Array(labels.length).fill(peerAverage),
      type: 'line',
      borderColor: colors.neutral.dark,
      borderWidth: 2,
      borderDash: [5, 5],
      pointRadius: 0,
      fill: false
    });
  }
  
  // Configure chart options
  const defaultOptions = getDefaultChartOptions('bar');
  
  // Specific options for peer comparison
  const peerOptions: Partial<ChartOptions> = {
    plugins: {
      tooltip: formatChartTooltip('currency'),
      legend: {
        display: true
      }
    },
    scales: {
      y: {
        beginAtZero: true,
        ticks: {
          callback: (value: any) => formatCurrency(value)
        },
        title: {
          display: true,
          text: 'Rate Amount'
        }
      }
    }
  };
  
  // Merge options
  const chartOptions = {
    ...defaultOptions,
    ...peerOptions,
    ...options
  };
  
  return {
    type: 'bar',
    data,
    options: chartOptions
  };
}

/**
 * Adds a trendline to an existing chart dataset
 * 
 * @param chartData - Chart data to enhance with a trendline
 * @param trendlineType - Type of trendline ('linear' or 'moving-average')
 * @returns Chart data with added trendline
 */
export function addTrendline(
  chartData: ChartData,
  trendlineType: string = 'linear'
): ChartData {
  // Only process if we have at least one dataset
  if (!chartData.datasets || chartData.datasets.length === 0) {
    return chartData;
  }
  
  // Get data from the first dataset
  const sourceDataset = chartData.datasets[0];
  const data = sourceDataset.data as number[];
  
  // Return unchanged if not enough data points
  if (data.length < 2) {
    return chartData;
  }
  
  let trendlineData: number[] = [];
  
  if (trendlineType === 'linear') {
    // Calculate linear regression
    // y = mx + b
    let sum_x = 0;
    let sum_y = 0;
    let sum_xy = 0;
    let sum_xx = 0;
    const n = data.length;
    
    for (let i = 0; i < n; i++) {
      sum_x += i;
      sum_y += data[i];
      sum_xy += i * data[i];
      sum_xx += i * i;
    }
    
    const m = (n * sum_xy - sum_x * sum_y) / (n * sum_xx - sum_x * sum_x);
    const b = (sum_y - m * sum_x) / n;
    
    // Generate trendline data points
    trendlineData = Array(n).fill(0).map((_, i) => m * i + b);
  } else if (trendlineType === 'moving-average') {
    // Calculate moving average (3-point window)
    const windowSize = Math.min(3, data.length);
    
    trendlineData = data.map((_, i) => {
      let sum = 0;
      let count = 0;
      
      for (let j = Math.max(0, i - windowSize + 1); j <= i; j++) {
        sum += data[j];
        count++;
      }
      
      return sum / count;
    });
  }
  
  // Create a new trendline dataset
  const trendlineDataset = {
    label: `${trendlineType === 'linear' ? 'Linear' : 'Moving Average'} Trendline`,
    data: trendlineData,
    type: 'line',
    borderColor: colors.neutral.dark,
    backgroundColor: 'transparent',
    borderWidth: 2,
    borderDash: trendlineType === 'linear' ? [5, 5] : [],
    pointRadius: 0,
    fill: false
  };
  
  // Add the trendline to the datasets
  return {
    labels: chartData.labels,
    datasets: [...chartData.datasets, trendlineDataset]
  };
}