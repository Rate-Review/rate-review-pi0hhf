import React, { useState, useRef, useEffect } from 'react';
import styled from 'styled-components';
import { useFileUpload } from '../../hooks/useFileUpload';
import Button from './Button';
import ProgressBar from './ProgressBar';
import Alert from './Alert';

/**
 * Props interface for the FileUpload component
 */
interface FileUploadProps {
  /**
   * MIME types or file extensions to accept
   * @default '.xlsx,.csv,application/vnd.openxmlformats-officedocument.spreadsheetml.sheet,application/vnd.ms-excel,text/csv'
   */
  accept?: string;
  /**
   * Whether to allow multiple file uploads
   * @default false
   */
  multiple?: boolean;
  /**
   * Callback when upload completes successfully
   */
  onUpload?: (result: any) => void;
  /**
   * Callback when an error occurs
   */
  onError?: (error: string) => void;
  /**
   * API endpoint to upload files to
   */
  uploadUrl: string;
  /**
   * List of allowed file extensions (e.g., ['.xlsx', '.csv'])
   * @default ['.xlsx', '.csv', '.xls']
   */
  allowedExtensions?: string[];
  /**
   * Maximum file size in MB
   * @default 10
   */
  maxFileSizeMB?: number;
  /**
   * Whether to show the progress bar
   * @default true
   */
  showProgressBar?: boolean;
  /**
   * Custom text for the upload button
   * @default 'Select File'
   */
  buttonText?: string;
  /**
   * Custom text for the drag and drop area
   * @default 'Drag and drop files here or click to select files'
   */
  dragDropText?: string;
}

/**
 * A reusable file upload component that provides a user interface for uploading files to the system.
 * Supports various file types including Excel and CSV, provides drag and drop functionality,
 * and feedback on upload progress, validation, and errors.
 */
