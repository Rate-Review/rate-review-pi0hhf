import React, { FC, memo, useState, useCallback } from 'react'; // React library for building the component ^18.2.0
import styled from 'styled-components'; // CSS-in-JS library for component styling ^5.3.10
import { FiCopy, FiCheck } from 'react-feather'; // Icon components for copy and success indicators ^2.0.10
import ReactMarkdown from 'react-markdown'; // Markdown renderer for formatted message content ^8.0.5
import Prism from 'prismjs'; // Syntax highlighting for code blocks in AI responses ^1.29.0

import Avatar from '../common/Avatar';
import AIFeedbackControls from './AIFeedbackControls';
import { ChatMessageProps } from '../../types/ai';
import { formatDate } from '../../utils/date';

// LD1: Styled container for the chat message
const MessageContainer = styled.div`
  display: flex;
  padding: ${(props) => props.theme.spacing.md}px;
  border-bottom: 1px solid ${(props) => props.theme.colors.divider};
  word-break: break-word;
`;

// LD1: Styled container for the message content
const MessageContent = styled.div`
  flex: 1;
  margin-left: ${(props) => props.theme.spacing.md}px;
  font-size: ${(props) => props.theme.typography.fontSize.md};
  color: ${(props) => props.theme.colors.text.primary};

  /* Style for code blocks */
  pre {
    background-color: ${(props) => props.theme.colors.background.light};
    padding: ${(props) => props.theme.spacing.sm}px;
    border-radius: ${(props) => props.theme.borderRadius.sm};
    overflow-x: auto;
    font-family: ${(props) => props.theme.typography.mono.fontFamily};
    font-size: ${(props) => props.theme.typography.fontSize.sm};
    margin: ${(props) => props.theme.spacing.xs}px 0;
  }

  /* Style for inline code */
  code {
    font-family: ${(props) => props.theme.typography.mono.fontFamily};
    font-size: ${(props) => props.theme.typography.fontSize.sm};
    background-color: ${(props) => props.theme.colors.background.light};
    padding: ${(props) => props.theme.spacing.xs}px;
    border-radius: ${(props) => props.theme.borderRadius.sm};
  }

  /* Style for tables */
  table {
    width: 100%;
    border-collapse: collapse;
    margin: ${(props) => props.theme.spacing.xs}px 0;
  }

  th,
  td {
    border: 1px solid ${(props) => props.theme.colors.divider};
    padding: ${(props) => props.theme.spacing.xs}px;
    text-align: left;
  }

  th {
    background-color: ${(props) => props.theme.colors.background.light};
    font-weight: ${(props) => props.theme.typography.fontWeight.medium};
  }

  /* Style for blockquotes */
  blockquote {
    margin: 0;
    padding-left: ${(props) => props.theme.spacing.md}px;
    border-left: 4px solid ${(props) => props.theme.colors.primary.main};
    font-style: italic;
    color: ${(props) => props.theme.colors.text.secondary};
  }
`;

// LD1: Styled timestamp for the message
const Timestamp = styled.div`
  font-size: ${(props) => props.theme.typography.fontSize.xs};
  color: ${(props) => props.theme.colors.text.disabled};
  margin-top: ${(props) => props.theme.spacing.xs}px;
  text-align: right;
`;

// LD1: Styled copy button
const CopyButton = styled.button`
  background: none;
  border: none;
  cursor: pointer;
  color: ${(props) => props.theme.colors.text.secondary};
  margin-left: ${(props) => props.theme.spacing.sm}px;
  opacity: 0.7;
  transition: opacity ${(props) => props.theme.transitions.fast};

  &:hover {
    opacity: 1;
  }

  &:focus {
    outline: none;
  }
`;

// LD1: Styled container for the copy success indicator
const CopySuccessIndicator = styled.span`
  color: ${(props) => props.theme.colors.success.main};
  margin-left: ${(props) => props.theme.spacing.sm}px;
`;

/**
 * Copies the message content to the clipboard and shows a success indicator
 */
const handleCopyToClipboard = () => {
  // LD1: Copy message content to clipboard using the navigator.clipboard API
  navigator.clipboard.writeText(ChatMessage.content);
  // LD1: Set copied state to true to show success indicator
  setCopied(true);
  // LD1: Set a timeout to reset the copied state after 2 seconds
  setTimeout(() => {
    setCopied(false);
  }, 2000);
};

/**
 * Renders the message content with proper formatting based on the content type
 * @param {string} content - The message content
 * @returns {ReactNode} Rendered message content with proper formatting
 */
const renderMessageContent = (content: string) => {
  // LD1: If content contains code blocks, use Prism for syntax highlighting
  // LD1: Render content as markdown using ReactMarkdown
  // LD1: Add special handling for tables, charts, and other structured data
  // LD1: Return the formatted content
  return (
    <ReactMarkdown
      components={{
        code({ node, inline, className, children, ...props }) {
          const match = (className || '').match(/language-(\w+)/);
          return !inline && match ? (
            <pre className={className}>
              <code className={className} {...props}>
                {String(children).replace(/\n$/, '')}
              </code>
            </pre>
          ) : (
            <code className={className} {...props}>
              {children}
            </code>
          );
        },
      }}
    >
      {content}
    </ReactMarkdown>
  );
};

/**
 * Component for rendering chat messages in the AI interface
 */
const ChatMessage: FC<ChatMessageProps> = memo(({ role, content, timestamp, showFeedbackControls, contentId, contentType, initialFeedback, onFeedbackSubmit }) => {
  // LD1: Initialize copied state for copy to clipboard functionality
  const [copied, setCopied] = useState(false);

  return (
    <MessageContainer>
      <Avatar name={role} />
      <MessageContent>
        {renderMessageContent(content)}
        <Timestamp>
          {formatDate(timestamp, 'MMM d, yyyy h:mm a')}
          {role === 'ASSISTANT' && (
            <>
              <CopyButton onClick={handleCopyToClipboard} aria-label="Copy message to clipboard">
                {copied ? <FiCheck size={16} /> : <FiCopy size={16} />}
              </CopyButton>
              {copied && <CopySuccessIndicator>Copied!</CopySuccessIndicator>}
            </>
          )}
        </Timestamp>
        {showFeedbackControls && role === 'ASSISTANT' && (
          <AIFeedbackControls
            contentId={contentId}
            contentType={contentType}
            initialFeedback={initialFeedback}
            onFeedbackSubmit={onFeedbackSubmit}
          />
        )}
      </MessageContent>
    </MessageContainer>
  );
});

export default ChatMessage;