import { createSlice, PayloadAction } from '@reduxjs/toolkit'; // ^1.9.5
import {
  Rate,
  RateState,
  RateFilter,
  RateSortOption
} from '../../types/rate';
import {
  fetchRates,
  fetchRateById,
  fetchRateHistory,
  submitRates,
  updateRate,
  approveRate,
  rejectRate,
  counterRate,
  fetchRateRequests,
  createRateRequest,
  fetchRateSubmissions
} from './ratesThunks';

/**
 * Initial state for the rates slice of the Redux store
 */
const initialState: RateState = {
  rates: {
    data: [],
    loading: false,
    error: null
  },
  rateById: {
    data: null,
    loading: false,
    error: null
  },
  rateHistory: {
    data: [],
    loading: false,
    error: null
  },
  rateRequests: {
    data: [],
    loading: false,
    error: null
  },
  rateSubmissions: {
    data: [],
    loading: false,
    error: null
  },
  rateFilters: {
    attorneyName: '',
    staffClass: '',
    effectiveDate: null,
    status: ''
  },
  rateSort: {
    field: 'amount',
    direction: 'desc'
  },
  pagination: {
    page: 1,
    limit: 10,
    total: 0
  }
};

/**
 * Redux Toolkit slice for managing rate-related data in the Justice Bid application.
 * This slice handles loading states, errors, filtering, sorting, and pagination
 * for rate data including submissions, negotiations, and approvals.
 */
