import React, { useEffect, useState, useCallback } from 'react'; // React library for building UI components // React hooks for state and lifecycle management
import { useParams, useNavigate } from 'react-router-dom'; // React Router hooks for navigation and URL parameters // React Router hooks for navigation and URL parameters
import { useDispatch, useSelector } from 'react-redux'; // Redux hooks for state management // Redux hooks for state management
import {
  Box,
  Paper,
  Container,
  Typography,
  Button,
  CircularProgress,
  Alert,
} from '@mui/material'; // Material UI components for layout and display // Material UI components for layout and display
import { ArrowBack } from '@mui/icons-material'; // Material UI icon for navigation // Material UI icon for navigation
import { styled } from '@mui/material/styles'; // Material UI styling utility // Material UI styling utility
import PageHeader from '../../components/layout/PageHeader';
import NegotiationInterface from '../../components/negotiation/NegotiationInterface';
import AIChatInterface from '../../components/ai/AIChatInterface';
import useNegotiations from '../../hooks/useNegotiations';
import { Negotiation, NegotiationStatus } from '../../types/negotiation';
import { ROUTES } from '../../constants/routes';

// LD1: Styled component for the main page container
const PageContainer = styled(Container)`
  padding: 24px;
  max-width: 1600px;
`;

// LD1: Styled component for the negotiation interface container
const NegotiationContainer = styled(Paper)`
  padding: 0;
  overflow: hidden;
  height: calc(100vh - 180px);
  display: flex;
  flex-direction: column;
`;

// LD1: Styled component for the loading container
const LoadingContainer = styled(Box)`
  display: flex;
  justify-content: center;
  align-items: center;
  height: 400px;
`;

// LD1: Styled component for the back button
const BackButton = styled(Button)`
  margin-bottom: 16px;
`;

/**
 * Main component for the negotiation detail page, displaying a specific negotiation's details
 */
const NegotiationDetailPage: React.FC = () => {
  // LD1: Extract negotiationId from URL parameters using useParams
  const { negotiationId } = useParams<{ negotiationId: string }>();

  // LD1: Initialize navigation function using useNavigate
  const navigate = useNavigate();

  // LD1: Get dispatch function using useDispatch
  const dispatch = useDispatch();

  // LD1: Set up state for loading status, error messages, and negotiation data
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [negotiation, setNegotiation] = useState<Negotiation | null>(null);

  // LD1: Use useNegotiations hook to access negotiation functionality
  const { fetchNegotiation } = useNegotiations({});

  // LD1: Implement useEffect to fetch negotiation data when the component mounts or negotiationId changes
  useEffect(() => {
    const loadNegotiation = async () => {
      setLoading(true);
      setError(null);
      try {
        if (negotiationId) {
          const negotiationData = await fetchNegotiation(negotiationId);
          setNegotiation(negotiationData);
        }
      } catch (e: any) {
        setError(e.message);
      } finally {
        setLoading(false);
      }
    };

    loadNegotiation();
  }, [negotiationId, fetchNegotiation]);

  // LD1: Implement handleBack function to navigate to negotiations list
  const handleBack = useCallback(() => {
    navigate(ROUTES.NEGOTIATIONS);
  }, [navigate]);

  // LD1: Implement handleActionExecuted callback for AI actions
  const handleActionExecuted = useCallback((actionResult: any) => {
    // TODO: Implement action execution handling
  }, []);

  // LD1: Function to generate breadcrumb items for the page header
  const getBreadcrumbItems = (negotiation: Negotiation | null) => {
    const baseBreadcrumbs = [
      { label: 'Negotiations', path: ROUTES.NEGOTIATIONS },
    ];

    if (negotiation) {
      return [
        ...baseBreadcrumbs,
        { label: getPageTitle(negotiation), path: '' },
      ];
    }

    return baseBreadcrumbs;
  };

  // LD1: Function to generate the page title based on negotiation data
  const getPageTitle = (negotiation: Negotiation | null) => {
    if (negotiation) {
      return `${negotiation.firm.name} vs. ${negotiation.client.name}`;
    }
    return 'Negotiation Details';
  };

  // LD1: Render loading spinner when data is being fetched
  if (loading) {
    return (
      <LoadingContainer>
        <CircularProgress />
      </LoadingContainer>
    );
  }

  // LD1: Render error message if there was an error fetching data
  if (error) {
    return <Alert severity="error" message={error} />;
  }

  // LD1: Render PageHeader with negotiation title and back button
  return (
    <PageContainer>
      <BackButton variant="outlined" startIcon={<ArrowBack />} onClick={handleBack}>
        Back to Negotiations
      </BackButton>
      <PageHeader title={getPageTitle(negotiation)} breadcrumbs={getBreadcrumbItems(negotiation)} />
      <NegotiationContainer>
        {negotiation && (
          <NegotiationInterface
            negotiationId={negotiationId}
            onActionExecuted={handleActionExecuted}
          />
        )}
      </NegotiationContainer>
      <AIChatInterface contextId={negotiationId} initiallyMinimized={true} onActionExecuted={handleActionExecuted} />
    </PageContainer>
  );
};

export default NegotiationDetailPage;