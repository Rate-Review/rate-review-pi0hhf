import React, { useEffect } from 'react'; // Core React library
import { Provider } from 'react-redux'; // Redux store provider
import { QueryClientProvider } from '@tanstack/react-query' //  ^4.29.0
import { ReactQueryDevtools } from '@tanstack/react-query-devtools' //  ^4.29.0
import { ThemeProvider as StyledThemeProvider } from 'styled-components' //  ^5.3.6
import { GlobalStyles } from './styles/GlobalStyles';
import AppRoutes from './routes'; // Main routing component
import { ThemeProvider } from './context/ThemeContext'; // Context provider for theme management
import { AIProvider } from './context/AIContext'; // Context provider for AI functionality
import { FeatureFlagProvider } from './context/FeatureFlagContext'; // Context provider for feature flags
import { OrganizationProvider } from './context/OrganizationContext'; // Context provider for organization data
import { PermissionProvider } from './context/PermissionContext'; // Context provider for user permissions
import ErrorBoundary from './components/common/ErrorBoundary'; // Error boundary component
import queryClient from './api/queryClient'; // React Query client

// LD1: Main application component that sets up providers and routing
const App: React.FC = () => {
  // LD1: Set up process.env check for development environment
  const isDevelopment = process.env.NODE_ENV === 'development';

  // LD1: Return the application component tree with all required providers
  return (
    // LD1: Wrap the application in StrictMode for development checks
    <React.StrictMode>
      {/* LD1: Set up QueryClientProvider for React Query functionality */}
      <QueryClientProvider client={queryClient}>
        {/* LD1: Include ReactQueryDevtools in development mode */}
        {isDevelopment && (
          <ReactQueryDevtools initialIsOpen={false} />
        )}
        {/* LD1: Set up ThemeProvider for application theming */}
        <ThemeProvider>
          <StyledThemeProvider theme={theme}>
            {/* LD1: Apply GlobalStyles for consistent styling across the app */}
            <GlobalStyles />
            {/* LD1: Set up feature flag provider for feature toggles */}
            <FeatureFlagProvider>
              {/* LD1: Set up organization context provider */}
              <OrganizationProvider>
                {/* LD1: Set up permission context provider */}
                <PermissionProvider>
                  {/* LD1: Set up AI context provider for AI functionality */}
                  <AIProvider>
                    {/* LD1: Wrap the entire application in ErrorBoundary for error handling */}
                    <ErrorBoundary>
                      {/* LD1: Render the AppRoutes component as the main content */}
                      <AppRoutes />
                    </ErrorBoundary>
                  </AIProvider>
                </PermissionProvider>
              </OrganizationProvider>
            </FeatureFlagProvider>
          </StyledThemeProvider>
        </ThemeProvider>
      </QueryClientProvider>
    </React.StrictMode>
  );
};

// IE3: Be generous about your exports so long as it doesn't create a security risk.
export default App;