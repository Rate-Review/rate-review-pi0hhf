/**
 * Authentication thunks for Redux store.
 * Handles all asynchronous authentication operations including login, registration, logout,
 * token refresh, MFA, and user profile management.
 * 
 * @version 1.0.0
 */

import { createAsyncThunk, Dispatch } from '@reduxjs/toolkit'; // ^1.9.5
import { toast } from 'react-toastify'; // ^9.1.3
import { handleApiError } from '../../api/errorHandling';
import { 
  login,
  register,
  logout,
  refreshToken,
  updateProfile,
  setupMFA,
  verifyMFA,
  resetPassword,
  fetchUserProfile
} from '../../services/auth';
import {
  LoginRequest,
  RegisterRequest,
  MfaSetupRequest,
  MfaVerifyRequest,
  ResetPasswordRequest,
  UpdateProfileRequest
} from '../../types/auth';

/**
 * Thunk action creator for user login
 * Dispatches authentication data on successful login
 */
export const loginUser = createAsyncThunk(
  'auth/login',
  async (credentials: LoginRequest, { rejectWithValue, dispatch }) => {
    try {
      dispatch({ type: 'auth/setLoading', payload: true });
      
      const response = await login(credentials);
      
      if (response.requiresTwoFactor) {
        // If MFA is required, return the MFA session data
        toast.info('Two-factor authentication required');
        return {
          mfaRequired: true,
          mfaToken: response.twoFactorToken
        };
      }
      
      // Login successful
      toast.success('Login successful');
      
      // Return auth data to be stored in Redux state
      return {
        user: response.user,
        token: response.token,
        refreshToken: response.refreshToken,
        isAuthenticated: true,
        mfaRequired: false,
        mfaToken: null
      };
    } catch (error) {
      const errorResponse = handleApiError(error);
      toast.error(`Login failed: ${errorResponse.message}`);
      return rejectWithValue(errorResponse);
    } finally {
      dispatch({ type: 'auth/setLoading', payload: false });
    }
  }
);

/**
 * Thunk action creator for user registration
 * Creates a new user account and optionally logs in
 */
export const registerUser = createAsyncThunk(
  'auth/register',
  async (userData: RegisterRequest, { rejectWithValue, dispatch }) => {
    try {
      dispatch({ type: 'auth/setLoading', payload: true });
      
      const response = await register(userData);
      
      toast.success('Registration successful');
      
      // If registration includes automatic login, return auth data
      if (response.token) {
        return {
          user: response.user,
          token: response.token,
          refreshToken: response.refreshToken,
          isAuthenticated: true
        };
      }
      
      // Otherwise just return success indication
      return { registered: true };
    } catch (error) {
      const errorResponse = handleApiError(error);
      toast.error(`Registration failed: ${errorResponse.message}`);
      return rejectWithValue(errorResponse);
    } finally {
      dispatch({ type: 'auth/setLoading', payload: false });
    }
  }
);

/**
 * Thunk action creator for user logout
 * Logs out the user and clears auth state
 */
export const logoutUser = createAsyncThunk(
  'auth/logout',
  async (_, { dispatch }) => {
    try {
      await logout();
      dispatch({ type: 'auth/clearAuth' });
      toast.info('You have been logged out');
      return { success: true };
    } catch (error) {
      // Even if server-side logout fails, still clear local auth state
      dispatch({ type: 'auth/clearAuth' });
      console.error('Logout error:', error);
      return { success: true };
    }
  }
);

/**
 * Thunk action creator for refreshing authentication token
 * Used to maintain user session without requiring re-login
 */
export const refreshAuthToken = createAsyncThunk(
  'auth/refreshToken',
  async (_, { rejectWithValue, dispatch }) => {
    try {
      const response = await refreshToken();
      
      return {
        token: response.token,
        refreshToken: response.refreshToken
      };
    } catch (error) {
      const errorResponse = handleApiError(error);
      
      // If the token is invalid, clear auth state
      if (errorResponse.code === '401') {
        dispatch({ type: 'auth/clearAuth' });
      }
      
      return rejectWithValue(errorResponse);
    }
  }
);

