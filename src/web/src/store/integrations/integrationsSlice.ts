import { createSlice, PayloadAction } from '@reduxjs/toolkit';
import { 
  IntegrationType, 
  IntegrationConfig, 
  FieldMappingSet, 
  SyncJob, 
  IntegrationSetupState 
} from '../../types/integration';

/**
 * State shape for integrations slice of Redux store
 */
interface IntegrationsState {
  /** List of all configured integrations */
  integrations: IntegrationConfig[];
  /** Currently selected integration for viewing/editing */
  currentIntegration: IntegrationConfig | null;
  /** Loading state for integration operations */
  loading: boolean;
  /** Error message from last failed operation */
  error: string | null;
  /** State for multi-step integration setup process */
  setupState: IntegrationSetupState | null;
  /** List of data synchronization jobs */
  syncJobs: SyncJob[];
}

// Initial state
const initialState: IntegrationsState = {
  integrations: [],
  currentIntegration: null,
  loading: false,
  error: null,
  setupState: null,
  syncJobs: []
};

/**
 * Redux slice for managing integration state in the Justice Bid Rate Negotiation System.
 * Handles state management for external system integrations including eBilling systems,
 * law firm billing systems, UniCourt, and file import/export functionality.
 */
const integrationsSlice = createSlice({
  name: 'integrations',
  initialState,
  reducers: {
    // Integration list management
    setIntegrations(state, action: PayloadAction<IntegrationConfig[]>) {
      state.integrations = action.payload;
    },
    setCurrentIntegration(state, action: PayloadAction<IntegrationConfig | null>) {
      state.currentIntegration = action.payload;
    },
    setIntegrationLoading(state, action: PayloadAction<boolean>) {
      state.loading = action.payload;
    },
    setIntegrationError(state, action: PayloadAction<string | null>) {
      state.error = action.payload;
    },
    addIntegration(state, action: PayloadAction<IntegrationConfig>) {
      state.integrations.push(action.payload);
    },
    updateIntegrationInList(state, action: PayloadAction<IntegrationConfig>) {
      const index = state.integrations.findIndex(i => i.id === action.payload.id);
      if (index !== -1) {
        state.integrations[index] = action.payload;
      }
    },
    removeIntegration(state, action: PayloadAction<string>) {
      state.integrations = state.integrations.filter(i => i.id !== action.payload);
    },

    // Field mapping management
    setFieldMappings(
      state, 
      action: PayloadAction<{ 
        integrationId: string; 
        mappings: FieldMappingSet[];
      }>
    ) {
      const integration = state.integrations.find(i => i.id === action.payload.integrationId);
      if (integration) {
        // For TypeScript, we need to ensure the integration has a mappings property
        // This would be added by the API or other initialization code
        (integration as any).mappings = action.payload.mappings;
      }
    },
    addFieldMapping(
      state,
      action: PayloadAction<{
        integrationId: string;
        mappingSetId: string;
        mapping: { sourceField: string; targetField: string; required: boolean; description?: string }
      }>
    ) {
      const integration = state.integrations.find(i => i.id === action.payload.integrationId);
      if (integration) {
        // Find the mapping set and add the new mapping
        const mappings = (integration as any).mappings || [];
        const mappingSetIndex = mappings.findIndex((ms: FieldMappingSet) => ms.id === action.payload.mappingSetId);
        
        if (mappingSetIndex !== -1) {
          const newMapping = {
            id: Date.now().toString(), // Use timestamp as a simple ID
            sourceField: action.payload.mapping.sourceField,
            targetField: action.payload.mapping.targetField,
            transformFunction: null,
            required: action.payload.mapping.required,
            description: action.payload.mapping.description || null
          };
          
          mappings[mappingSetIndex].mappings.push(newMapping);
        }
      }
    },
    updateFieldMapping(
      state,
      action: PayloadAction<{
        integrationId: string;
        mappingSetId: string;
        mappingId: string;
        updates: Partial<{ sourceField: string; targetField: string; required: boolean; description: string }>
      }>
    ) {
      const integration = state.integrations.find(i => i.id === action.payload.integrationId);
      if (integration) {
        const mappings = (integration as any).mappings || [];
        const mappingSetIndex = mappings.findIndex((ms: FieldMappingSet) => ms.id === action.payload.mappingSetId);
        
        if (mappingSetIndex !== -1) {
          const mappingSet = mappings[mappingSetIndex];
          const mappingIndex = mappingSet.mappings.findIndex(m => m.id === action.payload.mappingId);
          
          if (mappingIndex !== -1) {
            mappingSet.mappings[mappingIndex] = {
              ...mappingSet.mappings[mappingIndex],
              ...action.payload.updates
            };
          }
        }
      }
    },
    removeFieldMapping(
      state,
      action: PayloadAction<{
        integrationId: string;
        mappingSetId: string;
        mappingId: string;
      }>
    ) {
      const integration = state.integrations.find(i => i.id === action.payload.integrationId);
      if (integration) {
        const mappings = (integration as any).mappings || [];
        const mappingSetIndex = mappings.findIndex((ms: FieldMappingSet) => ms.id === action.payload.mappingSetId);
        
        if (mappingSetIndex !== -1) {
          const mappingSet = mappings[mappingSetIndex];
          mappingSet.mappings = mappingSet.mappings.filter(m => m.id !== action.payload.mappingId);
        }
      }
    },

    // Setup state management
    setSetupState(state, action: PayloadAction<IntegrationSetupState | null>) {
      state.setupState = action.payload;
    },
    updateSetupState(state, action: PayloadAction<Partial<IntegrationSetupState>>) {
      if (state.setupState) {
        state.setupState = {
          ...state.setupState,
          ...action.payload
        };
      }
    },
    clearSetupState(state) {
      state.setupState = null;
    },

    // Sync job management
    setSyncJobs(state, action: PayloadAction<SyncJob[]>) {
      state.syncJobs = action.payload;
    },
    addSyncJob(state, action: PayloadAction<SyncJob>) {
      state.syncJobs.push(action.payload);
    },
    updateSyncJob(state, action: PayloadAction<SyncJob>) {
      const index = state.syncJobs.findIndex(job => job.id === action.payload.id);
      if (index !== -1) {
        state.syncJobs[index] = action.payload;
      }
    }
  }
});

