/**
 * Configuration Service
 * 
 * Service module that provides functions for fetching, updating and managing system configuration settings
 * including organization settings, rate rules, approval workflows, integration settings, and other
 * configurable aspects of the Justice Bid system.
 * 
 * @version 1.0.0
 */

import { get, post, put, del } from '../services/api';
import { AxiosError } from 'axios'; // ^1.4.0

import { API_ROUTES } from '../constants/api';
import { OrganizationSettings } from '../types/organization';
import { RateRules } from '../types/rate';
import { ApprovalWorkflow } from '../types/negotiation';
import { IntegrationConfig } from '../types/integration';
import { AISettings } from '../types/ai';
import { NotificationSettings } from '../types/common';

/**
 * Fetches organization settings for the specified organization
 * @param organizationId - The ID of the organization
 * @returns Promise resolving to organization settings data
 */
export async function getOrganizationSettings(organizationId: string): Promise<OrganizationSettings> {
  try {
    const endpoint = `${API_ROUTES.ORGANIZATIONS.SETTINGS(organizationId)}`;
    const response = await get<OrganizationSettings>(endpoint);
    return response;
  } catch (error) {
    const axiosError = error as AxiosError;
    throw new Error(`Failed to fetch organization settings: ${axiosError.message}`);
  }
}

/**
 * Updates organization settings for the specified organization
 * @param organizationId - The ID of the organization
 * @param settings - The updated organization settings
 * @returns Promise resolving to updated organization settings
 */
export async function updateOrganizationSettings(
  organizationId: string, 
  settings: OrganizationSettings
): Promise<OrganizationSettings> {
  try {
    const endpoint = `${API_ROUTES.ORGANIZATIONS.SETTINGS(organizationId)}`;
    const response = await put<OrganizationSettings>(endpoint, settings);
    return response;
  } catch (error) {
    const axiosError = error as AxiosError;
    throw new Error(`Failed to update organization settings: ${axiosError.message}`);
  }
}

/**
 * Fetches rate rules for the specified organization
 * @param organizationId - The ID of the organization
 * @returns Promise resolving to rate rules configuration
 */
export async function getRateRules(organizationId: string): Promise<RateRules> {
  try {
    const endpoint = `${API_ROUTES.ORGANIZATIONS.DETAIL(organizationId)}/rate-rules`;
    const response = await get<RateRules>(endpoint);
    return response;
  } catch (error) {
    const axiosError = error as AxiosError;
    throw new Error(`Failed to fetch rate rules: ${axiosError.message}`);
  }
}

/**
 * Updates rate rules for the specified organization
 * @param organizationId - The ID of the organization
 * @param rateRules - The updated rate rules
 * @returns Promise resolving to updated rate rules
 */
export async function updateRateRules(
  organizationId: string, 
  rateRules: RateRules
): Promise<RateRules> {
  try {
    const endpoint = `${API_ROUTES.ORGANIZATIONS.DETAIL(organizationId)}/rate-rules`;
    const response = await put<RateRules>(endpoint, rateRules);
    return response;
  } catch (error) {
    const axiosError = error as AxiosError;
    throw new Error(`Failed to update rate rules: ${axiosError.message}`);
  }
}

/**
 * Fetches approval workflows for the specified organization
 * @param organizationId - The ID of the organization
 * @returns Promise resolving to list of approval workflows
 */
export async function getApprovalWorkflows(organizationId: string): Promise<ApprovalWorkflow[]> {
  try {
    const endpoint = `${API_ROUTES.ORGANIZATIONS.DETAIL(organizationId)}/approval-workflows`;
    const response = await get<ApprovalWorkflow[]>(endpoint);
    return response;
  } catch (error) {
    const axiosError = error as AxiosError;
    throw new Error(`Failed to fetch approval workflows: ${axiosError.message}`);
  }
}

/**
 * Creates a new approval workflow for the specified organization
 * @param organizationId - The ID of the organization
 * @param workflow - The approval workflow to create
 * @returns Promise resolving to created approval workflow
 */
export async function createApprovalWorkflow(
  organizationId: string, 
  workflow: ApprovalWorkflow
): Promise<ApprovalWorkflow> {
  try {
    const endpoint = `${API_ROUTES.ORGANIZATIONS.DETAIL(organizationId)}/approval-workflows`;
    const response = await post<ApprovalWorkflow>(endpoint, workflow);
    return response;
  } catch (error) {
    const axiosError = error as AxiosError;
    throw new Error(`Failed to create approval workflow: ${axiosError.message}`);
  }
}

/**
 * Updates an existing approval workflow
 * @param workflowId - The ID of the workflow to update
 * @param workflow - The updated approval workflow
 * @returns Promise resolving to updated approval workflow
 */
export async function updateApprovalWorkflow(
  workflowId: string, 
  workflow: ApprovalWorkflow
): Promise<ApprovalWorkflow> {
  try {
    const endpoint = `${API_ROUTES.ORGANIZATIONS.BASE}/approval-workflows/${workflowId}`;
    const response = await put<ApprovalWorkflow>(endpoint, workflow);
    return response;
  } catch (error) {
    const axiosError = error as AxiosError;
    throw new Error(`Failed to update approval workflow: ${axiosError.message}`);
  }
}

/**
 * Deletes an approval workflow
 * @param workflowId - The ID of the workflow to delete
 * @returns Promise resolving to void
 */
export async function deleteApprovalWorkflow(workflowId: string): Promise<void> {
  try {
    const endpoint = `${API_ROUTES.ORGANIZATIONS.BASE}/approval-workflows/${workflowId}`;
    await del(endpoint);
  } catch (error) {
    const axiosError = error as AxiosError;
    throw new Error(`Failed to delete approval workflow: ${axiosError.message}`);
  }
}

