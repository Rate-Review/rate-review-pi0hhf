import React, { useState, useEffect, useCallback } from 'react'; //  ^18.2.0
import { useParams, useNavigate } from 'react-router-dom'; // ^6.8.0
import { useDispatch, useSelector } from 'react-redux'; // ^8.0.5
import {
  Button,
  Alert,
  Spinner,
  TextField,
} from '../../components/common';
import { OCGNegotiationInterface } from '../../components/ocg/OCGNegotiationInterface';
import { OCG } from '../../types/ocg';
import { getOCG, submitOCGNegotiation } from '../../services/ocg';
import { handleApiError } from '../../api/errorHandling';
import MainLayout from '../../components/layout/MainLayout';

/**
 * Main component for the OCG negotiation page that allows law firms to negotiate Outside Counsel Guidelines by selecting alternative language options within their point budget.
 * @returns {JSX.Element} The rendered OCG negotiation page
 */
const OCGNegotiationPage: React.FC = () => {
  // LD1: Extract the OCG ID from URL parameters using useParams
  const { ocgId } = useParams<{ ocgId: string }>();

  // LD1: Use useNavigate for programmatic navigation
  const navigate = useNavigate();

  // LD1: Use Redux dispatch
  const dispatch = useDispatch();

  // LD1: Set up state variables for selectedAlternatives and comments
  const [selectedAlternatives, setSelectedAlternatives] = useState<Record<string, string>>({});
  const [comments, setComments] = useState<string>('');

  // LD1: Set up state variable for error and loading
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState<boolean>(false);

  // LD1: Use useQuery to fetch the OCG document data
  const ocg = useSelector((state: any) => state.ocg.currentOCG);

  // LD1: Use useEffect to fetch the OCG document data
  useEffect(() => {
    const fetchOCGData = async () => {
      if (ocgId) {
        setLoading(true);
        setError(null);
        try {
          const fetchedOCG = await getOCG(ocgId);
          dispatch({ type: 'ocg/setOCG', payload: fetchedOCG });
        } catch (e: any) {
          setError(handleApiError(e).message);
        } finally {
          setLoading(false);
        }
      }
    };

    fetchOCGData();
  }, [ocgId, dispatch]);

  // LD1: Handle alternatives selection with updateSelectedAlternatives function
  const updateSelectedAlternatives = useCallback(
    (sectionId: string, alternativeId: string) => {
      setSelectedAlternatives((prev) => ({
        ...prev,
        [sectionId]: alternativeId,
      }));
    },
    []
  );

  // LD1: Handle form submission with handleSubmit function
  const handleSubmit = async () => {
    setLoading(true);
    setError(null);
    try {
      if (ocgId) {
        const submissionData = {
          ocgId: ocgId,
          selections: selectedAlternatives,
          comments: comments,
        };
        await submitOCGNegotiation(submissionData);
        navigate('/ocg/list');
      }
    } catch (e: any) {
      setError(handleApiError(e).message);
    } finally {
      setLoading(false);
    }
  };

  // LD1: Show loading state while data is being fetched
  if (loading) {
    return (
      <MainLayout>
        <Spinner />
      </MainLayout>
    );
  }

  // LD1: Display error alert if data fetching fails
  if (error) {
    return (
      <MainLayout>
        <Alert severity="error" message={error} />
      </MainLayout>
    );
  }

  // LD1: Render main layout with OCG negotiation interface
  return (
    <MainLayout>
      {ocg && (
        <OCGNegotiationInterface
          ocgId={ocgId || ''}
          organizationId="" // TODO: Replace with actual organization ID
        />
      )}
    </MainLayout>
  );
};

export default OCGNegotiationPage;