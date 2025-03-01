import React, { useState, useEffect, useCallback } from 'react'; //  ^18.0.0
import {
  Grid,
  Typography,
  Box,
  Paper,
  IconButton,
  Tooltip,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Divider,
  Table,
  TableContainer,
  TableHead,
  TableBody,
  TableRow,
  TableCell,
} from '@mui/material'; //  ^5.14.0
import {
  Add,
  Edit,
  Delete,
  Search,
  FilterList,
  Refresh,
  Person,
  Email,
  VpnKey,
  CheckCircle,
  Cancel,
} from '@mui/icons-material'; //  ^5.14.0

import { usePermissions } from '../../hooks/usePermissions';
import { useOrganization } from '../../context/OrganizationContext';
import MainLayout from '../../components/layout/MainLayout';
import Button from '../../components/common/Button';
import Modal from '../../components/common/Modal';
import SearchBar from '../../components/common/SearchBar';
import UserForm from '../../components/forms/UserForm';
import ConfirmationDialog from '../../components/common/ConfirmationDialog';
import StatusIndicator from '../../components/common/StatusIndicator';
import Toast from '../../components/common/Toast';
import PageHeader from '../../components/layout/PageHeader';
import { PERMISSIONS } from '../../constants/permissions';
import { User, UserRole, UserFormData } from '../../types/user';
import { usersService } from '../../services/users';

/**
 * React functional component that renders the user management page
 */
