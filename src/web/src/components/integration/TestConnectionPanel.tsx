import React, { useState, useEffect, useCallback } from 'react'; //  ^18.0.0
import Button from '../common/Button';
import Alert from '../common/Alert';
import Spinner from '../common/Spinner';
import {
  Card,
  CardHeader,
  CardContent,
  CardFooter,
} from '../common/Card';
import TextField from '../common/TextField';
import {
  IntegrationType,
  AuthMethodType,
  TestConnectionRequest,
  ConnectionTestResult,
} from '../../types/integration';
import {
  testEBillingConnection,
  testLawFirmConnection,
  testUniCourtConnection,
} from '../../services/integrations';

/**
 * Interface defining the props for the TestConnectionPanel component.
 * @param integrationType - The type of integration to test (EBILLING, LAWFIRM, UNICOURT).
 * @param initialConfig - Initial configuration values for the connection.
 * @param onChange - Callback function when configuration changes.
 * @param onTestComplete - Callback function when test completes.
 * @param className - Additional CSS class names.
 */
interface TestConnectionPanelProps {
  integrationType: IntegrationType;
  initialConfig?: Partial<TestConnectionRequest>;
  onChange?: (config: TestConnectionRequest) => void;
  onTestComplete?: (result: ConnectionTestResult) => void;
  className?: string;
}

/**
 * Interface defining the structure for the connection configuration state.
 * @param apiUrl - API endpoint URL for the integration.
 * @param authMethod - Authentication method (API_KEY, OAUTH, BASIC).
 * @param apiKey - API key for API_KEY auth method.
 * @param clientId - Client ID for OAUTH auth method.
 * @param clientSecret - Client secret for OAUTH auth method.
 * @param username - Username for BASIC auth method.
 * @param password - Password for BASIC auth method.
 */
interface ConnectionConfig {
  apiUrl: string;
  authMethod: AuthMethodType;
  apiKey: string;
  clientId: string;
  clientSecret: string;
    username: string;
    password: string;
    systemType: string;
  additionalParams: Record<string, any>;
}

/**
 * A component that allows users to test connections to external systems.
 * @param props - The props for the component.
 * @returns A JSX element.
 */
