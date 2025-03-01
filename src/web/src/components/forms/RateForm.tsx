import React, { useState, useEffect } from 'react'; //  ^18.0.0
import styled from 'styled-components';
import TextField from '../common/TextField';
import Select from '../common/Select';
import DatePicker from '../common/DatePicker';
import Button from '../common/Button';
import useForm from '../../hooks/useForm';
import useRates from '../../hooks/useRates';
import {
  validateRateIncrease,
  validateNumeric,
  validatePositiveNumber,
  validateDateRange,
  validateCurrency,
} from '../../utils/validation';
import {
  Rate,
  RateType,
  CreateRateRequest,
  RateWithDetails,
} from '../../types/rate';
import { SUPPORTED_CURRENCIES } from '../../constants/currencies';

/**
 * @interface RateFormProps
 * @description Props for the RateForm component
 */
interface RateFormProps {
  initialValues?: RateWithDetails;
  onSubmit: (values: CreateRateRequest) => void;
  onCancel?: () => void;
  isEditing?: boolean;
  clientId: string;
  firmId: string;
  attorneyOptions?: { value: string; label: string }[];
  staffClassOptions?: { value: string; label: string }[];
  isAttorneyRate?: boolean;
  resetOnSubmit?: boolean;
  disableAttorneySelect?: boolean;
  disableStaffClassSelect?: boolean;
  className?: string;
}

/**
 * @interface RateFormValues
 * @description Form values for the RateForm component
 */
interface RateFormValues {
  attorneyId: string;
  staffClassId: string;
  amount: string;
  currency: string;
  effectiveDate: string;
  expirationDate: string;
  type: RateType;
}

/**
 * @styled_component FormContainer
 * @description A styled div component for the form container
 */
const FormContainer = styled.div`
  display: flex;
  flex-direction: column;
  gap: 16px;
  max-width: 600px;
  width: 100%;
`;

/**
 * @styled_component FormRow
 * @description A styled div component for a row in the form
 */
const FormRow = styled.div`
  display: flex;
  flex-direction: row;
  gap: 16px;
  width: 100%;
  @media (max-width: 768px) {
    flex-direction: column;
  }
`;

/**
 * @styled_component FormActions
 * @description A styled div component for the form actions
 */
const FormActions = styled.div`
  display: flex;
  flex-direction: row;
  justify-content: flex-end;
  gap: 16px;
  margin-top: 24px;
`;

/**
 * @function RateForm
 * @param {RateFormProps} props - Props for the RateForm component
 * @returns {JSX.Element} A form component for creating and editing attorney and staff class rates
 * @exports RateForm
 */
