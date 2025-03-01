/**
 * Redux Toolkit thunks for managing asynchronous operations related to negotiations in the Justice Bid rate negotiation system.
 * This file implements API calls to fetch, create, update, and manipulate negotiation data, handling loading states and errors.
 *
 * @version 1.0.0
 */

import { createAsyncThunk } from '@reduxjs/toolkit'; // ^1.9.5
import { negotiationsService } from '../../services/negotiations';
import {
  Negotiation,
  NegotiationFilters,
  SubmitCounterProposalRequest,
  NegotiationApprovalRequest,
  BulkNegotiationAction
} from '../../types/negotiation';
import { NEGOTIATION_STATUS } from '../../constants/negotiations';
import { RootState } from '../index';

/**
 * Async thunk for fetching a list of negotiations with optional filtering
 * @param filters - Optional filter parameters
 * @returns Promise<Negotiation[]> - Array of negotiations matching the filter criteria
 */
export const fetchNegotiations = createAsyncThunk<
  Negotiation[],
  NegotiationFilters,
  { rejectValue: { message: string } }
>(
  'negotiations/fetchNegotiations',
  async (filters: NegotiationFilters, thunkAPI) => {
    try {
      // Call negotiationsService.getNegotiations with the provided filters
      const response = await negotiationsService.getNegotiations(filters);
      
      // Return the negotiations array from the response
      return response.data?.negotiations || [];
    } catch (error: any) {
      // Handle any errors and propagate them through rejectWithValue
      return thunkAPI.rejectWithValue({ message: error.message });
    }
  }
);

/**
 * Async thunk for fetching a single negotiation by ID
 * @param id - Negotiation ID
 * @returns Promise<Negotiation> - Detailed negotiation data
 */
export const fetchNegotiationById = createAsyncThunk<
  Negotiation,
  string,
  { rejectValue: { message: string } }
>(
  'negotiations/fetchNegotiationById',
  async (id: string, thunkAPI) => {
    try {
      // Call negotiationsService.getNegotiationById with the provided ID
      const response = await negotiationsService.getNegotiationById(id);
      
      // Return the negotiation data from the response
      return response.data?.negotiation as Negotiation;
    } catch (error: any) {
      // Handle any errors and propagate them through rejectWithValue
      return thunkAPI.rejectWithValue({ message: error.message });
    }
  }
);

/**
 * Async thunk for creating a new negotiation
 * @param negotiationData - Negotiation creation data
 * @returns Promise<Negotiation> - The created negotiation data
 */
export const createNegotiation = createAsyncThunk<
  Negotiation,
  object,
  { rejectValue: { message: string } }
>(
  'negotiations/createNegotiation',
  async (negotiationData: object, thunkAPI) => {
    try {
      // Call negotiationsService.createNegotiation with the provided data
      const response = await negotiationsService.createNegotiation(negotiationData);
      
      // Return the created negotiation from the response
      return response.data?.negotiation as Negotiation;
    } catch (error: any) {
      // Handle any errors and propagate them through rejectWithValue
      return thunkAPI.rejectWithValue({ message: error.message });
    }
  }
);

/**
 * Async thunk for updating an existing negotiation's details
 * @param { id: string, data: any } - Object containing ID and update data
 * @returns Promise<Negotiation> - The updated negotiation data
 */
export const updateNegotiation = createAsyncThunk<
  Negotiation,
  { id: string; data: any },
  { rejectValue: { message: string } }
>(
  'negotiations/updateNegotiation',
  async ({ id, data }: { id: string; data: any }, thunkAPI) => {
    try {
      // Call negotiationsService.updateNegotiation with the ID and data
      const response = await negotiationsService.updateNegotiation(id, data);
      
      // Return the updated negotiation from the response
      return response.data?.negotiation as Negotiation;
    } catch (error: any) {
      // Handle any errors and propagate them through rejectWithValue
      return thunkAPI.rejectWithValue({ message: error.message });
    }
  }
);

/**
 * Async thunk for submitting counter-proposals for rates in a negotiation
 * @param counterProposal - Counter-proposal data
 * @returns Promise<Negotiation> - The updated negotiation with counter-proposals
 */
export const submitCounterProposal = createAsyncThunk<
  Negotiation,
  SubmitCounterProposalRequest,
  { rejectValue: { message: string } }
