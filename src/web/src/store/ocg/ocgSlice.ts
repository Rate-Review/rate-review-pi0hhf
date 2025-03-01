/**
 * Redux slice for managing Outside Counsel Guidelines (OCG) state in the application, including actions, reducers, and selectors for OCG management
 *
 * @packageDocumentation
 * @module store/ocg
 * @version 1.0.0
 */

import { createSlice, PayloadAction } from '@reduxjs/toolkit'; //  ^1.9.5
import { RootState } from '../index';
import { OCG, OCGSection, OCGAlternative } from '../../types/ocg';
import { fetchOCGs, fetchOCGById, createOCG, updateOCG, deleteOCG, submitOCGForNegotiation, negotiateOCG, publishOCG } from './ocgThunks';

/**
 * Interface defining the structure of the OCG state within the Redux store.
 * It includes arrays of OCGs, the currently selected OCG, loading states, and error messages.
 */
interface OCGState {
  ocgs: OCG[];
  currentOCG: OCG | null;
  loading: {
    list: boolean;
    detail: boolean;
    create: boolean;
    update: boolean;
    delete: boolean;
    submit: boolean;
		negotiate: boolean;
		publish: boolean;
  };
  error: {
    list: string | null;
    detail: string | null;
    create: string | null;
    update: string | null;
    delete: string | null;
    submit: string | null;
		negotiate: string | null;
		publish: string | null;
  };
}

/**
 * Initial state for the OCG slice.
 * Defines the default values for OCGs, currentOCG, loading, and error.
 */
const initialState: OCGState = {
  ocgs: [],
  currentOCG: null,
  loading: {
    list: false,
    detail: false,
    create: false,
    update: false,
    delete: false,
    submit: false,
		negotiate: false,
		publish: false,
  },
  error: {
    list: null,
    detail: null,
    create: null,
    update: null,
    delete: null,
    submit: null,
		negotiate: null,
		publish: null,
  },
};

/**
 * Redux slice for managing OCG state.
 * This slice contains reducers for manipulating OCG data, including adding, updating,
 * removing sections and alternatives, setting total points, and handling loading/error states.
 */
