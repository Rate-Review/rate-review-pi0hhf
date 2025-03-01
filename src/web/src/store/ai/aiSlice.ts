/**
 * Redux slice for managing AI-related state in the Justice Bid application.
 * This includes chat conversations, AI recommendations, and AI configuration settings.
 */

import { createSlice, PayloadAction } from '@reduxjs/toolkit'; // ^1.9.5
import {
  AIState,
  ChatMessage,
  AIRecommendation,
  AIConfiguration,
  ChatMessageRole,
  ChatConversation
} from '../../types/ai';
import {
  sendChatMessage,
  generateRecommendations,
  fetchAIConfiguration,
  updateAIConfiguration,
  sendAIFeedback
} from './aiThunks';

/**
 * Initial state for the AI slice
 */
const initialState: AIState = {
  isInitialized: false,
  isLoading: false,
  error: null,
  config: {
    environment: null,
    model: null,
    organizationId: null,
    dataAccess: {},
    personalizationEnabled: false
  },
  personalization: null,
  conversations: {},
  activeConversationId: null,
  recommendations: {}
};

/**
 * Redux slice for managing AI-related state
 */
export const aiSlice = createSlice({
  name: 'ai',
  initialState,
  reducers: {
    /**
     * Action to initialize a new chat conversation
     * @param state - Current AI state
     * @param action - Payload containing the new conversation
     */
    startChatConversation: (state, action: PayloadAction<ChatConversation>) => {
      state.conversations[action.payload.id] = action.payload;
      state.activeConversationId = action.payload.id;
    },
    /**
     * Action to set the currently active conversation
     * @param state - Current AI state
     * @param action - Payload containing the conversation ID
     */
    setActiveConversation: (state, action: PayloadAction<string | null>) => {
      state.activeConversationId = action.payload;
    },
    /**
     * Action to add a message to a conversation
     * @param state - Current AI state
     * @param action - Payload containing the chat message and conversation ID
     */
    addChatMessage: (state, action: PayloadAction<{ conversationId: string; message: ChatMessage }>) => {
      const { conversationId, message } = action.payload;
      if (state.conversations[conversationId]) {
        state.conversations[conversationId].messages.push(message);
      } else {
        // If the conversation doesn't exist, create a new one with the message
        state.conversations[conversationId] = {
          id: conversationId,
          messages: [message],
          createdAt: new Date().toISOString(),
          updatedAt: new Date().toISOString(),
        };
        state.activeConversationId = conversationId;
      }
    },
    /**
     * Action to set the loading state for chat operations
     * @param state - Current AI state
     * @param action - Payload containing the loading state
     */
    setChatLoading: (state, action: PayloadAction<boolean>) => {
      state.isLoading = action.payload;
    },
    /**
     * Action to set the loading state for recommendations
     * @param state - Current AI state
     * @param action - Payload containing the loading state
     */
    setRecommendationsLoading: (state, action: PayloadAction<boolean>) => {
    },
    /**
     * Action to store recommendations in state
     * @param state - Current AI state
     * @param action - Payload containing the recommendations and related rate IDs
     */
    setRecommendations: (state, action: PayloadAction<{ rateId: string; recommendations: AIRecommendation[] }>) => {
      const { rateId, recommendations } = action.payload;
      state.recommendations[rateId] = recommendations;
    },
    /**
     * Action to set AI configuration settings
     * @param state - Current AI state
     * @param action - Payload containing the AI configuration
     */
    setAIConfiguration: (state, action: PayloadAction<AIConfiguration>) => {
      state.config = action.payload;
    },
    /**
     * Action to set error state for AI operations
     * @param state - Current AI state
     * @param action - Payload containing the error message
     */
    setAIError: (state, action: PayloadAction<string | null>) => {
      state.error = action.payload;
    },
    /**
     * Action to clear error state
     * @param state - Current AI state
     */
    clearAIError: (state) => {
      state.error = null;
    },
  },
  extraReducers: (builder) => {
    builder.addCase(sendChatMessage.pending, (state) => {
      state.isLoading = true;
      state.error = null;
    });
    builder.addCase(sendChatMessage.fulfilled, (state, action) => {
      state.isLoading = false;
      const { conversationId, userMessage, aiResponse, isNewConversation } = action.payload;

      if (isNewConversation) {
        // Initialize a new conversation with both user and AI messages
        state.conversations[conversationId] = {
          id: conversationId,
          messages: [userMessage, aiResponse],
          createdAt: new Date().toISOString(),
          updatedAt: new Date().toISOString(),
        };
        state.activeConversationId = conversationId;
      } else {
        // Add both user and AI messages to the existing conversation
        state.conversations[conversationId].messages.push(userMessage);
        state.conversations[conversationId].messages.push(aiResponse);
      }
    });
    builder.addCase(sendChatMessage.rejected, (state, action) => {
      state.isLoading = false;
      state.error = action.payload as string;
    });
    builder.addCase(generateRecommendations.pending, (state) => {
      state.isLoading = true;
      state.error = null;
    });
    builder.addCase(generateRecommendations.fulfilled, (state, action) => {
      state.isLoading = false;
    });
     builder.addCase(generateRecommendations.rejected, (state, action) => {
      state.isLoading = false;
      state.error = action.payload as string;
    });
    builder.addCase(fetchAIConfiguration.pending, (state) => {
      state.isLoading = true;
      state.error = null;
    });
    builder.addCase(fetchAIConfiguration.fulfilled, (state, action) => {
      state.isLoading = false;
      state.config = action.payload;
      state.isInitialized = true;
    });
    builder.addCase(fetchAIConfiguration.rejected, (state, action) => {
      state.isLoading = false;
      state.error = action.payload as string;
    });
    builder.addCase(updateAIConfiguration.pending, (state) => {
      state.isLoading = true;
      state.error = null;
    });
    builder.addCase(updateAIConfiguration.fulfilled, (state, action) => {
      state.isLoading = false;
      state.config = action.payload;
    });
    builder.addCase(updateAIConfiguration.rejected, (state, action) => {
      state.isLoading = false;
      state.error = action.payload as string;
    });
     builder.addCase(sendAIFeedback.pending, (state) => {
      state.isLoading = true;
      state.error = null;
    });
    builder.addCase(sendAIFeedback.fulfilled, (state) => {
      state.isLoading = false;
    });
    builder.addCase(sendAIFeedback.rejected, (state, action) => {
      state.isLoading = false;
      state.error = action.payload as string;
    });
  },
});

// Action creators are generated for each case reducer function
export const {
    startChatConversation,
    setActiveConversation,
    addChatMessage,
    setChatLoading,
    setRecommendationsLoading,
    setRecommendations,
    setAIConfiguration,
    setAIError,
    clearAIError,
} = aiSlice.actions;

export default aiSlice.reducer;