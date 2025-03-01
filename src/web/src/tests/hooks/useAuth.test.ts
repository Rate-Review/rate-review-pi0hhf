import { ReactElement, useEffect } from 'react'; //  ^18.0.0
import { renderHook, act, waitFor } from '@testing-library/react'; //  ^14.0.0
import { store } from '@reduxjs/toolkit'; //  ^1.9.5
import {
  renderWithProviders,
  createTestStore,
} from '../testUtils';
import { authActions } from '../../store/auth/authSlice';
import {
  loginUser,
  logoutUser,
  refreshToken,
  verifyMfa,
  resetPassword,
  checkAuth,
} from '../../store/auth/authThunks';
import { useAuth } from '../../hooks/useAuth';
import { UserRole } from '../../types/user';

// Mock the auth thunks
jest.mock('../../store/auth/authThunks', () => ({
  loginUser: jest.fn(),
  logoutUser: jest.fn(),
  refreshToken: jest.fn(),
  verifyMfa: jest.fn(),
  resetPassword: jest.fn(),
  checkAuth: jest.fn(),
}));

// TestComponent helper component that uses the useAuth hook and exposes its returned values
const TestComponent = (props: any): ReactElement => {
  const {
    isAuthenticated,
    currentUser,
    userRole,
    loading,
    error,
    login,
    logout,
    verifyMfa,
    resetPassword,
    refreshTokenSilently,
    checkAuthStatus,
    hasRole,
  } = useAuth();

  return (
    <div data-testid="auth-state">
      <div data-testid="is-authenticated">{String(isAuthenticated)}</div>
      <div data-testid="current-user">{currentUser ? JSON.stringify(currentUser) : 'null'}</div>
      <div data-testid="user-role">{userRole}</div>
      <div data-testid="loading">{String(loading)}</div>
      <div data-testid="error">{error}</div>
      <button data-testid="login-button" onClick={() => login(props.loginCredentials)}>Login</button>
      <button data-testid="logout-button" onClick={() => logout()}>Logout</button>
      <button data-testid="verify-mfa-button" onClick={() => verifyMfa(props.mfaCredentials)}>Verify MFA</button>
	  <button data-testid="reset-password-button" onClick={() => resetPassword(props.resetPasswordCredentials)}>Reset Password</button>
    </div>
  );
};

