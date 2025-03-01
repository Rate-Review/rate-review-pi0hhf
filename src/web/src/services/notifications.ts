/**
 * Frontend service module that provides functions for interacting with the notification-related
 * endpoints of the Justice Bid API. It handles fetching notifications, marking notifications as 
 * read/unread, updating notification preferences, and real-time notification subscriptions.
 * 
 * @version 1.0.0
 */

import { 
  get, 
  post, 
  put, 
  delete as del, 
  getPaginated 
} from '../services/api';
import { 
  buildUrl, 
  buildUrlWithParams 
} from '../api/apiRoutes';
import { 
  NotificationType, 
  NotificationPriority, 
  PaginatedResponse,
  PaginationParams
} from '../types/common';

// Base API endpoint for notifications
const NOTIFICATIONS_API_BASE = '/notifications';

// Interface for notification objects
export interface Notification {
  id: string;
  type: NotificationType;
  priority: NotificationPriority;
  message: string;
  entityId?: string;
  entityType?: string;
  isRead: boolean;
  createdAt: string;
  userId: string;
}

// Interface for notification preferences
export interface NotificationPreference {
  type: NotificationType;
  enabled: boolean;
  channels: {
    email: boolean;
    inApp: boolean;
  };
}

/**
 * Fetches notifications for the current user with optional filtering
 * @param filter - Optional filter parameters
 * @returns Promise resolving to paginated notifications
 */
async function getNotifications(filter: {
  page?: number;
  pageSize?: number;
  type?: NotificationType;
  priority?: NotificationPriority;
  isRead?: boolean;
  startDate?: string;
  endDate?: string;
} = {}): Promise<PaginatedResponse<Notification>> {
  // Construct the API URL for notifications endpoint
  const url = buildUrl(NOTIFICATIONS_API_BASE);
  
  // Define pagination parameters
  const paginationParams: PaginationParams = {
    page: filter.page || 1,
    pageSize: filter.pageSize || 20
  };
  
  // Define filter parameters
  const filterParams = [];
  
  if (filter.type) {
    filterParams.push({
      field: 'type',
      operator: 'eq',
      value: filter.type
    });
  }
  
  if (filter.priority) {
    filterParams.push({
      field: 'priority',
      operator: 'eq',
      value: filter.priority
    });
  }
  
  if (filter.isRead !== undefined) {
    filterParams.push({
      field: 'isRead',
      operator: 'eq',
      value: filter.isRead
    });
  }
  
  if (filter.startDate && filter.endDate) {
    filterParams.push({
      field: 'createdAt',
      operator: 'between',
      value: [filter.startDate, filter.endDate]
    });
  } else if (filter.startDate) {
    filterParams.push({
      field: 'createdAt',
      operator: 'gte',
      value: filter.startDate
    });
  } else if (filter.endDate) {
    filterParams.push({
      field: 'createdAt',
      operator: 'lte',
      value: filter.endDate
    });
  }
  
  // Make the API call
  return getPaginated<Notification>(
    url,
    paginationParams,
    undefined, // No sorting parameters
    filterParams.length > 0 ? filterParams : undefined
  );
}

/**
 * Fetches the count of unread notifications for the current user
 * @returns Promise resolving to the count of unread notifications
 */
async function getUnreadCount(): Promise<number> {
  const url = buildUrl(`${NOTIFICATIONS_API_BASE}/unread-count`);
  const response = await get<{ count: number }>(url);
  return response.count;
}

/**
 * Marks a specific notification as read
 * @param notificationId - ID of the notification to mark as read
 * @returns Promise resolving to the updated notification
 */
async function markAsRead(notificationId: string): Promise<Notification> {
  const url = buildUrl(`${NOTIFICATIONS_API_BASE}/${notificationId}/read`);
  return put<Notification>(url, { isRead: true });
}

/**
 * Marks all notifications as read
 * @returns Promise resolving to success status and count of updated notifications
 */
async function markAllAsRead(): Promise<{ success: boolean, count: number }> {
  const url = buildUrl(`${NOTIFICATIONS_API_BASE}/mark-all-read`);
  return post<{ success: boolean, count: number }>(url);
}

/**
 * Dismisses/deletes a specific notification
 * @param notificationId - ID of the notification to dismiss
 * @returns Promise resolving to success status
 */
async function dismissNotification(notificationId: string): Promise<{ success: boolean }> {
  const url = buildUrl(`${NOTIFICATIONS_API_BASE}/${notificationId}`);
  return del<{ success: boolean }>(url);
}

/**
 * Fetches notification preferences for the current user
 * @returns Promise resolving to notification preferences
 */
