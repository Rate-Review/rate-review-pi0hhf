/**
 * Redux thunks for configuration-related actions that handle asynchronous operations such as fetching and updating organization settings, rate rules, notification preferences, and other system configurations.
 */

import { createAsyncThunk } from '@reduxjs/toolkit'; //  ^1.9.5
import { RootState } from '../index';
import configurationService from '../../services/configuration';
import { OrganizationSettings } from '../../types/organization';
import { RateRules } from '../../types/rate';
import { NotificationSettings } from '../../types/common';
import { AIConfiguration } from '../../types/ai';

/**
 * Async thunk that fetches the organization settings for the current user's organization
 */
export const fetchOrganizationSettings = createAsyncThunk<OrganizationSettings, void, { rejectValue: { message: string }; state: RootState }>(
  'configuration/fetchOrganizationSettings',
  async (_, thunkAPI) => {
    try {
      // Get organization ID from state
      const organizationId = thunkAPI.getState().auth.user?.organizationId;
      if (!organizationId) {
        return thunkAPI.rejectWithValue({ message: 'Organization ID not found' });
      }

      // Call configurationService.getOrganizationSettings with organization ID
      const settings = await configurationService.getOrganizationSettings(organizationId);

      // Return the organization settings data on success
      return settings;
    } catch (error: any) {
      // Handle errors and reject the promise with error message on failure
      return thunkAPI.rejectWithValue({ message: error.message });
    }
  }
);

/**
 * Async thunk that updates the organization settings for the current user's organization
 */
export const updateOrganizationSettings = createAsyncThunk<OrganizationSettings, OrganizationSettings, { rejectValue: { message: string }; state: RootState }>(
  'configuration/updateOrganizationSettings',
  async (settings, thunkAPI) => {
    try {
      // Get organization ID from state
      const organizationId = thunkAPI.getState().auth.user?.organizationId;
      if (!organizationId) {
        return thunkAPI.rejectWithValue({ message: 'Organization ID not found' });
      }

      // Call configurationService.updateOrganizationSettings with organization ID and settings
      const updatedSettings = await configurationService.updateOrganizationSettings(organizationId, settings);

      // Return the updated organization settings data on success
      return updatedSettings;
    } catch (error: any) {
      // Handle errors and reject the promise with error message on failure
      return thunkAPI.rejectWithValue({ message: error.message });
    }
  }
);

/**
 * Async thunk that fetches the rate rules for the current user's organization
 */
export const fetchRateRules = createAsyncThunk<RateRules, void, { rejectValue: { message: string }; state: RootState }>(
  'configuration/fetchRateRules',
  async (_, thunkAPI) => {
    try {
      // Get organization ID from state
      const organizationId = thunkAPI.getState().auth.user?.organizationId;
      if (!organizationId) {
        return thunkAPI.rejectWithValue({ message: 'Organization ID not found' });
      }

      // Call configurationService.getRateRules with organization ID
      const rateRules = await configurationService.getRateRules(organizationId);

      // Return the rate rules data on success
      return rateRules;
    } catch (error: any) {
      // Handle errors and reject the promise with error message on failure
      return thunkAPI.rejectWithValue({ message: error.message });
    }
  }
);

/**
 * Async thunk that updates the rate rules for the current user's organization
 */
export const updateRateRules = createAsyncThunk<RateRules, RateRules, { rejectValue: { message: string }; state: RootState }>(
  'configuration/updateRateRules',
  async (rules, thunkAPI) => {
    try {
      // Get organization ID from state
      const organizationId = thunkAPI.getState().auth.user?.organizationId;
      if (!organizationId) {
        return thunkAPI.rejectWithValue({ message: 'Organization ID not found' });
      }

      // Call configurationService.updateRateRules with organization ID and rules
      const updatedRules = await configurationService.updateRateRules(organizationId, rules);

      // Return the updated rate rules data on success
      return updatedRules;
    } catch (error: any) {
      // Handle errors and reject the promise with error message on failure
      return thunkAPI.rejectWithValue({ message: error.message });
    }
  }
);

/**
 * Async thunk that fetches the notification settings for the current user
 */
export const fetchNotificationSettings = createAsyncThunk<NotificationSettings, void, { rejectValue: { message: string }; state: RootState }>(
  'configuration/fetchNotificationSettings',
  async (_, thunkAPI) => {
    try {
      // Get user ID from state
      const userId = thunkAPI.getState().auth.user?.id;
      if (!userId) {
        return thunkAPI.rejectWithValue({ message: 'User ID not found' });
      }

      // Call configurationService.getNotificationSettings with user ID
      const notificationSettings = await configurationService.getNotificationSettings('user', userId);

      // Return the notification settings data on success
      return notificationSettings;
    } catch (error: any) {
      // Handle errors and reject the promise with error message on failure
      return thunkAPI.rejectWithValue({ message: error.message });
    }
  }
);

/**
 * Async thunk that updates the notification settings for the current user
 */
export const updateNotificationSettings = createAsyncThunk<NotificationSettings, NotificationSettings, { rejectValue: { message: string }; state: RootState }>(
  'configuration/updateNotificationSettings',
  async (settings, thunkAPI) => {
    try {
      // Get user ID from state
      const userId = thunkAPI.getState().auth.user?.id;
      if (!userId) {
        return thunkAPI.rejectWithValue({ message: 'User ID not found' });
      }

      // Call configurationService.updateNotificationSettings with user ID and settings
      const updatedSettings = await configurationService.updateNotificationSettings('user', userId, settings);

      // Return the updated notification settings data on success
      return updatedSettings;
    } catch (error: any) {
      // Handle errors and reject the promise with error message on failure
      return thunkAPI.rejectWithValue({ message: error.message });
    }
  }
);

/**
 * Async thunk that fetches the AI configuration settings for the organization
 */
export const fetchAIConfiguration = createAsyncThunk<AIConfiguration, void, { rejectValue: { message: string }; state: RootState }>(
  'configuration/fetchAIConfiguration',
  async (_, thunkAPI) => {
    try {
      // Get organization ID from state
      const organizationId = thunkAPI.getState().auth.user?.organizationId;
      if (!organizationId) {
        return thunkAPI.rejectWithValue({ message: 'Organization ID not found' });
      }

      // Call configurationService.getAIConfiguration with organization ID
      const aiConfiguration = await configurationService.getAIConfiguration(organizationId);

      // Return the AI configuration data on success
      return aiConfiguration;
    } catch (error: any) {
      // Handle errors and reject the promise with error message on failure
      return thunkAPI.rejectWithValue({ message: error.message });
    }
  }
);

/**
 * Async thunk that updates the AI configuration settings for the organization
 */
export const updateAIConfiguration = createAsyncThunk<AIConfiguration, AIConfiguration, { rejectValue: { message: string }; state: RootState }>(
  'configuration/updateAIConfiguration',
  async (config, thunkAPI) => {
    try {
      // Get organization ID from state
      const organizationId = thunkAPI.getState().auth.user?.organizationId;
      if (!organizationId) {
        return thunkAPI.rejectWithValue({ message: 'Organization ID not found' });
      }

      // Call configurationService.updateAIConfiguration with organization ID and config
      const updatedAIConfiguration = await configurationService.updateAIConfiguration(organizationId, config);

      // Return the updated AI configuration data on success
      return updatedAIConfiguration;
    } catch (error: any) {
      // Handle errors and reject the promise with error message on failure
      return thunkAPI.rejectWithValue({ message: error.message });
    }
  }
);