/**
 * Fetches integration configurations for the specified organization
 * @param organizationId - The ID of the organization
 * @param integrationType - The type of integration to fetch configurations for
 * @returns Promise resolving to list of integration configurations
 */
export async function getIntegrationConfigs(
  organizationId: string, 
  integrationType: string
): Promise<IntegrationConfig[]> {
  try {
    const endpoint = `${API_ROUTES.ORGANIZATIONS.DETAIL(organizationId)}/integrations/${integrationType}`;
    const response = await get<IntegrationConfig[]>(endpoint);
    return response;
  } catch (error) {
    const axiosError = error as AxiosError;
    throw new Error(`Failed to fetch integration configurations: ${axiosError.message}`);
  }
}

/**
 * Creates a new integration configuration
 * @param organizationId - The ID of the organization
 * @param config - The integration configuration to create
 * @returns Promise resolving to created integration configuration
 */
export async function createIntegrationConfig(
  organizationId: string, 
  config: IntegrationConfig
): Promise<IntegrationConfig> {
  try {
    const endpoint = `${API_ROUTES.ORGANIZATIONS.DETAIL(organizationId)}/integrations`;
    const response = await post<IntegrationConfig>(endpoint, config);
    return response;
  } catch (error) {
    const axiosError = error as AxiosError;
    throw new Error(`Failed to create integration configuration: ${axiosError.message}`);
  }
}

/**
 * Updates an existing integration configuration
 * @param configId - The ID of the configuration to update
 * @param config - The updated integration configuration
 * @returns Promise resolving to updated integration configuration
 */
export async function updateIntegrationConfig(
  configId: string, 
  config: IntegrationConfig
): Promise<IntegrationConfig> {
  try {
    const endpoint = `${API_ROUTES.ORGANIZATIONS.BASE}/integrations/${configId}`;
    const response = await put<IntegrationConfig>(endpoint, config);
    return response;
  } catch (error) {
    const axiosError = error as AxiosError;
    throw new Error(`Failed to update integration configuration: ${axiosError.message}`);
  }
}

/**
 * Deletes an integration configuration
 * @param configId - The ID of the configuration to delete
 * @returns Promise resolving to void
 */
export async function deleteIntegrationConfig(configId: string): Promise<void> {
  try {
    const endpoint = `${API_ROUTES.ORGANIZATIONS.BASE}/integrations/${configId}`;
    await del(endpoint);
  } catch (error) {
    const axiosError = error as AxiosError;
    throw new Error(`Failed to delete integration configuration: ${axiosError.message}`);
  }
}

/**
 * Tests the connection for an integration configuration
 * @param configId - The ID of the configuration to test
 * @returns Promise resolving to connection test result
 */
export async function testIntegrationConnection(
  configId: string
): Promise<{ success: boolean; message: string }> {
  try {
    const endpoint = `${API_ROUTES.ORGANIZATIONS.BASE}/integrations/${configId}/test`;
    const response = await post<{ success: boolean; message: string }>(endpoint);
    return response;
  } catch (error) {
    const axiosError = error as AxiosError;
    throw new Error(`Connection test failed: ${axiosError.message}`);
  }
}

/**
 * Fetches AI configuration settings for the specified organization
 * @param organizationId - The ID of the organization
 * @returns Promise resolving to AI configuration settings
 */
export async function getAISettings(organizationId: string): Promise<AISettings> {
  try {
    const endpoint = `${API_ROUTES.ORGANIZATIONS.DETAIL(organizationId)}/ai-settings`;
    const response = await get<AISettings>(endpoint);
    return response;
  } catch (error) {
    const axiosError = error as AxiosError;
    throw new Error(`Failed to fetch AI settings: ${axiosError.message}`);
  }
}

/**
 * Updates AI configuration settings for the specified organization
 * @param organizationId - The ID of the organization
 * @param settings - The updated AI settings
 * @returns Promise resolving to updated AI configuration settings
 */
export async function updateAISettings(
  organizationId: string, 
  settings: AISettings
): Promise<AISettings> {
  try {
    const endpoint = `${API_ROUTES.ORGANIZATIONS.DETAIL(organizationId)}/ai-settings`;
    const response = await put<AISettings>(endpoint, settings);
    return response;
  } catch (error) {
    const axiosError = error as AxiosError;
    throw new Error(`Failed to update AI settings: ${axiosError.message}`);
  }
}

/**
 * Fetches notification settings for the specified user or organization
 * @param idType - Type of ID ('user' or 'organization')
 * @param id - The ID of the user or organization
 * @returns Promise resolving to notification settings
 */
export async function getNotificationSettings(
  idType: string,
  id: string
): Promise<NotificationSettings> {
  try {
    const endpoint = `${API_URL}/notifications/${idType}/${id}/settings`;
    const response = await get<NotificationSettings>(endpoint);
    return response;
  } catch (error) {
    const axiosError = error as AxiosError;
    throw new Error(`Failed to fetch notification settings: ${axiosError.message}`);
  }
}

/**
 * Updates notification settings for the specified user or organization
 * @param idType - Type of ID ('user' or 'organization')
 * @param id - The ID of the user or organization
 * @param settings - The updated notification settings
 * @returns Promise resolving to updated notification settings
 */
export async function updateNotificationSettings(
  idType: string,
  id: string,
  settings: NotificationSettings
): Promise<NotificationSettings> {
  try {
    const endpoint = `${API_URL}/notifications/${idType}/${id}/settings`;
    const response = await put<NotificationSettings>(endpoint, settings);
    return response;
  } catch (error) {
    const axiosError = error as AxiosError;
    throw new Error(`Failed to update notification settings: ${axiosError.message}`);
  }
}