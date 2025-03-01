import React, { useState, useEffect, useMemo, useCallback } from 'react'; //  ^18.0.0
import { useNavigate, useSearchParams } from 'react-router-dom'; // ^6.4.0
import {
  Grid,
  Typography,
  Box,
  Dialog,
  IconButton,
} from '@mui/material'; // ^5.14.0
import { Add as AddIcon, Edit as EditIcon, Visibility as VisibilityIcon } from '@mui/icons-material'; // ^5.14.0
import { Attorney, AttorneySearchParams } from '../../../types/attorney';
import MainLayout from '../../../components/layout/MainLayout';
import Button from '../../../components/common/Button';
import SearchBar from '../../../components/common/SearchBar';
import Card from '../../../components/common/Card';
import Select from '../../../components/common/Select';
import AttorneyTable from '../../../components/tables/AttorneyTable';
import Pagination from '../../../components/common/Pagination';
import usePermissions from '../../../hooks/usePermissions';
import { ROUTES } from '../../../constants/routes';
import { getAttorneys } from '../../../services/attorneys';
import { useQuery } from '@tanstack/react-query'; //  ^4.0.0

/**
 * Main component function for the attorney list page
 * @returns {JSX.Element} Rendered attorney list page component
 */
const AttorneyListPage: React.FC = () => {
  // LD1: Initialize state for search query, filters, pagination, and selected attorneys
  const [searchQuery, setSearchQuery] = useState('');
  const [filters, setFilters] = useState<AttorneySearchParams>({});
  const [page, setPage] = useState(1);
  const [limit, setLimit] = useState(10);

  // LD1: Get URL search parameters using useSearchParams hook
  const [searchParams] = useSearchParams();

  // LD1: Get navigation function using useNavigate hook
  const navigate = useNavigate();

  // LD1: Check user permissions using usePermissions hook
  const { can } = usePermissions();

  // LD1: Fetch attorney data using useQuery hook from react-query with getAttorneys service
  const { isLoading, error, data } = useQuery(
    ['attorneys', page, limit, filters],
    () => getAttorneys({
      page,
      limit,
      filters,
    })
  );

  // LD1: Filter attorneys based on search query and selected filters
  const filteredAttorneys = useMemo(() => {
    if (!data?.items) return [];
    return data.items.filter((attorney) =>
      attorney.name.toLowerCase().includes(searchQuery.toLowerCase())
    );
  }, [data, searchQuery]);

  // LD1: Handle pagination of filtered attorneys
  const handlePageChange = (newPage: number) => {
    setPage(newPage);
  };

  const handleItemsPerPageChange = (newLimit: number) => {
    setLimit(newLimit);
    setPage(1);
  };

  // LD1: Handle add attorney button click by navigating to attorney form or opening modal
  const handleAddAttorney = () => {
    navigate('/attorneys/new');
  };

  // LD1: Handle view attorney details by navigating to attorney detail page
  const handleViewAttorney = (attorney: Attorney) => {
    navigate(`/attorneys/${attorney.id}`);
  };

  // LD1: Handle edit attorney by navigating to attorney form with attorney ID
  const handleEditAttorney = (attorney: Attorney) => {
    navigate(`/attorneys/${attorney.id}/edit`);
  };

  // LD1: Render MainLayout component with attorney list page content
  return (
    <MainLayout>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
        <Typography variant="h4" component="h1">
          Attorneys
        </Typography>
        {can('create', 'attorneys', 'organization') && (
          <Button variant="primary" onClick={handleAddAttorney}>
            <AddIcon />
            Add Attorney
          </Button>
        )}
      </Box>

      {/* LD1: Render filter section with search bar and dropdown filters */}
      <Box sx={{ display: 'flex', gap: 2, mb: 2 }}>
        <SearchBar
          placeholder="Search attorneys"
          value={searchQuery}
          onSearch={(value) => setSearchQuery(value)}
        />
      </Box>

      {/* LD1: Render AttorneyTable component with attorneys data and action handlers */}
      <AttorneyTable
        attorneys={filteredAttorneys}
        loading={isLoading}
        onRowAction={(action, attorney) => {
          if (action === 'view') {
            handleViewAttorney(attorney);
          } else if (action === 'edit') {
            handleEditAttorney(attorney);
          }
        }}
      />

      {/* LD1: Render Pagination component for navigating through pages */}
      {data && data.total && (
        <Pagination
          totalItems={data.total}
          itemsPerPage={limit}
          currentPage={page}
          onPageChange={handlePageChange}
          onItemsPerPageChange={handleItemsPerPageChange}
        />
      )}
    </MainLayout>
  );
};

export default AttorneyListPage;