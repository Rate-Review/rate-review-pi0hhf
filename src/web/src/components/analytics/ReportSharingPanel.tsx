import React, { useState, useEffect, useCallback } from 'react';
import Button from '../common/Button';
import Modal from '../common/Modal';
import Select from '../common/Select';
import TextField from '../common/TextField';
import { usePermissions } from '../../hooks/usePermissions';
import { useOrganization } from '../../context/OrganizationContext';
import { Organization, OrganizationType } from '../../types/organization';
import { User } from '../../types/user';
import { Autocomplete, Chip, CircularProgress } from '@mui/material'; //  ^5.14.0
import styled from 'styled-components';
import { toast } from 'react-toastify'; //  ^9.1.3
import { shareReport, getUsers } from '../../services/analytics'; // API function to share a report with users

// Define styled component for Autocomplete
const StyledAutocomplete = styled(Autocomplete)`
  width: 100%;
  margin-bottom: ${(props) => props.theme.spacing(2)}px;

  & .MuiFormControl-root {
    width: 100%;
  }
`;

// Define styled component for Chip
const StyledChip = styled(Chip)`
  margin: ${(props) => props.theme.spacing(0.5)}px;
`;

// Define the props for the ReportSharingPanel component
interface ReportSharingPanelProps {
  reportId: string;
  onShareComplete?: () => void;
}

/**
 * Component that renders a panel for sharing analytics reports with other users
 * @param {ReportSharingPanelProps} props - The props for the component
 * @returns {JSX.Element} The rendered component
 */
const ReportSharingPanel: React.FC<ReportSharingPanelProps> = ({ reportId, onShareComplete }) => {
  // LD1: Define state variables for modal open status, selected users, permission level, and message
  const [isOpen, setIsOpen] = useState(false);
  const [selectedUsers, setSelectedUsers] = useState<User[]>([]);
  const [permission, setPermission] = useState('view');
  const [message, setMessage] = useState('');

  // LD1: Define state for loading status and available users list
  const [loading, setLoading] = useState(false);
  const [availableUsers, setAvailableUsers] = useState<User[]>([]);

  // LD1: Use usePermissions hook to check if user has permission to share reports
  const { can } = usePermissions();
  const hasSharePermission = can('share', 'reports', 'organization');

  // LD1: Use useOrganization hook to get the current organization context
  const { currentOrganization } = useOrganization();

  /**
   * Opens the sharing modal and resets form state
   */
  const handleOpenModal = useCallback(() => {
    setIsOpen(true);
    setSelectedUsers([]);
    setPermission('view');
    setMessage('');
  }, []);

  /**
   * Closes the sharing modal and resets form state
   */
  const handleCloseModal = useCallback(() => {
    setIsOpen(false);
    setSelectedUsers([]);
    setPermission('view');
    setMessage('');
  }, []);

  /**
   * Handles changes to the selected users in the Autocomplete component
   * @param {any} event - The event object
   * @param {User[]} newValue - The new array of selected users
   */
  const handleUserChange = useCallback((event: any, newValue: User[]) => {
    setSelectedUsers(newValue);
  }, []);

  /**
   * Handles changes to the permission level dropdown
   * @param {React.ChangeEvent<HTMLInputElement>} event - The event object
   */
  const handlePermissionChange = useCallback((event: React.ChangeEvent<HTMLInputElement>) => {
    setPermission(event.target.value);
  }, []);

  /**
   * Handles changes to the share message text field
   * @param {React.ChangeEvent<HTMLInputElement>} event - The event object
   */
  const handleMessageChange = useCallback((event: React.ChangeEvent<HTMLInputElement>) => {
    setMessage(event.target.value);
  }, []);

  /**
   * Handles the share form submission
   * @param {React.FormEvent} event - The form event object
   */
  const handleSubmit = useCallback(async (event: React.FormEvent) => {
    event.preventDefault();

    if (selectedUsers.length === 0) {
      toast.warn('Please select at least one user to share with.');
      return;
    }

    setLoading(true);
    try {
      await shareReport(reportId, selectedUsers.map(user => user.id), permission, message);
      toast.success('Report shared successfully!');
      onShareComplete?.();
      handleCloseModal();
    } catch (error: any) {
      toast.error(`Failed to share report: ${error.message}`);
    } finally {
      setLoading(false);
    }
  }, [reportId, selectedUsers, permission, message, onShareComplete, handleCloseModal]);

  /**
   * Fetches users that the report can be shared with
   */
  const fetchUsers = useCallback(async () => {
    setLoading(true);
    try {
      const users = await getUsers();
      // Filter users based on permissions and relationship to current organization
      const filteredUsers = users.items.filter(user => {
        // Exclude users from other organizations
        if (currentOrganization && user.organizationId !== currentOrganization.id) {
          return false;
        }
        return true;
      });
      setAvailableUsers(filteredUsers);
    } catch (error: any) {
      toast.error(`Failed to fetch users: ${error.message}`);
    } finally {
      setLoading(false);
    }
  }, [currentOrganization]);

  // LD1: Set up useEffect to fetch available users when the modal opens
  useEffect(() => {
    if (isOpen) {
      fetchUsers();
    }
  }, [isOpen, fetchUsers]);

  // LD1: Render the component
  return (
    <div>
      <Button onClick={handleOpenModal} disabled={!hasSharePermission}>
        Share Report
      </Button>

      <Modal isOpen={isOpen} onClose={handleCloseModal} title="Share Report">
        <form onSubmit={handleSubmit}>
          <StyledAutocomplete
            multiple
            id="user-autocomplete"
            options={availableUsers}
            getOptionLabel={(user) => user.name}
            value={selectedUsers}
            onChange={handleUserChange}
            filterSelectedOptions
            renderInput={(params) => (
              <TextField
                {...params}
                label="Share with Users"
                placeholder="Select users to share with"
              />
            )}
            renderTags={(value, getTagProps) =>
              value.map((option: User, index: number) => (
                <StyledChip
                  key={option.id}
                  label={option.name}
                  {...getTagProps({ index })}
                />
              ))
            }
            loading={loading}
            renderOption={(props, option) => (
              <li {...props} key={option.id}>
                {option.name} ({option.email})
              </li>
            )}
          />

          <Select
            label="Permission"
            name="permission"
            value={permission}
            onChange={handlePermissionChange}
            options={[
              { value: 'view', label: 'View Only' },
              { value: 'edit', label: 'View and Edit' },
            ]}
            fullWidth
            required
          />

          <TextField
            label="Message (optional)"
            name="message"
            value={message}
            onChange={handleMessageChange}
            multiline
            rows={4}
            fullWidth
          />

          <Button type="button" onClick={handleCloseModal}>
            Cancel
          </Button>
          <Button type="submit" variant="primary" disabled={loading}>
            {loading ? <CircularProgress size={24} /> : 'Share'}
          </Button>
        </form>
      </Modal>
    </div>
  );
};

export default ReportSharingPanel;