/**
 * Service module that provides API communication functions for messaging features
 * in the Justice Bid Rate Negotiation System. Handles all message and thread 
 * operations including creation, retrieval, searching, and read status management.
 * 
 * @version 1.0.0
 */

import { api } from '../services/api';
import { API_ROUTES } from '../api/apiRoutes';
import { 
  Message, 
  MessageThread, 
  CreateMessageRequest, 
  CreateThreadRequest,
  MessageFilter,
  MessageResponse,
  ThreadResponse,
  MessageListResponse,
  ThreadListResponse,
  MarkMessagesAsReadRequest
} from '../types/message';
import { PaginationParams } from '../types/common';

/**
 * Fetches messages based on provided filters with pagination
 * @param filter - Filter criteria for messages
 * @param pagination - Pagination parameters
 * @returns Promise resolving to paginated list of messages
 */
const getMessages = async (
  filter?: MessageFilter,
  pagination?: PaginationParams
): Promise<MessageListResponse> => {
  const url = api.buildUrl(API_ROUTES.MESSAGES.BASE);
  return api.getPaginated<Message>(url, pagination || { page: 1, pageSize: 20 }, undefined, 
    filter ? Object.entries(filter)
      .filter(([_, value]) => value !== null && value !== undefined)
      .map(([key, value]) => ({ field: key, operator: 'eq', value })) 
      : undefined
  );
};

/**
 * Fetches a single message by ID
 * @param messageId - ID of the message to retrieve
 * @returns Promise resolving to the message response
 */
const getMessage = async (messageId: string): Promise<MessageResponse> => {
  const url = api.buildUrl(API_ROUTES.MESSAGES.BY_ID.replace(':id', messageId));
  return api.get<MessageResponse>(url);
};

/**
 * Fetches message threads based on provided filters with pagination
 * @param filter - Filter criteria for threads
 * @param pagination - Pagination parameters
 * @returns Promise resolving to paginated list of threads
 */
const getThreads = async (
  filter?: MessageFilter,
  pagination?: PaginationParams
): Promise<ThreadListResponse> => {
  const url = api.buildUrl(`${API_ROUTES.MESSAGES.BASE}/threads`);
  return api.getPaginated<MessageThread>(url, pagination || { page: 1, pageSize: 20 }, undefined,
    filter ? Object.entries(filter)
      .filter(([_, value]) => value !== null && value !== undefined)
      .map(([key, value]) => ({ field: key, operator: 'eq', value }))
      : undefined
  );
};

/**
 * Fetches a specific thread and its messages by ID
 * @param threadId - ID of the thread to retrieve
 * @returns Promise resolving to the thread with its messages
 */
const getThread = async (threadId: string): Promise<ThreadResponse> => {
  const url = api.buildUrl(API_ROUTES.MESSAGES.THREAD.replace(':id', threadId));
  return api.get<ThreadResponse>(url);
};

/**
 * Creates a new message
 * @param messageData - Data for the new message
 * @returns Promise resolving to the created message
 */
const createMessage = async (messageData: CreateMessageRequest): Promise<MessageResponse> => {
  const url = api.buildUrl(API_ROUTES.MESSAGES.BASE);
  
  // If the message has attachments, use uploadFile
  if (messageData.attachments && messageData.attachments.length > 0) {
    const mainFile = messageData.attachments[0].file;
    const additionalData: Record<string, any> = {};
    
    // Add the message data to additionalData
    additionalData.content = messageData.content;
    if (messageData.threadId) additionalData.threadId = messageData.threadId;
    if (messageData.parentId) additionalData.parentId = messageData.parentId;
    
    // Convert recipient IDs to JSON string if present
    if (messageData.recipientIds && messageData.recipientIds.length) {
      additionalData.recipientIds = JSON.stringify(messageData.recipientIds);
    }
    
    if (messageData.relatedEntityType) additionalData.relatedEntityType = messageData.relatedEntityType;
    if (messageData.relatedEntityId) additionalData.relatedEntityId = messageData.relatedEntityId;
    
    // Return the upload request
    return api.uploadFile<MessageResponse>(url, mainFile, additionalData);
  }
  
  // If no attachments, use regular post
  return api.post<MessageResponse>(url, messageData);
};

/**
 * Creates a new message thread with an optional initial message
 * @param threadData - Data for the new thread
 * @returns Promise resolving to the created thread
 */
const createThread = async (threadData: CreateThreadRequest): Promise<ThreadResponse> => {
  const url = api.buildUrl(`${API_ROUTES.MESSAGES.BASE}/thread`);
  return api.post<ThreadResponse>(url, threadData);
};

/**
 * Marks a specific message as read
 * @param messageId - ID of the message to mark as read
 * @returns Promise resolving to the updated message
 */
const markAsRead = async (messageId: string): Promise<MessageResponse> => {
  const url = api.buildUrl(`${API_ROUTES.MESSAGES.BY_ID.replace(':id', messageId)}/read`);
  return api.post<MessageResponse>(url);
};

/**
 * Marks all messages in a thread as read
 * @param threadId - ID of the thread to mark as read
 * @returns Promise resolving to the updated thread
 */
const markThreadAsRead = async (threadId: string): Promise<ThreadResponse> => {
  const url = api.buildUrl(`${API_ROUTES.MESSAGES.THREAD.replace(':id', threadId)}/read`);
  return api.post<ThreadResponse>(url);
};

/**
 * Marks multiple messages as read at once
 * @param messageIds - Array of message IDs to mark as read
 * @returns Promise resolving when operation completes
 */
const markMultipleAsRead = async (messageIds: string[]): Promise<void> => {
  const url = api.buildUrl(`${API_ROUTES.MESSAGES.BASE}/mark-read`);
  const payload: MarkMessagesAsReadRequest = { messageIds };
  return api.post<void>(url, payload);
};

/**
 * Searches for messages based on search query and filters
 * @param searchQuery - Text to search for in messages
 * @param filter - Additional filter criteria
 * @param pagination - Pagination parameters
 * @returns Promise resolving to search results
 */
const searchMessages = async (
  searchQuery: string,
  filter?: MessageFilter,
  pagination?: PaginationParams
): Promise<MessageListResponse> => {
  const url = api.buildUrl(`${API_ROUTES.MESSAGES.BASE}/search`);
  
  // Combine search query with other filters
  const searchFilter = { 
    ...(filter || {}),
    searchText: searchQuery 
  };
  
  return api.getPaginated<Message>(url, pagination || { page: 1, pageSize: 20 }, undefined,
    Object.entries(searchFilter)
      .filter(([_, value]) => value !== null && value !== undefined)
      .map(([key, value]) => ({ field: key, operator: 'eq', value }))
  );
};

/**
 * Deletes a specific message
 * @param messageId - ID of the message to delete
 * @returns Promise resolving when deletion completes
 */
const deleteMessage = async (messageId: string): Promise<void> => {
  const url = api.buildUrl(API_ROUTES.MESSAGES.BY_ID.replace(':id', messageId));
  return api.delete<void>(url);
};

export default {
  getMessages,
  getMessage,
  getThreads,
  getThread,
  createMessage,
  createThread,
  markAsRead,
  markThreadAsRead,
  markMultipleAsRead,
  searchMessages,
  deleteMessage
};