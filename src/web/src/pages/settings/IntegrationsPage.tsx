import React, { useState, useEffect, useCallback } from 'react'; // React library for building UI components //  ^18.2.0
import { useParams, useNavigate } from 'react-router-dom'; // Routing utilities //  ^6.4.0
import { useDispatch, useSelector } from 'react-redux'; // Redux hooks for accessing global state //  ^8.0.5
import MainLayout from '../../components/layout/MainLayout'; // Main layout wrapper component
import Tabs from '../../components/common/Tabs'; // Tab navigation component
import Button from '../../components/common/Button'; // Button component for user actions
import SearchBar from '../../components/common/SearchBar'; // Search component for filtering integrations
import Card from '../../components/common/Card'; // Card container component
import Modal from '../../components/common/Modal'; // Modal dialog component
import Spinner from '../../components/common/Spinner'; // Loading spinner component
import Alert from '../../components/common/Alert'; // Alert component for notifications and errors
import IntegrationTable from '../../components/tables/IntegrationTable'; // Table component for displaying integrations
import APIConfigurationPanel from '../../components/integration/APIConfigurationPanel'; // Panel for configuring API settings
import FieldMappingInterface from '../../components/integration/FieldMappingInterface'; // Interface for mapping fields between systems
import TestConnectionPanel from '../../components/integration/TestConnectionPanel'; // Panel for testing integration connections
import {
  selectIntegrations,
  selectLoading,
  selectError,
} from '../../store/integrations/integrationsSlice'; // Selector for integration state
import {
  fetchIntegrations,
  saveIntegration,
  testIntegration,
  deleteIntegration,
  testImport,
  testExport,
} from '../../store/integrations/integrationsThunks'; // Thunk for fetching integrations
import {
  Integration,
  IntegrationType,
  IntegrationStatus,
} from '../../types/integration'; // Type definition for integration data
import useFileUpload from '../../hooks/useFileUpload'; // Hook for handling file uploads
import usePermissions from '../../hooks/usePermissions'; // Hook for checking user permissions

/**
 * Main component for the Integrations page, allowing users to configure and manage external system integrations.
 */
