import React, { useState, useEffect, useMemo, useCallback } from 'react'; // ^18.2.0
import { useNavigate } from 'react-router-dom'; // ^6.4.0
import DataTable, { ColumnDef } from './DataTable';
import Button from '../common/Button';
import SearchBar from '../common/SearchBar';
import Select from '../common/Select';
import StatusIndicator from '../common/StatusIndicator';
import { Attorney } from '../../types/attorney';
import { usePermissions } from '../../hooks/usePermissions';
import { formatDate } from '../../utils/date';

/**
 * @interface AttorneyTableProps
 * @description Props for the AttorneyTable component
 */
interface AttorneyTableProps {
  attorneys: Attorney[] | undefined;
  loading: boolean;
  onRowAction: (action: string, attorney: Attorney) => void;
  initialFilters?: Record<string, any>;
  showActions?: boolean;
  selectable?: boolean;
  onSelectionChange?: (selectedIds: string[]) => void;
  selectedIds?: string[];
  customColumns?: any[];
}

/**
 * @interface AttorneyTableState
 * @description Internal state for the AttorneyTable component
 */
interface AttorneyTableState {
  searchQuery: string;
  filters: Record<string, any>;
  page: number;
  pageSize: number;
  sortField: string;
  sortDirection: 'asc' | 'desc';
}

/**
 * @component AttorneyTable
 * @description A functional component that displays attorney information in a tabular format
 */
const AttorneyTable: React.FC<AttorneyTableProps> = (props) => {
  // LD1: Destructure props
  const {
    attorneys = [],
    loading,
    onRowAction,
    initialFilters = {},
    showActions = true,
    selectable = false,
    onSelectionChange,
    selectedIds = [],
    customColumns = []
  } = props;

  // LD1: Initialize state using useState hook
  const [state, setState] = useState<AttorneyTableState>({
    searchQuery: '',
    filters: initialFilters,
    page: 1,
    pageSize: 10,
    sortField: 'name',
    sortDirection: 'asc',
  });

  // LD1: Access navigate function from useNavigate hook
  const navigate = useNavigate();

  // LD1: Access permission checking functions from usePermissions hook
  const { can } = usePermissions();

  // LD1: Define handleSearch function to update search query state
  const handleSearch = (query: string) => {
    setState(prevState => ({ ...prevState, searchQuery: query, page: 1 }));
  };

  // LD1: Define handleFilterChange function to update filter state
  const handleFilterChange = (filterName: string, value: string) => {
    setState(prevState => ({
      ...prevState,
      filters: { ...prevState.filters, [filterName]: value },
      page: 1,
    }));
  };

  // LD1: Define handleRowAction function to handle row actions
  const handleRowAction = (action: string, attorney: Attorney) => {
    if (action === 'view') {
      navigate(`/attorneys/${attorney.id}`);
    } else if (action === 'edit') {
      navigate(`/attorneys/${attorney.id}/edit`);
    } else if (action === 'delete') {
      // TODO: Implement delete confirmation dialog
      console.log(`Deleting attorney ${attorney.id}`);
    }
    onRowAction(action, attorney);
  };

  // LD1: Define getFilterOptions function to generate filter options
  const getFilterOptions = (attorneys: Attorney[]) => {
    const offices = [...new Set(attorneys.map(attorney => attorney.organization?.name))].map(office => ({ value: office, label: office }));
    const practiceAreas = [...new Set(attorneys.flatMap(attorney => attorney.practiceAreas))].map(area => ({ value: area, label: area }));
    return { offices, practiceAreas };
  };

  // LD1: Memoize filter options using useMemo hook
  const filterOptions = useMemo(() => getFilterOptions(attorneys), [attorneys]);

  // LD1: Define renderFilters function to render filter controls
  const renderFilters = () => (
    <div style={{ display: 'flex', gap: '16px', alignItems: 'center', padding: '16px' }}>
      <SearchBar placeholder="Search Attorneys" onSearch={handleSearch} />
      <Select
        name="office"
        label="Office"
        options={filterOptions.offices}
        value={state.filters.office || ''}
        onChange={(value) => handleFilterChange('office', value)}
      />
      <Select
        name="practiceArea"
        label="Practice Area"
        options={filterOptions.practiceAreas}
        value={state.filters.practiceArea || ''}
        onChange={(value) => handleFilterChange('practiceArea', value)}
      />
      <Button onClick={() => setState(prevState => ({ ...prevState, filters: {}, page: 1 }))}>Clear Filters</Button>
    </div>
  );

  // LD1: Define renderActions function to render action buttons
  const renderActions = () => (
    <div>
      {can('create', 'attorneys', 'organization') && (
        <Button variant="primary" onClick={() => navigate('/attorneys/new')}>
          Add Attorney
        </Button>
      )}
      {can('export', 'attorneys', 'organization') && (
        <Button variant="outline">
          Export
        </Button>
      )}
    </div>
  );

  // LD1: Define getColumns function to define table columns
  const getColumns = (): ColumnDef<Attorney>[] => [
    { id: 'name', label: 'Name', sortable: true, renderCell: (attorney) => attorney.name },
    { id: 'organization', label: 'Law Firm', sortable: true, renderCell: (attorney) => attorney.organization?.name },
    { id: 'office', label: 'Office', renderCell: (attorney) => attorney.officeIds?.join(', ') },
    { id: 'practiceAreas', label: 'Practice Area', renderCell: (attorney) => attorney.practiceAreas?.join(', ') },
    { id: 'barDate', label: 'Bar Date', sortable: true, renderCell: (attorney) => formatDate(attorney.barDate) },
    { id: 'status', label: 'Status', renderCell: (attorney) => <StatusIndicator status="Active" /> },
    ...(showActions ? [{
      id: 'actions',
      label: 'Actions',
      renderCell: (attorney) => (
        <>
          <Button size="small" onClick={() => handleRowAction('view', attorney)}>View</Button>
          {can('update', 'attorneys', 'organization') && (
            <Button size="small" onClick={() => handleRowAction('edit', attorney)}>Edit</Button>
          )}
          {can('delete', 'attorneys', 'organization') && (
            <Button size="small" onClick={() => handleRowAction('delete', attorney)}>Delete</Button>
          )}
        </>
      ),
    }] : []),
    ...customColumns,
  ];

  // LD1: Memoize columns using useMemo hook
  const columns = useMemo(() => getColumns(), [can, navigate, showActions, customColumns]);

  // LD1: Define filterAttorneys function to filter attorney data
  const filterAttorneys = (attorneys: Attorney[]): Attorney[] => {
    return attorneys.filter(attorney => {
      const searchRegex = new RegExp(state.searchQuery, 'i');
      return (
        searchRegex.test(attorney.name) ||
        searchRegex.test(attorney.organization?.name || '') ||
        attorney.practiceAreas.some(area => searchRegex.test(area))
      ) &&
        (state.filters.office ? attorney.organization?.name === state.filters.office : true) &&
        (state.filters.practiceArea ? attorney.practiceAreas.includes(state.filters.practiceArea) : true);
    });
  };

  // LD1: Memoize filtered attorneys using useMemo hook
  const filteredAttorneys = useMemo(() => filterAttorneys(attorneys), [attorneys, state.searchQuery, state.filters]);

  // LD1: Render the component
  return (
    <div>
      {renderFilters()}
      {renderActions()}
      <DataTable
        title="Attorneys"
        data={filteredAttorneys}
        columns={columns}
        isLoading={loading}
        selectable={selectable}
        onSelectionChange={onSelectionChange}
        onRowClick={(attorney) => handleRowAction('view', attorney)}
      />
    </div>
  );
};

export default AttorneyTable;