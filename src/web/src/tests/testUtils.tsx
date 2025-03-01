import { ReactNode } from 'react'; //  ^18.0.0
import { render, screen, waitFor, fireEvent } from '@testing-library/react'; //  ^14.0.0
import userEvent from '@testing-library/user-event'; //  ^14.0.0
import { Provider } from 'react-redux'; //  ^8.0.5
import { configureStore } from '@reduxjs/toolkit'; //  ^1.9.3
import { MemoryRouter } from 'react-router-dom'; //  ^6.8.2
import { rest, setupServer } from 'msw'; //  ^1.0.0
import { QueryClientProvider, QueryClient } from 'react-query'; //  ^3.39.3
import { store as realStore } from '../store';
import { ThemeProvider, ThemeContext } from '../context/ThemeContext';
import { OrganizationProvider } from '../context/OrganizationContext';
import { AIProvider } from '../context/AIContext';
import { PermissionProvider } from '../context/PermissionContext';

/**
 * Custom render function that wraps components with all necessary providers for testing (Redux, Router, Context providers)
 * @param {ReactNode} ui - The UI element (component) to render
 * @param {object} options - Optional parameters for configuring the test environment
 * @returns {object} Returns the standard render object from RTL plus additional helper methods
 */
const renderWithProviders = (ui: ReactNode, options: any = {}) => {
  // LD1: Configure default options for the render function
  const { preloadedState = {}, route = '/', history = undefined } = options;

  // LD1: Set up a memory router with initial entries if provided in options
  const wrapper = ({ children }: { children: ReactNode }) => (
    <MemoryRouter initialEntries={[route]} initialIndex={0} history={history}>
      {children}
    </MemoryRouter>
  );

  // LD1: Create a Redux store with preloaded state if provided in options
  const store = configureStore({
    reducer: (realStore as any).reducer,
    middleware: (getDefaultMiddleware) => getDefaultMiddleware({
      serializableCheck: false,
    }),
    preloadedState,
  });

  // LD1: Set up a React Query client for API requests
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: {
        retry: false,
      },
    },
  });

  // LD1: Render the component wrapped with all providers (Redux, Router, ThemeProvider, OrganizationProvider, AIProvider, PermissionProvider, QueryClientProvider)
  const renderResult = render(
    <Provider store={store}>
      <QueryClientProvider client={queryClient}>
        <ThemeProvider>
          <OrganizationProvider>
            <AIProvider>
              <PermissionProvider>
                {ui}
              </PermissionProvider>
            </AIProvider>
          </OrganizationProvider>
        </ThemeProvider>
      </QueryClientProvider>
    </Provider>,
    { wrapper }
  );

  // LD1: Return the render result with additional utility methods
  return {
    ...renderResult,
    store,
    queryClient,
  };
};

/**
 * Creates a Redux store with optional preloaded state for testing
 * @param {object} preloadedState - Optional preloaded state for the store
 * @returns {object} A configured Redux store with the preloaded state
 */
const createTestStore = (preloadedState: any = {}) => {
  // LD1: Import the reducer from the main store
  const reducer = (realStore as any).reducer;

  // LD1: Create and return a store using configureStore with the preloaded state
  return configureStore({
    reducer,
    middleware: (getDefaultMiddleware) => getDefaultMiddleware({
      serializableCheck: false,
    }),
    preloadedState,
  });
};

/**
 * Mocks the useAuth hook for testing components that depend on authentication
 * @param {object} mockValues - Mock values to return from the useAuth hook
 * @returns {void} Does not return a value
 */
const mockUseAuth = (mockValues: any) => {
  // LD1: Create a mock implementation of useAuth hook
  jest.mock('../hooks/useAuth', () => ({
    useAuth: () => ({
      isAuthenticated: true, // Set up default authentication values
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
      loading: false,
      error: null,
      login: jest.fn(),
      logout: jest.fn(),
      verifyMfa: jest.fn(),
      resetPassword: jest.fn(),
      refreshTokenSilently: jest.fn(),
      checkAuthStatus: jest.fn(),
      hasRole: jest.fn(),
      isOrgType: jest.fn(),
      ...mockValues, // Override defaults with provided mockValues
    }),
  }));
};

/**
 * Mocks the usePermissions hook for testing components with permission checks
 * @param {object} mockPermissions - Mock permissions to return from the usePermissions hook
 * @returns {void} Does not return a value
 */
const mockUsePermissions = (mockPermissions: string[]) => {
  // LD1: Create a mock implementation of usePermissions hook
  jest.mock('../hooks/usePermissions', () => ({
    usePermissions: () => ({
      hasPermission: (permission: string) => mockPermissions.includes(permission), // Override default permissions with provided mockPermissions
    }),
  }));
};

/**
 * Sets up API mocks for testing components that make API calls
 * @param {array} handlers - Array of MSW request handlers
 * @returns {object} MSW server instance that can be used to start/stop mocks
 */
const setupApiMocks = (handlers: any) => {
  // LD1: Import the setupServer function from MSW
  // LD1: Create a server with the provided handlers
  const server = setupServer(...handlers);

  // LD1: Return the server instance for use in tests
  return server;
};

/**
 * Utility function to wait for loading states to resolve in tests
 * @returns {Promise<void>} Resolves when loading is complete
 */
const waitForLoadingToFinish = async () => {
  // LD1: Use waitFor to check for absence of loading indicators
  await waitFor(() => {
    const loadingIndicators = screen.queryAllByText(/Loading/i);
    expect(loadingIndicators).toHaveLength(0);
  });

  // LD1: Return a promise that resolves when loading is complete
  return Promise.resolve();
};

export { renderWithProviders, createTestStore, mockUseAuth, mockUsePermissions, setupApiMocks, waitForLoadingToFinish };