const ratesSlice = createSlice({
  name: 'rates',
  initialState,
  reducers: {
    /**
     * Updates filter criteria for rates and resets to first page
     * @param state - Current state
     * @param action - Action containing new filter values
     */
    setRateFilters: (state, action: PayloadAction<RateFilter>) => {
      state.rateFilters = action.payload;
      state.pagination.page = 1; // Reset to first page when filters change
    },
    
    /**
     * Resets all filters to their initial values
     * @param state - Current state
     */
    resetRateFilters: (state) => {
      state.rateFilters = initialState.rateFilters;
      state.pagination.page = 1;
    },
    
    /**
     * Updates the sort criteria for rates
     * @param state - Current state
     * @param action - Action containing new sort options
     */
    setRateSort: (state, action: PayloadAction<RateSortOption>) => {
      state.rateSort = action.payload;
    },
    
    /**
     * Sets the current page number for pagination
     * @param state - Current state
     * @param action - Action containing new page number
     */
    setRatePage: (state, action: PayloadAction<number>) => {
      state.pagination.page = action.payload;
    },
    
    /**
     * Sets the item limit per page and resets to first page
     * @param state - Current state
     * @param action - Action containing new page size
     */
    setRateLimit: (state, action: PayloadAction<number>) => {
      state.pagination.limit = action.payload;
      state.pagination.page = 1; // Reset to first page when page size changes
    },
    
    /**
     * Clears all error messages in the state
     * @param state - Current state
     */
    clearRateErrors: (state) => {
      state.rates.error = null;
      state.rateById.error = null;
      state.rateHistory.error = null;
      state.rateRequests.error = null;
      state.rateSubmissions.error = null;
    },
    
    /**
     * Resets the entire state to initial values
     */
    resetRateState: () => initialState
  },
  extraReducers: (builder) => {
    // fetchRates - Get all rates based on filters
    builder
      .addCase(fetchRates.pending, (state) => {
        state.rates.loading = true;
        state.rates.error = null;
      })
      .addCase(fetchRates.fulfilled, (state, action) => {
        state.rates.loading = false;
        state.rates.data = action.payload;
        // If the API returns total count in metadata, update it
        if (action.payload.total !== undefined) {
          state.pagination.total = action.payload.total;
        } else {
          // Otherwise use the length of the returned array
          state.pagination.total = action.payload.length;
        }
      })
      .addCase(fetchRates.rejected, (state, action) => {
        state.rates.loading = false;
        state.rates.error = action.error.message || 'Failed to fetch rates';
      });

    // fetchRateById - Get a single rate by ID
    builder
      .addCase(fetchRateById.pending, (state) => {
        state.rateById.loading = true;
        state.rateById.error = null;
      })
      .addCase(fetchRateById.fulfilled, (state, action) => {
        state.rateById.loading = false;
        state.rateById.data = action.payload;
      })
      .addCase(fetchRateById.rejected, (state, action) => {
        state.rateById.loading = false;
        state.rateById.error = action.error.message || 'Failed to fetch rate details';
      });

    // fetchRateHistory - Get history for a specific rate
    builder
      .addCase(fetchRateHistory.pending, (state) => {
        state.rateHistory.loading = true;
        state.rateHistory.error = null;
      })
      .addCase(fetchRateHistory.fulfilled, (state, action) => {
        state.rateHistory.loading = false;
        state.rateHistory.data = action.payload;
      })
      .addCase(fetchRateHistory.rejected, (state, action) => {
        state.rateHistory.loading = false;
        state.rateHistory.error = action.error.message || 'Failed to fetch rate history';
      });

    // submitRates - Submit new rates for approval
    builder
      .addCase(submitRates.pending, (state) => {
        state.rates.loading = true;
        state.rates.error = null;
      })
      .addCase(submitRates.fulfilled, (state) => {
        state.rates.loading = false;
        // We would typically refresh the rates list after submission
        // but that would be handled by a separate action dispatch in the component
      })
      .addCase(submitRates.rejected, (state, action) => {
        state.rates.loading = false;
        state.rates.error = action.error.message || 'Failed to submit rates';
      });

    // updateRate - Update a single rate
    builder
      .addCase(updateRate.pending, (state) => {
        state.rates.loading = true;
        state.rates.error = null;
      })
      .addCase(updateRate.fulfilled, (state, action) => {
        state.rates.loading = false;
        // Update the rate in the rates array if it exists
        const updatedRate = action.payload;
        const index = state.rates.data.findIndex(rate => rate.id === updatedRate.id);
        if (index !== -1) {
          state.rates.data[index] = updatedRate;
        }
        
        // Also update the rateById if it's the same rate
        if (state.rateById.data && state.rateById.data.id === updatedRate.id) {
          state.rateById.data = updatedRate;
        }
      })
      .addCase(updateRate.rejected, (state, action) => {
        state.rates.loading = false;
        state.rates.error = action.error.message || 'Failed to update rate';
      });

    // approveRate - Approve one or more rates
    builder
      .addCase(approveRate.pending, (state) => {
        state.rates.loading = true;
        state.rates.error = null;
      })
      .addCase(approveRate.fulfilled, (state) => {
        state.rates.loading = false;
        // Update approved rates in the state
        // This would typically be followed by refreshing the rates list
      })
      .addCase(approveRate.rejected, (state, action) => {
        state.rates.loading = false;
        state.rates.error = action.error.message || 'Failed to approve rates';
      });

    // rejectRate - Reject one or more rates
    builder
      .addCase(rejectRate.pending, (state) => {
        state.rates.loading = true;
        state.rates.error = null;
      })
      .addCase(rejectRate.fulfilled, (state) => {
        state.rates.loading = false;
        // Update rejected rates in the state
        // This would typically be followed by refreshing the rates list
      })
      .addCase(rejectRate.rejected, (state, action) => {
        state.rates.loading = false;
        state.rates.error = action.error.message || 'Failed to reject rates';
      });

    // counterRate - Counter-propose one or more rates
    builder
      .addCase(counterRate.pending, (state) => {
        state.rates.loading = true;
        state.rates.error = null;
      })
      .addCase(counterRate.fulfilled, (state) => {
        state.rates.loading = false;
        // Update counter-proposed rates in the state
        // This would typically be followed by refreshing the rates list
      })
      .addCase(counterRate.rejected, (state, action) => {
        state.rates.loading = false;
        state.rates.error = action.error.message || 'Failed to counter-propose rates';
      });

    // fetchRateRequests - Get all rate requests
    builder
      .addCase(fetchRateRequests.pending, (state) => {
        state.rateRequests.loading = true;
        state.rateRequests.error = null;
      })
      .addCase(fetchRateRequests.fulfilled, (state, action) => {
        state.rateRequests.loading = false;
        state.rateRequests.data = action.payload;
      })
      .addCase(fetchRateRequests.rejected, (state, action) => {
        state.rateRequests.loading = false;
        state.rateRequests.error = action.error.message || 'Failed to fetch rate requests';
      });

    // createRateRequest - Create a new rate request
    builder
      .addCase(createRateRequest.pending, (state) => {
        state.rateRequests.loading = true;
        state.rateRequests.error = null;
      })
      .addCase(createRateRequest.fulfilled, (state) => {
        state.rateRequests.loading = false;
        // After creating a rate request, we would typically refresh the list
        // but that would be handled by a separate action dispatch in the component
      })
      .addCase(createRateRequest.rejected, (state, action) => {
        state.rateRequests.loading = false;
        state.rateRequests.error = action.error.message || 'Failed to create rate request';
      });

    // fetchRateSubmissions - Get all rate submissions
    builder
      .addCase(fetchRateSubmissions.pending, (state) => {
        state.rateSubmissions.loading = true;
        state.rateSubmissions.error = null;
      })
      .addCase(fetchRateSubmissions.fulfilled, (state, action) => {
        state.rateSubmissions.loading = false;
        state.rateSubmissions.data = action.payload;
      })
      .addCase(fetchRateSubmissions.rejected, (state, action) => {
        state.rateSubmissions.loading = false;
        state.rateSubmissions.error = action.error.message || 'Failed to fetch rate submissions';
      });
  }
});

