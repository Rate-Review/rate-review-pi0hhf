/**
 * Utility functions for processing and transforming analytics data in the Justice Bid Rate Negotiation System.
 * Supports rate impact analysis, peer comparisons, historical trends, and attorney performance analytics.
 *
 * @version 1.0.0
 */

import { 
  ImpactAnalysisResult, 
  ImpactAnalysisItem, 
  PeerComparisonResult, 
  PeerComparisonItem, 
  HistoricalTrendsResult, 
  HistoricalTrendSeries, 
  AttorneyPerformanceResult, 
  AnalyticsDimension, 
  ImpactViewType, 
  ChartDataSeries, 
  ChartDataPoint 
} from '../types/analytics';
import { 
  Rate, 
  RateHistoricalData 
} from '../types/rate';
import { 
  CurrencyCode, 
  DateRange, 
  ID 
} from '../types/common';
import { 
  formatCurrency, 
  convertCurrency 
} from './currency';
import { 
  formatDate, 
  getDateDifference 
} from './date';
import { 
  calculateRateIncrease, 
  calculateCAGR, 
  roundToDecimalPlaces 
} from './calculations';
import { 
  CURRENCY_VIEW_TYPES, 
  HISTORICAL_TREND_METRICS, 
  PEER_GROUP_COMPARISON_TYPES 
} from '../constants/analytics';

/**
 * Processes raw impact analysis data from the API to enrich and format it for display
 * 
 * @param data - Raw impact analysis data from API
 * @returns Processed impact analysis result ready for display
 */
export function processRateImpact(data: any): ImpactAnalysisResult {
  if (!data || typeof data !== 'object') {
    throw new Error('Invalid impact analysis data');
  }

  // Create a copy of the data to avoid mutating the original
  const result: ImpactAnalysisResult = {
    totalCurrentAmount: data.totalCurrentAmount || 0,
    totalProposedAmount: data.totalProposedAmount || 0,
    totalImpact: data.totalImpact || 0,
    percentageChange: data.percentageChange || 0,
    currency: data.currency || 'USD',
    items: [],
    highestImpact: null as unknown as ImpactAnalysisItem,
    lowestImpact: null as unknown as ImpactAnalysisItem,
    dimension: data.dimension || AnalyticsDimension.FIRM,
    peerComparison: data.peerComparison || null,
    multiYearProjection: data.multiYearProjection || null
  };

  // Process and enrich individual impact items
  if (Array.isArray(data.items)) {
    result.items = data.items.map((item: any) => {
      const processedItem: ImpactAnalysisItem = {
        id: item.id || '',
        label: item.label || '',
        currentAmount: item.currentAmount || 0,
        proposedAmount: item.proposedAmount || 0,
        impact: item.impact || (item.proposedAmount - item.currentAmount) || 0,
        percentageChange: item.percentageChange || calculateRateIncrease(item.currentAmount, item.proposedAmount),
        hoursLastYear: item.hoursLastYear || 0
      };
      return processedItem;
    });

    // Sort items by impact amount (descending)
    result.items.sort((a, b) => b.impact - a.impact);
    
    // Set highest and lowest impact items if available
    if (result.items.length > 0) {
      result.highestImpact = result.items[0];
      result.lowestImpact = result.items[result.items.length - 1];
    }
  }

  // Format currency values for display
  result.items.forEach(item => {
    item.currentAmount = roundToDecimalPlaces(item.currentAmount, 2);
    item.proposedAmount = roundToDecimalPlaces(item.proposedAmount, 2);
    item.impact = roundToDecimalPlaces(item.impact, 2);
    item.percentageChange = roundToDecimalPlaces(item.percentageChange, 4);
  });

  result.totalCurrentAmount = roundToDecimalPlaces(result.totalCurrentAmount, 2);
  result.totalProposedAmount = roundToDecimalPlaces(result.totalProposedAmount, 2);
  result.totalImpact = roundToDecimalPlaces(result.totalImpact, 2);
  result.percentageChange = roundToDecimalPlaces(result.percentageChange, 4);

  return result;
}

/**
 * Formats data for chart visualization based on the chart type and data dimensions
 * 
 * @param data - Raw data to format for charts
 * @param chartType - Type of chart to format data for
 * @param options - Optional configuration for formatting
 * @returns Array of series data ready for chart components
 */
