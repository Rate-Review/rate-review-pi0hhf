import { createAsyncThunk } from '@reduxjs/toolkit';
import { actions } from './integrationsSlice';
import {
  IntegrationType,
  IntegrationConfig,
  FieldMappingSet,
  TestConnectionRequest,
  ConnectionTestResult,
  ImportDataRequest,
  ExportDataRequest
} from '../../types/integration';
import {
  getIntegrations,
  getIntegrationById,
  createIntegration,
  updateIntegration,
  deleteIntegration,
  testEBillingConnection,
  testLawFirmConnection,
  testUniCourtConnection,
  getFieldMappingSets,
  createFieldMappingSet,
  updateFieldMappingSet,
  importDataFromEBilling,
  importDataFromLawFirm,
  exportDataToEBilling,
  exportDataToLawFirm,
  getSyncJobs,
  uploadFile,
  getFileTemplates,
  downloadFileTemplate
} from '../../services/integrations';

/**
 * Fetches all configured integrations for the current organization
 * 
 * @returns A promise that resolves to an array of IntegrationConfig objects
 */
export const fetchIntegrations = createAsyncThunk(
  'integrations/fetchAll',
  async (_, { dispatch }) => {
    try {
      dispatch(actions.setIntegrationLoading(true));
      const integrations = await getIntegrations();
      dispatch(actions.setIntegrations(integrations));
      return integrations;
    } catch (error) {
      dispatch(actions.setIntegrationError(error.message || 'Failed to fetch integrations'));
      throw error;
    } finally {
      dispatch(actions.setIntegrationLoading(false));
    }
  }
);

/**
 * Fetches a specific integration by ID
 * 
 * @param integrationId - The ID of the integration to fetch
 * @returns A promise that resolves to the requested IntegrationConfig
 */
export const fetchIntegrationById = createAsyncThunk(
  'integrations/fetchById',
  async (integrationId: string, { dispatch }) => {
    try {
      dispatch(actions.setIntegrationLoading(true));
      const integration = await getIntegrationById(integrationId);
      dispatch(actions.setCurrentIntegration(integration));
      return integration;
    } catch (error) {
      dispatch(actions.setIntegrationError(error.message || 'Failed to fetch integration'));
      throw error;
    } finally {
      dispatch(actions.setIntegrationLoading(false));
    }
  }
);

/**
 * Creates a new integration configuration
 * 
 * @param integrationConfig - The integration configuration to create
 * @returns A promise that resolves to the created IntegrationConfig
 */
export const createIntegrationConfig = createAsyncThunk(
  'integrations/create',
  async (integrationConfig: Partial<IntegrationConfig>, { dispatch }) => {
    try {
      dispatch(actions.setIntegrationLoading(true));
      const createdIntegration = await createIntegration(integrationConfig);
      dispatch(actions.addIntegration(createdIntegration));
      return createdIntegration;
    } catch (error) {
      dispatch(actions.setIntegrationError(error.message || 'Failed to create integration'));
      throw error;
    } finally {
      dispatch(actions.setIntegrationLoading(false));
    }
  }
);

/**
 * Updates an existing integration configuration
 * 
 * @param integrationId - The ID of the integration to update
 * @param updatedConfig - The updated integration configuration
 * @returns A promise that resolves to the updated IntegrationConfig
 */
export const updateIntegrationConfig = createAsyncThunk(
  'integrations/update',
  async (
    { integrationId, updatedConfig }: { integrationId: string; updatedConfig: Partial<IntegrationConfig> },
    { dispatch }
  ) => {
    try {
      dispatch(actions.setIntegrationLoading(true));
      const updatedIntegration = await updateIntegration(integrationId, updatedConfig);
      dispatch(actions.updateIntegrationInList(updatedIntegration));
      return updatedIntegration;
    } catch (error) {
      dispatch(actions.setIntegrationError(error.message || 'Failed to update integration'));
      throw error;
    } finally {
      dispatch(actions.setIntegrationLoading(false));
    }
  }
);

/**
 * Deletes an integration configuration
 * 
 * @param integrationId - The ID of the integration to delete
 * @returns A promise that resolves when the integration is deleted
 */
export const deleteIntegrationConfig = createAsyncThunk(
  'integrations/delete',
  async (integrationId: string, { dispatch }) => {
    try {
      dispatch(actions.setIntegrationLoading(true));
      await deleteIntegration(integrationId);
      dispatch(actions.removeIntegration(integrationId));
    } catch (error) {
      dispatch(actions.setIntegrationError(error.message || 'Failed to delete integration'));
      throw error;
    } finally {
      dispatch(actions.setIntegrationLoading(false));
    }
  }
);

/**
 * Tests connection to an external system integration
 * 
 * @param testRequest - The connection test request with integration details
 * @returns A promise that resolves to the connection test result
 */
