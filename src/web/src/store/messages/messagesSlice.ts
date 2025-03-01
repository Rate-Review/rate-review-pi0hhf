import { createSlice, PayloadAction } from '@reduxjs/toolkit'; //  ^1.9.5
import { Message, MessageThread, MessageFilter } from '../../types/message';
import {
  fetchMessages,
  fetchMessageById,
  fetchThreads,
  fetchThreadById,
  createMessage,
  markMessageAsRead,
  searchMessages
} from './messagesThunks';

/**
 * Interface defining the structure of the messages slice state
 */
interface MessagesState {
  messages: Message[];
  currentMessage: Message | null;
  threads: MessageThread[];
  currentThread: MessageThread | null;
  threadMessages: Message[];
  loading: boolean;
  error: string | null;
  filters: MessageFilter;
  totalMessages: number;
  totalThreads: number;
  unreadCount: number;
}

/**
 * Initial state for the messages slice of the Redux store
 */
const initialState: MessagesState = {
  messages: [],
  currentMessage: null,
  threads: [],
  currentThread: null,
  threadMessages: [],
  loading: false,
  error: null,
  filters: {},
  totalMessages: 0,
  totalThreads: 0,
  unreadCount: 0
};

/**
 * Redux slice for managing messages state in the Justice Bid Rate Negotiation System.
 * This file defines the initial state, reducers for synchronous operations, and
 * handles async thunk actions for the secure messaging system.
 */
const messagesSlice = createSlice({
  name: 'messages',
  initialState,
  reducers: {
    /**
     * Updates the messages list and total count in state
     * @param state - Current state
     * @param payload - Action payload containing messages and optional total count
     */
    setMessages: (state, action: PayloadAction<{ messages: Message[]; total?: number }>) => {
      state.messages = action.payload.messages;
      if (action.payload.total !== undefined) {
        state.totalMessages = action.payload.total;
      }
    },
    /**
     * Sets the currently selected message
     * @param state - Current state
     * @param payload - Action payload containing the message
     */
    setCurrentMessage: (state, action: PayloadAction<Message>) => {
      state.currentMessage = action.payload;
    },
    /**
     * Updates the threads list and total count in state
     * @param state - Current state
     * @param payload - Action payload containing threads and optional total count
     */
    setThreads: (state, action: PayloadAction<{ threads: MessageThread[]; total?: number }>) => {
      state.threads = action.payload.threads;
      if (action.payload.total !== undefined) {
        state.totalThreads = action.payload.total;
      }
    },
    /**
     * Sets the currently selected thread and its messages
     * @param state - Current state
     * @param payload - Action payload containing the thread and its messages
     */
    setCurrentThread: (state, action: PayloadAction<{ thread: MessageThread; messages: Message[] }>) => {
      state.currentThread = action.payload.thread;
      state.threadMessages = action.payload.messages;
    },
    /**
     * Updates the loading state during message operations
     * @param state - Current state
     * @param payload - Action payload containing the loading state
     */
    setLoading: (state, action: PayloadAction<boolean>) => {
      state.loading = action.payload;
    },
    /**
     * Sets the error message when message operations fail
     * @param state - Current state
     * @param payload - Action payload containing the error message
     */
    setError: (state, action: PayloadAction<string>) => {
      state.error = action.payload;
      state.loading = false;
    },
    /**
     * Clears any current error message
     * @param state - Current state
     */
    clearError: (state) => {
      state.error = null;
    },
    /**
     * Clears the currently selected message
     * @param state - Current state
     */
    clearCurrentMessage: (state) => {
      state.currentMessage = null;
    },
    /**
     * Clears the currently selected thread and its messages
     * @param state - Current state
     */
    clearCurrentThread: (state) => {
      state.currentThread = null;
      state.threadMessages = [];
    },
    /**
     * Updates the current message filters
     * @param state - Current state
     * @param payload - Action payload containing the message filters
     */
    setFilters: (state, action: PayloadAction<MessageFilter>) => {
      state.filters = action.payload;
    },
    /**
     * Updates the count of unread messages
     * @param state - Current state
     * @param payload - Action payload containing the unread count
     */
    setUnreadCount: (state, action: PayloadAction<number>) => {
      state.unreadCount = action.payload;
    },
    /**
     * Updates the read status of a specific message
     * @param state - Current state
     * @param payload - Action payload containing the message ID and read status
     */
    updateMessageReadStatus: (state, action: PayloadAction<{ messageId: string; isRead: boolean }>) => {
      const { messageId, isRead } = action.payload;
      // Update in messages array
      const messageIndex = state.messages.findIndex(msg => msg.id === messageId);
      if (messageIndex !== -1) {
        state.messages[messageIndex].isRead = isRead;
      }
      // Update in threadMessages array
      const threadMessageIndex = state.threadMessages.findIndex(msg => msg.id === messageId);
      if (threadMessageIndex !== -1) {
        state.threadMessages[threadMessageIndex].isRead = isRead;
      }
    }
  },
  extraReducers: (builder) => {
    builder
      .addCase(fetchMessages.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchMessages.fulfilled, (state, action) => {
        state.loading = false;
        state.messages = action.payload;
      })
      .addCase(fetchMessages.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message || 'Failed to fetch messages';
      })
      .addCase(fetchMessageById.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchMessageById.fulfilled, (state, action) => {
        state.loading = false;
        state.currentMessage = action.payload;
      })
      .addCase(fetchMessageById.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message || 'Failed to fetch message';
      })
      .addCase(fetchThreads.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchThreads.fulfilled, (state, action) => {
        state.loading = false;
        state.threads = action.payload;
      })
      .addCase(fetchThreads.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message || 'Failed to fetch threads';
      })
      .addCase(fetchThreadById.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchThreadById.fulfilled, (state, action) => {
        state.loading = false;
        state.currentThread = action.payload;
      })
      .addCase(fetchThreadById.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message || 'Failed to fetch thread';
      })
      .addCase(createMessage.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(createMessage.fulfilled, (state, action) => {
        state.loading = false;
        // Add new message to messages list and/or threadMessages if relevant
        if (state.currentThread && state.currentThread.id === action.payload.threadId) {
          state.threadMessages.push(action.payload);
        }
        state.messages.push(action.payload);
      })
      .addCase(createMessage.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message || 'Failed to create message';
      })
      .addCase(markMessageAsRead.fulfilled, (state, action) => {
        // Find message by ID in state.messages and state.threadMessages and update its isRead property
      })
      .addCase(searchMessages.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(searchMessages.fulfilled, (state, action) => {
        state.loading = false;
        state.messages = action.payload;
      })
      .addCase(searchMessages.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message || 'Failed to search messages';
      });
  },
});

// Extract the action creators
export const messagesActions = messagesSlice.actions;

// Export the reducer as the default export
export default messagesSlice.reducer;