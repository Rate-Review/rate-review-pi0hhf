import React, {
  createContext,
  useContext,
  useState,
  useEffect,
  useCallback,
  ReactNode,
  FC,
} from 'react'; // react v18.2.0
import {
  Organization,
  OrganizationType,
  OrganizationSettings,
  Office,
  Department,
  PeerGroupRelation,
} from '../types/organization';
import useOrganizations from '../hooks/useOrganizations';
import { useAuth } from '../hooks/useAuth';

/**
 * @interface OrganizationContextType
 * @description Type definition for organization context object
 */
export interface OrganizationContextType {
  currentOrganization: Organization | null;
  organizations: Organization[];
  settings: OrganizationSettings | null;
  offices: Office[];
  departments: Department[];
  peerGroups: PeerGroupRelation[];
  isLoading: boolean;
  error: string | null;
  setCurrentOrganization: (organization: Organization | null) => void;
  updateOrganizationSettings: (settings: Partial<OrganizationSettings>) => Promise<void>;
  getOrganizationById: (id: string) => Organization | undefined;
  getOrganizationsByType: (type: OrganizationType) => Organization[];
  createOffice: (office: Partial<Office>) => Promise<void>;
  updateOffice: (officeId: string, officeData: Partial<Office>) => Promise<void>;
  deleteOffice: (officeId: string) => Promise<void>;
  createDepartment: (department: Partial<Department>) => Promise<void>;
  updateDepartment: (departmentId: string, departmentData: Partial<Department>) => Promise<void>;
  deleteDepartment: (departmentId: string) => Promise<void>;
  refreshOrganizationData: () => Promise<void>;
}

/**
 * @interface OrganizationProviderProps
 * @description Props interface for OrganizationProvider component
 */
interface OrganizationProviderProps {
  children: ReactNode;
}

/**
 * @const OrganizationContext
 * @type React.Context
 * @description Context providing organization data and functionality
 */
export const OrganizationContext = createContext<OrganizationContextType | undefined>(
  undefined
);

/**
 * @function useOrganizationContext
 * @description Custom hook to access the organization context
 * @returns {OrganizationContextType} Object containing organization context values
 */
export const useOrganizationContext = (): OrganizationContextType => {
  const context = useContext(OrganizationContext);
  if (!context) {
    throw new Error(
      'useOrganizationContext must be used within an OrganizationProvider'
    );
  }
  return context;
};

/**
 * @function OrganizationProvider
 * @description Provider component for the organization context
 * @param {OrganizationProviderProps} { children } - React children
 * @returns {JSX.Element} Provider component wrapping children
 */
