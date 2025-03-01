/**
 * TypeScript type definitions for user-related data structures in the Justice Bid Rate Negotiation System.
 * This file defines interfaces for user profiles, permissions, and preferences that support
 * the user management functionality.
 */

import { Organization } from '../types/organization';

/**
 * Defines the possible roles a user can have in the system
 * These roles follow a hierarchical structure with increasing privileges
 */
export enum UserRole {
  SYSTEM_ADMINISTRATOR = 'SystemAdministrator',
  ORGANIZATION_ADMINISTRATOR = 'OrganizationAdministrator',
  RATE_ADMINISTRATOR = 'RateAdministrator',
  APPROVER = 'Approver',
  ANALYST = 'Analyst',
  STANDARD_USER = 'StandardUser'
}

/**
 * Defines the possible permissions a user can have in the system
 * Permissions are granular capabilities that can be assigned to users
 */
export enum UserPermission {
  VIEW_RATES = 'ViewRates',
  SUBMIT_RATES = 'SubmitRates',
  APPROVE_RATES = 'ApproveRates',
  COUNTER_PROPOSE_RATES = 'CounterProposeRates',
  VIEW_ANALYTICS = 'ViewAnalytics',
  MANAGE_USERS = 'ManageUsers',
  MANAGE_ORGANIZATION = 'ManageOrganization',
  MANAGE_INTEGRATIONS = 'ManageIntegrations',
  MANAGE_OCG = 'ManageOCG',
  NEGOTIATE_OCG = 'NegotiateOCG'
}

/**
 * Defines the structure of a user in the system
 * Contains core user data including authentication and authorization information
 */
export interface User {
  id: string;
  email: string;
  name: string;
  organizationId: string;
  organization: Organization;
  role: UserRole;
  permissions: UserPermission[];
  isContact: boolean;
  lastVerified: Date;
  createdAt: Date;
  updatedAt: Date;
}

/**
 * Defines user profile information for display and management purposes
 * Contains a subset of user data that's safe to expose in UI contexts
 */
export interface UserProfile {
  id: string;
  email: string;
  name: string;
  role: UserRole;
  organization: Organization;
  avatarUrl: string;
  preferences: UserPreferences;
}

/**
 * Defines user preferences for customizing the application experience
 * These settings affect how the application appears and behaves for the user
 */
export interface UserPreferences {
  theme: string;
  notificationSettings: NotificationSettings;
  defaultCurrency: string;
  defaultDateFormat: string;
}

/**
 * Defines user notification preferences
 * Controls which events trigger notifications and how they are delivered
 */
export interface NotificationSettings {
  email: boolean;
  inApp: boolean;
  rateRequests: boolean;
  rateApprovals: boolean;
  messages: boolean;
  ocgUpdates: boolean;
}

/**
 * Defines the data structure for user creation and editing forms
 * Contains the fields that can be submitted when creating or updating a user
 */
export interface UserFormData {
  email: string;
  name: string;
  role: UserRole;
  permissions: UserPermission[];
  isContact: boolean;
}

/**
 * Defines filtering options for user lists
 * Used to filter users in administration interfaces
 */
export interface UserFilter {
  role?: UserRole;
  isContact?: boolean;
  searchTerm?: string;
}