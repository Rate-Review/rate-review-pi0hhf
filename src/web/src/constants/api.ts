/**
 * API Constants
 * 
 * This file contains all API endpoint constants used throughout the Justice Bid application.
 * Centralizing these values ensures consistency and makes it easier to update API paths.
 */

// Base API configuration
export const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'https://api.justicebid.com';
export const API_VERSION = 'v1';
export const API_TIMEOUT = 30000; // 30 seconds default timeout
export const API_URL = `${API_BASE_URL}/api/${API_VERSION}`;

// Authentication endpoints
export const AUTH = {
  LOGIN: `${API_URL}/auth/login`,
  LOGOUT: `${API_URL}/auth/logout`,
  REFRESH_TOKEN: `${API_URL}/auth/refresh`,
  PROFILE: `${API_URL}/auth/profile`,
  MFA_SETUP: `${API_URL}/auth/mfa/setup`,
  SSO: `${API_URL}/auth/sso`
};

// Organization endpoints
export const ORGANIZATIONS = {
  BASE: `${API_URL}/organizations`,
  DETAIL: (id: string) => `${API_URL}/organizations/${id}`,
  USERS: (id: string) => `${API_URL}/organizations/${id}/users`,
  SETTINGS: (id: string) => `${API_URL}/organizations/${id}/settings`
};

// Rate management endpoints
export const RATES = {
  BASE: `${API_URL}/rates`,
  DETAIL: (id: string) => `${API_URL}/rates/${id}`,
  HISTORY: (id: string) => `${API_URL}/rates/${id}/history`,
  APPROVE: (id: string) => `${API_URL}/rates/${id}/approve`,
  REJECT: (id: string) => `${API_URL}/rates/${id}/reject`,
  COUNTER: (id: string) => `${API_URL}/rates/${id}/counter`
};

// Rate request endpoints
export const RATE_REQUESTS = {
  BASE: `${API_URL}/rate-requests`,
  DETAIL: (id: string) => `${API_URL}/rate-requests/${id}`,
  APPROVE: (id: string) => `${API_URL}/rate-requests/${id}/approve`,
  REJECT: (id: string) => `${API_URL}/rate-requests/${id}/reject`
};

// Negotiation endpoints
export const NEGOTIATIONS = {
  BASE: `${API_URL}/negotiations`,
  DETAIL: (id: string) => `${API_URL}/negotiations/${id}`,
  RATES: (id: string) => `${API_URL}/negotiations/${id}/rates`,
  SUBMIT: (id: string) => `${API_URL}/negotiations/${id}/submit`,
  APPROVE: (id: string) => `${API_URL}/negotiations/${id}/approve`,
  REJECT: (id: string) => `${API_URL}/negotiations/${id}/reject`
};

// Analytics endpoints
export const ANALYTICS = {
  IMPACT: `${API_URL}/analytics/impact`,
  COMPARISON: `${API_URL}/analytics/comparison`,
  TRENDS: `${API_URL}/analytics/trends`,
  PERFORMANCE: `${API_URL}/analytics/performance`,
  REPORTS: `${API_URL}/analytics/reports`
};

// Attorney endpoints
export const ATTORNEYS = {
  BASE: `${API_URL}/attorneys`,
  DETAIL: (id: string) => `${API_URL}/attorneys/${id}`,
  PERFORMANCE: (id: string) => `${API_URL}/attorneys/${id}/performance`
};

// Message endpoints
export const MESSAGES = {
  BASE: `${API_URL}/messages`,
  THREAD: (id: string) => `${API_URL}/messages/thread/${id}`,
  BY_NEGOTIATION: (negotiationId: string) => `${API_URL}/messages/negotiation/${negotiationId}`
};

// Outside Counsel Guidelines endpoints
export const OCG = {
  BASE: `${API_URL}/ocg`,
  DETAIL: (id: string) => `${API_URL}/ocg/${id}`,
  NEGOTIATE: (id: string) => `${API_URL}/ocg/${id}/negotiate`
};

// Integration endpoints
export const INTEGRATIONS = {
  EBILLING: {
    BASE: `${API_URL}/integrations/ebilling`,
    CONFIGURE: (system: string) => `${API_URL}/integrations/ebilling/${system}/configure`,
    IMPORT: (system: string) => `${API_URL}/integrations/ebilling/${system}/import`,
    EXPORT: (system: string) => `${API_URL}/integrations/ebilling/${system}/export`,
    TEST: (system: string) => `${API_URL}/integrations/ebilling/${system}/test`
  },
  UNICOURT: {
    BASE: `${API_URL}/integrations/unicourt`,
    ATTORNEYS: `${API_URL}/integrations/unicourt/attorneys`,
    MAPPING: `${API_URL}/integrations/unicourt/mapping`,
    REFRESH: `${API_URL}/integrations/unicourt/refresh`
  },
  FILE: {
    IMPORT: `${API_URL}/integrations/file/import`,
    EXPORT: `${API_URL}/integrations/file/export`,
    TEMPLATES: `${API_URL}/integrations/file/templates`
  }
};

// AI service endpoints
export const AI = {
  CHAT: `${API_URL}/ai/chat`,
  RECOMMENDATIONS: {
    RATES: `${API_URL}/ai/recommendations/rates`,
    ACTIONS: `${API_URL}/ai/recommendations/actions`
  },
  ANALYZE: `${API_URL}/ai/analyze`
};

// Health check endpoint
export const HEALTH = `${API_URL}/health`;