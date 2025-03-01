/**
 * TypeScript type definitions for authentication-related data structures in the Justice Bid Rate Negotiation System.
 * This file defines interfaces for login, registration, token management, and multi-factor authentication
 * that enable secure user authentication flows.
 */

import { User } from './user';

/**
 * Defines the authentication state structure maintained in the Redux store
 */
export interface AuthState {
  user: User | null;
  token: string | null;
  refreshToken: string | null;
  isAuthenticated: boolean;
  isInitialized: boolean;
  loading: boolean;
  error: string | null;
  mfaRequired: boolean;
  mfaToken: string | null;
}

/**
 * Defines the structure for login request payload
 */
export interface LoginRequest {
  email: string;
  password: string;
}

/**
 * Defines the structure for login response data
 */
export interface LoginResponse {
  user: User;
  token: string;
  refreshToken: string;
  requiresTwoFactor: boolean;
  twoFactorToken: string;
}

/**
 * Defines the structure for user registration request payload
 */
export interface RegisterRequest {
  email: string;
  password: string;
  name: string;
  organizationId: string;
  inviteToken: string;
}

/**
 * Defines the structure for two-factor authentication verification
 */
export interface TwoFactorRequest {
  twoFactorToken: string;
  code: string;
}

/**
 * Defines the structure for MFA setup response data
 */
export interface MFASetupResponse {
  qrCode: string;
  secret: string;
  backupCodes: string[];
}

/**
 * Defines the structure for MFA verification request
 */
export interface MFAVerifyRequest {
  code: string;
  secret: string;
}

/**
 * Defines the structure for token response data
 */
export interface TokenResponse {
  token: string;
  refreshToken: string;
  expiresIn: number;
}

/**
 * Defines the structure for decoded JWT token payload
 */
export interface TokenPayload {
  sub: string;
  userId: string;
  organizationId: string;
  role: string;
  permissions: string[];
  exp: number;
  iat: number;
}

/**
 * Defines the structure for password reset request
 */
export interface PasswordResetRequest {
  email: string;
}

/**
 * Defines the structure for password reset confirmation
 */
export interface PasswordResetConfirmRequest {
  token: string;
  password: string;
}

/**
 * Defines the structure for token refresh request
 */
export interface RefreshTokenRequest {
  refreshToken: string;
}

/**
 * Defines the structure for token validation request
 */
export interface TokenValidationRequest {
  token: string;
}

/**
 * Defines the structure for token validation response
 */
export interface TokenValidationResponse {
  valid: boolean;
  payload: TokenPayload | null;
}

/**
 * Defines the authentication context type for React context API
 * providing authentication functionality throughout the application
 */
export interface AuthContextType {
  isAuthenticated: boolean;
  user: User | null;
  loading: boolean;
  error: string | null;
  login: (credentials: LoginRequest) => Promise<LoginResponse>;
  logout: () => Promise<void>;
  register: (userData: RegisterRequest) => Promise<LoginResponse>;
  refreshToken: () => Promise<TokenResponse>;
  setupTwoFactor: () => Promise<MFASetupResponse>;
  verifyTwoFactor: (twoFactorData: TwoFactorRequest) => Promise<LoginResponse>;
  requestPasswordReset: (resetData: PasswordResetRequest) => Promise<void>;
  confirmPasswordReset: (confirmData: PasswordResetConfirmRequest) => Promise<void>;
  clearErrors: () => void;
}