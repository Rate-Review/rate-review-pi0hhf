/**
 * TypeScript type definitions for attorney-related data structures used 
 * in the frontend of the Justice Bid Rate Negotiation System.
 * 
 * This file defines types for attorneys, their performance metrics, ratings,
 * and related structures to support attorney management, performance analytics,
 * and UniCourt integration.
 */

import { BaseEntity, ID } from '../types/common';
import { OrganizationSummary } from '../types/organization';

/**
 * Represents a full attorney entity with all attributes
 */
export interface Attorney extends BaseEntity {
  id: ID;
  name: string;
  organizationId: ID;
  organization?: OrganizationSummary;
  barDate: string; // ISO date string
  graduationDate: string; // ISO date string
  promotionDate: string; // ISO date string
  officeIds: ID[];
  practiceAreas: string[];
  timekeeperIds: Record<string, string>; // Maps client IDs to timekeeper IDs
  unicourtId: string; // ID for UniCourt integration
  staffClassId: ID;
  staffClass?: StaffClassSummary;
  performanceData?: AttorneyPerformance;
  createdAt: string; // ISO date string
  updatedAt: string; // ISO date string
}

/**
 * Simplified attorney representation for summary views and references
 */
export interface AttorneySummary {
  id: ID;
  name: string;
  organizationId: ID;
  staffClassId: ID;
}

/**
 * Represents a summary of a staff class for use in attorney data structures
 */
export interface StaffClassSummary {
  id: ID;
  name: string;
  organizationId: ID;
}

/**
 * Defines the performance metrics associated with an attorney
 */
export interface AttorneyPerformance {
  attorneyId: ID;
  unicourt: UniCourtPerformance;
  ratings: AttorneyRating[];
  billingMetrics: AttorneyBillingMetrics;
}

/**
 * Defines performance metrics from UniCourt for an attorney
 */
export interface UniCourtPerformance {
  caseCount: number;
  winRate: number;
  caseTypes: Record<string, number>; // Case type to count mapping
  courts: Record<string, number>; // Court to count mapping
  percentile: number; // Performance percentile compared to peers
  lastUpdated: string; // ISO date string
}

/**
 * Defines client ratings for an attorney
 */
export interface AttorneyRating {
  clientId: ID;
  value: number; // Typically 1-5 scale
  comment: string;
  date: string; // ISO date string
}

/**
 * Defines billing performance metrics for an attorney
 */
export interface AttorneyBillingMetrics {
  hours: number; // Total hours billed
  fees: number; // Total fees generated
  matters: number; // Number of matters worked on
  utilization: number; // Utilization rate (percentage)
  realization: number; // Realization rate (percentage)
  period: string; // Time period for the metrics (e.g., "LAST_12_MONTHS")
}

/**
 * Data transfer object for creating a new attorney
 */
export interface CreateAttorneyDto {
  name: string;
  organizationId: ID;
  barDate: string; // ISO date string
  graduationDate: string; // ISO date string
  promotionDate: string; // ISO date string
  officeIds: ID[];
  practiceAreas: string[];
  timekeeperIds: Record<string, string>;
  staffClassId: ID;
}

/**
 * Data transfer object for updating an existing attorney
 */
export interface UpdateAttorneyDto {
  name?: string;
  barDate?: string; // ISO date string
  graduationDate?: string; // ISO date string
  promotionDate?: string; // ISO date string
  officeIds?: ID[];
  practiceAreas?: string[];
  timekeeperIds?: Record<string, string>;
  staffClassId?: ID;
}

/**
 * Parameters for searching and filtering attorneys
 */
export interface AttorneySearchParams {
  organizationId?: ID;
  name?: string;
  staffClassId?: ID;
  practiceArea?: string;
  officeId?: ID;
  page?: number;
  limit?: number;
}