const ocgSlice = createSlice({
  name: 'ocg',
  initialState,
  reducers: {
    /**
     * Clears the currently active OCG
     */
    clearCurrentOCG: (state) => {
      state.currentOCG = null;
    },
    /**
     * Adds a new section to the current OCG
     * @param state - The current OCG state
     * @param action - Payload containing the OCGSection to add
     */
    addSection: (state, action: PayloadAction<OCGSection>) => {
      if (state.currentOCG) {
        state.currentOCG.sections.push(action.payload);
      }
    },
    /**
     * Updates an existing section in the current OCG
     * @param state - The current OCG state
     * @param action - Payload containing the sectionId and updates to apply
     */
    updateSection: (state, action: PayloadAction<{ sectionId: string; updates: Partial<OCGSection> }>) => {
      if (state.currentOCG) {
        const sectionIndex = state.currentOCG.sections.findIndex(section => section.id === action.payload.sectionId);
        if (sectionIndex !== -1) {
          state.currentOCG.sections[sectionIndex] = {
            ...state.currentOCG.sections[sectionIndex],
            ...action.payload.updates,
          };
        }
      }
    },
    /**
     * Removes a section from the current OCG
     * @param state - The current OCG state
     * @param action - Payload containing the sectionId to remove
     */
    removeSection: (state, action: PayloadAction<string>) => {
      if (state.currentOCG) {
        state.currentOCG.sections = state.currentOCG.sections.filter(section => section.id !== action.payload);
      }
    },
    /**
     * Reorders sections based on array of section IDs
     * @param state - The current OCG state
     * @param action - Payload containing the ordered array of section IDs
     */
    reorderSections: (state, action: PayloadAction<string[]>) => {
      if (state.currentOCG) {
        const orderedSections: OCGSection[] = [];
        action.payload.forEach(sectionId => {
          const section = state.currentOCG?.sections.find(section => section.id === sectionId);
          if (section) {
            orderedSections.push(section);
          }
        });
        state.currentOCG.sections = orderedSections;
      }
    },
    /**
     * Adds an alternative to a section in the current OCG
     * @param state - The current OCG state
     * @param action - Payload containing the sectionId and OCGAlternative to add
     */
    addAlternative: (state, action: PayloadAction<{ sectionId: string; alternative: OCGAlternative }>) => {
      if (state.currentOCG) {
        const sectionIndex = state.currentOCG.sections.findIndex(section => section.id === action.payload.sectionId);
        if (sectionIndex !== -1) {
          state.currentOCG.sections[sectionIndex].alternatives.push(action.payload.alternative);
        }
      }
    },
    /**
     * Updates an alternative in a section
     * @param state - The current OCG state
     * @param action - Payload containing the sectionId, alternativeId, and updates to apply
     */
    updateAlternative: (state, action: PayloadAction<{ sectionId: string; alternativeId: string; updates: Partial<OCGAlternative> }>) => {
      if (state.currentOCG) {
        const sectionIndex = state.currentOCG.sections.findIndex(section => section.id === action.payload.sectionId);
        if (sectionIndex !== -1) {
          const alternativeIndex = state.currentOCG.sections[sectionIndex].alternatives.findIndex(
            alternative => alternative.id === action.payload.alternativeId
          );
          if (alternativeIndex !== -1) {
            state.currentOCG.sections[sectionIndex].alternatives[alternativeIndex] = {
              ...state.currentOCG.sections[sectionIndex].alternatives[alternativeIndex],
              ...action.payload.updates,
            };
          }
        }
      }
    },
    /**
     * Removes an alternative from a section
     * @param state - The current OCG state
     * @param action - Payload containing the sectionId and alternativeId to remove
     */
    removeAlternative: (state, action: PayloadAction<{ sectionId: string; alternativeId: string }>) => {
      if (state.currentOCG) {
        const sectionIndex = state.currentOCG.sections.findIndex(section => section.id === action.payload.sectionId);
        if (sectionIndex !== -1) {
          state.currentOCG.sections[sectionIndex].alternatives = state.currentOCG.sections[sectionIndex].alternatives.filter(
            alternative => alternative.id !== action.payload.alternativeId
          );
        }
      }
    },
    /**
     * Sets the total points for the OCG
     * @param state - The current OCG state
     * @param action - Payload containing the total points value
     */
    setTotalPoints: (state, action: PayloadAction<number>) => {
      if (state.currentOCG) {
        state.currentOCG.totalPoints = action.payload;
      }
    },
    /**
     * Sets the default point budget for firms
     * @param state - The current OCG state
     * @param action - Payload containing the default point budget value
     */
    setDefaultPointBudget: (state, action: PayloadAction<number>) => {
      // Implemented if default point budget is stored in OCG or globally
    },
    /**
     * Records a firm's selection of an alternative
     * @param state - The current OCG state
     * @param action - Payload containing the firmId, sectionId, and alternativeId
     */
    selectAlternative: (state, action: PayloadAction<{ firmId: string; sectionId: string; alternativeId: string }>) => {
      // Implemented if selections are stored in the OCG slice
    },
    /**
     * Clears all error messages
     * @param state - The current OCG state
     */
    clearErrors: (state) => {
      state.error = {
        list: null,
        detail: null,
        create: null,
        update: null,
        delete: null,
        submit: null,
				negotiate: null,
				publish: null,
      };
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(fetchOCGs.pending, (state) => {
        state.loading.list = true;
        state.error.list = null;
      })
      .addCase(fetchOCGs.fulfilled, (state, action) => {
        state.loading.list = false;
        state.ocgs = action.payload;
      })
      .addCase(fetchOCGs.rejected, (state, action) => {
        state.loading.list = false;
        state.error.list = action.error.message || 'Failed to fetch OCGs';
      })
      .addCase(fetchOCGById.pending, (state) => {
        state.loading.detail = true;
        state.error.detail = null;
      })
      .addCase(fetchOCGById.fulfilled, (state, action) => {
        state.loading.detail = false;
        state.currentOCG = action.payload;
      })
      .addCase(fetchOCGById.rejected, (state, action) => {
        state.loading.detail = false;
        state.error.detail = action.error.message || 'Failed to fetch OCG by ID';
      })
      .addCase(createOCG.pending, (state) => {
        state.loading.create = true;
        state.error.create = null;
      })
      .addCase(createOCG.fulfilled, (state, action) => {
        state.loading.create = false;
        state.ocgs.push(action.payload);
        state.currentOCG = action.payload;
      })
      .addCase(createOCG.rejected, (state, action) => {
        state.loading.create = false;
        state.error.create = action.error.message || 'Failed to create OCG';
      })
      .addCase(updateOCG.pending, (state) => {
        state.loading.update = true;
        state.error.update = null;
      })
      .addCase(updateOCG.fulfilled, (state, action) => {
        state.loading.update = false;
        const index = state.ocgs.findIndex(ocg => ocg.id === action.payload.id);
        if (index !== -1) {
          state.ocgs[index] = action.payload;
        }
        state.currentOCG = action.payload;
      })
      .addCase(updateOCG.rejected, (state, action) => {
        state.loading.update = false;
        state.error.update = action.error.message || 'Failed to update OCG';
      })
      .addCase(deleteOCG.pending, (state) => {
        state.loading.delete = true;
        state.error.delete = null;
      })
      .addCase(deleteOCG.fulfilled, (state, action) => {
        state.loading.delete = false;
        state.ocgs = state.ocgs.filter(ocg => ocg.id !== action.payload);
        state.currentOCG = null;
      })
      .addCase(deleteOCG.rejected, (state, action) => {
        state.loading.delete = false;
        state.error.delete = action.error.message || 'Failed to delete OCG';
      })
      .addCase(submitOCGForNegotiation.pending, (state) => {
        state.loading.submit = true;
        state.error.submit = null;
      })
      .addCase(submitOCGForNegotiation.fulfilled, (state, action) => {
        state.loading.submit = false;
        state.currentOCG = action.payload;
      })
      .addCase(submitOCGForNegotiation.rejected, (state, action) => {
        state.loading.submit = false;
        state.error.submit = action.error.message || 'Failed to submit OCG for negotiation';
      })
			.addCase(negotiateOCG.pending, (state) => {
        state.loading.negotiate = true;
        state.error.negotiate = null;
      })
      .addCase(negotiateOCG.fulfilled, (state, action) => {
        state.loading.negotiate = false;
        state.currentOCG = action.payload;
      })
      .addCase(negotiateOCG.rejected, (state, action) => {
        state.loading.negotiate = false;
        state.error.negotiate = action.error.message || 'Failed to negotiate OCG';
      })
			.addCase(publishOCG.pending, (state) => {
        state.loading.publish = true;
        state.error.publish = null;
      })
      .addCase(publishOCG.fulfilled, (state, action) => {
        state.loading.publish = false;
        state.currentOCG = action.payload;
      })
      .addCase(publishOCG.rejected, (state, action) => {
        state.loading.publish = false;
        state.error.publish = action.error.message || 'Failed to publish OCG';
      });
  },
});

// Extract the actions from the slice
export const {
  clearCurrentOCG,
  addSection,
  updateSection,
  removeSection,
  reorderSections,
  addAlternative,
  updateAlternative,
  removeAlternative,
  setTotalPoints,
  setDefaultPointBudget,
  selectAlternative,
  clearErrors,
} = ocgSlice.actions;

/**
 * Selector to get all OCGs from state
 * @param state - The root state
 * @returns Array of OCG objects
 */
export const selectOCGs = (state: RootState): OCG[] => state.ocg.ocgs;

/**
 * Selector to get the currently active OCG
 * @param state - The root state
 * @returns Current OCG object or null
 */
export const selectCurrentOCG = (state: RootState): OCG | null => state.ocg.currentOCG;

/**
 * Selector to get loading states for OCG operations
 * @param state - The root state
 * @returns Object containing loading flags for different operations
 */
export const selectOCGLoading = (state: RootState): object => state.ocg.loading;

/**
 * Selector to get error states for OCG operations
 * @param state - The root state
 * @returns Object containing error messages for different operations
 */
export const selectOCGErrors = (state: RootState): object => state.ocg.error;

/**
 * Factory selector to get a specific OCG by ID
 * @param id - The ID of the OCG to retrieve
 * @returns Function that accepts state and returns an OCG
 */
export const selectOCGById = (id: string) => (state: RootState): OCG | undefined =>
  state.ocg.ocgs.find(ocg => ocg.id === id);

/**
 * Factory selector to calculate total points used by a firm
 * @param firmId - The ID of the firm
 * @returns Function that accepts state and returns a number
 */
export const selectTotalPointsUsed = (firmId: string) => (state: RootState): number => {
  const currentOCG = state.ocg.currentOCG;
  if (!currentOCG || !currentOCG.firmSelections) {
    return 0;
  }

  let totalPoints = 0;
  for (const sectionId in currentOCG.firmSelections) {
    if (currentOCG.firmSelections.hasOwnProperty(sectionId)) {
      const selection = currentOCG.firmSelections[sectionId];
      if (selection.firmId === firmId) {
        totalPoints += selection.pointsUsed;
      }
    }
  }
  return totalPoints;
};

/**
 * Factory selector to calculate remaining points for a firm
 * @param firmId - The ID of the firm
 * @returns Function that accepts state and returns a number
 */
export const selectPointsRemaining = (firmId: string) => (state: RootState): number => {
  const currentOCG = state.ocg.currentOCG;
  if (!currentOCG) {
    return 0;
  }

  const totalPoints = currentOCG.totalPoints || 0;
  const pointsUsed = selectTotalPointsUsed(firmId)(state);
  return totalPoints - pointsUsed;
};

// Export the reducer
export default ocgSlice.reducer;