const IntegrationsPage: React.FC = () => {
  // LD1: Initialize state for active tab, selected integration, search query, and modal visibility
  const [activeTab, setActiveTab] = useState<IntegrationType>(IntegrationType.EBILLING);
  const [selectedIntegration, setSelectedIntegration] = useState<Integration | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [isModalOpen, setIsModalOpen] = useState(false);

  // LD1: Get the 'type' parameter from the URL using useParams
  const { type } = useParams<{ type: IntegrationType }>();

  // LD1: Get navigation function for routing using useNavigate
  const navigate = useNavigate();

  // LD1: Check user permissions for managing integrations using usePermissions
  const { can } = usePermissions();

  // LD1: Fetch integrations data on component mount using Redux
  const dispatch = useDispatch();
  useEffect(() => {
    dispatch(fetchIntegrations());
  }, [dispatch]);

  // LD1: Select integrations, loading state, and error state from Redux store
  const integrations = useSelector(selectIntegrations);
  const loading = useSelector(selectLoading);
  const error = useSelector(selectError);

  /**
   * Handles tab switching between different integration types (eBilling, Law Firm, UniCourt)
   * @param {IntegrationType} tab - The integration type to switch to
   * @returns {void} No return value
   */
  const handleTabChange = (tab: IntegrationType) => {
    setActiveTab(tab);
    setSelectedIntegration(null);
    navigate(`/settings/integrations/${tab}`);
  };

  /**
   * Handles integration selection for detailed configuration
   * @param {Integration} integration - The integration to configure
   * @returns {void} No return value
   */
  const handleIntegrationSelect = (integration: Integration) => {
    setSelectedIntegration(integration);
  };

  /**
   * Handles searching/filtering integrations based on search query
   * @param {string} query - The search query to filter integrations
   * @returns {void} No return value
   */
  const handleSearch = (query: string) => {
    setSearchQuery(query);
  };

  /**
   * Handles adding new integrations
   * @returns {void} No return value
   */
  const handleAddIntegration = () => {
    setIsModalOpen(true);
  };

  /**
   * Handles saving integration configurations
   * @returns {void} No return value
   */
  const handleSaveConfiguration = () => {
    setSelectedIntegration(null);
  };

  /**
   * Handles testing integration connections
   * @param {Integration} integration - The integration to test
   * @returns {void} No return value
   */
  const handleTestConnection = (integration: Integration) => {
    dispatch(testIntegration(integration));
  };

  /**
   * Handles testing import/export functionality
   * @param {Integration} integration - The integration to test
   * @param {string} type - The type of test to perform (import/export)
   * @returns {void} No return value
   */
  const handleTestImportExport = (integration: Integration, type: string) => {
    if (type === 'import') {
      dispatch(testImport(integration));
    } else {
      dispatch(testExport(integration));
    }
  };

  /**
   * Handles deleting integrations with confirmation
   * @param {string} integrationId - The ID of the integration to delete
   * @returns {void} No return value
   */
  const handleDeleteIntegration = (integrationId: string) => {
    if (window.confirm('Are you sure you want to delete this integration?')) {
      dispatch(deleteIntegration(integrationId));
      setSelectedIntegration(null);
    }
  };

  // LD1: Hook for handling file uploads for non-API systems
  const {
    fileInputRef,
    file,
    fileError,
    isUploading,
    uploadProgress,
    uploadError,
    uploadResult,
    handleFileChange,
    handleFileDrop,
    uploadFile,
    cancelUpload,
    resetFileUpload,
  } = useFileUpload({
    acceptedFileTypes: ['.csv', '.xlsx', '.xls'],
    maxFileSizeMB: 10,
    endpoint: '/api/upload',
  });

  // LD1: Define tab items for the Tabs component
  const tabItems = [
    { id: IntegrationType.EBILLING, label: 'eBilling Systems' },
    { id: IntegrationType.LAWFIRM, label: 'Law Firm Systems' },
    { id: IntegrationType.UNICOURT, label: 'UniCourt' },
    { id: IntegrationType.FILE, label: 'File Import/Export' },
  ];

  // LD1: Render loading spinner when data is being fetched
  if (loading) {
    return (
      <MainLayout>
        <Spinner />
      </MainLayout>
    );
  }

  // LD1: Render error alert when API requests fail
  if (error) {
    return (
      <MainLayout>
        <Alert severity="error" message={error} />
      </MainLayout>
    );
  }

  // LD1: Render the page layout with tabs for different integration types
  return (
    <MainLayout>
      <Card>
        <Tabs
          tabs={tabItems}
          activeTab={activeTab}
          onChange={handleTabChange}
        />
        <CardContent>
          {/* LD1: Render search bar for filtering integrations */}
          <SearchBar placeholder="Search integrations" onSearch={handleSearch} />

          {/* LD1: Render the list of existing integrations in a table */}
          <IntegrationTable
            integrations={integrations.filter((i) => i.type === activeTab)}
            isLoading={loading}
            onConfigure={handleIntegrationSelect}
            onTest={handleTestConnection}
            onView={handleIntegrationSelect}
          />
        </CardContent>
      </Card>

      {/* LD1: Render the configuration panels for the selected integration */}
      {selectedIntegration && (
        <Card>
          <CardHeader title={`Configure ${selectedIntegration.name}`} />
          <CardContent>
            {/* TODO: Implement APIConfigurationPanel, FieldMappingInterface, and TestConnectionPanel components */}
            <APIConfigurationPanel
              initialConfig={selectedIntegration.configuration}
              integrationType={selectedIntegration.type}
              onConfigurationSaved={handleSaveConfiguration}
            />
            <FieldMappingInterface
              integrationId={selectedIntegration.id}
              integrationType={selectedIntegration.type}
              sourceFields={[]}
              targetFields={[]}
              onSave={handleSaveConfiguration}
              onCancel={() => setSelectedIntegration(null)}
            />
            <TestConnectionPanel
              integrationType={selectedIntegration.type}
              initialConfig={{
                type: selectedIntegration.type,
                configuration: selectedIntegration.configuration,
              }}
            />
          </CardContent>
        </Card>
      )}

      {/* LD1: Render modals for confirmation actions */}
      <Modal isOpen={isModalOpen} onClose={() => setIsModalOpen(false)}>
        {/* TODO: Implement modal content for adding new integrations */}
        <h2>Add New Integration</h2>
        <p>This feature is under development.</p>
      </Modal>

      {/* LD1: Render appropriate permissions messaging if user lacks required permissions */}
      {!can('read', 'integrations', 'organization') && (
        <Alert severity="warning" message="You do not have permission to view integrations." />
      )}
    </MainLayout>
  );
};

export default IntegrationsPage;