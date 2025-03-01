import { configureStore } from '@reduxjs/toolkit'; //  ^1.9.0
import { waitFor } from '@testing-library/react'; //  ^13.4.0
import { authSlice, authReducer, authActions } from '../../../store/auth/authSlice';
import { loginUser, logoutUser, refreshAuthToken } from '../../../store/auth/authThunks';
import { AuthState, User, LoginCredentials } from '../../../types/auth';
import { setupStore } from '../../testUtils';

// Mock the auth service functions
jest.mock('../../../store/auth/authThunks', () => ({
  loginUser: jest.fn(),
  logoutUser: jest.fn(),
  refreshAuthToken: jest.fn(),
}));

describe('auth slice', () => {
  it('test initial state', () => {
    const store = setupStore();
    const state = store.getState().auth;
    expect(state.user).toBeNull();
    expect(state.isAuthenticated).toBe(false);
    expect(state.loading).toBe(false);
    expect(state.error).toBeNull();
  });

  it('test setUser action', () => {
    const store = setupStore();
    const mockUser: User = {
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
    };
    store.dispatch(authActions.setUser(mockUser));
    const state = store.getState().auth;
    expect(state.user).toEqual(mockUser);
    expect(state.isAuthenticated).toBe(true);
    expect(state.loading).toBe(false);
    expect(state.error).toBeNull();
  });

  it('test clearUser action', () => {
    const store = setupStore({
      auth: {
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
        loading: false,
        error: null,
        mfaRequired: false,
        mfaToken: null
      },
    });
    store.dispatch(authActions.logout());
    const state = store.getState().auth;
    expect(state.user).toBeNull();
    expect(state.token).toBeNull();
    expect(state.refreshToken).toBeNull();
    expect(state.isAuthenticated).toBe(false);
    expect(state.loading).toBe(false);
    expect(state.error).toBeNull();
    expect(state.mfaRequired).toBe(false);
    expect(state.mfaToken).toBeNull();
  });

  it('test loginUser thunk', async () => {
    const mockLoginUser = loginUser as jest.Mock;
    mockLoginUser.mockImplementation(async () => ({
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
      requiresTwoFactor: false,
      twoFactorToken: null
    }));

    const store = setupStore();
    const credentials: LoginCredentials = {
      email: 'test@example.com',
      password: 'password',
    };
    const result = await store.dispatch(loginUser(credentials));

    expect(store.getState().auth.loading).toBe(false);
    expect(store.getState().auth.user).toEqual({
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
    });
    expect(store.getState().auth.isAuthenticated).toBe(true);
  });

  it('test logoutUser thunk', async () => {
    const mockLogoutUser = logoutUser as jest.Mock;
    mockLogoutUser.mockImplementation(async () => Promise.resolve());

    const store = setupStore({
      auth: {
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
        loading: false,
        error: null,
        mfaRequired: false,
        mfaToken: null
      },
    });
    await store.dispatch(logoutUser());

    expect(store.getState().auth.loading).toBe(false);
    expect(store.getState().auth.user).toBeNull();
    expect(store.getState().auth.isAuthenticated).toBe(false);
  });

  it('test refreshUserToken thunk', async () => {
    const mockRefreshUserToken = refreshAuthToken as jest.Mock;
    mockRefreshUserToken.mockImplementation(async () => ({
      token: 'new-test-token',
      refreshToken: 'new-test-refresh-token',
    }));

    const store = setupStore({
      auth: {
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
        loading: false,
        error: null,
        mfaRequired: false,
        mfaToken: null
      },
    });
    await store.dispatch(refreshAuthToken());

    expect(store.getState().auth.loading).toBe(false);
    expect(store.getState().auth.token).toBe('new-test-token');
    expect(store.getState().auth.refreshToken).toBe('new-test-refresh-token');
    expect(store.getState().auth.isAuthenticated).toBe(true);
  });
});