/**
 * Thunk action creator for setting up MFA
 * Returns MFA setup information including QR code
 */
export const setupMfaAuthentication = createAsyncThunk(
  'auth/setupMfa',
  async (setupData: MfaSetupRequest, { rejectWithValue, dispatch }) => {
    try {
      dispatch({ type: 'auth/setLoading', payload: true });
      
      const response = await setupMFA(setupData);
      
      toast.success('MFA setup initiated. Scan the QR code with your authenticator app');
      
      return {
        qrCode: response.qrCode,
        secret: response.secret,
        backupCodes: response.backupCodes
      };
    } catch (error) {
      const errorResponse = handleApiError(error);
      toast.error(`MFA setup failed: ${errorResponse.message}`);
      return rejectWithValue(errorResponse);
    } finally {
      dispatch({ type: 'auth/setLoading', payload: false });
    }
  }
);

/**
 * Thunk action creator for verifying MFA code
 * Completes MFA verification and returns auth data
 */
export const verifyMfaCode = createAsyncThunk(
  'auth/verifyMfa',
  async (verifyData: MfaVerifyRequest, { rejectWithValue, dispatch }) => {
    try {
      dispatch({ type: 'auth/setLoading', payload: true });
      
      const response = await verifyMFA(verifyData.code, verifyData.secret);
      
      toast.success('Two-factor authentication successful');
      
      return {
        user: response.user,
        token: response.token,
        refreshToken: response.refreshToken,
        isAuthenticated: true,
        mfaRequired: false,
        mfaToken: null
      };
    } catch (error) {
      const errorResponse = handleApiError(error);
      toast.error(`Verification failed: ${errorResponse.message}`);
      return rejectWithValue(errorResponse);
    } finally {
      dispatch({ type: 'auth/setLoading', payload: false });
    }
  }
);

/**
 * Thunk action creator for password reset
 * Initiates or completes password reset process
 */
export const resetUserPassword = createAsyncThunk(
  'auth/resetPassword',
  async (resetData: ResetPasswordRequest, { rejectWithValue, dispatch }) => {
    try {
      dispatch({ type: 'auth/setLoading', payload: true });
      
      await resetPassword(resetData);
      
      toast.success('Password reset instructions have been sent to your email');
      
      return { success: true };
    } catch (error) {
      const errorResponse = handleApiError(error);
      toast.error(`Password reset failed: ${errorResponse.message}`);
      return rejectWithValue(errorResponse);
    } finally {
      dispatch({ type: 'auth/setLoading', payload: false });
    }
  }
);

/**
 * Thunk action creator for updating user profile
 * Updates user information and returns updated profile
 */
export const updateUserProfile = createAsyncThunk(
  'auth/updateProfile',
  async (profileData: UpdateProfileRequest, { rejectWithValue, dispatch }) => {
    try {
      dispatch({ type: 'auth/setLoading', payload: true });
      
      const updatedUser = await updateProfile(profileData);
      
      toast.success('Profile updated successfully');
      
      return { user: updatedUser };
    } catch (error) {
      const errorResponse = handleApiError(error);
      toast.error(`Profile update failed: ${errorResponse.message}`);
      return rejectWithValue(errorResponse);
    } finally {
      dispatch({ type: 'auth/setLoading', payload: false });
    }
  }
);

/**
 * Thunk action creator for fetching current user profile
 * Used to refresh user data in the state
 */
export const getUserProfile = createAsyncThunk(
  'auth/getUserProfile',
  async (_, { rejectWithValue, dispatch }) => {
    try {
      dispatch({ type: 'auth/setLoading', payload: true });
      
      const user = await fetchUserProfile();
      
      return { user };
    } catch (error) {
      const errorResponse = handleApiError(error);
      
      // Only show error notification for critical failures
      if (errorResponse.code !== '401') {
        toast.error(`Failed to fetch profile: ${errorResponse.message}`);
      }
      
      return rejectWithValue(errorResponse);
    } finally {
      dispatch({ type: 'auth/setLoading', payload: false });
    }
  }
);