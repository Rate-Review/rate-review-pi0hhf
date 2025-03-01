/**
 * Service layer for managing integrations with external systems in the 
 * Justice Bid Rate Negotiation System
 * 
 * Provides functions for configuring, testing, and managing data exchange with
 * eBilling systems, law firm billing systems, UniCourt, and file import/export.
 * 
 * @version 1.0.0
 */

import axiosInstance from '../api/axiosConfig';
import { API_ROUTES, buildUrl, buildUrlWithParams } from '../api/apiRoutes';
import {
  IntegrationType,
  IntegrationConfig,
  EBillingIntegrationConfig,
  LawFirmBillingIntegrationConfig,
  UniCourtIntegrationConfig,
  FileIntegrationConfig,
  TestConnectionRequest,
  ConnectionTestResult,
  FieldMapping,
  FieldMappingSet,
  ImportDataRequest,
  ExportDataRequest,
  SyncJob,
  FileTemplate
} from '../types/integration';

/**
 * Fetches all integrations for the current organization
 * @returns Promise resolving to array of integration configurations
 */
export const getIntegrations = async (): Promise<IntegrationConfig[]> => {
  const response = await axiosInstance.get(API_ROUTES.INTEGRATIONS.BASE);
  return response.data;
};

/**
 * Fetches a specific integration by ID
 * @param id Integration ID to fetch
 * @returns Promise resolving to the integration configuration
 */
export const getIntegrationById = async (id: string): Promise<IntegrationConfig> => {
  const url = buildUrlWithParams(`${API_ROUTES.INTEGRATIONS.BASE}/:id`, { id });
  const response = await axiosInstance.get(url);
  return response.data;
};

/**
 * Creates a new integration configuration
 * @param integrationConfig Partial integration configuration to create
 * @returns Promise resolving to the created integration
 */
export const createIntegration = async (
  integrationConfig: Partial<IntegrationConfig>
): Promise<IntegrationConfig> => {
  let endpoint;
  
  // Determine which endpoint to use based on integration type
  switch (integrationConfig.type) {
    case IntegrationType.EBILLING:
      endpoint = API_ROUTES.INTEGRATIONS.EBILLING.BASE;
      break;
    case IntegrationType.LAWFIRM:
      endpoint = API_ROUTES.INTEGRATIONS.LAWFIRM.BASE;
      break;
    case IntegrationType.UNICOURT:
      endpoint = API_ROUTES.INTEGRATIONS.UNICOURT.BASE;
      break;
    default:
      // Default to base endpoint
      endpoint = API_ROUTES.INTEGRATIONS.BASE;
  }
  
  const response = await axiosInstance.post(endpoint, integrationConfig);
  return response.data;
};

/**
 * Updates an existing integration configuration
 * @param id Integration ID to update
 * @param updatedConfig Updated integration configuration
 * @returns Promise resolving to the updated integration
 */
export const updateIntegration = async (
  id: string,
  updatedConfig: Partial<IntegrationConfig>
): Promise<IntegrationConfig> => {
  const url = buildUrlWithParams(`${API_ROUTES.INTEGRATIONS.BASE}/:id`, { id });
  const response = await axiosInstance.put(url, updatedConfig);
  return response.data;
};

/**
 * Deletes an integration configuration
 * @param id Integration ID to delete
 * @returns Promise resolving when the integration is deleted
 */
export const deleteIntegration = async (id: string): Promise<void> => {
  const url = buildUrlWithParams(`${API_ROUTES.INTEGRATIONS.BASE}/:id`, { id });
  await axiosInstance.delete(url);
};

/**
 * Tests connection to an eBilling system
 * @param request Test connection request payload
 * @returns Promise resolving to connection test result
 */
export const testEBillingConnection = async (
  request: TestConnectionRequest
): Promise<ConnectionTestResult> => {
  const response = await axiosInstance.post(API_ROUTES.INTEGRATIONS.EBILLING.TEST, request);
  return response.data;
};

/**
 * Tests connection to a law firm billing system
 * @param request Test connection request payload
 * @returns Promise resolving to connection test result
 */
