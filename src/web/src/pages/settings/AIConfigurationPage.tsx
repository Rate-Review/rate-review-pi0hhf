import React, { useState, useEffect, useCallback } from 'react'; // ^18.0.0
import {
  AIConfiguration,
  AIModel,
  AIEnvironment,
  AIFunctionType,
  AIPersonalizationSettings,
  DataAccessPermission,
  AIFeedback,
} from '../../../types/ai';
import {
  getAIConfiguration,
  updateAIConfiguration,
  resetAIPersonalization,
  submitAIFeedback,
} from '../../../services/ai';
import { useAI } from '../../../hooks/useAI';
import { usePermissions } from '../../../hooks/usePermissions';
import { PERMISSIONS } from '../../../constants/permissions';
import PageHeader from '../../../components/layout/PageHeader';
import Card from '../../../components/common/Card';
import Select from '../../../components/common/Select';
import Button from '../../../components/common/Button';
import Checkbox from '../../../components/common/Checkbox';
import Alert from '../../../components/common/Alert';
import Tabs from '../../../components/common/Tabs';
import Spinner from '../../../components/common/Spinner';
import Toast from '../../../components/common/Toast';
import ConfirmationDialog from '../../../components/common/ConfirmationDialog';
import AIFeedbackControls from '../../../components/ai/AIFeedbackControls';

/**
 * Main component for the AI Configuration page that allows organizations and users to customize their AI experience.
 * @returns {JSX.Element} The rendered AI configuration page
 */
