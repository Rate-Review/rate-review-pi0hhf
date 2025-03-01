/**
 * Service module for interacting with the Outside Counsel Guidelines (OCG) API endpoints.
 * Provides functions for managing OCGs, negotiating guidelines, and document operations.
 * 
 * @version 1.0.0
 */

import { api } from '../api';
import { API_ROUTES } from '../api/apiRoutes';
import {
  OCGDocument,
  OCGSummary,
  OCGSection,
  OCGAlternative,
  OCGNegotiation,
  OCGFirmSelection,
  CreateOCGRequest,
  UpdateOCGRequest,
  PublishOCGRequest,
  StartOCGNegotiationRequest,
  SubmitOCGSelectionsRequest
} from '../types/ocg';
import { PaginationParams } from '../types/common';

/**
 * Fetches a list of OCGs with optional filtering, sorting, and pagination
 * @param params - Optional object with filter, sort, and pagination options
 * @returns Promise resolving to an array of OCG summaries
 */
async function getOCGs(params?: {
  filter?: Record<string, any>;
  sort?: { field: string; direction: 'asc' | 'desc' };
  pagination?: PaginationParams;
}): Promise<OCGSummary[]> {
  const url = api.buildUrl(API_ROUTES.OCG.BASE);
  return api.get<OCGSummary[]>(url, { params });
}

/**
 * Fetches a single OCG document by its ID
 * @param id - The OCG document ID
 * @returns Promise resolving to the OCG document
 */
async function getOCGById(id: string): Promise<OCGDocument> {
  const url = api.buildUrlWithParams(API_ROUTES.OCG.BY_ID, { id });
  return api.get<OCGDocument>(url);
}

/**
 * Creates a new OCG document
 * @param ocgData - The OCG data to create
 * @returns Promise resolving to the created OCG document
 */
async function createOCG(ocgData: CreateOCGRequest): Promise<OCGDocument> {
  const url = api.buildUrl(API_ROUTES.OCG.BASE);
  return api.post<OCGDocument>(url, ocgData);
}

/**
 * Updates an existing OCG document
 * @param id - The OCG document ID
 * @param ocgData - The updated OCG data
 * @returns Promise resolving to the updated OCG document
 */
async function updateOCG(id: string, ocgData: UpdateOCGRequest): Promise<OCGDocument> {
  const url = api.buildUrlWithParams(API_ROUTES.OCG.BY_ID, { id });
  return api.put<OCGDocument>(url, ocgData);
}

/**
 * Deletes an OCG document
 * @param id - The OCG document ID
 * @returns Promise resolving when the OCG is deleted
 */
async function deleteOCG(id: string): Promise<void> {
  const url = api.buildUrlWithParams(API_ROUTES.OCG.BY_ID, { id });
  return api.delete<void>(url);
}

/**
 * Publishes an OCG document, making it available for negotiation
 * @param publishData - The publish request data containing the OCG ID
 * @returns Promise resolving to the published OCG document
 */
async function publishOCG(publishData: PublishOCGRequest): Promise<OCGDocument> {
  const url = api.buildUrlWithParams(API_ROUTES.OCG.BY_ID, { id: publishData.id }) + '/publish';
  return api.post<OCGDocument>(url, publishData);
}

/**
 * Creates a new section in an OCG document
 * @param ocgId - The OCG document ID
 * @param sectionData - The section data to create
 * @returns Promise resolving to the created section
 */
async function createSection(ocgId: string, sectionData: Omit<OCGSection, 'id'>): Promise<OCGSection> {
  const url = api.buildUrlWithParams(API_ROUTES.OCG.SECTIONS, { id: ocgId });
  return api.post<OCGSection>(url, sectionData);
}

/**
 * Updates an existing section in an OCG document
 * @param ocgId - The OCG document ID
 * @param sectionId - The section ID
 * @param sectionData - The updated section data
 * @returns Promise resolving to the updated section
 */
async function updateSection(
  ocgId: string,
  sectionId: string,
  sectionData: Partial<OCGSection>
): Promise<OCGSection> {
  const url = api.buildUrlWithParams(API_ROUTES.OCG.SECTIONS, { id: ocgId }) + `/${sectionId}`;
  return api.put<OCGSection>(url, sectionData);
}

/**
 * Deletes a section from an OCG document
 * @param ocgId - The OCG document ID
 * @param sectionId - The section ID
 * @returns Promise resolving when the section is deleted
 */
