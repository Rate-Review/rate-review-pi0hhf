/**
 * Service for handling authentication operations such as login, logout, token management,
 * SSO integration, and MFA verification.
 * 
 * @version 1.0.0
 */

import jwtDecode from 'jwt-decode'; // ^3.1.2
import api from './api';
import * as storage from '../utils/storage';
import { 
  AuthResponse, 
  TokenResponse,
  MFASetupResponse,
  LoginCredentials
} from '../types/auth';
import { User } from '../types/user';

/**
 * Authentication service providing functions for user authentication flows
 */
const authService = {
  /**
   * Authenticates a user with email and password credentials
   * @param credentials - Login credentials containing email and password
   * @returns Authentication response with user data and tokens
   */
  async login(credentials: LoginCredentials): Promise<AuthResponse> {
    const response = await api.post('/auth/login', credentials);
    
    if (response.token) {
      storage.setItem('auth_token', response.token);
      storage.setItem('refresh_token', response.refreshToken);
    }
    
    return response;
  },
  
  /**
   * Initiates Single Sign-On authentication flow
   * @param provider - SSO provider identifier (e.g., 'google', 'microsoft')
   */
  loginWithSSO(provider: string): void {
    const redirectUri = encodeURIComponent(`${window.location.origin}/auth/callback`);
    const ssoUrl = `/auth/sso?provider=${provider}&redirect_uri=${redirectUri}`;
    window.location.href = api.buildUrl(ssoUrl);
  },
  
  /**
   * Handles the callback from SSO provider after successful authentication
   * @param code - Authorization code returned from SSO provider
   * @returns Authentication response with user data and tokens
   */
  async handleSSOCallback(code: string): Promise<AuthResponse> {
    const response = await api.post('/auth/sso/callback', { code });
    
    if (response.token) {
      storage.setItem('auth_token', response.token);
      storage.setItem('refresh_token', response.refreshToken);
    }
    
    return response;
  },
  
  /**
   * Logs out the current user by invalidating tokens
   * @returns Promise resolving after logout completes
   */
  async logout(): Promise<void> {
    try {
      // Attempt to notify the server about logout
      await api.post('/auth/logout');
    } catch (error) {
      // Continue with local logout even if server request fails
      console.error('Logout error:', error);
    } finally {
      // Remove tokens from storage
      storage.removeItem('auth_token');
      storage.removeItem('refresh_token');
    }
  },
  
  /**
   * Refreshes the authentication token using the refresh token
   * @returns New authentication tokens
   */
  async refreshToken(): Promise<TokenResponse> {
    const refreshToken = this.getRefreshToken();
    
    if (!refreshToken) {
      throw new Error('No refresh token available');
    }
    
    const response = await api.post('/auth/refresh', { refreshToken });
    
    if (response.token) {
      storage.setItem('auth_token', response.token);
      storage.setItem('refresh_token', response.refreshToken);
    }
    
    return response;
  },
  
  /**
   * Initiates the password reset process for a user
   * @param email - Email address of the user
   * @returns Promise resolving after password reset request is sent
   */
  async resetPassword(email: string): Promise<void> {
    await api.post('/auth/reset-password', { email });
  },
  
  /**
   * Completes the password reset process with a new password
   * @param token - Password reset token from email
   * @param newPassword - New password to set
   * @returns Promise resolving after password has been reset
   */
  async confirmPasswordReset(token: string, newPassword: string): Promise<void> {
    await api.post('/auth/reset-password/confirm', { token, newPassword });
  },
  
  /**
   * Initiates Multi-Factor Authentication setup for a user
   * @returns MFA setup information including QR code data
   */
  async setupMFA(): Promise<MFASetupResponse> {
    return await api.post('/auth/setup-mfa');
  },
  
  /**
   * Verifies a Multi-Factor Authentication code during login or setup
   * @param code - Verification code from authenticator app
   * @param sessionId - Session ID for the verification process
   * @returns Authentication response with user data and tokens
   */
  async verifyMFA(code: string, sessionId: string): Promise<AuthResponse> {
    const response = await api.post('/auth/verify-mfa', { code, sessionId });
    
    if (response.token) {
      storage.setItem('auth_token', response.token);
      storage.setItem('refresh_token', response.refreshToken);
    }
    
    return response;
  },
  
  /**
   * Retrieves the current authentication token
   * @returns The authentication token or null if not authenticated
   */
  getToken(): string | null {
    return storage.getItem('auth_token');
  },
  
  /**
   * Stores the authentication token in storage
   * @param token - The authentication token to store
   */
  setToken(token: string): void {
    storage.setItem('auth_token', token);
  },
  
  /**
   * Retrieves the current refresh token
   * @returns The refresh token or null if not found
   */
  getRefreshToken(): string | null {
    return storage.getItem('refresh_token');
  },
  
  /**
   * Stores the refresh token in storage
   * @param token - The refresh token to store
   */
  setRefreshToken(token: string): void {
    storage.setItem('refresh_token', token);
  },
  
  /**
   * Checks if the user is currently authenticated
   * @returns True if the user is authenticated, false otherwise
   */
  isAuthenticated(): boolean {
    const token = this.getToken();
    if (!token) return false;
    
    try {
      const decoded: any = jwtDecode(token);
      // Check if token is expired
      return decoded.exp * 1000 > Date.now();
    } catch (error) {
      return false;
    }
  },
  
  /**
   * Retrieves the current authenticated user information
   * @returns User information if authenticated, null otherwise
   */
  getUser(): User | null {
    const token = this.getToken();
    if (!token) return null;
    
    try {
      const decoded: any = jwtDecode(token);
      // User information might be stored directly in the token payload
      // or in a nested user object depending on the backend implementation
      if (decoded.user) {
        return decoded.user as User;
      }
      
      // Extract user info from token claims if not in a user object
      return {
        id: decoded.userId || decoded.sub,
        email: decoded.email,
        name: decoded.name,
        organizationId: decoded.organizationId,
        role: decoded.role,
        permissions: decoded.permissions || [],
        organization: decoded.organization,
        isContact: decoded.isContact || false,
        lastVerified: decoded.lastVerified ? new Date(decoded.lastVerified) : new Date(),
        createdAt: decoded.createdAt ? new Date(decoded.createdAt) : new Date(),
        updatedAt: decoded.updatedAt ? new Date(decoded.updatedAt) : new Date(),
      } as User;
    } catch (error) {
      console.error('Error decoding user token:', error);
      return null;
    }
  },
  
  /**
   * Generates authentication headers for API requests
   * @returns Headers object with authorization token
   */
  getAuthHeaders(): { Authorization: string } {
    const token = this.getToken();
    return token ? { Authorization: `Bearer ${token}` } : {};
  }
};

export { authService };