import React, { useState, useEffect, ReactElement } from 'react'; //  ^18.2.0
import { useNavigate, Link } from 'react-router-dom'; //  ^6.4.0
import styled from 'styled-components'; //  ^5.3.8
import TextField from '../../components/common/TextField';
import Button from '../../components/common/Button';
import Alert from '../../components/common/Alert';
import AuthLayout from '../../components/layout/AuthLayout';
import { useAuth } from '../../hooks/useAuth';
import { LoginRequest, TwoFactorRequest } from '../../types/auth';

// Styled Components for Login Page
const LoginContainer = styled.div`
  width: 100%;
  max-width: 400px;
  margin: 0 auto;
`;

const FormGroup = styled.div`
  margin-bottom: 1.5rem;
`;

const ForgotPasswordLink = styled.div`
  text-align: right;
  margin-bottom: 1.5rem;
  font-size: 0.875rem;
`;

const SSOContainer = styled.div`
  margin-top: 2rem;
  text-align: center;
`;

const SSOButtonsContainer = styled.div`
  display: flex;
  justify-content: center;
  gap: 1rem;
  margin-top: 1rem;
`;

const OrDivider = styled.div`
  display: flex;
  align-items: center;
  margin: 1.5rem 0;
  color: var(--text-secondary);

  &::before,
  &::after {
    content: '';
    flex: 1;
    border-bottom: 1px solid var(--border-color);
  }

  &::before {
    margin-right: 1rem;
  }

  &::after {
    margin-left: 1rem;
  }
`;

const RegisterPrompt = styled.div`
  text-align: center;
  margin-top: 2rem;
  font-size: 0.875rem;
`;

const MFAContainer = styled.div`
  margin-top: 1rem;
  text-align: center;
`;

/**
 * @description Main login page component that renders the login form and handles authentication
 * @returns {JSX.Element} Rendered login page component
 */
const LoginPage: React.FC = (): ReactElement => {
  // Initialize form state with useState for email and password
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');

  // Initialize MFA state with useState for verification code
  const [verificationCode, setVerificationCode] = useState('');

  // Get authentication utilities and state from useAuth hook
  const { login, verifyMfa, loading, error, mfaRequired } = useAuth();

  // Get navigate function from useNavigate hook for redirection
  const navigate = useNavigate();

  /**
   * @description Handles the login form submission
   * @param {React.FormEvent<HTMLFormElement>} event
   * @returns {Promise<void>} Promise that resolves when login attempt completes
   */
  const handleSubmit = async (event: React.FormEvent<HTMLFormElement>): Promise<void> => {
    // Prevent default form submission behavior
    event.preventDefault();

    try {
      // Call login function from useAuth with email and password
      await login({ email, password });
    } catch (loginError: any) {
      // Handle errors with appropriate user feedback
      console.error('Login failed', loginError);
    }
  };

  /**
   * @description Handles the MFA verification form submission
   * @param {React.FormEvent<HTMLFormElement>} event
   * @returns {Promise<void>} Promise that resolves when MFA verification completes
   */
  const handleMfaSubmit = async (event: React.FormEvent<HTMLFormElement>): Promise<void> => {
    // Prevent default form submission behavior
    event.preventDefault();

    try {
      // Call verifyMfa function from useAuth with verification code
      await verifyMfa({ code: verificationCode });
    } catch (mfaError: any) {
      // Handle errors with appropriate user feedback
      console.error('MFA verification failed', mfaError);
    }
  };

  /**
   * @description Initiates SSO authentication flow with selected provider
   * @param {string} provider
   * @returns {void} No return value
   */
  const handleSSOLogin = (provider: string): void => {
    // Redirect to SSO authentication endpoint with provider parameter
    window.location.href = `/api/v1/auth/sso?provider=${provider}`;
  };

  // Render AuthLayout with login form content
  return (
    <AuthLayout title="Login">
      <LoginContainer>
        {/* Conditionally render MFA verification form if mfaRequired is true */}
        {mfaRequired ? (
          <form onSubmit={handleMfaSubmit}>
            <FormGroup>
              <TextField
                id="verificationCode"
                label="Verification Code"
                type="text"
                placeholder="Enter verification code"
                value={verificationCode}
                onChange={(e) => setVerificationCode(e.target.value)}
                required
                fullWidth
              />
            </FormGroup>
            <MFAContainer>
              <Button type="submit" disabled={loading}>
                {loading ? 'Verifying...' : 'Verify'}
              </Button>
            </MFAContainer>
          </form>
        ) : (
          <form onSubmit={handleSubmit}>
            {/* Render error message using Alert component if authentication errors occur */}
            {error && <Alert severity="error" message={error} />}
            <FormGroup>
              {/* Render form inputs for email and password */}
              <TextField
                id="email"
                label="Email"
                type="email"
                placeholder="Enter your email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
                fullWidth
              />
            </FormGroup>
            <FormGroup>
              <TextField
                id="password"
                label="Password"
                type="password"
                placeholder="Enter your password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                fullWidth
              />
            </FormGroup>
            <ForgotPasswordLink>
              <Link to="/auth/forgot-password">Forgot Password?</Link>
            </ForgotPasswordLink>
            {/* Render login button with loading state */}
            <Button type="submit" disabled={loading} fullWidth>
              {loading ? 'Logging in...' : 'Login'}
            </Button>
          </form>
        )}
        <OrDivider>or</OrDivider>
        <SSOContainer>
          <div>Login with SSO</div>
          <SSOButtonsContainer>
            {/* Render SSO login options */}
            <Button variant="outline" onClick={() => handleSSOLogin('google')}>
              Google
            </Button>
            <Button variant="outline" onClick={() => handleSSOLogin('microsoft')}>
              Microsoft
            </Button>
          </SSOButtonsContainer>
        </SSOContainer>
        <RegisterPrompt>
          Don't have an account? <Link to="/auth/register">Register</Link>
        </RegisterPrompt>
      </LoginContainer>
    </AuthLayout>
  );
};

export default LoginPage;