// Extract the action creators
export const actions = integrationsSlice.actions;

// Export the reducer as the default export
export default integrationsSlice.reducer;

// Selectors
export const selectors = {
  /**
   * Selects the entire integrations state slice
   */
  selectIntegrationsState: (state: { integrations: IntegrationsState }) => state.integrations,
  
  /**
   * Selects the list of all integrations
   */
  selectIntegrations: (state: { integrations: IntegrationsState }) => state.integrations.integrations,
  
  /**
   * Selects the currently selected integration
   */
  selectCurrentIntegration: (state: { integrations: IntegrationsState }) => state.integrations.currentIntegration,
  
  /**
   * Selects an integration by its ID
   */
  selectIntegrationById: (state: { integrations: IntegrationsState }, integrationId: string) => 
    state.integrations.integrations.find(i => i.id === integrationId),
  
  /**
   * Selects integrations by their type
   */
  selectIntegrationsByType: (state: { integrations: IntegrationsState }, type: IntegrationType) =>
    state.integrations.integrations.filter(i => i.type === type),
  
  /**
   * Selects the loading state for integration operations
   */
  selectIntegrationLoading: (state: { integrations: IntegrationsState }) => state.integrations.loading,
  
  /**
   * Selects the error message for failed operations
   */
  selectIntegrationError: (state: { integrations: IntegrationsState }) => state.integrations.error,
  
  /**
   * Selects the integration setup state
   */
  selectSetupState: (state: { integrations: IntegrationsState }) => state.integrations.setupState,
  
  /**
   * Selects the list of synchronization jobs
   */
  selectSyncJobs: (state: { integrations: IntegrationsState }) => state.integrations.syncJobs
};