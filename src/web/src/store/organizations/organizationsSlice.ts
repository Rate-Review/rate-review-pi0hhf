import { createSlice, PayloadAction } from '@reduxjs/toolkit'; // @reduxjs/toolkit v1.9.5
import { Organization, Office, Department } from '../../types/organization';
import { ReduxStateSlice } from '../../types/common';

/**
 * Interface for peer group data
 */
interface PeerGroup {
  id: string;
  name: string;
  description: string;
  criteria: object;
  members: string[];
}

/**
 * Type definition for the organizations slice state
 */
export interface OrganizationsState {
  organizations: Organization[];
  currentOrganizationId: string | null;
  peerGroups: PeerGroup[];
  relatedOrganizations: Organization[];
  offices: Office[];
  departments: Department[];
  loading: boolean;
  error: string | null;
}

// Initial state for the organizations slice
const initialState: OrganizationsState = {
  organizations: [],
  currentOrganizationId: null,
  peerGroups: [],
  relatedOrganizations: [],
  offices: [],
  departments: [],
  loading: false,
  error: null,
};

/**
 * Redux slice for managing organizations in the Justice Bid application.
 * Handles organizations, peer groups, offices, and departments.
 */
const organizationsSlice = createSlice({
  name: 'organizations',
  initialState,
  reducers: {
    // Organization management reducers
    setOrganizations(state, action: PayloadAction<Organization[]>) {
      state.organizations = action.payload;
    },
    addOrganization(state, action: PayloadAction<Organization>) {
      state.organizations.push(action.payload);
    },
    updateOrganization(state, action: PayloadAction<Organization>) {
      const index = state.organizations.findIndex(org => org.id === action.payload.id);
      if (index !== -1) {
        state.organizations[index] = action.payload;
      }
    },
    removeOrganization(state, action: PayloadAction<string>) {
      state.organizations = state.organizations.filter(org => org.id !== action.payload);
    },
    setCurrentOrganization(state, action: PayloadAction<string | null>) {
      state.currentOrganizationId = action.payload;
    },
    
    // Peer Group management reducers
    setPeerGroups(state, action: PayloadAction<PeerGroup[]>) {
      state.peerGroups = action.payload;
    },
    addPeerGroup(state, action: PayloadAction<PeerGroup>) {
      state.peerGroups.push(action.payload);
    },
    updatePeerGroup(state, action: PayloadAction<PeerGroup>) {
      const index = state.peerGroups.findIndex(group => group.id === action.payload.id);
      if (index !== -1) {
        state.peerGroups[index] = action.payload;
      }
    },
    removePeerGroup(state, action: PayloadAction<string>) {
      state.peerGroups = state.peerGroups.filter(group => group.id !== action.payload);
    },
    
    // Related Organizations reducers
    setRelatedOrganizations(state, action: PayloadAction<Organization[]>) {
      state.relatedOrganizations = action.payload;
    },
    
    // Offices management reducers
    setOffices(state, action: PayloadAction<Office[]>) {
      state.offices = action.payload;
    },
    addOffice(state, action: PayloadAction<Office>) {
      state.offices.push(action.payload);
    },
    updateOffice(state, action: PayloadAction<Office>) {
      const index = state.offices.findIndex(office => office.id === action.payload.id);
      if (index !== -1) {
        state.offices[index] = action.payload;
      }
    },
    removeOffice(state, action: PayloadAction<string>) {
      state.offices = state.offices.filter(office => office.id !== action.payload);
    },
    
    // Departments management reducers
    setDepartments(state, action: PayloadAction<Department[]>) {
      state.departments = action.payload;
    },
    addDepartment(state, action: PayloadAction<Department>) {
      state.departments.push(action.payload);
    },
    updateDepartment(state, action: PayloadAction<Department>) {
      const index = state.departments.findIndex(dept => dept.id === action.payload.id);
      if (index !== -1) {
        state.departments[index] = action.payload;
      }
    },
    removeDepartment(state, action: PayloadAction<string>) {
      state.departments = state.departments.filter(dept => dept.id !== action.payload);
    },
    
    // Loading and error state reducers
    setLoading(state, action: PayloadAction<boolean>) {
      state.loading = action.payload;
    },
    setError(state, action: PayloadAction<string | null>) {
      state.error = action.payload;
    },
  },
});

// Export actions and reducer
export const organizationsActions = organizationsSlice.actions;

/**
 * Selector for retrieving all organizations from state
 */
export const selectOrganizations = (state: any): Organization[] => 
  state.organizations.organizations;

/**
 * Selector for retrieving the current active organization
 */
export const selectCurrentOrganization = (state: any): Organization | undefined => {
  const { organizations, currentOrganizationId } = state.organizations;
  return organizations.find(org => org.id === currentOrganizationId);
};

/**
 * Selector for retrieving peer groups from state
 */
export const selectPeerGroups = (state: any): PeerGroup[] => 
  state.organizations.peerGroups;

/**
 * Selector for retrieving organizations related to the current organization
 */
export const selectRelatedOrganizations = (state: any): Organization[] => 
  state.organizations.relatedOrganizations;

/**
 * Selector for retrieving offices of the current organization
 */
export const selectOffices = (state: any): Office[] => 
  state.organizations.offices;

/**
 * Selector for retrieving departments of the current organization
 */
export const selectDepartments = (state: any): Department[] => 
  state.organizations.departments;

/**
 * Selector for retrieving the loading state of organization operations
 */
export const selectOrganizationsLoading = (state: any): boolean => 
  state.organizations.loading;

/**
 * Selector for retrieving any error from organization operations
 */
export const selectOrganizationsError = (state: any): string | null => 
  state.organizations.error;

// Export default reducer
export default organizationsSlice.reducer;