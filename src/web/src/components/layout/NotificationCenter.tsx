import React, { useRef, useEffect } from 'react'; // React library for building UI components //  ^18.0.0
import { Link } from 'react-router-dom'; // For navigation links to notification-related pages //  ^6.4.0
import { useNotifications } from '../../hooks/useNotifications'; // Hook to fetch and manage notifications
import NotificationList from '../dashboard/NotificationList'; // Component to display the list of notifications
import { Button, Spinner, Alert } from '../common'; // Button component for actions
import { routes } from '../../constants/routes'; // Application route constants
import styled from 'styled-components';

/**
 * @internal
 * @remarks
 * Props interface for the NotificationCenter component
 */
interface NotificationCenterProps {
  /**
   * @internal
   * @remarks
   * Callback function to close the notification center
   */
  onClose: () => void;
}

const NotificationCenterContainer = styled.div`
  position: absolute;
  top: 100%;
  right: 0;
  background-color: #fff;
  border: 1px solid #ccc;
  border-radius: 4px;
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.2);
  padding: 10px;
  width: 300px;
  z-index: 1000;
`;

const NotificationCenterHeader = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
`;

const NotificationCenterContent = styled.div`
  max-height: 300px;
  overflow-y: auto;
`;

const NotificationCenterFooter = styled.div`
  margin-top: 10px;
  text-align: center;
`;

/**
 * @internal
 * @remarks
 * Helper function to handle clicks outside the notification center
 */
const handleClickOutside = (event: MouseEvent, onClose: () => void, ref: React.RefObject<HTMLDivElement>): void => {
  // LD1: Check if the click target is contained within the notification center ref
  if (ref.current && !ref.current.contains(event.target as Node)) {
    // LD1: If the click is outside, call the onClose function passed via props
    onClose();
  }
};

/**
 * @internal
 * @remarks
 * Functional component that displays notifications in a dropdown panel
 */
const NotificationCenter: React.FC<NotificationCenterProps> = ({ onClose }) => {
  // LD1: Destructure onClose from props
  
  // LD1: Get notifications, loading, error, markAsRead, and markAllAsRead from useNotifications hook
  const { notifications, unreadCount, loading, error, markAsRead, markAllAsRead } = useNotifications();

  // LD1: Create a ref for the notification center container
  const notificationCenterRef = useRef<HTMLDivElement>(null);

  // LD1: Set up an effect to add and remove click event listeners to handle outside clicks
  useEffect(() => {
    const handleOutsideClick = (event: MouseEvent) => {
      handleClickOutside(event, onClose, notificationCenterRef);
    };

    // Add event listener when the component mounts
    document.addEventListener('mousedown', handleOutsideClick);

    // Remove event listener when the component unmounts
    return () => {
      document.removeEventListener('mousedown', handleOutsideClick);
    };
  }, [onClose]);

  // LD1: Render a container div with ref attached
  return (
    <NotificationCenterContainer ref={notificationCenterRef}>
      {/* LD1: Render header with title and 'Mark All as Read' button if there are unread notifications */}
      <NotificationCenterHeader>
        <h3>Notifications</h3>
        {unreadCount > 0 && (
          <Button size="small" onClick={markAllAsRead}>
            Mark All as Read
          </Button>
        )}
      </NotificationCenterHeader>

      {/* LD1: Render content area with loading spinner if loading */}
      <NotificationCenterContent>
        {loading && <Spinner />}

        {/* LD1: Render error alert if there is an error */}
        {error && <Alert severity="error" message={error} />}

        {/* LD1: Render NotificationList component with notifications and markAsRead function */}
        {notifications && (
          <NotificationList
            notifications={notifications}
            markAsRead={markAsRead}
            limit={5}
            showViewAll={false}
          />
        )}
      </NotificationCenterContent>

      {/* LD1: Render footer with a link to view all notifications */}
      <NotificationCenterFooter>
        <Link to={routes.MESSAGES}>View All Notifications</Link>
      </NotificationCenterFooter>
    </NotificationCenterContainer>
  );
};

export default NotificationCenter;