export const OrganizationProvider: FC<OrganizationProviderProps> = ({
  children,
}) => {
  // LD1: Get auth state and current user from useAuth hook
  const { isAuthenticated, currentUser } = useAuth();

  // LD1: Initialize organization state and helper functions from useOrganizations hook
  const {
    organizations,
    currentOrganization,
    peerGroups,
    offices,
    departments,
    loading,
    error,
    getOrganizationById,
    getOrganizationsByType,
    fetchOrganizations,
    fetchOrganizationDetails,
    setCurrentOrganizationById,
    createNewOrganization,
    updateExistingOrganization,
    deleteExistingOrganization,
    fetchOrganizationOffices,
    createOffice: createOfficeHook,
    updateOffice: updateOfficeHook,
    deleteOffice: deleteOfficeHook,
    fetchOrganizationDepartments,
    createDepartment: createDepartmentHook,
    updateDepartment: updateDepartmentHook,
    deleteDepartment: deleteDepartmentHook,
    fetchPeerGroups,
    createPeerGroup: createPeerGroupHook,
    updatePeerGroup: updatePeerGroupHook,
    deletePeerGroup: deletePeerGroupHook,
    fetchOrganizationSettings: fetchOrganizationSettingsHook,
    updateOrganizationSettings: updateOrganizationSettingsHook,
  } = useOrganizations();

  // LD1: Define currentOrganization state variable and setter
  const [currentOrg, setCurrentOrg] = useState<Organization | null>(
    currentOrganization || null
  );

  // LD1: Create effect to update currentOrganization when user changes
  useEffect(() => {
    if (currentOrganization) {
      setCurrentOrg(currentOrganization);
    }
  }, [currentOrganization]);

  // LD1: Create effect to load organization data when user is authenticated
  useEffect(() => {
    if (isAuthenticated && currentUser) {
      // Fetch organization details when authenticated
      fetchOrganizationDetails(currentUser.organizationId);
      fetchOrganizations(currentUser.organization.type);
    }
  }, [isAuthenticated, currentUser, fetchOrganizationDetails, fetchOrganizations]);

  // LD1: Create handler functions for modifying organization data
  const setCurrentOrganization = useCallback(
    (organization: Organization | null) => {
      setCurrentOrg(organization);
      if (organization) {
        setCurrentOrganizationById(organization.id);
      } else {
        setCurrentOrganizationById(null);
      }
    },
    [setCurrentOrganizationById]
  );

  const updateOrganizationSettings = useCallback(
    async (settings: Partial<OrganizationSettings>) => {
      if (currentOrg?.id) {
        await updateOrganizationSettingsHook(settings);
      }
    },
    [currentOrg, updateOrganizationSettingsHook]
  );

  const createOffice = useCallback(
    async (office: Partial<Office>) => {
      if (currentOrg?.id) {
        await createOfficeHook(currentOrg.id, office);
      }
    },
    [currentOrg, createOfficeHook]
  );

  const updateOffice = useCallback(
    async (officeId: string, officeData: Partial<Office>) => {
      if (currentOrg?.id) {
        await updateOfficeHook(currentOrg.id, officeId, officeData);
      }
    },
    [currentOrg, updateOfficeHook]
  );

  const deleteOffice = useCallback(
    async (officeId: string) => {
      if (currentOrg?.id) {
        await deleteOfficeHook(currentOrg.id, officeId);
      }
    },
    [currentOrg, deleteOfficeHook]
  );

  const createDepartment = useCallback(
    async (department: Partial<Department>) => {
      if (currentOrg?.id) {
        await createDepartmentHook(currentOrg.id, department);
      }
    },
    [currentOrg, createDepartmentHook]
  );

  const updateDepartment = useCallback(
    async (departmentId: string, departmentData: Partial<Department>) => {
      if (currentOrg?.id) {
        await updateDepartmentHook(currentOrg.id, departmentId, departmentData);
      }
    },
    [currentOrg, updateDepartmentHook]
  );

  const deleteDepartment = useCallback(
    async (departmentId: string) => {
      if (currentOrg?.id) {
        await deleteDepartmentHook(currentOrg.id, departmentId);
      }
    },
    [currentOrg, deleteDepartmentHook]
  );

  const refreshOrganizationData = useCallback(async () => {
    if (currentOrg?.id) {
      await fetchOrganizationDetails(currentOrg.id);
    }
  }, [currentOrg, fetchOrganizationDetails]);

  // LD1: Create context value object with current state and functions
  const contextValue: OrganizationContextType = {
    currentOrganization: currentOrg || null,
    organizations,
    settings: currentOrganization?.settings || null,
    offices,
    departments,
    peerGroups,
    isLoading: loading,
    error,
    setCurrentOrganization,
    updateOrganizationSettings,
    getOrganizationById,
    getOrganizationsByType,
    createOffice,
    updateOffice,
    deleteOffice,
    createDepartment,
    updateDepartment,
    deleteDepartment,
    refreshOrganizationData,
  };

  // LD1: Return OrganizationContext.Provider with value and children
  return (
    <OrganizationContext.Provider value={contextValue}>
      {children}
    </OrganizationContext.Provider>
  );
};