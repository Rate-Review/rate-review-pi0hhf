import { createAsyncThunk } from '@reduxjs/toolkit'; // version: ^1.9.5
import { AxiosError } from 'axios'; // version: ^1.4.0
import {
  ocgService,
} from '../../services/ocg';
import {
  OCG,
  OCGFilter,
  OCGNegotiationRequest,
  OCGNegotiationResponse,
} from '../../types/ocg';
import {
  RootState,
  AppDispatch,
} from '../index';

/**
 * Async thunk that fetches a list of OCGs based on filter criteria
 * @param filter - OCGFilter
 * @returns Promise<OCG[]> Resolves to an array of OCG objects if successful
 */
export const fetchOCGs = createAsyncThunk<OCG[], OCGFilter, { state: RootState, dispatch: AppDispatch, rejectValue: string }>(
  'ocg/fetchOCGs',
  async (filter, thunkAPI) => {
    try {
      // Call ocgService.getOCGs with filter parameters
      const ocgs = await ocgService.getOCGs({ filter });
      // Handle successful response by returning OCGs array
      return ocgs;
    } catch (error) {
      // Handle errors by checking for AxiosError type
      let errorMessage = 'Failed to fetch OCGs';
      if (error instanceof AxiosError) {
        // Extract error message from response or use fallback
        errorMessage = error.response?.data?.message || errorMessage;
      }
      // Return error message using rejectWithValue from ThunkAPI
      return thunkAPI.rejectWithValue(errorMessage);
    }
  }
);

/**
 * Async thunk that fetches a single OCG by its ID
 * @param id - string
 * @returns Promise<OCG> Resolves to an OCG object if successful
 */
export const fetchOCGById = createAsyncThunk<OCG, string, { state: RootState, dispatch: AppDispatch, rejectValue: string }>(
  'ocg/fetchOCGById',
  async (id, thunkAPI) => {
    try {
      // Call ocgService.getOCGById with the provided ID
      const ocg = await ocgService.getOCGById(id);
      // Handle successful response by returning OCG object
      return ocg;
    } catch (error) {
      // Handle errors by checking for AxiosError type
      let errorMessage = 'Failed to fetch OCG by ID';
      if (error instanceof AxiosError) {
        // Extract error message from response or use fallback
        errorMessage = error.response?.data?.message || errorMessage;
      }
      // Return error message using rejectWithValue from ThunkAPI
      return thunkAPI.rejectWithValue(errorMessage);
    }
  }
);

/**
 * Async thunk that creates a new OCG
 * @param ocgData - Partial<OCG>
 * @returns Promise<OCG> Resolves to the created OCG object if successful
 */
export const createOCG = createAsyncThunk<OCG, Partial<OCG>, { state: RootState, dispatch: AppDispatch, rejectValue: string }>(
  'ocg/createOCG',
  async (ocgData, thunkAPI) => {
    try {
      // Call ocgService.createOCG with the provided OCG data
      const createdOCG = await ocgService.createOCG(ocgData);
      // Handle successful response by returning created OCG object
      return createdOCG;
    } catch (error) {
      // Handle errors by checking for AxiosError type
      let errorMessage = 'Failed to create OCG';
      if (error instanceof AxiosError) {
        // Extract error message from response or use fallback
        errorMessage = error.response?.data?.message || errorMessage;
      }
      // Return error message using rejectWithValue from ThunkAPI
      return thunkAPI.rejectWithValue(errorMessage);
    }
  }
);

/**
 * Async thunk that updates an existing OCG
 * @param { id: string, ocgData: Partial<OCG> } - { id: string, ocgData: Partial<OCG> }
 * @returns Promise<OCG> Resolves to the updated OCG object if successful
 */
export const updateOCG = createAsyncThunk<OCG, { id: string, ocgData: Partial<OCG> }, { state: RootState, dispatch: AppDispatch, rejectValue: string }>(
  'ocg/updateOCG',
  async (payload, thunkAPI) => {
    try {
      // Destructure id and ocgData from payload ({ id, ocgData })
      const { id, ocgData } = payload;
      // Call ocgService.updateOCG with id and ocgData
      const updatedOCG = await ocgService.updateOCG(id, ocgData);
      // Handle successful response by returning updated OCG object
      return updatedOCG;
    } catch (error) {
      // Handle errors by checking for AxiosError type
      let errorMessage = 'Failed to update OCG';
      if (error instanceof AxiosError) {
        // Extract error message from response or use fallback
        errorMessage = error.response?.data?.message || errorMessage;
      }
      // Return error message using rejectWithValue from ThunkAPI
      return thunkAPI.rejectWithValue(errorMessage);
    }
  }
);

