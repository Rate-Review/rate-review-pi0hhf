import React, { useState, useEffect, useCallback } from 'react'; // React library for building UI components //  ^18.2.0
import { useParams, useNavigate } from 'react-router-dom'; // React Router hooks for navigation and URL parameters //  ^6.14.0
import { useDispatch, useSelector } from 'react-redux'; // Redux hooks for accessing and updating store state //  ^8.1.0
import {
  Box,
  Typography,
  Grid,
  Paper,
  Divider,
  IconButton,
  Tooltip,
  Skeleton,
  Chip,
  Alert,
} from '@mui/material'; // Material UI components for layout and display //  ^5.14.0
import {
  Edit,
  Delete,
  Share,
  PlayArrow,
  Download,
  Description,
  VisibilityOutlined,
  VerifiedUser,
  ArrowBack,
} from '@mui/icons-material'; // Material UI icons for action buttons //  ^5.14.0
import { format } from 'date-fns'; // Date formatting utility //  ^2.30.0

import MainLayout from '../../components/layout/MainLayout'; // Main layout component for consistent page layout
import Button from '../../components/common/Button'; // Common button component for actions
import StatusIndicator from '../../components/common/StatusIndicator'; // Component to display status indicators
import OCGSectionView from '../../components/ocg/OCGSectionView'; // Component to display OCG sections
import OCGPointBudget from '../../components/ocg/OCGPointBudget'; // Component to display OCG point budget
import usePermissions from '../../hooks/usePermissions'; // Custom hook for checking user permissions
import useOCG from '../../hooks/useOCG'; // Custom hook for OCG operations
import { RootState } from '../../store'; // Type definition for the Redux root state
import { fetchOCGDetail, startOCGNegotiation, deleteOCG } from '../../store/ocg/ocgSlice'; // Redux actions for OCG operations
import Breadcrumbs from '../../components/common/Breadcrumbs'; // Breadcrumbs navigation component
import ConfirmationDialog from '../../components/common/ConfirmationDialog'; // Dialog component for confirming actions
import Card from '../../components/common/Card'; // Card component for content sections
import EmptyState from '../../components/common/EmptyState'; // Component to display when no data is available
import { ROUTES } from '../../constants/routes'; // Route constants for navigation

/**
 * A page component that displays detailed information about a specific Outside Counsel Guidelines document,
 * including its sections, negotiation status, and actions available based on user permissions.
 */
