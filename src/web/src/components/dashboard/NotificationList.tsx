import React, { useEffect, useState } from 'react'; // React library for building UI components //  ^18.0.0
import { useNavigate } from 'react-router-dom'; // Routing library for navigation in React applications //  ^6.4.0
import { useNotifications } from '../../hooks/useNotifications'; // Custom hook for fetching and managing notifications
import { Notification } from '../../types'; // TypeScript interface for notification data structure
import Badge from '../common/Badge'; // UI component for displaying status badges
import Avatar from '../common/Avatar'; // UI component for displaying user avatars
import Button from '../common/Button'; // UI component for interactive buttons
import { formatDistanceToNow } from '../../utils/date'; // Utility function for formatting relative time
import styled from 'styled-components';

/**
 * @internal
 * @remarks
 * Props interface for the NotificationList component
 */
interface NotificationListProps {
  /**
   * @remarks
   * Maximum number of notifications to display
   */
  limit?: number;
  /**
   * @remarks
   * Whether to show a "View All" button
   */
  showViewAll?: boolean;
  /**
   * @remarks
   * Optional CSS class name
   */
  className?: string;
}

const NotificationListContainer = styled.div`
  /* Add styling for the container */
`;

const NotificationItem = styled.div`
  display: flex;
  align-items: center;
  padding: 10px;
  border-bottom: 1px solid #eee;
  &:last-child {
    border-bottom: none;
  }
`;

const NotificationContent = styled.div`
  flex: 1;
  margin-left: 10px;
`;

const NotificationActions = styled.div`
  display: flex;
  align-items: center;
`;

const ViewAllButtonContainer = styled.div`
  text-align: center;
  padding: 10px;
`;

/**
 * @internal
 * @remarks
 * Helper function to determine the appropriate badge type based on notification priority
 */
const getStatusBadge = (priority: string) => {
  switch (priority) {
    case 'high':
      return { variant: 'warning', label: 'High' };
    case 'medium':
      return { variant: 'info', label: 'Medium' };
    case 'low':
      return { variant: 'neutral', label: 'Low' };
    default:
      return { variant: 'primary', label: 'Normal' };
  }
};

/**
 * @internal
 * @remarks
 * Helper function to determine the appropriate icon based on notification type
 */
const getNotificationIcon = (type: string) => {
  switch (type) {
    case 'rate_request':
      return 'RateRequestIcon';
    case 'counter_proposal':
      return 'CounterProposalIcon';
    case 'approval':
      return 'ApprovalIcon';
    default:
      return 'DefaultIcon';
  }
};

/**
 * @internal
 * @remarks
 * Handler for when a user clicks on a notification
 */
const handleNotificationClick = (notification: Notification, navigate: any, markAsRead: any) => (event: React.MouseEvent) => {
  event.preventDefault();
  markAsRead(notification.id);
  // TODO: Implement navigation logic based on notification type
  // navigate(`/notifications/${notification.id}`);
};

/**
 * @internal
 * @remarks
 * A functional component that renders a list of notifications on the dashboard
 */
const NotificationList: React.FC<NotificationListProps> = ({ limit = 5, showViewAll = true, className }) => {
  // LD1: Define state for notifications using useState hook
  const [notifications, setNotifications] = useState<Notification[]>([]);

  // LD1: Use the useNotifications hook to access notification functionality
  const { notifications: allNotifications, markAsRead } = useNotifications();

  // LD1: Use the useNavigate hook for navigation to related content
  const navigate = useNavigate();

  // LD1: Fetch notifications on component mount using useEffect
  useEffect(() => {
    if (allNotifications) {
      setNotifications(allNotifications.slice(0, limit));
    }
  }, [allNotifications, limit]);

  // LD1: Render a list of notifications with avatars, content, timestamp, and action buttons
  return (
    <NotificationListContainer className={className}>
      {notifications.length > 0 ? (
        notifications.map((notification) => (
          <NotificationItem key={notification.id}>
            <Avatar name={notification.userId} />
            <NotificationContent>
              <a href="#" onClick={handleNotificationClick(notification, navigate, markAsRead)}>
                {notification.message}
              </a>
              <p>
                {formatDistanceToNow(notification.createdAt)} ago
                <Badge {...getStatusBadge(notification.priority)} />
              </p>
            </NotificationContent>
            <NotificationActions>
              <Button size="small" onClick={() => markAsRead(notification.id)}>
                Mark as Read
              </Button>
            </NotificationActions>
          </NotificationItem>
        ))
      ) : (
        <p>No notifications available.</p>
      )}
      {/* LD1: Render a 'View All' button at the bottom of the list */}
      {showViewAll && notifications.length > 0 && (
        <ViewAllButtonContainer>
          <Button variant="text" onClick={() => navigate('/notifications')}>
            View All
          </Button>
        </ViewAllButtonContainer>
      )}
    </NotificationListContainer>
  );
};

export default NotificationList;