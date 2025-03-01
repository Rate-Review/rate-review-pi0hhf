import React, { useState, useEffect } from 'react'; // React v18.0.0+
import { useForm, UseFormReturn } from '../../hooks/useForm'; // Custom hook for form handling with validation
import { useOrganizations } from '../../hooks/useOrganizations'; // Custom hook for organization and peer group operations
import Alert from '../common/Alert'; // UI component for displaying alerts and notifications
import Button from '../common/Button'; // UI component for button elements
import TextField from '../common/TextField'; // UI component for text input fields
import Select from '../common/Select'; // UI component for dropdown selection
import {
  PeerGroup,
  Organization,
  OrganizationType,
  PeerGroupCriteria,
} from '../../types/organization'; // Type definition for peer group data
import * as yup from 'yup'; // v1.0.0+ Schema validation library for form data

/**
 * Interface defining the props for the PeerGroupForm component
 */
interface PeerGroupFormProps {
  initialValues?: Partial<PeerGroup>;
  onSubmit: (peerGroup: PeerGroup) => void;
  onCancel: () => void;
}

/**
 * A form component for creating and editing peer groups
 */
const PeerGroupForm: React.FC<PeerGroupFormProps> = ({ initialValues = {}, onSubmit, onCancel }) => {
  // LD1: Initialize form state with useForm hook and validation schema
  const validationSchema = yup.object().shape({
    name: yup.string().required('Name is required'),
    description: yup.string().optional(),
    criteria: yup.array().of(yup.string()).required('At least one criteria is required'),
    members: yup.array().of(yup.string()).optional(),
  });

  const {
    values,
    errors,
    touched,
    isSubmitting,
    handleChange,
    handleBlur,
    handleSubmit,
    isValid,
    setValues,
  } = useForm<PeerGroup>({
    initialValues: {
      name: '',
      description: '',
      criteria: [],
      members: [],
      ...initialValues,
    },
    validationSchema: { validate: (values: PeerGroup) => validationSchema.validate(values, { abortEarly: false }) }, //IE1: Satisfies the type definition for validation schema
    onSubmit: handleSubmit,
  });

  // LD1: Setup state for tracking form submission, errors, and success
  const [submitError, setSubmitError] = useState<string | null>(null);
  const [submitSuccess, setSubmitSuccess] = useState<boolean>(false);

  // LD1: Fetch available organizations with the useOrganizations hook
  const { organizations, loading: organizationsLoading, error: organizationsError } = useOrganizations();

  // LD1: Handle form validation and submission
  const handleFormSubmit = async (formData: PeerGroup) => {
    setSubmitError(null);
    setSubmitSuccess(false);

    try {
      // LD1: Process form data into the correct format for the API
      const peerGroupData = formatPeerGroupData(formData);

      // LD1: Call the appropriate API function (create or update peer group)
      if (initialValues?.id) {
        // LD1: Update existing peer group
        console.log('Updating peer group:', peerGroupData);
        // await updatePeerGroup(initialValues.id, peerGroupData);
      } else {
        // LD1: Create new peer group
        console.log('Creating peer group:', peerGroupData);
        // await createPeerGroup(peerGroupData);
      }

      // LD1: Handle successful submission by showing success message and calling onSubmit callback
      setSubmitSuccess(true);
      onSubmit(peerGroupData);
    } catch (error: any) {
      // LD1: Handle errors by displaying error message and resetting submission state
      setSubmitError(error.message || 'An error occurred while submitting the form.');
    }
  };

  // LD1: Handle cancellation of the form
  const handleCancel = (event: React.MouseEvent<HTMLButtonElement>) => {
    event.preventDefault();
    onCancel();
  };

  // LD1: Maps organization data to format needed for Select component
  const mapOrganizationsToOptions = (organizations: Organization[]) => {
    return organizations.map(org => ({
      value: org.id,
      label: org.name,
    }));
  };

  // LD1: Gets the available criteria options for peer grouping
  const getAvailableCriteria = () => {
    return [
      { value: 'geography', label: 'Geography' },
      { value: 'practiceArea', label: 'Practice Area' },
      { value: 'size', label: 'Size' },
      { value: 'revenue', label: 'Revenue' },
    ];
  };

  // LD1: Formats form data into the structure expected by the API
  const formatPeerGroupData = (formData: PeerGroup): PeerGroup => {
    return {
      ...formData,
      criteria: Array.isArray(formData.criteria) ? formData.criteria.map(criteria => ({ value: criteria, label: criteria })) : [],
    };
  };

  // LD1: Render form with fields for name, description, criteria selection, and member organization selection
  return (
    <form onSubmit={handleSubmit}>
      {submitSuccess && <Alert severity="success" message="Peer group saved successfully!" />}
      {submitError && <Alert severity="error" message={submitError} />}

      <TextField
        name="name"
        label="Name"
        value={values.name || ''}
        onChange={handleChange}
        onBlur={handleBlur}
        error={touched.name && errors.name ? errors.name : undefined}
        required
        fullWidth
      />

      <TextField
        name="description"
        label="Description"
        value={values.description || ''}
        onChange={handleChange}
        onBlur={handleBlur}
        error={touched.description && errors.description ? errors.description : undefined}
        fullWidth
      />

      <Select
        name="criteria"
        label="Criteria"
        multiple
        options={getAvailableCriteria()}
        value={values.criteria || []}
        onChange={(selectedCriteria) => setValues({ ...values, criteria: selectedCriteria })}
        onBlur={handleBlur}
        error={touched.criteria && errors.criteria ? errors.criteria : undefined}
        required
        fullWidth
      />

      <Select
        name="members"
        label="Members"
        multiple
        options={mapOrganizationsToOptions(organizations)}
        value={values.members || []}
        onChange={(selectedMembers) => setValues({ ...values, members: selectedMembers })}
        onBlur={handleBlur}
        error={touched.members && errors.members ? errors.members : undefined}
        fullWidth
      />

      {/* LD1: Provide submit and cancel buttons with appropriate handlers */}
      <Button type="submit" disabled={isSubmitting || !isValid}>
        {initialValues?.id ? 'Update Peer Group' : 'Create Peer Group'}
      </Button>
      <Button variant="outline" onClick={handleCancel} disabled={isSubmitting}>
        Cancel
      </Button>
    </form>
  );
};

export default PeerGroupForm;