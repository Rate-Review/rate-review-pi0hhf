/**
 * Organization Service
 * 
 * Service module that handles API communication for organization-related operations 
 * in the Justice Bid Rate Negotiation System. Provides functions for creating, reading,
 * updating, and deleting organizations, as well as managing related entities like
 * offices, departments, settings, and peer groups.
 */

import axiosInstance from '../api/axiosConfig';
import { API_ROUTES, buildUrl, buildUrlWithParams } from '../api/apiRoutes';
import { 
  Organization,
  OrganizationType,
  OrganizationSettings,
  Office,
  Department,
  PeerGroupRelation,
  OrganizationRelationship
} from '../types/organization';
import { 
  PaginationParams, 
  FilterParams, 
  SortParams, 
  PaginatedResponse 
} from '../types/common';

// HTTP helper functions
const httpHelpers = {
  get: async <T>(url: string): Promise<T> => {
    const response = await axiosInstance.get<T>(url);
    return response.data;
  },
  post: async <T>(url: string, data?: any): Promise<T> => {
    const response = await axiosInstance.post<T>(url, data);
    return response.data;
  },
  put: async <T>(url: string, data?: any): Promise<T> => {
    const response = await axiosInstance.put<T>(url, data);
    return response.data;
  },
  del: async <T>(url: string): Promise<T> => {
    const response = await axiosInstance.delete<T>(url);
    return response.data;
  },
  getPaginated: async <T>(
    url: string, 
    pagination: PaginationParams, 
    sort?: SortParams, 
    filters?: FilterParams[]
  ): Promise<PaginatedResponse<T>> => {
    const params: Record<string, string> = {
      page: pagination.page.toString(),
      pageSize: pagination.pageSize.toString()
    };

    if (sort) {
      params.sortBy = sort.field;
      params.sortOrder = sort.order;
    }

    if (filters?.length) {
      filters.forEach((filter, index) => {
        params[`filter[${index}][field]`] = filter.field;
        params[`filter[${index}][operator]`] = filter.operator;
        params[`filter[${index}][value]`] = filter.value;
      });
    }

    const response = await axiosInstance.get<PaginatedResponse<T>>(url, { params });
    return response.data;
  }
};

/**
 * Retrieves a paginated list of organizations with optional filters for type, name, etc.
 * @param paginationParams - Parameters for pagination (page, pageSize)
 * @param filters - Optional filters to apply to the request
 * @param sort - Optional sorting configuration
 * @returns Paginated list of organizations
 */
export const getOrganizations = async (
  paginationParams: PaginationParams,
  filters?: FilterParams[],
  sort?: SortParams
): Promise<PaginatedResponse<Organization>> => {
  const url = buildUrl(API_ROUTES.ORGANIZATIONS.BASE);
  return httpHelpers.getPaginated<Organization>(url, paginationParams, sort, filters);
};

/**
 * Retrieves detailed information for a specific organization by ID
 * @param id - Organization ID
 * @returns Organization details
 */
export const getOrganizationById = async (id: string): Promise<Organization> => {
  const url = buildUrlWithParams(API_ROUTES.ORGANIZATIONS.BY_ID, { id });
  return httpHelpers.get<Organization>(url);
};

/**
 * Creates a new organization with the provided data
 * @param organizationData - Organization data to create
 * @returns The newly created organization
 */
export const createOrganization = async (
  organizationData: Partial<Organization>
): Promise<Organization> => {
  const url = buildUrl(API_ROUTES.ORGANIZATIONS.BASE);
  return httpHelpers.post<Organization>(url, organizationData);
};

/**
 * Updates an existing organization with the provided data
 * @param id - Organization ID
 * @param organizationData - Updated organization data
 * @returns The updated organization
 */
export const updateOrganization = async (
  id: string,
  organizationData: Partial<Organization>
): Promise<Organization> => {
  const url = buildUrlWithParams(API_ROUTES.ORGANIZATIONS.BY_ID, { id });
  return httpHelpers.put<Organization>(url, organizationData);
};

/**
 * Deletes an organization with the specified ID
 * @param id - Organization ID
 * @returns Promise that resolves when deletion is complete
 */
export const deleteOrganization = async (id: string): Promise<void> => {
  const url = buildUrlWithParams(API_ROUTES.ORGANIZATIONS.BY_ID, { id });
  return httpHelpers.del<void>(url);
};

/**
 * Retrieves settings for a specific organization
 * @param id - Organization ID
 * @returns Organization settings
 */
export const getOrganizationSettings = async (id: string): Promise<OrganizationSettings> => {
  const url = buildUrlWithParams(API_ROUTES.ORGANIZATIONS.SETTINGS, { id });
  return httpHelpers.get<OrganizationSettings>(url);
};

/**
 * Updates settings for a specific organization
 * @param id - Organization ID
 * @param settings - Updated organization settings
 * @returns Updated organization settings
 */
