/**
 * User Management Service
 * 
 * Provides functionality for managing users, including CRUD operations,
 * role and permission management, verification, and invitation processes.
 * This service interfaces with the backend API to perform user-related operations.
 * 
 * @version 1.0.0
 */

import { api } from './api';
import { API_ROUTES as apiRoutes } from '../api/apiRoutes';
import { 
  User, 
  UserRole, 
  UserPermission,
  UserFormData as CreateUserRequest,
  UserFormData as UpdateUserRequest
} from '../types/user';
import { PaginatedResponse } from '../types/common';

/**
 * Interface for user filtering options
 */
interface UserFilters {
  role?: UserRole;
  isContact?: boolean;
  searchTerm?: string;
}

/**
 * Interface for user invitation request data
 */
interface InviteUserRequest {
  email: string;
  name: string;
  role: UserRole;
  permissions?: UserPermission[];
  organizationId: string;
}

/**
 * Fetches a paginated list of users based on the provided filters
 * 
 * @param filters - Optional filters to apply to the user list
 * @param page - Page number for pagination (defaults to 1)
 * @param limit - Number of items per page (defaults to 10)
 * @returns Promise resolving to paginated user data
 */
const getUsers = async (
  filters: UserFilters = {}, 
  page: number = 1, 
  limit: number = 10
): Promise<PaginatedResponse<User>> => {
  // Construct query parameters
  const queryParams = {
    page,
    limit,
    ...filters
  };
  
  return api.get<PaginatedResponse<User>>(
    apiRoutes.USERS.BASE,
    { params: queryParams }
  );
};

/**
 * Fetches a single user by ID
 * 
 * @param userId - Unique identifier of the user
 * @returns Promise resolving to user data
 */
const getUser = async (userId: string): Promise<User> => {
  const url = apiRoutes.USERS.BY_ID.replace(':id', userId);
  return api.get<User>(url);
};

/**
 * Creates a new user within the organization
 * 
 * @param userData - User data for creation
 * @returns Promise resolving to the created user data
 */
const createUser = async (userData: CreateUserRequest): Promise<User> => {
  return api.post<User>(apiRoutes.USERS.BASE, userData);
};

/**
 * Updates an existing user's information
 * 
 * @param userId - Unique identifier of the user to update
 * @param userData - Updated user data
 * @returns Promise resolving to the updated user data
 */
const updateUser = async (userId: string, userData: UpdateUserRequest): Promise<User> => {
  const url = apiRoutes.USERS.BY_ID.replace(':id', userId);
  return api.put<User>(url, userData);
};

/**
 * Deletes a user from the system
 * 
 * @param userId - Unique identifier of the user to delete
 * @returns Promise resolving when deletion is complete
 */
const deleteUser = async (userId: string): Promise<void> => {
  const url = apiRoutes.USERS.BY_ID.replace(':id', userId);
  return api.delete<void>(url);
};

/**
 * Changes a user's role within the organization
 * 
 * @param userId - Unique identifier of the user
 * @param role - New role to assign to the user
 * @returns Promise resolving to the updated user data
 */
const changeUserRole = async (userId: string, role: UserRole): Promise<User> => {
  const url = apiRoutes.USERS.BY_ID.replace(':id', userId);
  return api.put<User>(url, { role });
};

/**
 * Assigns specific permissions to a user
 * 
 * @param userId - Unique identifier of the user
 * @param permissions - Array of permissions to assign
 * @returns Promise resolving to the updated user data
 */
const assignPermissions = async (userId: string, permissions: UserPermission[]): Promise<User> => {
  const url = apiRoutes.USERS.PERMISSIONS.replace(':id', userId);
  return api.put<User>(url, { permissions });
};

/**
 * Marks a user as a verified contact
 * 
 * @param userId - Unique identifier of the user to verify
 * @returns Promise resolving to the updated user data
 */
const verifyContact = async (userId: string): Promise<User> => {
  const url = apiRoutes.USERS.BY_ID.replace(':id', userId);
  return api.put<User>(url, { isContact: true, lastVerified: new Date().toISOString() });
};

/**
 * Sends an invitation to a new user to join the organization
 * 
 * @param inviteData - Data for the user invitation
 * @returns Promise resolving when invitation is sent
 */
const inviteUser = async (inviteData: InviteUserRequest): Promise<void> => {
  return api.post<void>(`${apiRoutes.USERS.BASE}/invite`, inviteData);
};

/**
 * Gets the list of available roles that can be assigned to users
 * 
 * @returns Promise resolving to array of available user roles
 */
const getAvailableRoles = async (): Promise<UserRole[]> => {
  return api.get<UserRole[]>(`${apiRoutes.USERS.BASE}/roles`);
};

/**
 * Fetches users belonging to a specific organization
 * 
 * @param organizationId - ID of the organization
 * @param filters - Optional filters to apply
 * @param page - Page number for pagination
 * @param limit - Number of items per page
 * @returns Promise resolving to paginated organization users
 */
const getUsersByOrganization = async (
  organizationId: string,
  filters: UserFilters = {},
  page: number = 1,
  limit: number = 10
): Promise<PaginatedResponse<User>> => {
  // Construct URL and query parameters
  const url = `${apiRoutes.ORGANIZATIONS.USERS.replace(':id', organizationId)}`;
  const queryParams = {
    page,
    limit,
    ...filters
  };
  
  return api.get<PaginatedResponse<User>>(url, { params: queryParams });
};

// Export all user management functions
export default {
  getUsers,
  getUser,
  createUser,
  updateUser,
  deleteUser,
  changeUserRole,
  assignPermissions,
  verifyContact,
  inviteUser,
  getAvailableRoles,
  getUsersByOrganization
};