export function formatChartData(
  data: any[],
  chartType: string,
  options: {
    groupBy?: string;
    labelField?: string;
    valueField?: string;
    seriesField?: string;
    colors?: string[];
    sortBy?: string;
    sortDirection?: 'asc' | 'desc';
  } = {}
): ChartDataSeries[] {
  if (!Array.isArray(data) || data.length === 0) {
    return [];
  }

  const {
    groupBy = null,
    labelField = 'label',
    valueField = 'value',
    seriesField = null,
    colors = ['#2C5282', '#38A169', '#DD6B20', '#E53E3E', '#3182CE'],
    sortBy = null,
    sortDirection = 'desc'
  } = options;

  // Function to get a color based on index with cycling
  const getColor = (index: number): string => {
    return colors[index % colors.length];
  };

  // If we need to group data by a series field
  if (seriesField && typeof seriesField === 'string') {
    // Group data by the series field
    const seriesMap = new Map<string, any[]>();
    
    data.forEach(item => {
      const seriesKey = item[seriesField]?.toString() || 'Unknown';
      if (!seriesMap.has(seriesKey)) {
        seriesMap.set(seriesKey, []);
      }
      seriesMap.get(seriesKey)?.push(item);
    });

    // Create a series for each group
    const result: ChartDataSeries[] = [];
    let colorIndex = 0;

    seriesMap.forEach((items, seriesKey) => {
      const seriesData: ChartDataPoint[] = items.map(item => ({
        label: item[labelField]?.toString() || '',
        value: Number(item[valueField]) || 0
      }));

      // Sort data points if requested
      if (sortBy) {
        seriesData.sort((a, b) => {
          const valueA = a[sortBy as keyof ChartDataPoint];
          const valueB = b[sortBy as keyof ChartDataPoint];
          const compareResult = valueA < valueB ? -1 : valueA > valueB ? 1 : 0;
          return sortDirection === 'asc' ? compareResult : -compareResult;
        });
      }

      result.push({
        name: seriesKey,
        data: seriesData,
        color: getColor(colorIndex++)
      });
    });

    return result;
  }
  
  // Single series case (no grouping by series)
  const dataPoints: ChartDataPoint[] = data.map(item => ({
    label: item[labelField]?.toString() || '',
    value: Number(item[valueField]) || 0
  }));

  // Sort data points if requested
  if (sortBy) {
    dataPoints.sort((a, b) => {
      const valueA = a[sortBy as keyof ChartDataPoint];
      const valueB = b[sortBy as keyof ChartDataPoint];
      const compareResult = valueA < valueB ? -1 : valueA > valueB ? 1 : 0;
      return sortDirection === 'asc' ? compareResult : -compareResult;
    });
  }

  // For pie charts, add colors to each data point
  if (chartType === 'pie') {
    dataPoints.forEach((point, index) => {
      point.color = getColor(index);
    });
  }

  return [{
    name: options.groupBy || 'Default',
    data: dataPoints,
    color: colors[0]
  }];
}

/**
 * Processes raw peer comparison data from the API to enrich and format it for display
 * 
 * @param data - Raw peer comparison data from API
 * @param options - Optional configuration for processing
 * @returns Processed peer comparison result ready for display
 */
export function processPeerComparison(
  data: any,
  options: {
    currency?: CurrencyCode;
    sortBy?: string;
    sortDirection?: 'asc' | 'desc';
  } = {}
): PeerComparisonResult {
  if (!data || typeof data !== 'object') {
    throw new Error('Invalid peer comparison data');
  }

  const { 
    currency = 'USD',
    sortBy = 'rateIncrease',
    sortDirection = 'desc'
  } = options;

  // Create base result structure
  const result: PeerComparisonResult = {
    peerGroup: data.peerGroup || {
      id: '',
      name: 'Unknown Peer Group',
      averageRateIncrease: 0,
      minRateIncrease: 0,
      maxRateIncrease: 0,
      percentile25: 0,
      percentile50: 0,
      percentile75: 0,
      averageRate: 0,
      currency: currency,
      memberCount: 0
    },
    items: [],
    yourAverage: data.yourAverage || 0,
    yourPercentile: data.yourPercentile || 0,
    dimension: data.dimension || AnalyticsDimension.FIRM,
    trends: data.trends || null
  };

  // Process and normalize comparison items
  if (Array.isArray(data.items)) {
    result.items = data.items.map((item: any) => {
      const processedItem: PeerComparisonItem = {
        id: item.id || '',
        name: item.name || 'Unknown',
        rateIncrease: item.rateIncrease || 0,
        rateAmount: item.rateAmount || 0,
        currency: item.currency || currency,
        percentile: item.percentile || 0,
        dimension: item.dimension || result.dimension
      };

      // Convert currency if needed
      if (processedItem.currency !== currency) {
        processedItem.rateAmount = convertCurrency(
          processedItem.rateAmount,
          processedItem.currency,
          currency,
          {} // This would need actual exchange rates in a real implementation
        );
        processedItem.currency = currency;
      }

      return processedItem;
    });

    // Sort items according to specified criteria
    if (sortBy && result.items.length > 0) {
      result.items.sort((a, b) => {
        const valueA = a[sortBy as keyof PeerComparisonItem];
        const valueB = b[sortBy as keyof PeerComparisonItem];
        
        // Handle different data types for sorting
        let compareResult: number;
        if (typeof valueA === 'number' && typeof valueB === 'number') {
          compareResult = valueA - valueB;
        } else {
          compareResult = String(valueA).localeCompare(String(valueB));
        }

        return sortDirection === 'asc' ? compareResult : -compareResult;
      });
    }
  }

  // Process trend data if present
  if (result.trends) {
    result.trends = result.trends.map(trend => ({
      ...trend,
      // Format or enhance trend data as needed
      year: trend.year,
      yourAverage: trend.yourAverage,
      peerAverage: trend.peerAverage
    }));
  }

  return result;
}

