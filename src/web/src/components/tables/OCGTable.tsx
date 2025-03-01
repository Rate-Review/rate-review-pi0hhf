import React, { useState, useEffect, useCallback } from 'react'; // ^18.2.0
import DataTable, { ColumnDef } from './DataTable';
import Button from '../common/Button';
import StatusIndicator from '../common/StatusIndicator';
import Tooltip from '../common/Tooltip';
import ConfirmationDialog from '../common/ConfirmationDialog';
import {
  OCGDocument,
  OCGStatus,
  OrganizationSummary,
  ocgService,
} from '../../types/ocg';
import { usePermissions } from '../../hooks/usePermissions';
import { formatDate } from '../../utils/date';
import {
  Edit,
  Delete,
  Publish,
  PlayArrow,
  GetApp,
} from '@mui/icons-material'; // ^5.14.0
import { Box, IconButton, Menu, MenuItem } from '@mui/material'; // ^5.14.0

/**
 * Props for the OCGTable component
 */
interface OCGTableProps {
  data: OCGDocument[];
  isLoading: boolean;
  onEdit: (ocg: OCGDocument) => void;
  onView: (ocg: OCGDocument) => void;
  onPublish: (ocg: OCGDocument) => void;
  onNegotiate: (ocg: OCGDocument) => void;
  onDelete: (ocg: OCGDocument) => void;
  onRefresh: () => void;
  showClient?: boolean;
  userType?: string;
}

/**
 * Returns the appropriate color for a given OCG status
 * @param status The OCG status
 * @returns Color code for the status indicator
 */
const getStatusColor = (status: OCGStatus): string => {
  switch (status) {
    case OCGStatus.Draft:
      return 'gray';
    case OCGStatus.Published:
      return 'green';
    case OCGStatus.Negotiating:
      return 'orange';
    case OCGStatus.Signed:
      return 'blue';
    default:
      return 'gray';
  }
};

/**
 * Table component for displaying OCG documents with actions
 * @param props Props for the component
 * @returns Rendered OCG table component
 */
