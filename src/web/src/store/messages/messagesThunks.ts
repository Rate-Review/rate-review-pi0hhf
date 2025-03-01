/**
 * Redux thunks for message-related asynchronous operations, including fetching, creating, and managing messages between law firms and clients during rate negotiations.
 * @version 1.0.0
 */

import { createAsyncThunk } from '@reduxjs/toolkit'; //  ^1.9.5
import messagesService from '../../services/messages';
import { Message, Thread, MessageFilter, CreateMessageRequest } from '../../types/message';
import { RootState } from '../index';

/**
 * Thunk to fetch messages based on provided filters
 * @param filter - Filter criteria for messages
 * @returns List of retrieved messages
 */
export const fetchMessages = createAsyncThunk<
  Message[],
  MessageFilter,
  { rejectValue: { message: string } }
>(
  'messages/fetchMessages',
  async (filter: MessageFilter, thunkAPI) => {
    try {
      // Call messagesService.getMessages with provided filter
      const response = await messagesService.getMessages(filter);
      // Return messages list on success
      return response.items;
    } catch (error: any) {
      // Handle and throw errors on failure
      return thunkAPI.rejectWithValue({ message: error.message });
    }
  }
);

/**
 * Thunk to fetch a single message by ID
 * @param messageId - ID of the message to retrieve
 * @returns Retrieved message
 */
export const fetchMessageById = createAsyncThunk<
  Message,
  string,
  { rejectValue: { message: string } }
>(
  'messages/fetchMessageById',
  async (messageId: string, thunkAPI) => {
    try {
      // Call messagesService.getMessage with messageId
      const response = await messagesService.getMessage(messageId);
      // Return message on success
      return response.data;
    } catch (error: any) {
      // Handle and throw errors on failure
      return thunkAPI.rejectWithValue({ message: error.message });
    }
  }
);

/**
 * Thunk to fetch message threads
 * @param filter - Filter criteria for threads
 * @returns List of retrieved message threads
 */
export const fetchThreads = createAsyncThunk<
  Thread[],
  MessageFilter,
  { rejectValue: { message: string } }
>(
  'messages/fetchThreads',
  async (filter: MessageFilter, thunkAPI) => {
    try {
      // Call messagesService.getThreads with provided filter
      const response = await messagesService.getThreads(filter);
      // Return threads list on success
      return response.items;
    } catch (error: any) {
      // Handle and throw errors on failure
      return thunkAPI.rejectWithValue({ message: error.message });
    }
  }
);

/**
 * Thunk to fetch a thread and its messages by ID
 * @param threadId - ID of the thread to retrieve
 * @returns Retrieved thread with messages
 */
export const fetchThreadById = createAsyncThunk<
  Thread,
  string,
  { rejectValue: { message: string } }
>(
  'messages/fetchThreadById',
  async (threadId: string, thunkAPI) => {
    try {
      // Call messagesService.getThread with threadId
      const response = await messagesService.getThread(threadId);
      // Return thread with its messages on success
      return response.data;
    } catch (error: any) {
      // Handle and throw errors on failure
      return thunkAPI.rejectWithValue({ message: error.message });
    }
  }
);

/**
 * Thunk to create a new message
 * @param messageData - Data for the new message
 * @returns Newly created message
 */
export const createMessage = createAsyncThunk<
  Message,
  CreateMessageRequest,
  { rejectValue: { message: string } }
>(
  'messages/createMessage',
  async (messageData: CreateMessageRequest, thunkAPI) => {
    try {
      // Call messagesService.createMessage with messageData
      const response = await messagesService.createMessage(messageData);
      // Return created message on success
      return response.data;
    } catch (error: any) {
      // Handle and throw errors on failure
      return thunkAPI.rejectWithValue({ message: error.message });
    }
  }
);

/**
 * Thunk to mark a message as read
 * @param messageId - ID of the message to mark as read
 * @returns Confirmation of update
 */
export const markMessageAsRead = createAsyncThunk<
  void,
  string,
  { rejectValue: { message: string }; state: RootState }
>(
  'messages/markMessageAsRead',
  async (messageId: string, thunkAPI) => {
    try {
      // Call messagesService.markAsRead with messageId
      await messagesService.markAsRead(messageId);
      // Return success confirmation
      return;
    } catch (error: any) {
      // Handle and throw errors on failure
      return thunkAPI.rejectWithValue({ message: error.message });
    }
  }
);

/**
 * Thunk to search for messages based on query
 * @param searchQuery - Text to search for in messages
 * @returns List of matching messages
 */
export const searchMessages = createAsyncThunk<
  Message[],
  string,
  { rejectValue: { message: string } }
>(
  'messages/searchMessages',
  async (searchQuery: string, thunkAPI) => {
    try {
      // Call messagesService.searchMessages with searchQuery
      const response = await messagesService.searchMessages(searchQuery);
      // Return matching messages on success
      return response.items;
    } catch (error: any) {
      // Handle and throw errors on failure
      return thunkAPI.rejectWithValue({ message: error.message });
    }
  }
);