export const testConnection = createAsyncThunk(
  'integrations/testConnection',
  async (testRequest: TestConnectionRequest, { dispatch }) => {
    try {
      dispatch(actions.setIntegrationLoading(true));
      
      let result: ConnectionTestResult;
      
      // Select the appropriate test function based on integration type
      switch (testRequest.type) {
        case IntegrationType.EBILLING:
          result = await testEBillingConnection(testRequest);
          break;
        case IntegrationType.LAWFIRM:
          result = await testLawFirmConnection(testRequest);
          break;
        case IntegrationType.UNICOURT:
          result = await testUniCourtConnection(testRequest);
          break;
        default:
          throw new Error(`Unsupported integration type: ${testRequest.type}`);
      }
      
      return result;
    } catch (error) {
      dispatch(actions.setIntegrationError(error.message || 'Connection test failed'));
      throw error;
    } finally {
      dispatch(actions.setIntegrationLoading(false));
    }
  }
);

/**
 * Fetches field mappings for an integration
 * 
 * @param integrationId - The ID of the integration to fetch mappings for
 * @returns A promise that resolves to an array of field mapping sets
 */
export const fetchFieldMappings = createAsyncThunk(
  'integrations/fetchFieldMappings',
  async (integrationId: string, { dispatch }) => {
    try {
      dispatch(actions.setIntegrationLoading(true));
      const mappings = await getFieldMappingSets(integrationId);
      dispatch(actions.setFieldMappings({ integrationId, mappings }));
      return mappings;
    } catch (error) {
      dispatch(actions.setIntegrationError(error.message || 'Failed to fetch field mappings'));
      throw error;
    } finally {
      dispatch(actions.setIntegrationLoading(false));
    }
  }
);

/**
 * Creates a new field mapping configuration for an integration
 * 
 * @param integrationId - The ID of the integration
 * @param mappingSet - The field mapping set to create
 * @returns A promise that resolves to the created field mapping set
 */
export const createFieldMappingConfiguration = createAsyncThunk(
  'integrations/createFieldMapping',
  async (
    { integrationId, mappingSet }: { integrationId: string; mappingSet: FieldMappingSet },
    { dispatch }
  ) => {
    try {
      dispatch(actions.setIntegrationLoading(true));
      const createdMapping = await createFieldMappingSet(integrationId, mappingSet);
      dispatch(actions.addFieldMapping({
        integrationId,
        mappingSetId: createdMapping.id,
        mapping: createdMapping.mappings[0] || { sourceField: '', targetField: '', required: false }
      }));
      return createdMapping;
    } catch (error) {
      dispatch(actions.setIntegrationError(error.message || 'Failed to create field mapping'));
      throw error;
    } finally {
      dispatch(actions.setIntegrationLoading(false));
    }
  }
);

/**
 * Updates an existing field mapping configuration
 * 
 * @param integrationId - The ID of the integration
 * @param mappingSetId - The ID of the mapping set to update
 * @param updatedMappingSet - The updated field mapping set
 * @returns A promise that resolves to the updated field mapping set
 */
export const updateFieldMappingConfiguration = createAsyncThunk(
  'integrations/updateFieldMapping',
  async (
    {
      integrationId,
      mappingSetId,
      updatedMappingSet
    }: {
      integrationId: string;
      mappingSetId: string;
      updatedMappingSet: FieldMappingSet;
    },
    { dispatch }
  ) => {
    try {
      dispatch(actions.setIntegrationLoading(true));
      const updatedMapping = await updateFieldMappingSet(
        integrationId,
        mappingSetId,
        updatedMappingSet
      );
      
      dispatch(actions.updateFieldMapping({
        integrationId,
        mappingSetId,
        mappingId: updatedMapping.mappings[0]?.id || '',
        updates: updatedMapping.mappings[0] || {}
      }));
      
      return updatedMapping;
    } catch (error) {
      dispatch(actions.setIntegrationError(error.message || 'Failed to update field mapping'));
      throw error;
    } finally {
      dispatch(actions.setIntegrationLoading(false));
    }
  }
);

/**
 * Fetches synchronization jobs for an integration
 * 
 * @param integrationId - The ID of the integration to fetch jobs for
 * @returns A promise that resolves to an array of sync jobs
 */
export const fetchSyncJobs = createAsyncThunk(
  'integrations/fetchSyncJobs',
  async (integrationId: string, { dispatch }) => {
    try {
      dispatch(actions.setIntegrationLoading(true));
      const syncJobs = await getSyncJobs(integrationId);
      dispatch(actions.setSyncJobs(syncJobs));
      return syncJobs;
    } catch (error) {
      dispatch(actions.setIntegrationError(error.message || 'Failed to fetch synchronization jobs'));
      throw error;
    } finally {
      dispatch(actions.setIntegrationLoading(false));
    }
  }
);

