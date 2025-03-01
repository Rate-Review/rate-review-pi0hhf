import React, { useState, useEffect } from 'react'; //  ^18.0.0
import styled from 'styled-components'; //  ^5.3.10
import Button from '../common/Button';
import TextField from '../common/TextField';
import Alert from '../common/Alert';
import Avatar from '../common/Avatar';
import useForm, { ValidationSchema } from '../../hooks/useForm';
import { useAuth } from '../../hooks/useAuth';
import { UserProfile, UserPreferences } from '../../types/user';
import userService from '../../services/users';
import { validateEmail, isRequired, validatePassword } from '../../utils/validation';

/**
 * Interface defining the props for the ProfileForm component
 */
interface ProfileFormProps {
  includePassword?: boolean;
  onSuccess?: () => void;
  readOnly?: boolean;
}

/**
 * Interface defining the form values for the profile form
 */
interface ProfileFormValues {
  email: string;
  name: string;
  password?: string;
  confirmPassword?: string;
  preferences?: UserPreferences;
}

/**
 * Creates a validation schema object for the profile form
 * @param includePassword - Whether to include password validation rules
 * @returns Validation schema with field validation functions
 */
const createValidationSchema = (includePassword: boolean): ValidationSchema<ProfileFormValues> => {
  // Create a base validation schema with email and name validation
  const schema: any = {
    validate: (values: ProfileFormValues) => {
      const errors: any = {};

      if (!isRequired(values.name)) {
        errors.name = 'Name is required';
      }

      if (!isRequired(values.email)) {
        errors.email = 'Email is required';
      } else if (!validateEmail(values.email)) {
        errors.email = 'Email is invalid';
      }

      if (includePassword) {
        if (!isRequired(values.password)) {
          errors.password = 'Password is required';
        } else {
          const passwordValidation = validatePassword(values.password);
          if (!passwordValidation.isValid) {
            errors.password = passwordValidation.error;
          }
        }

        if (!isRequired(values.confirmPassword)) {
          errors.confirmPassword = 'Confirm Password is required';
        } else if (values.password !== values.confirmPassword) {
          errors.confirmPassword = 'Passwords do not match';
        }
      }

      return errors;
    }
  };

  return schema;
};

/**
 * Creates initial form values based on current user profile data
 * @param currentUser - Current user profile data
 * @param includePassword - Whether to include password fields
 * @returns Initial form values for the profile form
 */
const createInitialValues = (currentUser: UserProfile, includePassword: boolean): ProfileFormValues => {
  // Extract relevant profile data from currentUser: email, name, preferences
  const initialValues: ProfileFormValues = {
    email: currentUser.email,
    name: currentUser.name,
    preferences: currentUser.preferences
  };

  // If includePassword is true, add empty password and confirmPassword fields
  if (includePassword) {
    initialValues.password = '';
    initialValues.confirmPassword = '';
  }

  return initialValues;
};

/**
 * A form that allows users to view and edit their profile information
 */
const ProfileForm: React.FC<ProfileFormProps> = ({ includePassword = false, onSuccess, readOnly = false }) => {
  // Retrieve current user information
  const { currentUser } = useAuth();

  // Manage alert message state for form submission results
  const [alertState, setAlertState] = useState<{ type: 'success' | 'error' | null; message: string | null }>({
    type: null,
    message: null
  });

  // Track form submission status
  const [isSubmitting, setIsSubmitting] = useState<boolean>(false);

  // Create validation schema based on includePassword prop
  const validationSchema = createValidationSchema(includePassword);

  // Set up form using useForm with initial values, validation schema, and submit handler
  const { values, errors, touched, handleChange, handleBlur, handleSubmit, setFieldValue } = useForm<ProfileFormValues>({
    initialValues: createInitialValues(currentUser as UserProfile, includePassword),
    validationSchema,
    onSubmit: async (values) => {
      // Set isSubmitting to true
      setIsSubmitting(true);

      try {
        // Try to update user profile using userService.updateUser
        await userService.updateUser(currentUser?.id, {
          name: values.name,
        });

        // If successful, set success alert and call onSuccess callback
        setAlertState({ type: 'success', message: 'Profile updated successfully!' });
        onSuccess?.();
      } catch (error: any) {
        // If error occurs, set error alert
        setAlertState({ type: 'error', message: error.message || 'Failed to update profile.' });
      } finally {
        // Finally set isSubmitting to false
        setIsSubmitting(false);
      }
    }
  });

  // Handle side effects and form initialization
  useEffect(() => {
    if (currentUser) {
      // Update form values when user data changes
      setFieldValue('name', currentUser.name, false);
      setFieldValue('email', currentUser.email, false);
    }
  }, [currentUser, setFieldValue]);

  return (
    <FormContainer>
      <FormSection>
        <FormHeading>Personal Information</FormHeading>
        <AvatarSection>
          <Avatar name={values.name} size="lg" />
        </AvatarSection>
        <TextField
          id="name"
          name="name"
          label="Name"
          value={values.name}
          onChange={handleChange}
          onBlur={handleBlur}
          error={errors.name}
          touched={touched.name}
          readOnly={readOnly}
        />
        <TextField
          id="email"
          name="email"
          label="Email"
          type="email"
          value={values.email}
          readOnly
        />
      </FormSection>

      {includePassword && (
        <FormSection>
          <FormHeading>Password</FormHeading>
          <TextField
            id="password"
            name="password"
            label="Password"
            type="password"
            value={values.password || ''}
            onChange={handleChange}
            onBlur={handleBlur}
            error={errors.password}
            touched={touched.password}
            readOnly={readOnly}
          />
          <TextField
            id="confirmPassword"
            name="confirmPassword"
            label="Confirm Password"
            type="password"
            value={values.confirmPassword || ''}
            onChange={handleChange}
            onBlur={handleBlur}
            error={errors.confirmPassword}
            touched={touched.confirmPassword}
            readOnly={readOnly}
          />
        </FormSection>
      )}

      {alertState.message && (
        <Alert severity={alertState.type === 'success' ? 'success' : 'error'} message={alertState.message} />
      )}

      {!readOnly && (
        <ButtonContainer>
          <Button type="submit" onClick={handleSubmit} disabled={isSubmitting}>
            {isSubmitting ? 'Updating...' : 'Update Profile'}
          </Button>
        </ButtonContainer>
      )}
    </FormContainer>
  );
};

export default ProfileForm;

const FormContainer = styled.div`
  max-width: 600px;
  margin: 0 auto;
  padding: 24px;
`;

const FormSection = styled.div`
  margin-bottom: 24px;
`;

const FormHeading = styled.h3`
  font-size: 18px;
  margin-bottom: 16px;
  color: ${props => props.theme.colors.primary.main};
`;

const AvatarSection = styled.div`
  display: flex;
  align-items: center;
  margin-bottom: 24px;
`;

const ButtonContainer = styled.div`
  display: flex;
  justify-content: flex-end;
  margin-top: 24px;
`;