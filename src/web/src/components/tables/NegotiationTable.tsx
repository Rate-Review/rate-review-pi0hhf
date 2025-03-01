import React, { useState, useMemo, useCallback, useEffect } from 'react'; // ^18.2.0
import { useNavigate } from 'react-router-dom'; // ^6.10.0
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Stack,
  Box,
  Typography,
  Chip,
  IconButton
} from '@mui/material'; // ^5.11.0
import {
  Edit,
  Delete,
  Visibility,
  CheckCircle,
  Cancel,
  ArrowForward
} from '@mui/icons-material'; // ^5.11.0

import DataTable from '../tables/DataTable';
import StatusIndicator from '../common/StatusIndicator';
import Button from '../common/Button';
import Tooltip from '../common/Tooltip';
import NegotiationFilters from '../negotiation/NegotiationFilters';
import { usePermissions } from '../../hooks/usePermissions';
import {
  Negotiation,
  NegotiationFilters as NegotiationFiltersType,
} from '../../types/negotiation';
import { NEGOTIATION_STATUS } from '../../constants/negotiations';
import { formatDate } from '../../utils/date';
import { useOrganizationContext } from '../../context/OrganizationContext';

/**
 * Interface defining the props for the NegotiationTable component
 */
interface NegotiationTableProps {
  negotiations: Negotiation[];
  isLoading: boolean;
  error: string | null;
  showFilters?: boolean;
  onNegotiationSelect?: (negotiation: Negotiation) => void;
}

/**
 * Returns the appropriate color for a negotiation status
 * @param {string} status - The status of the negotiation
 * @returns {string} The color code for the given status
 */
const getNegotiationStatusColor = (status: string): string => {
  switch (status) {
    case 'Approved':
    case 'Completed':
      return 'success';
    case 'Requested':
    case 'InProgress':
    case 'Countered':
      return 'warning';
    case 'Rejected':
      return 'error';
    default:
      return 'info';
  }
};

/**
 * Formats the negotiation status for display
 * @param {string} status - The status of the negotiation
 * @returns {string} Human-readable status text
 */
const formatStatus = (status: string): string => {
  switch (status) {
    case 'InProgress':
      return 'In Progress';
    case 'Countered':
      return 'Countered';
    default:
      return status.charAt(0).toUpperCase() + status.slice(1);
  }
};

/**
 * Component for displaying and interacting with negotiation data
 * @param {NegotiationTableProps} props - Props for the component
 * @returns {JSX.Element} Rendered NegotiationTable component
 */