export const updateOrganizationSettings = async (
  id: string,
  settings: OrganizationSettings
): Promise<OrganizationSettings> => {
  const url = buildUrlWithParams(API_ROUTES.ORGANIZATIONS.SETTINGS, { id });
  return httpHelpers.put<OrganizationSettings>(url, settings);
};

/**
 * Retrieves users associated with a specific organization
 * @param id - Organization ID
 * @param paginationParams - Parameters for pagination
 * @returns Paginated list of organization users
 */
export const getOrganizationUsers = async (
  id: string,
  paginationParams: PaginationParams
): Promise<PaginatedResponse<any>> => {
  const url = buildUrlWithParams(API_ROUTES.ORGANIZATIONS.USERS, { id });
  return httpHelpers.getPaginated<any>(url, paginationParams);
};

/**
 * Retrieves office locations for a specific organization
 * @param id - Organization ID
 * @returns Array of organization offices
 */
export const getOrganizationOffices = async (id: string): Promise<Office[]> => {
  const url = buildUrlWithParams(API_ROUTES.ORGANIZATIONS.BY_ID, { id }) + '/offices';
  return httpHelpers.get<Office[]>(url);
};

/**
 * Creates a new office for a specific organization
 * @param organizationId - Organization ID
 * @param officeData - Office data to create
 * @returns The newly created office
 */
export const createOrganizationOffice = async (
  organizationId: string,
  officeData: Partial<Office>
): Promise<Office> => {
  const url = buildUrlWithParams(API_ROUTES.ORGANIZATIONS.BY_ID, { id: organizationId }) + '/offices';
  return httpHelpers.post<Office>(url, officeData);
};

/**
 * Updates an existing office for a specific organization
 * @param organizationId - Organization ID
 * @param officeId - Office ID
 * @param officeData - Updated office data
 * @returns The updated office
 */
export const updateOrganizationOffice = async (
  organizationId: string,
  officeId: string,
  officeData: Partial<Office>
): Promise<Office> => {
  const url = buildUrlWithParams(API_ROUTES.ORGANIZATIONS.BY_ID, { id: organizationId }) + `/offices/${officeId}`;
  return httpHelpers.put<Office>(url, officeData);
};

/**
 * Deletes an office from a specific organization
 * @param organizationId - Organization ID
 * @param officeId - Office ID
 * @returns Promise that resolves when deletion is complete
 */
export const deleteOrganizationOffice = async (
  organizationId: string,
  officeId: string
): Promise<void> => {
  const url = buildUrlWithParams(API_ROUTES.ORGANIZATIONS.BY_ID, { id: organizationId }) + `/offices/${officeId}`;
  return httpHelpers.del<void>(url);
};

/**
 * Retrieves departments for a specific organization
 * @param id - Organization ID
 * @returns Array of organization departments
 */
export const getOrganizationDepartments = async (id: string): Promise<Department[]> => {
  const url = buildUrlWithParams(API_ROUTES.ORGANIZATIONS.BY_ID, { id }) + '/departments';
  return httpHelpers.get<Department[]>(url);
};

/**
 * Creates a new department for a specific organization
 * @param organizationId - Organization ID
 * @param departmentData - Department data to create
 * @returns The newly created department
 */
export const createOrganizationDepartment = async (
  organizationId: string,
  departmentData: Partial<Department>
): Promise<Department> => {
  const url = buildUrlWithParams(API_ROUTES.ORGANIZATIONS.BY_ID, { id: organizationId }) + '/departments';
  return httpHelpers.post<Department>(url, departmentData);
};

/**
 * Updates an existing department for a specific organization
 * @param organizationId - Organization ID
 * @param departmentId - Department ID
 * @param departmentData - Updated department data
 * @returns The updated department
 */
export const updateOrganizationDepartment = async (
  organizationId: string,
  departmentId: string,
  departmentData: Partial<Department>
): Promise<Department> => {
  const url = buildUrlWithParams(API_ROUTES.ORGANIZATIONS.BY_ID, { id: organizationId }) + `/departments/${departmentId}`;
  return httpHelpers.put<Department>(url, departmentData);
};

/**
 * Deletes a department from a specific organization
 * @param organizationId - Organization ID
 * @param departmentId - Department ID
 * @returns Promise that resolves when deletion is complete
 */
export const deleteOrganizationDepartment = async (
  organizationId: string,
  departmentId: string
): Promise<void> => {
  const url = buildUrlWithParams(API_ROUTES.ORGANIZATIONS.BY_ID, { id: organizationId }) + `/departments/${departmentId}`;
  return httpHelpers.del<void>(url);
};

/**
 * Retrieves peer groups for a specific organization
 * @param organizationId - Organization ID
 * @returns Array of peer group relations
 */
