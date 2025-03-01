/**
 * Constants related to negotiations in the Justice Bid system.
 * Defines statuses, types, actions, and other fixed values used throughout
 * the negotiation features of the application.
 */

/**
 * Possible statuses of a negotiation throughout its lifecycle
 */
export const NEGOTIATION_STATUS = {
  // Initial request states
  REQUESTED: 'requested',                // Initial rate request initiated
  SUBMITTED: 'submitted',                // Rates have been submitted
  UNDER_REVIEW: 'under_review',          // Client is reviewing the rates
  
  // Client response states
  CLIENT_APPROVED: 'client_approved',    // Client has approved rates
  CLIENT_REJECTED: 'client_rejected',    // Client has rejected rates
  CLIENT_COUNTER_PROPOSED: 'client_counter_proposed', // Client has counter-proposed
  
  // Law firm response states
  FIRM_ACCEPTED: 'firm_accepted',        // Law firm has accepted counter-proposal
  FIRM_COUNTER_PROPOSED: 'firm_counter_proposed', // Law firm has counter-proposed
  
  // Approval workflow states
  PENDING_APPROVAL: 'pending_approval',  // Awaiting internal approval
  APPROVED: 'approved',                  // All approvals received
  REJECTED: 'rejected',                  // Rejected in approval process
  MODIFIED: 'modified',                  // Modified during approval process
  
  // Final states
  EXPORTED: 'exported',                  // Exported to eBilling system
  ACTIVE: 'active',                      // Effective date reached
  EXPIRED: 'expired'                     // Expiration date reached
};

/**
 * Types of negotiations supported by the system
 */
export const NEGOTIATION_TYPE = {
  STANDARD: 'standard',                  // Standard rate negotiation
  OCG: 'ocg'                             // Outside Counsel Guidelines negotiation
};

/**
 * Roles users can have in a negotiation
 */
export const NEGOTIATION_ROLE = {
  LAW_FIRM: 'law_firm',                  // Law firm representative
  CLIENT: 'client',                      // Client representative
  APPROVER: 'approver'                   // Internal approver
};

/**
 * Possible statuses of an approval workflow
 */
export const APPROVAL_STATUS = {
  PENDING: 'pending',                    // Not yet started
  IN_PROGRESS: 'in_progress',            // Some approvals received
  APPROVED: 'approved',                  // All approvals received
  REJECTED: 'rejected'                   // Rejected by an approver
};

/**
 * Actions that can be taken during a negotiation
 */
export const NEGOTIATION_ACTION = {
  APPROVE: 'approve',                    // Approve rates
  REJECT: 'reject',                      // Reject rates
  COUNTER_PROPOSE: 'counter_propose',    // Counter-propose rates
  ACCEPT: 'accept',                      // Accept counter-proposed rates
  SUBMIT: 'submit',                      // Submit rates for review
  REQUEST: 'request',                    // Request rate submission
  EXPORT: 'export'                       // Export approved rates
};

/**
 * Filter options for negotiation listings
 */
export const NEGOTIATION_FILTER = {
  ALL: 'all',                            // All negotiations
  ACTIVE: 'active',                      // Active negotiations
  COMPLETED: 'completed',                // Completed negotiations
  PENDING: 'pending',                    // Pending negotiations
  REJECTED: 'rejected'                   // Rejected negotiations
};

/**
 * Sort options for negotiation listings
 */
export const NEGOTIATION_SORT = {
  DATE_NEWEST: 'date_newest',            // Newest first
  DATE_OLDEST: 'date_oldest',            // Oldest first
  DEADLINE_SOONEST: 'deadline_soonest',  // Soonest deadline first
  ORGANIZATION_NAME: 'organization_name', // Alphabetical by organization
  STATUS: 'status'                       // By status
};

/**
 * Tab options in the negotiation interface
 */
export const NEGOTIATION_TABS = {
  SUMMARY: 'summary',                    // Negotiation summary
  RATES: 'rates',                        // Rate details
  MESSAGES: 'messages',                  // Communication history
  HISTORY: 'history',                    // Negotiation history
  ANALYSIS: 'analysis'                   // Rate impact analysis
};

