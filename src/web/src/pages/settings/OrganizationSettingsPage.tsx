import React, { useState, useCallback, useEffect } from 'react'; // React core library v18.0+
import styled from 'styled-components'; // Styling library for component styling v5.3.9
import { toast } from 'react-toastify'; // Library for displaying toast notifications v9.1.1
import MainLayout from '../../components/layout/MainLayout'; // Main application layout component
import OrganizationForm from '../../components/forms/OrganizationForm'; // Form component for editing organization details
import { Card, CardHeader, CardContent } from '../../components/common/Card'; // Card components for sectioning content
import Button from '../../components/common/Button'; // Button component for actions
import { useOrganizationContext } from '../../context/OrganizationContext'; // Access organization context data and functions
import { usePermissions } from '../../hooks/usePermissions'; // Check user permissions for organization management actions
import { ACTIONS, RESOURCES, SCOPES } from '../../constants/permissions'; // Permission action constants
import ApprovalWorkflowForm from '../../components/forms/ApprovalWorkflowForm'; // Form component for approval workflow configuration
import PageHeader from '../../components/layout/PageHeader'; // Header component for the page title and actions
import Tabs from '../../components/common/Tabs'; // Tab navigation component for settings sections
import { Organization, OrganizationSettings } from '../../types/organization'; // Type definition for organization data

// LD1: Interface for tab options in the settings page
interface TabOption {
  id: string;
  label: string;
  icon?: React.ReactNode;
}

// LD1: Interface for modal state management
interface ModalState {
  isOpen: boolean;
  mode: 'create' | 'edit' | null;
  data?: any;
}

// LD1: Styled component for the main page container
const PageContainer = styled.div`
  max-width: 1200px;
  margin: 0 auto;
  padding: 16px;
`;

// LD1: Styled component for sectioning content
const SectionContainer = styled.div`
  margin-bottom: 24px;
`;

// LD1: Styled component for a grid layout of cards
const CardGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 16px;
  margin-top: 16px;

  @media (max-width: 768px) {
    grid-template-columns: 1fr;
  }
`;

// LD1: Styled component for action buttons
const ActionContainer = styled.div`
  display: flex;
  justify-content: flex-end;
  gap: 8px;
  margin-top: 16px;
`;

// LD1: Styled component for tab content
const TabContent = styled.div`
  padding: 16px 0;
`;

/**
 * Main page component for organization settings management
 */
const OrganizationSettingsPage: React.FC = () => {
  // LD1: Get organization data and functions from useOrganizationContext hook
  const { currentOrganization, updateOrganizationSettings, refreshOrganizationData } = useOrganizationContext();

  // LD1: Get permission checking function from usePermissions hook
  const { can } = usePermissions();

  // LD1: Initialize activeTab state to track the current settings tab
  const [activeTab, setActiveTab] = useState('details');

  // LD1: Initialize isEditing state to track form edit mode
  const [isEditing, setIsEditing] = useState(false);

  // LD1: Initialize modal states for different forms
  const [confirmDeleteModal, setConfirmDeleteModal] = useState<ModalState>({
    isOpen: false,
    mode: null,
    data: null,
  });

  // LD1: Create handler functions for form submissions
  const handleOrganizationUpdate = async (updatedData: Partial<Organization>) => {
    try {
      // Call API to update organization with new data
      // Show success toast notification on successful update
      toast.success('Organization updated successfully!');
      // Refresh organization data to reflect changes
      await refreshOrganizationData();
      // Set form back to view mode
      setIsEditing(false);
    } catch (error: any) {
      // Handle any errors with error toast notification
      toast.error(`Failed to update organization: ${error.message}`);
    }
  };

  const handleSettingsUpdate = async (updatedSettings: Partial<OrganizationSettings>) => {
    try {
      // Call updateOrganizationSettings with new settings data
      await updateOrganizationSettings(updatedSettings);
      // Show success toast notification
      toast.success('Organization settings updated successfully!');
      // Refresh organization data to reflect changes
      await refreshOrganizationData();
    } catch (error: any) {
      // Handle any errors with error toast notification
      toast.error(`Failed to update organization settings: ${error.message}`);
    }
  };

  // LD1: Create handler functions for tab changes
  const handleTabChange = (tabId: string) => {
    setActiveTab(tabId);
  };

  // LD1: Check user permissions for different organization management actions
  const canEditOrganization = can(ACTIONS.UPDATE, RESOURCES.ORGANIZATIONS, SCOPES.ORGANIZATION);
    
  // LD1: Define tab options based on organization type and permissions
  const tabOptions: TabOption[] = [
    { id: 'details', label: 'Organization Details' },
  ];

  // LD1: Render page with MainLayout wrapper
  return (
    <MainLayout>
      <PageContainer>
        {/* LD1: Display PageHeader with organization name and type */}
        <PageHeader
          title={`${currentOrganization?.name} (${currentOrganization?.type})`}
          actions={
            canEditOrganization && (
              <Button variant="primary" onClick={() => setIsEditing(true)}>
                Edit
              </Button>
            )
          }
        />

        {/* LD1: Render Tabs component for navigation between settings sections */}
        <Tabs
          tabs={tabOptions}
          activeTab={activeTab}
          onChange={handleTabChange}
        />

        {/* LD1: Render different content sections based on active tab */}
        <TabContent>
          {activeTab === 'details' && (
            <SectionContainer>
              <Card>
                <CardHeader title="Organization Details" />
                <CardContent>
                  {/* LD1: Organization Details tab: OrganizationForm in view or edit mode */}
                  <OrganizationForm
                    initialData={currentOrganization}
                    isEdit={isEditing}
                    onSuccess={() => setIsEditing(false)}
                    onCancel={() => setIsEditing(false)}
                  />
                </CardContent>
              </Card>
            </SectionContainer>
          )}
        </TabContent>
      </PageContainer>
    </MainLayout>
  );
};

// IE3: Be generous about your exports so long as it doesn't create a security risk.
export default OrganizationSettingsPage;