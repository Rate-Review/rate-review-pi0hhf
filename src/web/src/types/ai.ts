/**
 * TypeScript type definitions for AI-related data structures in the Justice Bid Rate Negotiation System.
 * This file includes data structures for AI chat functionality, recommendations, and configuration settings
 * that support the AI-first approach of the application.
 */

import { OrganizationId } from '../types/organization';
import { UserId } from '../types/user';
import { Rate } from '../types/rate';

/**
 * Enum defining possible roles in a chat conversation
 */
export enum ChatMessageRole {
  USER = 'USER',
  ASSISTANT = 'ASSISTANT',
  SYSTEM = 'SYSTEM'
}

/**
 * Interface defining the structure of a chat message between user and AI
 */
export interface ChatMessage {
  id: string;
  role: ChatMessageRole;
  content: string;
  timestamp: string;
}

/**
 * Interface defining a conversation thread between user and AI
 */
export interface ChatConversation {
  id: string;
  messages: ChatMessage[];
  createdAt: string;
  updatedAt: string;
}

/**
 * Enum defining available AI models that can be used
 */
export enum AIModel {
  GPT_4 = 'GPT_4',
  CLAUDE = 'CLAUDE',
  CUSTOM = 'CUSTOM'
}

/**
 * Enum defining possible AI environments
 */
export enum AIEnvironment {
  JUSTICE_BID = 'JUSTICE_BID',
  CLIENT = 'CLIENT'
}

/**
 * Interface defining AI configuration settings
 */
export interface AIConfiguration {
  environment: AIEnvironment;
  model: AIModel;
  organizationId: OrganizationId;
  dataAccess: object;
  personalizationEnabled: boolean;
}

/**
 * Interface defining user-specific AI personalization settings
 */
export interface AIPersonalizationSettings {
  userId: UserId;
  preferences: object;
  interactionHistory: object;
  feedbackSettings: object;
}

/**
 * Enum defining types of AI recommendations
 */
export enum RecommendationType {
  APPROVE = 'APPROVE',
  REJECT = 'REJECT',
  COUNTER = 'COUNTER'
}

/**
 * Interface defining AI recommendation structure for rates
 */
export interface AIRecommendation {
  id: string;
  type: RecommendationType;
  value: any;
  rationale: string;
  confidence: number;
  relatedRates: Rate[];
}

/**
 * Interface defining the request structure for AI rate recommendations
 */
export interface AIRateRecommendationRequest {
  rates: Rate[];
  context: object;
}

/**
 * Interface defining the response structure for AI rate recommendations
 */
export interface AIRateRecommendationResponse {
  recommendations: AIRecommendation[];
  explanations: object;
}

/**
 * Interface defining request structure for AI chat
 */
export interface AIChatRequest {
  message: string;
  conversationId: string | null;
  context: object;
}

/**
 * Interface defining response structure for AI chat
 */
export interface AIChatResponse {
  message: ChatMessage;
  conversationId: string;
  actions: object[];
}

/**
 * Interface defining the AI-related Redux state structure
 */
export interface AIState {
  isInitialized: boolean;
  isLoading: boolean;
  error: string | null;
  config: AIConfiguration;
  personalization: AIPersonalizationSettings | null;
  conversations: Record<string, ChatConversation>;
  activeConversationId: string | null;
  recommendations: Record<string, AIRecommendation[]>;
}