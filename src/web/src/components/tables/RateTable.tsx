import React, { useState, useEffect, useMemo, useCallback } from 'react'; // ^18.0.0
import { useTranslation } from 'react-i18next'; // ^12.0.0
import styled from 'styled-components'; // ^5.3.5
import { DataTable } from './DataTable';
import { Button } from '../common/Button';
import { TextField } from '../common/TextField';
import { Select } from '../common/Select';
import { Checkbox } from '../common/Checkbox';
import { StatusIndicator } from '../common/StatusIndicator';
import { Tooltip } from '../common/Tooltip';
import { RecommendationCard } from '../ai/RecommendationCard';
import { RateType, RateStatus, useRates } from '../../hooks/useRates';
import { usePermissions } from '../../hooks/usePermissions';
import { formatCurrency } from '../../utils/formatting';
import { calculatePercentageChange } from '../../utils/calculations';
import { RATE_STATUS_COLORS } from '../../constants/rates';

// Define the RateTableProps interface
interface RateTableProps {
  rates: RateType[];
  mode: string;
  onRateUpdate?: (rate: RateType) => void;
  onRateSelect?: (selectedRates: string[]) => void;
  onBulkAction?: (action: string, value: any) => void;
  showAIRecommendations?: boolean;
  isRealTime?: boolean;
  className?: string;
}

// Styled components
const RateTableContainer = styled.div`
  display: flex;
  flex-direction: column;
  width: 100%;
`;

const FilterContainer = styled.div`
  display: flex;
  flex-wrap: wrap;
  gap: 16px;
  margin-bottom: 16px;
`;

const ActionContainer = styled.div`
  display: flex;
  gap: 8px;
  justify-content: flex-end;
`;

const PercentageBadge = styled.div<{ exceedingMax: boolean }>`
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 0.875rem;
  font-weight: 500;
  background-color: ${props => props.exceedingMax ? 'rgba(229, 62, 62, 0.15)' : 'rgba(56, 161, 105, 0.15)'};
  color: ${props => props.exceedingMax ? '#E53E3E' : '#38A169'};
`;

const StyledDataTable = styled(DataTable)`
  & .rateColumn {
    font-weight: 500;
  }

  & .percentageColumn {
    text-align: right;
  }

  & .actionColumn {
    width: 180px;
  }
`;

