/**
 * routes.ts
 * 
 * This file defines all route paths for the Justice Bid Rate Negotiation System
 * to ensure consistent routing across components and prevent duplication or typos
 * in route path strings. This serves as a single source of truth for all
 * application routes, organized by categories for different user types.
 */

export const ROUTES = {
  // Auth Routes
  LOGIN: '/login',
  REGISTER: '/register',
  RESET_PASSWORD: '/reset-password',
  MFA_SETUP: '/mfa-setup',
  PROFILE: '/profile',
  
  // Error Routes
  ERROR: '/error',
  NOT_FOUND: '/not-found',
  
  // Organization Type Root Routes
  ADMIN: '/admin',
  CLIENT: '/client',
  LAW_FIRM: '/law-firm',
  
  // Dashboard Routes
  ADMIN_DASHBOARD: '/admin',
  CLIENT_DASHBOARD: '/client',
  LAW_FIRM_DASHBOARD: '/law-firm',
  
  // Rate Routes
  RATE_REQUESTS: '/rate-requests',
  RATE_SUBMISSIONS: '/rate-submissions',
  RATE_HISTORY: '/rate-history',
  RATE_ANALYTICS: '/rate-analytics',
  
  // Negotiation Routes
  NEGOTIATIONS: '/negotiations',
  ACTIVE_NEGOTIATIONS: '/negotiations/active',
  COMPLETED_NEGOTIATIONS: '/negotiations/completed',
  
  // Analytics Routes
  ANALYTICS: '/analytics',
  IMPACT_ANALYSIS: '/analytics/impact',
  PEER_COMPARISON: '/analytics/peer-comparison',
  HISTORICAL_TRENDS: '/analytics/historical-trends',
  ATTORNEY_PERFORMANCE: '/analytics/attorney-performance',
  CUSTOM_REPORTS: '/analytics/custom-reports',
  
  // Attorney Routes
  ATTORNEYS: '/attorneys',
  ATTORNEY_LIST: '/attorneys/list',
  STAFF_CLASS: '/attorneys/staff-class',
  
  // Messaging Routes
  MESSAGES: '/messages',
  ALL_MESSAGES: '/messages/all',
  MESSAGES_BY_NEGOTIATION: '/messages/negotiation',
  
  // OCG Routes
  OCG: '/ocg',
  OCG_LIST: '/ocg/list',
  OCG_EDITOR: '/ocg/editor',
  
  // Settings Routes
  SETTINGS: '/settings',
  ORGANIZATION_SETTINGS: '/settings/organization',
  USER_MANAGEMENT: '/settings/users',
  RATE_RULES: '/settings/rate-rules',
  PEER_GROUPS: '/settings/peer-groups',
  INTEGRATIONS: '/settings/integrations',
  NOTIFICATION_SETTINGS: '/settings/notifications',
  AI_CONFIGURATION: '/settings/ai-configuration',
};