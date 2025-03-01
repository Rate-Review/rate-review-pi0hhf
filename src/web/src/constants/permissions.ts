/**
 * permissions.ts
 * 
 * This file defines the permission-based access control system for Justice Bid,
 * including roles, actions, resources, scopes, and permission templates.
 */

/**
 * User roles within the application
 */
export const ROLES = {
  SYSTEM_ADMIN: 'system_admin',
  ORG_ADMIN: 'org_admin',
  RATE_ADMIN: 'rate_admin',
  APPROVER: 'approver',
  ANALYST: 'analyst',
  STANDARD_USER: 'standard_user'
};

/**
 * Permission actions that can be performed
 */
export const ACTIONS = {
  CREATE: 'create',
  READ: 'read',
  UPDATE: 'update',
  DELETE: 'delete',
  APPROVE: 'approve',
  REJECT: 'reject',
  COUNTER: 'counter',
  SUBMIT: 'submit',
  EXPORT: 'export',
  IMPORT: 'import',
  ALL: '*' // Wildcard for all actions
};

/**
 * Resources that can be acted upon
 */
export const RESOURCES = {
  RATES: 'rates',
  NEGOTIATIONS: 'negotiations',
  ATTORNEYS: 'attorneys',
  STAFF_CLASSES: 'staff_classes',
  ANALYTICS: 'analytics',
  REPORTS: 'reports',
  MESSAGES: 'messages',
  OCG: 'ocg',
  USERS: 'users',
  ORGANIZATIONS: 'organizations',
  PEER_GROUPS: 'peer_groups',
  INTEGRATIONS: 'integrations',
  SETTINGS: 'settings',
  ALL: '*' // Wildcard for all resources
};

/**
 * Scopes define the reach of permissions
 */
export const SCOPES = {
  ALL: '*', // All entities
  ORGANIZATION: 'organization', // Within the user's organization
  PEER_GROUP: 'peer_group', // Within the user's peer groups
  FIRM: 'firm', // Specific law firm
  CLIENT: 'client', // Specific client
  SELF: 'self' // User's own data
};

/**
 * Creates a standardized permission string by combining action, resource, and scope
 * 
 * @param action - The action being performed
 * @param resource - The resource being acted upon
 * @param scope - The scope of the permission
 * @returns Formatted permission string in the format 'action:resource:scope'
 */
export const permissionFormatter = (action: string, resource: string, scope: string): string => {
  return `${action}:${resource}:${scope}`;
};

/**
 * Checks if a user has a specific permission based on their permission array
 * 
 * @param userPermissions - Array of user's permissions
 * @param action - The action to check
 * @param resource - The resource to check
 * @param scope - The scope to check
 * @returns True if the user has the permission, false otherwise
 */
export const hasPermission = (
  userPermissions: string[],
  action: string,
  resource: string,
  scope: string
): boolean => {
  const specificPermission = permissionFormatter(action, resource, scope);
  
  // Check for the specific permission
  if (userPermissions.includes(specificPermission)) {
    return true;
  }
  
  // Check for wildcard permissions
  const wildcardResource = permissionFormatter(action, RESOURCES.ALL, scope);
  const wildcardAction = permissionFormatter(ACTIONS.ALL, resource, scope);
  const wildcardBoth = permissionFormatter(ACTIONS.ALL, RESOURCES.ALL, scope);
  const wildcardAll = permissionFormatter(ACTIONS.ALL, RESOURCES.ALL, SCOPES.ALL);
  
  return (
    userPermissions.includes(wildcardResource) ||
    userPermissions.includes(wildcardAction) ||
    userPermissions.includes(wildcardBoth) ||
    userPermissions.includes(wildcardAll)
  );
};

/**
 * Predefined permission templates for each role
 */
