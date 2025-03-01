import { useCallback, useMemo } from 'react'; //  ^18.0.0
import { useAuth } from './useAuth';
import { usePermissionContext } from '../context/PermissionContext';
import { ACTIONS, RESOURCES, SCOPES } from '../constants/permissions';

/**
 * @description Custom hook that provides permission checking functionality for the Justice Bid Rate Negotiation System.
 * Allows components to verify if the current user has specific permissions to perform actions on resources within various scopes.
 * @returns {object} Object containing permission checking functions
 */
export const usePermissions = () => {
  // IE1: Get authentication state using useAuth hook
  const { isAuthenticated, currentUser } = useAuth();

  // IE2: Get permission functions from usePermissionContext
  const { hasPermission: contextHasPermission, resetPermissionCache } = usePermissionContext();

  /**
   * @function can
   * @description Checks if the current user has permission to perform an action on a resource within a scope
   * @param {string} action - The action to check
   * @param {string} resource - The resource to check
   * @param {string} scope - The scope to check
   * @param {object} options - Optional parameters for the permission check
   * @returns {boolean} Whether the user has the specified permission
   */
  const can = useCallback(
    (action: string, resource: string, scope: string, options: any = {}): boolean => {
      // 1. Check if the user is authenticated
      if (!isAuthenticated || !currentUser) {
        return false;
      }

      // 2. Format the permission string by combining action, resource, and scope
      const permission = `${action}:${resource}:${scope}`;

      // 3. Call hasPermission from the permission context with the formatted permission
      const hasPerm = contextHasPermission(permission, options);

      // 4. Return the result of the permission check
      return hasPerm;
    },
    [isAuthenticated, currentUser, contextHasPermission]
  );

  /**
   * @function canAny
   * @description Checks if the current user has any of the specified permissions
   * @param {array} permissionChecks - An array of permission checks
   * @param {object} options - Optional parameters for the permission check
   * @returns {boolean} Whether the user has any of the specified permissions
   */
  const canAny = useCallback(
    (permissionChecks: { action: string; resource: string; scope: string }[], options: any = {}): boolean => {
      // 1. Check if the user is authenticated
      if (!isAuthenticated || !currentUser) {
        return false;
      }

      // 2. Loop through each permission check in the array
      for (const permissionCheck of permissionChecks) {
        // 3. Call can function for each permission check
        if (can(permissionCheck.action, permissionCheck.resource, permissionCheck.scope, options)) {
          // 4. If any permission check returns true, return true
          return true;
        }
      }

      // 5. Otherwise return false
      return false;
    },
    [isAuthenticated, currentUser, can]
  );

  /**
   * @function canAll
   * @description Checks if the current user has all of the specified permissions
   * @param {array} permissionChecks - An array of permission checks
   * @param {object} options - Optional parameters for the permission check
   * @returns {boolean} Whether the user has all of the specified permissions
   */
  const canAll = useCallback(
    (permissionChecks: { action: string; resource: string; scope: string }[], options: any = {}): boolean => {
      // 1. Check if the user is authenticated
      if (!isAuthenticated || !currentUser) {
        return false;
      }

      // 2. Loop through each permission check in the array
      for (const permissionCheck of permissionChecks) {
        // 3. Call can function for each permission check
        if (!can(permissionCheck.action, permissionCheck.resource, permissionCheck.scope, options)) {
          // 4. If any permission check returns false, return false
          return false;
        }
      }

      // 5. Otherwise return true
      return true;
    },
    [isAuthenticated, currentUser, can]
  );

  /**
   * @function canForEntity
   * @description Checks if the current user has permission for a specific entity
   * @param {string} action - The action to check
   * @param {string} resource - The resource to check
   * @param {object} entity - The entity to check permissions for
   * @param {object} options - Optional parameters for the permission check
   * @returns {boolean} Whether the user has the specified permission for the entity
   */
  const canForEntity = useCallback(
    (action: string, resource: string, entity: any, options: any = {}): boolean => {
      // 1. Check if the user is authenticated
      if (!isAuthenticated || !currentUser) {
        return false;
      }

      // 2. Determine the appropriate scope based on the entity and current user
      let scope = SCOPES.ORGANIZATION; // Default scope

      // 3. Format the permission string by combining action, resource, and determined scope
      const permission = `${action}:${resource}:${scope}`;

      // 4. Call hasPermission from the permission context with the formatted permission and entity context
      const hasPerm = contextHasPermission(permission, { ...options, entity });

      // 5. Return the result of the permission check
      return hasPerm;
    },
    [isAuthenticated, currentUser, contextHasPermission]
  );

  /**
   * @function refreshPermissions
   * @description Resets the permission cache to force fresh permission checks
   * @returns {void} No return value
   */
  const refreshPermissions = useCallback(() => {
    // 1. Call resetPermissionCache from the permission context
    resetPermissionCache();
  }, [resetPermissionCache]);

  // LD2: Return all permission checking functions in an object
  return useMemo(() => ({
    can,
    canAny,
    canAll,
    canForEntity,
    refreshPermissions
  }), [can, canAny, canAll, canForEntity, refreshPermissions]);
};