/**
 * Processes raw historical trend data from the API to enrich and format it for display
 * 
 * @param data - Raw historical trend data from API
 * @param options - Optional configuration for processing
 * @returns Processed historical trends result ready for display
 */
export function processHistoricalTrends(
  data: any,
  options: {
    currency?: CurrencyCode;
    includeCAGR?: boolean;
    includeYoYChange?: boolean;
  } = {}
): HistoricalTrendsResult {
  if (!data || typeof data !== 'object') {
    throw new Error('Invalid historical trends data');
  }

  const { 
    currency = 'USD',
    includeCAGR = true,
    includeYoYChange = true
  } = options;

  // Create base result structure
  const result: HistoricalTrendsResult = {
    series: [],
    overallCagr: data.overallCagr || 0,
    inflationData: data.inflationData || null,
    metricType: data.metricType || HISTORICAL_TREND_METRICS.RATE_INCREASES,
    currency: data.currency || currency,
    dimension: data.dimension || AnalyticsDimension.FIRM
  };

  // Process each series
  if (Array.isArray(data.series)) {
    result.series = data.series.map((series: any) => {
      const processedSeries: HistoricalTrendSeries = {
        id: series.id || '',
        name: series.name || 'Unknown',
        data: [],
        cagr: series.cagr || 0,
        dimension: series.dimension || result.dimension
      };

      // Process data points for this series
      if (Array.isArray(series.data)) {
        // Sort data points by year to ensure correct order
        const sortedData = [...series.data].sort((a, b) => a.year - b.year);
        
        processedSeries.data = sortedData.map((point, index) => {
          const resultPoint = {
            year: point.year,
            value: point.value || 0,
            percentChange: point.percentChange || 0
          };

          // Calculate year-over-year percentage change if requested and not provided
          if (includeYoYChange && index > 0 && !point.percentChange) {
            const previousValue = sortedData[index - 1].value;
            if (previousValue && previousValue !== 0) {
              resultPoint.percentChange = (resultPoint.value - previousValue) / previousValue;
            }
          }

          return resultPoint;
        });

        // Calculate CAGR if requested and not provided
        if (includeCAGR && !series.cagr && processedSeries.data.length >= 2) {
          const firstPoint = processedSeries.data[0];
          const lastPoint = processedSeries.data[processedSeries.data.length - 1];
          const yearSpan = lastPoint.year - firstPoint.year;
          
          if (yearSpan > 0 && firstPoint.value > 0) {
            processedSeries.cagr = Math.pow(lastPoint.value / firstPoint.value, 1 / yearSpan) - 1;
          }
        }
      }

      return processedSeries;
    });
  }

  // Process inflation data if present
  if (Array.isArray(result.inflationData)) {
    result.inflationData = result.inflationData.map((point, index, array) => {
      const resultPoint = {
        year: point.year,
        value: point.value || 0,
        percentChange: point.percentChange || 0
      };

      // Calculate percentage change if not provided
      if (!point.percentChange && index > 0) {
        const previousValue = array[index - 1].value;
        if (previousValue && previousValue !== 0) {
          resultPoint.percentChange = (resultPoint.value - previousValue) / previousValue;
        }
      }

      return resultPoint;
    });
  }

  return result;
}

/**
 * Processes raw attorney performance data from the API to enrich and format it for display
 * 
 * @param data - Raw attorney performance data from API
 * @param options - Optional configuration for processing
 * @returns Processed attorney performance result ready for display
 */