const UserManagementPage: React.FC = () => {
  // LD1: Initialize state variables for users, loading, error, search term, filters, current user, and modal states
  const [users, setUsers] = useState<User[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [search, setSearch] = useState('');
  const [filters, setFilters] = useState({ role: '', status: '' });
  const [currentUser, setCurrentUser] = useState<User | null>(null);
  const [isUserModalOpen, setIsUserModalOpen] = useState(false);
  const [isConfirmDialogOpen, setIsConfirmDialogOpen] = useState(false);
  const [formSubmitting, setFormSubmitting] = useState(false);

  // LD1: Use the usePermissions hook to check if the current user has permission to manage users
  const { can } = usePermissions();

  // LD1: Use the useOrganization hook to get the current organization ID
  const { currentOrganization } = useOrganization();

  // LD1: Fetch users for the current organization with optional search and filter parameters
  const fetchUsers = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      if (currentOrganization?.id) {
        const fetchedUsers = await usersService.getUsersByOrganization(
          currentOrganization.id,
          { searchTerm: search, ...filters }
        );
        setUsers(fetchedUsers.items);
      }
    } catch (e: any) {
      setError(e.message);
      Toast({ message: e.message, severity: 'error' });
    } finally {
      setLoading(false);
    }
  }, [currentOrganization?.id, search, filters]);

  // LD1: Open the user form modal for adding a new user
  const handleAddUser = () => {
    setCurrentUser(null);
    setIsUserModalOpen(true);
  };

  // LD1: Open the user form modal for editing an existing user
  const handleEditUser = (user: User) => {
    setCurrentUser(user);
    setIsUserModalOpen(true);
  };

  // LD1: Open the confirmation dialog for deactivating a user
  const handleDeactivateUser = (user: User) => {
    setCurrentUser(user);
    setIsConfirmDialogOpen(true);
  };

  // LD1: Handle the submission of the user form for creating or updating a user
  const handleUserSubmit = async (userData: UserFormData) => {
    setFormSubmitting(true);
    try {
      if (currentUser) {
        // Update existing user
        await usersService.updateUser(currentUser.id, userData);
        Toast({ message: 'User updated successfully', severity: 'success' });
      } else {
        // Create new user
        await usersService.createUser(userData);
        Toast({ message: 'User created successfully', severity: 'success' });
      }
      await fetchUsers(); // Refresh user list
      setIsUserModalOpen(false); // Close modal
      setCurrentUser(null); // Reset current user
    } catch (e: any) {
      setError(e.message);
      Toast({ message: e.message, severity: 'error' });
    } finally {
      setFormSubmitting(false);
    }
  };

  // LD1: Confirm and process the deactivation of a user
  const confirmDeactivateUser = async () => {
    setFormSubmitting(true);
    try {
      if (currentUser?.id && currentOrganization?.id) {
        await usersService.deactivateUser(currentUser.id);
        Toast({ message: 'User deactivated successfully', severity: 'success' });
        await fetchUsers(); // Refresh user list
        setIsConfirmDialogOpen(false); // Close confirmation dialog
        setCurrentUser(null); // Reset current user
      }
    } catch (e: any) {
      setError(e.message);
      Toast({ message: e.message, severity: 'error' });
    } finally {
      setFormSubmitting(false);
    }
  };

  // LD1: Handle search input changes and trigger user list filtering
  const handleSearch = (searchTerm: string) => {
    setSearch(searchTerm);
  };

  // LD1: Handle changes to user list filters
  const handleFilterChange = (newFilters: any) => {
    setFilters(newFilters);
  };

  // LD1: Refresh the user list with current search and filter settings
  const handleRefresh = () => {
    fetchUsers();
  };

  // LD1: Load users on component mount and when the organization changes
  useEffect(() => {
    fetchUsers();
  }, [fetchUsers]);

  // LD1: Render the user management page with a table of users and controls for adding, editing, and deactivating users
  return (
    <MainLayout>
      <PageHeader
        title="User Management"
        actions={
          can('create', 'users', 'organization') && (
            <Button variant="primary" onClick={handleAddUser}>
              <Add />
              Add User
            </Button>
          )
        }
      />

      <Grid container spacing={2} alignItems="center">
        <Grid item xs={12} sm={6}>
          <SearchBar placeholder="Search users" onSearch={handleSearch} />
        </Grid>
        <Grid item xs={12} sm={6} container justifyContent="flex-end">
          <Box display="flex" alignItems="center">
            <Tooltip title="Filter list">
              <IconButton>
                <FilterList />
              </IconButton>
            </Tooltip>
            <Tooltip title="Refresh list">
              <IconButton onClick={handleRefresh}>
                <Refresh />
              </IconButton>
            </Tooltip>
          </Box>
        </Grid>
      </Grid>

      <TableContainer component={Paper}>
        <Table aria-label="user table">
          <TableHead>
            <TableRow>
              <TableCell>Name</TableCell>
              <TableCell>Email</TableCell>
              <TableCell>Role</TableCell>
              <TableCell>Status</TableCell>
              <TableCell align="right">Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {users.map((user) => (
              <TableRow key={user.id}>
                <TableCell>
                  <Box display="flex" alignItems="center">
                    <Person sx={{ mr: 1 }} />
                    {user.name}
                  </Box>
                </TableCell>
                <TableCell>
                  <Box display="flex" alignItems="center">
                    <Email sx={{ mr: 1 }} />
                    {user.email}
                  </Box>
                </TableCell>
                <TableCell>{user.role}</TableCell>
                <TableCell>
                  <StatusIndicator
                    status={user.isContact ? 'Active' : 'Inactive'}
                    statusColorMap={{
                      Active: 'success',
                      Inactive: 'neutral',
                    }}
                  />
                </TableCell>
                <TableCell align="right">
                  {can('update', 'users', 'organization') && (
                    <Tooltip title="Edit user">
                      <IconButton onClick={() => handleEditUser(user)}>
                        <Edit />
                      </IconButton>
                    </Tooltip>
                  )}
                  {can('delete', 'users', 'organization') && (
                    <Tooltip title="Deactivate user">
                      <IconButton onClick={() => handleDeactivateUser(user)}>
                        <Delete />
                      </IconButton>
                    </Tooltip>
                  )}
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>

      <Modal isOpen={isUserModalOpen} onClose={() => setIsUserModalOpen(false)} title={currentUser ? 'Edit User' : 'Add User'}>
        <UserForm
          user={currentUser}
          organizationId={currentOrganization?.id || ''}
          onSubmit={handleUserSubmit}
          onCancel={() => setIsUserModalOpen(false)}
          isLoading={formSubmitting}
        />
      </Modal>

      <ConfirmationDialog
        isOpen={isConfirmDialogOpen}
        onClose={() => setIsConfirmDialogOpen(false)}
        onConfirm={confirmDeactivateUser}
        title="Deactivate User"
        message="Are you sure you want to deactivate this user? This action cannot be undone."
        confirmText="Deactivate"
        cancelText="Cancel"
        confirmButtonVariant="danger"
      />
    </MainLayout>
  );
};

export default UserManagementPage;