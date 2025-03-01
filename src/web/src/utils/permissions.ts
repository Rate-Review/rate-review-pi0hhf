/**
 * permissions.ts
 * 
 * This file provides utility functions for checking user permissions against
 * various actions, resources, and scopes in the Justice Bid system. These functions
 * support the role-based access control system that governs frontend functionality.
 */

import { User, UserRole } from '../types/user';
import { 
  ACTIONS, 
  RESOURCES, 
  SCOPES, 
  ROLES, 
  PERMISSION_TEMPLATES, 
  permissionFormatter 
} from '../constants/permissions';

/**
 * Checks if a user has a specific permission
 * 
 * @param user The user to check permissions for
 * @param permission The permission string to check
 * @returns True if the user has the permission, false otherwise
 */
export const hasPermission = (user: User | null | undefined, permission: string): boolean => {
  // If no user or permissions, deny access
  if (!user || !user.permissions) {
    return false;
  }

  // System Administrators have all permissions
  if (user.role === UserRole.SYSTEM_ADMINISTRATOR) {
    return true;
  }

  // Check if the user has the specific permission
  return user.permissions.includes(permission);
};

/**
 * Checks if a user has any of the specified permissions
 * 
 * @param user The user to check permissions for
 * @param permissions Array of permission strings to check
 * @returns True if the user has any of the permissions, false otherwise
 */
export const hasAnyPermission = (user: User | null | undefined, permissions: string[]): boolean => {
  // If no user or permissions, deny access
  if (!user || !user.permissions) {
    return false;
  }

  // System Administrators have all permissions
  if (user.role === UserRole.SYSTEM_ADMINISTRATOR) {
    return true;
  }

  // Check if the user has any of the specified permissions
  return permissions.some(permission => 
    user.permissions.includes(permission)
  );
};

/**
 * Checks if a user has all of the specified permissions
 * 
 * @param user The user to check permissions for
 * @param permissions Array of permission strings to check
 * @returns True if the user has all of the permissions, false otherwise
 */
export const hasAllPermissions = (user: User | null | undefined, permissions: string[]): boolean => {
  // If no user or permissions, deny access
  if (!user || !user.permissions) {
    return false;
  }

  // System Administrators have all permissions
  if (user.role === UserRole.SYSTEM_ADMINISTRATOR) {
    return true;
  }

  // Check if the user has all of the specified permissions
  return permissions.every(permission => 
    user.permissions.includes(permission)
  );
};

/**
 * Checks if a user has a specific role
 * 
 * @param user The user to check the role for
 * @param role The role to check
 * @returns True if the user has the role, false otherwise
 */
export const hasRole = (user: User | null | undefined, role: UserRole): boolean => {
  if (!user || !user.role) {
    return false;
  }

  return user.role === role;
};

/**
 * Checks if a user is a System Administrator
 * 
 * @param user The user to check
 * @returns True if the user is a System Administrator, false otherwise
 */
export const isSystemAdmin = (user: User | null | undefined): boolean => {
  return hasRole(user, UserRole.SYSTEM_ADMINISTRATOR);
};

/**
 * Checks if a user is an Organization Administrator
 * 
 * @param user The user to check
 * @returns True if the user is an Organization Administrator, false otherwise
 */
export const isOrgAdmin = (user: User | null | undefined): boolean => {
  return hasRole(user, UserRole.ORGANIZATION_ADMINISTRATOR);
};

/**
 * Checks if a user can perform a specific action on a resource within a scope
 * 
 * @param user The user to check permissions for
 * @param action The action to be performed (from ACTIONS)
 * @param resource The resource to perform the action on (from RESOURCES)
 * @param scope The scope in which the action is performed (from SCOPES)
 * @returns True if the user can perform the action, false otherwise
 */