export function processAttorneyPerformance(
  data: any,
  options: {
    currency?: CurrencyCode;
    includeUniCourt?: boolean;
  } = {}
): AttorneyPerformanceResult {
  if (!data || typeof data !== 'object') {
    throw new Error('Invalid attorney performance data');
  }

  const { 
    currency = 'USD',
    includeUniCourt = true
  } = options;

  // Create base result structure
  const result: AttorneyPerformanceResult = {
    attorneyId: data.attorneyId || '',
    attorneyName: data.attorneyName || 'Unknown Attorney',
    metrics: [],
    unicourtData: includeUniCourt ? data.unicourtData : null,
    staffClass: data.staffClass || '',
    practiceArea: data.practiceArea || '',
    overallRating: data.overallRating || 0,
    currentRate: {
      amount: data.currentRate?.amount || 0,
      currency: data.currentRate?.currency || currency
    }
  };

  // Process performance metrics
  if (Array.isArray(data.metrics)) {
    result.metrics = data.metrics.map(metric => ({
      type: metric.type,
      value: metric.value || 0,
      label: metric.label || '',
      trend: metric.trend || 0,
      percentile: metric.percentile || 0,
      historicalData: Array.isArray(metric.historicalData) 
        ? metric.historicalData.map(h => ({
            year: h.year,
            value: h.value || 0
          }))
        : []
    }));
  }

  // Process UniCourt data if present and requested
  if (includeUniCourt && data.unicourtData) {
    result.unicourtData = {
      caseCount: data.unicourtData.caseCount || 0,
      winRate: data.unicourtData.winRate || 0,
      averageCaseDuration: data.unicourtData.averageCaseDuration || 0,
      practiceAreaDistribution: Array.isArray(data.unicourtData.practiceAreaDistribution)
        ? data.unicourtData.practiceAreaDistribution
        : [],
      courtExperience: Array.isArray(data.unicourtData.courtExperience)
        ? data.unicourtData.courtExperience
        : [],
      overallPercentile: data.unicourtData.overallPercentile || 0
    };
  }

  // Format currency values if needed
  if (result.currentRate.currency !== currency) {
    result.currentRate.amount = convertCurrency(
      result.currentRate.amount,
      result.currentRate.currency,
      currency,
      {} // This would need actual exchange rates in a real implementation
    );
    result.currentRate.currency = currency;
  }

  return result;
}

/**
 * Prepares common parameters for analytics API requests from filter settings
 * 
 * @param filters - User-selected filter values
 * @returns Standardized parameters object for API requests
 */
export function prepareAnalyticsParams(
  filters: {
    clientId?: ID | null;
    firmId?: ID | null;
    attorneyId?: ID | null;
    staffClassId?: ID | null;
    practiceArea?: string | null;
    officeId?: ID | null;
    geography?: string | null;
    dateRange?: DateRange | null;
    peerGroupId?: ID | null;
    currency?: CurrencyCode;
    [key: string]: any;
  }
): Record<string, any> {
  // Create base params object with defaults
  const params: Record<string, any> = {
    currency: filters.currency || 'USD'
  };

  // Add ID filters if present
  const idFilters = ['clientId', 'firmId', 'attorneyId', 'staffClassId', 'officeId', 'peerGroupId'];
  idFilters.forEach(filter => {
    if (filters[filter]) {
      params[filter] = filters[filter];
    }
  });

  // Add string filters if present
  const stringFilters = ['practiceArea', 'geography'];
  stringFilters.forEach(filter => {
    if (filters[filter]) {
      params[filter] = filters[filter];
    }
  });

  // Process date range if present
  if (filters.dateRange) {
    params.startDate = filters.dateRange.startDate;
    params.endDate = filters.dateRange.endDate;
  }

  // Add any additional filters
  Object.entries(filters).forEach(([key, value]) => {
    if (
      value !== null && 
      value !== undefined && 
      !idFilters.includes(key) && 
      !stringFilters.includes(key) && 
      key !== 'dateRange' &&
      key !== 'currency'
    ) {
      params[key] = value;
    }
  });

  return params;
}

/**
 * Determines the optimal dimension to group analytics data by based on filters and data volume
 * 
 * @param filters - User-selected filter values
 * @param dataCount - Number of data points
 * @returns The optimal dimension for grouping
 */
export function determineOptimalGrouping(
  filters: {
    clientId?: ID | null;
    firmId?: ID | null;
    attorneyId?: ID | null;
    staffClassId?: ID | null;
    practiceArea?: string | null;
    officeId?: ID | null;
    geography?: string | null;
    [key: string]: any;
  },
  dataCount: number
): AnalyticsDimension {
  // If user has filtered by specific attributes, use complementary grouping
  if (filters.attorneyId) {
    return AnalyticsDimension.STAFF_CLASS;
  }

  if (filters.staffClassId) {
    return AnalyticsDimension.ATTORNEY;
  }

  if (filters.firmId) {
    // For a single firm, prefer staff class grouping
    return AnalyticsDimension.STAFF_CLASS;
  }

  if (filters.practiceArea) {
    return AnalyticsDimension.FIRM;
  }

  // Based on data volume, determine optimal grouping
  if (dataCount > 1000) {
    // With large data volumes, use higher-level grouping
    return AnalyticsDimension.FIRM;
  } else if (dataCount > 500) {
    return AnalyticsDimension.STAFF_CLASS;
  } else if (dataCount > 100) {
    return AnalyticsDimension.PRACTICE_AREA;
  } else {
    // For smaller datasets, more detailed grouping is manageable
    return AnalyticsDimension.ATTORNEY;
  }
}

/**
 * Generates a consistent color palette for chart visualization based on data categories
 * 
 * @param categories - Data categories that need colors
 * @param options - Optional configuration for color generation
 * @returns Mapping of categories to color values
 */
