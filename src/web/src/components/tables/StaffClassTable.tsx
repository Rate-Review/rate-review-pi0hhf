import React, { useMemo } from 'react'; // ^18.0.0
import { Edit, Delete, Add } from '@mui/icons-material'; // ^5.14+
import { IconButton, Chip } from '@mui/material'; // ^5.14+
import DataTable, { ColumnDef } from './DataTable';
import Button from '../common/Button';
import StatusIndicator from '../common/StatusIndicator';
import Tooltip from '../common/Tooltip';
import { useWindowSize } from '../../hooks/useWindowSize';
import { formatCurrency } from '../../utils/currency';
import { formatDate } from '../../utils/date';

/**
 * Interface defining the props for the StaffClassTable component
 */
export interface StaffClassTableProps {
  data: StaffClass[];
  isLoading: boolean;
  onEdit: (id: string) => void;
  onDelete: (id: string) => void;
  onRowClick?: (row: StaffClass) => void;
  customActions?: React.ReactNode;
  title?: string;
  pagination?: boolean;
  search?: boolean;
  emptyStateMessage?: string;
}

/**
 * Interface defining the structure of a staff class entity
 */
export interface StaffClass {
  id: string;
  name: string;
  organizationId: string;
  experienceType: string;
  minExperience: number;
  maxExperience: number;
  isActive: boolean;
  createdAt: string;
  updatedAt: string;
}

/**
 * Converts experience type enum value to a user-friendly label
 * @param experienceType 
 * @returns User-friendly label for experience type
 */
const getExperienceTypeLabel = (experienceType: string): string => {
  switch (experienceType) {
    case 'GRADUATION_YEAR':
      return 'Graduation Year';
    case 'BAR_DATE':
      return 'Bar Admission Date';
    case 'YEARS_IN_ROLE':
      return 'Years in Role';
    default:
      return experienceType;
  }
};

/**
 * Component that displays staff classes in a tabular format with filtering, sorting, and actions
 * @param props 
 * @returns Rendered StaffClassTable component
 */
const StaffClassTable: React.FC<StaffClassTableProps> = (props) => {
  // LD1: Destructure props to access data, onEdit, onDelete, etc.
  const {
    data,
    isLoading,
    onEdit,
    onDelete,
    onRowClick,
    customActions,
    title,
    pagination = true,
    search = true,
    emptyStateMessage = 'No staff classes available',
  } = props;

  // LD1: Use useMemo to define table columns with appropriate rendering
  const columns: ColumnDef<StaffClass>[] = useMemo(() => {
    // LD1: Define column configuration including ID, label, sortable, etc.
    return [
      {
        id: 'name',
        label: 'Name',
        sortable: true,
        minWidth: 150,
      },
      {
        id: 'experienceType',
        label: 'Experience Type',
        sortable: true,
        minWidth: 150,
        renderCell: (row) => getExperienceTypeLabel(row.experienceType),
      },
      {
        id: 'minExperience',
        label: 'Min Experience',
        sortable: true,
        minWidth: 120,
      },
      {
        id: 'maxExperience',
        label: 'Max Experience',
        sortable: true,
        minWidth: 120,
      },
      {
        id: 'isActive',
        label: 'Status',
        minWidth: 100,
        renderCell: (row) => (
          <StatusIndicator
            status={row.isActive ? 'Active' : 'Inactive'}
            label={row.isActive ? 'Active' : 'Inactive'}
            showDot
            showLabel
          />
        ),
      },
      {
        id: 'createdAt',
        label: 'Created At',
        sortable: true,
        minWidth: 150,
        renderCell: (row) => formatDate(row.createdAt),
      },
      {
        id: 'updatedAt',
        label: 'Updated At',
        sortable: true,
        minWidth: 150,
        renderCell: (row) => formatDate(row.updatedAt),
      },
      {
        id: 'actions',
        label: 'Actions',
        minWidth: 120,
        renderCell: (row) => (
          <div style={{ display: 'flex', gap: '8px' }}>
            <Tooltip title="Edit Staff Class">
              <IconButton aria-label="edit" onClick={() => onEdit(row.id)}>
                <Edit />
              </IconButton>
            </Tooltip>
            <Tooltip title="Delete Staff Class">
              <IconButton aria-label="delete" onClick={() => onDelete(row.id)}>
                <Delete />
              </IconButton>
            </Tooltip>
          </div>
        ),
      },
    ];
  }, [onEdit, onDelete]); // LD1: Add formatters for experience type, min/max experience, etc.

  // LD1: Return DataTable component with configured columns and data
  return (
    <DataTable<StaffClass>
      title={title}
      columns={columns}
      data={data}
      isLoading={isLoading}
      emptyStateMessage={emptyStateMessage}
      selectable={false}
      onRowClick={onRowClick}
      pagination={pagination}
      search={search}
      customActions={customActions}
    />
  ); // LD1: Pass through additional props like isLoading, pagination, etc.
};

export default StaffClassTable;