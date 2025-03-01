import React, { useState, useEffect, useMemo, useCallback } from 'react'; //  ^18.0.0
import styled from 'styled-components';
import StatusIndicator from '../common/StatusIndicator';
import Button from '../common/Button';
import SearchBar from '../common/SearchBar';
import Pagination from '../common/Pagination';
import EmptyState from '../common/EmptyState';
import Spinner from '../common/Spinner';
import { Settings, Refresh, Visibility } from '@mui/icons-material'; //  ^5.14.0
import { usePermissions } from '../../hooks/usePermissions';
import { formatDate } from '../../utils/date';
import { IntegrationType, IntegrationConfig } from '../../types/integration';

/**
 * Interface defining the props for the IntegrationTable component
 */
interface IntegrationTableProps {
  /** Array of integration configurations to display */
  integrations: IntegrationConfig[];
  /** Boolean indicating if the data is still loading */
  isLoading: boolean;
  /** Callback function for configuring an integration */
  onConfigure: (integration: IntegrationConfig) => void;
  /** Callback function for testing an integration */
  onTest: (integration: IntegrationConfig) => void;
  /** Callback function for viewing integration details */
  onView: (integration: IntegrationConfig) => void;
}

/**
 * Returns a user-friendly display name for integration type
 * @param type - IntegrationType enum value
 * @returns Human-readable integration type name
 */
const getIntegrationTypeDisplay = (type: IntegrationType): string => {
  switch (type) {
    case IntegrationType.EBILLING:
      return 'eBilling System';
    case IntegrationType.LAWFIRM:
      return 'Law Firm System';
    case IntegrationType.UNICOURT:
      return 'UniCourt';
    case IntegrationType.FILE:
      return 'File Import/Export';
    default:
      return type;
  }
};

/**
 * Gets color and display text for integration status
 * @param status - Integration status string
 * @returns Object containing color and display text
 */
const getStatusColorAndText = (status: string): { color: string; text: string } => {
  switch (status) {
    case 'active':
      return { color: 'success', text: 'Active' };
    case 'configured':
      return { color: 'warning', text: 'Configured' };
    case 'error':
      return { color: 'error', text: 'Error' };
    default:
      return { color: 'neutral', text: 'Not Configured' };
  }
};

/**
 * Filters integrations based on search query
 * @param integrations - Array of IntegrationConfig objects
 * @param query - Search query string
 * @returns Filtered array of integrations
 */
const filterIntegrations = (integrations: IntegrationConfig[], query: string): IntegrationConfig[] => {
  if (!query) {
    return integrations;
  }

  const lowerQuery = query.toLowerCase();
  return integrations.filter(integration =>
    integration.name.toLowerCase().includes(lowerQuery) ||
    getIntegrationTypeDisplay(integration.type).toLowerCase().includes(lowerQuery) ||
    integration.status.toLowerCase().includes(lowerQuery)
  );
};

/**
 * Handles pagination page changes
 * @param page - New page number
 */
interface HandlePageChangeSignature {
  (page: number): void;
}

/**
 * Handles search input changes
 */
interface HandleSearchSignature {
  (query: string): void;
}

/**
 * The main component function that renders the integration table
 */
interface IntegrationTableProps {
  integrations: IntegrationConfig[];
  isLoading: boolean;
  onConfigure: (integration: IntegrationConfig) => void;
  onTest: (integration: IntegrationConfig) => void;
  onView: (integration: IntegrationConfig) => void;
}