export const testLawFirmConnection = async (
  request: TestConnectionRequest
): Promise<ConnectionTestResult> => {
  const response = await axiosInstance.post(API_ROUTES.INTEGRATIONS.LAWFIRM.TEST, request);
  return response.data;
};

/**
 * Tests connection to the UniCourt API
 * @param request Test connection request payload
 * @returns Promise resolving to connection test result
 */
export const testUniCourtConnection = async (
  request: TestConnectionRequest
): Promise<ConnectionTestResult> => {
  const response = await axiosInstance.post(`${API_ROUTES.INTEGRATIONS.UNICOURT.BASE}/test`, request);
  return response.data;
};

/**
 * Fetches field mapping sets for an integration
 * @param integrationId Integration ID to fetch mappings for
 * @returns Promise resolving to array of field mapping sets
 */
export const getFieldMappingSets = async (integrationId: string): Promise<FieldMappingSet[]> => {
  const url = buildUrlWithParams(`${API_ROUTES.INTEGRATIONS.BASE}/:id/mapping`, { id: integrationId });
  const response = await axiosInstance.get(url);
  return response.data;
};

/**
 * Creates a new field mapping set for an integration
 * @param integrationId Integration ID to create mapping for
 * @param mappingSet Field mapping set to create
 * @returns Promise resolving to the created mapping set
 */
export const createFieldMappingSet = async (
  integrationId: string,
  mappingSet: FieldMappingSet
): Promise<FieldMappingSet> => {
  const url = buildUrlWithParams(`${API_ROUTES.INTEGRATIONS.BASE}/:id/mapping`, { id: integrationId });
  const response = await axiosInstance.post(url, mappingSet);
  return response.data;
};

/**
 * Updates an existing field mapping set
 * @param integrationId Integration ID
 * @param mappingSetId Mapping set ID to update
 * @param updatedMappingSet Updated field mapping set
 * @returns Promise resolving to the updated mapping set
 */
export const updateFieldMappingSet = async (
  integrationId: string,
  mappingSetId: string,
  updatedMappingSet: FieldMappingSet
): Promise<FieldMappingSet> => {
  const url = buildUrlWithParams(`${API_ROUTES.INTEGRATIONS.BASE}/:id/mapping/:mappingId`, {
    id: integrationId,
    mappingId: mappingSetId
  });
  const response = await axiosInstance.put(url, updatedMappingSet);
  return response.data;
};

/**
 * Imports data from an eBilling system
 * @param integrationId Integration ID to import from
 * @param request Import data request
 * @returns Promise resolving to the created sync job
 */
export const importDataFromEBilling = async (
  integrationId: string,
  request: ImportDataRequest
): Promise<SyncJob> => {
  const response = await axiosInstance.post(API_ROUTES.INTEGRATIONS.EBILLING.IMPORT, {
    integrationId,
    ...request
  });
  return response.data;
};

/**
 * Imports data from a law firm billing system
 * @param integrationId Integration ID to import from
 * @param request Import data request
 * @returns Promise resolving to the created sync job
 */
export const importDataFromLawFirm = async (
  integrationId: string,
  request: ImportDataRequest
): Promise<SyncJob> => {
  const response = await axiosInstance.post(API_ROUTES.INTEGRATIONS.LAWFIRM.IMPORT, {
    integrationId,
    ...request
  });
  return response.data;
};

/**
 * Exports data to an eBilling system
 * @param integrationId Integration ID to export to
 * @param request Export data request
 * @returns Promise resolving to the created sync job
 */
export const exportDataToEBilling = async (
  integrationId: string,
  request: ExportDataRequest
): Promise<SyncJob> => {
  const response = await axiosInstance.post(API_ROUTES.INTEGRATIONS.EBILLING.EXPORT, {
    integrationId,
    ...request
  });
  return response.data;
};

/**
 * Exports data to a law firm billing system
 * @param integrationId Integration ID to export to
 * @param request Export data request
 * @returns Promise resolving to the created sync job
 */
