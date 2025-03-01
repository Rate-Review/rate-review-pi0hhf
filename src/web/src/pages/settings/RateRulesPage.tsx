import React, { useState, useCallback, useEffect } from 'react'; //  ^18.0.0
import { toast } from '@mui/material'; //  ^5.14.0
import PageHeader from '../../components/layout/PageHeader';
import Card from '../../components/common/Card';
import TextField from '../../components/common/TextField';
import Select from '../../components/common/Select';
import Button from '../../components/common/Button';
import DatePicker from '../../components/common/DatePicker';
import Alert from '../../components/common/Alert';
import PeerGroupSelect from '../../components/forms/PeerGroupForm';
import { useAuth } from '../../hooks/useAuth';
import { usePermissions } from '../../hooks/usePermissions';
import {
  updateOrganizationSettings,
  getOrganizationSettings,
} from '../../services/organizations';
import { formatMonth } from '../../utils/date';
import { validateRateRules } from '../../utils/validation';
import { TOAST_TYPES } from '../../constants/toast';

/**
 * Main component function that renders the Rate Rules configuration page
 * @returns {JSX.Element} The rendered Rate Rules page component
 */
const RateRulesPage: React.FC = () => {
  // Initialize state for rate rules using useState hook
  const [rateRules, setRateRules] = useState({
    freezePeriod: 0,
    noticeRequired: 0,
    maxIncreasePercent: 0,
    submissionWindow: {
      startMonth: 1,
      startDay: 1,
      endMonth: 12,
      endDay: 31,
    },
  });

  // Initialize state for loading, saving, and validation states
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [hasChanges, setHasChanges] = useState(false);
  const [validationErrors, setValidationErrors] = useState<any>({});

  // Get current organization from useAuth hook
  const { organization } = useAuth();

  // Check if user has permission to edit rate rules
  const { hasPermission } = usePermissions();
  const canEditRateRules = hasPermission('update', 'settings', 'organization');

  /**
   * Fetches the organization's current rate rules settings
   */
  const fetchRateRules = useCallback(async () => {
    // Set loading state to true
    setLoading(true);
    try {
      // Call getOrganizationSettings API with organization ID
      const response = await getOrganizationSettings(organization?.id || '');
      // Extract rate rules from organization settings response
      const fetchedRateRules = response?.rateRules || {
        freezePeriod: 0,
        noticeRequired: 0,
        maxIncreasePercent: 0,
        submissionWindow: {
          startMonth: 1,
          startDay: 1,
          endMonth: 12,
          endDay: 31,
        },
      };
      // Update rate rules state with fetched data
      setRateRules(fetchedRateRules);
    } catch (error: any) {
      // Handle any errors and display appropriate messages
      toast.error(`Failed to load rate rules: ${error.message}`);
    } finally {
      // Set loading state to false
      setLoading(false);
    }
  }, [organization?.id]);

  // Fetch current organization rate rules on component mount
  useEffect(() => {
    if (organization?.id) {
      fetchRateRules();
    }
  }, [organization?.id, fetchRateRules]);

  /**
   * Handles changes to rate rule form fields
   * @param {React.ChangeEvent<HTMLInputElement>} event
   * @param {string} ruleType
   */
  const handleRuleChange = (
    event: React.ChangeEvent<HTMLInputElement>,
    ruleType: string
  ) => {
    // Extract field name and value from event
    const { name, value } = event.target;

    // Create a deep copy of the current rate rules state
    const updatedRateRules = { ...rateRules };

    // Update the specific field in the copied state
    (updatedRateRules as any)[name] = value;

    // Set hasChanges to true to track unsaved changes
    setHasChanges(true);

    // Update the rate rules state with the changes
    setRateRules(updatedRateRules);
  };

  /**
   * Handles changes to submission window date fields
   * @param {Date} date
   * @param {string} field
   */
  const handleSubmissionWindowChange = (date: Date, field: string) => {
    // Create a deep copy of the current rate rules state
    const updatedRateRules = { ...rateRules };

    // Extract month and day from the date object
    const month = date.getMonth() + 1; // Month is 0-indexed
    const day = date.getDate();

    // Update the specific submission window field
    if (updatedRateRules.submissionWindow) {
      updatedRateRules.submissionWindow[field as keyof typeof updatedRateRules.submissionWindow] = month;
    }

    // Set hasChanges to true to track unsaved changes
    setHasChanges(true);

    // Update the rate rules state with the changes
    setRateRules(updatedRateRules);
  };

  /**
   * Saves the updated rate rules to the organization settings
   */
  const handleSave = async () => {
    // Perform validation of rate rules using validateRateRules utility
    const validationResult = validateRateRules(rateRules);
    if (!validationResult.isValid) {
      // If validation fails, display error messages and return
      setValidationErrors(validationResult.errors);
      toast.error('Please correct the errors below.');
      return;
    }

    // Set saving state to true
    setSaving(true);
    try {
      // Prepare rate rules data for API request
      const settingsData = { rateRules };

      // Call updateOrganizationSettings API with updated data
      await updateOrganizationSettings(settingsData);

      // Show success message when save is complete
      toast.success('Rate rules saved successfully!');

      // Set saving state to false and hasChanges to false
      setSaving(false);
      setHasChanges(false);
    } catch (error: any) {
      // Handle any errors and display appropriate messages
      toast.error(`Failed to save rate rules: ${error.message}`);
    } finally {
      // Set saving state to false and hasChanges to false
      setSaving(false);
    }
  };

  /**
   * Resets the form to the last saved state
   */
  const handleCancel = () => {
    // Display confirmation dialog if there are unsaved changes
    if (hasChanges) {
      const confirmCancel = window.confirm(
        'Are you sure you want to cancel? Your changes will be lost.'
      );
      if (!confirmCancel) {
        return;
      }
    }

    // Reset form state to the original fetched data
    fetchRateRules();

    // Clear validation errors
    setValidationErrors({});

    // Set hasChanges to false
    setHasChanges(false);
  };

  // Render page header with title and description
  return (
    <div>
      <PageHeader title="Rate Rules" />

      {/* Render form sections for different types of rate rules */}
      <Card title="General Rate Rules">
        <TextField
          name="freezePeriod"
          label="Rate Freeze Period (months)"
          type="number"
          value={rateRules.freezePeriod?.toString() || ''}
          onChange={handleRuleChange}
          onBlur={handleRuleChange}
          error={validationErrors.freezePeriod}
          fullWidth
        />
        <TextField
          name="noticeRequired"
          label="Notice Period (days)"
          type="number"
          value={rateRules.noticeRequired?.toString() || ''}
          onChange={handleRuleChange}
          onBlur={handleRuleChange}
          error={validationErrors.noticeRequired}
          fullWidth
        />
        <TextField
          name="maxIncreasePercent"
          label="Maximum Increase Percentage"
          type="number"
          value={rateRules.maxIncreasePercent?.toString() || ''}
          onChange={handleRuleChange}
          onBlur={handleRuleChange}
          error={validationErrors.maxIncreasePercent}
          fullWidth
        />
      </Card>

      <Card title="Submission Window">
        <DatePicker
          label="Start Date"
          value={
            rateRules.submissionWindow
              ? `${rateRules.submissionWindow.startMonth}/${rateRules.submissionWindow.startDay}/2023`
              : null
          }
          onChange={(date) =>
            date && handleSubmissionWindowChange(date, 'startMonth')
          }
        />
        <DatePicker
          label="End Date"
          value={
            rateRules.submissionWindow
              ? `${rateRules.submissionWindow.endMonth}/${rateRules.submissionWindow.endDay}/2023`
              : null
          }
          onChange={(date) =>
            date && handleSubmissionWindowChange(date, 'endMonth')
          }
        />
      </Card>

      {/* Render save and cancel buttons */}
      <div>
        <Button onClick={handleSave} disabled={!canEditRateRules || saving}>
          Save
        </Button>
        <Button
          variant="outline"
          onClick={handleCancel}
          disabled={saving || loading}
        >
          Cancel
        </Button>
      </div>

      {/* Display loading state while fetching or saving data */}
      {loading && <div>Loading...</div>}
    </div>
  );
};

export default RateRulesPage;