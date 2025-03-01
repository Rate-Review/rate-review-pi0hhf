import React from 'react';
import { useNavigate } from 'react-router-dom'; // react-router-dom ^6.10.0
import styled from 'styled-components'; // styled-components ^5.3.9
import Badge from '../common/Badge';
import Avatar from '../common/Avatar';
import { MessageNotificationType } from '../../types/message';
import { formatTimeAgo } from '../../utils/date';

// Define the props interface for the component
interface MessageNotificationProps {
  /**
   * The notification message data to display
   */
  notification: MessageNotificationType;
  
  /**
   * Optional callback function when a message is marked as read
   */
  onRead?: (messageId: string) => void;
  
  /**
   * Optional CSS class name
   */
  className?: string;
}

// Styled components for the notification
const NotificationContainer = styled.div<{ unread: boolean }>`
  display: flex;
  padding: 12px 16px;
  border-bottom: 1px solid ${props => props.theme.colors.divider};
  cursor: pointer;
  transition: background-color 0.2s ease;
  background-color: ${props => props.unread ? props.theme.colors.background.light : props.theme.colors.background.paper};

  &:hover {
    background-color: ${props => props.theme.colors.background.light};
  }
`;

const AvatarContainer = styled.div`
  margin-right: 12px;
  flex-shrink: 0;
`;

const ContentContainer = styled.div`
  flex: 1;
  min-width: 0;
`;

const Header = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 4px;
`;

const SenderName = styled.span`
  font-weight: 500;
  font-size: 14px;
  color: ${props => props.theme.colors.text.primary};
`;

const Timestamp = styled.span`
  font-size: 12px;
  color: ${props => props.theme.colors.text.secondary};
`;

const MessagePreview = styled.p`
  margin: 0;
  font-size: 13px;
  color: ${props => props.theme.colors.text.secondary};
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 100%;
`;

const ActionBar = styled.div`
  display: flex;
  justify-content: flex-end;
  margin-top: 8px;
`;

const ActionButton = styled.button`
  background: none;
  border: none;
  padding: 4px 8px;
  font-size: 12px;
  color: ${props => props.theme.colors.primary.main};
  cursor: pointer;
  transition: color 0.2s ease;

  &:hover {
    color: ${props => props.theme.colors.primary.dark};
  }

  &:focus {
    outline: none;
    box-shadow: 0 0 0 2px ${props => props.theme.colors.primary.light};
  }
`;

/**
 * MessageNotification component displays a notification for an individual message,
 * showing sender information, a message preview, and action buttons.
 * 
 * This component supports the Secure Messaging System (F-007) and 
 * Notification System (F-011) requirements.
 */
const MessageNotification: React.FC<MessageNotificationProps> = ({
  notification,
  onRead,
  className
}) => {
  const navigate = useNavigate();

  /**
   * Handles click events on the notification, navigating to the appropriate message thread
   */
  const handleClick = (event: React.MouseEvent) => {
    event.preventDefault();
    navigate(`/messages/thread/${notification.threadId}`);
  };

  /**
   * Marks the notification as read
   */
  const handleMarkAsRead = (event: React.MouseEvent) => {
    event.stopPropagation();
    if (onRead) {
      onRead(notification.id);
    }
  };

  return (
    <NotificationContainer 
      className={className}
      unread={!notification.isRead}
      onClick={handleClick}
    >
      <AvatarContainer>
        <Avatar 
          name={notification.sender.name} 
          imageUrl={notification.sender.avatarUrl} 
          size="md"
        />
      </AvatarContainer>
      <ContentContainer>
        <Header>
          <SenderName>
            {notification.sender.name}
            {!notification.isRead && (
              <Badge
                variant="primary"
                content="New"
                size="small"
                style={{ marginLeft: '8px' }}
              />
            )}
          </SenderName>
          <Timestamp>{formatTimeAgo(notification.createdAt)}</Timestamp>
        </Header>
        <MessagePreview>
          {notification.content.length > 100 
            ? `${notification.content.substring(0, 100)}...` 
            : notification.content}
        </MessagePreview>
        <ActionBar>
          {!notification.isRead && (
            <ActionButton onClick={handleMarkAsRead} aria-label="Mark as read">
              Mark as read
            </ActionButton>
          )}
          <ActionButton onClick={handleClick} aria-label="View thread">
            View thread
          </ActionButton>
        </ActionBar>
      </ContentContainer>
    </NotificationContainer>
  );
};

export default MessageNotification;