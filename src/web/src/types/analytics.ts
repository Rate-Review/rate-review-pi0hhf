/**
 * TypeScript type definitions for analytics functionality in the Justice Bid Rate Negotiation System.
 * This file includes interfaces for rate impact analysis, peer comparisons, historical trends,
 * attorney performance metrics, and custom reports.
 */

import {
  ID,
  CurrencyCode,
  CurrencyAmount,
  DateRange,
  PaginatedResponse,
  TimeframeSelection,
  ChartDataPoint,
  ChartDataSeries,
  RateStatus,
  RateType
} from './common';

import {
  Rate,
  RateWithDetails,
  RateHistoricalData,
  RateAnalysis
} from './rate';

/**
 * Enum for different dimensions to analyze and group data by
 */
export enum AnalyticsDimension {
  FIRM = 'FIRM',
  STAFF_CLASS = 'STAFF_CLASS',
  ATTORNEY = 'ATTORNEY',
  PRACTICE_AREA = 'PRACTICE_AREA',
  OFFICE = 'OFFICE',
  GEOGRAPHY = 'GEOGRAPHY'
}

/**
 * Enum for different views of impact analysis data
 */
export enum ImpactViewType {
  TOTAL = 'TOTAL',
  NET_IMPACT = 'NET_IMPACT',
  PERCENTAGE = 'PERCENTAGE',
  MULTI_YEAR = 'MULTI_YEAR'
}

/**
 * Enum for different views of peer comparison data
 */
export enum PeerComparisonViewType {
  AVERAGE = 'AVERAGE',
  RANGE = 'RANGE',
  PERCENTILE = 'PERCENTILE'
}

/**
 * Enum for different metrics in historical trend analysis
 */
export enum HistoricalTrendMetricType {
  RATE_INCREASE = 'RATE_INCREASE',
  BILLING_VOLUME = 'BILLING_VOLUME',
  AFA_UTILIZATION = 'AFA_UTILIZATION',
  EFFECTIVE_RATE = 'EFFECTIVE_RATE'
}

/**
 * Enum for different metrics in attorney performance analysis
 */
export enum AttorneyPerformanceMetricType {
  HOURS = 'HOURS',
  MATTERS = 'MATTERS',
  CLIENT_RATING = 'CLIENT_RATING',
  UNICOURT_PERFORMANCE = 'UNICOURT_PERFORMANCE',
  EFFICIENCY = 'EFFICIENCY'
}

/**
 * Enum for report export formats
 */
export enum ReportExportFormat {
  PDF = 'PDF',
  EXCEL = 'EXCEL',
  CSV = 'CSV'
}

/**
 * Enum for chart types in analytics visualizations
 */
export enum ChartType {
  BAR = 'BAR',
  LINE = 'LINE',
  PIE = 'PIE',
  AREA = 'AREA',
  SCATTER = 'SCATTER'
}

/**
 * Common filter parameters for all analytics requests
 */
export interface AnalyticsFilterParams {
  clientId: ID | null;
  firmId: ID | null;
  attorneyId: ID | null;
  staffClassId: ID | null;
  practiceArea: string | null;
  officeId: ID | null;
  geography: string | null;
  dateRange: DateRange | null;
  timeframe: TimeframeSelection | null;
  peerGroupId: ID | null;
  currency: CurrencyCode;
  negotiationId: ID | null;
  rateStatus: RateStatus | null;
  rateType: RateType | null;
}

/**
 * Parameters for rate impact analysis requests
 */
export interface ImpactAnalysisParams {
  filters: AnalyticsFilterParams;
  viewType: ImpactViewType;
  groupBy: AnalyticsDimension;
  includePeerComparison: boolean;
  baseYear: number;
}

/**
 * Data item for impact analysis by dimension
 */
export interface ImpactAnalysisItem {
  label: string;
  id: ID;
  currentAmount: number;
  proposedAmount: number;
  impact: number;
  percentageChange: number;
  hoursLastYear: number;
}

/**
 * Result of rate impact analysis request
 */
export interface ImpactAnalysisResult {
  totalCurrentAmount: number;
  totalProposedAmount: number;
  totalImpact: number;
  percentageChange: number;
  currency: CurrencyCode;
  items: ImpactAnalysisItem[];
  highestImpact: ImpactAnalysisItem;
  lowestImpact: ImpactAnalysisItem;
  dimension: AnalyticsDimension;
  peerComparison: { 
    averageIncrease: number; 
    rangeMin: number; 
    rangeMax: number 
  } | null;
  multiYearProjection: { 
    year: number; 
    amount: number 
  }[] | null;
}

/**
 * Parameters for peer comparison analysis requests
 */
export interface PeerComparisonParams {
  filters: AnalyticsFilterParams;
  viewType: PeerComparisonViewType;
  groupBy: AnalyticsDimension;
  includeTrends: boolean;
}

/**
 * Peer group data for comparison analysis
 */
export interface PeerComparisonGroup {
  id: ID;
  name: string;
  averageRateIncrease: number;
  minRateIncrease: number;
  maxRateIncrease: number;
  percentile25: number;
  percentile50: number;
  percentile75: number;
  averageRate: number;
  currency: CurrencyCode;
  memberCount: number;
}

