import React, { useState, useEffect, useCallback } from 'react'; //  ^18.2.0
import { useNavigate } from 'react-router-dom'; //  ^6.4.0
import { useDispatch, useSelector } from 'react-redux'; //  ^8.0.0

import Button from '../common/Button';
import TextField from '../common/TextField';
import DatePicker from '../common/DatePicker';
import Select from '../common/Select';
import Alert from '../common/Alert';
import Spinner from '../common/Spinner';
import ConfirmationDialog from '../common/ConfirmationDialog';

import useOrganizationContext from '../../context/OrganizationContext';
import useOrganizations from '../../hooks/useOrganizations';
import { formatDate, addDays } from '../../utils/date';
import { Organization, OrganizationType } from '../../types/organization';
import { createRateRequest, validateRateRules } from '../../store/rates/ratesThunks';

/**
 * @interface RateRequestFormProps
 * @description Props for the RateRequestForm component
 */
interface RateRequestFormProps {
  onClose?: () => void;
  onSubmitSuccess?: () => void;
  initialRecipientId?: string;
}

/**
 * @interface RateRequestFormData
 * @description Form data structure for rate requests
 */
interface RateRequestFormData {
  recipientId: string;
  message: string;
  submissionDeadline: Date;
}

/**
 * @interface RateRuleValidationResult
 * @description Response from rate rule validation
 */
interface RateRuleValidationResult {
  isValid: boolean;
  errors: string[];
  warnings: string[];
  ruleDetails: object;
}

/**
 * @function validateForm
 * @description Validates the rate request form data
 * @param {RateRequestFormData} formData - The form data to validate
 * @returns {Record<string, string>} - Validation errors by field name
 */
const validateForm = (formData: RateRequestFormData): Record<string, string> => {
  const errors: Record<string, string> = {};

  if (!formData.recipientId) {
    errors.recipientId = 'Please select a recipient organization';
  }

  if (!formData.message || formData.message.trim().length === 0) {
    errors.message = 'Please enter a message';
  } else if (formData.message.length > 500) {
    errors.message = 'Message must be less than 500 characters';
  }

  if (!formData.submissionDeadline) {
    errors.submissionDeadline = 'Please select a submission deadline';
  } else if (formData.submissionDeadline <= new Date()) {
    errors.submissionDeadline = 'Submission deadline must be in the future';
  }

  return errors;
};

/**
 * @component RateRequestForm
 * @description Form component that handles rate request creation from both law firms and clients
 */
