import React, { useState, useEffect, useCallback } from 'react'; //  ^18.0.0
import { TextField } from '../common/TextField';
import { Select } from '../common/Select';
import { Button } from '../common/Button';
import { Alert } from '../common/Alert';
import { useAppDispatch, useAppSelector } from '../../store';
import { testConnection, saveAPIConfiguration } from '../../store/integrations/integrationsThunks';
import { selectIntegrationStatus } from '../../store/integrations/integrationsSlice';
import { IntegrationSystemType, APIConfigurationType, AuthType } from '../../types/integration';

/**
 * Interface defining the props for the APIConfigurationPanel component
 */
interface APIConfigurationPanelProps {
  initialConfig?: APIConfigurationType;
  integrationType: IntegrationSystemType;
  onConfigurationSaved: () => void;
}

/**
 * A panel component for configuring API connection details for external system integrations
 */
const APIConfigurationPanel: React.FC<APIConfigurationPanelProps> = ({
  initialConfig,
  integrationType,
  onConfigurationSaved,
}) => {
  // Initialize state for the API configuration
  const [config, setConfig] = useState<APIConfigurationType>({
    apiUrl: '',
    authType: 'api_key',
    credentials: {
      apiKey: '',
    },
  });

  // Initialize state for testing connection
  const [isTestingConnection, setIsTestingConnection] = useState(false);
  const [testConnectionResult, setTestConnectionResult] = useState<{ success: boolean; message: string } | null>(null);

  // Get Redux dispatch and selector hooks
  const dispatch = useAppDispatch();
  const { loading, error } = useAppSelector(selectIntegrationStatus);

  // Initialize form with initialConfig when provided
  useEffect(() => {
    if (initialConfig) {
      setConfig(initialConfig);
    }
  }, [initialConfig]);

  /**
   * Handles changes to input fields in the form
   * @param {string} field - The name of the field being changed
   * @param {any} value - The new value of the field
   * @returns {void} No return value
   */
  const handleInputChange = useCallback((field: string, value: any) => {
    setConfig((prevConfig) => ({
      ...prevConfig,
      [field]: value,
    }));
  }, []);

  /**
   * Handles changes to the authentication type selection
   * @param {AuthType} authType - The new authentication type
   * @returns {void} No return value
   */
  const handleAuthTypeChange = useCallback((authType: AuthType) => {
    setConfig((prevConfig) => ({
      ...prevConfig,
      authType: authType,
      credentials: {}, // Reset credentials when auth type changes
    }));
  }, []);

  /**
   * Initiates a test connection to verify the API configuration
   * @returns {void} No return value
   */
  const handleTestConnection = useCallback(async () => {
    setIsTestingConnection(true);
    setTestConnectionResult(null); // Clear previous test results

    try {
      const result = await dispatch(testConnection({
        type: integrationType,
        configuration: config,
      })).unwrap();

      setTestConnectionResult({ success: true, message: result.message });
    } catch (err: any) {
      setTestConnectionResult({ success: false, message: err.message || 'Connection test failed' });
    } finally {
      setIsTestingConnection(false);
    }
  }, [dispatch, config, integrationType]);

  /**
   * Saves the API configuration
   * @returns {void} No return value
   */
  const handleSaveConfiguration = useCallback(async () => {
    // Basic validation
    if (!config.apiUrl) {
      setTestConnectionResult({ success: false, message: 'API URL is required' });
      return;
    }

    try {
      await dispatch(saveAPIConfiguration(config)).unwrap();
      onConfigurationSaved();
    } catch (err: any) {
      setTestConnectionResult({ success: false, message: err.message || 'Failed to save configuration' });
    }
  }, [dispatch, config, onConfigurationSaved]);

  // Define authentication options for the Select component
  const authOptions = [
    { value: 'api_key', label: 'API Key' },
    { value: 'oauth', label: 'OAuth 2.0' },
    { value: 'basic', label: 'Basic Auth' },
  ];

  return (
    <div>
      {/* API URL Input */}
      <TextField
        label="API URL"
        name="apiUrl"
        value={config.apiUrl}
        onChange={(e) => handleInputChange('apiUrl', e.target.value)}
        required
        fullWidth
      />

      {/* Authentication Type Select */}
      <Select
        label="Authentication Type"
        name="authType"
        value={config.authType}
        onChange={(value) => handleAuthTypeChange(value as AuthType)}
        options={authOptions}
        required
        fullWidth
      />

      {/* Conditional rendering of credential fields based on auth type */}
      {config.authType === 'api_key' && (
        <TextField
          label="API Key"
          name="apiKey"
          value={config.credentials?.apiKey || ''}
          onChange={(e) => handleInputChange('credentials', { ...config.credentials, apiKey: e.target.value })}
          required
          fullWidth
        />
      )}

      {config.authType === 'oauth' && (
        <>
          <TextField
            label="Client ID"
            name="clientId"
            value={config.credentials?.clientId || ''}
            onChange={(e) => handleInputChange('credentials', { ...config.credentials, clientId: e.target.value })}
            required
            fullWidth
          />
          <TextField
            label="Client Secret"
            name="clientSecret"
            type="password"
            value={config.credentials?.clientSecret || ''}
            onChange={(e) => handleInputChange('credentials', { ...config.credentials, clientSecret: e.target.value })}
            required
            fullWidth
          />
        </>
      )}

      {config.authType === 'basic' && (
        <>
          <TextField
            label="Username"
            name="username"
            value={config.credentials?.username || ''}
            onChange={(e) => handleInputChange('credentials', { ...config.credentials, username: e.target.value })}
            required
            fullWidth
          />
          <TextField
            label="Password"
            name="password"
            type="password"
            value={config.credentials?.password || ''}
            onChange={(e) => handleInputChange('credentials', { ...config.credentials, password: e.target.value })}
            required
            fullWidth
          />
        </>
      )}

      {/* Test Connection Button */}
      <Button
        onClick={handleTestConnection}
        disabled={isTestingConnection || loading}
      >
        {isTestingConnection ? 'Testing...' : 'Test Connection'}
      </Button>

      {/* Test Connection Result Alert */}
      {testConnectionResult && (
        <Alert
          severity={testConnectionResult.success ? 'success' : 'error'}
          message={testConnectionResult.message}
        />
      )}

      {/* Save Configuration Button */}
      <Button
        onClick={handleSaveConfiguration}
        disabled={loading}
      >
        {loading ? 'Saving...' : 'Save Configuration'}
      </Button>
    </div>
  );
};

export default APIConfigurationPanel;