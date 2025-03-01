import React, { useState, ChangeEvent, FormEvent } from 'react'; //  ^18.2.0
import { useNavigate } from 'react-router-dom'; // ^6.10.0
import { useDispatch } from 'react-redux'; // ^8.0.5
import styled from 'styled-components'; // ^5.3.10
import validator from 'validator'; // ^13.9.0
import {
  register,
} from '../../services/auth';
import { useAuth } from '../../hooks/useAuth';
import { Button } from '../../components/common/Button';
import { TextField } from '../../components/common/TextField';
import { Select } from '../../components/common/Select';
import { Alert } from '../../components/common/Alert';
import { AuthLayout } from '../../components/layout/AuthLayout';
import { ROUTES } from '../../constants/routes';
import { RegisterFormData } from '../../types/auth';
import { OrganizationType } from '../../types/organization';

/**
 * The main component that renders the user registration page
 * @returns {JSX.Element} The rendered registration page
 */
const RegisterPage: React.FC = () => {
  // Define state variables for form data
  const [email, setEmail] = useState('');
  const [name, setName] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [organizationName, setOrganizationName] = useState('');
  const [organizationType, setOrganizationType] = useState<OrganizationType | ''>('');
  const [domain, setDomain] = useState('');

  // Define state variables for validation errors, form submission state, and API errors
  const [errors, setErrors] = useState<Partial<RegisterFormData>>({});
  const [loading, setLoading] = useState(false);
  const [apiError, setApiError] = useState<string | null>(null);

  // Set up navigation and Redux dispatch hooks
  const navigate = useNavigate();
  const dispatch = useDispatch();

  // Use the useAuth hook for authentication-related functionality
  const { register: authRegister } = useAuth();

  /**
   * Handles form input changes and updates state
   * @param {React.ChangeEvent<HTMLInputElement | HTMLSelectElement>} event
   * @returns {void} No return value
   */
  const handleInputChange = (event: ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value } = event.target;

    switch (name) {
      case 'email':
        setEmail(value);
        break;
      case 'name':
        setName(value);
        break;
      case 'password':
        setPassword(value);
        break;
      case 'confirmPassword':
        setConfirmPassword(value);
        break;
      case 'organizationName':
        setOrganizationName(value);
        break;
      case 'organizationType':
        setOrganizationType(value as OrganizationType);
        break;
      case 'domain':
        setDomain(value);
        break;
      default:
        break;
    }

    // Basic validation
    const newErrors = { ...errors };
    if (name === 'email' && value && !validator.isEmail(value)) {
      newErrors.email = 'Please enter a valid email address';
    } else if (name === 'confirmPassword' && value !== password) {
      newErrors.confirmPassword = 'This field must match password';
    } else {
      delete newErrors[name];
    }
    setErrors(newErrors);
  };

  /**
   * Validates all form fields before submission
   * @returns {boolean} Whether the form is valid
   */
  const validateForm = (): boolean => {
    const newErrors: Partial<RegisterFormData> = {};

    if (!validator.isEmail(email)) {
      newErrors.email = 'Please enter a valid email address';
    }
    if (!name) {
      newErrors.name = 'Please enter your name';
    }
    if (password.length < 8) {
      newErrors.password = 'Password must be at least 8 characters';
    }
    if (confirmPassword !== password) {
      newErrors.confirmPassword = 'This field must match password';
    }
    if (!organizationName) {
      newErrors.organizationName = 'Please enter your organization name';
    }
    if (!organizationType) {
      newErrors.organizationType = 'Please select an organization type';
    }
    if (organizationType === OrganizationType.CLIENT && !domain) {
      newErrors.domain = 'Please enter your organization domain';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  /**
   * Handles form submission for user registration
   * @param {React.FormEvent<HTMLFormElement>} event
   * @returns {void} No return value
   */
  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();

    if (validateForm()) {
      setLoading(true);
      setApiError(null);

      const registerData: RegisterFormData = {
        email,
        name,
        password,
        organizationName,
        organizationType,
        domain: organizationType === OrganizationType.CLIENT ? domain : undefined,
      };

      try {
        await authRegister(registerData);
        navigate(ROUTES.DASHBOARD);
      } catch (error: any) {
        setApiError(error?.message || 'Registration failed');
      } finally {
        setLoading(false);
      }
    }
  };

  return (
    <AuthLayout title="Create an Account">
      <FormContainer onSubmit={handleSubmit}>
        {apiError && <Alert severity="error" message={apiError} />}
        <FormGroup>
          <TextField
            label="Email"
            name="email"
            type="email"
            value={email}
            onChange={handleInputChange}
            error={errors.email}
            required
            fullWidth
          />
        </FormGroup>
        <FormGroup>
          <TextField
            label="Name"
            name="name"
            type="text"
            value={name}
            onChange={handleInputChange}
            error={errors.name}
            required
            fullWidth
          />
        </FormGroup>
        <FormGroup>
          <TextField
            label="Password"
            name="password"
            type="password"
            value={password}
            onChange={handleInputChange}
            error={errors.password}
            required
            fullWidth
          />
        </FormGroup>
        <FormGroup>
          <TextField
            label="Confirm Password"
            name="confirmPassword"
            type="password"
            value={confirmPassword}
            onChange={handleInputChange}
            error={errors.confirmPassword}
            required
            fullWidth
          />
        </FormGroup>
        <FormGroup>
          <TextField
            label="Organization Name"
            name="organizationName"
            type="text"
            value={organizationName}
            onChange={handleInputChange}
            error={errors.organizationName}
            required
            fullWidth
          />
        </FormGroup>
        <FormGroup>
          <Select
            label="Organization Type"
            name="organizationType"
            value={organizationType}
            onChange={(value) => handleInputChange({ target: { name: 'organizationType', value } } as ChangeEvent<HTMLSelectElement>)}
            options={[
              { value: OrganizationType.LAW_FIRM, label: 'Law Firm' },
              { value: OrganizationType.CLIENT, label: 'Client' },
            ]}
            error={errors.organizationType}
            required
            fullWidth
          />
        </FormGroup>
        {organizationType === OrganizationType.CLIENT && (
          <FormGroup>
            <TextField
              label="Organization Domain"
              name="domain"
              type="text"
              value={domain}
              onChange={handleInputChange}
              error={errors.domain}
              required
              fullWidth
            />
          </FormGroup>
        )}
        <Button type="submit" variant="primary" fullWidth disabled={loading}>
          {loading ? 'Creating Account...' : 'Create Account'}
        </Button>
        <LoginPrompt>
          Already have an account? <LoginLink to={ROUTES.LOGIN}>Log In</LoginLink>
        </LoginPrompt>
      </FormContainer>
    </AuthLayout>
  );
};

export default RegisterPage;

const FormContainer = styled.form`
  padding: ${(props) => props.theme.spacing(3)};
  margin-top: ${(props) => props.theme.spacing(2)};
  max-width: 400px;
`;

const FormTitle = styled.h2`
  font-size: 24px;
  font-weight: 500;
  color: ${(props) => props.theme.palette.text.primary};
  margin-bottom: ${(props) => props.theme.spacing(3)};
`;

const FormGroup = styled.div`
  margin-bottom: ${(props) => props.theme.spacing(2)};
`;

const FormRow = styled.div`
  display: flex;
  gap: ${(props) => props.theme.spacing(2)};
`;

const LoginPrompt = styled.p`
  margin-top: ${(props) => props.theme.spacing(3)};
  text-align: center;
  font-size: 14px;
`;

const LoginLink = styled.a`
  color: ${(props) => props.theme.palette.primary.main};
  text-decoration: none;
  &:hover {
    text-decoration: underline;
  }
`;