async function deleteSection(ocgId: string, sectionId: string): Promise<void> {
  const url = api.buildUrlWithParams(API_ROUTES.OCG.SECTIONS, { id: ocgId }) + `/${sectionId}`;
  return api.delete<void>(url);
}

/**
 * Creates a new alternative for a section in an OCG document
 * @param ocgId - The OCG document ID
 * @param sectionId - The section ID
 * @param alternativeData - The alternative data to create
 * @returns Promise resolving to the created alternative
 */
async function createAlternative(
  ocgId: string,
  sectionId: string,
  alternativeData: Omit<OCGAlternative, 'id'>
): Promise<OCGAlternative> {
  const url = api.buildUrlWithParams(API_ROUTES.OCG.ALTERNATIVES, { id: ocgId, sectionId });
  return api.post<OCGAlternative>(url, alternativeData);
}

/**
 * Updates an existing alternative for a section
 * @param ocgId - The OCG document ID
 * @param sectionId - The section ID
 * @param alternativeId - The alternative ID
 * @param alternativeData - The updated alternative data
 * @returns Promise resolving to the updated alternative
 */
async function updateAlternative(
  ocgId: string,
  sectionId: string,
  alternativeId: string,
  alternativeData: Partial<OCGAlternative>
): Promise<OCGAlternative> {
  const url = api.buildUrlWithParams(API_ROUTES.OCG.ALTERNATIVES, { id: ocgId, sectionId }) + `/${alternativeId}`;
  return api.put<OCGAlternative>(url, alternativeData);
}

/**
 * Deletes an alternative from a section
 * @param ocgId - The OCG document ID
 * @param sectionId - The section ID
 * @param alternativeId - The alternative ID
 * @returns Promise resolving when the alternative is deleted
 */
async function deleteAlternative(ocgId: string, sectionId: string, alternativeId: string): Promise<void> {
  const url = api.buildUrlWithParams(API_ROUTES.OCG.ALTERNATIVES, { id: ocgId, sectionId }) + `/${alternativeId}`;
  return api.delete<void>(url);
}

/**
 * Starts an OCG negotiation with a law firm
 * @param negotiationData - The negotiation request data
 * @returns Promise resolving to the created negotiation
 */
async function startOCGNegotiation(negotiationData: StartOCGNegotiationRequest): Promise<OCGNegotiation> {
  const url = api.buildUrl(API_ROUTES.OCG.BASE) + '/negotiations';
  return api.post<OCGNegotiation>(url, negotiationData);
}

/**
 * Gets all OCG negotiations for a client or firm
 * @param params - Optional object with filtering options
 * @returns Promise resolving to an array of OCG negotiations
 */
async function getOCGNegotiations(params?: {
  clientId?: string;
  firmId?: string;
  status?: string;
}): Promise<OCGNegotiation[]> {
  const url = api.buildUrl(API_ROUTES.OCG.BASE) + '/negotiations';
  return api.get<OCGNegotiation[]>(url, { params });
}

/**
 * Gets a specific OCG negotiation by ID
 * @param negotiationId - The negotiation ID
 * @returns Promise resolving to the OCG negotiation
 */
async function getOCGNegotiationById(negotiationId: string): Promise<OCGNegotiation> {
  const url = api.buildUrl(API_ROUTES.OCG.BASE) + `/negotiations/${negotiationId}`;
  return api.get<OCGNegotiation>(url);
}

/**
 * Submits law firm selections for an OCG negotiation
 * @param selectionsData - The selections data
 * @returns Promise resolving to the updated negotiation
 */
async function submitOCGSelections(selectionsData: SubmitOCGSelectionsRequest): Promise<OCGNegotiation> {
  const url = api.buildUrlWithParams(API_ROUTES.OCG.SELECTIONS, { id: selectionsData.negotiationId });
  return api.post<OCGNegotiation>(url, selectionsData);
}

/**
 * Approves law firm selections for an OCG negotiation
 * @param negotiationId - The negotiation ID
 * @param approvalData - Optional approval data with comments
 * @returns Promise resolving to the updated negotiation
 */
async function approveOCGSelections(
  negotiationId: string,
  approvalData?: { comments?: string }
): Promise<OCGNegotiation> {
  const url = api.buildUrl(API_ROUTES.OCG.BASE) + `/negotiations/${negotiationId}/approve`;
  return api.post<OCGNegotiation>(url, approvalData || {});
}

