/**
 * Constants for toast notifications throughout the Justice Bid application
 * Used to provide consistent user feedback on actions and events
 */

/**
 * Types of toast notifications
 */
export enum ToastType {
  SUCCESS = "success",
  ERROR = "error",
  WARNING = "warning",
  INFO = "info"
}

/**
 * Duration options for toast notifications in milliseconds
 */
export const ToastDuration = {
  SHORT: 3000,
  MEDIUM: 5000,
  LONG: 8000
};

/**
 * Position options for toast notifications
 */
export enum ToastPosition {
  TOP_RIGHT = "top-right",
  TOP_LEFT = "top-left",
  BOTTOM_RIGHT = "bottom-right",
  BOTTOM_LEFT = "bottom-left",
  TOP_CENTER = "top-center",
  BOTTOM_CENTER = "bottom-center"
}

/**
 * Configuration options for toast notifications
 */
export interface ToastConfig {
  position: ToastPosition;
  duration: number;
  closeButton: boolean;
  pauseOnHover: boolean;
}

/**
 * Default configuration for toast notifications
 */
export const DEFAULT_TOAST_CONFIG: ToastConfig = {
  position: ToastPosition.TOP_RIGHT,
  duration: ToastDuration.MEDIUM,
  closeButton: true,
  pauseOnHover: true
};

/**
 * Toast messages for rate-related actions
 */
export const RateMessages = {
  SUBMISSION_SUCCESS: "Rate submission successfully sent",
  SUBMISSION_ERROR: "Failed to submit rates. Please try again",
  APPROVAL_SUCCESS: "Rates have been approved",
  REJECTION: "Rates have been rejected",
  COUNTER_PROPOSAL_SENT: "Counter-proposal has been sent",
  COUNTER_PROPOSAL_RECEIVED: "New counter-proposal received"
};

/**
 * Toast messages for negotiation-related actions
 */
export const NegotiationMessages = {
  STARTED: "Negotiation has been initiated",
  COMPLETED: "Negotiation has been completed successfully",
  UPDATED: "Negotiation has been updated"
};

/**
 * Toast messages for integration-related actions
 */
export const IntegrationMessages = {
  CONNECTION_SUCCESS: "Connection established successfully",
  CONNECTION_ERROR: "Failed to connect. Please check your credentials",
  IMPORT_SUCCESS: "Data imported successfully",
  IMPORT_ERROR: "Failed to import data. Please try again",
  EXPORT_SUCCESS: "Data exported successfully",
  EXPORT_ERROR: "Failed to export data. Please try again"
};

/**
 * Toast messages for user management actions
 */
export const UserMessages = {
  CREATED: "User created successfully",
  UPDATED: "User information updated",
  DELETED: "User deleted",
  PERMISSION_UPDATED: "User permissions updated"
};

/**
 * Toast messages for system events
 */
export const SystemMessages = {
  GENERAL_ERROR: "An error occurred. Please try again",
  NETWORK_ERROR: "Network connection issue. Please check your connection",
  SESSION_EXPIRED: "Your session has expired. Please log in again"
};

/**
 * Toast messages for OCG-related actions
 */
export const OCGMessages = {
  SAVED: "Outside Counsel Guidelines saved as draft",
  PUBLISHED: "Outside Counsel Guidelines published successfully",
  NEGOTIATION_STARTED: "OCG negotiation has been initiated",
  NEGOTIATION_COMPLETED: "OCG negotiation has been completed"
};