import React, { useState, useEffect, FC } from 'react';
import { 
  Grid, 
  Select, 
  MenuItem, 
  TextField, 
  FormControl, 
  InputLabel, 
  Checkbox,
  FormControlLabel,
  Button
} from '@mui/material'; // v5.14+
import { DatePicker } from '@mui/x-date-pickers'; // v6.0+
import useDebounce from '../../hooks/useDebounce';
import { MessageFilter as MessageFilterType } from '../../types/message';

/**
 * Interface representing a negotiation option for the filter dropdown
 */
interface NegotiationOption {
  id: string;
  title: string;
}

/**
 * Interface representing an organization option for the filter dropdown
 */
interface OrganizationOption {
  id: string;
  name: string;
}

/**
 * Props for the MessageFilters component
 */
interface MessageFiltersProps {
  /** Current filter values */
  filters: MessageFilterType;
  /** Callback for when filters change */
  onFilterChange: (filters: MessageFilterType) => void;
  /** Available organizations to filter by */
  organizationOptions?: OrganizationOption[];
  /** Available negotiations to filter by */
  negotiationOptions?: NegotiationOption[];
  /** Whether to show the negotiation filter */
  showNegotiationFilter?: boolean;
  /** Whether to show the organization filter */
  showOrganizationFilter?: boolean;
  /** Whether to show the date filter */
  showDateFilter?: boolean;
  /** Whether to show the unread filter */
  showUnreadFilter?: boolean;
  /** Whether to show the search filter */
  showSearchFilter?: boolean;
}

/**
 * Component that provides filtering controls for messages in the Justice Bid Rate Negotiation System.
 * Allows users to filter messages by negotiation, organization, date range, content, and status.
 */
const MessageFilters: FC<MessageFiltersProps> = ({
  filters,
  onFilterChange,
  organizationOptions = [],
  negotiationOptions = [],
  showNegotiationFilter = true,
  showOrganizationFilter = true,
  showDateFilter = true,
  showUnreadFilter = true,
  showSearchFilter = true,
}) => {
  // Local state for search input (to be debounced)
  const [search, setSearch] = useState(filters.searchText || '');
  
  // Local state for date range (for DatePicker components)
  const [dateFrom, setDateFrom] = useState<Date | null>(
    filters.fromDate ? new Date(filters.fromDate) : null
  );
  const [dateTo, setDateTo] = useState<Date | null>(
    filters.toDate ? new Date(filters.toDate) : null
  );

  // Debounce search input to prevent excessive filter changes
  const debouncedSearch = useDebounce(search, 500);

  // Effect to update filters when debounced search changes
  useEffect(() => {
    if (debouncedSearch !== filters.searchText) {
      onFilterChange({
        ...filters,
        searchText: debouncedSearch || null
      });
    }
  }, [debouncedSearch, filters, onFilterChange]);

  /**
   * Handles changes to the negotiation filter dropdown
   */
  const handleNegotiationFilterChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const negotiationId = event.target.value;
    onFilterChange({
      ...filters,
      threadId: negotiationId === 'all' ? null : negotiationId
    });
  };

  /**
   * Handles changes to the organization filter dropdown
   */
  const handleOrganizationFilterChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const organizationId = event.target.value;
    onFilterChange({
      ...filters,
      senderId: organizationId === 'all' ? null : organizationId
    });
  };

  /**
   * Handles changes to the 'from date' filter
   */
  const handleDateFromChange = (date: Date | null) => {
    setDateFrom(date);
    onFilterChange({
      ...filters,
      fromDate: date ? date.toISOString() : null
    });
  };

  /**
   * Handles changes to the 'to date' filter
   */
  const handleDateToChange = (date: Date | null) => {
    setDateTo(date);
    onFilterChange({
      ...filters,
      toDate: date ? date.toISOString() : null
    });
  };

  /**
   * Handles changes to the search text filter with debounce
   */
  const handleSearchChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    setSearch(event.target.value);
    // The debounced effect will handle updating the filters
  };

  /**
   * Handles changes to the unread filter checkbox
   */
  const handleUnreadFilterChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    onFilterChange({
      ...filters,
      isRead: event.target.checked ? false : null
    });
  };

  /**
   * Clears all filters and resets to default state
   */
  const handleClearFilters = () => {
    setSearch('');
    setDateFrom(null);
    setDateTo(null);
    onFilterChange({
      threadId: null,
      parentId: null,
      senderId: null,
      isRead: null,
      relatedEntityType: null,
      relatedEntityId: null,
      fromDate: null,
      toDate: null,
      searchText: null
    });
  };

  return (
    <Grid container spacing={2} alignItems="center">
      {showNegotiationFilter && (
        <Grid item xs={12} sm={6} md={4} lg={3}>
          <FormControl fullWidth variant="outlined" size="small">
            <InputLabel id="negotiation-filter-label">Negotiation</InputLabel>
            <Select
              labelId="negotiation-filter-label"
              value={filters.threadId || 'all'}
              onChange={handleNegotiationFilterChange}
              label="Negotiation"
            >
              <MenuItem value="all">All Negotiations</MenuItem>
              {negotiationOptions.map((negotiation) => (
                <MenuItem key={negotiation.id} value={negotiation.id}>
                  {negotiation.title}
                </MenuItem>
              ))}
            </Select>
          </FormControl>
        </Grid>
      )}

      {showOrganizationFilter && (
        <Grid item xs={12} sm={6} md={4} lg={3}>
          <FormControl fullWidth variant="outlined" size="small">
            <InputLabel id="organization-filter-label">Organization</InputLabel>
            <Select
              labelId="organization-filter-label"
              value={filters.senderId || 'all'}
              onChange={handleOrganizationFilterChange}
              label="Organization"
            >
              <MenuItem value="all">All Organizations</MenuItem>
              {organizationOptions.map((org) => (
                <MenuItem key={org.id} value={org.id}>
                  {org.name}
                </MenuItem>
              ))}
            </Select>
          </FormControl>
        </Grid>
      )}

      {showDateFilter && (
        <>
          <Grid item xs={12} sm={6} md={4} lg={2}>
            <DatePicker
              label="From Date"
              value={dateFrom}
              onChange={handleDateFromChange}
              slotProps={{ 
                textField: { 
                  fullWidth: true, 
                  variant: 'outlined', 
                  size: 'small' 
                } 
              }}
            />
          </Grid>
          <Grid item xs={12} sm={6} md={4} lg={2}>
            <DatePicker
              label="To Date"
              value={dateTo}
              onChange={handleDateToChange}
              slotProps={{ 
                textField: { 
                  fullWidth: true, 
                  variant: 'outlined', 
                  size: 'small' 
                } 
              }}
            />
          </Grid>
        </>
      )}

      {showSearchFilter && (
        <Grid item xs={12} sm={6} md={4} lg={3}>
          <TextField
            fullWidth
            variant="outlined"
            size="small"
            label="Search"
            value={search}
            onChange={handleSearchChange}
            placeholder="Search message content..."
          />
        </Grid>
      )}

      {showUnreadFilter && (
        <Grid item xs={12} sm={6} md={4} lg={2}>
          <FormControlLabel
            control={
              <Checkbox
                checked={filters.isRead === false}
                onChange={handleUnreadFilterChange}
                color="primary"
              />
            }
            label="Unread Only"
          />
        </Grid>
      )}

      <Grid item xs={12} sm={6} md={4} lg={2}>
        <Button
          variant="outlined"
          onClick={handleClearFilters}
          fullWidth
          size="medium"
        >
          Clear Filters
        </Button>
      </Grid>
    </Grid>
  );
};

export default MessageFilters;