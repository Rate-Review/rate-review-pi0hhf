/**
 * TypeScript type definitions for rate-related entities in the Justice Bid Rate Negotiation System.
 * This file includes rate data structures, rate status enums, rate history tracking, and 
 * request/response interfaces for rate-related API calls.
 */

import { ID, TimestampedEntity } from './common';

/**
 * Enum representing different types of rates in the system
 */
export enum RateType {
  STANDARD = 'STANDARD',
  APPROVED = 'APPROVED',
  PROPOSED = 'PROPOSED',
  COUNTER_PROPOSED = 'COUNTER_PROPOSED'
}

/**
 * Enum representing different statuses a rate can have during its lifecycle
 */
export enum RateStatus {
  DRAFT = 'DRAFT',
  SUBMITTED = 'SUBMITTED',
  UNDER_REVIEW = 'UNDER_REVIEW',
  APPROVED = 'APPROVED',
  REJECTED = 'REJECTED'
}

/**
 * Interface for a historical entry of a rate change
 */
export interface RateHistoryEntry {
  amount: number;
  type: RateType;
  status: RateStatus;
  timestamp: string; // ISO date
  userId: ID;
  message: string | null;
}

/**
 * Main interface for rate data with all properties
 */
export interface Rate extends TimestampedEntity {
  id: ID;
  attorneyId: ID;
  clientId: ID;
  firmId: ID;
  staffClassId: ID | null;
  officeId: ID | null;
  amount: number;
  currency: string;
  type: RateType;
  effectiveDate: string; // ISO date
  expirationDate: string | null; // ISO date or null
  status: RateStatus;
  history: RateHistoryEntry[];
}

/**
 * Extended rate interface that includes additional details for display purposes
 */
export interface RateWithDetails {
  rate: Rate;
  attorneyName: string;
  firmName: string;
  clientName: string;
  staffClassName: string | null;
  officeName: string | null;
  currentRate: number | null;
  percentageChange: number | null;
}

/**
 * Interface for filtering rates in search queries
 */
export interface RateFilter {
  attorneyId: ID | null;
  clientId: ID | null;
  firmId: ID | null;
  staffClassId: ID | null;
  officeId: ID | null;
  type: RateType | null;
  status: RateStatus | null;
  effectiveDateFrom: string | null; // ISO date
  effectiveDateTo: string | null; // ISO date
}

/**
 * Interface for creating a new rate
 */
export interface CreateRateRequest {
  attorneyId: ID;
  clientId: ID;
  firmId: ID;
  staffClassId: ID | null;
  officeId: ID | null;
  amount: number;
  currency: string;
  type: RateType;
  effectiveDate: string; // ISO date
  expirationDate: string | null; // ISO date
}

/**
 * Interface for updating an existing rate
 */
export interface UpdateRateRequest {
  amount: number;
  type: RateType;
  status: RateStatus;
  effectiveDate: string; // ISO date
  expirationDate: string | null; // ISO date
  message: string | null;
}

/**
 * Interface for counter-proposing a rate during negotiation
 */
export interface CounterProposeRateRequest {
  amount: number;
  message: string | null;
}

/**
 * Interface for approving a rate
 */
export interface RateApprovalRequest {
  message: string | null;
}

/**
 * Interface for rejecting a rate
 */
export interface RateRejectionRequest {
  message: string | null;
}

/**
 * Interface for performing bulk actions on multiple rates
 */
export interface BulkRateAction {
  rateIds: ID[];
  action: 'approve' | 'reject' | 'counter';
  counterAmount: number | null;
  percentageChange: number | null;
  message: string | null;
}

/**
 * Interface for rate impact analysis data
 */
export interface RateImpactAnalysis {
  totalCurrentAmount: number;
  totalProposedAmount: number;
  totalDifference: number;
  percentageChange: number;
  breakdownByStaffClass: Record<string, {
    currentAmount: number, 
    proposedAmount: number, 
    difference: number, 
    percentageChange: number
  }>;
}

/**
 * Interface for client-defined rate rules
 */
export interface RateRule extends TimestampedEntity {
  id: ID;
  clientId: ID;
  name: string;
  description: string;
  maxIncreasePercent: number | null;
  freezePeriod: number | null; // Days
  noticeRequired: number | null; // Days
  submissionWindow: {
    startMonth: number;
    startDay: number;
    endMonth: number;
    endDay: number;
  } | null;
}

/**
 * Enum for the status of a rate request
 */
export enum RateRequestStatus {
  PENDING = 'PENDING',
  APPROVED = 'APPROVED',
  REJECTED = 'REJECTED'
}

/**
 * Interface for a rate request from a law firm to a client
 */
export interface RateRequest extends TimestampedEntity {
  id: ID;
  firmId: ID;
  clientId: ID;
  requestedBy: ID;
  requestDate: string; // ISO date
  status: RateRequestStatus;
  message: string | null;
  responseMessage: string | null;
  submissionDeadline: string | null; // ISO date
}