export const exportDataToLawFirm = async (
  integrationId: string,
  request: ExportDataRequest
): Promise<SyncJob> => {
  const response = await axiosInstance.post(API_ROUTES.INTEGRATIONS.LAWFIRM.EXPORT, {
    integrationId,
    ...request
  });
  return response.data;
};

/**
 * Fetches synchronization jobs for an integration
 * @param integrationId Integration ID to fetch jobs for
 * @returns Promise resolving to array of sync jobs
 */
export const getSyncJobs = async (integrationId: string): Promise<SyncJob[]> => {
  const url = buildUrlWithParams(`${API_ROUTES.INTEGRATIONS.BASE}/:id/jobs`, { id: integrationId });
  const response = await axiosInstance.get(url);
  return response.data;
};

/**
 * Fetches the status of a specific sync job
 * @param jobId Sync job ID to fetch
 * @returns Promise resolving to the sync job details
 */
export const getSyncJobStatus = async (jobId: string): Promise<SyncJob> => {
  const url = buildUrlWithParams(`${API_ROUTES.INTEGRATIONS.BASE}/jobs/:id`, { id: jobId });
  const response = await axiosInstance.get(url);
  return response.data;
};

/**
 * Fetches available file templates for import/export
 * @param dataType Optional data type filter
 * @returns Promise resolving to array of file templates
 */
export const getFileTemplates = async (dataType?: string): Promise<FileTemplate[]> => {
  const url = dataType
    ? `${API_ROUTES.INTEGRATIONS.FILE.TEMPLATES}?dataType=${dataType}`
    : API_ROUTES.INTEGRATIONS.FILE.TEMPLATES;
  const response = await axiosInstance.get(url);
  return response.data;
};

/**
 * Downloads a file template for import
 * @param templateId Template ID to download
 * @returns Promise resolving to the template file as a Blob
 */
export const downloadFileTemplate = async (templateId: string): Promise<Blob> => {
  const url = `${API_ROUTES.INTEGRATIONS.FILE.TEMPLATES}/${templateId}`;
  const response = await axiosInstance.get(url, {
    responseType: 'blob'
  });
  return response.data;
};

/**
 * Uploads a file for import
 * @param file File to upload
 * @param dataType Type of data being imported
 * @param options Additional options for import
 * @returns Promise resolving to the import result
 */
export const uploadFile = async (
  file: File,
  dataType: string,
  options?: object
): Promise<any> => {
  const formData = new FormData();
  formData.append('file', file);
  formData.append('dataType', dataType);
  
  if (options) {
    formData.append('options', JSON.stringify(options));
  }
  
  const response = await axiosInstance.post(API_ROUTES.INTEGRATIONS.FILE.IMPORT, formData, {
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  });
  
  return response.data;
};

/**
 * Searches for attorneys in UniCourt database
 * @param searchParams Search parameters
 * @returns Promise resolving to search results
 */
export const searchUniCourtAttorney = async (searchParams: object): Promise<any> => {
  const response = await axiosInstance.post(API_ROUTES.INTEGRATIONS.UNICOURT.SEARCH, searchParams);
  return response.data;
};

/**
 * Fetches detailed information about an attorney from UniCourt
 * @param attorneyId UniCourt attorney ID
 * @returns Promise resolving to attorney details
 */
export const getUniCourtAttorneyDetails = async (attorneyId: string): Promise<any> => {
  const url = buildUrlWithParams(API_ROUTES.INTEGRATIONS.UNICOURT.ATTORNEY, { id: attorneyId });
  const response = await axiosInstance.get(url);
  return response.data;
};

/**
 * Maps a UniCourt attorney to a Justice Bid attorney
 * @param justiceAttorneyId Justice Bid attorney ID
 * @param unicourtAttorneyId UniCourt attorney ID
 * @returns Promise resolving to the mapping result
 */
export const mapUniCourtAttorney = async (
  justiceAttorneyId: string,
  unicourtAttorneyId: string
): Promise<any> => {
  const response = await axiosInstance.post(API_ROUTES.INTEGRATIONS.UNICOURT.MAPPING, {
    justiceAttorneyId,
    unicourtAttorneyId
  });
  return response.data;
};