export function generateChartColors(
  categories: string[],
  options: {
    baseColors?: string[];
    preferredColors?: Record<string, string>;
    colorMode?: 'sequential' | 'categorical';
  } = {}
): Record<string, string> {
  const { 
    baseColors = [
      '#2C5282', // Primary blue
      '#38A169', // Green
      '#DD6B20', // Orange
      '#E53E3E', // Red
      '#3182CE', // Light blue
      '#805AD5', // Purple
      '#D69E2E', // Yellow
      '#4FD1C5', // Teal
      '#F56565', // Pink
      '#667EEA'  // Indigo
    ],
    preferredColors = {},
    colorMode = 'categorical'
  } = options;

  const result: Record<string, string> = {};

  // Function to calculate a color in a sequential scheme based on index
  const getSequentialColor = (index: number, total: number): string => {
    // For sequential colors, we interpolate between the first two base colors
    const startColor = hexToRgb(baseColors[0]);
    const endColor = hexToRgb(baseColors[1]);
    
    if (!startColor || !endColor) return baseColors[0];
    
    const ratio = index / (total - 1 || 1);
    const r = Math.round(startColor.r + (endColor.r - startColor.r) * ratio);
    const g = Math.round(startColor.g + (endColor.g - startColor.g) * ratio);
    const b = Math.round(startColor.b + (endColor.b - startColor.b) * ratio);
    
    return rgbToHex(r, g, b);
  };

  // Function to convert hex color to RGB
  const hexToRgb = (hex: string): { r: number, g: number, b: number } | null => {
    const match = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex);
    return match ? {
      r: parseInt(match[1], 16),
      g: parseInt(match[2], 16),
      b: parseInt(match[3], 16)
    } : null;
  };

  // Function to convert RGB to hex
  const rgbToHex = (r: number, g: number, b: number): string => {
    return `#${((1 << 24) + (r << 16) + (g << 8) + b).toString(16).slice(1)}`;
  };

  // Assign colors to each category
  categories.forEach((category, index) => {
    // First check if there's a preferred color
    if (preferredColors[category]) {
      result[category] = preferredColors[category];
      return;
    }

    // Otherwise generate a color based on the selected mode
    if (colorMode === 'sequential') {
      result[category] = getSequentialColor(index, categories.length);
    } else {
      // For categorical, cycle through the base colors
      result[category] = baseColors[index % baseColors.length];
    }
  });

  return result;
}

/**
 * Calculates year-over-year percentage changes for time series data
 * 
 * @param timeSeriesData - Array of data points with year and value properties
 * @returns Enhanced time series data with percentage changes
 */
export function calculateYearOverYearChange(
  timeSeriesData: Array<{ year: number; value: number; [key: string]: any }>
): Array<{ year: number; value: number; percentageChange: number; [key: string]: any }> {
  if (!Array.isArray(timeSeriesData) || timeSeriesData.length < 2) {
    return timeSeriesData.map(point => ({
      ...point,
      percentageChange: 0
    }));
  }

  // Sort data points by year
  const sortedData = [...timeSeriesData].sort((a, b) => a.year - b.year);
  
  // Calculate year-over-year changes
  return sortedData.map((point, index) => {
    const result = { ...point, percentageChange: 0 };
    
    if (index > 0) {
      const previousValue = sortedData[index - 1].value;
      if (previousValue && previousValue !== 0) {
        result.percentageChange = (point.value - previousValue) / previousValue;
      }
    }
    
    return result;
  });
}

/**
 * Generates a summary of key insights from analytics data for display or AI processing
 * 
 * @param data - Analytics data to summarize
 * @param dataType - Type of analytics data (impact, peer, historical, attorney)
 * @returns Summary with key insights and trends
 */