const IntegrationTable: React.FC<IntegrationTableProps> = ({
  integrations,
  isLoading,
  onConfigure,
  onTest,
  onView,
}) => {
  // Initialize state for current page, search query, and items per page
  const [currentPage, setCurrentPage] = useState(1);
  const [searchQuery, setSearchQuery] = useState('');
  const [itemsPerPage, setItemsPerPage] = useState(10);

  // Check user permissions for integration management using usePermissions hook
  const { can } = usePermissions();

  // Filter integrations based on search query using useMemo for performance
  const filteredIntegrations = useMemo(() => filterIntegrations(integrations, searchQuery), [integrations, searchQuery]);

  // Calculate paginated subset of integrations based on current page and items per page
  const paginatedIntegrations = useMemo(() => {
    const startIndex = (currentPage - 1) * itemsPerPage;
    const endIndex = startIndex + itemsPerPage;
    return filteredIntegrations.slice(startIndex, endIndex);
  }, [currentPage, itemsPerPage, filteredIntegrations]);

  // Calculate total pages based on filtered integrations and items per page
  const totalPages = Math.ceil(filteredIntegrations.length / itemsPerPage);

  // Handles pagination page changes
  const handlePageChange: HandlePageChangeSignature = useCallback((page: number) => {
    setCurrentPage(page);
  }, []);

  // Handles search input changes
  const handleSearch: HandleSearchSignature = useCallback((query: string) => {
    setSearchQuery(query);
    setCurrentPage(1);
  }, []);

  return (
    <div>
      {/* Render search bar for filtering integrations */}
      <SearchBar placeholder="Search integrations" onSearch={handleSearch} />

      {/* Render loading spinner when isLoading is true */}
      {isLoading ? (
        <Spinner size="48px" />
      ) : filteredIntegrations.length === 0 ? (
        /* Render empty state when no integrations match filter */
        <EmptyState title="No Integrations Found" message="No integrations match your search criteria." icon={<Settings />} />
      ) : (
        /* Render table with headers for Name, Type, Status, Last Sync, and Actions */
        <table style={{ width: '100%', borderCollapse: 'collapse' }}>
          <thead>
            <tr style={{ borderBottom: '1px solid #ddd', textAlign: 'left' }}>
              <th style={{ padding: '8px' }}>Name</th>
              <th style={{ padding: '8px' }}>Type</th>
              <th style={{ padding: '8px' }}>Status</th>
              <th style={{ padding: '8px' }}>Last Sync</th>
              <th style={{ padding: '8px' }}>Actions</th>
            </tr>
          </thead>
          <tbody>
            {/* Render integration rows with appropriate status indicators and action buttons */}
            {paginatedIntegrations.map(integration => {
              const { color: statusColor, text: statusText } = getStatusColorAndText(integration.status);
              return (
                <tr key={integration.id} style={{ borderBottom: '1px solid #ddd' }}>
                  <td style={{ padding: '8px' }}>{integration.name}</td>
                  <td style={{ padding: '8px' }}>{getIntegrationTypeDisplay(integration.type)}</td>
                  <td style={{ padding: '8px' }}>
                    <StatusIndicator status={statusText} statusColorMap={{ [statusText]: statusColor }} />
                  </td>
                  <td style={{ padding: '8px' }}>{integration.lastSyncDate ? formatDate(integration.lastSyncDate) : 'Never'}</td>
                  <td style={{ padding: '8px' }}>
                    {/* Action buttons: Configure, Test, View */}
                    {can('update', 'integrations', 'organization') && (
                      <Button variant="text" size="small" onClick={() => onConfigure(integration)} aria-label={`Configure ${integration.name}`}>
                        <Settings style={{ marginRight: '4px' }} />
                        Configure
                      </Button>
                    )}
                    {can('read', 'integrations', 'organization') && (
                      <Button variant="text" size="small" onClick={() => onTest(integration)} aria-label={`Test ${integration.name}`}>
                        <Refresh style={{ marginRight: '4px' }} />
                        Test
                      </Button>
                    )}
                    <Button variant="text" size="small" onClick={() => onView(integration)} aria-label={`View ${integration.name}`}>
                      <Visibility style={{ marginRight: '4px' }} />
                      View
                    </Button>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      )}

      {/* Render pagination controls if total pages > 1 */}
      {totalPages > 1 && (
        <Pagination
          totalItems={filteredIntegrations.length}
          itemsPerPage={itemsPerPage}
          currentPage={currentPage}
          onPageChange={handlePageChange}
        />
      )}
    </div>
  );
};

export default IntegrationTable;