import React, { useState, useEffect, useCallback } from 'react'; // React v18.0+
import { useNavigate } from 'react-router-dom'; // React Router v6.10.0
import { Box, Card, CardContent, Container, Typography, CircularProgress, Alert } from '@mui/material'; // Material UI v5.11.0+

import PageHeader from '../../components/layout/PageHeader';
import NegotiationTable from '../../components/tables/NegotiationTable';
import NegotiationFilters from '../../components/negotiation/NegotiationFilters';
import Button from '../../components/common/Button';
import useNegotiations from '../../hooks/useNegotiations';
import { usePermissions } from '../../hooks/usePermissions';
import { Negotiation, NegotiationStatus, NegotiationFilters as NegotiationFiltersType } from '../../types/negotiation';
import { useAppDispatch, useAppSelector } from '../../store';
import { fetchNegotiations, selectActiveNegotiations, selectNegotiationLoading, selectNegotiationError, setNegotiationFilters } from '../../store/negotiations/negotiationsSlice';
import { useOrganizationContext } from '../../context/OrganizationContext';

/**
 * Returns the appropriate page title based on organization type
 * @param   {string} organizationType - Organization type
 * @returns {string} Page title string
 */
const getPageTitle = (organizationType: string): string => {
  if (organizationType === 'LAW_FIRM') {
    return 'Active Client Negotiations';
  } else if (organizationType === 'CLIENT') {
    return 'Active Law Firm Negotiations';
  } else {
    return 'Active Negotiations';
  }
};

/**
 * React functional component that displays a list of active negotiations
 * @returns Rendered component with negotiations list and filters
 */
export const ActiveNegotiationsPage: React.FC = () => {
  // LD1: Initialize state for filter visibility (showFilters)
  const [showFilters, setShowFilters] = useState(false);

  // LD1: Access Redux store with useAppDispatch and useAppSelector
  const dispatch = useAppDispatch();

  // LD1: Get current organization info with useOrganizationContext
  const { currentOrganization } = useOrganizationContext();

  // LD1: Get negotiation-related data and functions from useNegotiations hook
  const { negotiations, negotiationLoading, negotiationError, fetchNegotiations: fetchNegotiationsData } = useNegotiations({ fetchOnMount: false });

  // LD1: Get permissions with usePermissions hook
  const { can } = usePermissions();

  // LD1: Get navigation function from useNavigate
  const navigate = useNavigate();

  // LD1: Select active negotiations, loading and error state from Redux
  const activeNegotiations = useAppSelector(selectActiveNegotiations);
  const loading = useAppSelector(selectNegotiationLoading);
  const error = useAppSelector(selectNegotiationError);

  // LD1: Define default filters for active negotiations (status IN_PROGRESS or REQUESTED)
  const defaultFilters: NegotiationFiltersType = {
    status: [NegotiationStatus.IN_PROGRESS, NegotiationStatus.REQUESTED],
    type: [],
    clientId: '',
    firmId: '',
    startDate: '',
    endDate: '',
    search: '',
    sortBy: '',
    sortDirection: '',
    page: 1,
    pageSize: 10,
  };

  // LD1: Define handleFilterChange function to update filters and load negotiations
  const handleFilterChange = useCallback((newFilters: NegotiationFiltersType) => {
    dispatch(setNegotiationFilters(newFilters));
    fetchNegotiationsData(newFilters);
  }, [dispatch, fetchNegotiationsData]);

  // LD1: Define handleNavigateToDetail function to navigate to negotiation details
  const handleNavigateToDetail = useCallback((negotiation: Negotiation) => {
    navigate(`/negotiations/${negotiation.id}`);
  }, [navigate]);

  // LD1: Define handleCreateNegotiation function to navigate to negotiation creation
  const handleCreateNegotiation = useCallback(() => {
    navigate('/negotiations/new');
  }, [navigate]);

  // LD1: Define toggleFilters function to show/hide filters section
  const toggleFilters = useCallback(() => {
    setShowFilters((prevShowFilters) => !prevShowFilters);
  }, []);

  // LD1: Use useEffect to load negotiations when component mounts
  useEffect(() => {
    fetchNegotiationsData(defaultFilters);
  }, [fetchNegotiationsData, defaultFilters]);

  // LD1: Define refreshNegotiations function to reload data
  const refreshNegotiations = useCallback(() => {
    fetchNegotiationsData(defaultFilters);
  }, [fetchNegotiationsData, defaultFilters]);

  // LD1: Define pageActions to include Create Negotiation button if user has permission
  const pageActions = can('create', 'negotiations', 'organization') ? (
    <Button variant="primary" onClick={handleCreateNegotiation}>
      Create Negotiation
    </Button>
  ) : null;

  // LD1: Return JSX with PageHeader, filters section (if visible), and NegotiationTable
  return (
    <Container maxWidth="xl">
      <PageHeader title={getPageTitle(currentOrganization?.type || '')} actions={pageActions} />

      {showFilters && (
        <Card sx={{ mb: 2 }}>
          <CardContent>
            <NegotiationFilters onFilterChange={handleFilterChange} />
          </CardContent>
        </Card>
      )}

      {loading ? (
        <Box display="flex" justifyContent="center">
          <CircularProgress />
        </Box>
      ) : error ? (
        <Alert severity="error">{error}</Alert>
      ) : negotiations.length === 0 ? (
        <Typography variant="body1">No active negotiations found.</Typography>
      ) : (
        <NegotiationTable
          negotiations={negotiations}
          isLoading={loading}
          error={error}
          onNegotiationSelect={handleNavigateToDetail}
        />
      )}
    </Container>
  );
};