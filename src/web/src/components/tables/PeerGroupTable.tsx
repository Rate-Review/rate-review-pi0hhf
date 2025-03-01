import React, { useState, useEffect, useMemo, useCallback } from 'react'; // React v18.0+
import { useSelector } from 'react-redux'; // react-redux v8.0.5
import { useTranslation } from 'react-i18next'; // react-i18next v12.0.0
import styled from 'styled-components'; // styled-components v5.3.5
import DataTable from './DataTable';
import Button from '../common/Button';
import Badge from '../common/Badge';
import Tooltip from '../common/Tooltip';
import Select from '../common/Select';
import TextField from '../common/TextField';
import useOrganizations from '../../hooks/useOrganizations';
import usePermissions from '../../hooks/usePermissions';
import { PeerGroupRelation, Organization, OrganizationType } from '../../types/organization';

/**
 * Interface defining the props for the PeerGroupTable component
 */
interface PeerGroupTableProps {
  peerGroups: PeerGroupRelation[];
  onEdit: (peerGroup: PeerGroupRelation) => void;
  onDelete: (peerGroupId: string) => void;
  isLoading: boolean;
  showFilters: boolean;
  className?: string;
}

/**
 * Container for the peer group table
 */
const PeerGroupTableContainer = styled.div`
  display: flex;
  flex-direction: column;
  width: 100%;
`;

/**
 * Container for filter controls
 */
const FilterContainer = styled.div`
  display: flex;
  flex-wrap: wrap;
  gap: 16px;
  margin-bottom: 16px;
`;

/**
 * Container for action buttons
 */
const ActionContainer = styled.div`
  display: flex;
  gap: 8px;
  justify-content: flex-end;
`;

/**
 * Container for criteria display
 */
const CriteriaContainer = styled.div`
  display: flex;
  flex-direction: column;
  gap: 4px;
`;

/**
 * Styled extension of the DataTable component
 */
const StyledDataTable = styled(DataTable)`
  & .nameColumn {
    font-weight: 500;
  }

  & .criteriaColumn {
    color: #666;
    font-size: 0.875rem;
  }

  & .membersColumn {
    text-align: center;
  }

  & .actionColumn {
    width: 120px;
  }
`;

/**
 * A functional component that renders a table for displaying and managing peer groups
 */
