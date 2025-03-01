import React, { useState, useEffect, useCallback } from 'react'; //  ^18.0.0
import { useNavigate } from 'react-router-dom'; //  ^6.0+
import { useDispatch, useSelector } from 'react-redux'; //  ^8.0+
import {
  Box,
  Grid,
  Paper,
  Typography,
  Stepper,
  Step,
  StepLabel,
  CircularProgress,
  Divider,
  RadioGroup,
  Radio,
  FormControlLabel,
  FormControl,
  FormLabel,
} from '@mui/material'; //  ^5.14+
import { TextField } from '../common/TextField';
import { Select } from '../common/Select';
import { Button } from '../common/Button';
import { Alert } from '../common/Alert';
import { APIConfigurationPanel } from '../integration/APIConfigurationPanel';
import { FieldMappingInterface } from '../integration/FieldMappingInterface';
import { TestConnectionPanel } from '../integration/TestConnectionPanel';
import { SyncConfigurationPanel } from '../integration/SyncConfigurationPanel';
import {
  IntegrationType,
  IntegrationConfig,
  AuthMethodType,
  SyncFrequency,
  ErrorHandling,
  FieldMapping,
} from '../../types/integration';
import { RootState } from '../../store';
import {
  saveIntegrationConfig,
  testConnection,
  fetchFieldMetadata,
  fetchIntegrationById,
} from '../../store/integrations/integrationsThunks';
import {
  selectIntegrationLoading,
  selectIntegrationError,
} from '../../store/integrations/integrationsSlice';

// Define the props for the IntegrationForm component
interface IntegrationFormProps {
  integrationId?: string;
}

/**
 * A comprehensive React functional component that renders a step-by-step form for configuring and managing integrations with external systems such as eBilling platforms, law firm billing systems, and UniCourt. It guides users through basic configuration, API settings, field mapping, and synchronization configuration.
 * @param {IntegrationFormProps} props - props (containing integrationId?: string)
 */
