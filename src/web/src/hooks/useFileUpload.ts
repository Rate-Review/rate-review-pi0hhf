import { useState, useCallback, useRef, useEffect } from 'react';
import axios, { CancelTokenSource } from 'axios';
import { api } from '../services/api';

/**
 * Interface for the options passed to the useFileUpload hook
 */
interface UseFileUploadOptions {
  /**
   * Array of accepted file types (MIME types or extensions starting with '.')
   */
  acceptedFileTypes: string[];
  /**
   * Maximum file size allowed in megabytes
   */
  maxFileSizeMB: number;
  /**
   * API endpoint where the file will be uploaded
   */
  endpoint: string;
  /**
   * Additional data to include with the file upload
   */
  additionalData?: Record<string, any>;
  /**
   * Optional custom validation function for the file
   */
  validateFile?: (file: File) => string | null;
  /**
   * Callback fired when upload is successful
   */
  onUploadSuccess?: (result: any) => void;
  /**
   * Callback fired when upload encounters an error
   */
  onUploadError?: (error: string) => void;
}

/**
 * Interface for the return values from the useFileUpload hook
 */
interface UseFileUploadReturn {
  /**
   * Reference to the file input element for DOM manipulation
   */
  fileInputRef: React.RefObject<HTMLInputElement>;
  /**
   * The currently selected file or null if none selected
   */
  file: File | null;
  /**
   * Error message related to file validation or null if valid
   */
  fileError: string | null;
  /**
   * Boolean indicating if upload is in progress
   */
  isUploading: boolean;
  /**
   * Upload progress percentage (0-100)
   */
  uploadProgress: number;
  /**
   * Error message related to upload process or null if no error
   */
  uploadError: string | null;
  /**
   * Result data from successful upload or null
   */
  uploadResult: any | null;
  /**
   * Handler for file input change events
   */
  handleFileChange: (event: React.ChangeEvent<HTMLInputElement>) => void;
  /**
   * Handler for drag and drop events
   */
  handleFileDrop: (event: React.DragEvent<HTMLDivElement>) => void;
  /**
   * Function to initiate file upload
   */
  uploadFile: () => Promise<any | null>;
  /**
   * Function to cancel ongoing upload
   */
  cancelUpload: () => void;
  /**
   * Function to reset all file upload state values
   */
  resetFileUpload: () => void;
}

/**
 * Custom hook for handling file uploads with validation, progress tracking, and error handling
 * @param options Configuration options for the file upload
 * @returns Object containing file upload state and handlers
 */
