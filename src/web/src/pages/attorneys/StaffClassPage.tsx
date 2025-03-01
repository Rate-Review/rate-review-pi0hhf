import React, { useState, useEffect, useCallback } from 'react'; // ^18.2.0
import StaffClassTable from '../../components/tables/StaffClassTable';
import StaffClassForm from '../../components/forms/StaffClassForm';
import PageHeader from '../../components/layout/PageHeader';
import Button from '../../components/common/Button';
import Modal from '../../components/common/Modal';
import Card from '../../components/common/Card';
import useRates from '../../hooks/useRates';
import useOrganizations from '../../hooks/useOrganizations';
import { StaffClass } from '../../types/rate';
import { Add } from '@mui/icons-material'; // ^5.14.0
import { toast } from 'react-toastify'; // ^9.1.3

/**
 * Component for managing staff classes that categorize attorneys based on experience criteria
 */
const StaffClassPage: React.FC = () => {
  // LD1: Initialize state for staff classes, loading state, modal visibility, and form data
  const [staffClasses, setStaffClasses] = useState<StaffClass[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [selectedStaffClass, setSelectedStaffClass] = useState<StaffClass | null>(null);

  // LD1: Get organization context using useOrganizations hook
  const { currentOrganization } = useOrganizations();

  // LD1: Access staff class functionality from useRates hook
  const { loadRates } = useRates();

  // LD1: Implement useEffect to load staff classes when component mounts
  useEffect(() => {
    const loadStaffClasses = async () => {
      if (currentOrganization?.id) {
        setIsLoading(true);
        try {
          // TODO: Implement API call to fetch staff classes for the organization
          // const fetchedStaffClasses = await api.getStaffClasses(currentOrganization.id);
          // setStaffClasses(fetchedStaffClasses);
          console.log('Loading staff classes for organization:', currentOrganization.id);
        } catch (error: any) {
          toast.error(`Failed to load staff classes: ${error.message}`);
        } finally {
          setIsLoading(false);
        }
      }
    };

    loadStaffClasses();
  }, [currentOrganization, loadRates]);

  // LD1: Handle modal opening for create/edit operations
  const handleOpenModal = useCallback((staffClass?: StaffClass) => {
    setSelectedStaffClass(staffClass || null);
    setIsModalOpen(true);
  }, []);

  // LD1: Handle modal closing and form cancellation
  const handleCloseModal = useCallback(() => {
    setIsModalOpen(false);
    setSelectedStaffClass(null);
  }, []);

  // LD1: Implement staff class creation and updating
  const handleStaffClassSubmit = useCallback(async (formData: any) => {
    setIsLoading(true);
    try {
      if (selectedStaffClass) {
        // TODO: Implement API call to update staff class
        // await api.updateStaffClass(selectedStaffClass.id, formData);
        toast.success('Staff class updated successfully');
      } else {
        // TODO: Implement API call to create staff class
        // await api.createStaffClass(formData);
        toast.success('Staff class created successfully');
      }
      // Refresh staff classes after submission
      // await loadStaffClasses();
    } catch (error: any) {
      toast.error(`Failed to submit staff class: ${error.message}`);
    } finally {
      setIsLoading(false);
      handleCloseModal();
    }
  }, [selectedStaffClass, handleCloseModal, loadRates]);

  // LD1: Implement staff class deletion with confirmation
  const handleStaffClassDelete = useCallback(async (staffClassId: string) => {
    if (window.confirm('Are you sure you want to delete this staff class?')) {
      setIsLoading(true);
      try {
        // TODO: Implement API call to delete staff class
        // await api.deleteStaffClass(staffClassId);
        toast.success('Staff class deleted successfully');
        // Refresh staff classes after deletion
        // await loadStaffClasses();
      } catch (error: any) {
        toast.error(`Failed to delete staff class: ${error.message}`);
      } finally {
        setIsLoading(false);
      }
    }
  }, [loadRates]);

  // LD1: Render page header with title and add button
  // LD1: Render staff class table with data and action handlers
  // LD1: Render modal with staff class form for create/edit operations
  // LD1: Render confirmation dialog for deletion
  return (
    <Card>
      <PageHeader
        title="Staff Classes"
        actions={
          <Button variant="primary" onClick={() => handleOpenModal()}>
            <Add />
            Add Staff Class
          </Button>
        }
      />

      <StaffClassTable
        data={staffClasses}
        isLoading={isLoading}
        onEdit={handleOpenModal}
        onDelete={handleStaffClassDelete}
        emptyStateMessage="No staff classes have been created yet."
      />

      <Modal
        isOpen={isModalOpen}
        onClose={handleCloseModal}
        title={selectedStaffClass ? 'Edit Staff Class' : 'Create Staff Class'}
      >
        <StaffClassForm
          initialData={selectedStaffClass ? {
            id: selectedStaffClass.id,
            name: selectedStaffClass.name,
            experience_type: selectedStaffClass.experienceType,
            min_experience: selectedStaffClass.minExperience,
            max_experience: selectedStaffClass.maxExperience,
            practice_area: selectedStaffClass.practiceArea,
            geography: selectedStaffClass.geography,
            is_active: selectedStaffClass.isActive,
            organization_id: selectedStaffClass.organizationId,
          } : undefined}
          onSubmit={handleSubmitForm}
          onCancel={handleCloseModal}
        />
      </Modal>
    </Card>
  );
};

export default StaffClassPage;