/**
 * Negotiation interaction modes
 */
export const NEGOTIATION_MODE = {
  REALTIME: 'realtime',                  // Changes communicated immediately
  BATCH: 'batch'                         // Changes sent in batches
};

/**
 * Human-readable labels for negotiation statuses
 */
export const STATUS_LABELS: Record<string, string> = {
  [NEGOTIATION_STATUS.REQUESTED]: 'Rate Request',
  [NEGOTIATION_STATUS.SUBMITTED]: 'Submitted',
  [NEGOTIATION_STATUS.UNDER_REVIEW]: 'Under Review',
  [NEGOTIATION_STATUS.CLIENT_APPROVED]: 'Client Approved',
  [NEGOTIATION_STATUS.CLIENT_REJECTED]: 'Client Rejected',
  [NEGOTIATION_STATUS.CLIENT_COUNTER_PROPOSED]: 'Client Counter-Proposed',
  [NEGOTIATION_STATUS.FIRM_ACCEPTED]: 'Firm Accepted',
  [NEGOTIATION_STATUS.FIRM_COUNTER_PROPOSED]: 'Firm Counter-Proposed',
  [NEGOTIATION_STATUS.PENDING_APPROVAL]: 'Pending Approval',
  [NEGOTIATION_STATUS.APPROVED]: 'Approved',
  [NEGOTIATION_STATUS.REJECTED]: 'Rejected',
  [NEGOTIATION_STATUS.MODIFIED]: 'Modified',
  [NEGOTIATION_STATUS.EXPORTED]: 'Exported',
  [NEGOTIATION_STATUS.ACTIVE]: 'Active',
  [NEGOTIATION_STATUS.EXPIRED]: 'Expired'
};

/**
 * Color codes for visualizing negotiation statuses
 */
export const STATUS_COLORS: Record<string, string> = {
  [NEGOTIATION_STATUS.REQUESTED]: '#718096',      // Neutral
  [NEGOTIATION_STATUS.SUBMITTED]: '#3182CE',      // Info blue
  [NEGOTIATION_STATUS.UNDER_REVIEW]: '#3182CE',   // Info blue
  [NEGOTIATION_STATUS.CLIENT_APPROVED]: '#38A169', // Success green
  [NEGOTIATION_STATUS.CLIENT_REJECTED]: '#E53E3E', // Error red
  [NEGOTIATION_STATUS.CLIENT_COUNTER_PROPOSED]: '#DD6B20', // Warning orange
  [NEGOTIATION_STATUS.FIRM_ACCEPTED]: '#38A169',  // Success green
  [NEGOTIATION_STATUS.FIRM_COUNTER_PROPOSED]: '#DD6B20', // Warning orange
  [NEGOTIATION_STATUS.PENDING_APPROVAL]: '#805AD5', // Purple
  [NEGOTIATION_STATUS.APPROVED]: '#38A169',       // Success green
  [NEGOTIATION_STATUS.REJECTED]: '#E53E3E',       // Error red
  [NEGOTIATION_STATUS.MODIFIED]: '#DD6B20',       // Warning orange
  [NEGOTIATION_STATUS.EXPORTED]: '#2C5282',       // Deep blue
  [NEGOTIATION_STATUS.ACTIVE]: '#38A169',         // Success green
  [NEGOTIATION_STATUS.EXPIRED]: '#718096'         // Neutral
};

/**
 * Available bulk actions for rate negotiations
 */
export const BULK_ACTIONS = [
  { value: NEGOTIATION_ACTION.APPROVE, label: 'Approve Selected' },
  { value: NEGOTIATION_ACTION.REJECT, label: 'Reject Selected' },
  { value: NEGOTIATION_ACTION.COUNTER_PROPOSE, label: 'Counter-Propose Selected' },
  { value: NEGOTIATION_ACTION.ACCEPT, label: 'Accept Selected' }
];