async function getPreferences(): Promise<NotificationPreference[]> {
  const url = buildUrl(`${NOTIFICATIONS_API_BASE}/preferences`);
  const response = await get<{ preferences: NotificationPreference[] } | NotificationPreference[]>(url);
  
  // Handle both response formats (direct array or nested in preferences property)
  return Array.isArray(response) ? response : response.preferences;
}

/**
 * Updates notification preferences for the current user
 * @param preferences - Updated notification preferences
 * @returns Promise resolving to updated notification preferences
 */
async function updatePreferences(
  preferences: NotificationPreference[]
): Promise<NotificationPreference[]> {
  const url = buildUrl(`${NOTIFICATIONS_API_BASE}/preferences`);
  const response = await put<{ preferences: NotificationPreference[] } | NotificationPreference[]>(
    url, 
    { preferences }
  );
  
  // Handle both response formats (direct array or nested in preferences property)
  return Array.isArray(response) ? response : response.preferences;
}

/**
 * Subscribes to real-time notifications
 * @param onNotification - Callback function to handle incoming notifications
 * @returns Promise resolving to an object with an unsubscribe function
 */
async function subscribeToNotifications(
  onNotification: (notification: Notification) => void
): Promise<{ unsubscribe: () => void }> {
  try {
    // Get the websocket URL from the API
    const response = await get<{ url: string }>(`${NOTIFICATIONS_API_BASE}/stream`);
    
    // Extract WebSocket URL or construct it based on current environment
    const wsUrl = response.url || (() => {
      const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
      const host = window.location.host;
      const apiPath = process.env.REACT_APP_API_URL || '/api/v1';
      return `${wsProtocol}//${host}${apiPath}${NOTIFICATIONS_API_BASE}/stream`;
    })();
    
    // Create WebSocket connection
    const socket = new WebSocket(wsUrl);
    let reconnectTimer: number | null = null;
    let isClosing = false;
    
    const handleOpen = () => {
      console.log('Notification stream connected');
    };
    
    const handleMessage = (event: MessageEvent) => {
      try {
        const data = JSON.parse(event.data);
        if (data.notification) {
          onNotification(data.notification);
        }
      } catch (error) {
        console.error('Error parsing notification data:', error);
      }
    };
    
    const handleClose = (event: CloseEvent) => {
      console.log('Notification stream closed', event.code, event.reason);
      
      // Only attempt to reconnect if not intentionally closed
      if (!isClosing && event.code !== 1000) {
        // Attempt to reconnect after 5 seconds
        reconnectTimer = window.setTimeout(() => {
          console.log('Attempting to reconnect to notification stream...');
          subscribeToNotifications(onNotification);
        }, 5000);
      }
    };
    
    const handleError = (error: Event) => {
      console.error('Notification stream error:', error);
    };
    
    // Set up event handlers
    socket.addEventListener('open', handleOpen);
    socket.addEventListener('message', handleMessage);
    socket.addEventListener('close', handleClose);
    socket.addEventListener('error', handleError);
    
    // Return an object with an unsubscribe function
    return {
      unsubscribe: () => {
        // Mark as intentionally closing to prevent reconnection attempts
        isClosing = true;
        
        // Clear any pending reconnection attempts
        if (reconnectTimer) {
          clearTimeout(reconnectTimer);
        }
        
        // Remove event listeners
        socket.removeEventListener('open', handleOpen);
        socket.removeEventListener('message', handleMessage);
        socket.removeEventListener('close', handleClose);
        socket.removeEventListener('error', handleError);
        
        // Close the socket if open or connecting
        if (socket.readyState === WebSocket.OPEN || socket.readyState === WebSocket.CONNECTING) {
          socket.close(1000, 'Client unsubscribed');
        }
      }
    };
  } catch (error) {
    console.error('Failed to subscribe to notifications:', error);
    throw error;
  }
}

/**
 * Sends a test notification to verify notification setup
 * @param type - Type of notification to test
 * @param priority - Priority level of the test notification
 * @returns Promise resolving to success status
 */
async function testNotification(
  type: NotificationType,
  priority: NotificationPriority
): Promise<{ success: boolean }> {
  const url = buildUrl(`${NOTIFICATIONS_API_BASE}/test`);
  return post<{ success: boolean }>(url, { type, priority });
}

export default {
  getNotifications,
  getUnreadCount,
  markAsRead,
  markAllAsRead,
  dismissNotification,
  getPreferences,
  updatePreferences,
  subscribeToNotifications,
  testNotification
};

export type { Notification, NotificationPreference };