export function useFileUpload(options: UseFileUploadOptions): UseFileUploadReturn {
  const {
    acceptedFileTypes,
    maxFileSizeMB,
    endpoint,
    additionalData = {},
    validateFile: externalValidate,
    onUploadSuccess,
    onUploadError
  } = options;

  // State for selected file and validation
  const [file, setFile] = useState<File | null>(null);
  const [fileError, setFileError] = useState<string | null>(null);
  
  // State for upload process
  const [isUploading, setIsUploading] = useState<boolean>(false);
  const [uploadProgress, setUploadProgress] = useState<number>(0);
  const [uploadError, setUploadError] = useState<string | null>(null);
  const [uploadResult, setUploadResult] = useState<any | null>(null);
  
  // References
  const fileInputRef = useRef<HTMLInputElement>(null);
  const cancelTokenSource = useRef<CancelTokenSource | null>(null);
  
  // Reset the cancel token source when component unmounts
  useEffect(() => {
    return () => {
      if (cancelTokenSource.current) {
        cancelTokenSource.current.cancel('Component unmounted');
      }
    };
  }, []);

  /**
   * Validates a file against size and type restrictions
   * @param file File to validate
   * @returns Error message or null if valid
   */
  const validateFile = useCallback((file: File): string | null => {
    // Check file size
    const fileSizeInMB = file.size / (1024 * 1024);
    if (fileSizeInMB > maxFileSizeMB) {
      return `File size exceeds the maximum allowed size of ${maxFileSizeMB}MB`;
    }
    
    // Check file type if acceptedFileTypes is not empty
    if (acceptedFileTypes.length > 0) {
      const fileType = file.type;
      const fileExtension = '.' + file.name.split('.').pop()?.toLowerCase();
      
      // Check if the file type matches any of the accepted MIME types
      const hasValidMimeType = acceptedFileTypes.some(type => 
        !type.startsWith('.') && type === fileType
      );
      
      // Check if the file extension matches any of the accepted extensions
      const hasValidExtension = acceptedFileTypes.some(type => 
        type.startsWith('.') && type.toLowerCase() === fileExtension
      );
      
      if (!hasValidMimeType && !hasValidExtension) {
        return `Invalid file type. Accepted types: ${acceptedFileTypes.join(', ')}`;
      }
    }
    
    // Use external validation if provided
    if (externalValidate) {
      return externalValidate(file);
    }
    
    return null;
  }, [acceptedFileTypes, maxFileSizeMB, externalValidate]);

  /**
   * Handles file selection from input element
   * @param event Change event from file input
   */
  const handleFileChange = useCallback((event: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = event.target.files?.[0] || null;
    
    if (selectedFile) {
      const error = validateFile(selectedFile);
      setFile(selectedFile);
      setFileError(error);
      
      // Reset upload states when a new file is selected
      setUploadProgress(0);
      setUploadError(null);
      setUploadResult(null);
    }
  }, [validateFile]);

  /**
   * Handles file drop events for drag and drop functionality
   * @param event Drag event from drop target
   */
  const handleFileDrop = useCallback((event: React.DragEvent<HTMLDivElement>) => {
    event.preventDefault();
    event.stopPropagation();
    
    const droppedFile = event.dataTransfer.files?.[0] || null;
    
    if (droppedFile) {
      const error = validateFile(droppedFile);
      setFile(droppedFile);
      setFileError(error);
      
      // Reset upload states when a new file is dropped
      setUploadProgress(0);
      setUploadError(null);
      setUploadResult(null);
    }
  }, [validateFile]);

  /**
   * Initiates file upload process
   * @returns Promise resolving to upload result or null if error
   */
  const uploadFile = useCallback(async (): Promise<any | null> => {
    if (!file) {
      setUploadError('No file selected');
      if (onUploadError) onUploadError('No file selected');
      return null;
    }
    
    if (fileError) {
      setUploadError(fileError);
      if (onUploadError) onUploadError(fileError);
      return null;
    }
    
    try {
      setIsUploading(true);
      setUploadProgress(0);
      setUploadError(null);
      
      // Create a new cancel token source for this upload
      cancelTokenSource.current = axios.CancelToken.source();
      
      // Create form data
      const formData = new FormData();
      formData.append('file', file);
      
      // Add any additional data to form data
      Object.entries(additionalData).forEach(([key, value]) => {
        formData.append(key, typeof value === 'object' ? JSON.stringify(value) : String(value));
      });
      
      // Use axios directly to support cancellation
      const response = await axios.post(endpoint, formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        },
        onUploadProgress: (progressEvent) => {
          if (progressEvent.total) {
            const percentCompleted = Math.round((progressEvent.loaded * 100) / progressEvent.total);
            setUploadProgress(percentCompleted);
          }
        },
        cancelToken: cancelTokenSource.current.token
      });
      
      const result = response.data;
      setUploadResult(result);
      setIsUploading(false);
      
      if (onUploadSuccess) {
        onUploadSuccess(result);
      }
      
      return result;
    } catch (error) {
      setIsUploading(false);
      
      // Check if the request was cancelled
      if (axios.isCancel(error)) {
        setUploadError('Upload cancelled');
      } else {
        const errorMessage = error instanceof Error ? error.message : 'Unknown error occurred';
        setUploadError(errorMessage);
        
        if (onUploadError) {
          onUploadError(errorMessage);
        }
      }
      
      return null;
    }
  }, [file, fileError, endpoint, additionalData, onUploadSuccess, onUploadError]);

  /**
   * Cancels an ongoing upload
   */
  const cancelUpload = useCallback(() => {
    if (isUploading && cancelTokenSource.current) {
      cancelTokenSource.current.cancel('Upload cancelled by user');
      setIsUploading(false);
      setUploadError('Upload cancelled');
    }
  }, [isUploading]);

  /**
   * Resets all file upload state values
   */
  const resetFileUpload = useCallback(() => {
    setFile(null);
    setFileError(null);
    setIsUploading(false);
    setUploadProgress(0);
    setUploadError(null);
    setUploadResult(null);
    
    // Reset the file input value
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  }, []);

  // Return the hook state and functions
  return {
    fileInputRef,
    file,
    fileError,
    isUploading,
    uploadProgress,
    uploadError,
    uploadResult,
    handleFileChange,
    handleFileDrop,
    uploadFile,
    cancelUpload,
    resetFileUpload
  };
}