const OCGTable: React.FC<OCGTableProps> = (props) => {
  // LD1: Destructure props to access data, onEdit, onView, onPublish, onNegotiate, etc.
  const {
    data,
    isLoading,
    onEdit,
    onView,
    onPublish,
    onNegotiate,
    onDelete,
    onRefresh,
    showClient,
    userType,
  } = props;

  // LD1: Set up state for loading state, dialog visibility, and selected OCG
  const [isDeleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [selectedOCG, setSelectedOCG] = useState<OCGDocument | null>(null);

  // LD1: Set up permission checks with usePermissions hook
  const { can } = usePermissions();

  // LD1: Define table columns with appropriate cell renderers
  const columns: ColumnDef<OCGDocument>[] = [
    {
      id: 'title',
      label: 'Title',
      sortable: true,
      filterable: true,
      description: 'OCG document title',
    },
    {
      id: 'client',
      label: 'Client',
      sortable: true,
      filterable: true,
      description: 'Client organization name (shown only in law firm view)',
      conditional: true,
      condition: showClient === true,
    },
    {
      id: 'version',
      label: 'Version',
      sortable: true,
      filterable: false,
      description: 'OCG document version number',
    },
    {
      id: 'status',
      label: 'Status',
      sortable: true,
      filterable: true,
      description: 'Current OCG status with visual indicator',
      renderCell: (ocg) => (
        <StatusIndicator
          status={ocg.status}
          label={ocg.status}
          statusColorMap={{
            Draft: getStatusColor(OCGStatus.Draft),
            Published: getStatusColor(OCGStatus.Published),
            Negotiating: getStatusColor(OCGStatus.Negotiating),
            Signed: getStatusColor(OCGStatus.Signed),
          }}
        />
      ),
    },
    {
      id: 'updatedAt',
      label: 'Last Updated',
      sortable: true,
      filterable: true,
      description: 'Date of last update',
      renderCell: (ocg) => formatDate(ocg.updatedAt),
    },
    {
      id: 'actions',
      label: 'Actions',
      sortable: false,
      filterable: false,
      description: 'Action buttons for OCG management',
      renderCell: (ocg) => (
        <Box sx={{ display: 'flex', gap: 1, alignItems: 'center' }}>
          <Tooltip title="Edit">
            <span>
              <IconButton
                aria-label="edit"
                onClick={() => handleEdit(ocg)}
                disabled={!can('update', 'ocg', 'organization')}
              >
                <Edit />
              </IconButton>
            </span>
          </Tooltip>
          <Tooltip title="Publish">
            <span>
              <IconButton
                aria-label="publish"
                onClick={() => handlePublish(ocg)}
                disabled={!can('update', 'ocg', 'organization')}
              >
                <Publish />
              </IconButton>
            </span>
          </Tooltip>
          <Tooltip title="Start Negotiation">
            <span>
              <IconButton
                aria-label="negotiate"
                onClick={() => handleNegotiate(ocg)}
                disabled={!can('update', 'ocg', 'organization')}
              >
                <PlayArrow />
              </IconButton>
            </span>
          </Tooltip>
          <Tooltip title="Download">
            <span>
              <IconButton
                aria-label="download"
                onClick={() => handleDownload(ocg, 'pdf')}
                disabled={!can('read', 'ocg', 'organization')}
              >
                <GetApp />
              </IconButton>
            </span>
          </Tooltip>
          <Tooltip title="Delete">
            <span>
              <IconButton
                aria-label="delete"
                onClick={() => handleDelete(ocg)}
                disabled={!can('delete', 'ocg', 'organization')}
              >
                <Delete />
              </IconButton>
            </span>
          </Tooltip>
        </Box>
      ),
    },
  ];

  // LD1: Define action handlers for edit, delete, publish, start negotiation, etc.
  const handleEdit = (ocg: OCGDocument) => {
    onEdit(ocg);
  };

  const handleView = (ocg: OCGDocument) => {
    onView(ocg);
  };

  const handlePublish = (ocg: OCGDocument) => {
    onPublish(ocg);
  };

  const handleNegotiate = (ocg: OCGDocument) => {
    onNegotiate(ocg);
  };

  const handleDelete = (ocg: OCGDocument) => {
    setDeleteDialogOpen(true);
    setSelectedOCG(ocg);
  };

  const handleDownload = (ocg: OCGDocument, format: string) => {
    ocgService.downloadOCGDocument(ocg.id, format as 'pdf' | 'docx', `${ocg.title}.${format}`);
  };

  // LD1: Define confirmation dialog for delete action
  const confirmDelete = async () => {
    if (selectedOCG) {
      try {
        await ocgService.deleteOCG(selectedOCG.id);
        onDelete(selectedOCG);
      } catch (error) {
        console.error('Error deleting OCG:', error);
      } finally {
        setDeleteDialogOpen(false);
        setSelectedOCG(null);
        onRefresh();
      }
    }
  };

  // LD1: Return DataTable component with defined columns, data, and handlers
  return (
    <>
      <DataTable
        title="Outside Counsel Guidelines"
        data={data}
        columns={columns}
        isLoading={isLoading}
        selectable={false}
        onRowClick={handleView}
        customActions={
          <Button variant="outlined" onClick={onRefresh}>
            Refresh
          </Button>
        }
      />
      <ConfirmationDialog
        isOpen={isDeleteDialogOpen}
        title="Delete OCG"
        message="Are you sure you want to delete this OCG? This action cannot be undone."
        confirmText="Delete"
        cancelText="Cancel"
        confirmButtonVariant="danger"
        onConfirm={confirmDelete}
        onCancel={() => setDeleteDialogOpen(false)}
      />
    </>
  );
};

export default OCGTable;