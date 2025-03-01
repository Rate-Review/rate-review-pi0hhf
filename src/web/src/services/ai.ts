/**
 * AI Service
 * 
 * Service module that provides functions for interacting with the AI-related endpoints
 * of the Justice Bid backend API. This includes chat functionality, rate recommendations,
 * process management suggestions, and personalization settings.
 * 
 * @version 1.0.0
 */

import {
  ChatRequest,
  ChatResponse,
  RecommendationRequest,
  RecommendationResponse,
  AIProcessManagementRequest,
  AIProcessManagementResponse,
  AIConfigurationRequest,
  AIConfigurationResponse,
  AIExplanationRequest,
  AIExplanationResponse
} from '../types/ai';
import { api } from './api';

/**
 * Sends a user message to the AI chat service and receives a response
 * @param request - Chat request containing user message and conversation context
 * @returns Promise resolving to the chat response with AI message
 */
export async function sendChatMessage(request: ChatRequest): Promise<ChatResponse> {
  return api.post('/ai/chat', request);
}

/**
 * Gets AI-driven recommendations for rate proposals or counter-proposals
 * @param request - Request containing rate information and context
 * @returns Promise resolving to rate recommendations from the AI
 */
export async function getRateRecommendations(request: RecommendationRequest): Promise<RecommendationResponse> {
  return api.post('/ai/recommendations/rates', request);
}

/**
 * Gets AI-driven recommendations for workflow and process management
 * @param request - Request containing current user context and workflow status
 * @returns Promise resolving to process management recommendations
 */
export async function getProcessRecommendations(request: AIProcessManagementRequest): Promise<AIProcessManagementResponse> {
  return api.post('/ai/recommendations/actions', request);
}

/**
 * Updates AI personalization settings and configuration
 * @param request - Request containing user preferences and configuration settings
 * @returns Promise resolving to updated AI configuration
 */
export async function updateAIConfiguration(request: AIConfigurationRequest): Promise<AIConfigurationResponse> {
  return api.put('/ai/configuration', request);
}

/**
 * Gets current AI configuration and personalization settings
 * @returns Promise resolving to current AI configuration
 */
export async function getAIConfiguration(): Promise<AIConfigurationResponse> {
  return api.get('/ai/configuration');
}

/**
 * Gets detailed explanation for an AI recommendation
 * @param request - Request containing recommendation ID and context
 * @returns Promise resolving to detailed explanation of the recommendation
 */
export async function getRecommendationExplanation(request: AIExplanationRequest): Promise<AIExplanationResponse> {
  return api.post('/ai/analyze', request);
}