export const TestConnectionPanel: React.FC<TestConnectionPanelProps> = ({
  integrationType,
  initialConfig,
  onChange,
  onTestComplete,
  className,
}) => {
  // Define the initial state for the connection configuration.
  const [config, setConfig] = useState<Partial<ConnectionConfig>>({
    apiUrl: '',
    authMethod: AuthMethodType.API_KEY,
    apiKey: '',
    clientId: '',
    clientSecret: '',
    username: '',
    password: '',
      systemType: '',
    additionalParams: {},
  });

  // Define the state for the test result, loading state, and error message.
  const [testResult, setTestResult] = useState<ConnectionTestResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Initialize the configuration from the initialConfig prop when the component mounts or when the prop changes.
  useEffect(() => {
    if (initialConfig) {
      setConfig(initialConfig.configuration);
    }
  }, [initialConfig]);

  /**
   * Handles changes to connection configuration inputs.
   * @param field - The name of the field that changed.
   * @param value - The new value of the field.
   */
  const handleConfigChange = useCallback((field: string, value: any) => {
    setConfig((prevConfig) => ({
      ...prevConfig,
      [field]: value,
    }));
    setTestResult(null);
    setError(null);
    if (onChange) {
      onChange({
        type: integrationType,
        configuration: {
          ...config,
          [field]: value,
        },
      });
    }
  }, [config, integrationType, onChange]);

  /**
   * Initiates a connection test based on the current configuration.
   */
  const handleTestConnection = async () => {
    setLoading(true);
    setError(null);

    try {
      if (!config) {
        throw new Error('Connection configuration is missing.');
      }

      let testFunction;
      switch (integrationType) {
        case IntegrationType.EBILLING:
          testFunction = testEBillingConnection;
          break;
        case IntegrationType.LAWFIRM:
          testFunction = testLawFirmConnection;
          break;
        case IntegrationType.UNICOURT:
          testFunction = testUniCourtConnection;
          break;
        default:
          throw new Error(`Unsupported integration type: ${integrationType}`);
      }

      const request: TestConnectionRequest = {
        type: integrationType,
        configuration: config,
      };

      const response = await testFunction(request);
      setTestResult(response);
      if (onTestComplete) {
        onTestComplete(response);
      }
    } catch (err: any) {
      setError(err.message || 'Failed to test connection.');
    } finally {
      setLoading(false);
    }
  };

  /**
   * Returns the appropriate label for the test button based on the integration type.
   * @returns The label for the test button.
   */
  const getTestButtonLabel = (): string => {
    switch (integrationType) {
      case IntegrationType.EBILLING:
        return 'Test eBilling Connection';
      case IntegrationType.LAWFIRM:
        return 'Test Law Firm Connection';
      case IntegrationType.UNICOURT:
        return 'Test UniCourt API';
      default:
        return 'Test Connection';
    }
  };

  /**
   * Renders the appropriate authentication method fields based on the selected auth method.
   * @returns A JSX element containing the authentication method fields.
   */
  const renderAuthMethodFields = (): JSX.Element | null => {
    switch (config?.authMethod) {
      case AuthMethodType.API_KEY:
        return (
          <div className="form-group">
            <TextField
              label="API Key"
              value={config.apiKey || ''}
              onChange={(value) => handleConfigChange('apiKey', value)}
              required
              fullWidth
            />
          </div>
        );
      case AuthMethodType.OAUTH:
        return (
          <>
            <div className="form-group">
              <TextField
                label="Client ID"
                value={config.clientId || ''}
                onChange={(value) => handleConfigChange('clientId', value)}
                required
                fullWidth
              />
            </div>
            <div className="form-group">
              <TextField
                label="Client Secret"
                type="password"
                value={config.clientSecret || ''}
                onChange={(value) => handleConfigChange('clientSecret', value)}
                required
                fullWidth
              />
            </div>
          </>
        );
      case AuthMethodType.BASIC:
        return (
          <>
            <div className="form-group">
              <TextField
                label="Username"
                value={config.username || ''}
                onChange={(value) => handleConfigChange('username', value)}
                required
                fullWidth
              />
            </div>
            <div className="form-group">
              <TextField
                label="Password"
                type="password"
                value={config.password || ''}
                onChange={(value) => handleConfigChange('password', value)}
                required
                fullWidth
              />
            </div>
          </>
        );
      default:
        return null;
    }
  };

  /**
   * Renders connection-specific fields based on the integration type.
   * @returns A JSX element containing the integration-specific fields.
   */
  const renderConnectionFields = (): JSX.Element | null => {
    switch (integrationType) {
      case IntegrationType.EBILLING:
      case IntegrationType.LAWFIRM:
        return (
          <div className="form-group">
            <TextField
              label="System Type"
              value={config.systemType || ''}
              onChange={(value) => handleConfigChange('systemType', value)}
              fullWidth
            />
          </div>
        );
      case IntegrationType.UNICOURT:
        return null;
      default:
        return null;
    }
  };

  return (
    <Card className={className}>
      <CardHeader title="Test Connection" />
      <CardContent>
        <div className="form-group">
          <TextField
            label="API URL"
            value={config.apiUrl || ''}
            onChange={(value) => handleConfigChange('apiUrl', value)}
            required
            fullWidth
          />
        </div>
        <div className="form-group">
          <label htmlFor="authMethod">Authentication Method</label>
          <select
            id="authMethod"
            value={config.authMethod || AuthMethodType.API_KEY}
            onChange={(e) => handleConfigChange('authMethod', e.target.value)}
          >
            <option value={AuthMethodType.API_KEY}>API Key</option>
            <option value={AuthMethodType.OAUTH}>OAuth 2.0</option>
            <option value={AuthMethodType.BASIC}>Basic Auth</option>
          </select>
        </div>
        {renderAuthMethodFields()}
        {renderConnectionFields()}
        <div className="test-result">
          {testResult && !error ? (
            <Alert
              severity={testResult.success ? 'success' : 'error'}
              message={testResult.message}
            />
          ) : null}
        </div>
        <div className="error">
          {error ? <Alert severity="error" message={error} /> : null}
        </div>
      </CardContent>
      <CardFooter>
        <Button onClick={handleTestConnection} disabled={loading} variant="primary">
          {loading ? <Spinner size="20px" color="white" /> : getTestButtonLabel()}
        </Button>
      </CardFooter>
    </Card>
  );
};