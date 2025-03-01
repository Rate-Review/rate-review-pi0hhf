import axios from 'axios'; // ^1.4.0
import { apiClient, API_ROUTES, FileUploadResponse, FileDownloadOptions, FileImportOptions, ImportValidationResult } from '../api';
import { validateFileSize, validateFileType } from '../utils/file';

/**
 * Service for handling file operations such as uploads, downloads, imports, and exports in the Justice Bid application
 */

/**
 * Uploads a file to the server with optional metadata
 * @param file The file to upload
 * @param options Optional metadata
 * @returns Response containing the uploaded file details and server response
 */
export const uploadFile = async (
  file: File,
  options?: object
): Promise<FileUploadResponse> => {
  // LD1: Validate file size using validateFileSize utility
  if (!validateFileSize(file)) {
    throw new Error('File size exceeds the limit.');
  }

  // LD1: Validate file type using validateFileType utility
  if (!validateFileType(file)) {
    throw new Error('Invalid file type.');
  }

  // LD1: Create FormData object and append file
  const formData = new FormData();
  formData.append('file', file);

  // LD1: Add any metadata from options to FormData
  if (options) {
    Object.entries(options).forEach(([key, value]) => {
      formData.append(key, String(value));
    });
  }

  // LD1: Make POST request to API_ROUTES.FILES.UPLOAD endpoint
  try {
    const response = await apiClient.post<FileUploadResponse>(API_ROUTES.DOCUMENTS.UPLOAD, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    // LD1: Return response with uploaded file details
    return response;
  } catch (error) {
    console.error('File upload failed:', error);
    throw error;
  }
};

/**
 * Downloads a file from the server with the specified options
 * @param fileId The ID of the file to download
 * @param options File download options
 * @returns File blob that can be used to create a download link
 */
export const downloadFile = async (
  fileId: string,
  options?: FileDownloadOptions
): Promise<Blob> => {
  // LD1: Make GET request to API_ROUTES.FILES.DOWNLOAD endpoint with fileId
  // LD1: Set responseType to 'blob' in request config
  // LD1: Add any additional parameters from options
  try {
    const response = await apiClient.get<Blob>(API_ROUTES.DOCUMENTS.DOWNLOAD(fileId), {
      responseType: 'blob', // Ensure response is treated as a blob
      params: options, // Include any additional parameters
    });
    // LD1: Return the blob response data
    return response;
  } catch (error) {
    console.error('File download failed:', error);
    throw error;
  }
};

/**
 * Exports rate data to a file in the specified format
 * @param filters Filters for the rate data
 * @param format The format to export the data in
 * @returns File blob containing the exported rates
 */
export const exportRates = async (
  filters: object,
  format: string
): Promise<Blob> => {
  // LD1: Make POST request to API_ROUTES.RATES.EXPORT endpoint with filters and format
  // LD1: Set responseType to 'blob' in request config
  try {
    const response = await apiClient.post<Blob>(API_ROUTES.RATES.EXPORT, filters, {
      responseType: 'blob',
      params: { format },
    });
    // LD1: Return the blob response data
    return response;
  } catch (error) {
    console.error('Rate export failed:', error);
    throw error;
  }
};

/**
 * Exports billing history data to a file in the specified format
 * @param filters Filters for the billing history data
 * @param format The format to export the data in
 * @returns File blob containing the exported billing history
 */
export const exportBillingHistory = async (
  filters: object,
  format: string
): Promise<Blob> => {
  // LD1: Make POST request to API_ROUTES.BILLING.EXPORT endpoint with filters and format
  // LD1: Set responseType to 'blob' in request config
  try {
    const response = await apiClient.post<Blob>(API_ROUTES.INTEGRATIONS.FILE.EXPORT, filters, {
      responseType: 'blob',
      params: { format },
    });
    // LD1: Return the blob response data
    return response;
  } catch (error) {
    console.error('Billing history export failed:', error);
    throw error;
  }
};

/**
 * Gets a template file for data import in the specified format
 * @param templateType The type of template to retrieve
 * @param format The format of the template
 * @returns Template file blob that can be downloaded
 */
export const getTemplateFile = async (
  templateType: string,
  format: string
): Promise<Blob> => {
  // LD1: Make GET request to API_ROUTES.FILES.TEMPLATES endpoint with templateType and format parameters
  // LD1: Set responseType to 'blob' in request config
  try {
    const response = await apiClient.get<Blob>(API_ROUTES.INTEGRATIONS.FILE.TEMPLATES, {
      responseType: 'blob',
      params: { templateType, format },
    });
    // LD1: Return the blob response data
    return response;
  } catch (error) {
    console.error('Template file retrieval failed:', error);
    throw error;
  }
};

/**
 * Imports rate data from a file with mapping options
 * @param file The file containing the rate data
 * @param importOptions Options for the import process including field mappings
 * @returns Response containing the import results including success count and errors
 */
export const importRates = async (
  file: File,
  importOptions?: FileImportOptions
): Promise<object> => {
  // LD1: Validate file using validateFileType utility (must be Excel or CSV)
  if (!validateFileType(file, ['.xlsx', '.xls', '.csv'])) {
    throw new Error('Invalid file type. Only Excel and CSV files are supported.');
  }

  // LD1: Create FormData object and append file
  const formData = new FormData();
  formData.append('file', file);

  // LD1: Add field mapping options to FormData
  if (importOptions) {
    Object.entries(importOptions).forEach(([key, value]) => {
      formData.append(key, JSON.stringify(value));
    });
  }

  // LD1: Make POST request to API_ROUTES.RATES.IMPORT endpoint
  try {
    const response = await apiClient.post(API_ROUTES.RATES.IMPORT, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    // LD1: Return response with import results
    return response;
  } catch (error) {
    console.error('Rate import failed:', error);
    throw error;
  }
};

/**
 * Imports billing history data from a file with mapping options
 * @param file The file containing the billing history data
 * @param importOptions Options for the import process including field mappings
 * @returns Response containing the import results including success count and errors
 */
export const importBillingHistory = async (
  file: File,
  importOptions?: FileImportOptions
): Promise<object> => {
  // LD1: Validate file using validateFileType utility (must be Excel or CSV)
  if (!validateFileType(file, ['.xlsx', '.xls', '.csv'])) {
    throw new Error('Invalid file type. Only Excel and CSV files are supported.');
  }

  // LD1: Create FormData object and append file
  const formData = new FormData();
  formData.append('file', file);

  // LD1: Add field mapping options to FormData
  if (importOptions) {
    Object.entries(importOptions).forEach(([key, value]) => {
      formData.append(key, JSON.stringify(value));
    });
  }

  // LD1: Make POST request to API_ROUTES.BILLING.IMPORT endpoint
  try {
    const response = await apiClient.post(API_ROUTES.INTEGRATIONS.FILE.IMPORT, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    // LD1: Return response with import results
    return response;
  } catch (error) {
    console.error('Billing history import failed:', error);
    throw error;
  }
};

/**
 * Validates import data before actual import
 * @param file The file containing the data to validate
 * @param importType The type of data being imported
 * @param importOptions Options for the import process including field mappings
 * @returns Validation results including any errors or warnings
 */
export const validateImportData = async (
  file: File,
  importType: string,
  importOptions?: FileImportOptions
): Promise<ImportValidationResult> => {
  // LD1: Create FormData object and append file
  const formData = new FormData();
  formData.append('file', file);

  // LD1: Add importType and mapping options to FormData
  formData.append('importType', importType);
  if (importOptions) {
    Object.entries(importOptions).forEach(([key, value]) => {
      formData.append(key, JSON.stringify(value));
    });
  }

  // LD1: Make POST request to API_ROUTES.FILES.VALIDATE endpoint
  try {
    const response = await apiClient.post<ImportValidationResult>(API_ROUTES.INTEGRATIONS.FILE.IMPORT, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    // LD1: Return response with validation results including data preview
    return response;
  } catch (error) {
    console.error('Import validation failed:', error);
    throw error;
  }
};

/**
 * Exports Outside Counsel Guidelines to a PDF file
 * @param ocgId The ID of the OCG to export
 * @param options Additional options for the export
 * @returns PDF file blob containing the OCG document
 */
export const exportOCG = async (
  ocgId: string,
  options?: object
): Promise<Blob> => {
  // LD1: Make GET request to API_ROUTES.OCG.EXPORT endpoint with ocgId
  // LD1: Set responseType to 'blob' in request config
  // LD1: Include any additional options as query parameters
  try {
    const response = await apiClient.get<Blob>(API_ROUTES.OCG.BY_ID(ocgId), {
      responseType: 'blob',
      params: options,
    });
    // LD1: Return the blob response data
    return response;
  } catch (error) {
    console.error('OCG export failed:', error);
    throw error;
  }
};

/**
 * Helper function to initiate browser download of a blob with a filename
 * @param blob The blob to download
 * @param filename The filename for the downloaded file
 */
export const initiateDownload = (blob: Blob, filename: string): void => {
  // LD1: Create a URL for the blob using URL.createObjectURL
  const url = URL.createObjectURL(blob);

  // LD1: Create a temporary anchor element
  const link = document.createElement('a');

  // LD1: Set the href to the blob URL
  link.href = url;

  // LD1: Set the download attribute to the filename
  link.download = filename;

  // LD1: Programmatically click the anchor element to trigger download
  document.body.appendChild(link);
  link.click();

  // LD1: Clean up by revoking the blob URL
  document.body.removeChild(link);
  URL.revokeObjectURL(url);
};