import React, {
  createContext,
  useContext,
  useState,
  useEffect,
  useCallback,
  ReactNode,
  FC,
} from 'react'; // react v18.0.0
import { useAI } from '../hooks/useAI';
import {
  ChatMessage,
  AIRecommendation,
  AIConfiguration,
  AIPersonalizationSettings,
} from '../types/ai';

/**
 * @interface AIContextType
 * @description Type definition for AI context values
 */
export interface AIContextType {
  chatMessages: ChatMessage[];
  recommendations: AIRecommendation[];
  isLoading: boolean;
  error: string | null;
  sendChatMessage: (message: string) => Promise<void>;
  getRateRecommendations: (rateId: string) => Promise<void>;
  getProcessRecommendations: () => Promise<void>;
  resetChatHistory: () => void;
  provideFeedback: (feedback: object) => Promise<void>;
  isChatOpen: boolean;
  toggleChat: () => void;
}

/**
 * @interface AIProviderProps
 * @description Props interface for AIProvider component
 */
interface AIProviderProps {
  children: ReactNode;
}

/**
 * @const AIContext
 * @type React.Context
 * @description Context providing AI data and functionality
 */
export const AIContext = createContext<AIContextType | undefined>(undefined);

/**
 * @function useAIContext
 * @description Custom hook to access AI context values
 * @returns {AIContextType} Object containing AI context values
 */
export const useAIContext = (): AIContextType => {
  const context = useContext(AIContext);
  if (!context) {
    throw new Error('useAIContext must be used within an AIProvider');
  }
  return context;
};

/**
 * @function AIProvider
 * @description Provider component for the AI context
 * @param {AIProviderProps} { children } - React children
 * @returns {JSX.Element} Provider component wrapping children
 */
export const AIProvider: FC<AIProviderProps> = ({ children }) => {
  // LD1: Use the useAI hook to access all AI functionality from Redux and services
  const {
    chatMessages,
    recommendations,
    isLoading,
    error,
    sendChatMessage,
    getRateRecommendations,
    getProcessRecommendations,
    resetChatHistory,
    provideFeedback,
  } = useAI();

  // LD1: Define state variable for controlling chat window visibility
  const [isChatOpen, setIsChatOpen] = useState(false);

  // LD1: Implement toggleChat function to toggle chat window visibility
  const toggleChat = useCallback(() => {
    setIsChatOpen((prev) => !prev);
  }, []);

  // LD1: Create an AIContextValue object with all values and functions from useAI
  const AIContextValue: AIContextType = {
    chatMessages,
    recommendations,
    isLoading,
    error,
    sendChatMessage,
    getRateRecommendations,
    getProcessRecommendations,
    resetChatHistory,
    provideFeedback,
    isChatOpen,
    toggleChat,
  };

  // LD1: Return AIContext.Provider with the AIContextValue object
  // LD1: Render children within the provider
  return (
    <AIContext.Provider value={AIContextValue}>
      {children}
    </AIContext.Provider>
  );
};