const AIConfigurationPage: React.FC = () => {
  // LD1: Check if the user has permission to manage AI configuration
  const { can } = usePermissions();
  const hasManageAIConfigPermission = can(
    'update',
    'ai',
    'organization'
  );

  // LD1: Initialize state for AI configuration settings, loading status, error messages, and success messages
  const [aiConfig, setAiConfig] = useState<AIConfiguration | null>(null);
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);

  // LD1: Initialize state for confirmation dialog visibility
  const [confirmDialogOpen, setConfirmDialogOpen] = useState(false);

  // LD1: Initialize state for current active tab
  const [activeTab, setActiveTab] = useState('environment');

  // IE1: Use the useAI hook to access AI-related functions
  const { provideFeedback } = useAI();

  // LD1: Fetch current AI configuration on component mount
  useEffect(() => {
    fetchAIConfigurationData();
  }, []);

  /**
   * Fetches the current AI configuration from the server.
   * @returns {Promise<void>} A promise that resolves when the configuration is fetched
   */
  const fetchAIConfigurationData = useCallback(async () => {
    // LD1: Set loading state to true
    setLoading(true);
    setError(null);
    try {
      // LD1: Call the AI service to get the current configuration
      const config = await getAIConfiguration();
      // LD1: Update the configuration state with the fetched data
      setAiConfig(config);
    } catch (err: any) {
      // LD1: Handle any errors and display error messages
      setError(err.message || 'Failed to fetch AI configuration.');
    } finally {
      // LD1: Set loading state to false when complete
      setLoading(false);
    }
  }, []);

  /**
   * Handles saving the AI configuration changes.
   * @param {React.FormEvent} event
   * @returns {Promise<void>} A promise that resolves when the configuration is saved
   */
  const handleSaveConfiguration = useCallback(async (event: React.FormEvent) => {
    // LD1: Prevent default form submission behavior
    event.preventDefault();
    // LD1: Set saving state to true
    setSaving(true);
    setError(null);
    setSuccessMessage(null);

    try {
      // LD1: Validate the configuration settings
      if (!aiConfig) {
        throw new Error('No AI configuration to save.');
      }

      // LD1: Call the AI service to update the configuration
      await updateAIConfiguration(aiConfig);

      // LD1: Show success notification on successful update
      setSuccessMessage('AI configuration saved successfully!');
    } catch (err: any) {
      // LD1: Handle any errors and display error messages
      setError(err.message || 'Failed to save AI configuration.');
    } finally {
      // LD1: Set saving state to false when complete
      setSaving(false);
    }
  }, [aiConfig]);

  /**
   * Handles resetting AI personalization data.
   * @returns {Promise<void>} A promise that resolves when personalization is reset
   */
  const handleResetPersonalization = useCallback(async () => {
    // LD1: Set confirmation dialog state to visible
    setConfirmDialogOpen(true);
  }, []);

  /**
   * Handles the confirmation of resetting AI personalization data.
   * @returns {Promise<void>} A promise that resolves when personalization is reset
   */
  const handleConfirmReset = useCallback(async () => {
    setConfirmDialogOpen(false);
    setSaving(true);
    setError(null);
    setSuccessMessage(null);

    try {
      // LD1: If confirmed, call the AI service to reset personalization
      await resetAIPersonalization();

      // LD1: Show success notification on successful reset
      setSuccessMessage('AI personalization reset successfully!');
    } catch (err: any) {
      // LD1: Handle any errors and display error messages
      setError(err.message || 'Failed to reset AI personalization.');
    } finally {
      // LD1: Set saving state to false when complete
      setSaving(false);
    }
  }, []);

  /**
   * Handles the cancellation of resetting AI personalization data.
   * @returns {void} No return value
   */
  const handleCancelReset = useCallback(() => {
    setConfirmDialogOpen(false);
  }, []);

  /**
   * Handles changing the active configuration tab.
   * @param {string} tabId
   * @returns {void} No return value
   */
  const handleTabChange = useCallback((tabId: string) => {
    // LD1: Update the active tab state with the new tab ID
    setActiveTab(tabId);
  }, []);

  /**
   * Handles changes to the AI environment selection.
   * @param {React.ChangeEvent<HTMLSelectElement>} event
   * @returns {void} No return value
   */
  const handleEnvironmentChange = useCallback((event: React.ChangeEvent<HTMLSelectElement>) => {
    // LD1: Extract the new environment value from the event
    const newEnvironment = event.target.value as AIEnvironment;

    // LD1: Update the environment in the configuration state
    setAiConfig((prevConfig) =>
      prevConfig ? { ...prevConfig, environment: newEnvironment } : null
    );

    // LD1: Update any dependent settings based on the new environment
    // (e.g., available models, data access options)
  }, []);

  /**
   * Handles changes to AI model selections for different functions.
   * @param {AIFunctionType} functionType
   * @param {React.ChangeEvent<HTMLSelectElement>} event
   * @returns {void} No return value
   */
  const handleModelChange = useCallback(
    (functionType: AIFunctionType, event: React.ChangeEvent<HTMLSelectElement>) => {
      // LD1: Extract the new model value from the event
      const newModel = event.target.value as AIModel;

      // LD1: Update the model for the specified function type in the configuration state
      setAiConfig((prevConfig) => {
        if (!prevConfig) return null;
        return { ...prevConfig, model: newModel };
      });
    },
    []
  );

  /**
   * Handles changes to data access control settings.
   * @param {string} dataType
   * @param {DataAccessPermission} permission
   * @returns {void} No return value
   */
  const handleDataAccessChange = useCallback(
    (dataType: string, permission: DataAccessPermission) => {
      // LD1: Update the data access permission for the specified data type in the configuration state
      setAiConfig((prevConfig) => {
        if (!prevConfig) return null;
        return {
          ...prevConfig,
          dataAccess: { ...prevConfig.dataAccess, [dataType]: permission },
        };
      });
    },
    []
  );

  /**
   * Handles changes to personalization settings.
   * @param {string} settingKey
   * @param {boolean} enabled
   * @returns {void} No return value
   */
  const handlePersonalizationChange = useCallback(
    (settingKey: string, enabled: boolean) => {
      // LD1: Update the specified personalization setting in the configuration state
      setAiConfig((prevConfig) => {
        if (!prevConfig) return null;
        return {
          ...prevConfig,
          personalizationEnabled: enabled,
        };
      });
    },
    []
  );
  
  /**
   * Handles submitting feedback about AI performance.
   * @param {AIFeedback} feedback
   * @returns {Promise<void>} A promise that resolves when feedback is submitted
   */
  const handleFeedbackSubmit = useCallback(async (feedback: AIFeedback) => {
    setError(null);
    setSuccessMessage(null);
    try {
      // LD1: Call the AI service to submit feedback
      await submitAIFeedback(feedback);
      // LD1: Show success notification on successful submission
      setSuccessMessage('Feedback submitted successfully!');
    } catch (err: any) {
      // LD1: Handle any errors and display error messages
      setError(err.message || 'Failed to submit feedback.');
    }
  }, []);

  /**
   * Renders the environment selection section of the configuration form.
   * @returns {JSX.Element} The rendered environment section
   */
  const renderEnvironmentSection = useCallback(() => {
    return (
      <>
        <CardHeader title="AI Environment" />
        <CardContent>
          <p>
            Choose the environment for AI processing. You can use Justice Bid's
            AI environment or your own.
          </p>
          <Select
            label="Environment"
            name="environment"
            value={aiConfig?.environment || ''}
            onChange={handleEnvironmentChange}
            options={[
              { value: AIEnvironment.JUSTICE_BID, label: 'Justice Bid AI' },
              { value: AIEnvironment.CLIENT, label: 'Client AI' },
            ]}
          />
          {aiConfig?.environment === AIEnvironment.CLIENT && (
            <Alert severity="warning">
              Using your own AI environment requires additional configuration.
            </Alert>
          )}
        </CardContent>
      </>
    );
  }, [aiConfig, handleEnvironmentChange]);

  /**
   * Renders the model selection section of the configuration form.
   * @returns {JSX.Element} The rendered model section
   */
  const renderModelSection = useCallback(() => {
    return (
      <>
        <CardHeader title="AI Model Selection" />
        <CardContent>
          <p>
            Select the AI model to use for different functions. Different models
            have different capabilities and cost implications.
          </p>
          <Select
            label="Chat Model"
            name="chatModel"
            value={aiConfig?.model || ''}
            onChange={(event) => handleModelChange(AIFunctionType.CHAT, event)}
            options={[
              { value: AIModel.GPT_4, label: 'GPT-4' },
              { value: AIModel.CLAUDE, label: 'Claude' },
            ]}
          />
        </CardContent>
      </>
    );
  }, [aiConfig, handleModelChange]);

  /**
   * Renders the data access control section of the configuration form.
   * @returns {JSX.Element} The rendered data access section
   */
  const renderDataAccessSection = useCallback(() => {
    return (
      <>
        <CardHeader title="Data Access Control" />
        <CardContent>
          <p>
            Control which data the AI has access to. Limiting data access can
            improve privacy and security.
          </p>
          {/* Add data access controls here */}
        </CardContent>
      </>
    );
  }, []);

  /**
   * Renders the personalization settings section of the configuration form.
   * @returns {JSX.Element} The rendered personalization section
   */
  const renderPersonalizationSection = useCallback(() => {
    return (
      <>
        <CardHeader title="Personalization Settings" />
        <CardContent>
          <p>
            Enable or disable AI personalization features. Personalization
            allows the AI to adapt to your preferences and behavior.
          </p>
          <Checkbox
            label="Enable Content Highlighting"
            name="contentHighlighting"
            checked={aiConfig?.personalizationEnabled || false}
            onChange={(enabled) =>
              handlePersonalizationChange('contentHighlighting', enabled)
            }
          />
          <Button onClick={handleResetPersonalization}>
            Reset Personalization Data
          </Button>
        </CardContent>
      </>
    );
  }, [aiConfig, handlePersonalizationChange, handleResetPersonalization]);

  /**
   * Renders the feedback collection section of the configuration form.
   * @returns {JSX.Element} The rendered feedback section
   */
  const renderFeedbackSection = useCallback(() => {
    return (
      <>
        <CardHeader title="Feedback Collection" />
        <CardContent>
          <p>
            Provide feedback on AI performance to help us improve the AI
            models.
          </p>
          <AIFeedbackControls contentId="ai-config-page" contentType="page" onFeedbackSubmit={handleFeedbackSubmit} />
        </CardContent>
      </>
    );
  }, [handleFeedbackSubmit]);

  // LD1: Render tabs for different configuration sections
  const tabs = [
    { id: 'environment', label: 'Environment' },
    { id: 'model', label: 'Model' },
    { id: 'dataAccess', label: 'Data Access' },
    { id: 'personalization', label: 'Personalization' },
    { id: 'feedback', label: 'Feedback' },
  ];

  return (
    <div>
      <PageHeader title="AI Configuration" />
      {loading ? (
        <Spinner />
      ) : (
        <form onSubmit={handleSaveConfiguration}>
          <Card>
            <Tabs
              tabs={tabs}
              activeTab={activeTab}
              onChange={handleTabChange}
            />
            {/* LD1: Render appropriate configuration section based on active tab */}
            {activeTab === 'environment' && renderEnvironmentSection()}
            {activeTab === 'model' && renderModelSection()}
            {activeTab === 'dataAccess' && renderDataAccessSection()}
            {activeTab === 'personalization' && renderPersonalizationSection()}
            {activeTab === 'feedback' && renderFeedbackSection()}
          </Card>
          {/* LD1: Show save button and reset personalization button */}
          <Button type="submit" disabled={saving || !hasManageAIConfigPermission}>
            {saving ? 'Saving...' : 'Save Configuration'}
          </Button>
        </form>
      )}
      {/* LD1: Display loading spinner during API operations */}
      {saving && <Spinner />}
      {/* LD1: Show success/error notifications for configuration changes */}
      {successMessage && <Alert severity="success" message={successMessage} />}
      {error && <Alert severity="error" message={error} />}
      <ConfirmationDialog
        isOpen={confirmDialogOpen}
        title="Reset Personalization Data"
        message="Are you sure you want to reset your AI personalization data? This action cannot be undone."
        confirmText="Reset"
        onConfirm={handleConfirmReset}
        onCancel={handleCancelReset}
      />
    </div>
  );
};

export default AIConfigurationPage;