/**
 * Rejects law firm selections for an OCG negotiation
 * @param negotiationId - The negotiation ID
 * @param rejectionData - Rejection data with feedback
 * @returns Promise resolving to the updated negotiation
 */
async function rejectOCGSelections(
  negotiationId: string,
  rejectionData: { feedback: string }
): Promise<OCGNegotiation> {
  const url = api.buildUrl(API_ROUTES.OCG.BASE) + `/negotiations/${negotiationId}/reject`;
  return api.post<OCGNegotiation>(url, rejectionData);
}

/**
 * Updates the point budget for a firm in an OCG negotiation
 * @param negotiationId - The negotiation ID
 * @param budgetData - The updated budget data
 * @returns Promise resolving to the updated negotiation
 */
async function updateFirmPointBudget(
  negotiationId: string,
  budgetData: { pointBudget: number }
): Promise<OCGNegotiation> {
  const url = api.buildUrl(API_ROUTES.OCG.BASE) + `/negotiations/${negotiationId}/budget`;
  return api.put<OCGNegotiation>(url, budgetData);
}

/**
 * Finalizes an OCG after negotiation is complete
 * @param ocgId - The OCG document ID
 * @returns Promise resolving to the finalized OCG document
 */
async function finalizeOCG(ocgId: string): Promise<OCGDocument> {
  const url = api.buildUrlWithParams(API_ROUTES.OCG.BY_ID, { id: ocgId }) + '/finalize';
  return api.post<OCGDocument>(url);
}

/**
 * Adds an electronic signature to an OCG
 * @param ocgId - The OCG document ID
 * @param signatureData - The signature data
 * @returns Promise resolving to the signed OCG document
 */
async function signOCG(
  ocgId: string,
  signatureData: { name: string; title: string; date: string }
): Promise<OCGDocument> {
  const url = api.buildUrlWithParams(API_ROUTES.OCG.BY_ID, { id: ocgId }) + '/sign';
  return api.post<OCGDocument>(url, signatureData);
}

/**
 * Gets the version history for an OCG
 * @param ocgId - The OCG document ID
 * @returns Promise resolving to an array of version history entries
 */
async function getOCGVersionHistory(
  ocgId: string
): Promise<Array<{ version: number; date: string; changedBy: string }>> {
  const url = api.buildUrlWithParams(API_ROUTES.OCG.BY_ID, { id: ocgId }) + '/history';
  return api.get<Array<{ version: number; date: string; changedBy: string }>>(url);
}

/**
 * Generates a document (PDF/DOCX) from an OCG
 * @param ocgId - The OCG document ID
 * @param options - Options like format, filename, etc.
 * @returns Promise resolving to the document blob
 */
async function generateOCGDocument(
  ocgId: string,
  options: { format: 'pdf' | 'docx'; includeHistory?: boolean }
): Promise<Blob> {
  const url = api.buildUrlWithParams(API_ROUTES.OCG.BY_ID, { id: ocgId }) + '/document';
  const params = {
    format: options.format,
    includeHistory: options.includeHistory
  };
  return api.get<Blob>(url, { params, responseType: 'blob' });
}

/**
 * Downloads a generated OCG document
 * @param ocgId - The OCG document ID
 * @param format - The document format ('pdf' or 'docx')
 * @param filename - The filename to save as
 * @returns Promise resolving when the download starts
 */
async function downloadOCGDocument(
  ocgId: string,
  format: 'pdf' | 'docx',
  filename: string
): Promise<void> {
  const url = api.buildUrlWithParams(API_ROUTES.OCG.BY_ID, { id: ocgId }) + '/document';
  const params = { format };
  return api.downloadFile(url, filename, { params });
}

export default {
  getOCGs,
  getOCGById,
  createOCG,
  updateOCG,
  deleteOCG,
  publishOCG,
  createSection,
  updateSection,
  deleteSection,
  createAlternative,
  updateAlternative,
  deleteAlternative,
  startOCGNegotiation,
  getOCGNegotiations,
  getOCGNegotiationById,
  submitOCGSelections,
  approveOCGSelections,
  rejectOCGSelections,
  updateFirmPointBudget,
  finalizeOCG,
  signOCG,
  getOCGVersionHistory,
  generateOCGDocument,
  downloadOCGDocument
};