/**
 * Async thunk that deletes an OCG by its ID
 * @param id - string
 * @returns Promise<string> Resolves to the deleted OCG ID if successful
 */
export const deleteOCG = createAsyncThunk<string, string, { state: RootState, dispatch: AppDispatch, rejectValue: string }>(
  'ocg/deleteOCG',
  async (id, thunkAPI) => {
    try {
      // Call ocgService.deleteOCG with the provided ID
      await ocgService.deleteOCG(id);
      // Handle successful response by returning the deleted OCG ID
      return id;
    } catch (error) {
      // Handle errors by checking for AxiosError type
      let errorMessage = 'Failed to delete OCG';
      if (error instanceof AxiosError) {
        // Extract error message from response or use fallback
        errorMessage = error.response?.data?.message || errorMessage;
      }
      // Return error message using rejectWithValue from ThunkAPI
      return thunkAPI.rejectWithValue(errorMessage);
    }
  }
);

/**
 * Async thunk that submits OCG negotiation selections from a law firm
 * @param negotiationData - OCGNegotiationRequest
 * @returns Promise<OCG> Resolves to the updated OCG with negotiation data if successful
 */
export const submitOCGNegotiation = createAsyncThunk<OCG, OCGNegotiationRequest, { state: RootState, dispatch: AppDispatch, rejectValue: string }>(
  'ocg/submitOCGNegotiation',
  async (negotiationData, thunkAPI) => {
    try {
      // Call ocgService.submitOCGNegotiation with negotiation data
      const updatedOCG = await ocgService.submitOCGNegotiation(negotiationData);
      // Handle successful response by returning updated OCG object
      return updatedOCG;
    } catch (error) {
      // Handle errors by checking for AxiosError type
      let errorMessage = 'Failed to submit OCG negotiation';
      if (error instanceof AxiosError) {
        // Extract error message from response or use fallback
        errorMessage = error.response?.data?.message || errorMessage;
      }
      // Return error message using rejectWithValue from ThunkAPI
      return thunkAPI.rejectWithValue(errorMessage);
    }
  }
);

/**
 * Async thunk that allows a client to respond to OCG negotiation from a law firm
 * @param responseData - OCGNegotiationResponse
 * @returns Promise<OCG> Resolves to the updated OCG with response data if successful
 */
export const respondToOCGNegotiation = createAsyncThunk<OCG, OCGNegotiationResponse, { state: RootState, dispatch: AppDispatch, rejectValue: string }>(
  'ocg/respondToOCGNegotiation',
  async (responseData, thunkAPI) => {
    try {
      // Call ocgService.respondToOCGNegotiation with response data
      const updatedOCG = await ocgService.respondToOCGNegotiation(responseData);
      // Handle successful response by returning updated OCG object
      return updatedOCG;
    } catch (error) {
      // Handle errors by checking for AxiosError type
      let errorMessage = 'Failed to respond to OCG negotiation';
      if (error instanceof AxiosError) {
        // Extract error message from response or use fallback
        errorMessage = error.response?.data?.message || errorMessage;
      }
      // Return error message using rejectWithValue from ThunkAPI
      return thunkAPI.rejectWithValue(errorMessage);
    }
  }
);

/**
 * Async thunk that finalizes an OCG after negotiations are complete
 * @param id - string
 * @returns Promise<OCG> Resolves to the finalized OCG object if successful
 */
export const finalizeOCG = createAsyncThunk<OCG, string, { state: RootState, dispatch: AppDispatch, rejectValue: string }>(
  'ocg/finalizeOCG',
  async (id, thunkAPI) => {
    try {
      // Call ocgService.finalizeOCG with the provided ID
      const finalizedOCG = await ocgService.finalizeOCG(id);
      // Handle successful response by returning finalized OCG object
      return finalizedOCG;
    } catch (error) {
      // Handle errors by checking for AxiosError type
      let errorMessage = 'Failed to finalize OCG';
      if (error instanceof AxiosError) {
        // Extract error message from response or use fallback
        errorMessage = error.response?.data?.message || errorMessage;
      }
      // Return error message using rejectWithValue from ThunkAPI
      return thunkAPI.rejectWithValue(errorMessage);
    }
  }
);