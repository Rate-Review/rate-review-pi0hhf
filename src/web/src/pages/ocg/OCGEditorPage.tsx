import React, { useState, useEffect, useCallback } from 'react'; // React core functionality for component creation and state management //  ^18.0.0
import { useParams, useNavigate } from 'react-router-dom'; // React Router hooks for URL parameter access and navigation //  ^6.0.0
import { toast } from 'react-toastify'; // Display notification messages after operations //  ^9.1.3
import MainLayout from '../../components/layout/MainLayout'; // Main application layout wrapper
import Breadcrumbs from '../../components/common/Breadcrumbs'; // Navigation breadcrumbs for the page
import OCGEditor from '../../components/ocg/OCGEditor'; // Main OCG editor component
import Button from '../../components/common/Button'; // Button component for save, preview, and publish actions
import ConfirmationDialog from '../../components/common/ConfirmationDialog'; // Dialog for confirming publish action
import { useOCG } from '../../hooks/useOCG'; // Custom hook for OCG operations
import { OCG, OCGSection, OCGAlternative } from '../../types/ocg'; // Type definition for OCG data
import useAIContext from '../../context/AIContext'; // Access AI capabilities for OCG editing assistance

/**
 * @function OCGEditorPage
 * @description Main component for OCG editor page that handles creating new OCGs or editing existing ones
 * @returns {JSX.Element} Rendered OCG editor page
 */
const OCGEditorPage: React.FC = () => {
  // LD1: Extract OCG ID from URL parameters if it exists
  const { id } = useParams<{ id: string }>();

  // LD1: Set up state for OCG data, loading state, and publish confirmation dialog
  const [ocg, setOcg] = useState<OCG | null>(null);
  const [loading, setLoading] = useState(false);
  const [isPublishDialogOpen, setIsPublishDialogOpen] = useState(false);

  // LD1: Use the useOCG hook to fetch, save, and publish OCGs
  const {
    getOCGById,
    createOCG,
    updateOCG,
    publishOCG,
    currentOCG,
    clearCurrentOCG,
  } = useOCG();

  // LD1: Use the useNavigate hook for navigation
  const navigate = useNavigate();

  // LD1: Use the useAIContext hook to access AI capabilities
  const { /* aiSuggestions, */ /* getAISuggestions */ } = useAIContext();

  // LD1: Fetch OCG data if in edit mode (ID exists)
  useEffect(() => {
    if (id) {
      setLoading(true);
      getOCGById(id)
        .then((fetchedOCG) => {
          setOcg(fetchedOCG);
        })
        .catch((error) => {
          toast.error(`Failed to load OCG: ${error.message}`);
        })
        .finally(() => {
          setLoading(false);
        });
    } else {
      // Initialize a new OCG object
      setOcg({
        id: '',
        title: 'New OCG',
        version: 1,
        status: 'Draft',
        clientId: '',
        client: { id: '', name: '', type: 'Client' },
        sections: [],
        totalPoints: 100,
        createdAt: new Date(),
        updatedAt: new Date(),
      });
    }

    return () => {
      clearCurrentOCG();
    };
  }, [id, getOCGById, clearCurrentOCG]);

  // LD1: Handle form state changes from the OCG editor component
  const handleOCGChange = (updatedOCG: OCG) => {
    setOcg(updatedOCG);
  };

  // LD1: Implement save, preview, and publish functions
  const handleSave = async (ocgToSave: OCG) => {
    setLoading(true);
    try {
      if (ocgId) {
        // Update existing OCG
        await updateOCG(ocgId, ocgToSave);
        toast.success('OCG updated successfully');
      } else {
        // Create new OCG
        await createOCG(ocgToSave);
        toast.success('OCG created successfully');
      }
    } catch (error: any) {
      toast.error(`Failed to save OCG: ${error.message}`);
    } finally {
      setLoading(false);
    }
  };

  const handlePreview = () => {
    // TODO: Implement preview functionality
    console.log('Preview OCG');
  };

  const handlePublish = async () => {
    if (ocg?.id) {
      setLoading(true);
      try {
        await publishOCG(ocg.id);
        toast.success('OCG published successfully');
      } catch (error: any) {
        toast.error(`Failed to publish OCG: ${error.message}`);
      } finally {
        setLoading(false);
        setIsPublishDialogOpen(false);
      }
    }
  };

  const handleCancel = () => {
    navigate('/ocg/list');
  };

  // LD1: Render the page layout with breadcrumbs, title, and OCG editor
  return (
    <MainLayout>
      <Breadcrumbs routes={[{ path: '/ocg/list', label: 'OCGs' }, { path: '', label: 'OCG Editor' }]} />
      <h2>{id ? 'Edit OCG' : 'Create OCG'}</h2>
      <OCGEditor
        ocgId={id}
        initialData={ocg}
        isLoading={loading}
        onSaveDraft={handleSave}
        onPublish={() => setIsPublishDialogOpen(true)}
        onCancel={handleCancel}
      />

      {/* LD1: Include action buttons for save, preview, and publish */}
      <div>
        <Button onClick={handleSave} disabled={loading}>
          Save Draft
        </Button>
        <Button onClick={handlePreview} disabled={loading}>
          Preview
        </Button>
        <Button onClick={() => setIsPublishDialogOpen(true)} disabled={loading}>
          Publish
        </Button>
        <Button onClick={handleCancel} disabled={loading}>
          Cancel
        </Button>
      </div>

      {/* LD1: Include confirmation dialog for publishing */}
      <ConfirmationDialog
        isOpen={isPublishDialogOpen}
        title="Publish OCG"
        message="Are you sure you want to publish this OCG? This action cannot be undone."
        onConfirm={handlePublish}
        onCancel={() => setIsPublishDialogOpen(false)}
      />
    </MainLayout>
  );
};

// IE3: Be generous about your exports so long as it doesn't create a security risk.
export default OCGEditorPage;