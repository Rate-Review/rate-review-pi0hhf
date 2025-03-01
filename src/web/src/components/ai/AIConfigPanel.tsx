import React, { useState, useEffect, useCallback } from 'react'; //  ^18.0.0
import { useDispatch, useSelector } from 'react-redux'; //  ^8.1.1

import { RootState } from '../../store';
import { updateAIConfig, resetAIConfig } from '../../store/ai/aiThunks';
import {
  AIEnvironment,
  AIModel,
  AIFunction,
  AIConfiguration,
} from '../../types/ai';
import { Card, CardHeader, CardContent, CardFooter } from '../common/Card';
import { Select } from '../common/Select';
import { Button } from '../common/Button';
import { Checkbox } from '../common/Checkbox';
import { Alert } from '../common/Alert';
import { usePermissions } from '../../hooks/usePermissions';

/**
 * @interface AIConfigPanelProps
 * @description Props for the AIConfigPanel component
 */
interface AIConfigPanelProps {
  title?: string;
  onSave?: (config: AIConfiguration) => void;
}

/**
 * @component AIConfigPanel
 * @description A configuration panel for AI settings in the Justice Bid system
 */
const AIConfigPanel: React.FC<AIConfigPanelProps> = ({ title, onSave }) => {
  // LD1: Initialize state variables
  const [config, setConfig] = useState<AIConfiguration>({
    environment: AIEnvironment.JUSTICE_BID,
    model: AIModel.GPT_4,
    organizationId: '',
    dataAccess: {},
    personalizationEnabled: false,
  });
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);

  // LD1: Select the current AI configuration from Redux store
  const aiConfigFromStore = useSelector((state: RootState) => state.ai.config);

  // LD1: Dispatch actions to update AI configuration
  const dispatch = useDispatch();

    // LD1: Use the usePermissions hook to check if the user has permission to modify AI settings
  const { can } = usePermissions();
  const canModifyAIConfig = can('update', 'ai', 'organization');

  // LD1: Initialize local config state when Redux store data changes
  useEffect(() => {
    if (aiConfigFromStore) {
      setConfig(aiConfigFromStore);
    }
  }, [aiConfigFromStore]);

  /**
   * @function handleEnvironmentChange
   * @description Handles changes to the AI environment selection
   * @param {React.ChangeEvent<HTMLSelectElement>} event - The change event
   * @returns {void}
   */
  const handleEnvironmentChange = (event: React.ChangeEvent<HTMLSelectElement>): void => {
    const selectedEnvironment = event.target.value as AIEnvironment;
    setConfig((prevConfig) => ({
      ...prevConfig,
      environment: selectedEnvironment,
    }));
    setSuccessMessage(null);
  };

  /**
   * @function handleModelChange
   * @description Handles changes to AI model selection for specific functions
   * @param {AIFunction} functionType - The AI function type
   * @param {AIModel} model - The selected AI model
   * @returns {void}
   */
  const handleModelChange = (functionType: AIFunction, model: AIModel): void => {
    setConfig((prevConfig) => ({
      ...prevConfig,
      model: model,
    }));
    setSuccessMessage(null);
  };

  /**
   * @function handleDataAccessChange
   * @description Handles changes to data access permissions
   * @param {string} dataType - The data type being accessed
   * @param {boolean} checked - Whether access is granted
   * @returns {void}
   */
  const handleDataAccessChange = (dataType: string, checked: boolean): void => {
    setConfig((prevConfig) => ({
      ...prevConfig,
      dataAccess: {
        ...prevConfig.dataAccess,
        [dataType]: checked,
      },
    }));
    setSuccessMessage(null);
  };

  /**
   * @function handlePersonalizationChange
   * @description Handles changes to personalization settings
   * @param {string} setting - The personalization setting being changed
   * @param {boolean} checked - Whether the setting is enabled
   * @returns {void}
   */
  const handlePersonalizationChange = (setting: string, checked: boolean): void => {
    setConfig((prevConfig) => ({
      ...prevConfig,
      personalizationEnabled: checked,
    }));
    setSuccessMessage(null);
  };

  /**
   * @function handleSave
   * @description Saves the current AI configuration
   * @returns {void}
   */
  const handleSave = useCallback(async (): Promise<void> => {
    setIsLoading(true);
    setError(null);
    try {
      await dispatch(updateAIConfig(config)).unwrap();
      setSuccessMessage('AI configuration saved successfully!');
      setIsLoading(false);
      onSave?.(config);
    } catch (err: any) {
      setError(err.message || 'Failed to save AI configuration.');
      setIsLoading(false);
    }
  }, [config, dispatch, onSave]);

  /**
   * @function handleReset
   * @description Resets AI configuration to system defaults
   * @returns {void}
   */
  const handleReset = useCallback(async (): Promise<void> => {
    setIsLoading(true);
    setError(null);
    try {
      const defaultConfig = await dispatch(resetAIConfig()).unwrap();
      setConfig(defaultConfig);
      setSuccessMessage('AI configuration reset to defaults!');
      setIsLoading(false);
    } catch (err: any) {
      setError(err.message || 'Failed to reset AI configuration.');
      setIsLoading(false);
    }
  }, [dispatch]);

  // LD1: Render the AI configuration panel
  return (
    <Card>
      <CardHeader title={title || 'AI Configuration'} />
      <CardContent>
        {error && <Alert severity="error" message={error} />}
        {successMessage && <Alert severity="success" message={successMessage} />}

        {/* Environment Selection */}
        <div>
          <Select
            label="AI Environment"
            name="aiEnvironment"
            value={config.environment}
            onChange={handleEnvironmentChange}
            options={[
              { value: AIEnvironment.JUSTICE_BID, label: 'Justice Bid' },
              { value: AIEnvironment.CLIENT, label: 'Client' },
            ]}
            disabled={!canModifyAIConfig}
          />
        </div>

        {/* Model Selection */}
        <div>
          <Select
            label="Model"
            name="aiModel"
            value={config.model}
            onChange={(value) => handleModelChange(AIFunction.CHAT, value as AIModel)}
            options={[
              { value: AIModel.GPT_4, label: 'GPT-4' },
            ]}
            disabled={!canModifyAIConfig}
          />
        </div>

        {/* Data Access Control */}
        <div>
          <h3>Data Access Control</h3>
          <Checkbox
            label="Access to Rate Data"
            name="rateDataAccess"
            checked={!!config.dataAccess?.rateData}
            onChange={(checked) => handleDataAccessChange('rateData', checked)}
            disabled={!canModifyAIConfig}
          />
        </div>

        {/* Personalization Settings */}
        <div>
          <h3>Personalization Settings</h3>
          <Checkbox
            label="Enable AI Personalization"
            name="aiPersonalization"
            checked={!!config.personalizationEnabled}
            onChange={handlePersonalizationChange}
            disabled={!canModifyAIConfig}
          />
        </div>
      </CardContent>
      <CardFooter>
      {canModifyAIConfig && (
        <>
          <Button variant="secondary" onClick={handleReset} disabled={isLoading}>
            Reset to Defaults
          </Button>
          <Button onClick={handleSave} disabled={isLoading}>
            Save
          </Button>
        </>
      )}
      </CardFooter>
    </Card>
  );
};

export default AIConfigPanel;