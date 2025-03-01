import React, { useState, useEffect, useRef, useCallback } from 'react'; //  ^18.2.0
import { useSelector, useDispatch } from 'react-redux'; // ^8.1.1
import styled from '@emotion/styled'; //  ^11.10.6
import {
  Box,
  Typography,
  Divider,
  Button,
  IconButton,
  Tooltip,
} from '@mui/material'; //  ^5.14.0
import { Reply as ReplyIcon } from '@mui/icons-material'; //  ^5.14.0

import {
  Message,
  MessageTree,
} from '../../types/message';
import MessageComposer from './MessageComposer';
import MessageAttachments from './MessageAttachments';
import Avatar from '../common/Avatar';
import Spinner from '../common/Spinner';
import RecommendationCard from '../ai/RecommendationCard';
import { formatDate } from '../../utils/date';
import { useAuth } from '../../hooks/useAuth';
import { useOrganizationContext } from '../../context/OrganizationContext';
import {
  fetchThreadById,
  markMessageAsRead,
  createMessage,
} from '../../store/messages/messagesThunks';

/**
 * @interface MessageThreadProps
 * @description Props for the MessageThread component
 */
interface MessageThreadProps {
  threadId: string;
  negotiationId?: string;
  showComposer?: boolean;
  autoScroll?: boolean;
  showAIRecommendations?: boolean;
  onMessageSent?: () => void;
  className?: string;
}

/**
 * @styledcomponent ThreadContainer
 * @description Container for the entire message thread
 */
const ThreadContainer = styled(Box)`
  max-height: 600px;
  overflow-y: auto;
  padding: 16px;
  display: flex;
  flex-direction: column;
`;

/**
 * @styledcomponent MessageItem
 * @description Container for a single message item
 */
const MessageItem = styled(Box)`
  margin-bottom: 16px;
  display: flex;
  flex-direction: column;
`;

/**
 * @styledcomponent MessageContent
 * @description Container for the message content
 */
const MessageContent = styled(Box)<{ isCurrentUser: boolean }>`
  padding: 12px;
  border-radius: 8px;
  background-color: ${props => props.isCurrentUser ? '#e3f2fd' : '#f5f5f5'};
  align-self: ${props => props.isCurrentUser ? 'flex-end' : 'flex-start'};
  max-width: 80%;
`;

/**
 * @styledcomponent MessageHeader
 * @description Header section of a message showing sender and timestamp
 */
const MessageHeader = styled(Box)`
  display: flex;
  align-items: center;
  margin-bottom: 8px;
`;

/**
 * @styledcomponent SenderInfo
 * @description Container for sender information
 */
const SenderInfo = styled(Box)`
  display: flex;
  align-items: center;
  margin-right: auto;
`;

/**
 * @styledcomponent SenderName
 * @description Styled component for the sender's name
 */
const SenderName = styled(Typography)`
  font-weight: 500;
  margin-left: 8px;
`;

/**
 * @styledcomponent Timestamp
 * @description Styled component for the message timestamp
 */
const Timestamp = styled(Typography)`
  font-size: 12px;
  color: #757575;
`;

/**
 * @styledcomponent MessageBody
 * @description Styled component for the message body text
 */
const MessageBody = styled(Typography)`
  white-space: pre-wrap;
  word-break: break-word;
`;

/**
 * @styledcomponent ChildMessages
 * @description Container for child messages with indentation
 */
const ChildMessages = styled(Box)<{ level: number }>`
  margin-left: ${props => props.level * 24}px;
  margin-top: 12px;
`;

/**
 * @styledcomponent EmptyState
 * @description Styled component for empty thread state
 */
const EmptyState = styled(Box)`
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 32px;
  text-align: center;
  color: #757575;
`;

/**
 * @styledcomponent ComposerContainer
 * @description Container for the message composer
 */
const ComposerContainer = styled(Box)`
  margin-top: 16px;
  border-top: 1px solid #e0e0e0;
  padding-top: 16px;
`;

/**
 * @styledcomponent RecommendationsContainer
 * @description Container for AI recommendation cards
 */
const RecommendationsContainer = styled(Box)`
  margin-top: 16px;
  margin-bottom: 16px;
  display: flex;
  flex-direction: column;
  gap: 8px;
`;

/**
 * @function MessageThread
 * @description Component for displaying a hierarchical thread of messages
 */
