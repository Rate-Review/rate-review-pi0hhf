import React, { useState, useEffect } from 'react'; // React v18.0.0+
import styled from 'styled-components'; // styled-components v5.3.10
import { useForm } from '../../hooks/useForm';
import TextField from '../common/TextField';
import Select from '../common/Select';
import Checkbox from '../common/Checkbox';
import Button from '../common/Button';
import {
  UserRole,
  UserPermission,
  UserFormData,
} from '../../types/user';
import userService from '../../services/users';
import { validateEmail, isRequired } from '../../utils/validation';
import { usePermissions } from '../../hooks/usePermissions';

/**
 * @interface UserFormProps
 * @description Props for the UserForm component
 */
interface UserFormProps {
  user?: User | null;
  organizationId: string;
  onSubmit: (data: UserFormData) => void;
  onCancel: () => void;
  isLoading?: boolean;
}

/**
 * Creates validation schema for the user form
 * @param isEditMode 
 * @returns Validation schema object for the form
 */
const createValidationSchema = (isEditMode: boolean) => ({
  validate: (values: UserFormData) => {
    const errors: any = {};
    // Create validation rules for name field using isRequired
    if (!isRequired(values.name)) {
      errors.name = 'Name is required';
    }
    // Create validation rules for email field using isRequired and validateEmail
    if (!isRequired(values.email)) {
      errors.email = 'Email is required';
    } else if (!validateEmail(values.email)) {
      errors.email = 'Invalid email format';
    }
    // Include password validation only if not in edit mode
    if (!isEditMode && !isRequired(values.password)) {
      errors.password = 'Password is required';
    }
    // Create validation rules for role field using isRequired
    if (!isRequired(values.role)) {
      errors.role = 'Role is required';
    }
    // Return validation schema object with all field validations
    return errors;
  },
});

/**
 * Prepares initial values for the form based on user data
 * @param user 
 * @returns Initial form values
 */
const prepareInitialValues = (user: User | null): UserFormData => {
  // Check if user data is provided for edit mode
  if (user) {
    // If editing, use existing user data for initial values
    return {
      email: user.email,
      name: user.name,
      role: user.role,
      permissions: user.permissions,
      isContact: user.isContact,
    };
  } else {
    // If creating, set default empty values
    return {
      email: '',
      name: '',
      role: UserRole.STANDARD_USER,
      permissions: [],
      isContact: false,
    };
  }
};

/**
 * A form component for creating and editing users within an organization
 * @param props - Props for the UserForm component
 */
const UserForm: React.FC<UserFormProps> = ({
  user,
  organizationId,
  onSubmit,
  onCancel,
  isLoading = false,
}) => {
  // Determine if form is in edit mode based on presence of user prop
  const isEditMode = !!user;

  // Create validation schema based on edit mode
  const validationSchema = createValidationSchema(isEditMode);

  // Prepare initial form values from user data if provided
  const initialValues = prepareInitialValues(user);

  // Use useForm hook to manage form state and validation
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
  } = useForm<UserFormData>({
    initialValues,
    validationSchema,
    onSubmit,
  });

  // Manage available roles and permissions lists state
  const [availableRoles, setAvailableRoles] = useState<UserRole[]>([]);
  const [availablePermissions, setAvailablePermissions] = useState<UserPermission[]>(Object.values(UserPermission));

  // Fetch available roles using userService.getAvailableRoles on component mount
  useEffect(() => {
    userService.getAvailableRoles()
      .then(roles => setAvailableRoles(roles))
      .catch(error => console.error("Failed to fetch available roles:", error));
  }, []);

  // Format roles as options for Select component
  const roleOptions = availableRoles.map(role => ({
    value: role,
    label: role.replace(/([A-Z])/g, ' $1').trim(), // Add space before capital letters for display
  }));

  // Define form submission handler that creates or updates user via API
  const handleSubmitWrapper = async (data: UserFormData) => {
    if (user) {
      await userService.updateUser(user.id, data);
    } else {
      await userService.createUser(data);
    }
  };

  // Check current user permissions to determine which permissions they can manage
  const { can } = usePermissions();

  // Render form with TextField for name and email inputs
  return (
    <FormContainer>
      <FormSection>
        <FormTitle>{isEditMode ? 'Edit User' : 'Create User'}</FormTitle>
        <FormRow>
          <TextField
            id="name"
            name="name"
            label="Name"
            value={values.name}
            onChange={handleChange}
            onBlur={handleBlur}
            error={touched.name && errors.name}
            required
            fullWidth
          />
        </FormRow>
        <FormRow>
          <TextField
            id="email"
            name="email"
            label="Email"
            type="email"
            value={values.email}
            onChange={handleChange}
            onBlur={handleBlur}
            error={touched.email && errors.email}
            required
            fullWidth
          />
        </FormRow>
        {!isEditMode && (
          <FormRow>
            <TextField
              id="password"
              name="password"
              label="Password"
              type="password"
              onChange={handleChange}
              onBlur={handleBlur}
              error={touched.password && errors.password}
              required
              fullWidth
            />
          </FormRow>
        )}
        <FormRow>
          <Select
            id="role"
            name="role"
            label="Role"
            value={values.role}
            onChange={(value) => setFieldValue('role', value)}
            onBlur={handleBlur}
            options={roleOptions}
            error={touched.role && errors.role}
            required
            fullWidth
          />
        </FormRow>
        <FormRow>
          <Checkbox
            id="isContact"
            name="isContact"
            label="Is Contact"
            checked={values.isContact}
            onChange={(checked) => setFieldValue('isContact', checked)}
          />
        </FormRow>
      </FormSection>
      <FormSection>
        <SectionLabel>Permissions</SectionLabel>
        <PermissionsContainer>
          {availablePermissions.map((permission) => (
            <Checkbox
              key={permission}
              id={`permission-${permission}`}
              name={`permission-${permission}`}
              label={permission}
              checked={values.permissions?.includes(permission)}
              onChange={(checked) => {
                const currentPermissions = values.permissions || [];
                if (checked) {
                  setFieldValue('permissions', [...currentPermissions, permission]);
                } else {
                  setFieldValue(
                    'permissions',
                    currentPermissions.filter((p) => p !== permission)
                  );
                }
              }}
              disabled={!can('update', 'users', 'organization')}
            />
          ))}
        </PermissionsContainer>
      </FormSection>
      <FormActions>
        <Button onClick={onCancel} variant="outline">
          Cancel
        </Button>
        <Button
          onClick={handleSubmit}
          disabled={!isValid || isSubmitting || isLoading}
        >
          {isSubmitting || isLoading ? 'Submitting...' : 'Submit'}
        </Button>
      </FormActions>
    </FormContainer>
  );
};

export default UserForm;

const FormContainer = styled.div`
  max-width: 600px;
  width: 100%;
  margin: 0 auto;
`;

const FormSection = styled.div`
  margin-bottom: 24px;
`;

const FormTitle = styled.h2`
  font-size: 24px;
  font-weight: 500;
  margin-bottom: 16px;
  color: ${props => props.theme.colors.primary.main};
`;

const FormRow = styled.div`
  margin-bottom: 16px;
`;

const FormActions = styled.div`
  display: flex;
  justify-content: flex-end;
  gap: 16px;
  margin-top: 32px;
`;

const PermissionsContainer = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 16px;
  margin-top: 16px;
`;

const SectionLabel = styled.div`
  font-size: 16px;
  font-weight: 500;
  margin-bottom: 12px;
  color: ${props => props.theme.colors.text.primary};
`;