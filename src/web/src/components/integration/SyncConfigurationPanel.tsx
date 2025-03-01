import React, { useState, useEffect } from 'react';
import { Card, CardContent } from '../common/Card';
import Select from '../common/Select';
import Button from '../common/Button';
import TextField from '../common/TextField';
import Checkbox from '../common/Checkbox';
import Alert from '../common/Alert';
import {
  IntegrationType,
  SyncSettings,
} from '../../types/integration';
import {
  selectIntegrationById,
} from '../../store/integrations/integrationsSlice';
import { updateSyncSettings } from '../../store/integrations/integrationsThunks';
import { useAppDispatch, useAppSelector } from '../../store/hooks'; // Assuming you have a custom hook for dispatch
import { useForm, SubmitHandler } from 'react-hook-form'; //  ^7.34.0

// Define the props for the SyncConfigurationPanel component
interface SyncConfigurationPanelProps {
  integrationType: IntegrationType;
  integrationId: string;
  onSaveComplete: () => void;
}

// Define the form data structure
interface SyncConfigurationFormData {
  importFrequency: string;
  exportBehavior: string;
  errorHandling: string;
  enableScheduledSync: boolean;
  syncStartTime: string;
}

// Define the alert state structure
interface AlertState {
  visible: boolean;
  type: 'success' | 'error';
  message: string;
}

/**
 * A component that renders a panel for configuring synchronization settings for integrations
 */
const SyncConfigurationPanel: React.FC<SyncConfigurationPanelProps> = ({
  integrationType,
  integrationId,
  onSaveComplete,
}) => {
  // Initialize form state using react-hook-form
  const { register, handleSubmit, watch, setValue, formState: { errors } } = useForm<SyncConfigurationFormData>();

  // Create state variables for loading and alert status
  const [loading, setLoading] = useState(false);
  const [alert, setAlert] = useState<AlertState>({ visible: false, type: 'success', message: '' });

  // Use useSelector to get the integration by ID
  const integration = useAppSelector((state) => selectIntegrationById(state.integrations, integrationId));

  // Use useDispatch to dispatch Redux actions
  const dispatch = useAppDispatch();

  // Define frequency options (hourly, daily, weekly, monthly, manual)
  const frequencyOptions = [
    { value: 'hourly', label: 'Hourly' },
    { value: 'daily', label: 'Daily' },
    { value: 'weekly', label: 'Weekly' },
    { value: 'monthly', label: 'Monthly' },
    { value: 'manual', label: 'Manual' },
  ];

  // Define export behavior options (append, overwrite, merge)
  const exportBehaviorOptions = [
    { value: 'append', label: 'Append' },
    { value: 'overwrite', label: 'Overwrite' },
    { value: 'merge', label: 'Merge' },
  ];

  // Define error handling options (stop on error, log and continue, skip errors)
  const errorHandlingOptions = [
    { value: 'stopOnError', label: 'Stop on Error' },
    { value: 'logAndContinue', label: 'Log and Continue' },
    { value: 'skipErrors', label: 'Skip Errors' },
  ];

  // useEffect to set default form values when integration data is loaded
  useEffect(() => {
    if (integration && integration.configuration && (integration.configuration as any).syncSettings) {
      const syncSettings = (integration.configuration as any).syncSettings as SyncSettings;
      setValue('importFrequency', syncSettings.importFrequency || 'manual');
      setValue('exportBehavior', syncSettings.exportBehavior || 'append');
      setValue('errorHandling', syncSettings.errorHandling || 'stopOnError');
      setValue('enableScheduledSync', syncSettings.enableScheduledSync || false);
      setValue('syncStartTime', syncSettings.syncStartTime || '00:00');
    }
  }, [integration, setValue]);

  // Create handleSubmit function to validate and process form submission
  const onSubmit: SubmitHandler<SyncConfigurationFormData> = async (data) => {
    setLoading(true);
    setAlert({ visible: false, type: 'success', message: '' });
    try {
      // Dispatch updateSyncSettings thunk with form data and integration ID
      await dispatch(
        updateSyncSettings({
          integrationId: integrationId,
          syncSettings: {
            importFrequency: data.importFrequency,
            exportBehavior: data.exportBehavior,
            errorHandling: data.errorHandling,
            enableScheduledSync: data.enableScheduledSync,
            syncStartTime: data.syncStartTime,
          },
        })
      ).unwrap();

      // Handle success state after form submission
      setAlert({ visible: true, type: 'success', message: 'Synchronization settings saved successfully!' });
      onSaveComplete();
    } catch (error: any) {
      // Handle error states after form submission
      setAlert({ visible: true, type: 'error', message: error.message || 'Failed to save synchronization settings.' });
    } finally {
      setLoading(false);
    }
  };

  // Watch the enableScheduledSync value to conditionally render the time selector
  const enableScheduledSync = watch('enableScheduledSync');

  return (
    <Card title="Synchronization Settings">
      <CardContent>
        {alert.visible && <Alert severity={alert.type} message={alert.message} onClose={() => setAlert({ ...alert, visible: false })} />}
        <form onSubmit={handleSubmit(onSubmit)}>
          <Select
            label="Import Frequency"
            name="importFrequency"
            options={frequencyOptions}
            required
            fullWidth
            {...register("importFrequency", { required: "Import Frequency is required" })}
            error={errors.importFrequency?.message}
          />
          <Select
            label="Export Behavior"
            name="exportBehavior"
            options={exportBehaviorOptions}
            required
            fullWidth
            {...register("exportBehavior", { required: "Export Behavior is required" })}
            error={errors.exportBehavior?.message}
          />
          <Select
            label="Error Handling"
            name="errorHandling"
            options={errorHandlingOptions}
            required
            fullWidth
            {...register("errorHandling", { required: "Error Handling is required" })}
            error={errors.errorHandling?.message}
          />
          <Checkbox
            name="enableScheduledSync"
            label="Enable Scheduled Synchronization"
            {...register("enableScheduledSync")}
          />
          {enableScheduledSync && (
            <TextField
              label="Sync Start Time"
              name="syncStartTime"
              type="time"
              fullWidth
              {...register("syncStartTime", { required: "Sync Start Time is required" })}
              error={errors.syncStartTime?.message}
            />
          )}
          <Button type="submit" disabled={loading}>
            {loading ? 'Saving...' : 'Save'}
          </Button>
        </form>
      </CardContent>
    </Card>
  );
};

export default SyncConfigurationPanel;