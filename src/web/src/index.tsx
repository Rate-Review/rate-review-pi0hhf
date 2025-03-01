import React from 'react'; // Core React library //  ^18.0+
import ReactDOM from 'react-dom/client'; // React DOM rendering //  ^18.0+
import { Provider } from 'react-redux'; // Redux store provider //  ^8.0+
import { QueryClientProvider } from 'react-query' //  ^4.0+
import App from './App'; // Main application component
import store from './store'; // Redux store configuration
import { ThemeProvider } from './context/ThemeContext'; // Theme context provider
import { AIProvider } from './context/AIContext'; // AI functionality context provider
import { FeatureFlagProvider } from './context/FeatureFlagContext'; // Feature flag context provider
import { OrganizationProvider } from './context/OrganizationContext'; // Organization context provider
import { PermissionProvider } from './context/PermissionContext'; // Permission context provider
import { queryClient } from './api/queryClient'; // React Query client configuration
import './styles/global.css'; // Global CSS styles

// LD1: Create a React DOM root for rendering the application
const root = ReactDOM.createRoot(document.getElementById('root') as HTMLElement);

// LD1: Render the application with all necessary providers
root.render(
  // LD1: Wrap the application in StrictMode for development checks
  <React.StrictMode>
    {/* LD1: Set up QueryClientProvider for React Query functionality */}
    <QueryClientProvider client={queryClient}>
      {/* LD1: Set up ThemeProvider for application theming */}
      <ThemeProvider>
        {/* LD1: Set up FeatureFlagProvider for feature toggles */}
        <FeatureFlagProvider>
          {/* LD1: Set up OrganizationProvider for organization data */}
          <OrganizationProvider>
            {/* LD1: Set up PermissionProvider for user permissions */}
            <PermissionProvider>
              {/* LD1: Set up AIProvider for AI functionality */}
              <AIProvider>
                {/* LD1: Set up Redux Provider for global state management */}
                <Provider store={store}>
                  {/* LD1: Render the main App component */}
                  <App />
                </Provider>
              </AIProvider>
            </PermissionProvider>
          </OrganizationProvider>
        </FeatureFlagProvider>
      </ThemeProvider>
    </QueryClientProvider>
  </React.StrictMode>
);