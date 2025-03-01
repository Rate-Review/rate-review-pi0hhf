/**
 * TypeScript type definitions for the rate negotiation system.
 * Defines the data structures used throughout the application for handling
 * negotiations between law firms and clients.
 */

import { Rate, RateSubmission } from './rate';
import { Organization } from './organization';
import { User } from './user';
import { MessageThread } from './message';

/**
 * Enum representing the possible statuses of a negotiation
 */
export enum NegotiationStatus {
  REQUESTED = 'REQUESTED',
  SUBMITTED = 'SUBMITTED',
  UNDER_REVIEW = 'UNDER_REVIEW',
  CLIENT_APPROVED = 'CLIENT_APPROVED',
  CLIENT_REJECTED = 'CLIENT_REJECTED',
  CLIENT_COUNTERED = 'CLIENT_COUNTERED',
  FIRM_ACCEPTED = 'FIRM_ACCEPTED',
  FIRM_COUNTERED = 'FIRM_COUNTERED',
  PENDING_APPROVAL = 'PENDING_APPROVAL',
  APPROVED = 'APPROVED',
  REJECTED = 'REJECTED',
  COMPLETED = 'COMPLETED',
  EXPORTED = 'EXPORTED',
  EXPIRED = 'EXPIRED'
}

/**
 * Enum representing the types of negotiations in the system
 */
export enum NegotiationType {
  RATE_SUBMISSION = 'RATE_SUBMISSION',
  OCG_NEGOTIATION = 'OCG_NEGOTIATION'
}

/**
 * Enum representing the approval status of a negotiation
 */
export enum ApprovalStatus {
  PENDING = 'PENDING',
  IN_PROGRESS = 'IN_PROGRESS',
  APPROVED = 'APPROVED',
  REJECTED = 'REJECTED',
  MODIFIED = 'MODIFIED'
}

/**
 * Main interface for negotiation data structure
 */
export interface Negotiation {
  id: string;
  type: NegotiationType;
  status: NegotiationStatus;
  clientId: string;
  firmId: string;
  client: Organization;
  firm: Organization;
  requestDate: string;
  submissionDeadline: string;
  completionDate: string;
  messageThreadId: string;
  rateIds: string[];
  approvalWorkflowId: string;
  approvalStatus: ApprovalStatus;
  createdBy: string;
  createdAt: string;
  updatedAt: string;
}

/**
 * Interface for negotiation summary data used in listings
 */
export interface NegotiationSummary {
  id: string;
  type: NegotiationType;
  status: NegotiationStatus;
  clientName: string;
  firmName: string;
  submissionDeadline: string;
  lastUpdated: string;
  rateCount: number;
  averageIncrease: number;
}

/**
 * Interface for detailed negotiation data with all related information
 */
export interface NegotiationDetail {
  negotiation: Negotiation;
  rates: Rate[];
  messageThread: MessageThread;
  participants: NegotiationParticipant[];
  history: NegotiationHistoryItem[];
  stats: RateNegotiationStats;
  isRealTimeMode: boolean;
}

/**
 * Interface for participants in a negotiation
 */
export interface NegotiationParticipant {
  userId: string;
  user: User;
  role: string;
  organizationId: string;
  joinedAt: string;
  isActive: boolean;
}

/**
 * Interface for negotiation history items
 */
export interface NegotiationHistoryItem {
  id: string;
  negotiationId: string;
  action: string;
  description: string;
  performedBy: string;
  performedAt: string;
  metadata: Record<string, any>;
}

/**
 * Interface for negotiation search and filter criteria
 */
export interface NegotiationFilters {
  status: NegotiationStatus[];
  type: NegotiationType[];
  clientId: string;
  firmId: string;
  startDate: string;
  endDate: string;
  search: string;
  sortBy: string;
  sortDirection: string;
  page: number;
  pageSize: number;
}

/**
 * Interface for statistics related to rate negotiations
 */
export interface RateNegotiationStats {
  totalRates: number;
  approvedRates: number;
  rejectedRates: number;
  counterProposedRates: number;
  pendingRates: number;
  averageIncrease: number;
  totalImpact: number;
  impactPercentage: number;
  peerGroupComparison: PeerGroupComparison;
}

/**
 * Interface for peer group comparison data
 */
export interface PeerGroupComparison {
  averageIncrease: number;
  minIncrease: number;
  maxIncrease: number;
  peerGroupName: string;
}

/**
 * Interface for request payload to create a new negotiation
 */
export interface NegotiationCreateRequest {
  type: NegotiationType;
  clientId: string;
  firmId: string;
  submissionDeadline: string;
  message: string;
}

/**
 * Interface for counter-proposal data structure
 */
export interface CounterProposal {
  rateId: string;
  counterAmount: number;
  message: string;
  proposedBy: string;
  proposedAt: string;
}

/**
 * Type representing actions that can be taken on a negotiation
 */
export type NegotiationAction = 'approve' | 'reject' | 'counter' | 'accept' | 'submit';

/**
 * Interface for bulk actions on multiple rates in a negotiation
 */
export interface BulkNegotiationAction {
  action: NegotiationAction;
  rateIds: string[];
  message: string;
  counterAmounts: Record<string, number>;
}

/**
 * Interface for API responses related to negotiation actions
 */
export interface NegotiationResponse {
  id: string;
  success: boolean;
  message: string;
  negotiation: Negotiation;
}