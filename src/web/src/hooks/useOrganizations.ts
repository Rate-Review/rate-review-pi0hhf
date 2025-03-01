import { useDispatch, useSelector } from 'react-redux'; // react-redux v8.1.1
import { useState, useCallback, useEffect } from 'react'; // react v18.0+
import {
  Organization,
  Office,
  Department,
  OrganizationType,
  OrganizationSettings,
  PeerGroupRelation,
  OrganizationRelationship
} from '../types/organization';
import {
  organizationsActions,
  selectOrganizations,
  selectCurrentOrganization,
  selectPeerGroups,
  selectRelatedOrganizations,
  selectOffices,
  selectDepartments,
  selectOrganizationsLoading,
  selectOrganizationsError
} from '../store/organizations/organizationsSlice';
import {
  fetchClientOrganizations,
  fetchLawFirmOrganizations,
  fetchOrganizationById,
  createOrganization,
  updateOrganization,
  deleteOrganization,
  fetchOrganizationRelationships,
  createOrganizationRelationship,
  updateOrganizationRelationship,
  deleteOrganizationRelationship,
  fetchOrganizationSettings,
  updateOrganizationSettings
} from '../store/organizations/organizationsThunks';

/**
 * Hook providing organization management functionality including CRUD operations and state access
 * @returns Object containing organization data and functions for manipulating organizations
 */
