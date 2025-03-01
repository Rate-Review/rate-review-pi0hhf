import React, { useState, useEffect } from 'react'; //  ^18.2.0
import { useNavigate } from 'react-router-dom'; //  ^6.10.0
import styled from 'styled-components'; //  ^5.3.10
import { useAuth } from '../../hooks/useAuth';
import { authService } from '../../services/auth';
import { MFASetupResponse } from '../../types/auth';
import Button from '../../components/common/Button';
import TextField from '../../components/common/TextField';
import Alert from '../../components/common/Alert';

/**
 * A page component that handles multi-factor authentication (MFA) setup for users
 * in the Justice Bid Rate Negotiation System. It provides a guided setup process
 * for generating and scanning QR codes, verifying MFA codes, and displaying backup
 * codes for secure user authentication.
 */
const MFASetupPage: React.FC = () => {
  // Access the navigate function from react-router-dom
  const navigate = useNavigate();

  // Access authentication functions and state from the useAuth hook
  const { verifyMfa } = useAuth();

  // State variables for managing the MFA setup process
  const [loading, setLoading] = useState<boolean>(false);
  const [setupResponse, setSetupResponse] = useState<MFASetupResponse | null>(null);
  const [verificationCode, setVerificationCode] = useState<string>('');
  const [error, setError] = useState<string>('');
  const [verificationSuccess, setVerificationSuccess] = useState<boolean>(false);
  const [setupStep, setSetupStep] = useState<number>(1);
  const [backupCodes, setBackupCodes] = useState<string[]>([]);

  // Effect to initiate MFA setup on component mount
  useEffect(() => {
    // Define an async function to handle the MFA setup process
    const setupMFA = async () => {
      setLoading(true); // Set loading state to true
      setError(''); // Clear any existing error messages
      try {
        // Call authService.setupMFA() to initiate MFA setup
        const response = await authService.setupMFA();
        setSetupResponse(response); // Store setup response in state
      } catch (err: any) {
        setError(err.message || 'Failed to setup MFA. Please try again.'); // Set error message state
      } finally {
        setLoading(false); // Set loading state to false regardless of outcome
      }
    };

    setupMFA(); // Call the setupMFA function
  }, []);

  /**
   * Handles the verification of the user-entered MFA code
   */
  const handleVerifyCode = async () => {
    setLoading(true); // Set loading state to true
    setError(''); // Clear any existing error messages

    // Validate the code is a 6-digit number
    if (!/^\d{6}$/.test(verificationCode)) {
      setError('Verification code must be a 6-digit number.');
      setLoading(false); // Set loading state to false
      return;
    }

    try {
      // Call authService.verifyMFA with the code and secret from the setup response
      if (setupResponse?.secret) {
        await verifyMfa({ code: verificationCode, secret: setupResponse?.secret });
        setVerificationSuccess(true); // Set verification success state to true
        setBackupCodes(setupResponse?.backupCodes || []); // Store backup codes
        setSetupStep(2);
      }
    } catch (err: any) {
      setError(err.message || 'Failed to verify code. Please try again.'); // Set error message state
    } finally {
      setLoading(false); // Set loading state to false regardless of outcome
    }
  };

  /**
   * Generates and downloads a text file containing the backup codes
   */
  const handleDownloadBackupCodes = () => {
    // Format backup codes as a single string
    const backupCodesText = backupCodes.join('\n');

    // Create a blob with the backup codes
    const blob = new Blob([backupCodesText], { type: 'text/plain' });

    // Create a temporary download link element
    const element = document.createElement('a');
    element.href = URL.createObjectURL(blob);
    element.download = 'backup-codes.txt'; // Set the download filename

    document.body.appendChild(element); // Append to the document
    element.click(); // Simulate click to start download

    document.body.removeChild(element); // Remove the element
    URL.revokeObjectURL(element.href); // Revoke the object URL
  };

  /**
   * Completes the MFA setup process and redirects to the dashboard
   */
  const handleComplete = () => {
    navigate('/dashboard'); // Use navigate function to redirect to dashboard
    // Optionally show a success message toast (via implementation in parent component)
  };

  return (
    <Container>
      <Title>Set Up Multi-Factor Authentication</Title>
      <Description>Enhance your account security by setting up multi-factor authentication.</Description>
      {error && <Alert severity="error" message={error} />}

      {setupStep === 1 && setupResponse && (
        <div>
          <Description>1. Scan the QR code below with your authenticator app (Google Authenticator, Authy, etc.)</Description>
          <QRCodeContainer>
            <QRImage src={setupResponse?.qrCode} alt="QR Code for MFA" />
          </QRCodeContainer>
          <Description>2. If you can't scan the QR code, enter this code manually in your app:</Description>
          <SecretContainer>{setupResponse?.secret}</SecretContainer>
          <Description>3. Enter the 6-digit verification code from your authenticator app:</Description>
          <TextField
            value={verificationCode}
            onChange={(e) => setVerificationCode(e.target.value)}
            placeholder="6-digit code"
            type="text"
            fullWidth
            required
            disabled={loading}
          />
          <ButtonContainer>
            <Button onClick={handleVerifyCode} disabled={loading || verificationCode.length !== 6} fullWidth>
              {loading ? 'Verifying...' : 'Verify Code'}
            </Button>
          </ButtonContainer>
        </div>
      )}

      {setupStep === 2 && verificationSuccess && (
        <div>
          <Alert severity="success" message="MFA setup successful!" />
          <Description>Please save these backup codes. You'll need them if you lose access to your authenticator app.</Description>
          <BackupCodesContainer>
            <BackupCodesList>
              {backupCodes.map(code => (
                <BackupCode key={code}>{code}</BackupCode>
              ))}
            </BackupCodesList>
          </BackupCodesContainer>
          <ButtonContainer>
            <Button onClick={handleDownloadBackupCodes} variant="outline" color="secondary">Download Backup Codes</Button>
            <Button onClick={handleComplete}>Complete Setup</Button>
          </ButtonContainer>
        </div>
      )}

      {loading && !setupResponse && <div>Loading...</div>}
    </Container>
  );
};

export default MFASetupPage;

const Container = styled.div`
  max-width: 500px;
  margin: 2rem auto;
  padding: 2rem;
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
`;

const Title = styled.h1`
  font-size: 1.5rem;
  margin-bottom: 1.5rem;
  text-align: center;
  color: ${props => props.theme.colors.primary};
`;

const Description = styled.p`
  margin-bottom: 1.5rem;
  color: ${props => props.theme.colors.text.secondary};
`;

const QRCodeContainer = styled.div`
  display: flex;
  justify-content: center;
  margin: 2rem 0;
`;

const QRImage = styled.img`
  max-width: 200px;
  border: 1px solid #eee;
`;

const SecretContainer = styled.div`
  margin: 1rem 0;
  padding: 0.75rem;
  background-color: #f5f5f5;
  border-radius: 4px;
  font-family: monospace;
  text-align: center;
`;

const ButtonContainer = styled.div`
  display: flex;
  justify-content: space-between;
  margin-top: 1.5rem;
  gap: 1rem;
`;

const BackupCodesContainer = styled.div`
  margin: 1.5rem 0;
  padding: 1rem;
  background-color: #f5f5f5;
  border-radius: 4px;
  font-family: monospace;
`;

const BackupCodesList = styled.div`
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 0.5rem;
`;

const BackupCode = styled.div`
  padding: 0.5rem;
  background-color: white;
  border: 1px solid #ddd;
  border-radius: 4px;
  text-align: center;
`;