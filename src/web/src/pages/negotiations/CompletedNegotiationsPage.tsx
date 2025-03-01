import React, { useState, useEffect, useMemo } from 'react'; //  ^18.0.0
import { useNavigate } from 'react-router-dom'; // ^6.4.0
import {
  Box,
  Card,
  Typography,
  IconButton,
  Tooltip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Stack
} from '@mui/material'; // ^5.14+
import { Visibility } from '@mui/icons-material'; // ^5.14+
import { useAuth } from '../../hooks/useAuth';
import { usePermissions } from '../../hooks/usePermissions';
import Button from '../../components/common/Button';
import PageHeader from '../../components/layout/PageHeader';
import NegotiationTable from '../../components/tables/NegotiationTable';
import NegotiationFilters from '../../components/negotiation/NegotiationFilters';
import EmptyState from '../../components/common/EmptyState';
import Spinner from '../../components/common/Spinner';
import Pagination from '../../components/common/Pagination';
import ExportControls from '../../components/analytics/ExportControls';
import { useNegotiations } from '../../hooks/useNegotiations';
import { Negotiation, FilterCriteria, PaginationState } from '../../types/negotiation';
import { NEGOTIATION_STATUS } from '../../constants/negotiations';
import { ROUTES } from '../../constants/routes';

/**
 * Component that displays a list of completed negotiations with filtering and pagination capabilities
 */
const CompletedNegotiationsPage: React.FC = () => {
  // LD1: Initialize loading state with useState(false)
  const [loading, setLoading] = useState<boolean>(false);
  // LD1: Initialize negotiations state with useState<Negotiation[]>([])
  const [negotiations, setNegotiations] = useState<Negotiation[]>([]);
  // LD1: Initialize filters state with useState<FilterCriteria>({ status: [], dateRange: null, firmId: null, clientId: null })
  const [filters, setFilters] = useState<FilterCriteria>({ status: [], dateRange: null, firmId: null, clientId: null });
  // LD1: Initialize pagination state with useState<PaginationState>({ page: 1, pageSize: 10, totalItems: 0 })
  const [pagination, setPagination] = useState<PaginationState>({ page: 1, pageSize: 10, totalItems: 0 });

  // LD1: Get user information and role using useAuth() hook
  const { user, isClient, isLawFirm } = useAuth();
  // LD1: Get permission checking function using usePermissions() hook
  const { hasPermission } = usePermissions();
  // LD1: Get negotiations functions using useNegotiations() hook
  const { getNegotiations, exportNegotiations } = useNegotiations();

  // LD1: Define completedStatuses constant using useMemo to include APPROVED, REJECTED, EXPORTED, EXPIRED statuses
  const completedStatuses = useMemo(() => [
    NEGOTIATION_STATUS.APPROVED,
    NEGOTIATION_STATUS.REJECTED,
    NEGOTIATION_STATUS.EXPORTED,
    NEGOTIATION_STATUS.EXPIRED,
  ], []);

  // LD1: Define fetchCompletedNegotiations function to fetch negotiations with filters including completedStatuses
  const fetchCompletedNegotiations = async () => {
    setLoading(true);
    try {
      // TODO: Implement API call to fetch completed negotiations with filters and pagination
      // const response = await getNegotiations({ ...filters, status: completedStatuses, page: pagination.page, pageSize: pagination.pageSize });
      // setNegotiations(response.data);
      // setPagination({ ...pagination, totalItems: response.total });
    } catch (error) {
      console.error('Failed to fetch completed negotiations:', error);
    } finally {
      setLoading(false);
    }
  };

  // LD1: Define handleFilterChange function to update filters state and reset pagination
  const handleFilterChange = (newFilters: FilterCriteria) => {
    setFilters(newFilters);
    setPagination({ ...pagination, page: 1 });
  };

  // LD1: Define handlePageChange function to update pagination state
  const handlePageChange = (newPage: number) => {
    setPagination({ ...pagination, page: newPage });
  };

  // LD1: Define handleExport function to export negotiations data in selected format
  const handleExport = async (format: string) => {
    try {
      // TODO: Implement API call to export negotiations data in selected format
      // await exportNegotiations(format, filters);
      console.log('Exporting negotiations in format:', format);
    } catch (error) {
      console.error('Failed to export negotiations:', error);
    }
  };

  // LD1: Define handleViewDetails function to navigate to negotiation detail page
  const navigate = useNavigate();
  const handleViewDetails = (negotiationId: string) => {
    navigate(`${ROUTES.NEGOTIATIONS}/${negotiationId}`);
  };

  // LD1: Use useEffect to call fetchCompletedNegotiations when component mounts or when filters/pagination change
  useEffect(() => {
    fetchCompletedNegotiations();
  }, [filters, pagination]);

  // LD1: Render PageHeader with 'Completed Negotiations' title and ExportControls component
  // LD1: Render NegotiationFilters component with filters prop and handleFilterChange callback
  // LD1: Render loading spinner when loading is true
  // LD1: Render EmptyState component when not loading and negotiations array is empty
  // LD1: Render Card containing NegotiationTable with negotiations data when not loading and has data
  // LD1: Configure NegotiationTable with onRowClick handler that calls handleViewDetails
  // LD1: Render Pagination component at the bottom of the table with current page state and handlePageChange callback
  return (
    <div>
      <PageHeader
        title="Completed Negotiations"
        actions={<ExportControls data={negotiations} title="Completed Negotiations" onExport={handleExport} isLoading={loading} />}
      />
      <NegotiationFilters filters={filters} onFilterChange={handleFilterChange} />
      {loading ? (
        <Spinner />
      ) : negotiations.length === 0 ? (
        <EmptyState title="No Completed Negotiations" message="There are no completed negotiations to display." />
      ) : (
        <Card>
          <NegotiationTable
            negotiations={negotiations}
            isLoading={loading}
            onRowClick={(negotiation) => handleViewDetails(negotiation.id)}
          />
          <Pagination
            totalItems={pagination.totalItems}
            itemsPerPage={pagination.pageSize}
            currentPage={pagination.page}
            onPageChange={handlePageChange}
          />
        </Card>
      )}
    </div>
  );
};

export default CompletedNegotiationsPage;