const PeerGroupTable: React.FC<PeerGroupTableProps> = ({
  peerGroups,
  onEdit,
  onDelete,
  isLoading,
  showFilters,
  className,
}) => {
  // LD1: Set up state for filters (type, search)
  const [filters, setFilters] = useState({
    type: 'all',
    search: '',
  });

  // LD1: Use useOrganizations hook to access peer group data and operations
  const {  } = useOrganizations();

  // LD1: Use usePermissions hook to check user permissions for peer group actions
  const { checkPermission } = usePermissions();

  /**
   * Handles changes to filter selections
   */
  const handleFilterChange = (filterName: string, value: any) => {
    // LD1: Create a new filters object by spreading the current filters
    setFilters(prevFilters => ({
      ...prevFilters,
      [filterName]: value,
    }));
  };

  /**
   * Handles the edit action for a peer group
   */
  const handleEdit = (peerGroup: PeerGroupRelation) => {
    // LD1: Check if the onEdit callback is provided
    if (onEdit) {
      // LD1: Call the onEdit callback with the peer group data
      onEdit(peerGroup);
    } else {
      console.error('Edit callback not provided');
    }
  };

  /**
   * Handles the delete action for a peer group
   */
  const handleDelete = (peerGroup: PeerGroupRelation) => {
    // LD1: Check if the onDelete callback is provided
    if (onDelete) {
      // LD1: Call the onDelete callback with the peer group ID
      onDelete(peerGroup.id);
    } else {
      console.error('Delete callback not provided');
    }
  };

  /**
   * Formats peer group criteria into readable text
   */
  const formatCriteria = (criteria: any[]): string => {
    // LD1: Check if criteria is an array and has items
    if (Array.isArray(criteria) && criteria.length > 0) {
      // LD1: Map each criterion to a readable string (e.g., 'Geography: New York')
      const criteriaStrings = criteria.map(criterion => {
        const [key, value] = Object.entries(criterion)[0];
        return `${key}: ${value}`;
      });

      // LD1: Join the strings with commas
      return criteriaStrings.join(', ');
    }

    // LD1: Return 'None' if no criteria are found
    return 'None';
  };

  /**
   * Renders a cell displaying the number of members in a peer group
   */
  const renderMembersCell = (peerGroup: PeerGroupRelation): JSX.Element => {
    // LD1: Extract members array from peer group
    const members = peerGroup.members || [];

    // LD1: Get the count of members
    const memberCount = members.length;

    // LD1: Render a Badge component with the count
    return (
      <Badge content={memberCount} variant="primary">
        {/* LD1: Add a Tooltip showing the list of member names if available */}
        {memberCount > 0 && (
          <Tooltip content={members.join(', ')}>
            <span>{memberCount} Members</span>
          </Tooltip>
        )}
      </Badge>
    );
  };

  /**
   * Renders filter options for peer group types
   */
  const renderTypeFilterOptions = (): JSX.Element => {
    // LD1: Create options array for different group types (All, Law Firm, Client)
    const options = [
      { value: 'all', label: 'All' },
      { value: OrganizationType.LawFirm, label: 'Law Firm' },
      { value: OrganizationType.Client, label: 'Client' },
    ];

    // LD1: Return a Select component with the options
    return (
      <Select
        name="type"
        label="Type"
        options={options}
        value={filters.type}
        onChange={(value) => handleFilterChange('type', value)} // LD1: Bind to handleFilterChange for the 'type' filter
      />
    );
  };

  /**
   * Renders action buttons for a peer group row
   */
  const renderActionCell = (peerGroup: PeerGroupRelation): JSX.Element => {
    // LD1: Use checkPermission from usePermissions hook to determine available actions
    const canEdit = checkPermission('update', 'peer_groups', 'organization');
    const canDelete = checkPermission('delete', 'peer_groups', 'organization');

    return (
      <ActionContainer>
        {/* LD1: Render edit button if user has edit permission */}
        {canEdit && (
          <Button variant="text" size="small" onClick={() => handleEdit(peerGroup)}>
            Edit
          </Button>
        )}

        {/* LD1: Render delete button if user has delete permission */}
        {canDelete && (
          <Button variant="text" size="small" onClick={() => handleDelete(peerGroup)}>
            Delete
          </Button>
        )}
      </ActionContainer>
    );
  };

  // LD1: Define memoized filtered peer groups based on filter state
  const filteredPeerGroups = useMemo(() => {
    let filtered = [...peerGroups];

    if (filters.type !== 'all') {
      filtered = filtered.filter(group => group.type === filters.type);
    }

    if (filters.search) {
      filtered = filtered.filter(group =>
        group.name.toLowerCase().includes(filters.search.toLowerCase())
      );
    }

    return filtered;
  }, [peerGroups, filters]);

  // LD1: Define the tableColumns configuration with appropriate rendering for each column
  const tableColumns = useMemo(() => [
    {
      id: 'name',
      label: 'Name',
      sortable: true,
      className: 'nameColumn',
    },
    {
      id: 'description',
      label: 'Description',
      sortable: false,
    },
    {
      id: 'criteria',
      label: 'Criteria',
      sortable: false,
      className: 'criteriaColumn',
      renderCell: (peerGroup: PeerGroupRelation) => (
        <CriteriaContainer>{formatCriteria(peerGroup.criteria)}</CriteriaContainer>
      ),
    },
    {
      id: 'members',
      label: 'Members',
      sortable: false,
      className: 'membersColumn',
      renderCell: (peerGroup: PeerGroupRelation) => renderMembersCell(peerGroup),
    },
    {
      id: 'actions',
      label: 'Actions',
      sortable: false,
      className: 'actionColumn',
      renderCell: (peerGroup: PeerGroupRelation) => renderActionCell(peerGroup),
    },
  ], [checkPermission]);

  // LD1: Return JSX with filter controls and DataTable component
  return (
    <PeerGroupTableContainer className={className}>
      {showFilters && (
        <FilterContainer>
          {renderTypeFilterOptions()}
          <TextField
            name="search"
            label="Search"
            placeholder="Search by name"
            value={filters.search}
            onChange={(e) => handleFilterChange('search', e.target.value)}
          />
        </FilterContainer>
      )}
      <StyledDataTable
        title="Peer Groups"
        columns={tableColumns}
        data={filteredPeerGroups}
        isLoading={isLoading}
      />
    </PeerGroupTableContainer>
  );
};

export default PeerGroupTable;