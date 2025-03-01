/**
 * Redux slice for authentication state management in the Justice Bid Rate Negotiation System.
 * This slice handles user authentication, token management, MFA verification, and session handling.
 * 
 * @packageDocumentation
 * @module store/auth
 * @version 1.0.0
 */

import { createSlice, PayloadAction } from '@reduxjs/toolkit'; // v1.9.5
import { AuthState } from '../../types/auth';
import { User } from '../../types/user';
import storage from '../../utils/storage';

/**
 * Initial authentication state values
 */
const initialState: AuthState = {
  user: null,
  token: null,
  refreshToken: null,
  isAuthenticated: false,
  isInitialized: false,
  loading: false,
  error: null,
  mfaRequired: false,
  mfaToken: null
};

/**
 * Authentication slice containing reducers for managing auth state
 */
const authSlice = createSlice({
  name: 'auth',
  initialState,
  reducers: {
    /**
     * Updates authentication state with token and user information
     */
    setAuth: (state, action: PayloadAction<{ token?: string; refreshToken?: string; user?: User }>) => {
      const { token, refreshToken, user } = action.payload;
      
      if (token) {
        state.token = token;
        storage.setItem('token', token);
      }
      
      if (refreshToken) {
        state.refreshToken = refreshToken;
        storage.setItem('refresh_token', refreshToken);
      }
      
      if (user) {
        state.user = user;
      }
      
      state.isAuthenticated = true;
      state.loading = false;
      state.error = null;
    },
    
    /**
     * Updates only the user information in the auth state
     */
    setUser: (state, action: PayloadAction<User>) => {
      state.user = action.payload;
    },
    
    /**
     * Updates the loading state during authentication operations
     */
    setLoading: (state, action: PayloadAction<boolean>) => {
      state.loading = action.payload;
    },
    
    /**
     * Sets the error message when authentication operations fail
     */
    setError: (state, action: PayloadAction<string>) => {
      state.error = action.payload;
      state.loading = false;
    },
    
    /**
     * Clears any current error message
     */
    clearError: (state) => {
      state.error = null;
    },
    
    /**
     * Updates the MFA requirement state during authentication
     */
    setMfaRequired: (state, action: PayloadAction<{ required: boolean; token?: string }>) => {
      state.mfaRequired = action.payload.required;
      state.mfaToken = action.payload.token || null;
    },
    
    /**
     * Clears the MFA state after verification or cancelation
     */
    clearMfa: (state) => {
      state.mfaRequired = false;
      state.mfaToken = null;
    },
    
    /**
     * Initializes authentication state from persistent storage
     */
    initialize: (state) => {
      const token = storage.getItem<string>('token');
      const refreshToken = storage.getItem<string>('refresh_token');
      
      if (token && refreshToken) {
        state.token = token;
        state.refreshToken = refreshToken;
        state.isAuthenticated = true;
      }
      
      state.isInitialized = true;
    },
    
    /**
     * Clears authentication state on logout
     */
    logout: (state) => {
      // Clear auth state
      state.user = null;
      state.token = null;
      state.refreshToken = null;
      state.isAuthenticated = false;
      state.mfaRequired = false;
      state.mfaToken = null;
      state.error = null;
      
      // Remove tokens from storage
      storage.removeItem('token');
      storage.removeItem('refresh_token');
    }
  }
});

// Export actions for use in components and thunks
export const authActions = authSlice.actions;

// Export reducer as default for use in store configuration
export default authSlice.reducer;