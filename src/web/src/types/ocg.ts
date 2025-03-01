/**
 * TypeScript type definitions for Outside Counsel Guidelines (OCG) features in the 
 * Justice Bid Rate Negotiation System.
 * 
 * This file defines the structure of OCG documents, sections, alternatives, and 
 * the negotiation process between clients and law firms.
 */

import { UUID } from '../types/common';
import { OrganizationSummary } from '../types/organization';

/**
 * Represents the various states an OCG can be in within the system
 */
export enum OCGStatus {
  Draft = 'Draft',
  Published = 'Published',
  Negotiating = 'Negotiating',
  Signed = 'Signed'
}

/**
 * Represents a section within an OCG document
 */
export interface OCGSection {
  id: UUID;
  title: string;
  content: string;
  isNegotiable: boolean;
  alternatives: OCGAlternative[];
  order: number;
}

/**
 * Represents an alternative option for negotiable sections
 */
export interface OCGAlternative {
  id: UUID;
  title: string;
  content: string;
  points: number;
  isDefault: boolean;
}

/**
 * Represents a complete OCG document
 */
export interface OCGDocument {
  id: UUID;
  title: string;
  version: number;
  status: OCGStatus;
  clientId: UUID;
  client: OrganizationSummary;
  sections: OCGSection[];
  totalPoints: number;
  createdAt: Date;
  updatedAt: Date;
}

/**
 * Represents a law firm's selection of alternatives during OCG negotiation
 */
export interface OCGFirmSelection {
  sectionId: UUID;
  alternativeId: UUID;
  pointsUsed: number;
}

/**
 * Represents the status of an OCG negotiation
 */
export enum OCGNegotiationStatus {
  InProgress = 'InProgress',
  Submitted = 'Submitted',
  CounterProposed = 'CounterProposed',
  Accepted = 'Accepted',
  Rejected = 'Rejected',
  Completed = 'Completed'
}

/**
 * Represents an active negotiation of an OCG between a client and a law firm
 */
export interface OCGNegotiation {
  id: UUID;
  ocgId: UUID;
  ocg: OCGDocument;
  firmId: UUID;
  firm: OrganizationSummary;
  pointBudget: number;
  pointsUsed: number;
  selections: Record<UUID, OCGFirmSelection>;
  status: OCGNegotiationStatus;
  comments: string;
  createdAt: Date;
  updatedAt: Date;
}

/**
 * Lightweight version of OCGDocument for lists and summaries
 */
export interface OCGSummary {
  id: UUID;
  title: string;
  version: number;
  status: OCGStatus;
  clientId: UUID;
  client: OrganizationSummary;
  createdAt: Date;
  updatedAt: Date;
}

/**
 * Request payload for creating a new OCG
 */
export interface CreateOCGRequest {
  title: string;
  clientId: UUID;
  sections: Omit<OCGSection, 'id'>[];
  totalPoints: number;
}

/**
 * Request payload for updating an existing OCG
 */
export interface UpdateOCGRequest {
  title: string;
  sections: OCGSection[];
  totalPoints: number;
}

/**
 * Request payload for publishing an OCG
 */
export interface PublishOCGRequest {
  id: UUID;
}

/**
 * Request payload for starting an OCG negotiation with a law firm
 */
export interface StartOCGNegotiationRequest {
  ocgId: UUID;
  firmId: UUID;
  pointBudget: number;
}

/**
 * Request payload for submitting law firm selections during OCG negotiation
 */
export interface SubmitOCGSelectionsRequest {
  negotiationId: UUID;
  selections: Record<UUID, OCGFirmSelection>;
  comments: string;
}

/**
 * Represents the OCG-related state in the Redux store
 */
export interface OCGState {
  ocgs: Record<UUID, OCGDocument>;
  negotiations: Record<UUID, OCGNegotiation>;
  loading: boolean;
  error: string | null;
  activeOCGId: UUID | null;
  activeNegotiationId: UUID | null;
}