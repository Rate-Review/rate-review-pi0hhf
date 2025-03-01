import { createSlice, PayloadAction } from '@reduxjs/toolkit'; // ^1.9.5
import {
  NegotiationState,
  Negotiation,
  NegotiationStatus,
  NegotiationFilters
} from '../types/negotiation';
import {
  fetchNegotiations,
  fetchNegotiationById,
  submitCounterProposal,
  approveNegotiation,
  rejectNegotiation
} from './negotiationsThunks';
import { NEGOTIATION_STATUS } from '../constants/negotiations';
import { RootState } from '../index';

/**
 * The initial state for the negotiations slice
 */
const initialState: NegotiationState = {
  negotiations: [],
  loading: false,
  error: null,
  filters: {
    status: [],
    type: [],
    clientId: '',
    firmId: '',
    startDate: '',
    endDate: '',
    search: '',
    sortBy: '',
    sortDirection: '',
    page: 1,
    pageSize: 10
  }
};

/**
 * Redux slice for managing the negotiations state in the Justice Bid rate negotiation system.
 * This file defines the state shape, actions, reducers, and selectors related to negotiations.
 */
const negotiationsSlice = createSlice({
  name: 'negotiations',
  initialState,
  reducers: {
    /**
     * Updates the filters in state
     * @param state 
     * @param action 
     */
    setNegotiationFilters: (state, action: PayloadAction<NegotiationFilters>) => {
      state.filters = action.payload;
    },
    /**
     * Resets filters to default values
     * @param state 
     */
    resetNegotiationFilters: (state) => {
      state.filters = initialState.filters;
    },
    /**
     * Clears the negotiations array
     * @param state 
     */
    clearNegotiations: (state) => {
      state.negotiations = [];
    }
  },
  extraReducers: (builder) => {
    builder
      // fetchNegotiations
      .addCase(fetchNegotiations.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchNegotiations.fulfilled, (state, action) => {
        state.loading = false;
        state.negotiations = action.payload;
      })
      .addCase(fetchNegotiations.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message || 'Failed to fetch negotiations';
      })
      // fetchNegotiationById
      .addCase(fetchNegotiationById.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchNegotiationById.fulfilled, (state, action) => {
        state.loading = false;
        // Find the index of the negotiation to update
        const index = state.negotiations.findIndex(
          (negotiation) => negotiation.id === action.payload.id
        );
        if (index !== -1) {
          // Update the negotiation in the array
          state.negotiations[index] = action.payload;
        }
      })
      .addCase(fetchNegotiationById.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message || 'Failed to fetch negotiation';
      })
      // submitCounterProposal
      .addCase(submitCounterProposal.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(submitCounterProposal.fulfilled, (state, action) => {
        state.loading = false;
        // Find the index of the negotiation to update
        const index = state.negotiations.findIndex(
          (negotiation) => negotiation.id === action.payload.id
        );
        if (index !== -1) {
          // Update the negotiation in the array
          state.negotiations[index] = action.payload;
        }
      })
      .addCase(submitCounterProposal.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message || 'Failed to submit counter proposal';
      })
      // approveNegotiation
      .addCase(approveNegotiation.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(approveNegotiation.fulfilled, (state, action) => {
        state.loading = false;
        // Find the index of the negotiation to update
        const index = state.negotiations.findIndex(
          (negotiation) => negotiation.id === action.payload.id
        );
        if (index !== -1) {
          // Update the negotiation in the array
          state.negotiations[index] = action.payload;
        }
      })
      .addCase(approveNegotiation.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message || 'Failed to approve negotiation';
      })
      // rejectNegotiation
      .addCase(rejectNegotiation.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(rejectNegotiation.fulfilled, (state, action) => {
        state.loading = false;
        // Find the index of the negotiation to update
        const index = state.negotiations.findIndex(
          (negotiation) => negotiation.id === action.payload.id
        );
        if (index !== -1) {
          // Update the negotiation in the array
          state.negotiations[index] = action.payload;
        }
      })
      .addCase(rejectNegotiation.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message || 'Failed to reject negotiation';
      });
  },
});

// Extract the action creators from the slice
export const { setNegotiationFilters, resetNegotiationFilters, clearNegotiations } = negotiationsSlice.actions;

// Define RootState type for selectors
interface RootStateWithNegotiations {
    negotiations: NegotiationState;
}

/**
 * Selector to retrieve all negotiations from the state
 * @param state 
 * @returns Array of negotiations
 */
export const selectAllNegotiations = (state: RootStateWithNegotiations): Negotiation[] => state.negotiations.negotiations;

/**
 * Selector to retrieve a specific negotiation by ID
 * @param state 
 * @param id 
 * @returns The negotiation with the matching ID, or undefined if not found
 */
export const selectNegotiationById = (state: RootStateWithNegotiations, id: string): Negotiation | undefined =>
  state.negotiations.negotiations.find((negotiation) => negotiation.id === id);

/**
 * Selector to retrieve all active negotiations
 * @param state 
 * @returns Array of active negotiations
 */
export const selectActiveNegotiations = (state: RootStateWithNegotiations): Negotiation[] =>
  state.negotiations.negotiations.filter((negotiation) => negotiation.status === NEGOTIATION_STATUS.IN_PROGRESS);

/**
 * Selector to retrieve negotiations filtered by status
 * @param state 
 * @param status 
 * @returns Array of negotiations with the specified status
 */
export const selectNegotiationsByStatus = (state: RootStateWithNegotiations, status: NegotiationStatus): Negotiation[] =>
  state.negotiations.negotiations.filter((negotiation) => negotiation.status === status);

/**
 * Selector to retrieve negotiations filtered by multiple criteria
 * @param state 
 * @param filters 
 * @returns Array of negotiations matching the filter criteria
 */
export const selectNegotiationsByFilters = (state: RootStateWithNegotiations, filters: NegotiationFilters): Negotiation[] => {
  let filteredNegotiations = [...state.negotiations.negotiations];

  if (filters.status && filters.status.length > 0) {
    filteredNegotiations = filteredNegotiations.filter(negotiation =>
      filters.status.includes(negotiation.status)
    );
  }

  if (filters.type && filters.type.length > 0) {
    filteredNegotiations = filteredNegotiations.filter(negotiation =>
      filters.type.includes(negotiation.type)
    );
  }

  if (filters.clientId) {
    filteredNegotiations = filteredNegotiations.filter(negotiation =>
      negotiation.clientId === filters.clientId
    );
  }

  if (filters.firmId) {
    filteredNegotiations = filteredNegotiations.filter(negotiation =>
      negotiation.firmId === filters.firmId
    );
  }

  return filteredNegotiations;
};

/**
 * Selector to retrieve the loading state
 * @param state 
 * @returns The loading state
 */
export const selectNegotiationLoading = (state: RootStateWithNegotiations): boolean => state.negotiations.loading;

/**
 * Selector to retrieve any error state
 * @param state 
 * @returns The error message or null if no error
 */
export const selectNegotiationError = (state: RootStateWithNegotiations): string | null => state.negotiations.error;

// Export the reducer
export default negotiationsSlice.reducer;

// Export selectors
export {
  selectAllNegotiations,
  selectNegotiationById,
  selectActiveNegotiations,
  selectNegotiationsByStatus,
  selectNegotiationsByFilters,
  selectNegotiationLoading,
  selectNegotiationError
};