export const IntegrationForm: React.FC<IntegrationFormProps> = ({ integrationId }) => {
  // Define state variables for managing the form
  const [activeStep, setActiveStep] = useState(0);
  const [formData, setFormData] = useState<Partial<IntegrationConfig>>({
    type: IntegrationType.EBILLING,
    name: '',
    description: '',
    configuration: {
      authMethod: AuthMethodType.API_KEY,
    },
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);
  const [testing, setTesting] = useState(false);

  // Get Redux dispatch and selector hooks
  const dispatch = useDispatch();
  const navigate = useNavigate();
  const integrationLoading = useSelector((state: RootState) => selectIntegrationLoading(state));
  const integrationError = useSelector((state: RootState) => selectIntegrationError(state));

  // Load existing integration configuration if editing
  useEffect(() => {
    if (integrationId) {
      setLoading(true);
      dispatch(fetchIntegrationById(integrationId))
        .unwrap()
        .then((integration) => {
          setFormData(integration);
        })
        .catch((err) => {
          setError(err.message || 'Failed to load integration');
        })
        .finally(() => {
          setLoading(false);
        });
    }
  }, [dispatch, integrationId]);

  /**
   * Validates the integration form data based on the current step
   * @param {IntegrationConfig} formData
   * @param {number} currentStep
   * @returns {object} Validation result with isValid boolean and error message
   */
  const validateForm = (formData: Partial<IntegrationConfig>, currentStep: number) => {
    // Check if required fields are filled based on the current step
    if (currentStep === 0) {
      if (!formData.type || !formData.name) {
        return { isValid: false, message: 'Integration type and name are required' };
      }
    }
    return { isValid: true, message: null };
  };

  /**
   * Handles navigation to the next step in the integration setup process
   */
  const handleNext = () => {
    // Validate the current step
    const validationResult = validateForm(formData, activeStep);
    if (validationResult.isValid) {
      // Increment the active step
      setActiveStep((prevActiveStep) => prevActiveStep + 1);
    } else {
      // Set error state with appropriate message
      setError(validationResult.message || 'Please fill in all required fields');
    }
  };

  /**
   * Handles navigation to the previous step in the integration setup process
   */
  const handleBack = () => {
    setActiveStep((prevActiveStep) => prevActiveStep - 1);
    setError(null);
  };

  /**
   * Handles the submission of the integration configuration
   */
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setSuccess(false);

    try {
      // Dispatch the saveIntegrationConfig thunk with the form data
      await dispatch(saveIntegrationConfig(formData)).unwrap();

      // Handle successful submission
      setSuccess(true);
      navigate('/integrations');
    } catch (err: any) {
      // Handle errors
      setError(err.message || 'Failed to save integration');
    } finally {
      // Set loading state to false
      setLoading(false);
    }
  };

  /**
   * Handles cancellation of the integration setup process
   */
  const handleCancel = () => {
    navigate('/integrations');
  };

  /**
   * Handles changes to the integration type selection
   * @param {string} type
   */
  const handleIntegrationTypeChange = (type: string) => {
    setFormData({
      ...formData,
      type: type as IntegrationType,
      configuration: {
        authMethod: AuthMethodType.API_KEY,
      },
    });
    setError(null);
  };

  /**
   * Handles changes to the specific system selection
   * @param {string} system
   */
  const handleSystemChange = (system: string) => {
    setFormData({
      ...formData,
      configuration: {
        ...formData.configuration,
        system,
      },
    });
    setError(null);
  };

  /**
   * Handles changes to the authentication method selection
   * @param {string} method
   */
  const handleAuthMethodChange = (method: string) => {
    setFormData({
      ...formData,
      configuration: {
        ...formData.configuration,
        authMethod: method as AuthMethodType,
      },
    });
    setError(null);
  };

  /**
   * Handles changes to form input fields
   * @param {string} field
   * @param {any} value
   */
  const handleInputChange = (field: string, value: any) => {
    setFormData({
      ...formData,
      [field]: value,
    });
    setError(null);
  };

  /**
   * Handles the test connection action
   */
  const handleTestConnection = async () => {
    setTesting(true);
    setError(null);

    try {
      // Dispatch the testConnection thunk with the form data
      await dispatch(testConnection({
        type: formData.type as IntegrationType,
        configuration: formData.configuration,
      })).unwrap();
    } catch (err: any) {
      // Handle errors
      setError(err.message || 'Connection test failed');
    } finally {
      // Set testing state to false
      setTesting(false);
    }
  };

  /**
   * Renders the content for the current step in the integration setup process
   * @param {number} step
   * @returns {JSX.Element} The rendered step content
   */
  const renderStepContent = (step: number) => {
    switch (step) {
      case 0:
        return (
          <>
            <TextField
              label="Integration Name"
              name="name"
              value={formData.name || ''}
              onChange={(e) => handleInputChange('name', e.target.value)}
              required
              fullWidth
            />
            <Select
              label="Integration Type"
              name="type"
              value={formData.type || ''}
              onChange={handleIntegrationTypeChange}
              options={[
                { value: IntegrationType.EBILLING, label: 'eBilling System' },
                { value: IntegrationType.LAWFIRM, label: 'Law Firm Billing System' },
                { value: IntegrationType.UNICOURT, label: 'UniCourt' },
              ]}
              required
              fullWidth
            />
          </>
        );
      case 1:
        return (
          <APIConfigurationPanel
            integrationType={formData.type as IntegrationType}
            initialConfig={formData.configuration}
            onConfigurationSaved={() => {
              console.log('API Configuration Saved');
            }}
          />
        );
      case 2:
        return (
          <FieldMappingInterface
            integrationId={integrationId || ''}
            integrationType={formData.type as IntegrationType}
            sourceFields={[]}
            targetFields={[]}
          />
        );
      case 3:
        return (
          <SyncConfigurationPanel
            integrationType={formData.type as IntegrationType}
            integrationId={integrationId || ''}
            onSaveComplete={() => {
              console.log('Sync Configuration Saved');
            }}
          />
        );
      default:
        return <div>Unknown step</div>;
    }
  };

  return (
    <Box sx={{ width: '100%' }}>
      <Stepper activeStep={activeStep} alternativeLabel>
        {[
          'Basic Configuration',
          'API Configuration',
          'Field Mapping',
          'Sync Configuration',
        ].map((label) => (
          <Step key={label}>
            <StepLabel>{label}</StepLabel>
          </Step>
        ))}
      </Stepper>
      <Box sx={{ mt: 2 }}>
        {renderStepContent(activeStep)}
        <Divider sx={{ my: 2 }} />
        <Box sx={{ display: 'flex', flexDirection: 'row', pt: 2 }}>
          <Button
            color="inherit"
            disabled={activeStep === 0}
            onClick={handleBack}
            sx={{ mr: 1 }}
          >
            Back
          </Button>
          <Box sx={{ flex: '1 1 auto' }} />
          {activeStep === 3 ? (
            <Button type="submit" onClick={handleSubmit} disabled={loading}>
              {loading ? 'Submitting...' : 'Submit'}
            </Button>
          ) : (
            <Button onClick={handleNext} disabled={loading}>
              Next
            </Button>
          )}
          <Button onClick={handleCancel}>Cancel</Button>
        </Box>
      </Box>
    </Box>
  );
};