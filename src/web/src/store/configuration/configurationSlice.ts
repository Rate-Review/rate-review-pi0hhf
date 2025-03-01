import { createSlice, PayloadAction } from '@reduxjs/toolkit'; //  ^1.9.5
import { RootState } from '../index';
import { RateRule } from '../../types/organization';
import { AIConfiguration } from '../../types/ai';
import { IntegrationConfig } from '../../types/integration';
import { NotificationSettings } from '../../types/user';

/**
 * Interface defining the structure of the configuration state
 */
interface ConfigurationState {
  rateRules: RateRule[];
  aiConfiguration: AIConfiguration | null;
  integrationSettings: IntegrationConfig[];
  approvalWorkflow: object | null;
  notificationPreferences: NotificationSettings | null;
}

/**
 * Initial state for the configuration slice
 */
const initialState: ConfigurationState = {
  rateRules: [],
  aiConfiguration: null,
  integrationSettings: [],
  approvalWorkflow: null,
  notificationPreferences: null,
};

/**
 * Creates the Redux slice for configuration management
 */
const configurationSlice = createSlice({
  name: 'configuration',
  initialState,
  reducers: {
    /**
     * Reducer to set rate rules in the state
     * @param state - The current state
     * @param action - Payload action containing the rate rules to set
     */
    setRateRules: (state, action: PayloadAction<RateRule[]>) => {
      state.rateRules = action.payload;
    },
    /**
     * Reducer to set AI configuration in the state
     * @param state - The current state
     * @param action - Payload action containing the AI configuration to set
     */
    setAIConfiguration: (state, action: PayloadAction<AIConfiguration | null>) => {
      state.aiConfiguration = action.payload;
    },
    /**
     * Reducer to set integration settings in the state
     * @param state - The current state
     * @param action - Payload action containing the integration settings to set
     */
    setIntegrationSettings: (state, action: PayloadAction<IntegrationConfig[]>) => {
      state.integrationSettings = action.payload;
    },
    /**
     * Reducer to set approval workflow configuration in the state
     * @param state - The current state
     * @param action - Payload action containing the approval workflow configuration to set
     */
    setApprovalWorkflow: (state, action: PayloadAction<object | null>) => {
      state.approvalWorkflow = action.payload;
    },
    /**
     * Reducer to set notification preferences in the state
     * @param state - The current state
     * @param action - Payload action containing the notification preferences to set
     */
    setNotificationPreferences: (state, action: PayloadAction<NotificationSettings | null>) => {
      state.notificationPreferences = action.payload;
    },
    /**
     * Reducer to reset the configuration state to its initial values
     * @param state - The current state
     */
    resetConfiguration: (state) => {
      state.rateRules = [];
      state.aiConfiguration = null;
      state.integrationSettings = [];
      state.approvalWorkflow = null;
      state.notificationPreferences = null;
    },
  },
  extraReducers: (builder) => {
    // Add extra reducers here for handling async actions if needed
  },
});

// Export the reducer from the slice
export default configurationSlice.reducer;

// Export the actions from the slice
export const configurationSliceActions = configurationSlice.actions;

// Export individual action creators for use in components
export const {
  setRateRules,
  setAIConfiguration,
  setIntegrationSettings,
  setApprovalWorkflow,
  setNotificationPreferences,
  resetConfiguration,
} = configurationSlice.actions;

/**
 * Selector to get rate rules from the state
 * @param state - The root state
 * @returns The rate rules configuration
 */
export const selectRateRules = (state: RootState) => state.configuration.rateRules;

/**
 * Selector to get AI configuration from the state
 * @param state - The root state
 * @returns The AI configuration settings
 */
export const selectAIConfiguration = (state: RootState) => state.configuration.aiConfiguration;

/**
 * Selector to get integration settings from the state
 * @param state - The root state
 * @returns The integration settings
 */
export const selectIntegrationSettings = (state: RootState) => state.configuration.integrationSettings;

/**
 * Selector to get approval workflow configuration from the state
 * @param state - The root state
 * @returns The approval workflow configuration
 */
export const selectApprovalWorkflow = (state: RootState) => state.configuration.approvalWorkflow;

/**
 * Selector to get notification preferences from the state
 * @param state - The root state
 * @returns The notification preferences
 */
export const selectNotificationPreferences = (state: RootState) => state.configuration.notificationPreferences;