/**
 * Imports data from an external system
 * 
 * @param integrationId - The ID of the integration to import from
 * @param importRequest - The import request configuration
 * @returns A promise that resolves to the created import job
 */
export const importData = createAsyncThunk(
  'integrations/importData',
  async (
    { integrationId, importRequest }: { integrationId: string; importRequest: ImportDataRequest },
    { dispatch, getState }
  ) => {
    try {
      dispatch(actions.setIntegrationLoading(true));
      
      // Get integration to determine type
      const integration = await getIntegrationById(integrationId);
      let importJob;
      
      // Call appropriate import function based on integration type
      switch (integration.type) {
        case IntegrationType.EBILLING:
          importJob = await importDataFromEBilling(integrationId, importRequest);
          break;
        case IntegrationType.LAWFIRM:
          importJob = await importDataFromLawFirm(integrationId, importRequest);
          break;
        default:
          throw new Error(`Import not supported for integration type: ${integration.type}`);
      }
      
      dispatch(actions.addSyncJob(importJob));
      return importJob;
    } catch (error) {
      dispatch(actions.setIntegrationError(error.message || 'Data import failed'));
      throw error;
    } finally {
      dispatch(actions.setIntegrationLoading(false));
    }
  }
);

/**
 * Exports data to an external system
 * 
 * @param integrationId - The ID of the integration to export to
 * @param exportRequest - The export request configuration
 * @returns A promise that resolves to the created export job
 */
export const exportData = createAsyncThunk(
  'integrations/exportData',
  async (
    { integrationId, exportRequest }: { integrationId: string; exportRequest: ExportDataRequest },
    { dispatch }
  ) => {
    try {
      dispatch(actions.setIntegrationLoading(true));
      
      // Get integration to determine type
      const integration = await getIntegrationById(integrationId);
      let exportJob;
      
      // Call appropriate export function based on integration type
      switch (integration.type) {
        case IntegrationType.EBILLING:
          exportJob = await exportDataToEBilling(integrationId, exportRequest);
          break;
        case IntegrationType.LAWFIRM:
          exportJob = await exportDataToLawFirm(integrationId, exportRequest);
          break;
        default:
          throw new Error(`Export not supported for integration type: ${integration.type}`);
      }
      
      dispatch(actions.addSyncJob(exportJob));
      return exportJob;
    } catch (error) {
      dispatch(actions.setIntegrationError(error.message || 'Data export failed'));
      throw error;
    } finally {
      dispatch(actions.setIntegrationLoading(false));
    }
  }
);

/**
 * Uploads a file for data import
 * 
 * @param file - The file to upload
 * @param dataType - The type of data in the file (rates, attorneys, etc.)
 * @param options - Additional options for the import
 * @returns A promise that resolves to the upload result
 */
export const uploadFileForImport = createAsyncThunk(
  'integrations/uploadFile',
  async (
    { file, dataType, options = {} }: { file: File; dataType: string; options?: object },
    { dispatch }
  ) => {
    try {
      dispatch(actions.setIntegrationLoading(true));
      const result = await uploadFile(file, dataType, options);
      return result;
    } catch (error) {
      dispatch(actions.setIntegrationError(error.message || 'File upload failed'));
      throw error;
    } finally {
      dispatch(actions.setIntegrationLoading(false));
    }
  }
);

/**
 * Fetches available file templates for import/export
 * 
 * @param dataType - Optional data type to filter templates
 * @returns A promise that resolves to an array of file templates
 */
export const fetchFileTemplates = createAsyncThunk(
  'integrations/fetchFileTemplates',
  async (dataType: string, { dispatch }) => {
    try {
      dispatch(actions.setIntegrationLoading(true));
      const templates = await getFileTemplates(dataType);
      return templates;
    } catch (error) {
      dispatch(actions.setIntegrationError(error.message || 'Failed to fetch file templates'));
      throw error;
    } finally {
      dispatch(actions.setIntegrationLoading(false));
    }
  }
);

/**
 * Downloads a file template
 * 
 * @param templateId - The ID of the template to download
 * @returns A promise that resolves to the template file as a Blob
 */
export const downloadTemplate = createAsyncThunk(
  'integrations/downloadTemplate',
  async (templateId: string, { dispatch }) => {
    try {
      dispatch(actions.setIntegrationLoading(true));
      const templateBlob = await downloadFileTemplate(templateId);
      return templateBlob;
    } catch (error) {
      dispatch(actions.setIntegrationError(error.message || 'Failed to download template'));
      throw error;
    } finally {
      dispatch(actions.setIntegrationLoading(false));
    }
  }
);