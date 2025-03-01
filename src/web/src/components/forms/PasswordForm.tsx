import React, { useState, useEffect } from 'react'; //  ^18.2.0
import { z } from 'zod'; //  ^3.22.2
import { useForm } from 'react-hook-form'; //  ^7.45.4
import { zodResolver } from '@hookform/resolvers/zod'; //  ^3.3.1
import TextField from '../common/TextField';
import Button from '../common/Button';
import Alert from '../common/Alert';
import ProgressBar from '../common/ProgressBar';
import { useAuth } from '../../hooks/useAuth';
import theme from '../../theme';

/**
 * Interface defining the properties for the PasswordForm component
 */
interface PasswordFormProps {
  mode: 'change' | 'reset';
  onCancel?: () => void;
}

/**
 * Calculates password strength based on length and complexity
 * @param password - Password to evaluate
 * @returns Score from 0-100 representing password strength
 */
const calculatePasswordStrength = (password: string): number => {
  let score = 0;

  // Add points based on password length (longer = more points)
  if (password.length >= 8) score += 20;
  if (password.length >= 12) score += 20;
  if (password.length >= 16) score += 20;

  // Add points for containing uppercase letters
  if (/[A-Z]/.test(password)) score += 10;

  // Add points for containing lowercase letters
  if (/[a-z]/.test(password)) score += 10;

  // Add points for containing numbers
  if (/[0-9]/.test(password)) score += 10;

  // Add points for containing special characters
  if (/[^A-Za-z0-9]/.test(password)) score += 10;

  // Add bonus points for using multiple character types
  const uniqueChars = new Set(password.split('')).size;
  if (uniqueChars >= 10) score += 10;

  // Return final score capped at 100
  return Math.min(score, 100);
};

/**
 * Returns a color based on password strength score
 * @param strength - Password strength score
 * @returns Color code (error, warning, or success)
 */
const getStrengthColor = (strength: number): string => {
  if (strength < 40) return 'error';
  if (strength < 70) return 'warning';
  return 'success';
};

/**
 * Returns a descriptive label based on password strength score
 * @param strength - Password strength score
 * @returns Descriptive label (Weak, Moderate, Strong)
 */
const getStrengthLabel = (strength: number): string => {
  if (strength < 40) return 'Weak';
  if (strength < 70) return 'Moderate';
  return 'Strong';
};

/**
 * Form component for changing or resetting user passwords with validation and feedback
 * @param props - PasswordFormProps
 * @returns Rendered form component
 */
const PasswordForm: React.FC<PasswordFormProps> = ({ mode, onCancel }) => {
  // Define password validation schema using zod (min length 12, 3 of 4 complexity types)
  const passwordSchema = z.string()
    .min(12, { message: 'Password must be at least 12 characters' })
    .refine((password) => {
      const hasUppercase = /[A-Z]/.test(password);
      const hasLowercase = /[a-z]/.test(password);
      const hasNumbers = /[0-9]/.test(password);
      const hasSymbols = /[^A-Za-z0-9]/.test(password);
      const complexityCount = [hasUppercase, hasLowercase, hasNumbers, hasSymbols].filter(Boolean).length;
      return complexityCount >= 3;
    }, {
      message: 'Password must contain at least 3 of the following: uppercase letters, lowercase letters, numbers, and symbols',
    });

  // Define form schema combining password fields with appropriate validation
  const formSchema = z.object({
    currentPassword: mode === 'change' ? z.string().min(1, { message: 'Current password is required' }) : z.string().optional(),
    newPassword: passwordSchema,
    confirmPassword: passwordSchema,
  }).refine((data) => data.newPassword === data.confirmPassword, {
    message: "Passwords don't match",
    path: ['confirmPassword'], // Path to the confirmPassword field
  });

  // Define form type based on schema
  type FormData = z.infer<typeof formSchema>;

  // Initialize form using react-hook-form with zodResolver
  const {
    register,
    handleSubmit,
    watch,
    formState: { errors, isSubmitting, isValid },
  } = useForm<FormData>({
    resolver: zodResolver(formSchema),
    mode: 'onChange',
  });

  // Access authentication functions from useAuth hook
  const { changePassword, resetPassword } = useAuth();

  // Track loading state during submission
  const [loading, setLoading] = useState(false);

  // Track error state for API errors
  const [apiError, setApiError] = useState<string | null>(null);

  // Track success state for form submission
  const [success, setSuccess] = useState(false);

  // Track password strength state
  const newPasswordValue = watch('newPassword');
  const [passwordStrength, setPasswordStrength] = useState(0);

  // Handle form submission based on mode (change or reset)
  const onSubmit = async (data: FormData) => {
    setLoading(true);
    setApiError(null);
    setSuccess(false);

    try {
      if (mode === 'change') {
        // Change password flow
        await changePassword({
          currentPassword: data.currentPassword || '',
          newPassword: data.newPassword,
        });
        setSuccess(true);
      } else {
        // Reset password flow
        await resetPassword({
          token: '', // Token needs to be passed here
          password: data.newPassword,
        });
        setSuccess(true);
      }
    } catch (error: any) {
      setApiError(error.message || 'Failed to submit password form');
    } finally {
      setLoading(false);
    }
  };

  // Calculate password strength when new password changes
  useEffect(() => {
    setPasswordStrength(calculatePasswordStrength(newPasswordValue));
  }, [newPasswordValue]);

  // Render form with appropriate fields based on mode (current password for change mode)
  return (
    <form onSubmit={handleSubmit(onSubmit)}>
      {mode === 'change' && (
        <TextField
          label="Current Password"
          type="password"
          id="currentPassword"
          {...register('currentPassword')}
          error={errors.currentPassword?.message}
          fullWidth
        />
      )}
      <TextField
        label="New Password"
        type="password"
        id="newPassword"
        {...register('newPassword')}
        error={errors.newPassword?.message}
        fullWidth
        helpText={
          <>
            Password Strength: {getStrengthLabel(passwordStrength)}
            <ProgressBar
              value={passwordStrength}
              color={getStrengthColor(passwordStrength)}
              variant="determinate"
              showPercentage={false}
            />
          </>
        }
      />
      <TextField
        label="Confirm New Password"
        type="password"
        id="confirmPassword"
        {...register('confirmPassword')}
        error={errors.confirmPassword?.message}
        fullWidth
      />
      {success && (
        <Alert severity="success" message="Password changed successfully!" />
      )}
      {apiError && <Alert severity="error" message={apiError} />}
      <Button type="submit" disabled={isSubmitting || loading || !isValid}>
        {loading ? 'Submitting...' : 'Submit'}
      </Button>
      {onCancel && (
        <Button variant="text" onClick={onCancel} disabled={loading}>
          Cancel
        </Button>
      )}
    </form>
  );
};

export default PasswordForm;