// Export actions
export const {
  setRateFilters,
  resetRateFilters,
  setRateSort,
  setRatePage,
  setRateLimit,
  clearRateErrors,
  resetRateState
} = ratesSlice.actions;

// Define RootState type for selectors
export interface RootState {
  rates: RateState;
}

/**
 * Selectors for accessing rate state from components
 */

// Rates list selectors
export const selectRates = (state: RootState) => state.rates.rates.data;
export const selectRatesLoading = (state: RootState) => state.rates.rates.loading;
export const selectRatesError = (state: RootState) => state.rates.rates.error;

// Single rate selectors
export const selectRateById = (state: RootState) => state.rates.rateById.data;
export const selectRateByIdLoading = (state: RootState) => state.rates.rateById.loading;
export const selectRateByIdError = (state: RootState) => state.rates.rateById.error;

// Rate history selectors
export const selectRateHistory = (state: RootState) => state.rates.rateHistory.data;
export const selectRateHistoryLoading = (state: RootState) => state.rates.rateHistory.loading;
export const selectRateHistoryError = (state: RootState) => state.rates.rateHistory.error;

// Rate requests selectors
export const selectRateRequests = (state: RootState) => state.rates.rateRequests.data;
export const selectRateRequestsLoading = (state: RootState) => state.rates.rateRequests.loading;
export const selectRateRequestsError = (state: RootState) => state.rates.rateRequests.error;

// Rate submissions selectors
export const selectRateSubmissions = (state: RootState) => state.rates.rateSubmissions.data;
export const selectRateSubmissionsLoading = (state: RootState) => state.rates.rateSubmissions.loading;
export const selectRateSubmissionsError = (state: RootState) => state.rates.rateSubmissions.error;

// Filter and pagination selectors
export const selectRateFilters = (state: RootState) => state.rates.rateFilters;
export const selectRateSort = (state: RootState) => state.rates.rateSort;
export const selectRatePagination = (state: RootState) => state.rates.pagination;

// Export the reducer
export default ratesSlice.reducer;