/**
 * Redux thunks for handling organization-related asynchronous operations including fetching, creating, updating, and deleting organizations as well as managing relationships between client and law firm organizations.
 * @packageDocumentation
 */

import { createAsyncThunk } from '@reduxjs/toolkit'; //  ^1.9.5
import {
  Organization,
  OrganizationRelationship,
  OrganizationSettings,
  CreateOrganizationRequest,
  UpdateOrganizationRequest
} from '../../types/organization';
import { RootState } from '../index';
import { organizationsService } from '../../services/organizations'; // Service for handling organization-related API calls

/**
 * Fetches a list of client organizations.
 * @returns A promise that resolves to an array of client organizations
 */
export const fetchClientOrganizations = createAsyncThunk<
  Organization[],
  void,
  { rejectValue: { message: string } }
>(
  'organizations/fetchClientOrganizations',
  async (_, thunkApi) => {
    try {
      const organizations = await organizationsService.getClientOrganizations();
      return organizations;
    } catch (error: any) {
      return thunkApi.rejectWithValue({ message: error.message });
    }
  }
);

/**
 * Fetches a list of law firm organizations.
 * @returns A promise that resolves to an array of law firm organizations
 */
export const fetchLawFirmOrganizations = createAsyncThunk<
  Organization[],
  void,
  { rejectValue: { message: string } }
>(
  'organizations/fetchLawFirmOrganizations',
  async (_, thunkApi) => {
    try {
      const organizations = await organizationsService.getLawFirmOrganizations();
      return organizations;
    } catch (error: any) {
      return thunkApi.rejectWithValue({ message: error.message });
    }
  }
);

/**
 * Fetches a specific organization by its ID.
 * @param organizationId - The ID of the organization to fetch
 * @returns A promise that resolves to the requested organization
 */
export const fetchOrganizationById = createAsyncThunk<
  Organization,
  string,
  { rejectValue: { message: string } }
>(
  'organizations/fetchOrganizationById',
  async (organizationId, thunkApi) => {
    try {
      const organization = await organizationsService.getOrganizationById(organizationId);
      return organization;
    } catch (error: any) {
      return thunkApi.rejectWithValue({ message: error.message });
    }
  }
);

/**
 * Creates a new organization.
 * @param organizationData - The data for the new organization
 * @returns A promise that resolves to the newly created organization
 */
export const createOrganization = createAsyncThunk<
  Organization,
  CreateOrganizationRequest,
  { rejectValue: { message: string } }
>(
  'organizations/createOrganization',
  async (organizationData, thunkApi) => {
    try {
      const organization = await organizationsService.createOrganization(organizationData);
      return organization;
    } catch (error: any) {
      return thunkApi.rejectWithValue({ message: error.message });
    }
  }
);

/**
 * Updates an existing organization.
 * @param organizationData - The updated data for the organization
 * @returns A promise that resolves to the updated organization
 */
export const updateOrganization = createAsyncThunk<
  Organization,
  UpdateOrganizationRequest,
  { rejectValue: { message: string } }
>(
  'organizations/updateOrganization',
  async (organizationData, thunkApi) => {
    try {
      const organization = await organizationsService.updateOrganization(organizationData);
      return organization;
    } catch (error: any) {
      return thunkApi.rejectWithValue({ message: error.message });
    }
  }
);

/**
 * Deletes an organization by its ID.
 * @param organizationId - The ID of the organization to delete
 * @returns A promise that resolves when the organization is deleted
 */
export const deleteOrganization = createAsyncThunk<
  void,
  string,
  { rejectValue: { message: string } }
>(
  'organizations/deleteOrganization',
  async (organizationId, thunkApi) => {
    try {
      await organizationsService.deleteOrganization(organizationId);
      return;
    } catch (error: any) {
      return thunkApi.rejectWithValue({ message: error.message });
    }
  }
);

/**
 * Fetches relationships for a specific organization.
 * @param organizationId - The ID of the organization to fetch relationships for
 * @returns A promise that resolves to an array of organization relationships
 */
export const fetchOrganizationRelationships = createAsyncThunk<
  OrganizationRelationship[],
  string,
  { rejectValue: { message: string } }
>(
  'organizations/fetchOrganizationRelationships',
  async (organizationId, thunkApi) => {
    try {
      const relationships = await organizationsService.getOrganizationRelationships(organizationId);
      return relationships;
    } catch (error: any) {
      return thunkApi.rejectWithValue({ message: error.message });
    }
  }
);

/**
 * Creates a new relationship between two organizations.
 * @param relationshipData - The data for the new relationship
 * @returns A promise that resolves to the newly created relationship
 */
export const createOrganizationRelationship = createAsyncThunk<
  OrganizationRelationship,
  object,
  { rejectValue: { message: string } }
>(
  'organizations/createOrganizationRelationship',
  async (relationshipData, thunkApi) => {
    try {
      const relationship = await organizationsService.createOrganizationRelationship(relationshipData);
      return relationship;
    } catch (error: any) {
      return thunkApi.rejectWithValue({ message: error.message });
    }
  }
);

/**
 * Updates an existing relationship between organizations.
 * @param relationshipData - The updated data for the relationship
 * @returns A promise that resolves to the updated relationship
 */
export const updateOrganizationRelationship = createAsyncThunk<
  OrganizationRelationship,
  object,
  { rejectValue: { message: string } }
>(
  'organizations/updateOrganizationRelationship',
  async (relationshipData, thunkApi) => {
    try {
      const relationship = await organizationsService.updateOrganizationRelationship(relationshipData);
      return relationship;
    } catch (error: any) {
      return thunkApi.rejectWithValue({ message: error.message });
    }
  }
);

/**
 * Deletes a relationship between organizations.
 * @param relationshipId - The ID of the relationship to delete
 * @returns A promise that resolves when the relationship is deleted
 */
export const deleteOrganizationRelationship = createAsyncThunk<
  void,
  string,
  { rejectValue: { message: string } }
>(
  'organizations/deleteOrganizationRelationship',
  async (relationshipId, thunkApi) => {
    try {
      await organizationsService.deleteOrganizationRelationship(relationshipId);
      return;
    } catch (error: any) {
      return thunkApi.rejectWithValue({ message: error.message });
    }
  }
);

/**
 * Fetches settings for a specific organization.
 * @param organizationId - The ID of the organization to fetch settings for
 * @returns A promise that resolves to the organization settings
 */
export const fetchOrganizationSettings = createAsyncThunk<
  OrganizationSettings,
  string,
  { rejectValue: { message: string } }
>(
  'organizations/fetchOrganizationSettings',
  async (organizationId, thunkApi) => {
    try {
      const settings = await organizationsService.getOrganizationSettings(organizationId);
      return settings;
    } catch (error: any) {
      return thunkApi.rejectWithValue({ message: error.message });
    }
  }
);

/**
 * Updates settings for a specific organization.
 * @param settingsData - The updated settings data
 * @returns A promise that resolves to the updated organization settings
 */
export const updateOrganizationSettings = createAsyncThunk<
  OrganizationSettings,
  object,
  { rejectValue: { message: string } }
>(
  'organizations/updateOrganizationSettings',
  async (settingsData, thunkApi) => {
    try {
      const organizationId = (thunkApi.getState() as RootState).organizations.currentOrganizationId;
      if (!organizationId) {
        throw new Error('Organization ID is required to update settings.');
      }
      const settings = await organizationsService.updateOrganizationSettings(organizationId, settingsData);
      return settings;
    } catch (error: any) {
      return thunkApi.rejectWithValue({ message: error.message });
    }
  }
);