import React, { useEffect } from 'react'; // React core library v18.0+
import styled from 'styled-components'; // Styling library for component styling v5.3.10
import * as Yup from 'yup'; // Schema validation library for form validation v1.0.0
import { Organization, OrganizationType } from '../../types/organization'; // Type definitions for organization-related data
import useOrganizations from '../../hooks/useOrganizations'; // Custom hook for organization management operations
import useForm from '../../hooks/useForm'; // Custom hook for form state management and validation
import TextField from '../common/TextField'; // Input field component for organization properties
import Select from '../common/Select'; // Dropdown select component for organization type selection
import Button from '../common/Button'; // Button component for form submission and cancellation

/**
 * Interface defining the props for the OrganizationForm component
 */
interface OrganizationFormProps {
  initialData?: Organization;
  isEdit?: boolean;
  onSuccess: () => void;
  onCancel: () => void;
}

/**
 * Validates that the domain follows proper format and doesn't contain restricted subdomains
 * @param domain The domain to validate
 * @returns Whether the domain is valid
 */
const validateDomain = (domain: string): boolean => {
  // Regular expression for a valid domain format
  const domainRegex = /^(?!:\/\/)(?:[a-zA-Z0-9-]+\\.)*[a-zA-Z0-9][a-zA-Z0-9-]+[a-zA-Z0-9]\\.[^-][a-zA-Z0-9-]+(?:\\.[a-zA-Z0-9-]+)*$/;

  // Restricted subdomains that are not allowed
  const restrictedSubdomains = ['localhost', 'example', 'test'];

  // Check if the domain matches the valid format and doesn't contain restricted subdomains
  return domainRegex.test(domain) && !restrictedSubdomains.some(sub => domain.includes(sub));
};

/**
 * Form component for creating and editing organization entities in the Justice Bid system
 */
const OrganizationForm: React.FC<OrganizationFormProps> = ({ initialData, isEdit = false, onSuccess, onCancel }) => {
  // Use the useOrganizations hook to access organization management functions
  const { createNewOrganization, updateExistingOrganization, loading: organizationsLoading, error: organizationsError } = useOrganizations();

  // Define the Yup validation schema for the organization form fields
  const validationSchema = Yup.object().shape({
    name: Yup.string().required('Organization name is required').min(2, 'Organization name must be at least 2 characters').max(100, 'Organization name cannot exceed 100 characters'),
    type: Yup.string().oneOf(Object.values(OrganizationType), 'Invalid organization type').required('Organization type is required'),
    domain: Yup.string().required('Email domain is required').test('valid-domain', 'Valid domain format is required', value => validateDomain(value)),
    settings: Yup.object().shape({
      defaultCurrency: Yup.string().optional().oneOf(['USD', 'EUR', 'GBP', 'CAD'], 'Valid currency code is required')
    })
  });

  // Use the useForm hook to manage form state and validation
  const {
    values,
    errors,
    touched,
    isSubmitting,
    isValid,
    handleChange,
    handleBlur,
    handleSubmit,
    setFieldValue,
    setFieldError,
  } = useForm({
    initialValues: {
      name: initialData?.name || '',
      type: initialData?.type || OrganizationType.LawFirm,
      domain: initialData?.domain || '',
      settings: {
        defaultCurrency: initialData?.settings?.defaultCurrency || 'USD'
      }
    },
    validationSchema: { validate: (values: any) => validationSchema.validate(values, { abortEarly: false }) },
    onSubmit: async (formValues) => {
      try {
        // Call the appropriate organization management function based on whether it's an edit or create operation
        if (isEdit && initialData) {
          await updateExistingOrganization(formValues);
        } else {
          await createNewOrganization(formValues);
        }

        // Call the onSuccess callback to notify the parent component
        onSuccess();
      } catch (error: any) {
        // Set the server error message if the submission fails
        setFieldError('server', error.message);
      }
    }
  });

  // Set the initial values when the component mounts in edit mode
  useEffect(() => {
    if (initialData) {
      setFieldValue('name', initialData.name);
      setFieldValue('type', initialData.type);
      setFieldValue('domain', initialData.domain);
      setFieldValue('settings.defaultCurrency', initialData.settings.defaultCurrency);
    }
  }, [initialData, setFieldValue]);

  return (
    <FormContainer>
      <FormSection>
        <FormTitle>{isEdit ? 'Edit Organization' : 'Create Organization'}</FormTitle>
        <TextField
          id="name"
          name="name"
          label="Organization Name"
          value={values.name}
          onChange={handleChange}
          onBlur={handleBlur}
          error={touched.name && errors.name}
          required
        />
        <Select
          id="type"
          name="type"
          label="Organization Type"
          value={values.type}
          onChange={(value) => setFieldValue('type', value)}
          onBlur={handleBlur}
          options={[
            { value: OrganizationType.LawFirm, label: 'Law Firm' },
            { value: OrganizationType.Client, label: 'Client' },
          ]}
          required
        />
        <TextField
          id="domain"
          name="domain"
          label="Email Domain"
          value={values.domain}
          onChange={handleChange}
          onBlur={handleBlur}
          error={touched.domain && errors.domain}
          required
          helpText="The email domain for the organization (e.g., @example.com)"
        />
      </FormSection>

      <FormSection>
        <FormTitle>Settings</FormTitle>
        <Select
          id="settings.defaultCurrency"
          name="settings.defaultCurrency"
          label="Default Currency"
          value={values.settings?.defaultCurrency || 'USD'}
          onChange={(value) => setFieldValue('settings.defaultCurrency', value)}
          onBlur={handleBlur}
          options={[
            { value: 'USD', label: 'USD - US Dollar' },
            { value: 'EUR', label: 'EUR - Euro' },
            { value: 'GBP', label: 'GBP - British Pound' },
            { value: 'CAD', label: 'CAD - Canadian Dollar' },
          ]}
          helpText="The default currency for this organization"
        />
      </FormSection>

      {errors.server && <ErrorMessage>{errors.server}</ErrorMessage>}

      <ButtonContainer>
        <Button onClick={onCancel} disabled={isSubmitting}>
          Cancel
        </Button>
        <Button
          variant="primary"
          onClick={handleSubmit}
          disabled={isSubmitting || !isValid}
        >
          {isEdit ? 'Update' : 'Create'}
        </Button>
      </ButtonContainer>
    </FormContainer>
  );
};

export default OrganizationForm;

// Styled components for the OrganizationForm
const FormContainer = styled.div`
  width: 100%;
  max-width: 800px;
  margin: 0 auto;
`;

const FormSection = styled.div`
  margin-bottom: 24px;
`;

const FormTitle = styled.h2`
  font-size: 24px;
  margin-bottom: 16px;
  color: ${props => props.theme.colors.primary.main};
`;

const FieldRow = styled.div`
  display: flex;
  gap: 16px;
  margin-bottom: 16px;

  @media (max-width: 768px) {
    flex-direction: column;
    gap: 8px;
  }
`;

const ButtonContainer = styled.div`
  display: flex;
  justify-content: flex-end;
  gap: 16px;
  margin-top: 24px;
`;

const ErrorMessage = styled.div`
  color: ${(props) => props.theme.colors.error.main};
  font-size: 14px;
  margin-top: 4px;
`;