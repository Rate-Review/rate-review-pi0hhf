/**
 * API Routes Configuration
 * 
 * Defines all API route constants and URL construction functions for the
 * Justice Bid Rate Negotiation System frontend.
 */

// Base API URL from environment with fallback
const API_BASE_URL = process.env.REACT_APP_API_URL || '/api/v1';

/**
 * Constructs a complete API URL by joining the base URL with the provided path
 * @param path - The API endpoint path
 * @returns Complete API URL
 */
export const buildUrl = (path: string): string => {
  // Remove leading slash from path if present
  const formattedPath = path.startsWith('/') ? path.substring(1) : path;
  // Join API_BASE_URL with the formatted path
  return `${API_BASE_URL}/${formattedPath}`;
};

/**
 * Constructs an API URL with path parameters replaced by their values
 * @param path - The API endpoint path with parameters in :paramName format
 * @param params - Object with parameter names and values to substitute
 * @returns API URL with parameters substituted
 */
export const buildUrlWithParams = (
  path: string,
  params: Record<string, string | number>
): string => {
  // Create a copy of the path
  let result = path;
  
  // Loop through params and replace :paramName with param value
  Object.entries(params).forEach(([key, value]) => {
    result = result.replace(`:${key}`, value.toString());
  });
  
  // Return the path with params substituted
  return buildUrl(result);
};

/**
 * API Routes
 * 
 * Defines all API endpoints for the Justice Bid Rate Negotiation System.
 * Routes are organized by domain/feature and follow RESTful conventions.
 */
export const API_ROUTES = {
  AUTH: {
    LOGIN: '/auth/login',
    LOGOUT: '/auth/logout',
    REGISTER: '/auth/register',
    REFRESH_TOKEN: '/auth/refresh',
    RESET_PASSWORD: '/auth/reset-password',
    VERIFY_EMAIL: '/auth/verify-email',
    SETUP_MFA: '/auth/setup-mfa',
    VERIFY_MFA: '/auth/verify-mfa',
    ME: '/auth/me'
  },
  
  USERS: {
    BASE: '/users',
    BY_ID: '/users/:id',
    PERMISSIONS: '/users/:id/permissions'
  },
  
  ORGANIZATIONS: {
    BASE: '/organizations',
    BY_ID: '/organizations/:id',
    USERS: '/organizations/:id/users',
    SETTINGS: '/organizations/:id/settings'
  },
  
  ATTORNEYS: {
    BASE: '/attorneys',
    BY_ID: '/attorneys/:id',
    PERFORMANCE: '/attorneys/:id/performance'
  },
  
  STAFF_CLASSES: {
    BASE: '/staff-classes',
    BY_ID: '/staff-classes/:id'
  },
  
  PEER_GROUPS: {
    BASE: '/peer-groups',
    BY_ID: '/peer-groups/:id',
    MEMBERS: '/peer-groups/:id/members'
  },
  
  RATES: {
    BASE: '/rates',
    BY_ID: '/rates/:id',
    HISTORY: '/rates/:id/history',
    APPROVE: '/rates/:id/approve',
    REJECT: '/rates/:id/reject',
    COUNTER: '/rates/:id/counter',
    IMPORT: '/rates/import',
    EXPORT: '/rates/export'
  },
  
  NEGOTIATIONS: {
    BASE: '/negotiations',
    BY_ID: '/negotiations/:id',
    STATUS: '/negotiations/:id/status',
    RATES: '/negotiations/:id/rates',
    SUBMIT: '/negotiations/:id/submit',
    APPROVE: '/negotiations/:id/approve',
    REJECT: '/negotiations/:id/reject'
  },
  
  MESSAGES: {
    BASE: '/messages',
    BY_ID: '/messages/:id',
    THREAD: '/messages/thread/:id'
  },
  
  DOCUMENTS: {
    BASE: '/documents',
    BY_ID: '/documents/:id',
    DOWNLOAD: '/documents/:id/download',
    UPLOAD: '/documents/upload'
  },
  
  OCG: {
    BASE: '/ocg',
    BY_ID: '/ocg/:id',
    SECTIONS: '/ocg/:id/sections',
    ALTERNATIVES: '/ocg/:id/sections/:sectionId/alternatives',
    SELECTIONS: '/ocg/:id/selections'
  },
  
  ANALYTICS: {
    IMPACT: '/analytics/impact',
    COMPARISON: '/analytics/comparison',
    TRENDS: '/analytics/trends',
    PERFORMANCE: '/analytics/performance',
    REPORTS: '/analytics/reports',
    REPORT_BY_ID: '/analytics/reports/:id'
  },
  
  INTEGRATIONS: {
    EBILLING: {
      BASE: '/integrations/ebilling',
      TEST: '/integrations/ebilling/test',
      IMPORT: '/integrations/ebilling/import',
      EXPORT: '/integrations/ebilling/export',
      MAPPING: '/integrations/ebilling/mapping'
    },
    LAWFIRM: {
      BASE: '/integrations/lawfirm',
      TEST: '/integrations/lawfirm/test',
      IMPORT: '/integrations/lawfirm/import',
      EXPORT: '/integrations/lawfirm/export',
      MAPPING: '/integrations/lawfirm/mapping'
    },
    UNICOURT: {
      BASE: '/integrations/unicourt',
      SEARCH: '/integrations/unicourt/search',
      ATTORNEY: '/integrations/unicourt/attorney/:id',
      MAPPING: '/integrations/unicourt/mapping'
    },
    FILE: {
      IMPORT: '/integrations/file/import',
      EXPORT: '/integrations/file/export',
      TEMPLATES: '/integrations/file/templates'
    }
  },
  
  AI: {
    CHAT: '/ai/chat',
    RECOMMENDATIONS: {
      RATES: '/ai/recommendations/rates',
      ACTIONS: '/ai/recommendations/actions'
    },
    ANALYZE: '/ai/analyze',
    CONFIGURATION: '/ai/configuration'
  }
};