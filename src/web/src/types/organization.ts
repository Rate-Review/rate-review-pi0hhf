/**
 * TypeScript type definitions for organization entities in the Justice Bid Rate Negotiation System.
 * This file defines the structure of law firms, clients, and related organizational constructs.
 */

/**
 * Defines the possible types of organizations in the system
 */
export enum OrganizationType {
  LawFirm = "LawFirm",
  Client = "Client",
  Admin = "Admin"
}

/**
 * Represents an office location for an organization
 */
export interface Office {
  id: string;
  name: string;
  city: string;
  state: string;
  country: string;
  region: string;
}

/**
 * Represents a department within an organization
 */
export interface Department {
  id: string;
  name: string;
  description: string;
}

/**
 * Represents a contact person within an organization
 */
export interface Contact {
  id: string;
  userId: string;
  name: string;
  email: string;
  role: string;
  phone: string;
  isActive: boolean;
  lastVerified: Date;
}

/**
 * Defines the window during which rate submissions are allowed
 */
export interface SubmissionWindow {
  startMonth: number;
  startDay: number;
  endMonth: number;
  endDay: number;
}

/**
 * Defines rules for rate submissions and negotiations
 */
export interface RateRule {
  freezePeriod: number;
  noticeRequired: number;
  maxIncreasePercent: number;
  submissionWindow: SubmissionWindow;
}

/**
 * Contains organization-specific settings
 */
export interface OrganizationSettings {
  rateRules: RateRule;
  approvalWorkflow: object; // This will likely need to be a more specific type in the future
  afaTarget: number;
  defaultCurrency: string;
}

/**
 * Represents a peer group relationship for comparative analysis
 */
export interface PeerGroupRelation {
  id: string;
  name: string;
  description: string;
  members: string[];
}

/**
 * Main organization entity representing either a law firm or client
 */
export interface Organization {
  id: string;
  name: string;
  type: OrganizationType;
  domain: string;
  settings: OrganizationSettings;
  offices: Office[];
  departments: Department[];
  contacts: Contact[];
  createdAt: Date;
  updatedAt: Date;
}

/**
 * Simplified organization reference used in lists and dropdowns
 */
export interface OrganizationSummary {
  id: string;
  name: string;
  type: OrganizationType;
}

/**
 * Status of the relationship between organizations
 */
export enum RelationshipStatus {
  Active = "Active",
  Inactive = "Inactive",
  Pending = "Pending"
}

/**
 * Represents the relationship between a law firm and client
 */
export interface OrganizationRelationship {
  clientId: string;
  firmId: string;
  status: RelationshipStatus;
  startDate: Date;
}