const useOrganizations = () => {
  // LD1: Initialize Redux dispatch function using useDispatch
  const dispatch = useDispatch();

  // LD1: Select organization-related state from Redux store using selectors
  const organizations = useSelector(selectOrganizations);
  const currentOrganization = useSelector(selectCurrentOrganization);
  const peerGroups = useSelector(selectPeerGroups);
  const relatedOrganizations = useSelector(selectRelatedOrganizations);
  const offices = useSelector(selectOffices);
  const departments = useSelector(selectDepartments);
  const loading = useSelector(selectOrganizationsLoading);
  const error = useSelector(selectOrganizationsError);

  // LD1: Create loading state for tracking asynchronous operations
  const [localLoading, setLocalLoading] = useState(false);
  const [localError, setLocalError] = useState<string | null>(null);

  // LD1: Implement getOrganizationById function to find an organization by ID
  const getOrganizationById = useCallback((id: string): Organization | undefined => {
    return organizations.find(org => org.id === id);
  }, [organizations]);

  // LD1: Implement getOrganizationsByType function to filter organizations by type
  const getOrganizationsByType = useCallback((type: OrganizationType): Organization[] => {
    return organizations.filter(org => org.type === type);
  }, [organizations]);

  // LD1: Implement fetchOrganizations function to load organizations from the API
  const fetchOrganizations = useCallback(async (type: OrganizationType) => {
    setLocalLoading(true);
    setLocalError(null);
    try {
      let action;
      if (type === OrganizationType.Client) {
        action = fetchClientOrganizations();
      } else {
        action = fetchLawFirmOrganizations();
      }
      await dispatch(action).unwrap();
    } catch (e: any) {
      setLocalError(e.message);
    } finally {
      setLocalLoading(false);
    }
  }, [dispatch]);

  // LD1: Implement fetchOrganizationDetails function to load a specific organization's details
  const fetchOrganizationDetails = useCallback(async (organizationId: string) => {
    setLocalLoading(true);
    setLocalError(null);
    try {
      await dispatch(fetchOrganizationById(organizationId)).unwrap();
    } catch (e: any) {
      setLocalError(e.message);
    } finally {
      setLocalLoading(false);
    }
  }, [dispatch]);

  // LD1: Implement setCurrentOrganizationById function to update the current active organization
  const setCurrentOrganizationById = useCallback((organizationId: string | null) => {
    dispatch(organizationsActions.setCurrentOrganization(organizationId));
  }, [dispatch]);

  // LD1: Implement createNewOrganization function to create a new organization
  const createNewOrganization = useCallback(async (organizationData: Partial<Organization>) => {
    setLocalLoading(true);
    setLocalError(null);
    try {
      await dispatch(createOrganization(organizationData)).unwrap();
    } catch (e: any) {
      setLocalError(e.message);
    } finally {
      setLocalLoading(false);
    }
  }, [dispatch]);

  // LD1: Implement updateExistingOrganization function to update an organization
  const updateExistingOrganization = useCallback(async (organizationData: Partial<Organization>) => {
    if (!currentOrganization?.id) {
      setLocalError('No current organization selected.');
      return;
    }
    setLocalLoading(true);
    setLocalError(null);
    try {
      await dispatch(updateOrganization({ id: currentOrganization.id, ...organizationData } as any)).unwrap();
    } catch (e: any) {
      setLocalError(e.message);
    } finally {
      setLocalLoading(false);
    }
  }, [dispatch, currentOrganization]);

  // LD1: Implement deleteExistingOrganization function to delete an organization
  const deleteExistingOrganization = useCallback(async (organizationId: string) => {
    setLocalLoading(true);
    setLocalError(null);
    try {
      await dispatch(deleteOrganization(organizationId)).unwrap();
    } catch (e: any) {
      setLocalError(e.message);
    } finally {
      setLocalLoading(false);
    }
  }, [dispatch]);

  // LD1: Implement fetchOrganizationOffices function to load organization offices
  const fetchOrganizationOffices = useCallback(async (organizationId: string) => {
    setLocalLoading(true);
    setLocalError(null);
    try {
      // TODO: Implement thunk and API call for fetching offices
      // await dispatch(fetchOffices(organizationId)).unwrap();
      console.log('Fetching offices for organization:', organizationId);
    } catch (e: any) {
      setLocalError(e.message);
    } finally {
      setLocalLoading(false);
    }
  }, []);

  // LD1: Implement createOffice, updateOffice, and deleteOffice functions for office management
  const createOffice = useCallback(async (organizationId: string, officeData: Partial<Office>) => {
    setLocalLoading(true);
    setLocalError(null);
    try {
      // TODO: Implement thunk and API call for creating office
      // await dispatch(createOfficeThunk({ organizationId, officeData })).unwrap();
      console.log('Creating office:', officeData, 'for organization:', organizationId);
    } catch (e: any) {
      setLocalError(e.message);
    } finally {
      setLocalLoading(false);
    }
  }, []);

  const updateOffice = useCallback(async (organizationId: string, officeId: string, officeData: Partial<Office>) => {
    setLocalLoading(true);
    setLocalError(null);
    try {
      // TODO: Implement thunk and API call for updating office
      // await dispatch(updateOfficeThunk({ organizationId, officeId, officeData })).unwrap();
      console.log('Updating office:', officeData, 'for organization:', organizationId, 'with ID:', officeId);
    } catch (e: any) {
      setLocalError(e.message);
    } finally {
      setLocalLoading(false);
    }
  }, []);

  const deleteOffice = useCallback(async (organizationId: string, officeId: string) => {
    setLocalLoading(true);
    setLocalError(null);
    try {
      // TODO: Implement thunk and API call for deleting office
      // await dispatch(deleteOfficeThunk({ organizationId, officeId })).unwrap();
      console.log('Deleting office with ID:', officeId, 'from organization:', organizationId);
    } catch (e: any) {
      setLocalError(e.message);
    } finally {
      setLocalLoading(false);
    }
  }, []);

  // LD1: Implement fetchOrganizationDepartments function to load organization departments
  const fetchOrganizationDepartments = useCallback(async (organizationId: string) => {
    setLocalLoading(true);
    setLocalError(null);
    try {
      // TODO: Implement thunk and API call for fetching departments
      // await dispatch(fetchDepartments(organizationId)).unwrap();
      console.log('Fetching departments for organization:', organizationId);
    } catch (e: any) {
      setLocalError(e.message);
    } finally {
      setLocalLoading(false);
    }
  }, []);

  // LD1: Implement createDepartment, updateDepartment, and deleteDepartment functions for department management
  const createDepartment = useCallback(async (organizationId: string, departmentData: Partial<Department>) => {
    setLocalLoading(true);
    setLocalError(null);
    try {
      // TODO: Implement thunk and API call for creating department
      // await dispatch(createDepartmentThunk({ organizationId, departmentData })).unwrap();
      console.log('Creating department:', departmentData, 'for organization:', organizationId);
    } catch (e: any) {
      setLocalError(e.message);
    } finally {
      setLocalLoading(false);
    }
  }, []);

  const updateDepartment = useCallback(async (organizationId: string, departmentId: string, departmentData: Partial<Department>) => {
    setLocalLoading(true);
    setLocalError(null);
    try {
      // TODO: Implement thunk and API call for updating department
      // await dispatch(updateDepartmentThunk({ organizationId, departmentId, departmentData })).unwrap();
      console.log('Updating department:', departmentData, 'for organization:', organizationId, 'with ID:', departmentId);
    } catch (e: any) {
      setLocalError(e.message);
    } finally {
      setLocalLoading(false);
    }
  }, []);

  const deleteDepartment = useCallback(async (organizationId: string, departmentId: string) => {
    setLocalLoading(true);
    setLocalError(null);
    try {
      // TODO: Implement thunk and API call for deleting department
      // await dispatch(deleteDepartmentThunk({ organizationId, departmentId })).unwrap();
      console.log('Deleting department with ID:', departmentId, 'from organization:', organizationId);
    } catch (e: any) {
      setLocalError(e.message);
    } finally {
      setLocalLoading(false);
    }
  }, []);

  // LD1: Implement fetchOrganizationPeerGroups function to load peer groups
  const fetchPeerGroups = useCallback(async (organizationId: string) => {
    setLocalLoading(true);
    setLocalError(null);
    try {
      // TODO: Implement thunk and API call for fetching peer groups
      // await dispatch(fetchPeerGroupsThunk(organizationId)).unwrap();
      console.log('Fetching peer groups for organization:', organizationId);
    } catch (e: any) {
      setLocalError(e.message);
    } finally {
      setLocalLoading(false);
    }
  }, []);

  // LD1: Implement createPeerGroup, updatePeerGroup, and deletePeerGroup functions for peer group management
  const createPeerGroup = useCallback(async (organizationId: string, peerGroupData: Partial<PeerGroupRelation>) => {
    setLocalLoading(true);
    setLocalError(null);
    try {
      // TODO: Implement thunk and API call for creating peer group
      // await dispatch(createPeerGroupThunk({ organizationId, peerGroupData })).unwrap();
      console.log('Creating peer group:', peerGroupData, 'for organization:', organizationId);
    } catch (e: any) {
      setLocalError(e.message);
    } finally {
      setLocalLoading(false);
    }
  }, []);

  const updatePeerGroup = useCallback(async (organizationId: string, peerGroupId: string, peerGroupData: Partial<PeerGroupRelation>) => {
    setLocalLoading(true);
    setLocalError(null);
    try {
      // TODO: Implement thunk and API call for updating peer group
      // await dispatch(updatePeerGroupThunk({ organizationId, peerGroupId, peerGroupData })).unwrap();
      console.log('Updating peer group:', peerGroupData, 'for organization:', organizationId, 'with ID:', peerGroupId);
    } catch (e: any) {
      setLocalError(e.message);
    } finally {
      setLocalLoading(false);
    }
  }, []);

  const deletePeerGroup = useCallback(async (organizationId: string, peerGroupId: string) => {
    setLocalLoading(true);
    setLocalError(null);
    try {
      // TODO: Implement thunk and API call for deleting peer group
      // await dispatch(deletePeerGroupThunk({ organizationId, peerGroupId })).unwrap();
      console.log('Deleting peer group with ID:', peerGroupId, 'from organization:', organizationId);
    } catch (e: any) {
      setLocalError(e.message);
    } finally {
      setLocalLoading(false);
    }
  }, []);

  // LD1: Implement fetchRelatedOrganizations function to load related organizations
    const fetchRelatedOrganizations = useCallback(async (organizationId: string) => {
        setLocalLoading(true);
        setLocalError(null);
        try {
            await dispatch(fetchOrganizationRelationships(organizationId)).unwrap();
        } catch (e: any) {
            setLocalError(e.message);
        } finally {
            setLocalLoading(false);
        }
    }, [dispatch]);

    // LD1: Implement createRelationship, updateRelationship, and deleteRelationship functions for relationship management
    const createRelationship = useCallback(async (relationshipData: Partial<OrganizationRelationship>) => {
        setLocalLoading(true);
        setLocalError(null);
        try {
            await dispatch(createOrganizationRelationship(relationshipData)).unwrap();
        } catch (e: any) {
            setLocalError(e.message);
        } finally {
            setLocalLoading(false);
        }
    }, [dispatch]);

    const updateRelationship = useCallback(async (clientId: string, firmId: string, relationshipData: Partial<OrganizationRelationship>) => {
        setLocalLoading(true);
        setLocalError(null);
        try {
            // Ensure clientId and firmId are provided
            if (!clientId || !firmId) {
                throw new Error('Client ID and Firm ID are required to update a relationship.');
            }
            await dispatch(updateOrganizationRelationship({ clientId, firmId, ...relationshipData }) as any).unwrap();
        } catch (e: any) {
            setLocalError(e.message);
        } finally {
            setLocalLoading(false);
        }
    }, [dispatch]);

    const deleteRelationship = useCallback(async (relationshipId: string) => {
        setLocalLoading(true);
        setLocalError(null);
        try {
            await dispatch(deleteOrganizationRelationship(relationshipId)).unwrap();
        } catch (e: any) {
            setLocalError(e.message);
        } finally {
            setLocalLoading(false);
        }
    }, [dispatch]);

    // LD1: Implement fetchSettings and updateSettings functions for organization settings
    const fetchOrganizationSettingsData = useCallback(async (organizationId: string) => {
        setLocalLoading(true);
        setLocalError(null);
        try {
            await dispatch(fetchOrganizationSettings(organizationId)).unwrap();
        } catch (e: any) {
            setLocalError(e.message);
        } finally {
            setLocalLoading(false);
        }
    }, [dispatch]);

    const updateOrganizationSettingsData = useCallback(async (settingsData: Partial<OrganizationSettings>) => {
        setLocalLoading(true);
        setLocalError(null);
        try {
            await dispatch(updateOrganizationSettings(settingsData) as any).unwrap();
        } catch (e: any) {
            setLocalError(e.message);
        } finally {
            setLocalLoading(false);
        }
    }, [dispatch]);

  // LD1: Create effect to reset error state when dependencies change
  useEffect(() => {
    setLocalError(null);
  }, [organizations, currentOrganization, peerGroups, relatedOrganizations, offices, departments]);

  // LD1: Return an object containing all organization state and functions
  return {
    organizations,
    currentOrganization,
    peerGroups,
    relatedOrganizations,
    offices,
    departments,
    loading: loading || localLoading,
    error: error || localError,
    getOrganizationById,
    getOrganizationsByType,
    fetchOrganizations,
    fetchOrganizationDetails,
    setCurrentOrganizationById,
    createNewOrganization,
    updateExistingOrganization,
    deleteExistingOrganization,
    fetchOrganizationOffices,
    createOffice,
    updateOffice,
    deleteOffice,
    fetchOrganizationDepartments,
    createDepartment,
    updateDepartment,
    deleteDepartment,
    fetchPeerGroups,
    createPeerGroup,
    updatePeerGroup,
    deletePeerGroup,
    fetchRelatedOrganizations,
    createRelationship,
    updateRelationship,
    deleteRelationship,
    fetchOrganizationSettings: fetchOrganizationSettingsData,
    updateOrganizationSettings: updateOrganizationSettingsData
  };
};

export default useOrganizations;