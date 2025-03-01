/**
 * Redux thunks for notification-related asynchronous operations in the Justice Bid Rate Negotiation System.
 * Handles fetching notifications, marking notifications as read, dismissing notifications, and updating notification preferences.
 * 
 * @version 1.0.0
 */

import { createAsyncThunk } from '@reduxjs/toolkit'; // ^1.9.5
import { RootState, AppDispatch } from '../index';
import notificationsService, { 
  getNotifications,
  markAsRead,
  markAllAsRead,
  updatePreferences,
  dismissNotification,
  subscribeToNotifications
} from '../../services/notifications';
import { Notification, NotificationPreferences, NotificationFilter } from '../../types';

// Action type constants
export const SET_NOTIFICATIONS = 'notifications/setNotifications';
export const ADD_NOTIFICATION = 'notifications/addNotification';
export const UPDATE_NOTIFICATION = 'notifications/updateNotification';
export const REMOVE_NOTIFICATION = 'notifications/removeNotification';
export const SET_PREFERENCES = 'notifications/setPreferences';

// Track subscription reference for cleanup
let notificationSubscription: { unsubscribe: () => void } | null = null;

/**
 * Thunk for fetching notifications from the API and updating the store.
 * Supports filtering by notification type, urgency, read status, and date range.
 * 
 * @param filter Optional filter parameters to limit the notifications returned
 * @returns A promise that resolves to the array of fetched notifications
 */
export const fetchNotifications = createAsyncThunk<
  Array<Notification>,
  NotificationFilter | undefined,
  { state: RootState; dispatch: AppDispatch }
>('notifications/fetchNotifications', async (filter, thunkAPI) => {
  try {
    const response = await notificationsService.getNotifications(filter);
    
    // Update the Redux store with fetched notifications
    thunkAPI.dispatch({
      type: SET_NOTIFICATIONS,
      payload: response.items
    });
    
    return response.items;
  } catch (error) {
    return thunkAPI.rejectWithValue({
      message: error instanceof Error ? error.message : 'Failed to fetch notifications'
    });
  }
});

/**
 * Thunk for marking a notification as read.
 * Updates the read status in the API and the Redux store.
 * 
 * @param notificationId ID of the notification to mark as read
 * @returns A promise that resolves when the notification is marked as read
 */
export const markNotificationAsRead = createAsyncThunk<
  void,
  string,
  { dispatch: AppDispatch }
>('notifications/markAsRead', async (notificationId, thunkAPI) => {
  try {
    await notificationsService.markAsRead(notificationId);
    
    // Update the notification's read status in the Redux store
    thunkAPI.dispatch({
      type: UPDATE_NOTIFICATION,
      payload: { id: notificationId, isRead: true }
    });
  } catch (error) {
    return thunkAPI.rejectWithValue({
      message: error instanceof Error ? error.message : 'Failed to mark notification as read'
    });
  }
});

/**
 * Thunk for marking all notifications as read.
 * Updates the read status for all notifications in the API and the Redux store.
 * 
 * @returns A promise that resolves when all notifications are marked as read
 */
export const markAllNotificationsAsRead = createAsyncThunk<
  void,
  void,
  { dispatch: AppDispatch; state: RootState }
>('notifications/markAllAsRead', async (_, thunkAPI) => {
  try {
    const result = await notificationsService.markAllAsRead();
    
    // Get current notifications from state
    const state = thunkAPI.getState();
    const notifications = state.notifications.items;
    
    // Create updated notifications array with all items marked as read
    const updatedNotifications = notifications.map(notification => ({
      ...notification,
      isRead: true
    }));
    
    // Update all notifications in the Redux store
    thunkAPI.dispatch({
      type: SET_NOTIFICATIONS,
      payload: updatedNotifications
    });
  } catch (error) {
    return thunkAPI.rejectWithValue({
      message: error instanceof Error ? error.message : 'Failed to mark all notifications as read'
    });
  }
});

/**
 * Thunk for dismissing a notification.
 * Removes the notification from the API and the Redux store.
 * 
 * @param notificationId ID of the notification to dismiss
 * @returns A promise that resolves when the notification is dismissed
 */
export const dismissNotification = createAsyncThunk<
  void,
  string,
  { dispatch: AppDispatch }
>('notifications/dismiss', async (notificationId, thunkAPI) => {
  try {
    await notificationsService.dismissNotification(notificationId);
    
    // Remove the notification from the Redux store
    thunkAPI.dispatch({
      type: REMOVE_NOTIFICATION,
      payload: notificationId
    });
  } catch (error) {
    return thunkAPI.rejectWithValue({
      message: error instanceof Error ? error.message : 'Failed to dismiss notification'
    });
  }
});

/**
 * Thunk for updating notification preferences.
 * Updates preference settings in the API and the Redux store,
 * including email notification preferences and urgency level settings.
 * 
 * @param preferences New notification preference settings
 * @returns A promise that resolves to the updated notification preferences
 */
export const updateNotificationPreferences = createAsyncThunk<
  NotificationPreferences,
  NotificationPreferences,
  { dispatch: AppDispatch }
>('notifications/updatePreferences', async (preferences, thunkAPI) => {
  try {
    const data = await notificationsService.updatePreferences(preferences);
    
    // Update notification preferences in the Redux store
    thunkAPI.dispatch({
      type: SET_PREFERENCES,
      payload: data
    });
    
    return data;
  } catch (error) {
    return thunkAPI.rejectWithValue({
      message: error instanceof Error ? error.message : 'Failed to update notification preferences'
    });
  }
});

/**
 * Thunk for subscribing to real-time notifications.
 * Sets up a subscription to receive real-time notification updates.
 * 
 * @returns A promise that resolves when the subscription is set up
 */
export const subscribeToRealTimeNotifications = createAsyncThunk<
  void,
  void,
  { dispatch: AppDispatch }
>('notifications/subscribe', async (_, thunkAPI) => {
  try {
    // Clean up any existing subscription
    if (notificationSubscription) {
      notificationSubscription.unsubscribe();
    }
    
    // Set up new subscription with callback that dispatches new notifications
    notificationSubscription = await notificationsService.subscribeToNotifications(
      (notification) => {
        thunkAPI.dispatch({
          type: ADD_NOTIFICATION,
          payload: notification
        });
      }
    );
  } catch (error) {
    return thunkAPI.rejectWithValue({
      message: error instanceof Error ? error.message : 'Failed to subscribe to notifications'
    });
  }
});

/**
 * Thunk for unsubscribing from real-time notifications.
 * Cleans up the real-time notification subscription.
 * 
 * @returns A promise that resolves when the subscription is cleaned up
 */
export const unsubscribeFromRealTimeNotifications = createAsyncThunk<
  void,
  void,
  {}
>('notifications/unsubscribe', async (_, thunkAPI) => {
  try {
    // Clean up subscription if it exists
    if (notificationSubscription) {
      notificationSubscription.unsubscribe();
      notificationSubscription = null;
    }
  } catch (error) {
    return thunkAPI.rejectWithValue({
      message: error instanceof Error ? error.message : 'Failed to unsubscribe from notifications'
    });
  }
});