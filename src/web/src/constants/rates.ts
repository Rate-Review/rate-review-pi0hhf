/**
 * Constants for rate management in Justice Bid Rate Negotiation System
 * This file contains all rate-related constants, enums, and fixed values used
 * throughout the application for rate management features.
 */

/**
 * Defines the possible statuses of a rate throughout its lifecycle
 */
export const RATE_STATUS = {
  DRAFT: 'draft',
  SUBMITTED: 'submitted',
  UNDER_REVIEW: 'under_review',
  APPROVED: 'approved',
  REJECTED: 'rejected'
} as const;

export type RateStatus = typeof RATE_STATUS[keyof typeof RATE_STATUS];

/**
 * Defines the different types of rates in the system
 */
export const RATE_TYPE = {
  STANDARD: 'standard',
  APPROVED: 'approved',
  PROPOSED: 'proposed',
  COUNTER_PROPOSED: 'counter_proposed'
} as const;

export type RateType = typeof RATE_TYPE[keyof typeof RATE_TYPE];

/**
 * Defines the actions that can be taken on a rate during negotiation
 */
export const RATE_ACTION = {
  APPROVE: 'approve',
  REJECT: 'reject',
  COUNTER_PROPOSE: 'counter_propose',
  ACCEPT: 'accept',
  SUBMIT: 'submit'
} as const;

export type RateAction = typeof RATE_ACTION[keyof typeof RATE_ACTION];

/**
 * Defines the display modes for rate data in the UI
 */
export const RATE_DISPLAY_MODE = {
  SIMPLE: 'simple',
  DETAILED: 'detailed',
  COMPARISON: 'comparison'
} as const;

export type RateDisplayMode = typeof RATE_DISPLAY_MODE[keyof typeof RATE_DISPLAY_MODE];

/**
 * Defines the possible statuses for a rate request
 */
export const RATE_REQUEST_STATUS = {
  PENDING: 'pending',
  APPROVED: 'approved',
  REJECTED: 'rejected'
} as const;

export type RateRequestStatus = typeof RATE_REQUEST_STATUS[keyof typeof RATE_REQUEST_STATUS];

/**
 * Defines filter options for rate listings
 */
export const RATE_FILTER = {
  ALL: 'all',
  PENDING: 'pending',
  ACTIVE: 'active',
  HISTORICAL: 'historical'
} as const;

export type RateFilter = typeof RATE_FILTER[keyof typeof RATE_FILTER];

/**
 * Defines sort options for rate listings
 */
export const RATE_SORT = {
  AMOUNT_HIGHEST: 'amount_highest',
  AMOUNT_LOWEST: 'amount_lowest',
  EFFECTIVE_DATE_NEWEST: 'effective_date_newest',
  EFFECTIVE_DATE_OLDEST: 'effective_date_oldest',
  ATTORNEY_NAME: 'attorney_name',
  STAFF_CLASS: 'staff_class'
} as const;

export type RateSort = typeof RATE_SORT[keyof typeof RATE_SORT];

/**
 * Default maximum rate increase percentage (5%) when not specified by client
 */
export const DEFAULT_MAX_RATE_INCREASE = 5;

/**
 * Validation rules for rate data
 */
export const RATE_VALIDATION_RULES = {
  MIN_RATE: 0,
  MAX_RATE: 10000, // Maximum reasonable rate amount
  MIN_EFFECTIVE_PERIOD: 30 // Minimum days a rate should be effective
};

/**
 * Human-readable labels for rate statuses
 */
export const STATUS_LABELS: Record<RateStatus, string> = {
  [RATE_STATUS.DRAFT]: 'Draft',
  [RATE_STATUS.SUBMITTED]: 'Submitted',
  [RATE_STATUS.UNDER_REVIEW]: 'Under Review',
  [RATE_STATUS.APPROVED]: 'Approved',
  [RATE_STATUS.REJECTED]: 'Rejected'
};

/**
 * Color codes for visualizing rate statuses
 */
export const STATUS_COLORS: Record<RateStatus, string> = {
  [RATE_STATUS.DRAFT]: '#718096', // Neutral gray
  [RATE_STATUS.SUBMITTED]: '#3182CE', // Blue
  [RATE_STATUS.UNDER_REVIEW]: '#DD6B20', // Orange
  [RATE_STATUS.APPROVED]: '#38A169', // Green
  [RATE_STATUS.REJECTED]: '#E53E3E' // Red
};

/**
 * Format options for rate export/import
 */
export const RATE_FORMATS = {
  EXCEL: 'excel',
  CSV: 'csv',
  JSON: 'json'
};

/**
 * Available bulk actions for rates in the negotiation interface
 */
export const BULK_RATE_ACTIONS = [
  { value: RATE_ACTION.APPROVE, label: 'Approve Selected' },
  { value: RATE_ACTION.REJECT, label: 'Reject Selected' },
  { value: RATE_ACTION.COUNTER_PROPOSE, label: 'Counter Propose Selected' }
];