const RateForm: React.FC<RateFormProps> = ({
  initialValues,
  onSubmit,
  onCancel,
  isEditing = false,
  clientId,
  firmId,
  attorneyOptions = [],
  staffClassOptions = [],
  isAttorneyRate = true,
  resetOnSubmit = false,
  disableAttorneySelect = false,
  disableStaffClassSelect = false,
  className,
}) => {
  // LD1: Initialize state for currency and rate type options
  const [currencyOptions, setCurrencyOptions] = useState(SUPPORTED_CURRENCIES);
  const [rateTypeOptions, setRateTypeOptions] = useState([
    { value: 'standard', label: 'Standard' },
    { value: 'approved', label: 'Approved' },
    { value: 'proposed', label: 'Proposed' },
    { value: 'counter_proposed', label: 'Counter Proposed' },
  ]);

  // LD1: Define initial form values based on whether we are editing or creating a new rate
  const initialFormValues: RateFormValues = {
    attorneyId: initialValues?.rate?.attorneyId || '',
    staffClassId: initialValues?.rate?.staffClassId || '',
    amount: initialValues?.rate?.amount?.toString() || '',
    currency: initialValues?.rate?.currency || 'USD',
    effectiveDate: initialValues?.rate?.effectiveDate || '',
    expirationDate: initialValues?.rate?.expirationDate || '',
    type: initialValues?.rate?.type || 'standard' as RateType,
  };

  // LD1: Use the useForm hook to manage form state and validation
  const {
    values,
    errors,
    touched,
    isSubmitting,
    handleChange,
    handleBlur,
    handleSubmit: handleFormSubmit,
    setFieldValue,
    resetForm,
    isValid,
  } = useForm<RateFormValues>({
    initialValues: initialFormValues,
    validationSchema: {
      validate: async (values: RateFormValues) => {
        return validateFormValues(values);
      },
    },
    onSubmit: async (values: RateFormValues) => {
      handleSubmit(values);
    },
    validateOnBlur: true,
    validateOnChange: true,
  });

  // LD1: Implement form validation logic
  /**
   * @function validateFormValues
   * @description Validates the form values against client rate rules and basic validation rules
   * @param {object} values - The form values to validate
   * @returns {object} An object containing validation errors, if any
   */
  const validateFormValues = (values: RateFormValues) => {
    let errors: any = {};

    // LD1: Validate amount is a positive number
    if (!validatePositiveNumber(values.amount)) {
      errors.amount = 'Amount must be a positive number';
    }

    // LD1: Validate currency is supported
    if (!validateCurrency(values.currency)) {
      errors.currency = 'Currency is not supported';
    }

    // LD1: Validate effective date is present and valid
    if (!values.effectiveDate) {
      errors.effectiveDate = 'Effective date is required';
    }

    // LD1: Validate expiration date is after effective date if provided
    if (values.effectiveDate && values.expirationDate) {
      const dateRangeValidation = validateDateRange(
        values.effectiveDate,
        values.expirationDate
      );
      if (!dateRangeValidation.isValid) {
        errors.expirationDate = dateRangeValidation.error;
      }
    }

    // LD1: If editing existing rate, validate rate increase percentage
    if (isEditing && initialValues?.rate?.amount) {
      const rateIncreaseValidation = validateRateIncrease(
        initialValues.rate.amount,
        parseFloat(values.amount)
      );
      if (!rateIncreaseValidation.isValid) {
        errors.amount = rateIncreaseValidation.error;
      }
    }

    // LD1: If client rate rules exist, validate against them
    // TODO: Implement client rate rule validation logic here

    return errors;
  };

  // LD1: Implement form submission logic
  /**
   * @function handleSubmit
   * @description Handles form submission by calling the onSubmit callback with validated form data
   * @param {object} values - The form values to submit
   * @returns {void} No return value
   */
  const handleSubmit = (values: RateFormValues) => {
    // LD1: Format the values (e.g., parse numeric values, format dates)
    const formattedValues: CreateRateRequest = {
      attorneyId: values.attorneyId,
      clientId: clientId,
      firmId: firmId,
      staffClassId: values.staffClassId,
      amount: parseFloat(values.amount),
      currency: values.currency,
      effectiveDate: values.effectiveDate,
      expirationDate: values.expirationDate,
      type: values.type,
    };

    // LD1: Call onSubmit callback with formatted data
    onSubmit(formattedValues);

    // LD1: Reset form if resetOnSubmit is true
    if (resetOnSubmit) {
      resetForm();
    }
  };

  // LD1: Implement form cancellation logic
  /**
   * @function handleCancel
   * @description Handles cancellation of the form
   * @returns {void} No return value
   */
  const handleCancel = () => {
    // LD1: Call onCancel callback if provided
    if (onCancel) {
      onCancel();
    }

    // LD1: Reset form to initial values
    resetForm();
  };

  return (
    <FormContainer className={className}>
      {isAttorneyRate ? (
        <Select
          name="attorneyId"
          label="Attorney"
          value={values.attorneyId}
          onChange={(value) => setFieldValue('attorneyId', value)}
          onBlur={handleBlur}
          options={attorneyOptions}
          error={errors.attorneyId}
          touched={touched.attorneyId}
          required
          fullWidth
          disabled={disableAttorneySelect}
        />
      ) : (
        <Select
          name="staffClassId"
          label="Staff Class"
          value={values.staffClassId}
          onChange={(value) => setFieldValue('staffClassId', value)}
          onBlur={handleBlur}
          options={staffClassOptions}
          error={errors.staffClassId}
          touched={touched.staffClassId}
          required
          fullWidth
          disabled={disableStaffClassSelect}
        />
      )}
      <TextField
        name="amount"
        label="Amount"
        value={values.amount}
        onChange={handleChange}
        onBlur={handleBlur}
        type="number"
        placeholder="Enter amount"
        error={errors.amount}
        touched={touched.amount}
        required
        fullWidth
      />
      <Select
        name="currency"
        label="Currency"
        value={values.currency}
        onChange={(value) => setFieldValue('currency', value)}
        onBlur={handleBlur}
        options={currencyOptions}
        error={errors.currency}
        touched={touched.currency}
        required
        fullWidth
      />
      <DatePicker
        name="effectiveDate"
        label="Effective Date"
        value={values.effectiveDate}
        onChange={(value) => setFieldValue('effectiveDate', value)}
        onBlur={handleBlur}
        format="MM/dd/yyyy"
        placeholder="MM/DD/YYYY"
        error={errors.effectiveDate}
        helperText="Select the date the rate becomes effective"
        fullWidth
      />
      <DatePicker
        name="expirationDate"
        label="Expiration Date"
        value={values.expirationDate}
        onChange={(value) => setFieldValue('expirationDate', value)}
        onBlur={handleBlur}
        format="MM/dd/yyyy"
        placeholder="MM/DD/YYYY"
        error={errors.expirationDate}
        helperText="Select the date the rate expires"
        fullWidth
      />
      <Select
        name="type"
        label="Rate Type"
        value={values.type}
        onChange={(value) => setFieldValue('type', value)}
        onBlur={handleBlur}
        options={rateTypeOptions}
        error={errors.type}
        touched={touched.type}
        required
        fullWidth
      />
      <FormActions>
        <Button onClick={handleCancel} disabled={isSubmitting}>
          Cancel
        </Button>
        <Button
          variant="primary"
          onClick={handleFormSubmit}
          disabled={isSubmitting || !isValid}
        >
          {isEditing ? 'Update Rate' : 'Create Rate'}
        </Button>
      </FormActions>
    </FormContainer>
  );
};

RateForm.defaultProps = {
  initialValues: {
    attorneyId: '',
    staffClassId: '',
    amount: '',
    currency: 'USD',
    effectiveDate: '',
    expirationDate: '',
    type: 'standard' as RateType,
  },
  isEditing: false,
  isAttorneyRate: true,
  resetOnSubmit: false,
  disableAttorneySelect: false,
  disableStaffClassSelect: false,
};

export default RateForm;