// RateTable component definition
const RateTable: React.FC<RateTableProps> = ({
  rates,
  mode,
  onRateUpdate,
  onRateSelect,
  onBulkAction,
  showAIRecommendations = false,
  isRealTime = false,
  className,
}) => {
  // Destructure props to access rates, mode, callbacks, etc.
  const { t } = useTranslation();

  // Set up state using useState hooks for selectedRates, filteredRates, sortColumn, sortDirection
  const [selectedRates, setSelectedRates] = useState<string[]>([]);
  const [filteredRates, setFilteredRates] = useState<RateType[]>(rates);
  const [sortColumn, setSortColumn] = useState<string>('attorneyName');
  const [sortDirection, setSortDirection] = useState<'asc' | 'desc'>('asc');

  // Set up state for filters (staffClass, attorney, status, office, search)
  const [filters, setFilters] = useState({
    staffClass: '',
    attorney: '',
    status: '',
    office: '',
    search: '',
  });

  // Use useRates hook to access rate operations like approveRate, rejectRate, counterRate, updateRate
  const { approveRate, rejectRate, counterRate, updateRate } = useRates();

  // Use usePermissions hook to check user permissions for rate actions
  const { can } = usePermissions();

  // Define memoized filter options using the getFilterOptions helper function
  const filterOptions = useMemo(() => getFilterOptions(rates), [rates]);

  // Define the handleRateChange function for updating rate values
  const handleRateChange = useCallback((rateId: string, event: React.ChangeEvent<HTMLInputElement>) => {
    event.preventDefault();
    const newRateValue = event.target.value;

    if (!/^\d*\.?\d*$/.test(newRateValue)) {
      return;
    }

    const newRate = parseFloat(newRateValue);

    if (isNaN(newRate)) {
      return;
    }

    const updatedRates = rates.map(rate => {
      if (rate.id === rateId) {
        return { ...rate, amount: newRate };
      }
      return rate;
    });

    if (isRealTime) {
      updateRate(rateId, { amount: newRate });
    }
  }, [rates, isRealTime, updateRate]);

  // Define the handleSelectAll function for selecting/deselecting all rows
  const handleSelectAll = useCallback((event: React.ChangeEvent<HTMLInputElement>) => {
    const checked = event.target.checked;
    if (checked) {
      const allRateIds = filteredRates.map(rate => rate.id);
      setSelectedRates(allRateIds);
      onRateSelect?.(allRateIds);
    } else {
      setSelectedRates([]);
      onRateSelect?.([]);
    }
  }, [filteredRates, onRateSelect]);

  // Define the handleRowSelect function for selecting individual rows
  const handleRowSelect = useCallback((rateId: string, selected: boolean) => {
    setSelectedRates(prevSelected => {
      if (selected) {
        return [...prevSelected, rateId];
      } else {
        return prevSelected.filter(id => id !== rateId);
      }
    });
  }, []);

  // Define the handleFilterChange function for updating filters
  const handleFilterChange = useCallback((filterName: string, value: string | string[]) => {
    setFilters(prevFilters => ({
      ...prevFilters,
      [filterName]: value,
    }));
  }, []);

  // Define the handleSort function for sorting columns
  const handleSort = useCallback((column: string) => {
    if (sortColumn === column) {
      setSortDirection(sortDirection === 'asc' ? 'desc' : 'asc');
    } else {
      setSortColumn(column);
      setSortDirection('asc');
    }
  }, [sortColumn, sortDirection]);

  // Define the applyBulkAction function for batch operations on selected rates
  const applyBulkAction = useCallback((action: string, value: any) => {
    if (selectedRates.length === 0) {
      alert('Please select rates to apply this action.');
      return;
    }

    if (action === 'approve') {
      selectedRates.forEach(rateId => approveRate(rateId));
    } else if (action === 'reject') {
      selectedRates.forEach(rateId => rejectRate(rateId));
    } else if (action === 'counter') {
      selectedRates.forEach(rateId => counterRate({ rateId, amount: value }));
    }

    onBulkAction?.(action, value);
    setSelectedRates([]);
  }, [selectedRates, approveRate, rejectRate, counterRate, onBulkAction]);

  // Use useEffect to update filteredRates when rates or filters change
  useEffect(() => {
    let newFilteredRates = [...rates];

    if (filters.staffClass) {
      newFilteredRates = newFilteredRates.filter(rate => rate.staffClassId === filters.staffClass);
    }
    if (filters.attorney) {
      newFilteredRates = newFilteredRates.filter(rate => rate.attorneyId === filters.attorney);
    }
    if (filters.status) {
      newFilteredRates = newFilteredRates.filter(rate => rate.status === filters.status);
    }
    if (filters.office) {
      newFilteredRates = newFilteredRates.filter(rate => rate.officeId === filters.office);
    }
    if (filters.search) {
      const searchTerm = filters.search.toLowerCase();
      newFilteredRates = newFilteredRates.filter(rate =>
        rate.attorneyName.toLowerCase().includes(searchTerm) ||
        rate.staffClassName.toLowerCase().includes(searchTerm)
      );
    }

    setFilteredRates(newFilteredRates);
  }, [rates, filters]);

  // Define the tableColumns configuration with appropriate rendering for each column type
  const tableColumns = useMemo(() => [
    {
      id: 'select',
      label: '',
      sortable: false,
      filterable: false,
      renderCell: (rate: RateType) => (
        <Checkbox
          checked={selectedRates.includes(rate.id)}
          onChange={(selected) => handleRowSelect(rate.id, selected)}
        />
      ),
    },
    {
      id: 'attorneyName',
      label: t('Attorney'),
      sortable: true,
      renderCell: (rate: RateType) => rate.attorneyName,
    },
    {
      id: 'staffClass',
      label: t('Staff Class'),
      sortable: true,
      renderCell: (rate: RateType) => rate.staffClassName,
    },
    {
      id: 'currentRate',
      label: t('Current Rate'),
      sortable: true,
      renderCell: (rate: RateType) => renderRateCell(rate, 'currentRate', false),
    },
    {
      id: 'proposedRate',
      label: t('Proposed Rate'),
      sortable: true,
      renderCell: (rate: RateType) => renderRateCell(rate, 'proposedRate', mode === 'edit' || mode === 'negotiation'),
    },
    {
      id: 'percentageChange',
      label: t('Change'),
      sortable: false,
      filterable: false,
      renderCell: (rate: RateType) => renderPercentageCell(rate.proposedRate, rate.currentRate, 5),
    },
    {
      id: 'status',
      label: t('Status'),
      sortable: false,
      filterable: true,
      renderCell: (rate: RateType) => (
        <StatusIndicator status={rate.status} statusColorMap={RATE_STATUS_COLORS} />
      ),
    },
    {
      id: 'actions',
      label: t('Actions'),
      sortable: false,
      filterable: false,
      renderCell: (rate: RateType) => renderActionCell(rate),
    },
  ], [t, selectedRates, handleRowSelect, mode, can]);

  // Return JSX with filter controls, bulk action controls, and DataTable component
  return (
    <RateTableContainer className={className}>
      {renderFilters()}
      {renderBulkActions()}
      <StyledDataTable
        data={filteredRates}
        columns={tableColumns}
        selectable
        onSelectionChange={(selected) => setSelectedRates(selected.map(item => item.id))}
      />
    </RateTableContainer>
  );

  function getFilterOptions(rates: RateType[]) {
    const staffClasses = [...new Set(rates.map(rate => rate.staffClassName))].sort();
    const attorneys = [...new Set(rates.map(rate => rate.attorneyName))].sort();
    const statuses = [...new Set(rates.map(rate => rate.status))].sort();
    const offices = [...new Set(rates.map(rate => rate.officeName))].sort();

    return {
      staffClassOptions: staffClasses.map(staffClass => ({ value: staffClass, label: staffClass })),
      attorneyOptions: attorneys.map(attorney => ({ value: attorney, label: attorney })),
      statusOptions: statuses.map(status => ({ value: status, label: status })),
      officeOptions: offices.map(office => ({ value: office, label: office })),
    };
  }

  function renderRateCell(rate: RateType, field: string, editable: boolean) {
    const rateValue = rate[field];
    const formattedRate = formatCurrency(rateValue);

    if (editable && mode === 'edit' || mode === 'negotiation') {
      return (
        <TextField
          value={rateValue}
          onChange={(event) => handleRateChange(rate.id, event)}
          data-testid={`rate-input-${rate.id}`}
        />
      );
    } else {
      return <div data-testid={`rate-value-${rate.id}`}>{formattedRate}</div>;
    }
  }

  function renderPercentageCell(currentValue: number, previousValue: number, maxAllowedPercentage: number) {
    const percentageChange = calculatePercentageChange(currentValue, previousValue);
    const formattedPercentage = (percentageChange > 0 ? '+' : '') + percentageChange.toFixed(1) + '%';
    const exceedingMax = Math.abs(percentageChange) > maxAllowedPercentage;

    return (
      <Tooltip title={exceedingMax ? "Exceeds maximum allowed percentage" : ""}>
        <PercentageBadge exceedingMax={exceedingMax}>
          {formattedPercentage}
        </PercentageBadge>
      </Tooltip>
    );
  }

  function renderActionCell(rate: RateType) {
    return (
      <ActionContainer>
        {mode === 'negotiation' && (
          <>
            {can('approve', 'rates', 'organization') && (
              <Button size="small" onClick={() => approveRate(rate.id)} data-testid={`approve-button-${rate.id}`}>
                Approve
              </Button>
            )}
            {can('reject', 'rates', 'organization') && (
              <Button size="small" onClick={() => rejectRate(rate.id)} data-testid={`reject-button-${rate.id}`}>
                Reject
              </Button>
            )}
            {can('counter', 'rates', 'organization') && (
              <Button size="small" onClick={() => counterRate({ rateId: rate.id, amount: 100 })} data-testid={`counter-button-${rate.id}`}>
                Counter
              </Button>
            )}
          </>
        )}
        {mode === 'edit' && (
          <>
            {can('update', 'rates', 'organization') && (
              <Button size="small" onClick={() => { }} data-testid={`edit-button-${rate.id}`}>
                Edit
              </Button>
            )}
            {can('delete', 'rates', 'organization') && (
              <Button size="small" onClick={() => { }} data-testid={`delete-button-${rate.id}`}>
                Delete
              </Button>
            )}
          </>
        )}
        {mode === 'view' && (
          <Button size="small" onClick={() => { }} data-testid={`view-button-${rate.id}`}>
            View Details
          </Button>
        )}
      </ActionContainer>
    );
  }

  function renderFilters() {
    return (
      <FilterContainer>
        <Select
          label="Staff Class"
          name="staffClass"
          options={filterOptions.staffClassOptions}
          value={filters.staffClass}
          onChange={(value) => handleFilterChange('staffClass', value)}
          data-testid="staff-class-filter"
        />
        <Select
          label="Attorney"
          name="attorney"
          options={filterOptions.attorneyOptions}
          value={filters.attorney}
          onChange={(value) => handleFilterChange('attorney', value)}
          data-testid="attorney-filter"
        />
        <Select
          label="Status"
          name="status"
          options={filterOptions.statusOptions}
          value={filters.status}
          onChange={(value) => handleFilterChange('status', value)}
          data-testid="status-filter"
        />
        <Select
          label="Office"
          name="office"
          options={filterOptions.officeOptions}
          value={filters.office}
          onChange={(value) => handleFilterChange('office', value)}
          data-testid="office-filter"
        />
        <TextField
          label="Search"
          name="search"
          value={filters.search}
          onChange={(event) => handleFilterChange('search', event.target.value)}
          data-testid="search-filter"
        />
        <Button onClick={() => setFilters({ staffClass: '', attorney: '', status: '', office: '', search: '' })} data-testid="clear-filters">
          Clear Filters
        </Button>
      </FilterContainer>
    );
  }

  function renderBulkActions() {
    if (selectedRates.length > 0) {
      return (
        <div>
          Bulk Actions ({selectedRates.length} selected):
          <Select
            label="Select Action"
            name="bulkAction"
            options={[
              { value: 'approve', label: 'Approve Selected' },
              { value: 'reject', label: 'Reject Selected' },
              { value: 'counter', label: 'Counter Propose Selected' },
            ]}
            onChange={(value) => { }}
            data-testid="bulk-action-select"
          />
          <TextField label="Value" name="bulkValue" />
          <Button onClick={() => applyBulkAction('approve', 100)} data-testid="apply-bulk-action">
            Apply
          </Button>
          <Button onClick={() => setSelectedRates([])} data-testid="cancel-bulk-action">
            Cancel
          </Button>
        </div>
      );
    } else {
      return null;
    }
  }
};

export default RateTable;