export const NegotiationTable: React.FC<NegotiationTableProps> = ({
  negotiations,
  isLoading,
  error,
  showFilters = true,
  onNegotiationSelect
}) => {
  // LD1: Use useState hooks to manage component state (selectedRows, filters, pagination, etc.)
  const [selectedRows, setSelectedRows] = useState<string[]>([]);
  const [deleteConfirmationOpen, setDeleteConfirmationOpen] = useState(false);
  const [negotiationToDelete, setNegotiationToDelete] = useState<Negotiation | null>(null);

  // LD1: Use usePermissions hook to check user permissions for actions
  const { can } = usePermissions();

  // LD1: Use useOrganizationContext to determine organization type and role
  const { currentOrganization } = useOrganizationContext();

  // LD1: Use useNavigate for navigation to detail views
  const navigate = useNavigate();

  // LD1: Define handleSort, handlePageChange, handleRowsPerPageChange functions
  const handleSort = () => {
    console.log('Sorting');
  };

  const handlePageChange = () => {
    console.log('Page Change');
  };

  const handleRowsPerPageChange = () => {
    console.log('Rows Per Page Change');
  };

  // LD1: Define handleFilterChange function to update filters
  const handleFilterChange = () => {
    console.log('Filter Change');
  };

  // LD1: Define handleSelect and handleSelectAll functions for row selection
  const handleSelect = () => {
    console.log('Select');
  };

  const handleSelectAll = () => {
    console.log('Select All');
  };

  // LD1: Define action handlers (handleView, handleEdit, handleDelete, etc.)
  const handleView = (negotiation: Negotiation) => {
    navigate(`/negotiations/${negotiation.id}`);
  };

  const handleEdit = (negotiation: Negotiation) => {
    console.log('Edit negotiation:', negotiation);
  };

  const handleDelete = (negotiation: Negotiation) => {
    setNegotiationToDelete(negotiation);
    setDeleteConfirmationOpen(true);
  };

  const confirmDelete = () => {
    console.log('Deleting negotiation:', negotiationToDelete);
    setDeleteConfirmationOpen(false);
    setNegotiationToDelete(null);
  };

  const cancelDelete = () => {
    setDeleteConfirmationOpen(false);
    setNegotiationToDelete(null);
  };

  // LD1: Define getActionButtons function to return appropriate buttons based on status and permissions
  const getActionButtons = (negotiation: Negotiation) => {
    const buttons = [];

    buttons.push(
      <Tooltip key="view" title="View Negotiation">
        <IconButton onClick={() => handleView(negotiation)} aria-label="view">
          <Visibility />
        </IconButton>
      </Tooltip>
    );

    if (can('update', 'negotiations', 'organization')) {
      buttons.push(
        <Tooltip key="edit" title="Edit Negotiation">
          <IconButton onClick={() => handleEdit(negotiation)} aria-label="edit">
            <Edit />
          </IconButton>
        </Tooltip>
      );
    }

    if (can('delete', 'negotiations', 'organization')) {
      buttons.push(
        <Tooltip key="delete" title="Delete Negotiation">
          <IconButton onClick={() => handleDelete(negotiation)} aria-label="delete">
            <Delete />
          </IconButton>
        </Tooltip>
      );
    }

    return buttons;
  };

  // LD1: Use useMemo to calculate filteredNegotiations based on filters
  const filteredNegotiations = useMemo(() => {
    return negotiations;
  }, [negotiations]);

  // LD1: Define table columns with appropriate render functions
  const columns = useMemo(() => [
    {
      id: 'clientName',
      label: 'Client',
      sortable: true,
      renderCell: (negotiation: Negotiation) => negotiation.client.name,
    },
    {
      id: 'firmName',
      label: 'Law Firm',
      sortable: true,
      renderCell: (negotiation: Negotiation) => negotiation.firm.name,
    },
    {
      id: 'status',
      label: 'Status',
      sortable: true,
      renderCell: (negotiation: Negotiation) => (
        <StatusIndicator
          status={negotiation.status}
          label={formatStatus(negotiation.status)}
        />
      ),
    },
    {
      id: 'submissionDeadline',
      label: 'Deadline',
      sortable: true,
      renderCell: (negotiation: Negotiation) => formatDate(negotiation.submissionDeadline, 'MM/DD/YYYY'),
    },
    {
      id: 'actions',
      label: 'Actions',
      renderCell: (negotiation: Negotiation) => (
        <Stack direction="row" spacing={1}>
          {getActionButtons(negotiation)}
        </Stack>
      ),
    },
  ], [can, navigate]);

  // LD1: Return JSX with NegotiationFilters (if showFilters is true)
  // LD1: Return DataTable component with columns, data, and event handlers
  // LD1: Include confirmation dialog for delete actions
  return (
    <div>
      {showFilters && <NegotiationFilters onFilterChange={handleFilterChange} />}
      <DataTable
        title="Negotiations"
        columns={columns}
        data={filteredNegotiations}
        isLoading={isLoading}
        emptyStateMessage={error || 'No negotiations found.'}
        selectable
        onRowClick={(negotiation) => onNegotiationSelect?.(negotiation)}
        onSelectionChange={setSelectedRows}
        defaultSortField="submissionDeadline"
        defaultSortDirection="asc"
      />
      <Dialog
        open={deleteConfirmationOpen}
        onClose={cancelDelete}
        aria-labelledby="alert-dialog-title"
        aria-describedby="alert-dialog-description"
      >
        <DialogTitle id="alert-dialog-title">Confirm Delete</DialogTitle>
        <DialogContent>
          Are you sure you want to delete this negotiation?
        </DialogContent>
        <DialogActions>
          <Button onClick={cancelDelete} variant="text">
            Cancel
          </Button>
          <Button onClick={confirmDelete} variant="primary">
            Delete
          </Button>
        </DialogActions>
      </Dialog>
    </div>
  );
};