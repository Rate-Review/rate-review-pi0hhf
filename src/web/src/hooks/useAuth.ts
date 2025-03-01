import { useState, useEffect, useCallback } from 'react'; //  ^18.0.0
import { useAppDispatch, useAppSelector } from '../store';
import {
  loginUser,
  logoutUser,
  refreshAuthToken,
  verifyMfaCode,
  resetUserPassword,
  getUserProfile,
} from '../store/auth/authThunks';
import {
  selectIsAuthenticated,
  selectCurrentUser,
  selectCurrentUserRole,
  selectAuthLoading,
  selectAuthError,
  selectMfaRequired,
  authActions,
} from '../store/auth/authSlice';
import {
  LoginCredentials,
  MfaCredentials,
  ResetPasswordCredentials,
  User,
  UserRole,
} from '../types/auth';
import { OrganizationType } from '../types/organization';

/**
 * @description Custom hook that provides authentication functionality and state for components
 * @returns {object} Auth hook interface with authentication state and methods
 */
export const useAuth = () => {
  // Access Redux store dispatch and selector functions
  const dispatch = useAppDispatch();

  // Select authentication state from Redux store
  const isAuthenticated = useAppSelector(selectIsAuthenticated);
  const currentUser = useAppSelector(selectCurrentUser);
  const userRole = useAppSelector(selectCurrentUserRole);
  const loading = useAppSelector(selectAuthLoading);
  const error = useAppSelector(selectAuthError);
  const mfaRequired = useAppSelector(selectMfaRequired);

  /**
   * @description Defines login function that dispatches login thunk with credentials
   * @param {LoginCredentials} credentials - Login credentials
   * @returns {Promise<void>}
   */
  const login = useCallback(
    (credentials: LoginCredentials) => {
      return dispatch(loginUser(credentials)) as any;
    },
    [dispatch]
  );

  /**
   * @description Defines logout function that dispatches logout thunk
   * @returns {Promise<void>}
   */
  const logout = useCallback(() => {
    return dispatch(logoutUser()) as any;
  }, [dispatch]);

  /**
   * @description Defines verifyMfa function that handles multi-factor authentication verification
   * @param {MfaCredentials} credentials - MFA credentials
   * @returns {Promise<void>}
   */
  const verifyMfa = useCallback(
    (credentials: MfaCredentials) => {
      return dispatch(verifyMfaCode(credentials)) as any;
    },
    [dispatch]
  );

  /**
   * @description Defines resetPassword function for password reset functionality
   * @param {ResetPasswordCredentials} credentials - Reset password credentials
   * @returns {Promise<void>}
   */
  const resetPassword = useCallback(
    (credentials: ResetPasswordCredentials) => {
      return dispatch(resetUserPassword(credentials)) as any;
    },
    [dispatch]
  );

  /**
   * @description Defines refreshTokenSilently function to refresh JWT token when needed
   * @returns {Promise<void>}
   */
  const refreshTokenSilently = useCallback(() => {
    return dispatch(refreshAuthToken()) as any;
  }, [dispatch]);

    /**
   * @description Defines checkAuthStatus function to verify current authentication status
   * @returns {Promise<void>}
   */
  const checkAuthStatus = useCallback(() => {
    return dispatch(getUserProfile()) as any;
  }, [dispatch]);

  /**
   * @description Checks if the current user has a specific role
   * @param {UserRole} role - The role to check for
   * @returns {boolean} - True if the user has the role, false otherwise
   */
  const hasRole = (role: UserRole): boolean => {
    return currentUser?.role === role;
  };

  /**
   * @description Checks if the current user's organization is of a specific type
   * @param {OrganizationType} orgType - The organization type to check for
   * @returns {boolean} - True if the organization is of the specified type, false otherwise
   */
  const isOrgType = (orgType: OrganizationType): boolean => {
    return currentUser?.organization.type === orgType;
  };

  // Set up useEffect to check authentication status on component mount
  useEffect(() => {
    dispatch(authActions.initialize());
    checkAuthStatus();
  }, [dispatch, checkAuthStatus]);

  // Set up useEffect to refresh token before expiration
  useEffect(() => {
    let intervalId: NodeJS.Timeout;

    if (isAuthenticated) {
      // Refresh the token every 5 minutes
      intervalId = setInterval(() => {
        refreshTokenSilently();
      }, 5 * 60 * 1000);
    }

    return () => clearInterval(intervalId);
  }, [isAuthenticated, refreshTokenSilently]);

  // Return authentication state and methods as an object
  return {
    isAuthenticated,
    currentUser,
    userRole,
    loading,
    error,
    mfaRequired,
    login,
    logout,
    verifyMfa,
    resetPassword,
    refreshTokenSilently,
    checkAuthStatus,
    hasRole,
    isOrgType
  };
};