const RateRequestForm: React.FC<RateRequestFormProps> = ({ onClose, onSubmitSuccess, initialRecipientId }) => {
  // Hooks for navigation, Redux dispatch, and organization context
  const navigate = useNavigate();
  const dispatch = useDispatch();
  const { currentOrganization } = useOrganizationContext();
  const { organizations, loading: orgsLoading } = useOrganizations();

  // Redux loading state
  const loading = useSelector((state: any) => state.rates.rateRequests.loading);

  // Component state for form data, errors, and submission status
  const [formData, setFormData] = useState<RateRequestFormData>({
    recipientId: initialRecipientId || '',
    message: '',
    submissionDeadline: addDays(new Date(), 30),
  });
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [isSubmitting, setIsSubmitting] = useState<boolean>(false);
  const [isValidating, setIsValidating] = useState<boolean>(false);
  const [formSuccess, setFormSuccess] = useState<boolean>(false);
  const [serverError, setServerError] = useState<string>('');
  const [ruleValidation, setRuleValidation] = useState<RateRuleValidationResult | null>(null);
  const [showWarningDialog, setShowWarningDialog] = useState<boolean>(false);

  /**
   * @function handleInputChange
   * @description Handles text input changes
   * @param {React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>} e - The input change event
   */
  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target;
    setFormData({ ...formData, [name]: value });
    setErrors({ ...errors, [name]: '' });
  };

  /**
   * @function handleSelectChange
   * @description Handles dropdown selection changes
   * @param {string} name - The name of the select field
   * @param {string} value - The selected value
   */
  const handleSelectChange = (name: string, value: string) => {
    setFormData({ ...formData, [name]: value });
    setErrors({ ...errors, [name]: '' });
    if (name === 'recipientId') {
      validateRules(value);
    }
  };

  /**
   * @function handleDateChange
   * @description Handles date picker changes
   * @param {string} name - The name of the date field
   * @param {Date} date - The selected date
   */
  const handleDateChange = (name: string, date: Date) => {
    setFormData({ ...formData, [name]: date });
    setErrors({ ...errors, [name]: '' });
  };

  /**
   * @function handleSubmit
   * @description Handles form submission
   * @param {React.FormEvent<HTMLFormElement>} e - The form submit event
   */
  const handleSubmit = (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();

    const validationErrors = validateForm(formData);
    if (Object.keys(validationErrors).length > 0) {
      setErrors(validationErrors);
      return;
    }

    if (ruleValidation && ruleValidation.warnings && ruleValidation.warnings.length > 0) {
      setShowWarningDialog(true);
      return;
    }

    handleProceedAnyway();
  };

  /**
   * @function validateRules
   * @description Validates form against client rate rules
   * @param {string} recipientId - The ID of the recipient organization
   */
  const validateRules = (recipientId: string) => {
    if (!recipientId) return;

    setIsValidating(true);
    dispatch(validateRateRules({
      clientId: recipientId,
      rates: []
    }))
      .then((result: any) => {
        setRuleValidation(result.payload);
      })
      .catch((error: any) => {
        console.error('Rule validation error:', error);
        setServerError('Error validating rate rules. Please try again.');
      })
      .finally(() => setIsValidating(false));
  };

  /**
   * @function getFilteredOrganizations
   * @description Filters organizations based on current organization type
   * @returns {Organization[]} - Filtered list of organizations
   */
  const getFilteredOrganizations = (): Organization[] => {
    if (currentOrganization?.type === OrganizationType.LawFirm) {
      return organizations.filter(org => org.type === OrganizationType.Client);
    } else if (currentOrganization?.type === OrganizationType.Client) {
      return organizations.filter(org => org.type === OrganizationType.LawFirm);
    }
    return [];
  };

  /**
   * @function handleProceedAnyway
   * @description Handles proceeding with submission despite warnings
   */
  const handleProceedAnyway = () => {
    setShowWarningDialog(false);
    setIsSubmitting(true);
    setServerError('');

    dispatch(createRateRequest({
      firmId: currentOrganization?.id,
      clientId: formData.recipientId,
      requestedBy: currentOrganization?.id,
      requestDate: formatDate(new Date()),
      status: 'pending',
      message: formData.message,
      submissionDeadline: formatDate(formData.submissionDeadline),
    } as any))
      .then(() => {
        setFormSuccess(true);
        if (onSubmitSuccess) {
          onSubmitSuccess();
        }
      })
      .catch((error: any) => {
        console.error('Rate request creation error:', error);
        setServerError('Error creating rate request. Please try again.');
      })
      .finally(() => setIsSubmitting(false));
  };

  /**
   * @function renderRuleValidation
   * @description Renders validation results for rate rules
   * @returns {JSX.Element | null} - Alert component with validation results
   */
  const renderRuleValidation = (): JSX.Element | null => {
    if (isValidating) {
      return <Spinner size="16px" />;
    }

    if (ruleValidation && ruleValidation.errors && ruleValidation.errors.length > 0) {
      return <Alert severity="error" message={ruleValidation.errors.join('\n')} />;
    }

    if (ruleValidation && ruleValidation.warnings && ruleValidation.warnings.length > 0) {
      return <Alert severity="warning" message={ruleValidation.warnings.join('\n')} />;
    }

    if (ruleValidation && ruleValidation.isValid) {
      return <Alert severity="success" message="Rate request complies with client rules." />;
    }

    return null;
  };

  return (
    <form onSubmit={handleSubmit}>
      {serverError && <Alert severity="error" message={serverError} />}
      {formSuccess && <Alert severity="success" message="Rate request submitted successfully!" />}

      {!orgsLoading ? (
        <Select
          name="recipientId"
          label="Recipient Organization"
          value={formData.recipientId}
          onChange={handleSelectChange}
          options={getFilteredOrganizations().map(org => ({ value: org.id, label: org.name }))}
          error={errors.recipientId}
          required
          fullWidth
        />
      ) : (
        <Spinner size="16px" />
      )}

      <TextField
        name="message"
        label="Message"
        value={formData.message}
        onChange={handleInputChange}
        error={errors.message}
        required
        fullWidth
        multiline
        rows={4}
      />

      <DatePicker
        name="submissionDeadline"
        label="Submission Deadline"
        value={formatDate(formData.submissionDeadline)}
        onChange={handleDateChange}
        error={errors.submissionDeadline}
        required
        fullWidth
      />

      {formData.recipientId && renderRuleValidation()}

      <Button type="submit" disabled={isSubmitting || Object.keys(errors).length > 0} fullWidth>
        {isSubmitting ? <Spinner size="16px" /> : 'Submit Request'}
      </Button>
      <ConfirmationDialog
        isOpen={showWarningDialog}
        title="Proceed with Submission?"
        message="The rate request has some warnings. Do you want to proceed anyway?"
        confirmText="Proceed Anyway"
        cancelText="Cancel"
        onConfirm={handleProceedAnyway}
        onCancel={() => setShowWarningDialog(false)}
      />
    </form>
  );
};

export default RateRequestForm;