export const canPerformAction = (
  user: User | null | undefined,
  action: string,
  resource: string,
  scope: string
): boolean => {
  // If no user, deny access
  if (!user) {
    return false;
  }

  // System Administrators can perform any action
  if (isSystemAdmin(user)) {
    return true;
  }

  // Format the specific permission
  const specificPermission = permissionFormatter(action, resource, scope);
  
  // Check for specific permission
  if (hasPermission(user, specificPermission)) {
    return true;
  }

  // Check for wildcard permissions
  const wildcardActionPermission = permissionFormatter(ACTIONS.ALL, resource, scope);
  const wildcardResourcePermission = permissionFormatter(action, RESOURCES.ALL, scope);
  const wildcardBothPermission = permissionFormatter(ACTIONS.ALL, RESOURCES.ALL, scope);
  const wildcardAllPermission = permissionFormatter(ACTIONS.ALL, RESOURCES.ALL, SCOPES.ALL);

  return (
    hasPermission(user, wildcardActionPermission) ||
    hasPermission(user, wildcardResourcePermission) ||
    hasPermission(user, wildcardBothPermission) ||
    hasPermission(user, wildcardAllPermission)
  );
};

/**
 * Gets all resources that a user has read access to within a specific scope
 * 
 * @param user The user to check permissions for
 * @param scope The scope to check visibility in
 * @returns Array of resource names the user can access
 */
export const getVisibleResources = (
  user: User | null | undefined,
  scope: string
): string[] => {
  // If no user, return empty array
  if (!user) {
    return [];
  }

  // System Administrators can access all resources
  if (isSystemAdmin(user)) {
    return Object.values(RESOURCES);
  }

  // Filter resources to those the user has READ permission for
  return Object.values(RESOURCES).filter(resource => 
    resource !== RESOURCES.ALL && canPerformAction(user, ACTIONS.READ, resource, scope)
  );
};

/**
 * Gets all actions that a user can perform on a specific resource within a scope
 * 
 * @param user The user to check permissions for
 * @param resource The resource to check actions for
 * @param scope The scope in which the actions would be performed
 * @returns Array of action names the user can perform
 */
export const getAvailableActions = (
  user: User | null | undefined,
  resource: string,
  scope: string
): string[] => {
  // If no user, return empty array
  if (!user) {
    return [];
  }

  // System Administrators can perform all actions
  if (isSystemAdmin(user)) {
    return Object.values(ACTIONS);
  }

  // Filter actions to those the user can perform on the given resource
  return Object.values(ACTIONS).filter(action => 
    action !== ACTIONS.ALL && canPerformAction(user, action, resource, scope)
  );
};

/**
 * Checks if a user has permission to access a resource within a specific scope
 * 
 * @param user The user to check permissions for
 * @param resource The resource to check access for
 * @param scope The scope type (organization, peer_group, etc.)
 * @param scopeId The specific ID of the scope (organization ID, peer group ID, etc.)
 * @returns True if the user has access to the resource within the scope, false otherwise
 */
export const hasResourceScope = (
  user: User | null | undefined,
  resource: string,
  scope: string,
  scopeId: string
): boolean => {
  // If no user, deny access
  if (!user) {
    return false;
  }

  // System Administrators have access to all resources in all scopes
  if (isSystemAdmin(user)) {
    return true;
  }

  // Check if the user has read access to the resource in the given scope
  const hasReadPermission = canPerformAction(user, ACTIONS.READ, resource, scope);

  // For organization scope, check if it's the user's organization
  if (scope === SCOPES.ORGANIZATION) {
    return hasReadPermission && user.organizationId === scopeId;
  }

  // For other scopes, additional checks would be implemented here
  // This could involve checking user.scopeMappings or similar data
  // For now, just check the basic permission
  return hasReadPermission;
};

/**
 * Checks if a user can access a specific route based on required permissions
 * 
 * @param user The user to check permissions for
 * @param requiredPermissions Permission or array of permissions required for the route
 * @returns True if the user can access the route, false otherwise
 */
export const canAccessRoute = (
  user: User | null | undefined,
  requiredPermissions: string | string[]
): boolean => {
  // If no user, deny access
  if (!user) {
    return false;
  }

  // System Administrators can access all routes
  if (isSystemAdmin(user)) {
    return true;
  }

  // Convert single permission to array
  const permissions = Array.isArray(requiredPermissions) 
    ? requiredPermissions 
    : [requiredPermissions];

  // Check if the user has any of the required permissions
  return hasAnyPermission(user, permissions);
};