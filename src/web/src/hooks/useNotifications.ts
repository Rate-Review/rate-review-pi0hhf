/**
 * Custom React hook that provides access to user notifications from Redux store and exposes functions for notification management.
 * Supports real-time notification updates via WebSockets and handles notification preferences as specified in the system requirements.
 *
 * @packageDocumentation
 * @module hooks
 * @version 1.0.0
 */

import { useCallback, useEffect, useState } from 'react'; //  ^18.2.0
import { useSelector, useDispatch } from 'react-redux'; //  ^8.0.5
import { io, Socket } from 'socket.io-client'; //  ^4.5.1
import { RootState } from '../store';
import {
  selectNotifications,
  selectUnreadCount,
  selectLoading,
  selectError,
  notificationsActions,
} from '../store/notifications/notificationsSlice';
import {
  fetchNotifications,
  markNotificationAsRead,
  markAllNotificationsAsRead,
  updateNotificationPreferences,
  subscribeToRealTimeNotifications,
  unsubscribeFromRealTimeNotifications,
} from '../store/notifications/notificationsThunks';
import { NotificationPreference as NotificationPreferenceData, Notification } from '../types';

/**
 * React hook that provides access to notification state from Redux and functions for notification management, with real-time notification updates via WebSockets
 *
 * @returns {object} An object containing notification state and management functions
 */
export const useNotifications = () => {
  // LD1: Get current notification state from Redux using useSelector with selectors
  const notifications = useSelector(selectNotifications);
  const unreadCount = useSelector(selectUnreadCount);
  const loading = useSelector(selectLoading);
  const error = useSelector(selectError);

  // LD1: Get dispatch function using useDispatch
  const dispatch = useDispatch();

  // LD1: Set up socket state for real-time notifications using useState
  const [socket, setSocket] = useState<Socket | null>(null);

  // LD1: Create fetchNotifications function using useCallback that dispatches the fetchNotifications thunk
  const fetchNotifications = useCallback(() => {
    dispatch(fetchNotifications());
  }, [dispatch]);

  // LD1: Create markAsRead function using useCallback that dispatches the markAsRead thunk with notification ID
  const markAsRead = useCallback(
    (notificationId: string) => {
      dispatch(markNotificationAsRead(notificationId));
    },
    [dispatch]
  );

  // LD1: Create markAllAsRead function using useCallback that dispatches the markAllAsRead thunk
  const markAllAsRead = useCallback(() => {
    dispatch(markAllNotificationsAsRead());
  }, [dispatch]);

  // LD1: Create updatePreferences function using useCallback that dispatches the updateNotificationPreferences thunk with preference data
  const updatePreferences = useCallback(
    (preferences: NotificationPreferenceData) => {
      dispatch(updateNotificationPreferences(preferences));
    },
    [dispatch]
  );

  // LD1: Set up useEffect to fetch notifications when the component mounts
  useEffect(() => {
    fetchNotifications();

    // IE1: Clean up function to clear any errors
    return () => {
      dispatch(notificationsActions.clearError());
    };
  }, [dispatch, fetchNotifications]);

  // LD1: Set up useEffect to initialize WebSocket connection for real-time notifications
  useEffect(() => {
    dispatch(subscribeToRealTimeNotifications());
    return () => {
      dispatch(unsubscribeFromRealTimeNotifications());
    };
  }, [dispatch]);

  // LD1: Return object with notification state and handler functions
  return {
    notifications,
    unreadCount,
    loading,
    error,
    fetchNotifications,
    markAsRead,
    markAllAsRead,
    updatePreferences,
  };
};