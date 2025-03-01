import React, { useState, useEffect, useCallback } from 'react'; //  ^18.0.0
import { TextField } from '../common/TextField';
import { Select } from '../common/Select';
import { Button } from '../common/Button';
import { Alert } from '../common/Alert';
import useRates from '../../hooks/useRates';
import useOrganizations from '../../hooks/useOrganizations';
import styled from 'styled-components'; //  ^5.3.6
import { useForm, Controller } from 'react-hook-form'; //  ^7.40.0
import { yupResolver } from '@hookform/resolvers/yup'; //  ^2.9.0
import * as yup from 'yup'; //  ^0.32.11

/**
 * Interface defining the staff class form data structure
 */
export interface StaffClassFormData {
  id?: string | undefined;
  name: string;
  experience_type: string;
  min_experience: number;
  max_experience?: number | undefined;
  practice_area?: string | undefined;
  geography?: string | undefined;
  is_active: boolean;
  organization_id: string;
}

/**
 * Interface defining the props for the StaffClassForm component
 */
export interface StaffClassFormProps {
  initialData?: StaffClassFormData | undefined;
  onSubmit: (data: StaffClassFormData) => void;
  onCancel: () => void;
}

/**
 * Validates that min experience is less than or equal to max experience
 * @param {object} values - Object containing min_experience and max_experience
 * @returns {boolean} True if valid, false if invalid
 */
const validateExperienceRange = (values: { min_experience: number; max_experience?: number }): boolean => {
  // Check if both min_experience and max_experience are provided
  if (values.min_experience !== undefined && values.max_experience !== undefined) {
    // Verify min_experience <= max_experience
    return values.min_experience <= values.max_experience;
  }
  return true;
};

/**
 * Array of options for experience type dropdown
 * @returns {array} Array of option objects with value and label properties
 */
const experienceTypeOptions = () => {
  return [
    { value: 'BAR_YEAR', label: 'Bar Year' },
    { value: 'GRADUATION_YEAR', label: 'Graduation Year' },
    { value: 'YEARS_IN_ROLE', label: 'Years in Role' },
  ];
};

/**
 * Form component for creating and editing staff classes
 */
const StaffClassForm: React.FC<StaffClassFormProps> = ({ initialData, onSubmit, onCancel }) => {
  // LD1: Destructure props to access initialData, onSubmit, and onCancel
  // LD1: Set up form validation schema using yup
  const validationSchema = yup.object().shape({
    name: yup.string().required('Name is required'),
    experience_type: yup.string().required('Experience Type is required'),
    min_experience: yup.number().required('Minimum Experience is required').positive('Minimum Experience must be positive'),
    max_experience: yup.number().positive('Maximum Experience must be positive').when('min_experience', {
      is: (min_experience: number) => min_experience !== undefined,
      then: yup.number().test(
        'max_experience',
        'Maximum Experience must be greater than or equal to Minimum Experience',
        function (max_experience) {
          return validateExperienceRange({ min_experience: this.parent.min_experience, max_experience });
        }
      )
    }),
    practice_area: yup.string(),
    geography: yup.string(),
    is_active: yup.boolean().required('Active status is required'),
  });

  // LD1: Initialize form using react-hook-form with validation schema
  const { control, handleSubmit, formState: { errors }, reset } = useForm<StaffClassFormData>({
    resolver: yupResolver(validationSchema),
    defaultValues: initialData,
    mode: 'onBlur',
  });

  // LD1: Get current organization data using useOrganizations hook
  const { currentOrganization } = useOrganizations();

  // LD1: Set up state for form errors and submission status
  const [formError, setFormError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  // LD1: Define submit handler that validates and processes form data
  const handleSubmitForm = async (data: StaffClassFormData) => {
    if (!currentOrganization?.id) {
      setFormError('Organization ID is missing.');
      return;
    }

    setIsSubmitting(true);
    setFormError(null);

    try {
      // LD1: Add organization ID to the form data
      const formData: StaffClassFormData = {
        ...data,
        organization_id: currentOrganization.id,
      };

      // LD1: Call the onSubmit function passed as a prop
      onSubmit(formData);
    } catch (error: any) {
      setFormError(error.message || 'An error occurred while submitting the form.');
    } finally {
      setIsSubmitting(false);
    }
  };

  // LD1: Render form with text fields for name, min/max experience, and practice area
  // LD1: Render dropdown for experience type (BAR_YEAR, GRADUATION_YEAR, YEARS_IN_ROLE)
  // LD1: Render checkbox for active status
  // LD1: Render form controls (submit and cancel buttons)
  // LD1: Return the complete form structure
  return (
    <FormContainer onSubmit={handleSubmit(handleSubmitForm)}>
      {formError && (
        <ErrorContainer>
          <Alert severity="error" message={formError} />
        </ErrorContainer>
      )}

      <TextField
        control={control}
        name="name"
        label="Name"
        required
        error={errors.name?.message}
      />

      <Controller
        name="experience_type"
        control={control}
        defaultValue=""
        render={({ field }) => (
          <Select
            {...field}
            label="Experience Type"
            options={experienceTypeOptions()}
            required
            error={errors.experience_type?.message}
          />
        )}
      />

      <FieldRow>
        <TextField
          control={control}
          name="min_experience"
          label="Minimum Experience"
          type="number"
          required
          error={errors.min_experience?.message}
        />

        <TextField
          control={control}
          name="max_experience"
          label="Maximum Experience"
          type="number"
          error={errors.max_experience?.message}
        />
      </FieldRow>

      <TextField
        control={control}
        name="practice_area"
        label="Practice Area"
      />

      <TextField
        control={control}
        name="geography"
        label="Geography"
      />

      <Controller
        name="is_active"
        control={control}
        defaultValue={true}
        render={({ field }) => (
          <div>
            <label>
              Active:
              <input type="checkbox" {...field} />
            </label>
          </div>
        )}
      />

      <ButtonContainer>
        <Button onClick={onCancel} variant="secondary">
          Cancel
        </Button>
        <Button type="submit" disabled={isSubmitting}>
          {isSubmitting ? 'Submitting...' : 'Submit'}
        </Button>
      </ButtonContainer>
    </FormContainer>
  );
};

export default StaffClassForm;

// LD1: Styled components for consistent UI
const FormContainer = styled.form`
  display: flex;
  flex-direction: column;
  gap: 16px;
  width: 100%;
  max-width: 600px;
`;

const FieldRow = styled.div`
  display: flex;
  gap: 16px;
  width: 100%;

  @media (max-width: 768px) {
    flex-direction: column;
  }
`;

const ButtonContainer = styled.div`
  display: flex;
  justify-content: flex-end;
  gap: 16px;
  margin-top: 24px;
`;

const ErrorContainer = styled.div`
  margin-bottom: 16px;
`;