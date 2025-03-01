/**
 * Constants related to analytics functionality for the Justice Bid Rate Negotiation System.
 * These constants are used throughout the application for consistent analytics operations
 * including chart types, time periods, metrics, and filter categories.
 */

/**
 * Time period constants for filtering analytics data
 */
export const TIME_PERIODS = {
  YEAR: 'year',
  QUARTER: 'quarter',
  MONTH: 'month',
  CUSTOM: 'custom'
} as const;

/**
 * Chart type constants for analytics visualizations
 */
export const CHART_TYPES = {
  BAR: 'bar',
  LINE: 'line',
  PIE: 'pie',
  AREA: 'area',
  SCATTER: 'scatter'
} as const;

/**
 * Filter category constants for analytics dashboards
 */
export const FILTER_CATEGORIES = {
  FIRM: 'firm',
  PRACTICE_AREA: 'practiceArea',
  GEOGRAPHY: 'geography',
  STAFF_CLASS: 'staffClass',
  ATTORNEY: 'attorney'
} as const;

/**
 * Metric type constants for analytics calculations
 */
export const METRICS = {
  RATE_IMPACT: 'rateImpact',
  APPROVAL_RATE: 'approvalRate',
  COUNTER_PROPOSAL_RATE: 'counterProposalRate',
  AVERAGE_INCREASE: 'averageIncrease',
  HISTORICAL_CAGR: 'historicalCAGR'
} as const;

/**
 * Analytics view type constants for different dashboard views
 */
export const ANALYTICS_VIEWS = {
  IMPACT_ANALYSIS: 'impactAnalysis',
  PEER_COMPARISON: 'peerComparison',
  HISTORICAL_TRENDS: 'historicalTrends',
  ATTORNEY_PERFORMANCE: 'attorneyPerformance',
  CUSTOM_REPORT: 'customReport'
} as const;

/**
 * Default filter settings for analytics dashboards
 */
export const DEFAULT_FILTERS = {
  timePeriod: TIME_PERIODS.YEAR,
  firm: 'all',
  practiceArea: 'all',
  geography: 'all'
} as const;

/**
 * Currency view options for rate impact analysis
 */
export const CURRENCY_VIEW_TYPES = {
  TOTAL: 'total',
  NET_IMPACT: 'netImpact',
  PERCENTAGE: 'percentage'
} as const;

/**
 * Comparison type constants for peer group analytics
 */
export const PEER_GROUP_COMPARISON_TYPES = {
  AVERAGE: 'average',
  RANGE: 'range',
  PERCENTILE: 'percentile'
} as const;

/**
 * Metric constants for historical trend analysis
 */
export const HISTORICAL_TREND_METRICS = {
  RATE_INCREASES: 'rateIncreases',
  BILLING_VOLUME: 'billingVolume',
  AFA_UTILIZATION: 'afaUtilization'
} as const;

/**
 * Performance metric constants for attorney analytics
 */
export const ATTORNEY_PERFORMANCE_METRICS = {
  HOURS: 'hours',
  MATTERS: 'matters',
  CLIENT_RATING: 'clientRating',
  UNICOURT_PERFORMANCE: 'unicourtPerformance'
} as const;

/**
 * Export format constants for analytics reports
 */
export const REPORT_EXPORT_FORMATS = {
  PDF: 'pdf',
  EXCEL: 'excel',
  CSV: 'csv'
} as const;