export const PERMISSION_TEMPLATES = {
  /**
   * System Administrator - Complete access to all features
   */
  SYSTEM_ADMIN_TEMPLATE: [
    permissionFormatter(ACTIONS.ALL, RESOURCES.ALL, SCOPES.ALL)
  ],
  
  /**
   * Organization Administrator - Full access to their organization
   */
  ORG_ADMIN_TEMPLATE: [
    // Organization management permissions
    permissionFormatter(ACTIONS.ALL, RESOURCES.ORGANIZATIONS, SCOPES.ORGANIZATION),
    permissionFormatter(ACTIONS.ALL, RESOURCES.USERS, SCOPES.ORGANIZATION),
    permissionFormatter(ACTIONS.ALL, RESOURCES.SETTINGS, SCOPES.ORGANIZATION),
    permissionFormatter(ACTIONS.ALL, RESOURCES.PEER_GROUPS, SCOPES.ORGANIZATION),
    permissionFormatter(ACTIONS.ALL, RESOURCES.INTEGRATIONS, SCOPES.ORGANIZATION),
    
    // Full access to all other resources within the organization
    permissionFormatter(ACTIONS.ALL, RESOURCES.RATES, SCOPES.ORGANIZATION),
    permissionFormatter(ACTIONS.ALL, RESOURCES.NEGOTIATIONS, SCOPES.ORGANIZATION),
    permissionFormatter(ACTIONS.ALL, RESOURCES.ATTORNEYS, SCOPES.ORGANIZATION),
    permissionFormatter(ACTIONS.ALL, RESOURCES.STAFF_CLASSES, SCOPES.ORGANIZATION),
    permissionFormatter(ACTIONS.ALL, RESOURCES.ANALYTICS, SCOPES.ORGANIZATION),
    permissionFormatter(ACTIONS.ALL, RESOURCES.REPORTS, SCOPES.ORGANIZATION),
    permissionFormatter(ACTIONS.ALL, RESOURCES.MESSAGES, SCOPES.ORGANIZATION),
    permissionFormatter(ACTIONS.ALL, RESOURCES.OCG, SCOPES.ORGANIZATION)
  ],
  
  /**
   * Rate Administrator - Can manage rates and negotiations
   */
  RATE_ADMIN_TEMPLATE: [
    // Rate management permissions
    permissionFormatter(ACTIONS.ALL, RESOURCES.RATES, SCOPES.ORGANIZATION),
    permissionFormatter(ACTIONS.ALL, RESOURCES.NEGOTIATIONS, SCOPES.ORGANIZATION),
    permissionFormatter(ACTIONS.ALL, RESOURCES.ATTORNEYS, SCOPES.ORGANIZATION),
    permissionFormatter(ACTIONS.ALL, RESOURCES.STAFF_CLASSES, SCOPES.ORGANIZATION),
    permissionFormatter(ACTIONS.ALL, RESOURCES.MESSAGES, SCOPES.ORGANIZATION),
    
    // Read-only access to analytics
    permissionFormatter(ACTIONS.READ, RESOURCES.ANALYTICS, SCOPES.ORGANIZATION),
    permissionFormatter(ACTIONS.READ, RESOURCES.REPORTS, SCOPES.ORGANIZATION),
    
    // OCG permissions
    permissionFormatter(ACTIONS.READ, RESOURCES.OCG, SCOPES.ORGANIZATION),
    permissionFormatter(ACTIONS.UPDATE, RESOURCES.OCG, SCOPES.ORGANIZATION),
    
    // Limited user management
    permissionFormatter(ACTIONS.READ, RESOURCES.USERS, SCOPES.ORGANIZATION),
    
    // Limited settings access
    permissionFormatter(ACTIONS.READ, RESOURCES.SETTINGS, SCOPES.ORGANIZATION)
  ],
  
  /**
   * Approver - Can approve/reject rates, but not create them
   */
  APPROVER_TEMPLATE: [
    // Approval permissions
    permissionFormatter(ACTIONS.READ, RESOURCES.RATES, SCOPES.ORGANIZATION),
    permissionFormatter(ACTIONS.APPROVE, RESOURCES.RATES, SCOPES.ORGANIZATION),
    permissionFormatter(ACTIONS.REJECT, RESOURCES.RATES, SCOPES.ORGANIZATION),
    permissionFormatter(ACTIONS.COUNTER, RESOURCES.RATES, SCOPES.ORGANIZATION),
    
    // Negotiation permissions
    permissionFormatter(ACTIONS.READ, RESOURCES.NEGOTIATIONS, SCOPES.ORGANIZATION),
    permissionFormatter(ACTIONS.UPDATE, RESOURCES.NEGOTIATIONS, SCOPES.ORGANIZATION),
    
    // Messaging permissions
    permissionFormatter(ACTIONS.ALL, RESOURCES.MESSAGES, SCOPES.ORGANIZATION),
    
    // Read access to supporting data
    permissionFormatter(ACTIONS.READ, RESOURCES.ATTORNEYS, SCOPES.ORGANIZATION),
    permissionFormatter(ACTIONS.READ, RESOURCES.STAFF_CLASSES, SCOPES.ORGANIZATION),
    permissionFormatter(ACTIONS.READ, RESOURCES.ANALYTICS, SCOPES.ORGANIZATION),
    permissionFormatter(ACTIONS.READ, RESOURCES.REPORTS, SCOPES.ORGANIZATION),
    permissionFormatter(ACTIONS.READ, RESOURCES.OCG, SCOPES.ORGANIZATION)
  ],
  
  /**
   * Analyst - Can view and analyze data but not modify it
   */
  ANALYST_TEMPLATE: [
    // Read-only access to most resources
    permissionFormatter(ACTIONS.READ, RESOURCES.RATES, SCOPES.ORGANIZATION),
    permissionFormatter(ACTIONS.READ, RESOURCES.NEGOTIATIONS, SCOPES.ORGANIZATION),
    permissionFormatter(ACTIONS.READ, RESOURCES.ATTORNEYS, SCOPES.ORGANIZATION),
    permissionFormatter(ACTIONS.READ, RESOURCES.STAFF_CLASSES, SCOPES.ORGANIZATION),
    permissionFormatter(ACTIONS.READ, RESOURCES.OCG, SCOPES.ORGANIZATION),
    
    // Full analytics permissions
    permissionFormatter(ACTIONS.ALL, RESOURCES.ANALYTICS, SCOPES.ORGANIZATION),
    permissionFormatter(ACTIONS.ALL, RESOURCES.REPORTS, SCOPES.ORGANIZATION),
    
    // Export permissions
    permissionFormatter(ACTIONS.EXPORT, RESOURCES.RATES, SCOPES.ORGANIZATION),
    permissionFormatter(ACTIONS.EXPORT, RESOURCES.NEGOTIATIONS, SCOPES.ORGANIZATION),
    
    // Limited messaging
    permissionFormatter(ACTIONS.READ, RESOURCES.MESSAGES, SCOPES.ORGANIZATION),
    permissionFormatter(ACTIONS.CREATE, RESOURCES.MESSAGES, SCOPES.SELF)
  ],
  
  /**
   * Standard User - Basic access
   */
  STANDARD_USER_TEMPLATE: [
    // Read access to organization data
    permissionFormatter(ACTIONS.READ, RESOURCES.RATES, SCOPES.ORGANIZATION),
    permissionFormatter(ACTIONS.READ, RESOURCES.NEGOTIATIONS, SCOPES.ORGANIZATION),
    permissionFormatter(ACTIONS.READ, RESOURCES.ATTORNEYS, SCOPES.ORGANIZATION),
    permissionFormatter(ACTIONS.READ, RESOURCES.STAFF_CLASSES, SCOPES.ORGANIZATION),
    
    // Limited analytics
    permissionFormatter(ACTIONS.READ, RESOURCES.ANALYTICS, SCOPES.ORGANIZATION),
    permissionFormatter(ACTIONS.READ, RESOURCES.REPORTS, SCOPES.ORGANIZATION),
    
    // Messaging for self
    permissionFormatter(ACTIONS.READ, RESOURCES.MESSAGES, SCOPES.ORGANIZATION),
    permissionFormatter(ACTIONS.CREATE, RESOURCES.MESSAGES, SCOPES.SELF),
    permissionFormatter(ACTIONS.UPDATE, RESOURCES.MESSAGES, SCOPES.SELF),
    
    // User profile
    permissionFormatter(ACTIONS.READ, RESOURCES.USERS, SCOPES.SELF),
    permissionFormatter(ACTIONS.UPDATE, RESOURCES.USERS, SCOPES.SELF)
  ]
};