import React, {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState, // React v18.0+
} from 'react'; //  ^18.0.0
import { useAuth } from '../hooks/useAuth';
import { PERMISSIONS } from '../constants/permissions';
import { useOrganizationContext } from './OrganizationContext';
import { Permission } from '../types/auth'; // Import Permission type

/**
 * @interface PermissionContextValue
 * @description Interface defining the structure of the permission context value.
 */
interface PermissionContextValue {
  hasPermission: (permission: string, options?: any) => boolean;
  hasAnyPermission: (permissions: string[], options?: any) => boolean;
  hasAllPermissions: (permissions: string[], options?: any) => boolean;
  resetPermissionCache: () => void;
}

/**
 * @const PermissionContext
 * @description Creates a context for managing permissions.
 */
export const PermissionContext = createContext<PermissionContextValue | undefined>(
  undefined
);

/**
 * @function usePermissionContext
 * @description Hook to access the permission context.
 * @returns {PermissionContextValue} The permission context value.
 * @throws {Error} If used outside of a PermissionProvider.
 */
export const usePermissionContext = (): PermissionContextValue => {
  const context = useContext(PermissionContext);
  if (!context) {
    throw new Error(
      'usePermissionContext must be used within a PermissionProvider'
    );
  }
  return context;
};

/**
 * @interface PermissionProviderProps
 * @description Interface for the PermissionProvider props.
 */
interface PermissionProviderProps {
  children: React.ReactNode;
}

/**
 * @component PermissionProvider
 * @description Provides permission checking functionality to the application.
 * @param {PermissionProviderProps} { children } - The children to render within the provider.
 * @returns {JSX.Element} A PermissionContext.Provider wrapping the children.
 */
export const PermissionProvider: React.FC<PermissionProviderProps> = ({
  children,
}) => {
  // IE1: Access the current user and authentication status from the useAuth hook.
  const { isAuthenticated, currentUser } = useAuth();

  // IE3: Access the current organization context.
  const { currentOrganization } = useOrganizationContext();

  // LD1: Initialize a state variable to cache permission check results.
  const [permissionCache, setPermissionCache] = useState<Record<string, boolean>>({});

  /**
   * @function hasPermission
   * @description Checks if the current user has a specific permission.
   * @param {string} permission - The permission to check.
   * @param {object} options - Optional parameters for the permission check.
   * @returns {boolean} True if the user has the permission, false otherwise.
   */
  const hasPermission = useCallback(
    (permission: string, options: any = {}): boolean => {
      // 1. Check if user is authenticated
      if (!isAuthenticated || !currentUser) {
        return false;
      }

      // 2. Check if the permission exists in the permission cache
      if (permissionCache[permission] !== undefined) {
        return permissionCache[permission];
      }

      // 3. Check if the user has the required permission based on their roles and direct permissions
      let hasPerm = currentUser.permissions.includes(permission as any);

      // 4. Consider organization context if relevant for the permission
      if (currentOrganization && permission.includes(':organization')) {
        // Adjust permission check based on organization context
        // Example: Check if the user has the permission within their organization
        // This might involve checking if the permission is granted to the organization
        // or if the user's role grants the permission within the organization
        // This is a placeholder and needs to be adapted to your specific logic
        // hasPerm = hasPerm && checkOrganizationPermissions(permission, currentOrganization);
      }

      // 5. Consider entity-specific permissions if provided in options
      if (options?.entityId) {
        // Adjust permission check based on entity-specific permissions
        // Example: Check if the user has the permission for a specific rate or negotiation
        // This might involve checking if the user is the owner of the entity
        // or if the entity has specific permissions granted to the user
        // This is a placeholder and needs to be adapted to your specific logic
        // hasPerm = hasPerm && checkEntityPermissions(permission, options.entityId);
      }

      // 6. Cache the result for future checks
      setPermissionCache((prevCache) => ({ ...prevCache, [permission]: hasPerm }));

      // 7. Return the permission check result
      return hasPerm;
    },
    [isAuthenticated, currentUser, currentOrganization, permissionCache]
  );

  /**
   * @function hasAnyPermission
   * @description Checks if the user has any of the given permissions.
   * @param {string[]} permissions - An array of permissions to check.
   * @param {object} options - Optional parameters for the permission check.
   * @returns {boolean} True if the user has any of the specified permissions, false otherwise.
   */
  const hasAnyPermission = useCallback(
    (permissions: string[], options: any = {}): boolean => {
      // 1. Loop through each permission in the array
      for (const permission of permissions) {
        // 2. For each permission, call hasPermission function
        if (hasPermission(permission, options)) {
          // 3. If any permission check returns true, return true
          return true;
        }
      }

      // 4. Otherwise return false
      return false;
    },
    [hasPermission]
  );

  /**
   * @function hasAllPermissions
   * @description Checks if the user has all of the given permissions.
   * @param {string[]} permissions - An array of permissions to check.
   * @param {object} options - Optional parameters for the permission check.
   * @returns {boolean} True if the user has all of the specified permissions, false otherwise.
   */
  const hasAllPermissions = useCallback(
    (permissions: string[], options: any = {}): boolean => {
      // 1. Loop through each permission in the array
      for (const permission of permissions) {
        // 2. For each permission, call hasPermission function
        if (!hasPermission(permission, options)) {
          // 3. If any permission check returns false, return false
          return false;
        }
      }

      // 4. Otherwise return true
      return true;
    },
    [hasPermission]
  );

  /**
   * @function resetPermissionCache
   * @description Clears the permission cache to force fresh permission checks.
   * @returns {void}
   */
  const resetPermissionCache = useCallback(() => {
    // 1. Clear the permission cache object/state
    setPermissionCache({});
  }, []);

  // LD1: Define the context value object.
  const contextValue: PermissionContextValue = {
    hasPermission,
    hasAnyPermission,
    hasAllPermissions,
    resetPermissionCache,
  };

  // LD1: Return the PermissionContext.Provider with the context value and children.
  return (
    <PermissionContext.Provider value={contextValue}>
      {children}
    </PermissionContext.Provider>
  );
};

/**
 * @function usePermissionContext
 * @description Hook to access the permission context.
 * @returns {PermissionContextValue} The permission context value.
 * @throws {Error} If used outside of a PermissionProvider.
 */
export const usePermissionContext = (): PermissionContextValue => {
  const context = useContext(PermissionContext);
  if (!context) {
    throw new Error(
      'usePermissionContext must be used within a PermissionProvider'
    );
  }
  return context;
};

// Export PermissionContext for testing purposes
export { PermissionContext };