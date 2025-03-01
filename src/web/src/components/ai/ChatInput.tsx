import React, { useState, useEffect, useRef, useCallback } from 'react'; //  ^18.0.0
import styled from 'styled-components'; //  ^5.3.10
import TextField from '../common/TextField';
import Button from '../common/Button';
import { useAI } from '../../hooks/useAI';
import theme from '../../theme';
import { Send, Clear } from '@mui/icons-material'; //  ^5.14.0

/**
 * @interface ChatInputProps
 * @description Interface defining the props for the ChatInput component
 */
interface ChatInputProps {
  onSendMessage: (message: string) => void;
  placeholder?: string;
  disabled?: boolean;
  clearAfterSend?: boolean;
  autoFocus?: boolean;
  className?: string;
}

/**
 * @const InputContainer
 * @description A styled div component that contains the text input and action buttons
 */
const InputContainer = styled.div`
  display: flex;
  align-items: flex-end;
  width: 100%;
  position: relative;
  margin-top: ${props => props.theme.spacing(1)};
`;

/**
 * @const ActionsContainer
 * @description A styled div component that contains the action buttons
 */
const ActionsContainer = styled.div`
  display: flex;
  align-items: center;
  margin-left: ${props => props.theme.spacing(1)};
`;

/**
 * @const StyledTextField
 * @description A styled TextField component for the chat input
 */
const StyledTextField = styled(TextField)`
  flex: 1;
  & textarea {
    resize: none;
    min-height: 40px;
    max-height: 120px;
    overflow-y: auto;
  }
`;

/**
 * @function ChatInput
 * @param {ChatInputProps} props - The props for the component
 * @returns {JSX.Element} - The rendered component
 * @description A component that provides a text input field with send button for the AI chat interface
 */
const ChatInput: React.FC<ChatInputProps> = ({
  onSendMessage,
  placeholder = 'Type your message...',
  disabled = false,
  clearAfterSend = true,
  autoFocus = false,
  className,
}) => {
  // LD1: Initialize input state with useState hook
  const [input, setInput] = useState('');

  // LD1: Create a ref for the input element with useRef
  const inputRef = useRef<HTMLInputElement>(null);

  // LD1: Get isLoading state from useAI hook
  const { isLoading } = useAI();

  // LD1: Implement handleInputChange function to update input state
  const handleInputChange = useCallback((event: React.ChangeEvent<HTMLInputElement>) => {
    setInput(event.target.value);
  }, []);

  // LD1: Implement handleKeyPress function to send message on Enter key
  const handleKeyPress = useCallback(
    (event: React.KeyboardEvent<HTMLInputElement>) => {
      if (event.key === 'Enter' && !event.shiftKey && !disabled && !isLoading && input.trim()) {
        onSendMessage(input);
        if (clearAfterSend) {
          setInput('');
        }
      }
    },
    [input, onSendMessage, disabled, isLoading, clearAfterSend, setInput]
  );

  // LD1: Implement handleSendMessage function to validate and send message
  const handleSendMessage = useCallback(() => {
    if (!disabled && !isLoading && input.trim()) {
      onSendMessage(input);
      if (clearAfterSend) {
        setInput('');
      }
    }
  }, [input, onSendMessage, disabled, isLoading, clearAfterSend, setInput]);

  // LD1: Implement handleClearInput function to clear the input field
  const handleClearInput = useCallback(() => {
    setInput('');
  }, [setInput]);

  // LD1: Use useEffect to focus input when autoFocus is true
  useEffect(() => {
    if (autoFocus && inputRef.current) {
      inputRef.current.focus();
    }
  }, [autoFocus, inputRef]);

  // LD1: Render InputContainer with styled TextField and action buttons
  return (
    <InputContainer className={className}>
      <StyledTextField
        inputProps={{ ref: inputRef }}
        placeholder={placeholder}
        value={input}
        onChange={handleInputChange}
        onKeyDown={handleKeyPress}
        fullWidth
        disabled={disabled || isLoading}
        aria-label="AI Chat Input"
      />
      <ActionsContainer>
        <Button
          variant="text"
          color="primary"
          onClick={handleSendMessage}
          disabled={disabled || isLoading}
          aria-label="Send Message"
        >
          <Send />
        </Button>
        {input && (
          <Button
            variant="text"
            color="primary"
            onClick={handleClearInput}
            disabled={disabled || isLoading}
            aria-label="Clear Input"
          >
            <Clear />
          </Button>
        )}
      </ActionsContainer>
    </InputContainer>
  );
};

// IE3: Be generous about your exports so long as it doesn't create a security risk.
export default ChatInput;