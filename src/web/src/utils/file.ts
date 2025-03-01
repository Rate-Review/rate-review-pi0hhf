import FileType from 'file-type'; // file-type@^16.5.4

// Constants for file validation
export const ALLOWED_MIME_TYPES = [
  'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
  'application/vnd.ms-excel',
  'text/csv',
  'application/pdf'
];

export const ALLOWED_EXTENSIONS = ['.xlsx', '.xls', '.csv', '.pdf'];
export const MAX_FILE_SIZE = 10 * 1024 * 1024; // 10MB
export const DEFAULT_ENCODING = 'utf-8';

// Interfaces
export interface FileValidationResult {
  valid: boolean;
  errors: string[];
}

export interface FileValidationOptions {
  maxSize?: number;
  allowedTypes?: string[];
}

export interface CSVParseOptions {
  delimiter?: string;
  hasHeader?: boolean;
}

/**
 * Validates if the file is of an allowed type based on extension or MIME type
 * @param file The file to validate
 * @param allowedTypes Array of allowed file extensions or MIME types
 * @returns True if the file type is allowed, false otherwise
 */
export const validateFileType = (file: File, allowedTypes: string[] = ALLOWED_EXTENSIONS): boolean => {
  if (!file || !file.name) {
    return false;
  }
  
  const extension = getFileExtension(file.name).toLowerCase();
  
  // Check by extension
  const isExtensionValid = allowedTypes.some(type => 
    type.startsWith('.') ? extension === type.toLowerCase() : false
  );
  
  // Check by MIME type if available
  const isMimeValid = allowedTypes.some(type => 
    !type.startsWith('.') ? file.type === type : false
  );
  
  return isExtensionValid || isMimeValid;
};

/**
 * Validates if the file size is within allowed limits
 * @param file The file to validate
 * @param maxSize Maximum allowed file size in bytes
 * @returns True if the file size is within limits, false otherwise
 */
export const validateFileSize = (file: File, maxSize: number = MAX_FILE_SIZE): boolean => {
  return file && file.size <= maxSize;
};

/**
 * Comprehensive file validation checking both type and size
 * @param file The file to validate
 * @param options Validation options including max size and allowed types
 * @returns Validation result with success status and any error messages
 */
export const validateFile = (
  file: File, 
  options: FileValidationOptions = { maxSize: MAX_FILE_SIZE, allowedTypes: ALLOWED_EXTENSIONS }
): FileValidationResult => {
  const result: FileValidationResult = {
    valid: true,
    errors: []
  };
  
  if (!file) {
    result.valid = false;
    result.errors.push('No file provided');
    return result;
  }
  
  // Check file type
  if (options.allowedTypes && !validateFileType(file, options.allowedTypes)) {
    result.valid = false;
    result.errors.push(`File type not allowed. Allowed types: ${options.allowedTypes.join(', ')}`);
  }
  
  // Check file size
  if (options.maxSize && !validateFileSize(file, options.maxSize)) {
    result.valid = false;
    result.errors.push(`File size exceeds the maximum allowed size of ${formatFileSize(options.maxSize)}`);
  }
  
  return result;
};

/**
 * Reads a file and returns its contents as text using FileReader
 * @param file The file to read
 * @param encoding Character encoding to use (default: utf-8)
 * @returns Promise resolving to the file contents as text
 */
export const readFileAsText = (file: File, encoding: string = DEFAULT_ENCODING): Promise<string> => {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    
    reader.onload = (event) => {
      resolve(event.target?.result as string);
    };
    
    reader.onerror = (error) => {
      reject(new Error(`Failed to read file: ${error}`));
    };
    
    reader.readAsText(file, encoding);
  });
};

/**
 * Reads a file and returns its contents as ArrayBuffer for binary processing
 * @param file The file to read
 * @returns Promise resolving to the file contents as ArrayBuffer
 */
export const readFileAsArrayBuffer = (file: File): Promise<ArrayBuffer> => {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    
    reader.onload = (event) => {
      resolve(event.target?.result as ArrayBuffer);
    };
    
    reader.onerror = (error) => {
      reject(new Error(`Failed to read file: ${error}`));
    };
    
    reader.readAsArrayBuffer(file);
  });
};

/**
 * Parses CSV file content into a structured array
 * @param content The CSV content as a string
 * @param options Options for parsing including delimiter and header flag
 * @returns 2D array representing the CSV data
 */
