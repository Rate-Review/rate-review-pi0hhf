/**
 * Redux thunks for AI-related functionality including chat interactions, rate recommendations, process management, and personalization in the Justice Bid application.
 */

import { createAsyncThunk } from '@reduxjs/toolkit'; // ^1.9.5
import { toast } from 'react-toastify'; // ^9.1.3
import { handleApiError } from '../../api/errorHandling';
import { sendChatMessage as sendChatMessageService, getRateRecommendations, getProcessRecommendations, updateAIConfiguration as updateAIConfigService, getAIConfiguration, getRecommendationExplanation as getExplanationService } from '../../services/ai';
import { AIChatRequest, AIRateRecommendationRequest, AIProcessManagementRequest, AIConfigurationRequest, AIExplanationRequest, ChatMessageRole } from '../../types/ai';
import { RootState } from '../index';

/**
 * Constants that define the action types for AI thunks
 */
export const AI_THUNK_TYPES = {
  SEND_CHAT_MESSAGE: 'ai/sendChatMessage',
  GENERATE_RECOMMENDATIONS: 'ai/generateRecommendations',
  GENERATE_PROCESS_RECOMMENDATIONS: 'ai/generateProcessRecommendations',
  FETCH_AI_CONFIGURATION: 'ai/fetchAIConfiguration',
  UPDATE_AI_CONFIGURATION: 'ai/updateAIConfiguration',
  GET_RECOMMENDATION_EXPLANATION: 'ai/getRecommendationExplanation',
  SEND_AI_FEEDBACK: 'ai/sendAIFeedback'
};

/**
 * Thunk action creator for sending a message to the AI chat interface and receiving a response
 * @param request - AIChatRequest
 */
export const sendChatMessage = createAsyncThunk(
  AI_THUNK_TYPES.SEND_CHAT_MESSAGE,
  async (request: AIChatRequest, thunkAPI) => {
    try {
      // Extract conversation state from Redux if needed
      const { ai: { conversations } } = thunkAPI.getState() as RootState;

      // Create a user message object with the request message
      const userMessage = {
        id: Date.now().toString(),
        role: ChatMessageRole.USER,
        content: request.message,
        timestamp: new Date().toISOString(),
      };

      // Call the sendChatMessageService with the request
      const response = await sendChatMessageService(request);

      // If successful, return payload with conversationId, user message, and AI response
      return {
        conversationId: response.conversationId,
        userMessage: userMessage,
        aiResponse: response.message,
        isNewConversation: !conversations[response.conversationId],
      };
    } catch (error) {
      // If unsuccessful, return the rejected value with error information
      return thunkAPI.rejectWithValue({ message: handleApiError(error).message });
    }
  }
);

/**
 * Thunk action creator for getting AI recommendations for rate proposals
 * @param request - AIRateRecommendationRequest
 */
export const generateRecommendations = createAsyncThunk(
  AI_THUNK_TYPES.GENERATE_RECOMMENDATIONS,
  async (request: AIRateRecommendationRequest, thunkAPI) => {
    try {
      // Call the getRateRecommendations service function with the request
      const response = await getRateRecommendations(request);
      // If successful, return the recommendations payload
      return response;
    } catch (error) {
      // If unsuccessful, return the rejected value with error information
      return thunkAPI.rejectWithValue({ message: handleApiError(error).message });
    }
  }
);

/**
 * Thunk action creator for getting AI recommendations for process management
 * @param request - AIProcessManagementRequest
 */
export const generateProcessRecommendations = createAsyncThunk(
  AI_THUNK_TYPES.GENERATE_PROCESS_RECOMMENDATIONS,
  async (request: AIProcessManagementRequest, thunkAPI) => {
    try {
      // Call the getProcessRecommendations service function with the request
      const response = await getProcessRecommendations(request);
      // If successful, return the process recommendations payload
      return response;
    } catch (error) {
      // If unsuccessful, return the rejected value with error information
      return thunkAPI.rejectWithValue({ message: handleApiError(error).message });
    }
  }
);

/**
 * Thunk action creator for fetching AI configuration settings
 */
export const fetchAIConfiguration = createAsyncThunk(
  AI_THUNK_TYPES.FETCH_AI_CONFIGURATION,
  async (_, thunkAPI) => {
    try {
      // Call the getAIConfiguration service function
      const response = await getAIConfiguration();
      // If successful, return the configuration payload
      return response;
    } catch (error) {
      // If unsuccessful, return the rejected value with error information
      return thunkAPI.rejectWithValue({ message: handleApiError(error).message });
    }
  }
);

/**
 * Thunk action creator for updating AI configuration and personalization settings
 * @param config - AIConfigurationRequest
 */
export const updateAIConfiguration = createAsyncThunk(
  AI_THUNK_TYPES.UPDATE_AI_CONFIGURATION,
  async (config: AIConfigurationRequest, thunkAPI) => {
    try {
      // Call the updateAIConfigService function with the config
      const response = await updateAIConfigService(config);

      // Show success toast notification
      toast.success('AI configuration updated successfully');

      // If successful, return the updated configuration payload
      return response;
    } catch (error) {
      // Show error toast notification
      toast.error(`Failed to update AI configuration: ${handleApiError(error).message}`);
      // If unsuccessful, return the rejected value with error information
      return thunkAPI.rejectWithValue({ message: handleApiError(error).message });
    }
  }
);

/**
 * Thunk action creator for getting detailed explanation for an AI recommendation
 * @param request - AIExplanationRequest
 */
export const getRecommendationExplanation = createAsyncThunk(
  AI_THUNK_TYPES.GET_RECOMMENDATION_EXPLANATION,
  async (request: AIExplanationRequest, thunkAPI) => {
    try {
      // Call the getExplanationService function with the request
      const response = await getExplanationService(request);
      // If successful, return the explanation payload
      return response;
    } catch (error) {
      // If unsuccessful, return the rejected value with error information
      return thunkAPI.rejectWithValue({ message: handleApiError(error).message });
    }
  }
);

/**
 * Thunk action creator for sending user feedback about AI recommendations
 * @param feedback - feedback
 */
export const sendAIFeedback = createAsyncThunk(
  AI_THUNK_TYPES.SEND_AI_FEEDBACK,
  async (feedback: object, thunkAPI) => {
    try {
      // Create an AIConfigurationRequest with the feedback data
      const config: AIConfigurationRequest = {
        feedback: feedback,
      };

      // Call the updateAIConfigService function with the request
      const response = await updateAIConfigService(config);

      // Show success toast notification
      toast.success('AI feedback sent successfully');

      // If successful, return the feedback payload
      return feedback;
    } catch (error) {
      // Show error toast notification
      toast.error(`Failed to send AI feedback: ${handleApiError(error).message}`);
      // If unsuccessful, return the rejected value with error information
      return thunkAPI.rejectWithValue({ message: handleApiError(error).message });
    }
  }
);