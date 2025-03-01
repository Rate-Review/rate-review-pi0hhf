import React, {
  createContext,
  useContext,
  useState,
  useEffect,
  useCallback,
  ReactNode,
  FC,
} from 'react'; // react v18.0.0
import { useAuth } from '../hooks/useAuth';
import { useOrganization } from '../context/OrganizationContext';
import { getItem, setItem } from '../utils/storage';

// Define a type for available feature flag keys
interface FeatureKey {
  REAL_TIME_NEGOTIATION: string;
  AI_RECOMMENDATIONS: string;
  UNICOURT_INTEGRATION: string;
  ADVANCED_ANALYTICS: string;
  CUSTOM_REPORTS: string;
  OCG_NEGOTIATION: string;
  MOBILE_VIEWS: string;
}

// Define default feature flags
const FEATURE_FLAGS: FeatureKey = {
  REAL_TIME_NEGOTIATION: 'real_time_negotiation',
  AI_RECOMMENDATIONS: 'ai_recommendations',
  UNICOURT_INTEGRATION: 'unicourt_integration',
  ADVANCED_ANALYTICS: 'advanced_analytics',
  CUSTOM_REPORTS: 'custom_reports',
  OCG_NEGOTIATION: 'ocg_negotiation',
  MOBILE_VIEWS: 'mobile_views',
};

// Define storage key for user-specific feature flag preferences
const STORAGE_KEY_FEATURE_PREFS = 'feature_preferences';

// Define the type for feature flag context values
interface FeatureFlagContextType {
  features: Record<string, boolean>;
  isEnabled: (featureKey: string) => boolean;
  toggleFeature: (featureKey: string, enabled: boolean) => void;
}

// Create a context for feature flags
export const FeatureFlagContext = createContext<FeatureFlagContextType | undefined>(
  undefined
);

// Define the props for the FeatureFlagProvider component
interface FeatureFlagProviderProps {
  children: ReactNode;
  initialFlags?: Record<string, boolean>;
}

// Create a provider component for the feature flag context
export const FeatureFlagProvider: FC<FeatureFlagProviderProps> = ({
  children,
  initialFlags,
}) => {
  // Access the authentication context
  const { isAuthenticated, currentUser, hasRole } = useAuth();

  // Access the organization context
  const { currentOrganization } = useOrganization();

  // Define state for feature flags
  const [features, setFeatures] = useState<Record<string, boolean>>(() => {
    // Load saved user preferences from localStorage
    const savedPreferences = getItem<Record<string, boolean>>(STORAGE_KEY_FEATURE_PREFS, {});

    // Merge default flags, environment flags, and user preferences
    const mergedFlags: Record<string, boolean> = {
      ...Object.values(FEATURE_FLAGS).reduce((acc: Record<string, boolean>, key) => {
        acc[key] = false; // Default all flags to false
        return acc;
      }, {}),
      ...(initialFlags || {}), // Override with initial flags
      ...(process.env.REACT_APP_FEATURE_FLAGS ? JSON.parse(process.env.REACT_APP_FEATURE_FLAGS) : {}), // Override with environment flags
      ...(savedPreferences || {}), // Override with saved preferences
    };

    return mergedFlags;
  });

  // Define function to check if a feature is enabled
  const isEnabled = useCallback(
    (featureKey: string): boolean => {
      return features[featureKey] || false;
    },
    [features]
  );

  // Define function to toggle a feature flag
  const toggleFeature = useCallback(
    (featureKey: string, enabled: boolean) => {
      setFeatures((prevFeatures) => ({
        ...prevFeatures,
        [featureKey]: enabled,
      }));
    },
    []
  );

  // Use useEffect to save user preferences when they change
  useEffect(() => {
    if (isAuthenticated && currentUser) {
      setItem(STORAGE_KEY_FEATURE_PREFS, features);
    }
  }, [features, isAuthenticated, currentUser]);

  // Apply role-based flag rules based on user role
  useEffect(() => {
    if (isAuthenticated && currentUser) {
      const roleBasedFlags: Record<string, boolean> = {};

      // Example: Enable advanced analytics for administrators
      if (hasRole('OrganizationAdministrator') || hasRole('SystemAdministrator')) {
        roleBasedFlags[FEATURE_FLAGS.ADVANCED_ANALYTICS] = true;
      }

      // Merge role-based flags with existing flags
      setFeatures((prevFeatures) => ({
        ...prevFeatures,
        ...roleBasedFlags,
      }));
    }
  }, [isAuthenticated, currentUser, hasRole]);

  // Apply organization-specific flag rules
  useEffect(() => {
    if (currentOrganization) {
      const orgSpecificFlags: Record<string, boolean> = {};

      // Example: Enable UniCourt integration for specific organizations
      if (currentOrganization.name === 'Acme Corp') {
        orgSpecificFlags[FEATURE_FLAGS.UNICOURT_INTEGRATION] = true;
      }

      // Merge organization-specific flags with existing flags
      setFeatures((prevFeatures) => ({
        ...prevFeatures,
        ...orgSpecificFlags,
      }));
    }
  }, [currentOrganization]);

  // Define the context value
  const contextValue: FeatureFlagContextType = {
    features,
    isEnabled,
    toggleFeature,
  };

  // Return the provider with the context value
  return (
    <FeatureFlagContext.Provider value={contextValue}>
      {children}
    </FeatureFlagContext.Provider>
  );
};

// Create a custom hook to access the feature flag context
export const useFeatureFlags = (): FeatureFlagContextType => {
  const context = useContext(FeatureFlagContext);
  if (!context) {
    throw new Error('useFeatureFlags must be used within a FeatureFlagProvider');
  }
  return context;
};