const OCGDetailPage: React.FC = () => {
  // LD1: Extract OCG ID from URL parameters using useParams hook
  const { id } = useParams<{ id: string }>();

  // LD1: Get navigate function from useNavigate hook
  const navigate = useNavigate();

  // LD1: Get dispatch function from useDispatch hook
  const dispatch = useDispatch();

  // LD1: Get OCG data and loading state from Redux store using useSelector
  const ocg = useSelector((state: RootState) => state.ocg.currentOCG);
  const loading = useSelector((state: RootState) => state.ocg.loading.detail);

  // LD1: Initialize state for delete confirmation dialog
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);

  // LD1: Use the useOCG hook to access OCG-related functions
  const { canEdit, canDelete, canNegotiate } = useOCG();

  // LD1: Use the usePermissions hook to check user permissions
  const { can } = usePermissions();

  // LD1: Fetch OCG data when component mounts using useEffect hook
  useEffect(() => {
    if (id) {
      dispatch(fetchOCGDetail(id));
    }
  }, [id, dispatch]);

  // LD1: Handler function to navigate to the OCG editor page
  const handleEditOCG = () => {
    navigate(`${ROUTES.OCG_EDITOR}/${id}`);
  };

  // LD1: Handler function to show delete confirmation dialog
  const handleDeleteOCG = () => {
    setDeleteDialogOpen(true);
  };

  // LD1: Handler function to confirm OCG deletion
  const confirmDeleteOCG = () => {
    if (id) {
      dispatch(deleteOCG(id));
      setDeleteDialogOpen(false);
      navigate(ROUTES.OCG_LIST);
    }
  };

  // LD1: Handler function to share the OCG
  const handleShareOCG = () => {
    // TODO: Implement share functionality (e.g., generate shareable link or open share dialog)
    console.log('Share OCG');
  };

  // LD1: Handler function to start OCG negotiation
  const handleStartNegotiation = () => {
    // TODO: Implement start negotiation functionality
    console.log('Start OCG Negotiation');
  };

  // LD1: Handler function to download OCG as PDF
  const handleDownloadOCG = () => {
    // TODO: Implement download OCG as PDF functionality
    console.log('Download OCG as PDF');
  };

  // LD1: Function to render action buttons based on user permissions and OCG status
  const renderActionButtons = () => {
    if (!ocg) return null;

    return (
      <Box display="flex" gap={2}>
        {canEdit && (
          <Button variant="outlined" startIcon={<Edit />} onClick={handleEditOCG}>
            Edit
          </Button>
        )}
        {canDelete && (
          <Button variant="outlined" color="error" startIcon={<Delete />} onClick={handleDeleteOCG}>
            Delete
          </Button>
        )}
        <Button variant="outlined" startIcon={<Share />} onClick={handleShareOCG}>
          Share
        </Button>
        {canNegotiate && (
          <Button variant="contained" startIcon={<PlayArrow />} onClick={handleStartNegotiation}>
            Start Negotiation
          </Button>
        )}
        <Button variant="outlined" startIcon={<Download />} onClick={handleDownloadOCG}>
          Download PDF
        </Button>
      </Box>
    );
  };

  // LD1: Function to render OCG sections
  const renderOCGSections = () => {
    if (!ocg || !ocg.sections) return null;

    return (
      <Grid container spacing={3}>
        {ocg.sections.map((section) => (
          <Grid item xs={12} key={section.id}>
            <OCGSectionView section={section} />
          </Grid>
        ))}
      </Grid>
    );
  };

  // LD1: Function to render OCG metadata section
  const renderMetadataSection = () => {
    if (!ocg) return null;

    return (
      <Card>
        <Typography variant="h6" gutterBottom>
          OCG Information
        </Typography>
        <Typography variant="body2">Created: {format(new Date(ocg.createdAt), 'MMMM d, yyyy')}</Typography>
        <Typography variant="body2">Last Modified: {format(new Date(ocg.updatedAt), 'MMMM d, yyyy')}</Typography>
        <Typography variant="body2">Version: {ocg.version}</Typography>
        <StatusIndicator status={ocg.status} />
      </Card>
    );
  };

  // LD1: Define breadcrumbs for navigation
  const breadcrumbs = [
    { label: 'OCGs', path: ROUTES.OCG_LIST },
    { label: ocg ? ocg.title : 'Loading...', path: '' },
  ];

  // LD1: Render loading skeleton while data is being fetched
  if (loading || !id) {
    return (
      <MainLayout>
        <Breadcrumbs routes={breadcrumbs} />
        <Skeleton variant="rectangular" width="100%" height={200} />
        <Skeleton variant="text" width="80%" />
        <Skeleton variant="text" width="60%" />
        <Skeleton variant="rectangular" width="100%" height={100} />
      </MainLayout>
    );
  }

  // LD1: Render error state if OCG cannot be loaded
  if (!ocg) {
    return (
      <MainLayout>
        <Breadcrumbs routes={breadcrumbs} />
        <Alert severity="error">Failed to load OCG. Please check the ID or try again later.</Alert>
      </MainLayout>
    );
  }

  // LD1: Render the main layout with breadcrumbs, OCG header, action buttons, and OCG sections
  return (
    <MainLayout>
      <Breadcrumbs routes={breadcrumbs} />
      <Box mb={3} display="flex" justifyContent="space-between" alignItems="center">
        <Typography variant="h4">{ocg.title}</Typography>
        {renderActionButtons()}
      </Box>
      <Grid container spacing={3}>
        <Grid item xs={12} md={8}>
          {renderOCGSections()}
        </Grid>
        <Grid item xs={12} md={4}>
          {renderMetadataSection()}
        </Grid>
      </Grid>

      {/* LD1: Render confirmation dialog for delete action */}
      <ConfirmationDialog
        isOpen={deleteDialogOpen}
        title="Delete OCG"
        message="Are you sure you want to delete this OCG? This action cannot be undone."
        confirmText="Delete"
        cancelText="Cancel"
        confirmButtonVariant="danger"
        onConfirm={confirmDeleteOCG}
        onCancel={() => setDeleteDialogOpen(false)}
      />
    </MainLayout>
  );
};

export default OCGDetailPage;