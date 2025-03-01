import React, { useState, useCallback, useEffect } from 'react'; //  ^18.2.0
import styled from 'styled-components'; //  ^5.3.6
import {
  Box,
  Grid,
  Typography,
  Paper,
  Step,
  Stepper,
  StepLabel,
} from '@mui/material'; //  ^5.14.0
import { useTranslation } from 'react-i18next'; //  ^12.0.0
import FileUpload from '../common/FileUpload';
import Button from '../common/Button';
import Alert from '../common/Alert';
import ProgressBar from '../common/ProgressBar';
import Select from '../common/Select';
import FieldMappingInterface from './FieldMappingInterface';
import useFileUpload from '../../hooks/useFileUpload';
import fileService from '../../services/file';
import {
  FileImportConfig,
  FileValidationResult,
  ImportOptions,
  FileType,
} from '../../types/integration';

const Container = styled(Box)`
  width: 100%;
  max-width: 800px;
  margin: 0 auto;
  padding: 20px;
`;

const StyledPaper = styled(Paper)`
  padding: 20px;
`;

const FileImportInterface: React.FC<{
  dataType?: string;
  onImportComplete?: () => void;
  initialConfig?: FileImportConfig;
}> = ({ dataType, onImportComplete, initialConfig }) => {
  // IE3: Using useTranslation hook to support internationalization
  const { t } = useTranslation();

  // LD1: Define state variables for managing the import process
  const [selectedFileType, setSelectedFileType] = useState<FileType | null>(
    initialConfig?.configuration?.fileType || null
  );
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [validationResult, setValidationResult] = useState<
    FileValidationResult | null
  >(null);
  const [fieldMappings, setFieldMappings] = useState<object | null>(null);
  const [previewData, setPreviewData] = useState<array | null>(null);
  const [importOptions, setImportOptions] = useState<ImportOptions>({});
  const [activeStep, setActiveStep] = useState<number>(0);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [progress, setProgress] = useState<number>(0);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  // LD1: Define file upload handlers using the useFileUpload hook
  const {
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
    resetFileUpload,
  } = useFileUpload({
    acceptedFileTypes: ['.xlsx', '.csv'],
    maxFileSizeMB: 10,
    endpoint: '/api/upload', // Replace with your actual upload endpoint
    onUploadSuccess: (result) => {
      console.log('Upload successful:', result);
    },
    onUploadError: (error) => {
      console.error('Upload error:', error);
    },
  });

  // LD1: Define handler for file selection
  const handleFileSelect = (file: File) => {
    setSelectedFile(file);
    setValidationResult(null);
    setError(null);

    // LD1: Call validateFile function from fileService to validate the file format
    fileService
      .validateFile(file)
      .then((result) => {
        setValidationResult(result);
        if (!result.valid) {
          setError(result.errors.join(', '));
        } else {
          setActiveStep(2); // Enable the next step (field mapping)
        }
      })
      .catch((err) => {
        setError(err.message);
      });
  };

  // LD1: Define handler for template download
  const handleTemplateDownload = async () => {
    if (!selectedFileType) {
      setError('Please select a file type first.');
      return;
    }

    try {
      // LD1: Call downloadTemplate function from fileService with the selected file type
      const templateBlob = await fileService.downloadTemplate(selectedFileType);
      const url = window.URL.createObjectURL(templateBlob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `template.${selectedFileType}`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      window.URL.revokeObjectURL(url);
    } catch (err) {
      setError(err.message);
    }
  };

  // LD1: Define handler for mapping completion
  const handleMappingComplete = (mappings: object) => {
    setFieldMappings(mappings);
    // LD1: Call previewData function from fileService with the file and mappings
    fileService
      .previewData(selectedFile, mappings)
      .then((data) => {
        setPreviewData(data);
        setActiveStep(4); // Enable the next step (import options)
      })
      .catch((err) => {
        setError(err.message);
      });
  };

  // LD1: Define handler for import submission
  const handleImportSubmit = async () => {
    if (!selectedFile || !fieldMappings) {
      setError('Please select a file and map the fields first.');
      return;
    }

    setIsLoading(true);
    setProgress(0);

    try {
      // LD1: Call importData function from fileService
      const importResult = await fileService.importData(
        selectedFile,
        fieldMappings,
        importOptions,
        (p) => setProgress(p)
      );

      setSuccess('Data imported successfully!');
      if (onImportComplete) {
        onImportComplete();
      }
      setActiveStep(0); // Reset the form
    } catch (err) {
      setError(err.message);
    } finally {
      setIsLoading(false);
      setProgress(0);
    }
  };

  // LD1: Define handler for file type change
  const handleFileTypeChange = (fileType: FileType) => {
    setSelectedFileType(fileType);
    setSelectedFile(null);
    setValidationResult(null);
    setFieldMappings(null);
  };

  // LD1: Define handler for import options change
  const handleImportOptionsChange = (options: ImportOptions) => {
    setImportOptions(options);
  };

  // LD1: Define steps for the import process
  const steps = [
    'Select File Type',
    'Upload File',
    'Map Fields',
    'Set Import Options',
    'Confirm Import',
  ];

  return (
    <Container>
      <Stepper activeStep={activeStep}>
        {steps.map((label, index) => (
          <Step key={label}>
            <StepLabel>{label}</StepLabel>
          </Step>
        ))}
      </Stepper>

      {activeStep === 0 && (
        <StyledPaper>
          <Typography variant="h6">Select File Type</Typography>
          <Select
            label="File Type"
            value={selectedFileType || ''}
            onChange={(value) => handleFileTypeChange(value as FileType)}
            options={[
              { label: 'Excel', value: FileType.EXCEL },
              { label: 'CSV', value: FileType.CSV },
            ]}
          />
          <Button onClick={handleTemplateDownload}>Download Template</Button>
        </StyledPaper>
      )}

      {activeStep === 1 && (
        <StyledPaper>
          <Typography variant="h6">Upload File</Typography>
          <FileUpload onFileSelect={handleFileSelect} />
          {validationResult && !validationResult.valid && (
            <Alert severity="error" message={validationResult.errors.join(', ')} />
          )}
        </StyledPaper>
      )}

      {activeStep === 2 && (
        <StyledPaper>
          <Typography variant="h6">Map Fields</Typography>
          <FieldMappingInterface
            sourceFields={[]} // Replace with your actual source fields
            targetFields={[]} // Replace with your actual target fields
            onMappingComplete={handleMappingComplete}
          />
        </StyledPaper>
      )}

      {activeStep === 3 && (
        <StyledPaper>
          <Typography variant="h6">Set Import Options</Typography>
          {/* Add import options form here */}
          <Button onClick={() => setActiveStep(4)}>Next</Button>
        </StyledPaper>
      )}

      {activeStep === 4 && (
        <StyledPaper>
          <Typography variant="h6">Confirm Import</Typography>
          {/* Display preview data and import options */}
          <Button onClick={handleImportSubmit}>Import</Button>
        </StyledPaper>
      )}

      {isLoading && <ProgressBar value={progress} />}
      {error && <Alert severity="error" message={error} />}
      {success && <Alert severity="success" message={success} />}
    </Container>
  );
};

export default FileImportInterface;