describe('useAuth hook', () => {
  it('should return authentication state from Redux store', () => {
    // Create a test Redux store with authenticated state
    const testStore = createTestStore({
      auth: {
        isAuthenticated: true,
        currentUser: {
          id: 'test-user',
          email: 'test@example.com',
          name: 'Test User',
          organizationId: 'test-org',
          role: 'StandardUser',
          permissions: [],
          organization: {
            id: 'test-org',
            name: 'Test Org',
            type: 'Client',
          },
          isContact: false,
          lastVerified: new Date(),
          createdAt: new Date(),
          updatedAt: new Date(),
        },
        userRole: 'StandardUser',
        loading: false,
        error: null,
        mfaRequired: false,
        mfaToken: null,
        isInitialized: true,
        token: 'test-token',
        refreshToken: 'test-refresh-token',
      },
    });

    // Render the test component with the store
    const { getByTestId } = renderWithProviders(<TestComponent />, { preloadedState: testStore.getState() });

    // Assert that isAuthenticated is true
    expect(getByTestId('is-authenticated').textContent).toBe('true');

    // Assert that currentUser matches the expected user object
    expect(getByTestId('current-user').textContent).toBe(JSON.stringify({
      id: 'test-user',
      email: 'test@example.com',
      name: 'Test User',
      organizationId: 'test-org',
      role: 'StandardUser',
      permissions: [],
      organization: {
        id: 'test-org',
        name: 'Test Org',
        type: 'Client',
      },
      isContact: false,
      lastVerified: expect.any(String),
      createdAt: expect.any(String),
      updatedAt: expect.any(String),
    }));

    // Assert that userRole matches the expected role
    expect(getByTestId('user-role').textContent).toBe('StandardUser');
  });

  it('should handle login successfully', async () => {
    // Mock the login thunk to return a successful result
    (loginUser as jest.Mock).mockResolvedValue({
      user: {
        id: 'test-user',
        email: 'test@example.com',
        name: 'Test User',
        organizationId: 'test-org',
        role: 'StandardUser',
        permissions: [],
        organization: {
          id: 'test-org',
          name: 'Test Org',
          type: 'Client',
        },
        isContact: false,
        lastVerified: new Date(),
        createdAt: new Date(),
        updatedAt: new Date(),
      },
      token: 'test-token',
      refreshToken: 'test-refresh-token',
      isAuthenticated: true,
      mfaRequired: false,
      mfaToken: null,
    });

    // Render the test component
    const { getByTestId } = renderWithProviders(<TestComponent loginCredentials={{ email: 'test@example.com', password: 'password' }} />);

    // Trigger the login function with test credentials
    act(() => {
      const loginButton = getByTestId('login-button');
      loginButton.click();
    });

    // Assert that the login thunk was called with correct credentials
    expect(loginUser).toHaveBeenCalledWith({ email: 'test@example.com', password: 'password' });

    // Assert that isAuthenticated changes to true after successful login
    await waitFor(() => {
      expect(getByTestId('is-authenticated').textContent).toBe('true');
    });
  });

  it('should handle login failure', async () => {
    // Mock the login thunk to return a rejected promise with an error
    (loginUser as jest.Mock).mockRejectedValue(new Error('Invalid credentials'));

    // Render the test component
    const { getByTestId } = renderWithProviders(<TestComponent loginCredentials={{ email: 'test@example.com', password: 'password' }} />);

    // Trigger the login function with test credentials
    act(() => {
      const loginButton = getByTestId('login-button');
      loginButton.click();
    });

    // Assert that the login thunk was called
    expect(loginUser).toHaveBeenCalled();

    // Assert that error state is populated with the error message
    await waitFor(() => {
      expect(getByTestId('error').textContent).toBe('Error: Invalid credentials');
    });

    // Assert that isAuthenticated remains false
    expect(getByTestId('is-authenticated').textContent).toBe('false');
  });

  it('should handle MFA requirement during login', async () => {
    // Mock the login thunk to return a result indicating MFA is required
    (loginUser as jest.Mock).mockResolvedValue({ mfaRequired: true, mfaToken: 'mfa-token' });

    // Render the test component
    const { getByTestId } = renderWithProviders(<TestComponent loginCredentials={{ email: 'test@example.com', password: 'password' }} />);

    // Trigger the login function with test credentials
    act(() => {
      const loginButton = getByTestId('login-button');
      loginButton.click();
    });

    // Assert that the login thunk was called
    expect(loginUser).toHaveBeenCalled();

    // Assert that mfaRequired is set to true
    // Assert that isAuthenticated remains false
    await waitFor(() => {
        expect(getByTestId('is-authenticated').textContent).toBe('false');
    });
  });

  it('should handle MFA verification successfully', async () => {
    // Set initial store state with mfaRequired true
    const preloadedState = {
      auth: {
        isAuthenticated: false,
        currentUser: null,
        userRole: null,
        loading: false,
        error: null,
        mfaRequired: true,
        mfaToken: 'mfa-token',
        isInitialized: true,
        token: null,
        refreshToken: null,
      },
    };

    // Mock the verifyMfa thunk to return a successful result
    (verifyMfa as jest.Mock).mockResolvedValue({
      user: {
        id: 'test-user',
        email: 'test@example.com',
        name: 'Test User',
        organizationId: 'test-org',
        role: 'StandardUser',
        permissions: [],
        organization: {
          id: 'test-org',
          name: 'Test Org',
          type: 'Client',
        },
        isContact: false,
        lastVerified: new Date(),
        createdAt: new Date(),
        updatedAt: new Date(),
      },
      token: 'test-token',
      refreshToken: 'test-refresh-token',
      isAuthenticated: true,
      mfaRequired: false,
      mfaToken: null,
    });

    // Render the test component
    const { getByTestId } = renderWithProviders(<TestComponent mfaCredentials={{ code: '123456', sessionId: 'mfa-token' }} />, { preloadedState });

    // Trigger the verifyMfa function with test code
    act(() => {
      const verifyMfaButton = getByTestId('verify-mfa-button');
      verifyMfaButton.click();
    });

    // Assert that the verifyMfa thunk was called with correct code
    expect(verifyMfa).toHaveBeenCalledWith({ code: '123456', sessionId: 'mfa-token' });

    // Assert that isAuthenticated changes to true after successful verification
    await waitFor(() => {
      expect(getByTestId('is-authenticated').textContent).toBe('true');
    });
  });

  it('should handle logout correctly', async () => {
    // Create a test Redux store with authenticated state
    const testStore = createTestStore({
      auth: {
        isAuthenticated: true,
        currentUser: {
          id: 'test-user',
          email: 'test@example.com',
          name: 'Test User',
          organizationId: 'test-org',
          role: 'StandardUser',
          permissions: [],
          organization: {
            id: 'test-org',
            name: 'Test Org',
            type: 'Client',
          },
          isContact: false,
          lastVerified: new Date(),
          createdAt: new Date(),
          updatedAt: new Date(),
        },
        userRole: 'StandardUser',
        loading: false,
        error: null,
        mfaRequired: false,
        mfaToken: null,
        isInitialized: true,
        token: 'test-token',
        refreshToken: 'test-refresh-token',
      },
    });

    // Mock the logout thunk to return a successful result
    (logoutUser as jest.Mock).mockResolvedValue({});

    // Render the test component with the store
    const { getByTestId } = renderWithProviders(<TestComponent />, { preloadedState: testStore.getState() });

    // Trigger the logout function
    act(() => {
      const logoutButton = getByTestId('logout-button');
      logoutButton.click();
    });

    // Assert that the logout thunk was called
    expect(logoutUser).toHaveBeenCalled();

    // Assert that isAuthenticated changes to false after logout
    await waitFor(() => {
      expect(getByTestId('is-authenticated').textContent).toBe('false');
    });
  });

  it('should refresh token silently', async () => {
    // Create a test Redux store with authenticated state
    const testStore = createTestStore({
      auth: {
        isAuthenticated: true,
        currentUser: {
          id: 'test-user',
          email: 'test@example.com',
          name: 'Test User',
          organizationId: 'test-org',
          role: 'StandardUser',
          permissions: [],
          organization: {
            id: 'test-org',
            name: 'Test Org',
            type: 'Client',
          },
          isContact: false,
          lastVerified: new Date(),
          createdAt: new Date(),
          updatedAt: new Date(),
        },
        userRole: 'StandardUser',
        loading: false,
        error: null,
        mfaRequired: false,
        mfaToken: null,
        isInitialized: true,
        token: 'test-token',
        refreshToken: 'test-refresh-token',
      },
    });

    // Mock the refreshToken thunk to return a successful result
    (refreshToken as jest.Mock).mockResolvedValue({});

    // Render the test component with the store
    const { result } = renderHook(() => useAuth(), { wrapper: ({ children }) => <Provider store={testStore}>{children}</Provider> });

    // Trigger the refreshTokenSilently function
    act(() => {
      result.current.refreshTokenSilently();
    });

    // Assert that the refreshToken thunk was called
    expect(refreshToken).toHaveBeenCalled();

    // Assert that isAuthenticated remains true
    expect(testStore.getState().auth.isAuthenticated).toBe(true);
  });

  it('should check auth status on mount', () => {
    // Mock the checkAuth thunk
    (checkAuth as jest.Mock).mockResolvedValue({});

    // Render the test component
    renderWithProviders(<TestComponent />);

    // Assert that the checkAuth thunk was called once on mount
    expect(checkAuth).toHaveBeenCalledTimes(1);
  });

  it('should provide hasRole function that checks user roles correctly', () => {
    // Create a test Redux store with a user having a specific role
    const testStore = createTestStore({
      auth: {
        isAuthenticated: true,
        currentUser: {
          id: 'test-user',
          email: 'test@example.com',
          name: 'Test User',
          organizationId: 'test-org',
          role: 'RateAdministrator',
          permissions: [],
          organization: {
            id: 'test-org',
            name: 'Test Org',
            type: 'Client',
          },
          isContact: false,
          lastVerified: new Date(),
          createdAt: new Date(),
          updatedAt: new Date(),
        },
        userRole: 'RateAdministrator',
        loading: false,
        error: null,
        mfaRequired: false,
        mfaToken: null,
        isInitialized: true,
        token: 'test-token',
        refreshToken: 'test-refresh-token',
      },
    });

    // Render the test component with the store
    const { result } = renderHook(() => useAuth(), { wrapper: ({ children }) => <Provider store={testStore}>{children}</Provider> });

    // Test hasRole function with matching role
    const hasMatchingRole = result.current.hasRole(UserRole.RATE_ADMINISTRATOR);

    // Assert that hasRole returns true for matching role
    expect(hasMatchingRole).toBe(true);

    // Test hasRole function with non-matching role
    const hasNonMatchingRole = result.current.hasRole(UserRole.STANDARD_USER);

    // Assert that hasRole returns false for non-matching role
    expect(hasNonMatchingRole).toBe(false);
  });

  it('should handle resetPassword correctly', async () => {
    // Mock the resetPassword thunk to return a successful result
    (resetPassword as jest.Mock).mockResolvedValue({});

    // Render the test component
    const { getByTestId } = renderWithProviders(<TestComponent resetPasswordCredentials={{ email: 'test@example.com' }} />);

    // Trigger the resetPassword function with test data
    act(() => {
      const resetButton = getByTestId('reset-password-button');
      resetButton.click();
    });

    // Assert that the resetPassword thunk was called with correct data
    expect(resetPassword).toHaveBeenCalledWith({ email: 'test@example.com' });
  });
});