const MessageThread: React.FC<MessageThreadProps> = ({
  threadId,
  negotiationId,
  showComposer = true,
  autoScroll = true,
  showAIRecommendations = false,
  onMessageSent,
  className,
}) => {
  // LD1: Initialize Redux state using useSelector
  const messages = useSelector((state: any) => state.messages.messages);
  const loading = useSelector((state: any) => state.messages.loading);
  const error = useSelector((state: any) => state.messages.error);
  const { currentUser } = useAuth();
  const { currentOrganization } = useOrganizationContext();

  // LD1: Initialize component state using useState
  const [replyToMessage, setReplyToMessage] = useState<Message | null>(null);

  // LD1: Initialize Redux dispatch
  const dispatch = useDispatch();

  // LD1: Create refs for scrolling and focusing
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const composerRef = useRef<HTMLDivElement>(null);

  /**
   * @function scrollToBottom
   * @description Scrolls the message thread to the bottom to show latest messages
   */
  const scrollToBottom = useCallback(() => {
    if (messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, []);

  /**
   * @function handleReply
   * @description Handles the reply action for a specific message
   * @param {Message} message - The message being replied to
   */
  const handleReply = (message: Message) => {
    setReplyToMessage(message);
    if (composerRef.current) {
      // TODO: Implement focus on composer
    }
  };

  /**
   * @interface MessageTree
   * @extends Message
   * @description Extended Message type with children for hierarchical display
   */
  interface MessageTree extends Message {
    children: MessageTree[];
  }

  /**
   * @function buildMessageTree
   * @description Builds a hierarchical tree of messages based on parent-child relationships
   * @param {Message[]} messages - The list of messages to organize
   * @returns {MessageTree[]} A tree structure of messages with children property
   */
  const buildMessageTree = (messages: Message[]): MessageTree[] => {
    const messageMap: { [id: string]: MessageTree } = {};
    const rootMessages: MessageTree[] = [];

    // First pass: add all messages to the map
    messages.forEach(message => {
      messageMap[message.id] = { ...message, children: [] };
    });

    // Second pass: build the tree structure by adding children to parent messages
    messages.forEach(message => {
      const messageItem = messageMap[message.id];
      if (message.parentId && messageMap[message.parentId]) {
        messageMap[message.parentId].children.push(messageItem);
      } else {
        rootMessages.push(messageItem);
      }
    });

    return rootMessages;
  };

  /**
   * @function renderMessageItem
   * @description Renders a single message item with its children
   * @param {MessageTree} message - The message to render
   * @param {number} level - The indentation level for the message
   * @returns {JSX.Element} Rendered message component with children
   */
  const renderMessageItem = (message: MessageTree, level: number = 0): JSX.Element => {
    const isCurrentUser = currentUser?.id === message.senderId;

    return (
      <React.Fragment key={message.id}>
        <MessageItem>
          <MessageContent isCurrentUser={isCurrentUser}>
            <MessageHeader>
              <SenderInfo>
                <Avatar name={message.sender.name} imageUrl={message.sender.avatarUrl} size="sm" />
                <SenderName>{message.sender.name}</SenderName>
              </SenderInfo>
              <Timestamp>{formatDate(message.createdAt, 'MMM d, yyyy h:mm a')}</Timestamp>
            </MessageHeader>
            <MessageBody>{message.content}</MessageBody>
            <MessageAttachments attachments={message.attachments} />
            <Box sx={{ display: 'flex', justifyContent: 'flex-end', mt: 1 }}>
              <Button size="small" variant="text" startIcon={<ReplyIcon />} onClick={() => handleReply(message)}>
                Reply
              </Button>
            </Box>
          </MessageContent>
        </MessageItem>
        {message.children.length > 0 && (
          <ChildMessages level={level + 1}>
            {message.children.map(child => renderMessageItem(child, level + 1))}
          </ChildMessages>
        )}
      </React.Fragment>
    );
  };

  // LD1: Use useEffect to fetch messages when thread ID changes
  useEffect(() => {
    if (threadId) {
      dispatch(fetchThreadById(threadId));
    }
  }, [threadId, dispatch]);

  // LD1: Use useEffect to scroll to bottom when messages change if autoScroll is enabled
  useEffect(() => {
    if (autoScroll) {
      scrollToBottom();
    }
  }, [messages, autoScroll, scrollToBottom]);

  // LD1: Use useEffect to mark new messages as read when they are loaded
  useEffect(() => {
    if (messages && messages.length > 0) {
      // TODO: Implement mark as read
    }
  }, [messages]);

  return (
    <ThreadContainer className={className}>
      {loading && <Spinner />}
      {error && <Typography color="error">{error}</Typography>}
      {!loading && !error && messages && messages.length === 0 && (
        <EmptyState>
          <Typography variant="subtitle1">No messages in this thread.</Typography>
        </EmptyState>
      )}
      {!loading && messages && buildMessageTree(messages).map(message => renderMessageItem(message))}
      <div ref={messagesEndRef} />
      {showAIRecommendations && (
        <RecommendationsContainer>
          {/* TODO: Implement AI Recommendations */}
        </RecommendationsContainer>
      )}
      {showComposer && (
        <ComposerContainer ref={composerRef}>
          <MessageComposer
            threadId={threadId}
            parentId={replyToMessage?.id || null}
            onMessageSent={onMessageSent}
          />
        </ComposerContainer>
      )}
    </ThreadContainer>
  );
};

export default MessageThread;