export function summarizeAnalyticsData(
  data: any,
  dataType: 'impact' | 'peer' | 'historical' | 'attorney'
): {
  keyMetrics: Record<string, any>;
  insights: string[];
  trends: string[];
  comparisons: Record<string, any>;
} {
  // Initialize result structure
  const result = {
    keyMetrics: {},
    insights: [],
    trends: [],
    comparisons: {}
  };

  // Process based on data type
  switch (dataType) {
    case 'impact':
      if (data && typeof data === 'object') {
        // Extract key metrics
        result.keyMetrics = {
          totalImpact: data.totalImpact || 0,
          percentageChange: data.percentageChange || 0,
          currency: data.currency || 'USD'
        };
        
        // Generate insights
        if (data.percentageChange > 0.05) {
          result.insights.push('Rate increase is above 5%, which may require special approval.');
        }
        
        if (data.highestImpact) {
          result.insights.push(`${data.highestImpact.label} has the highest impact at ${formatCurrency(data.highestImpact.impact, data.currency)}.`);
        }
        
        // Add peer comparison if available
        if (data.peerComparison) {
          result.comparisons = data.peerComparison;
          
          if (data.percentageChange > data.peerComparison.averageIncrease) {
            result.insights.push(`Rate increase is above peer group average of ${(data.peerComparison.averageIncrease * 100).toFixed(1)}%.`);
          } else {
            result.insights.push(`Rate increase is below peer group average of ${(data.peerComparison.averageIncrease * 100).toFixed(1)}%.`);
          }
        }
      }
      break;
      
    case 'peer':
      if (data && typeof data === 'object') {
        // Extract key metrics
        result.keyMetrics = {
          yourAverage: data.yourAverage || 0,
          yourPercentile: data.yourPercentile || 0,
          peerGroupAverage: data.peerGroup?.averageRateIncrease || 0,
          peerGroupRange: {
            min: data.peerGroup?.minRateIncrease || 0,
            max: data.peerGroup?.maxRateIncrease || 0
          }
        };
        
        // Generate insights
        if (data.yourPercentile > 75) {
          result.insights.push(`Your rates are in the top quartile (${data.yourPercentile.toFixed(0)}th percentile) of the peer group.`);
        } else if (data.yourPercentile < 25) {
          result.insights.push(`Your rates are in the bottom quartile (${data.yourPercentile.toFixed(0)}th percentile) of the peer group.`);
        }
        
        // Add trend analysis if available
        if (Array.isArray(data.trends) && data.trends.length > 1) {
          const firstYear = data.trends[0].year;
          const lastYear = data.trends[data.trends.length - 1].year;
          
          result.trends.push(`From ${firstYear} to ${lastYear}, your average rate increased by ${((data.trends[data.trends.length - 1].yourAverage / data.trends[0].yourAverage - 1) * 100).toFixed(1)}%.`);
          result.trends.push(`During the same period, peer average rates increased by ${((data.trends[data.trends.length - 1].peerAverage / data.trends[0].peerAverage - 1) * 100).toFixed(1)}%.`);
        }
      }
      break;
      
    case 'historical':
      if (data && typeof data === 'object') {
        // Extract key metrics
        result.keyMetrics = {
          overallCagr: data.overallCagr || 0,
          metricType: data.metricType || '',
          currency: data.currency || 'USD'
        };
        
        // Generate insights for each series
        if (Array.isArray(data.series)) {
          data.series.forEach(series => {
            if (series.data && series.data.length > 1) {
              const firstPoint = series.data[0];
              const lastPoint = series.data[series.data.length - 1];
              const totalChange = ((lastPoint.value / firstPoint.value) - 1) * 100;
              
              result.trends.push(`${series.name}: ${totalChange.toFixed(1)}% ${totalChange >= 0 ? 'increase' : 'decrease'} from ${firstPoint.year} to ${lastPoint.year}.`);
            }
            
            if (series.cagr) {
              result.insights.push(`${series.name} has a compound annual growth rate of ${(series.cagr * 100).toFixed(1)}%.`);
            }
          });
        }
        
        // Add inflation comparison if available
        if (Array.isArray(data.inflationData) && data.inflationData.length > 0) {
          const firstInflation = data.inflationData[0];
          const lastInflation = data.inflationData[data.inflationData.length - 1];
          const inflationChange = ((lastInflation.value / firstInflation.value) - 1) * 100;
          
          result.comparisons.inflation = {
            totalChange: inflationChange,
            startYear: firstInflation.year,
            endYear: lastInflation.year
          };
          
          // Compare growth to inflation
          if (data.overallCagr * 100 > inflationChange) {
            result.insights.push(`Rates have grown faster than inflation (${(data.overallCagr * 100).toFixed(1)}% vs. ${inflationChange.toFixed(1)}%).`);
          } else {
            result.insights.push(`Rates have grown slower than inflation (${(data.overallCagr * 100).toFixed(1)}% vs. ${inflationChange.toFixed(1)}%).`);
          }
        }
      }
      break;
      
    case 'attorney':
      if (data && typeof data === 'object') {
        // Extract key metrics
        result.keyMetrics = {
          attorneyName: data.attorneyName || 'Unknown Attorney',
          currentRate: data.currentRate || { amount: 0, currency: 'USD' },
          staffClass: data.staffClass || '',
          overallRating: data.overallRating || 0
        };
        
        // Generate insights from metrics
        if (Array.isArray(data.metrics)) {
          data.metrics.forEach(metric => {
            if (metric.percentile > 75) {
              result.insights.push(`${metric.label}: Top performer (${metric.percentile.toFixed(0)}th percentile).`);
            } else if (metric.percentile < 25) {
              result.insights.push(`${metric.label}: Below average (${metric.percentile.toFixed(0)}th percentile).`);
            }
            
            if (metric.trend > 0.1) {
              result.trends.push(`${metric.label}: Strong positive trend (+${(metric.trend * 100).toFixed(1)}%).`);
            } else if (metric.trend < -0.1) {
              result.trends.push(`${metric.label}: Negative trend (${(metric.trend * 100).toFixed(1)}%).`);
            }
          });
        }
        
        // Add UniCourt insights if available
        if (data.unicourtData) {
          result.comparisons.unicourt = {
            winRate: data.unicourtData.winRate || 0,
            caseCount: data.unicourtData.caseCount || 0,
            overallPercentile: data.unicourtData.overallPercentile || 0
          };
          
          if (data.unicourtData.winRate > 0.7) {
            result.insights.push(`Strong court performance with ${(data.unicourtData.winRate * 100).toFixed(0)}% win rate across ${data.unicourtData.caseCount} cases.`);
          }
          
          if (data.unicourtData.overallPercentile > 75) {
            result.insights.push(`Top performing attorney in court (${data.unicourtData.overallPercentile.toFixed(0)}th percentile).`);
          }
        }
      }
      break;
  }

  return result;
}

