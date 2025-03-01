import React, { useState, useEffect, useRef, useCallback } from 'react'; // React library for building UI components ^18.0.0
import { useSelector, useDispatch } from 'react-redux'; // Redux hooks for accessing global state ^8.0.5
import styled from 'styled-components'; // For styled component definitions ^5.3.6
import {
  Box,
  Paper,
  Typography,
  IconButton,
  CircularProgress,
  Collapse,
} from '@mui/material'; // Material UI components for layout and display ^5.14.0
import {
  ArrowDropUp,
  ArrowDropDown,
  Close,
  Send,
  Clear,
} from '@mui/icons-material'; // Material UI icons for the interface ^5.14.0

import ChatMessage from './ChatMessage'; // For rendering individual chat messages
import ChatInput from './ChatInput'; // For capturing user input
import AIFeedbackControls from './AIFeedbackControls'; // For providing feedback on AI responses
import { useAI } from '../../hooks/useAI'; // Custom hook for AI operations
import { useAuth } from '../../hooks/useAuth'; // For checking user permissions
import { Message, AIAction } from '../../types/ai'; // Types for AI interactions
import { executeAction } from '../../store/ai/aiThunks'; // Thunk for executing AI suggested actions
import { setMinimized } from '../../store/ai/aiSlice'; // Action to update chat minimized state

// LD1: Interface for the AIChatInterface component props
interface AIChatInterfaceProps {
  initiallyMinimized?: boolean;
  contextId?: string;
  placeholder?: string;
  onActionExecuted?: (action: AIAction) => void;
  className?: string;
}

// LD1: Styled component for the chat container
const StyledChatContainer = styled.div`
  display: flex;
  flex-direction: column;
  height: 400px;
  border: 1px solid #ccc;
  border-radius: 5px;
  overflow: hidden;
`;

// LD1: Styled component for the chat header
const StyledChatHeader = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px;
  background-color: #f0f0f0;
`;

// LD1: Styled component for the messages container
const StyledMessagesContainer = styled.div`
  flex: 1;
  padding: 8px;
  overflow-y: auto;
`;

// LD1: Styled component for the input container
const StyledInputContainer = styled.div`
  padding: 8px;
  border-top: 1px solid #ccc;
`;

// LD1: Constant for the local storage key
const LOCAL_STORAGE_KEY = 'justice-bid-chat-history';

// LD1: Main component function for the AI chat interface
const AIChatInterface: React.FC<AIChatInterfaceProps> = ({
  initiallyMinimized = false,
  contextId,
  placeholder,
  onActionExecuted,
  className,
}) => {
  // LD1: Initialize state for messages, loading status, and minimized state
  const [messages, setMessages] = useState<Message[]>([]);
  const [loading, setLoading] = useState(false);
  const [minimized, setLocalMinimized] = useState(initiallyMinimized);

  // LD1: Set up messagesEndRef for scrolling to the bottom of the chat
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // LD1: Get minimized state and dispatch function from Redux
  const reduxMinimized = useSelector((state: any) => state.ai.minimized);
  const dispatch = useDispatch();

  // LD1: Get sendMessage and provideFeedback functions from useAI hook
  const { sendChatMessage, provideFeedback: sendFeedback } = useAI();

  // LD1: Get checkPermission function from useAuth hook
  const { checkPermission } = useAuth();

  // LD1: Define scrollToBottom function with useCallback
  const scrollToBottom = useCallback(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, []);

  // LD1: Define handleSendMessage function with useCallback
  const handleSendMessage = useCallback(
    async (message: string) => {
      setLoading(true);
      try {
        if (sendChatMessage) {
          await sendChatMessage(message);
          scrollToBottom();
        }
      } finally {
        setLoading(false);
      }
    },
    [sendChatMessage, scrollToBottom]
  );

  // LD1: Define handleToggleChat function
  const handleToggleChat = () => {
    dispatch(setMinimized(!minimized));
    setLocalMinimized(!minimized);
  };

  // LD1: Define handleClearChat function
  const handleClearChat = () => {
    setMessages([]);
    localStorage.removeItem(LOCAL_STORAGE_KEY);
  };

  // LD1: Define handleExecuteAction function with useCallback
  const handleExecuteAction = useCallback(
    async (action: AIAction) => {
      if (checkPermission && checkPermission(action.requiredPermission)) {
        dispatch(executeAction(action));
        if (onActionExecuted) {
          onActionExecuted(action);
        }
      }
    },
    [dispatch, checkPermission, onActionExecuted]
  );

  // LD1: Define handleFeedback function with useCallback
  const handleFeedback = useCallback(
    async (contentId: string, contentType: string, feedbackType: string) => {
      if (sendFeedback) {
        await sendFeedback({ contentId, contentType, feedbackType });
      }
    },
    [sendFeedback]
  );

  // LD1: Use useEffect to load saved chat history on mount
  useEffect(() => {
    const storedMessages = localStorage.getItem(LOCAL_STORAGE_KEY);
    if (storedMessages) {
      setMessages(JSON.parse(storedMessages));
    }
  }, []);

  // LD1: Use useEffect to save chat history when messages change
  useEffect(() => {
    localStorage.setItem(LOCAL_STORAGE_KEY, JSON.stringify(messages));
  }, [messages]);

  // LD1: Use useEffect to load context-specific messages when contextId changes
  useEffect(() => {
    if (contextId) {
      // TODO: Implement logic to load context-specific messages
      console.log('Loading context-specific messages for:', contextId);
    }
  }, [contextId]);

  // LD1: Use useEffect to scroll to bottom when messages change
  useEffect(() => {
    scrollToBottom();
  }, [messages, scrollToBottom]);

  // LD1: Render UI based on minimized state with conditional rendering
  return (
    <StyledChatContainer className={className}>
      <StyledChatHeader>
        <Typography variant="h6">AI Assistant</Typography>
        <Box>
          <IconButton onClick={handleToggleChat} aria-label="Toggle Chat">
            {minimized ? <ArrowDropDown /> : <ArrowDropUp />}
          </IconButton>
          <IconButton onClick={handleClearChat} aria-label="Clear Chat">
            <Clear />
          </IconButton>
          <IconButton onClick={handleToggleChat} aria-label="Close Chat">
            <Close />
          </IconButton>
        </Box>
      </StyledChatHeader>
      <Collapse in={!minimized} timeout="auto" unmountOnExit>
        <StyledMessagesContainer>
          {messages.map((message) => (
            <ChatMessage
              key={message.id}
              role={message.role}
              content={message.content}
              timestamp={message.timestamp}
              showFeedbackControls={message.role === 'ASSISTANT'}
              contentId={message.id}
              contentType="chat_message"
              onFeedbackSubmit={(feedbackType) =>
                handleFeedback(message.id, 'chat_message', feedbackType)
              }
            />
          ))}
          {loading && <CircularProgress />}
          <div ref={messagesEndRef} />
        </StyledMessagesContainer>
        <StyledInputContainer>
          <ChatInput
            onSendMessage={handleSendMessage}
            placeholder={placeholder}
            disabled={loading}
            autoFocus
          />
        </StyledInputContainer>
      </Collapse>
    </StyledChatContainer>
  );
};

// IE3: Be generous about your exports so long as it doesn't create a security risk.
export default AIChatInterface;