const FileUpload: React.FC<FileUploadProps> = ({
  accept = '.xlsx,.csv,application/vnd.openxmlformats-officedocument.spreadsheetml.sheet,application/vnd.ms-excel,text/csv',
  multiple = false,
  onUpload,
  onError,
  uploadUrl,
  allowedExtensions = ['.xlsx', '.csv', '.xls'],
  maxFileSizeMB = 10,
  showProgressBar = true,
  buttonText = 'Select File',
  dragDropText = 'Drag and drop files here or click to select files'
}) => {
  // State for drag-and-drop UI
  const [isDragging, setIsDragging] = useState<boolean>(false);
  
  // State for tracking selected files
  const [files, setFiles] = useState<File[]>([]);
  
  // State for tracking upload progress
  const [progress, setProgress] = useState<number>(0);
  
  // State for tracking errors
  const [error, setError] = useState<string | null>(null);
  
  // Reference to file input element
  const fileInputRef = useRef<HTMLInputElement>(null);

  /**
   * Handles file selection when files are chosen via the file input
   */
  const handleFileInputChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFiles = event.target.files;
    if (selectedFiles && selectedFiles.length > 0) {
      // Convert FileList to array and limit to single file if multiple is false
      const fileArray = multiple ? Array.from(selectedFiles) : [selectedFiles[0]];
      
      // Validate files
      const validationError = validateFiles(fileArray);
      if (validationError) {
        setError(validationError);
        if (onError) onError(validationError);
        return;
      }
      
      setFiles(fileArray);
      setError(null);
    }
  };

  /**
   * Validates files against allowed extensions and size limits
   */
  const validateFiles = (fileList: File[]): string | null => {
    // Validate file extensions
    const invalidFiles = fileList.filter(file => {
      const extension = '.' + file.name.split('.').pop()?.toLowerCase();
      return !allowedExtensions.map(ext => ext.toLowerCase()).includes(extension);
    });
    
    if (invalidFiles.length > 0) {
      return `Invalid file type(s). Allowed extensions: ${allowedExtensions.join(', ')}`;
    }
    
    // Validate file size
    const oversizedFiles = fileList.filter(file => file.size > maxFileSizeMB * 1024 * 1024);
    if (oversizedFiles.length > 0) {
      return `File size exceeds the maximum allowed size of ${maxFileSizeMB}MB`;
    }
    
    return null;
  };

  /**
   * Drag and drop event handlers
   */
  const handleDragEnter = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(true);
  };
  
  const handleDragOver = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(true);
  };
  
  const handleDragLeave = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);
  };
  
  const handleDrop = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);
    
    const droppedFiles = e.dataTransfer.files;
    if (droppedFiles && droppedFiles.length > 0) {
      // Convert FileList to array and limit to single file if multiple is false
      const fileArray = multiple ? Array.from(droppedFiles) : [droppedFiles[0]];
      
      // Validate files
      const validationError = validateFiles(fileArray);
      if (validationError) {
        setError(validationError);
        if (onError) onError(validationError);
        return;
      }
      
      setFiles(fileArray);
      setError(null);
    }
  };

  /**
   * Handles file upload process
   */
  const handleUpload = async () => {
    if (files.length === 0) {
      setError("Please select a file to upload");
      if (onError) onError("Please select a file to upload");
      return;
    }
    
    try {
      setProgress(0);
      
      const formData = new FormData();
      files.forEach((file, index) => {
        formData.append(multiple ? `file${index}` : 'file', file);
      });
      
      // Use the uploadFile function from the hook via API service
      const result = await uploadFile(uploadUrl, formData, (progressEvent) => {
        if (progressEvent.total) {
          const percentCompleted = Math.round((progressEvent.loaded * 100) / progressEvent.total);
          setProgress(percentCompleted);
        }
      });
      
      // Reset file input
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
      
      // Clear files and reset state
      setFiles([]);
      setError(null);
      
      // Call onUpload callback
      if (onUpload) {
        onUpload(result);
      }
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : "An error occurred during upload";
      setError(errorMessage);
      if (onError) {
        onError(errorMessage);
      }
    }
  };

  /**
   * Triggers the file input click to open file selection dialog
   */
  const handleSelectFile = () => {
    if (fileInputRef.current) {
      fileInputRef.current.click();
    }
  };

  /**
   * Cancels the upload process and resets state
   */
  const handleCancel = () => {
    setFiles([]);
    setProgress(0);
    setError(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  return (
    <Container>
      {/* Drag and drop area */}
      <DropZone
        onDragEnter={handleDragEnter}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        isDragging={isDragging}
        onClick={handleSelectFile}
        aria-label="File upload drop zone"
      >
        <DropZoneText>{dragDropText}</DropZoneText>
        
        {/* Hidden file input */}
        <input
          type="file"
          ref={fileInputRef}
          style={{ display: 'none' }}
          accept={accept}
          multiple={multiple}
          onChange={handleFileInputChange}
          aria-label="File input"
        />
        
        {/* File selection button */}
        <Button
          variant="primary"
          onClick={handleSelectFile}
        >
          {buttonText}
        </Button>
      </DropZone>
      
      {/* Selected file info */}
      {files.length > 0 && (
        <FileInfo>
          <FileList>
            <FileListHeader>
              Selected {files.length > 1 ? `Files (${files.length})` : 'File'}:
            </FileListHeader>
            <FileListContent>
              {files.map((file, index) => (
                <FileItem key={index}>
                  <FileName>{file.name}</FileName>
                  <FileSize>({formatFileSize(file.size)})</FileSize>
                </FileItem>
              ))}
            </FileListContent>
          </FileList>
          
          <ButtonGroup>
            <Button
              variant="primary"
              onClick={handleUpload}
              disabled={progress > 0 && progress < 100}
            >
              Upload
            </Button>
            <Button
              variant="outline"
              onClick={handleCancel}
              disabled={progress > 0 && progress < 100}
            >
              Cancel
            </Button>
          </ButtonGroup>
        </FileInfo>
      )}
      
      {/* Progress indicator */}
      {showProgressBar && progress > 0 && (
        <ProgressBar
          value={progress}
          label="Upload Progress"
          variant="determinate"
          size="medium"
        />
      )}
      
      {/* Error message */}
      {error && (
        <Alert
          severity="error"
          message={error}
          onClose={() => setError(null)}
        />
      )}
      
      {/* Success message */}
      {progress === 100 && !error && (
        <Alert
          severity="success"
          message="File uploaded successfully!"
          onClose={() => setProgress(0)}
        />
      )}
    </Container>
  );
};

// Helper function to upload a file - uses the API service
const uploadFile = async (
  url: string,
  formData: FormData,
  onProgress?: (progressEvent: { loaded: number; total?: number }) => void
): Promise<any> => {
  const { api } = await import('../../services/api');
  return api.uploadFile(url, formData.get('file') as File, {}, onProgress);
};

// Helper function to format file size
const formatFileSize = (bytes: number): string => {
  if (bytes === 0) return '0 Bytes';
  
  const k = 1024;
  const sizes = ['Bytes', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
};

// Styled components
const Container = styled.div`
  margin: ${props => props.theme.spacing.md}px 0;
  width: 100%;
`;

const DropZone = styled.div<{ isDragging: boolean }>`
  border: 2px dashed ${props => props.isDragging 
    ? props.theme.colors.primary.main 
    : props.theme.colors.divider};
  border-radius: ${props => props.theme.spacing.sm}px;
  padding: ${props => props.theme.spacing.lg}px;
  text-align: center;
  transition: all 250ms ease-in-out;
  background-color: ${props => props.isDragging 
    ? 'rgba(74, 105, 162, 0.1)' 
    : 'transparent'};
  cursor: pointer;
`;

const DropZoneText = styled.p`
  margin-bottom: ${props => props.theme.spacing.md}px;
  color: ${props => props.theme.colors.text.secondary};
  font-family: ${props => props.theme.typography.fontFamily.primary};
`;

const FileInfo = styled.div`
  margin-top: ${props => props.theme.spacing.md}px;
  padding: ${props => props.theme.spacing.md}px;
  border: 1px solid ${props => props.theme.colors.divider};
  border-radius: ${props => props.theme.spacing.sm}px;
  background-color: ${props => props.theme.colors.background.light};
`;

const FileList = styled.div`
  margin-bottom: ${props => props.theme.spacing.md}px;
`;

const FileListHeader = styled.h4`
  font-family: ${props => props.theme.typography.fontFamily.primary};
  font-size: ${props => props.theme.typography.fontSize.md};
  font-weight: ${props => props.theme.typography.fontWeight.medium};
  margin-top: 0;
  margin-bottom: ${props => props.theme.spacing.sm}px;
`;

const FileListContent = styled.div`
  max-height: 200px;
  overflow-y: auto;
`;

const FileItem = styled.div`
  display: flex;
  align-items: center;
  padding: ${props => props.theme.spacing.sm}px;
  border-bottom: 1px solid ${props => props.theme.colors.divider};
  
  &:last-child {
    border-bottom: none;
  }
`;

const FileName = styled.span`
  font-family: ${props => props.theme.typography.fontFamily.primary};
  font-weight: ${props => props.theme.typography.fontWeight.medium};
  margin-right: ${props => props.theme.spacing.sm}px;
  word-break: break-word;
  flex-grow: 1;
`;

const FileSize = styled.span`
  font-family: ${props => props.theme.typography.fontFamily.primary};
  color: ${props => props.theme.colors.text.secondary};
  font-size: ${props => props.theme.typography.fontSize.sm};
  white-space: nowrap;
`;

const ButtonGroup = styled.div`
  display: flex;
  gap: ${props => props.theme.spacing.sm}px;
`;

export default FileUpload;