import React, { useState } from 'react'; //  ^18.2.0
import { useNavigate, useParams, Link } from 'react-router-dom'; //  ^6.4.0
import styled from 'styled-components'; //  ^5.3.8
import { z } from 'zod'; //  ^3.22.2
import { useAuth } from '../../hooks/useAuth';
import TextField from '../../components/common/TextField';
import Button from '../../components/common/Button';
import Alert from '../../components/common/Alert';
import AuthLayout from '../../components/layout/AuthLayout';
import PasswordForm from '../../components/forms/PasswordForm';

/**
 * Main component for the password reset page that handles both request and confirmation phases
 * @returns {JSX.Element} Rendered password reset page component
 */
const ResetPasswordPage: React.FC = () => {
  // Get token parameter from URL using useParams hook if available
  const { token } = useParams<{ token: string }>();

  // Initialize states for email input, success messages, and form phase
  const [email, setEmail] = useState('');
  const [success, setSuccess] = useState(false);
  const isConfirmationPhase = !!token;

  // Get authentication utilities and state from useAuth hook
  const { resetPassword, loading, error } = useAuth();

  // Get navigate function from useNavigate hook for redirection
  const navigate = useNavigate();

  // Create email validation schema using zod
  const emailSchema = z.string().email({ message: 'Invalid email address' });

  /**
   * Handles the password reset request form submission
   * @param {React.FormEvent<HTMLFormElement>} event
   * @returns {Promise<void>} Promise that resolves when reset request completes
   */
  const handleRequestReset = async (event: React.FormEvent<HTMLFormElement>) => {
    // Prevent default form submission behavior
    event.preventDefault();

    try {
      // Validate email input using zod schema
      emailSchema.parse(email);

      // Call resetPassword function with email
      await resetPassword({ email });

      // Set success state to true when request succeeds
      setSuccess(true);
    } catch (err: any) {
      // Handle any errors from the reset request
      if (err instanceof z.ZodError) {
        // Set error state with validation message
        console.error('Validation error:', err.errors[0].message);
      } else {
        // Set error state with API error message
        console.error('API error:', err.message);
      }
    }
  };

  /**
   * Handles the password reset confirmation when received from PasswordForm
   * @param {object} { password: string, confirmPassword: string }
   * @returns {Promise<void>} Promise that resolves when password reset completes
   */
  const handleConfirmReset = async ({ password, confirmPassword }: { password: string, confirmPassword: string }) => {
    try {
      // Ensure token is available from URL params
      if (!token) {
        throw new Error('Reset token is missing');
      }

      // Call confirmPasswordReset function with token and new password
      await resetPassword({ token, password });

      // Set success state to true when reset succeeds
      setSuccess(true);
    } catch (err: any) {
      // Handle any errors from the reset confirmation
      console.error('Password reset confirmation error:', err.message);
    }
  };

  // Render AuthLayout with appropriate title based on phase
  return (
    <AuthLayout title={isConfirmationPhase ? 'Reset Password' : 'Request Password Reset'}>
      {/* Render request form (email input) if in request phase */}
      {!isConfirmationPhase ? (
        <ResetContainer>
          <FormGroup>
            <TextField
              label="Email Address"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="Enter your email"
              required
              fullWidth
            />
          </FormGroup>
          <Button onClick={handleRequestReset} disabled={loading} fullWidth>
            {loading ? 'Sending Request...' : 'Request Reset'}
          </Button>
          {success && (
            <SuccessMessage>
              Password reset instructions sent to your email.
            </SuccessMessage>
          )}
          {error && <Alert severity="error" message={error} />}
          <LoginLink>
            <Link to="/login">Back to Login</Link>
          </LoginLink>
        </ResetContainer>
      ) : (
        // Render password reset form (PasswordForm) if in confirmation phase
        <PasswordForm mode="reset" onCancel={() => navigate('/login')} onSubmit={handleConfirmReset} />
      )}
    </AuthLayout>
  );
};

export default ResetPasswordPage;

const ResetContainer = styled.div`
  width: 100%;
  max-width: 400px;
  margin: 0 auto;
`;

const FormGroup = styled.div`
  margin-bottom: 1.5rem;
`;

const SuccessMessage = styled.div`
  margin: 1.5rem 0;
  text-align: center;
  color: var(--color-success);
`;

const LoginLink = styled.div`
  margin-top: 1.5rem;
  text-align: center;
  font-size: 0.875rem;
`;