export const parseCSV = (
  content: string, 
  options: CSVParseOptions = { delimiter: ',', hasHeader: true }
): Array<Array<string>> => {
  const lines = content.split(/\r\n|\n|\r/).filter(line => line.trim() !== '');
  
  // Determine delimiter if not specified
  const delimiter = options.delimiter || detectDelimiter(content);
  
  const result: Array<Array<string>> = [];
  
  for (const line of lines) {
    const row: string[] = [];
    let inQuotes = false;
    let currentValue = '';
    
    for (let i = 0; i < line.length; i++) {
      const char = line[i];
      
      if (char === '"') {
        // Handle quoted values
        if (i < line.length - 1 && line[i + 1] === '"') {
          // Double quotes inside quoted value
          currentValue += '"';
          i++; // Skip the next quote
        } else {
          // Toggle quote state
          inQuotes = !inQuotes;
        }
      } else if (char === delimiter && !inQuotes) {
        // End of field
        row.push(currentValue);
        currentValue = '';
      } else {
        // Normal character
        currentValue += char;
      }
    }
    
    // Add the last field
    row.push(currentValue);
    result.push(row);
  }
  
  return result;
};

/**
 * Helper function to detect delimiter in CSV content
 * @param content The CSV content to analyze
 * @returns The detected delimiter character
 */
const detectDelimiter = (content: string): string => {
  const firstLine = content.split(/\r\n|\n|\r/)[0];
  
  const delimiters = [',', ';', '\t', '|'];
  let maxCount = 0;
  let bestDelimiter = ',';
  
  for (const delimiter of delimiters) {
    const count = (firstLine.match(new RegExp(delimiter, 'g')) || []).length;
    if (count > maxCount) {
      maxCount = count;
      bestDelimiter = delimiter;
    }
  }
  
  return bestDelimiter;
};

/**
 * Creates a download URL for a blob or file
 * @param blob The blob to create a URL for
 * @param filename The filename (used for reference)
 * @returns URL that can be used for downloading the file
 */
export const createDownloadLink = (blob: Blob, filename: string): string => {
  return URL.createObjectURL(blob);
};

/**
 * Triggers a file download in the browser
 * @param content The content to download (Blob or string)
 * @param filename The name to give the downloaded file
 * @param mimeType The MIME type of the file (default: application/octet-stream)
 */
export const downloadFile = (
  content: Blob | string, 
  filename: string, 
  mimeType: string = 'application/octet-stream'
): void => {
  // Create Blob if content is string
  const blob = typeof content === 'string' 
    ? new Blob([content], { type: mimeType }) 
    : content;
  
  // Create download URL
  const url = URL.createObjectURL(blob);
  
  // Create temporary link element
  const link = document.createElement('a');
  link.href = url;
  link.download = filename;
  
  // Append to document, click, and clean up
  document.body.appendChild(link);
  link.click();
  
  // Clean up
  setTimeout(() => {
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  }, 100);
};

/**
 * Extracts the file extension from a filename
 * @param filename The filename to extract extension from
 * @returns File extension including the dot (e.g., '.xlsx')
 */
export const getFileExtension = (filename: string): string => {
  const parts = filename.split('.');
  return parts.length > 1 ? `.${parts[parts.length - 1].toLowerCase()}` : '';
};

/**
 * Determines the MIME type based on file extension
 * @param filename The filename to determine MIME type for
 * @returns MIME type for the file
 */
export const getMimeType = (filename: string): string => {
  const extension = getFileExtension(filename).toLowerCase();
  
  const mimeTypeMap: Record<string, string> = {
    '.xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    '.xls': 'application/vnd.ms-excel',
    '.csv': 'text/csv',
    '.pdf': 'application/pdf',
    '.json': 'application/json',
    '.txt': 'text/plain',
    '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    '.doc': 'application/msword',
    '.zip': 'application/zip',
    '.xml': 'application/xml',
    '.png': 'image/png',
    '.jpg': 'image/jpeg',
    '.jpeg': 'image/jpeg',
    '.gif': 'image/gif'
  };
  
  return mimeTypeMap[extension] || 'application/octet-stream';
};

/**
 * Formats a file size in bytes to a human-readable string
 * @param bytes The file size in bytes
 * @returns Formatted file size (e.g., '2.5 MB')
 */
export const formatFileSize = (bytes: number): string => {
  if (bytes === 0) return '0 Bytes';
  
  const k = 1024;
  const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
};