>(
  'negotiations/submitCounterProposal',
  async (counterProposal: SubmitCounterProposalRequest, thunkAPI) => {
    try {
      // Call negotiationsService.submitCounterProposals with the provided data
      const response = await negotiationsService.submitCounterProposals(counterProposal);
      
      // Return the updated negotiation from the response
      return response.data?.negotiation as Negotiation;
    } catch (error: any) {
      // Handle any errors and propagate them through rejectWithValue
      return thunkAPI.rejectWithValue({ message: error.message });
    }
  }
);

/**
 * Async thunk for submitting bulk actions on multiple rates in a negotiation
 * @param bulkAction - Bulk action data
 * @returns Promise<Negotiation> - The updated negotiation after bulk actions
 */
export const submitBulkAction = createAsyncThunk<
  Negotiation,
  BulkNegotiationAction,
  { rejectValue: { message: string } }
>(
  'negotiations/submitBulkAction',
  async (bulkAction: BulkNegotiationAction, thunkAPI) => {
    try {
      // Call negotiationsService.submitBulkRateAction with the provided data
      const response = await negotiationsService.submitBulkRateAction(bulkAction);
      
      // Return the updated negotiation from the response
      return response.data?.negotiation as Negotiation;
    } catch (error: any) {
      // Handle any errors and propagate them through rejectWithValue
      return thunkAPI.rejectWithValue({ message: error.message });
    }
  }
);

/**
 * Async thunk for approving a negotiation
 * @param approvalData - Approval data
 * @returns Promise<Negotiation> - The updated negotiation with approval status
 */
export const approveNegotiation = createAsyncThunk<
  Negotiation,
  NegotiationApprovalRequest,
  { rejectValue: { message: string } }
>(
  'negotiations/approveNegotiation',
  async (approvalData: NegotiationApprovalRequest, thunkAPI) => {
    try {
      // Call negotiationsService.submitApproval with the provided data
      const response = await negotiationsService.submitApproval(approvalData);
      
      // Return the updated negotiation from the response
      return response.data?.negotiation as Negotiation;
    } catch (error: any) {
      // Handle any errors and propagate them through rejectWithValue
      return thunkAPI.rejectWithValue({ message: error.message });
    }
  }
);

/**
 * Async thunk for rejecting a negotiation
 * @param { id: string, reason: string } - Object containing ID and rejection reason
 * @returns Promise<Negotiation> - The updated negotiation with rejected status
 */
export const rejectNegotiation = createAsyncThunk<
  Negotiation,
  { id: string; reason: string },
  { rejectValue: { message: string } }
>(
  'negotiations/rejectNegotiation',
  async ({ id, reason }: { id: string; reason: string }, thunkAPI) => {
    try {
      // Call negotiationsService.updateNegotiationStatus with the ID and REJECTED status
      const response = await negotiationsService.updateNegotiationStatus(id, NEGOTIATION_STATUS.REJECTED);
      
      // Return the updated negotiation from the response
      return response.data?.negotiation as Negotiation;
    } catch (error: any) {
      // Handle any errors and propagate them through rejectWithValue
      return thunkAPI.rejectWithValue({ message: error.message });
    }
  }
);

/**
 * Async thunk for toggling real-time negotiation mode
 * @param { negotiationId: string, enabled: boolean } - Object containing negotiation ID and enabled flag
 * @returns Promise<Negotiation> - The updated negotiation with new mode setting
 */
export const toggleRealTimeNegotiation = createAsyncThunk<
  Negotiation,
  { negotiationId: string; enabled: boolean },
  { rejectValue: { message: string } }
>(
  'negotiations/toggleRealTimeNegotiation',
  async ({ negotiationId, enabled }: { negotiationId: string; enabled: boolean }, thunkAPI) => {
    try {
      // Call negotiationsService.toggleRealTimeMode with the negotiationId and enabled flag
      const response = await negotiationsService.toggleRealTimeMode(negotiationId, enabled);
      
      // Return the updated negotiation from the response
      return response.data?.negotiation as Negotiation;
    } catch (error: any) {
      // Handle any errors and propagate them through rejectWithValue
      return thunkAPI.rejectWithValue({ message: error.message });
    }
  }
);