/**
 * Filters analytics data based on user-selected criteria
 * 
 * @param data - Array of analytics data items
 * @param filters - Filter criteria to apply
 * @returns Filtered data items
 */
export function filterAnalyticsData<T extends Record<string, any>>(
  data: T[],
  filters: Record<string, any>
): T[] {
  if (!Array.isArray(data) || data.length === 0) {
    return [];
  }

  if (!filters || Object.keys(filters).length === 0) {
    return data;
  }

  return data.filter(item => {
    // Iterate through all filters
    return Object.entries(filters).every(([key, filterValue]) => {
      // Skip null or undefined filter values
      if (filterValue === null || filterValue === undefined) {
        return true;
      }

      const itemValue = item[key];

      // Handle special filter cases
      if (key === 'dateRange' && filterValue.startDate && filterValue.endDate) {
        // For date range filters, check if item date is within range
        const itemDate = new Date(item.date || item.effectiveDate || item.createdAt);
        const startDate = new Date(filterValue.startDate);
        const endDate = new Date(filterValue.endDate);
        
        return itemDate >= startDate && itemDate <= endDate;
      }

      // Handle array filter values (IN operator)
      if (Array.isArray(filterValue)) {
        return filterValue.includes(itemValue);
      }

      // Handle nested filter objects
      if (typeof filterValue === 'object' && !Array.isArray(filterValue)) {
        const operator = filterValue.operator;
        const value = filterValue.value;
        
        switch (operator) {
          case 'eq':
            return itemValue === value;
          case 'neq':
            return itemValue !== value;
          case 'gt':
            return itemValue > value;
          case 'gte':
            return itemValue >= value;
          case 'lt':
            return itemValue < value;
          case 'lte':
            return itemValue <= value;
          case 'contains':
            return String(itemValue).toLowerCase().includes(String(value).toLowerCase());
          case 'in':
            return Array.isArray(value) && value.includes(itemValue);
          case 'between':
            return Array.isArray(value) && itemValue >= value[0] && itemValue <= value[1];
          default:
            return true;
        }
      }

      // Default case: direct equality comparison
      return itemValue === filterValue;
    });
  });
}

/**
 * Sorts analytics data based on specified fields and directions
 * 
 * @param data - Array of analytics data items
 * @param sortBy - Field to sort by
 * @param sortDirection - Sort direction ('asc' or 'desc')
 * @returns Sorted data items
 */
export function sortAnalyticsData<T extends Record<string, any>>(
  data: T[],
  sortBy: string,
  sortDirection: 'asc' | 'desc' = 'desc'
): T[] {
  if (!Array.isArray(data) || data.length === 0) {
    return [];
  }

  if (!sortBy) {
    return data;
  }

  return [...data].sort((a, b) => {
    const valueA = a[sortBy];
    const valueB = b[sortBy];
    
    // Handle different data types
    if (typeof valueA === 'number' && typeof valueB === 'number') {
      return sortDirection === 'asc' ? valueA - valueB : valueB - valueA;
    }
    
    if (valueA instanceof Date && valueB instanceof Date) {
      return sortDirection === 'asc' 
        ? valueA.getTime() - valueB.getTime() 
        : valueB.getTime() - valueA.getTime();
    }
    
    // Convert to strings for string comparison or if types don't match
    const stringA = String(valueA || '');
    const stringB = String(valueB || '');
    
    return sortDirection === 'asc' 
      ? stringA.localeCompare(stringB) 
      : stringB.localeCompare(stringA);
  });
}

/**
 * Converts analytics data to CSV format for export
 * 
 * @param data - Analytics data to export
 * @param dataType - Type of analytics data being exported
 * @returns CSV formatted string
 */