/**
 * Individual item in peer comparison analysis
 */
export interface PeerComparisonItem {
  id: ID;
  name: string;
  rateIncrease: number;
  rateAmount: number;
  currency: CurrencyCode;
  percentile: number;
  dimension: AnalyticsDimension;
}

/**
 * Result of peer comparison analysis request
 */
export interface PeerComparisonResult {
  peerGroup: PeerComparisonGroup;
  items: PeerComparisonItem[];
  yourAverage: number;
  yourPercentile: number;
  dimension: AnalyticsDimension;
  trends: { 
    year: number; 
    yourAverage: number; 
    peerAverage: number 
  }[] | null;
}

/**
 * Parameters for historical trends analysis requests
 */
export interface HistoricalTrendsParams {
  filters: AnalyticsFilterParams;
  metricType: HistoricalTrendMetricType;
  groupBy: AnalyticsDimension;
  includeInflation: boolean;
  years: number;
}

/**
 * Data point for historical trend analysis
 */
export interface HistoricalTrendPoint {
  year: number;
  value: number;
  percentChange: number;
}

/**
 * Data series for historical trend analysis
 */
export interface HistoricalTrendSeries {
  id: ID;
  name: string;
  data: HistoricalTrendPoint[];
  cagr: number;
  dimension: AnalyticsDimension;
}

/**
 * Result of historical trends analysis request
 */
export interface HistoricalTrendsResult {
  series: HistoricalTrendSeries[];
  overallCagr: number;
  inflationData: HistoricalTrendPoint[] | null;
  metricType: HistoricalTrendMetricType;
  currency: CurrencyCode;
  dimension: AnalyticsDimension;
}

/**
 * Parameters for attorney performance analysis requests
 */
export interface AttorneyPerformanceParams {
  attorneyId: ID;
  filters: AnalyticsFilterParams;
  metricTypes: AttorneyPerformanceMetricType[];
  includeUniCourtData: boolean;
}

/**
 * Metric data for attorney performance analysis
 */
export interface AttorneyPerformanceMetric {
  type: AttorneyPerformanceMetricType;
  value: number;
  label: string;
  trend: number;
  percentile: number;
  historicalData: { year: number; value: number }[];
}

/**
 * UniCourt performance data for attorneys
 */
export interface UniCourtPerformanceData {
  caseCount: number;
  winRate: number;
  averageCaseDuration: number;
  practiceAreaDistribution: { area: string; percentage: number }[];
  courtExperience: { court: string; caseCount: number }[];
  overallPercentile: number;
}

/**
 * Result of attorney performance analysis request
 */
export interface AttorneyPerformanceResult {
  attorneyId: ID;
  attorneyName: string;
  metrics: AttorneyPerformanceMetric[];
  unicourtData: UniCourtPerformanceData | null;
  staffClass: string;
  practiceArea: string;
  overallRating: number;
  currentRate: CurrencyAmount;
}

/**
 * Parameters for creating custom reports
 */
export interface CustomReportParams {
  name: string;
  description: string;
  reportType: string;
  filters: AnalyticsFilterParams;
  chartType: ChartType;
  dimensions: AnalyticsDimension[];
  metrics: string[];
  sortBy: string;
  sortDirection: string;
  limit: number;
}

/**
 * Configuration for chart visualization in custom reports
 */
export interface ChartConfiguration {
  type: ChartType;
  title: string;
  xAxisLabel: string;
  yAxisLabel: string;
  colorPalette: string[];
  showLegend: boolean;
  showDataLabels: boolean;
  stacked: boolean;
}

/**
 * Custom report definition and data
 */
export interface CustomReport {
  id: ID;
  name: string;
  description: string;
  createdAt: string;
  createdBy: ID;
  lastModified: string;
  reportType: string;
  parameters: CustomReportParams;
  status: string;
  chartConfiguration: ChartConfiguration;
  data: any[];
  chartData: ChartDataSeries[];
  sharedWith: ID[];
}

/**
 * Parameters for exporting analytics data
 */
export interface ExportParams {
  format: ReportExportFormat;
  reportId: ID | null;
  filters: AnalyticsFilterParams | null;
  includeCharts: boolean;
  includeSummary: boolean;
  fileName: string;
}

/**
 * Redux state for analytics
 */
export interface AnalyticsState {
  impactAnalysis: {
    data: ImpactAnalysisResult | null;
    loading: boolean;
    error: string | null;
  };
  peerComparison: {
    data: PeerComparisonResult | null;
    loading: boolean;
    error: string | null;
  };
  historicalTrends: {
    data: HistoricalTrendsResult | null;
    loading: boolean;
    error: string | null;
  };
  attorneyPerformance: {
    data: AttorneyPerformanceResult | null;
    loading: boolean;
    error: string | null;
  };
  customReports: {
    list: CustomReport[];
    current: CustomReport | null;
    loading: boolean;
    error: string | null;
  };
  filters: AnalyticsFilterParams;
}