export const getPeerGroups = async (organizationId: string): Promise<PeerGroupRelation[]> => {
  const url = buildUrl(API_ROUTES.PEER_GROUPS.BASE) + `?organizationId=${organizationId}`;
  return httpHelpers.get<PeerGroupRelation[]>(url);
};

/**
 * Creates a new peer group for an organization
 * @param peerGroupData - Peer group data to create
 * @returns The newly created peer group
 */
export const createPeerGroup = async (
  peerGroupData: Partial<PeerGroupRelation>
): Promise<PeerGroupRelation> => {
  const url = buildUrl(API_ROUTES.PEER_GROUPS.BASE);
  return httpHelpers.post<PeerGroupRelation>(url, peerGroupData);
};

/**
 * Updates an existing peer group
 * @param peerGroupId - Peer group ID
 * @param peerGroupData - Updated peer group data
 * @returns The updated peer group
 */
export const updatePeerGroup = async (
  peerGroupId: string,
  peerGroupData: Partial<PeerGroupRelation>
): Promise<PeerGroupRelation> => {
  const url = buildUrlWithParams(API_ROUTES.PEER_GROUPS.BY_ID, { id: peerGroupId });
  return httpHelpers.put<PeerGroupRelation>(url, peerGroupData);
};

/**
 * Deletes a peer group
 * @param peerGroupId - Peer group ID
 * @returns Promise that resolves when deletion is complete
 */
export const deletePeerGroup = async (peerGroupId: string): Promise<void> => {
  const url = buildUrlWithParams(API_ROUTES.PEER_GROUPS.BY_ID, { id: peerGroupId });
  return httpHelpers.del<void>(url);
};

/**
 * Retrieves members of a specific peer group
 * @param peerGroupId - Peer group ID
 * @param paginationParams - Parameters for pagination
 * @returns Paginated list of organizations in the peer group
 */
export const getPeerGroupMembers = async (
  peerGroupId: string,
  paginationParams: PaginationParams
): Promise<PaginatedResponse<Organization>> => {
  const url = buildUrlWithParams(API_ROUTES.PEER_GROUPS.MEMBERS, { id: peerGroupId });
  return httpHelpers.getPaginated<Organization>(url, paginationParams);
};

/**
 * Adds an organization to a peer group
 * @param peerGroupId - Peer group ID
 * @param organizationId - Organization ID to add
 * @returns Promise that resolves when addition is complete
 */
export const addPeerGroupMember = async (
  peerGroupId: string,
  organizationId: string
): Promise<void> => {
  const url = buildUrlWithParams(API_ROUTES.PEER_GROUPS.MEMBERS, { id: peerGroupId });
  return httpHelpers.post<void>(url, { organizationId });
};

/**
 * Removes an organization from a peer group
 * @param peerGroupId - Peer group ID
 * @param organizationId - Organization ID to remove
 * @returns Promise that resolves when removal is complete
 */
export const removePeerGroupMember = async (
  peerGroupId: string,
  organizationId: string
): Promise<void> => {
  const url = API_ROUTES.PEER_GROUPS.MEMBERS.replace(':id', peerGroupId) + '/' + organizationId;
  return httpHelpers.del<void>(url);
};

/**
 * Retrieves relationships between organizations (law firm-client connections)
 * @param organizationId - Organization ID
 * @param paginationParams - Parameters for pagination
 * @returns Paginated list of organization relationships
 */
export const getOrganizationRelationships = async (
  organizationId: string,
  paginationParams: PaginationParams
): Promise<PaginatedResponse<OrganizationRelationship>> => {
  const url = buildUrlWithParams(API_ROUTES.ORGANIZATIONS.BY_ID, { id: organizationId }) + '/relationships';
  return httpHelpers.getPaginated<OrganizationRelationship>(url, paginationParams);
};

/**
 * Creates a relationship between a law firm and client organization
 * @param relationshipData - Relationship data to create
 * @returns The newly created relationship
 */
export const createOrganizationRelationship = async (
  relationshipData: Partial<OrganizationRelationship>
): Promise<OrganizationRelationship> => {
  const url = buildUrl(API_ROUTES.ORGANIZATIONS.BASE) + '/relationships';
  return httpHelpers.post<OrganizationRelationship>(url, relationshipData);
};

/**
 * Updates an existing relationship between organizations
 * @param clientId - Client organization ID
 * @param firmId - Law firm organization ID
 * @param relationshipData - Updated relationship data
 * @returns The updated relationship
 */
export const updateOrganizationRelationship = async (
  clientId: string,
  firmId: string,
  relationshipData: Partial<OrganizationRelationship>
): Promise<OrganizationRelationship> => {
  const url = buildUrl(API_ROUTES.ORGANIZATIONS.BASE) + `/relationships/${clientId}/${firmId}`;
  return httpHelpers.put<OrganizationRelationship>(url, relationshipData);
};