export function exportAnalyticsToCSV(
  data: any,
  dataType: 'impact' | 'peer' | 'historical' | 'attorney'
): string {
  if (!data) {
    return '';
  }

  // Define column headers based on data type
  let headers: string[] = [];
  let rows: string[][] = [];

  switch (dataType) {
    case 'impact':
      if (data.items && Array.isArray(data.items)) {
        headers = ['Label', 'Current Amount', 'Proposed Amount', 'Impact', 'Percentage Change', 'Hours Last Year'];
        
        rows = data.items.map((item: any) => [
          item.label || '',
          item.currentAmount?.toString() || '0',
          item.proposedAmount?.toString() || '0',
          item.impact?.toString() || '0',
          ((item.percentageChange || 0) * 100).toFixed(2) + '%',
          item.hoursLastYear?.toString() || '0'
        ]);
        
        // Add summary row
        rows.push([
          'TOTAL',
          data.totalCurrentAmount?.toString() || '0',
          data.totalProposedAmount?.toString() || '0',
          data.totalImpact?.toString() || '0',
          ((data.percentageChange || 0) * 100).toFixed(2) + '%',
          ''
        ]);
      }
      break;
      
    case 'peer':
      if (data.items && Array.isArray(data.items)) {
        headers = ['Name', 'Rate Increase', 'Rate Amount', 'Percentile'];
        
        rows = data.items.map((item: any) => [
          item.name || '',
          ((item.rateIncrease || 0) * 100).toFixed(2) + '%',
          item.rateAmount?.toString() || '0',
          (item.percentile || 0).toFixed(0) + '%'
        ]);
        
        // Add summary row
        if (data.peerGroup) {
          rows.push([
            'PEER GROUP AVERAGE',
            ((data.peerGroup.averageRateIncrease || 0) * 100).toFixed(2) + '%',
            data.peerGroup.averageRate?.toString() || '0',
            '50%'
          ]);
          
          rows.push([
            'YOUR AVERAGE',
            ((data.yourAverage || 0) * 100).toFixed(2) + '%',
            '',
            (data.yourPercentile || 0).toFixed(0) + '%'
          ]);
        }
      }
      break;
      
    case 'historical':
      if (data.series && Array.isArray(data.series)) {
        // Determine all years across all series
        const yearsSet = new Set<number>();
        data.series.forEach((series: any) => {
          if (Array.isArray(series.data)) {
            series.data.forEach((point: any) => yearsSet.add(point.year));
          }
        });
        
        const years = Array.from(yearsSet).sort();
        
        // Create headers with series names
        headers = ['Year', ...data.series.map((s: any) => s.name || 'Unknown')];
        
        // Create rows for each year
        rows = years.map(year => {
          const row = [year.toString()];
          
          data.series.forEach((series: any) => {
            const yearData = Array.isArray(series.data) 
              ? series.data.find((d: any) => d.year === year) 
              : null;
            
            row.push(yearData ? yearData.value.toString() : '');
          });
          
          return row;
        });
        
        // Add CAGR row
        const cagrRow = ['CAGR'];
        data.series.forEach((series: any) => {
          cagrRow.push(((series.cagr || 0) * 100).toFixed(2) + '%');
        });
        rows.push(cagrRow);
      }
      break;
      
    case 'attorney':
      if (data.metrics && Array.isArray(data.metrics)) {
        headers = ['Metric', 'Value', 'Percentile', 'Trend'];
        
        rows = data.metrics.map((metric: any) => [
          metric.label || metric.type || '',
          metric.value?.toString() || '0',
          (metric.percentile || 0).toFixed(0) + '%',
          ((metric.trend || 0) * 100).toFixed(2) + '%'
        ]);
        
        // Add UniCourt data if available
        if (data.unicourtData) {
          rows.push(['Case Count', data.unicourtData.caseCount?.toString() || '0', '', '']);
          rows.push(['Win Rate', ((data.unicourtData.winRate || 0) * 100).toFixed(0) + '%', '', '']);
          rows.push(['Average Case Duration', data.unicourtData.averageCaseDuration?.toString() || '0', '', '']);
          rows.push(['Court Performance Percentile', (data.unicourtData.overallPercentile || 0).toFixed(0) + '%', '', '']);
        }
        
        // Add attorney general info
        rows.unshift(['Attorney', data.attorneyName || '', '', '']);
        rows.unshift(['Staff Class', data.staffClass || '', '', '']);
        rows.unshift(['Practice Area', data.practiceArea || '', '', '']);
        rows.unshift(['Current Rate', `${data.currentRate?.amount || '0'} ${data.currentRate?.currency || 'USD'}`, '', '']);
      }
      break;
  }

  // Convert to CSV format
  const csvContent = [
    headers.join(','),
    ...rows.map(row => 
      row.map(cell => {
        // Escape commas and quotes
        if (cell.includes(',') || cell.includes('"')) {
          return `"${cell.replace(/"/g, '""')}"`;
        }
        return cell;
      }).join(',')
    )
  ].join('\n');

  return csvContent;
}