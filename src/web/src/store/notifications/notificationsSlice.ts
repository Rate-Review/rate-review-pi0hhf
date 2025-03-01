/**
 * Redux Toolkit slice for managing notification state in the Justice Bid Rate Negotiation System.
 * Handles notification fetching, reading, dismissal, and preferences with corresponding reducers and selectors.
 * 
 * @packageDocumentation
 * @module store/notifications
 * @version 1.0.0
 */

import { createSlice, PayloadAction } from '@reduxjs/toolkit'; //  ^1.9.5
import { RootState } from '../index';
import { Notification, NotificationPreferences } from '../../types';
import { SET_NOTIFICATIONS, ADD_NOTIFICATION, UPDATE_NOTIFICATION, REMOVE_NOTIFICATION, SET_PREFERENCES } from './notificationsThunks';

/**
 * @internal
 * @remarks
 * Interface for the notifications portion of the Redux store
 */
interface NotificationsState {
  /**
   * @remarks
   * Array of notifications
   */
  notifications: Notification[];
  /**
   * @remarks
   * Count of unread notifications
   */
  unreadCount: number;
  /**
   * @remarks
   * User's notification preferences
   */
  preferences: NotificationPreferences[];
  /**
   * @remarks
   * Whether notifications are loading
   */
  isLoading: boolean;
  /**
   * @remarks
   * Error message if any
   */
  error: string | null;
  /**
   * @remarks
   * Whether the notification panel is open
   */
  isPanelOpen: boolean;
}

/**
 * @internal
 * @remarks
 * Initial state for the notifications slice
 */
const initialState: NotificationsState = {
  notifications: [],
  unreadCount: 0,
  preferences: [],
  isLoading: false,
  error: null,
  isPanelOpen: false
};

/**
 * @internal
 * @remarks
 * Notifications slice for managing notification state
 */
const notificationsSlice = createSlice({
  name: 'notifications',
  initialState,
  reducers: {
    /**
     * Clears any error state in the notifications slice
     */
    clearError: (state) => {
      state.error = null;
    },
    /**
     * Toggles the visibility of the notification panel
     * @param action - PayloadAction<boolean | undefined>
     */
    toggleNotificationPanel: (state, action: PayloadAction<boolean | undefined>) => {
      if (action.payload !== undefined) {
        state.isPanelOpen = action.payload;
      } else {
        state.isPanelOpen = !state.isPanelOpen;
      }
    },
    /**
     * Resets the notification state to initial values
     */
    resetNotifications: () => initialState
  },
  extraReducers: (builder) => {
    builder
      .addCase(SET_NOTIFICATIONS, (state, action) => {
        state.notifications = action.payload;
        state.unreadCount = action.payload.filter(n => !n.isRead).length;
        state.isLoading = false;
      })
      .addCase(ADD_NOTIFICATION, (state, action) => {
        state.notifications.unshift(action.payload);
        if (!action.payload.isRead) {
          state.unreadCount += 1;
        }
      })
      .addCase(UPDATE_NOTIFICATION, (state, action) => {
        const index = state.notifications.findIndex(n => n.id === action.payload.id);
        if (index !== -1) {
          state.notifications[index] = { ...state.notifications[index], ...action.payload };
          if (action.payload.isRead && !state.notifications[index].isRead) {
            state.unreadCount = Math.max(0, state.unreadCount - 1);
          }
        }
      })
      .addCase(REMOVE_NOTIFICATION, (state, action) => {
        const index = state.notifications.findIndex(n => n.id === action.payload);
        if (index !== -1) {
          if (!state.notifications[index].isRead) {
            state.unreadCount = Math.max(0, state.unreadCount - 1);
          }
          state.notifications.splice(index, 1);
        }
      })
      .addCase(SET_PREFERENCES, (state, action) => {
        state.preferences = action.payload;
      });
  },
});

/**
 * @internal
 * @remarks
 * Export actions for use in components
 */
export const notificationsActions = {
    clearError: notificationsSlice.actions.clearError,
    toggleNotificationPanel: notificationsSlice.actions.toggleNotificationPanel,
    resetNotifications: notificationsSlice.actions.resetNotifications,
};

/**
 * @internal
 * @remarks
 * Selector to get all notifications from state
 * @param state - RootState
 * @returns Array of all notifications
 */
export const selectNotifications = (state: RootState): Notification[] => state.notifications.notifications;

/**
 * @internal
 * @remarks
 * Selector to get unread notification count from state
 * @param state - RootState
 * @returns Count of unread notifications
 */
export const selectUnreadCount = (state: RootState): number => state.notifications.unreadCount;

/**
 * @internal
 * @remarks
 * Selector to get notification preferences from state
 * @param state - RootState
 * @returns User's notification preferences
 */
export const selectNotificationPreferences = (state: RootState): NotificationPreferences[] => state.notifications.preferences;

/**
 * @internal
 * @remarks
 * Selector to get notification panel open state
 * @param state - RootState
 * @returns Whether the notification panel is open
 */
export const selectIsNotificationPanelOpen = (state: RootState): boolean => state.notifications.isPanelOpen;

/**
 * @internal
 * @remarks
 * Export the notifications reducer
 */
export default notificationsSlice.reducer;