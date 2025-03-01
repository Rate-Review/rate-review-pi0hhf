import React, { useState, useCallback, useMemo } from 'react'; //  ^18.0.0
import { useFileUpload } from '../../hooks/useFileUpload';
import { useRates } from '../../hooks/useRates';
import { FileUpload } from '../common/FileUpload';
import { Button } from '../common/Button';
import { Alert } from '../common/Alert';
import { ProgressBar } from '../common/ProgressBar';
import { Tabs } from '../common/Tabs';
import { FieldMappingInterface } from '../integration/FieldMappingInterface';
import { validateRateImport } from '../../utils/validation';
import { parseFileData } from '../../utils/file';
import { RATE_IMPORT_REQUIRED_FIELDS, RATE_IMPORT_TEMPLATES } from '../../constants/rates';
import { RateImportFormProps, RateImportData, RateFieldMapping } from '../../types/rate';

/**
 * A form component that allows users to import rate data from Excel or CSV files, with functionality for file selection, validation, field mapping, and submission.
 */
const RateImportForm: React.FC<RateImportFormProps> = ({
  organizationId,
  onImportComplete,
}) => {
  // LD1: Initialize component state for file upload, validation, field mapping, and import steps
  const [file, setFile] = useState<File | null>(null);
  const [parsedData, setParsedData] = useState<RateImportData[] | null>(null);
  const [validationErrors, setValidationErrors] = useState<string[] | null>(null);
  const [fieldMapping, setFieldMapping] = useState<RateFieldMapping | null>(null);
  const [importResult, setImportResult] = useState<string | null>(null);
  const [currentStep, setCurrentStep] = useState<'upload' | 'mapping' | 'confirm' | 'result'>('upload');
  const [isSubmitting, setIsSubmitting] = useState(false);

  // LD1: Use custom hooks for file upload and rate operations
  const { uploadFile, fileState } = useFileUpload({
    acceptedFileTypes: ['.xlsx', '.csv'],
    maxFileSizeMB: 5,
    endpoint: '/api/rates/import', // Replace with your actual API endpoint
    onUploadSuccess: (result) => {
      setImportResult('Rates imported successfully!');
      if (onImportComplete) {
        onImportComplete();
      }
    },
    onUploadError: (error) => {
      setValidationErrors([error]);
    },
  });
  const { importRates } = useRates();

  // LD1: Define available steps for the import process
  const steps = useMemo(() => [
    { id: 'upload', label: 'Upload File' },
    { id: 'mapping', label: 'Map Fields' },
    { id: 'confirm', label: 'Confirm Import' },
    { id: 'result', label: 'Import Result' },
  ], []);

  // LD1: Define function for handling file selection event from the FileUpload component
  const handleFileChange = (file: File) => {
    // LD1: Update file state with the selected file
    setFile(file);

    // LD1: Reset any previous validation errors and parsed data
    setValidationErrors(null);
    setParsedData(null);

    // LD1: Parse the file data based on file type (Excel/CSV)
    parseFileData(file)
      .then((data: RateImportData[]) => {
        // LD1: Validate the parsed data structure and required fields
        const errors = validateRateImport(data, RATE_IMPORT_REQUIRED_FIELDS);
        if (errors.length > 0) {
          setValidationErrors(errors);
        } else {
          // LD1: Update component state with parsed data and any validation errors
          setParsedData(data);
          // LD1: Advance to the next step if validation is successful
          setCurrentStep('mapping');
        }
      })
      .catch((error: any) => {
        setValidationErrors([error.message]);
      });
  };

  // LD1: Define function for handling field mapping changes from the FieldMappingInterface component
  const handleFieldMapping = (mapping: RateFieldMapping) => {
    // LD1: Update the fieldMapping state with the new mapping
    setFieldMapping(mapping);

    // LD1: Transform the parsed data based on the new field mapping
    // LD1: Validate the transformed data for any issues
    // LD1: Update validation errors state if any issues are found
  };

  // LD1: Define function for handling the import submission process
  const handleImport = async () => {
    // LD1: Set isSubmitting state to true to show progress indicator
    setIsSubmitting(true);

    try {
      // LD1: Transform the data based on current field mapping
      const transformedData = parsedData?.map((item) => ({
        // Apply field mapping here
        ...item,
      }));

      if (transformedData) {
        // LD1: Call importRates function with the transformed data and organizationId
        await importRates(transformedData);
        // LD1: Handle successful import by updating importResult state
        setImportResult('Rates imported successfully!');
        if (onImportComplete) {
          onImportComplete();
        }
      }
    } catch (error: any) {
      // LD1: Handle import errors by updating validationErrors state
      setValidationErrors([error.message]);
    } finally {
      // LD1: Set isSubmitting state to false when complete
      setIsSubmitting(false);
      // LD1: Advance to the final step showing the import result
      setCurrentStep('result');
    }
  };

  // LD1: Define function for resetting the form state to start a new import
  const handleReset = () => {
    // LD1: Reset all state variables to their initial values
    setFile(null);
    setParsedData(null);
    setValidationErrors(null);
    setFieldMapping(null);
    setImportResult(null);
    setIsSubmitting(false);

    // LD1: Return to the first step of the import process
    setCurrentStep('upload');
  };

  // LD1: Define function for downloading template files for Excel and CSV formats
  const downloadTemplate = (format: string) => {
    // LD1: Get the template URL from RATE_IMPORT_TEMPLATES for the specified format
    const templateURL = RATE_IMPORT_TEMPLATES[format];

    // LD1: Create a link element to trigger the download
    const link = document.createElement('a');

    // LD1: Set the link's href attribute to the template URL
    link.href = templateURL;

    // LD1: Set the download attribute with an appropriate filename
    link.download = `rate_import_template.${format}`;

    // LD1: Trigger the click event on the link
    link.click();

    // LD1: Remove the link element from the DOM
    link.remove();
  };

  // LD1: Define function for rendering the appropriate step content based on the current step
  const renderStep = () => {
    switch (currentStep) {
      // LD1: Render file selection step with FileUpload component when in 'upload' step
      case 'upload':
        return (
          <div>
            <FileUpload
              accept=".xlsx, .csv"
              onUpload={handleFileChange}
              onError={setValidationErrors}
              uploadUrl="/api/rates/import" // Replace with your actual API endpoint
            />
            {validationErrors && (
              <Alert
                severity="error"
                message={validationErrors.join('\n')}
                onClose={() => setValidationErrors(null)}
              />
            )}
            <div>
              <Button onClick={() => downloadTemplate('xlsx')}>
                Download Excel Template
              </Button>
              <Button onClick={() => downloadTemplate('csv')}>
                Download CSV Template
              </Button>
            </div>
          </div>
        );

      // LD1: Render field mapping step with FieldMappingInterface when in 'mapping' step
      case 'mapping':
        return (
          <FieldMappingInterface
            integrationId={organizationId}
            integrationType="file"
            sourceFields={[]} // Replace with your actual source fields
            targetFields={[]} // Replace with your actual target fields
            onSave={() => setCurrentStep('confirm')}
            onCancel={() => setCurrentStep('upload')}
          />
        );

      // LD1: Render confirmation step with summary and import button when in 'confirm' step
      case 'confirm':
        return (
          <div>
            {/* Display summary of data to be imported */}
            <Button onClick={handleImport} disabled={isSubmitting}>
              {isSubmitting ? 'Importing...' : 'Import'}
            </Button>
          </div>
        );

      // LD1: Render result step with success message or errors when in 'result' step
      case 'result':
        return (
          <div>
            {importResult && <Alert severity="success" message={importResult} />}
            {validationErrors && (
              <Alert
                severity="error"
                message={validationErrors.join('\n')}
                onClose={() => setValidationErrors(null)}
              />
            )}
            <Button onClick={handleReset}>Import Another File</Button>
          </div>
        );

      default:
        return null;
    }
  };

  return (
    <div>
      <Tabs
        tabs={steps}
        activeTab={currentStep}
        onChange={(stepId) => setCurrentStep(stepId as 'upload' | 'mapping' | 'confirm' | 'result')}
      />
      {renderStep()}
    </div>
  );
};

export default RateImportForm;