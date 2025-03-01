/**
 * TypeScript interface declarations for message-related data structures
 * used throughout the Justice Bid Rate Negotiation System's frontend.
 * 
 * These types support the secure hierarchical messaging system that
 * allows communication between law firms and clients during rate negotiations.
 */

import { User } from '../types/user';
import { PaginationParams, PaginatedResponse } from '../types/common';

/**
 * Interface for message file attachments
 */
export interface Attachment {
  id: string;
  fileName: string;
  fileType: string;
  fileSize: number;
  fileUrl: string;
}

/**
 * Interface for uploading attachments with a message
 */
export interface AttachmentUpload {
  fileName: string;
  fileType: string;
  fileSize: number;
  file: File | Blob;
}

/**
 * Enum type for what entity a message relates to
 */
export enum RelatedEntityType {
  Negotiation = 'Negotiation',
  Rate = 'Rate',
  OCG = 'OCG'
}

/**
 * Interface for message data
 * Supports hierarchical organization through threadId and parentId
 */
export interface Message {
  id: string;
  threadId: string;
  parentId: string | null;
  senderId: string;
  sender: User;
  recipientIds: string[];
  content: string;
  attachments: Attachment[];
  relatedEntityType: RelatedEntityType | null;
  relatedEntityId: string | null;
  isRead: boolean;
  createdAt: string;
  updatedAt: string;
}

/**
 * Interface for message thread data
 * Threads organize messages into related conversations
 */
export interface MessageThread {
  id: string;
  title: string;
  participants: User[];
  relatedEntityType: RelatedEntityType | null;
  relatedEntityId: string | null;
  messageCount: number;
  unreadCount: number;
  latestMessage: Message | null;
  createdAt: string;
  updatedAt: string;
}

/**
 * Interface for creating a new message request
 */
export interface CreateMessageRequest {
  content: string;
  threadId: string | null;
  parentId: string | null;
  recipientIds: string[];
  attachments: AttachmentUpload[] | null;
  relatedEntityType: RelatedEntityType | null;
  relatedEntityId: string | null;
}

/**
 * Interface for creating a new message thread request
 */
export interface CreateThreadRequest {
  title: string;
  participantIds: string[];
  relatedEntityType: RelatedEntityType | null;
  relatedEntityId: string | null;
  initialMessage: CreateMessageRequest | null;
}

/**
 * Interface for filtering messages in API requests
 * Supports the ability to search and filter messages (F-007-RQ-004)
 */
export interface MessageFilter {
  threadId: string | null;
  parentId: string | null;
  senderId: string | null;
  isRead: boolean | null;
  relatedEntityType: RelatedEntityType | null;
  relatedEntityId: string | null;
  fromDate: string | null;
  toDate: string | null;
  searchText: string | null;
}

/**
 * Interface for message API response
 */
export interface MessageResponse {
  data: Message;
  status: string;
  message: string | null;
}

/**
 * Interface for thread API response with messages
 */
export interface ThreadResponse {
  data: MessageThread;
  messages: Message[];
  status: string;
  message: string | null;
}

/**
 * Interface for paginated message list response
 */
export interface MessageListResponse extends PaginatedResponse {
  items: Message[];
}

/**
 * Interface for paginated thread list response
 */
export interface ThreadListResponse extends PaginatedResponse {
  items: MessageThread[];
}

/**
 * Interface for marking multiple messages as read
 */
export interface MarkMessagesAsReadRequest {
  messageIds: string[];
}