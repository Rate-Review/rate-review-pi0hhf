import React, { useState, useEffect, useCallback, useMemo } from 'react'; // React v18.0+
import { Button } from '../common/Button';
import { Select } from '../common/Select';
import { TextField } from '../common/TextField';
import { DatePicker } from '../common/DatePicker';
import { NEGOTIATION_STATUS } from '../../constants/negotiations';
import { useOrganizationContext } from '../../context/OrganizationContext';
import { useDebounce } from '../../hooks/useDebounce';
import { useWindowSize } from '../../hooks/useWindowSize';
import { NegotiationFilters as NegotiationFiltersType } from '../../types/negotiation';
import { OrganizationType } from '../../types/organization';
import { getOrganizations } from '../../services/organizations';
import { useAppDispatch, useAppSelector } from '../../store';
import { setNegotiationFilters, selectNegotiationFilters } from '../../store/negotiations/negotiationsSlice';

/**
 * A React functional component that renders a set of filter controls for negotiation data.
 * @param {object} props - Component props
 * @returns {JSX.Element} The rendered component
 */
export const NegotiationFilters: React.FC<{ onFilterChange?: (filters: NegotiationFiltersType) => void; compact?: boolean }> = ({ onFilterChange, compact }) => {
  // Define default filters based on current date (last 30 days) and empty status/search
  const defaultFilters = useMemo(() => ({
    status: [],
    type: [],
    clientId: '',
    firmId: '',
    startDate: new Date(new Date().setDate(new Date().getDate() - 30)).toISOString().split('T')[0],
    endDate: new Date().toISOString().split('T')[0],
    search: '',
    sortBy: '',
    sortDirection: '',
    page: 1,
    pageSize: 10
  }), []);

  // Initialize state for filters with default values or initialFilters prop
  const [filters, setFilters] = useState<NegotiationFiltersType>(defaultFilters);

  // Extract current organization context using useOrganizationContext hook
  const { currentOrganization, organizations, getOrganizationsByType } = useOrganizationContext();

  // Set up Redux store connection using useAppSelector and useAppDispatch
  const reduxFilters = useAppSelector(selectNegotiationFilters);
  const dispatch = useAppDispatch();

  // Get current window size for responsive layout adjustments
  const { width } = useWindowSize();

  // Initialize state for organizations list and loading state
  const [organizationOptions, setOrganizationOptions] = useState([]);
  const [loadingOrganizations, setLoadingOrganizations] = useState(false);

  // Use useDebounce hook to create debounced version of search term
  const debouncedSearchTerm = useDebounce(filters.search, 300);

  // Set up effect to load organizations list on component mount
  useEffect(() => {
    const loadOrganizations = async () => {
      setLoadingOrganizations(true);
      try {
        let orgs;
        if (currentOrganization?.type === OrganizationType.Client) {
          orgs = await getOrganizationsByType(OrganizationType.LawFirm);
        } else {
          orgs = await getOrganizationsByType(OrganizationType.Client);
        }
        setOrganizationOptions(orgs.map(org => ({ value: org.id, label: org.name })));
      } catch (error) {
        console.error("Failed to load organizations:", error);
      } finally {
        setLoadingOrganizations(false);
      }
    };

    loadOrganizations();
  }, [currentOrganization, getOrganizationsByType]);

  // Set up effect to sync filters with Redux store when changed
  useEffect(() => {
    dispatch(setNegotiationFilters(filters));
    onFilterChange?.(filters);
  }, [filters, dispatch, onFilterChange]);

  /**
   * Updates a single filter field in the state
   * @param {string} field - The name of the filter field to update
   * @param {any} value - The new value for the filter field
   * @returns {void} No return value
   */
  const handleFilterChange = (field: string, value: any) => {
    setFilters(prevFilters => ({
      ...prevFilters,
      [field]: value,
    }));
  };

  /**
   * Applies the current filters and notifies parent component
   * @returns {void} No return value
   */
  const handleApplyFilters = () => {
    dispatch(setNegotiationFilters(filters));
    onFilterChange?.(filters);
  };

  /**
   * Resets all filters to default values
   * @returns {void} No return value
   */
  const handleResetFilters = () => {
    setFilters(defaultFilters);
    dispatch(setNegotiationFilters(defaultFilters));
    onFilterChange?.(defaultFilters);
  };

  // Create memoized status options from NEGOTIATION_STATUS enum
  const statusOptions = useMemo(() => {
    return Object.entries(NEGOTIATION_STATUS).map(([key, value]) => ({
      value: value,
      label: key.replace(/_/g, ' '),
    }));
  }, []);

  // Create memoized organization label based on user organization type
  const organizationLabel = useMemo(() => {
    return currentOrganization?.type === OrganizationType.Client ? 'Law Firm' : 'Client';
  }, [currentOrganization]);

  // Determine layout class based on compact prop and window size
  const layoutClass = compact || width < 768 ? 'flex' : 'grid';

  return (
    <div>
      <form className={`${layoutClass === 'grid' ? 'grid grid-cols-1 md:grid-cols-3 gap-4' : 'flex flex-col gap-2'}`}>
        <Select
          label="Status"
          name="status"
          multiple
          options={statusOptions}
          value={filters.status}
          onChange={(value) => handleFilterChange('status', value)}
        />
        {currentOrganization?.type && (
          <Select
            label={organizationLabel}
            name={currentOrganization.type === OrganizationType.Client ? 'firmId' : 'clientId'}
            options={organizationOptions}
            value={filters.firmId || filters.clientId}
            onChange={(value) => handleFilterChange(currentOrganization.type === OrganizationType.Client ? 'firmId' : 'clientId', value)}
            disabled={loadingOrganizations}
          />
        )}
        <DatePicker
          label="Start Date"
          name="startDate"
          value={filters.startDate}
          onChange={(value) => handleFilterChange('startDate', value)}
        />
        <DatePicker
          label="End Date"
          name="endDate"
          value={filters.endDate}
          onChange={(value) => handleFilterChange('endDate', value)}
        />
        <TextField
          label="Search"
          name="search"
          placeholder="Search negotiations"
          value={filters.search}
          onChange={(e) => handleFilterChange('search', e.target.value)}
        />
      </form>
      <div className="mt-4 flex justify-end gap-2">
        <Button variant="primary" onClick={handleApplyFilters}>
          Apply Filters
        </Button>
        {Object.keys(filters).some(key => filters[key]) && (
          <Button variant="text" onClick={handleResetFilters}>
            Reset Filters
          </Button>
        )}
      </div>
    </div>
  );
};