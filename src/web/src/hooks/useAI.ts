import { useState, useEffect, useCallback, useMemo } from 'react'; // ^18.0.0
import { useSelector, useDispatch } from 'react-redux'; // ^8.0.5
import useDebounce from './useDebounce';
import { RootState, AppDispatch } from '../store';
import {
  sendMessage,
  getRateRecommendations,
  getProcessRecommendations,
  provideFeedback,
} from '../services/ai';
import {
  AIMessage,
  AIRecommendation,
  AIPersonalizationSettings,
  ChatMessage,
  RecommendationType,
  AIChatRequest,
  AIRateRecommendationRequest,
} from '../types/ai';
import {
  setChatMessages,
  setRecommendations,
  setIsLoading,
  setError,
} from '../store/ai/aiSlice';
import { useOrganizationContext } from '../context/OrganizationContext';

/**
 * Custom hook that provides AI functionality including chat interaction, recommendations, and personalization
 * @returns {object} Object containing AI state and functions
 */
export const useAI = () => {
  // LD1: Initialize state from Redux store using useSelector
  const chatMessages = useSelector((state: RootState) => state.ai.chatMessages);
  const recommendations = useSelector((state: RootState) => state.ai.recommendations);
  const isLoading = useSelector((state: RootState) => state.ai.isLoading);
  const error = useSelector((state: RootState) => state.ai.error);

  // LD1: Get Redux dispatch function with useDispatch
  const dispatch = useDispatch<AppDispatch>();

  // LD1: Get organization context using useOrganizationContext
  const { currentOrganization } = useOrganizationContext();

  // IE1: Check that currentOrganization is used correctly based on the source files provided to you.
  const organizationId = currentOrganization?.id;

  // LD1: Create debounced versions of AI request functions using useDebounce
  const debouncedGetRateRecommendations = useDebounce(
    (request: AIRateRecommendationRequest) => {
      dispatch(fetchRecommendations(request));
    },
    300
  );

  const debouncedGetChatResponse = useDebounce(
    (request: AIChatRequest) => {
      dispatch(fetchChatResponse(request));
    },
    300
  );

  const debouncedGetPersonalization = useDebounce(
    (userId: string) => {
      dispatch(fetchPersonalization(userId));
    },
    300
  );

  // LD1: Implement sendChatMessage function to send user messages to AI and update state
  const sendChatMessage = useCallback(
    async (message: string) => {
      if (!organizationId) {
        console.error('Organization ID is missing.');
        return;
      }
      // Create a chat request object
      const chatRequest: AIChatRequest = {
        message: message,
        conversationId: '123', // TODO: Replace with actual conversation ID
        context: {
          organizationId: organizationId,
        },
      };

      // Call the debounced version of the AI request
      debouncedGetChatResponse(chatRequest);
    },
    [organizationId, debouncedGetChatResponse]
  );

  // LD1: Implement getRateRecommendations function to get AI suggestions for rate proposals or counter-proposals
  const getRateRecommendations = useCallback(
    async (rateId: string) => {
      if (!organizationId) {
        console.error('Organization ID is missing.');
        return;
      }
      // Create a rate recommendation request object
      const recommendationRequest: AIRateRecommendationRequest = {
        rates: [], // TODO: Replace with actual rate data
        context: {
          organizationId: organizationId,
        },
      };

      // Call the debounced version of the AI request
      debouncedGetRateRecommendations(recommendationRequest);
    },
    [organizationId, debouncedGetRateRecommendations]
  );

  // LD1: Implement getProcessRecommendations function to get AI workflow suggestions and prioritization
  const getProcessRecommendations = useCallback(async () => {
    // TODO: Implement process recommendations logic
    console.log('getProcessRecommendations');
  }, []);

  // LD1: Implement resetChatHistory function to clear chat messages
  const resetChatHistory = useCallback(() => {
    // TODO: Implement reset chat history logic
    console.log('resetChatHistory');
  }, []);

  // LD1: Implement provideFeedback function to send user feedback on AI responses
  const provideFeedback = useCallback(async (feedback: object) => {
    // TODO: Implement provide feedback logic
    console.log('provideFeedback', feedback);
  }, []);

  // LD1: Use useEffect to initialize recommendations based on current context when component mounts
  useEffect(() => {
    if (organizationId) {
      // TODO: Implement initialization logic
      debouncedGetPersonalization(organizationId);
      console.log('Initializing AI for organization:', organizationId);
    }
  }, [organizationId, debouncedGetPersonalization]);

  // LD1: Return all state and functions as a single object
  return {
    chatMessages,
    recommendations,
    isLoading,
    error,
    sendChatMessage,
    getRateRecommendations,
    getProcessRecommendations,
    resetChatHistory,
    provideFeedback,
  };
};

// IE3: Be generous about your exports so long as it doesn't create a security risk.
export default useAI;

// Implement fetchRecommendations thunk
const fetchRecommendations = createAsyncThunk(
  'ai/fetchRecommendations',
  async (request: AIRateRecommendationRequest, thunkAPI) => {
    try {
      const response = await getRateRecommendations(request);
      return response;
    } catch (error: any) {
      return thunkAPI.rejectWithValue(error.message);
    }
  }
);

// Implement fetchChatResponse thunk
const fetchChatResponse = createAsyncThunk(
  'ai/fetchChatResponse',
  async (request: AIChatRequest, thunkAPI) => {
    try {
      const response = await sendMessage(request);
      return response;
    } catch (error: any) {
      return thunkAPI.rejectWithValue(error.message);
    }
  }
);

// Implement fetchPersonalization thunk
const fetchPersonalization = createAsyncThunk(
  'ai/fetchPersonalization',
  async (userId: string, thunkAPI) => {
    try {
      // TODO: Implement fetch personalization logic
      console.log('Fetching personalization for user:', userId);
      return {};
    } catch (error: any) {
      return thunkAPI.rejectWithValue(error.message);
    }
  }
);