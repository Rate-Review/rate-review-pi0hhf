import React, { useState, useEffect, useCallback } from 'react'; // React library for building UI components // React v18.0+
import { useDispatch, useSelector } from 'react-redux'; // Redux hooks for accessing global state // react-redux v8.0.5

import PeerGroupTable from '../../../components/tables/PeerGroupTable'; // Table component for displaying peer groups with options to edit and delete
import PeerGroupForm from '../../../components/forms/PeerGroupForm'; // Form component for creating and editing peer groups with criteria selection
import Button from '../../../components/common/Button'; // Button component for user actions
import Modal from '../../../components/common/Modal'; // Modal component for forms and confirmations
import Card from '../../../components/common/Card'; // Card component for containing content sections
import Alert from '../../../components/common/Alert'; // Alert component for showing success/error messages
import ConfirmationDialog from '../../../components/common/ConfirmationDialog'; // Dialog for confirming delete actions
import PageHeader from '../../../components/layout/PageHeader'; // Header component with title and action buttons
import MainLayout from '../../../components/layout/MainLayout'; // Main layout wrapper for pages
import RecommendationCard from '../../../components/ai/RecommendationCard'; // Component for displaying AI-suggested peer groups
import { usePermissions } from '../../../hooks/usePermissions'; // Hook for checking user permissions
import { PeerGroup } from '../../../types/organization'; // Type definition for peer group data
import { fetchPeerGroups, createPeerGroup, updatePeerGroup, deletePeerGroup } from '../../../store/organizations/organizationsThunks'; // Redux thunk actions for peer group operations
import { selectPeerGroups, selectPeerGroupsLoading } from '../../../store/organizations/organizationsSlice'; // Redux selectors for peer group state
import Toast from '../../../components/common/Toast'; // Toast notification component for user feedback
import Spinner from '../../../components/common/Spinner'; // Loading indicator component

/**
 * Main component that renders the peer groups management page
 */
const PeerGroupsPage: React.FC = () => {
  // LD1: Initialize Redux hooks (useDispatch, useSelector)
  const dispatch = useDispatch();

  // LD1: Use selectors to get peer groups and loading state from Redux store
  const peerGroups = useSelector(selectPeerGroups);
  const loading = useSelector(selectPeerGroupsLoading);

  // LD1: Initialize local state for modal visibility, selected peer group, and delete confirmation
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [selectedPeerGroup, setSelectedPeerGroup] = useState<PeerGroup | null>(null);
  const [isDeleteConfirmationOpen, setIsDeleteConfirmationOpen] = useState(false);

  // LD1: Use useEffect to dispatch fetchPeerGroups action on component mount
  useEffect(() => {
    dispatch(fetchPeerGroups());
  }, [dispatch]);

  // LD1: Define handlers for creating, updating, and deleting peer groups
  const handleCreatePeerGroup = async (peerGroupData: PeerGroup) => {
    try {
      await dispatch(createPeerGroup(peerGroupData) as any).unwrap();
      setIsModalOpen(false);
      Toast.success('Peer group created successfully!');
    } catch (error: any) {
      Toast.error(`Failed to create peer group: ${error.message}`);
    }
  };

  const handleUpdatePeerGroup = async (peerGroupData: PeerGroup) => {
    if (!selectedPeerGroup?.id) {
      Toast.error('No peer group selected for update.');
      return;
    }
    try {
      await dispatch(updatePeerGroup({ id: selectedPeerGroup.id, ...peerGroupData }) as any).unwrap();
      setIsModalOpen(false);
      Toast.success('Peer group updated successfully!');
    } catch (error: any) {
      Toast.error(`Failed to update peer group: ${error.message}`);
    }
  };

  const handleDeletePeerGroup = async () => {
    if (!selectedPeerGroup?.id) {
      Toast.error('No peer group selected for deletion.');
      return;
    }
    try {
      await dispatch(deletePeerGroup(selectedPeerGroup.id)).unwrap();
      setIsDeleteConfirmationOpen(false);
      Toast.success('Peer group deleted successfully!');
    } catch (error: any) {
      Toast.error(`Failed to delete peer group: ${error.message}`);
    }
  };

  // LD1: Define handlers for opening and closing modals
  const handleOpenCreateModal = () => {
    setSelectedPeerGroup(null);
    setIsModalOpen(true);
  };

  const handleOpenEditModal = (peerGroup: PeerGroup) => {
    setSelectedPeerGroup(peerGroup);
    setIsModalOpen(true);
  };

  const handleCloseModal = () => {
    setSelectedPeerGroup(null);
    setIsModalOpen(false);
  };

  const handleOpenDeleteConfirmation = (peerGroup: PeerGroup) => {
    setSelectedPeerGroup(peerGroup);
    setIsDeleteConfirmationOpen(true);
  };

  const handleCloseDeleteConfirmation = () => {
    setIsDeleteConfirmationOpen(false);
  };

  // LD1: Check user permissions for creating and managing peer groups
  const { can } = usePermissions();
  const canCreate = can('create', 'peer_groups', 'organization');
  const canManage = can('update', 'peer_groups', 'organization') && can('delete', 'peer_groups', 'organization');

  // LD1: Render the main layout with page header, content card, and modals
  return (
    <MainLayout>
      <PageHeader
        title="Peer Groups"
        actions={
          canCreate && (
            <Button variant="primary" onClick={handleOpenCreateModal}>
              Create Peer Group
            </Button>
          )
        }
      />
      <Card>
        {loading ? (
          <Spinner />
        ) : (
          <PeerGroupTable
            peerGroups={peerGroups}
            onEdit={handleOpenEditModal}
            onDelete={handleOpenDeleteConfirmation}
            isLoading={loading}
            showFilters
          />
        )}
      </Card>

      {/* LD1: Conditionally render AI recommendation card for suggested peer groups */}
      {/* <RecommendationCard recommendation={} onApply={} onDismiss={} onViewExplanation={} /> */}

      {/* LD1: Render create/edit modal with form when open */}
      <Modal
        isOpen={isModalOpen}
        onClose={handleCloseModal}
        title={selectedPeerGroup ? 'Edit Peer Group' : 'Create Peer Group'}
      >
        <PeerGroupForm
          initialValues={selectedPeerGroup || { name: '', description: '', criteria: [], members: [] }}
          onSubmit={selectedPeerGroup ? handleUpdatePeerGroup : handleCreatePeerGroup}
          onCancel={handleCloseModal}
        />
      </Modal>

      {/* LD1: Render delete confirmation dialog when open */}
      <ConfirmationDialog
        isOpen={isDeleteConfirmationOpen}
        title="Delete Peer Group"
        message={`Are you sure you want to delete peer group "${selectedPeerGroup?.name}"?`}
        confirmText="Delete"
        cancelText="Cancel"
        confirmButtonVariant="danger"
        onConfirm={handleDeletePeerGroup}
        onCancel={handleCloseDeleteConfirmation}
      />
    </MainLayout>
  );
};

export default PeerGroupsPage;