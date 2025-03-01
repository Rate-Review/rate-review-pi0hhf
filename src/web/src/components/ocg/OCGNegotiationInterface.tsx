import React, { useState, useEffect, useMemo, useCallback } from 'react'; //  ^18.2.0
import { useDispatch, useSelector } from 'react-redux'; // ^8.0.5
import { toast } from 'react-toastify'; // ^9.1.3
import {
  Button,
  Card,
  TextField,
} from '../common';
import OCGPointBudget from './OCGPointBudget';
import OCGSectionView from './OCGSectionView';
import RecommendationCard from '../ai/RecommendationCard';
import { useOCG } from '../../hooks/useOCG';
import {
  OCG,
  OCGSection,
  OCGAlternative,
  OCGNegotiationInterfaceProps,
} from '../../types/ocg';
import {
  selectOCG,
  selectOCGLoading,
} from '../../store/ocg/ocgSlice';
import {
  saveOCGSelections,
  submitOCGNegotiation,
  getOCG,
} from '../../store/ocg/ocgThunks';

/**
 * Main functional component for the OCG negotiation interface
 * @param {OCGNegotiationInterfaceProps} props - Props for the component
 * @returns {JSX.Element} Rendered component
 */
export const OCGNegotiationInterface: React.FC<OCGNegotiationInterfaceProps> = ({
  ocgId,
  organizationId,
}) => {
  // LD1: Set up state variables for selectedAlternatives, comments, loading, and submitting
  const [selectedAlternatives, setSelectedAlternatives] = useState<Record<string, string>>({});
  const [comments, setComments] = useState<string>('');
  const [loading, setLoading] = useState<boolean>(false);
  const [submitting, setSubmitting] = useState<boolean>(false);

  // LD1: Use Redux hooks to dispatch actions and select OCG data
  const dispatch = useDispatch();
  const ocg = useSelector((state: any) => selectOCG(state, ocgId));
  const ocgLoading = useSelector(selectOCGLoading);

  // LD1: Use useOCG hook for OCG functionality
  const {
    getPointsRemaining,
    submitSelections,
  } = useOCG();

  // LD1: Fetch OCG data on component mount using getOCG thunk
  useEffect(() => {
    dispatch(getOCG(ocgId));
  }, [dispatch, ocgId]);

  // LD1: Calculate points used and remaining based on selections
  const pointsUsed = useMemo(() => {
    if (!ocg) return 0;
    let totalPoints = 0;
    for (const sectionId in selectedAlternatives) {
      const section = ocg.sections.find((s) => s.id === sectionId);
      const alternative = section?.alternatives.find((a) => a.id === selectedAlternatives[sectionId]);
      totalPoints += alternative?.points || 0;
    }
    return totalPoints;
  }, [selectedAlternatives, ocg]);

  const pointsRemaining = useMemo(() => {
    if (!ocg) return 0;
    return ocg.totalPoints - pointsUsed;
  }, [ocg, pointsUsed]);

  /**
   * Handles the selection of an alternative option for a section
   * @param {string} sectionId - ID of the section
   * @param {string} alternativeId - ID of the selected alternative
   * @returns {void} No return value
   */
  const handleSectionChange = useCallback((sectionId: string, alternativeId: string) => {
    setSelectedAlternatives(prev => ({ ...prev, [sectionId]: alternativeId }));
  }, []);

  /**
   * Handles changes to the comments text field
   * @param {React.ChangeEvent<HTMLTextAreaElement>} event - Change event
   * @returns {void} No return value
   */
  const handleCommentsChange = useCallback((event: React.ChangeEvent<HTMLTextAreaElement>) => {
    setComments(event.target.value);
  }, []);

  /**
   * Saves the current OCG selections as a draft
   * @returns {Promise<void>} Promise resolving when save is complete
   */
  const handleSaveDraft = useCallback(async () => {
    setLoading(true);
    try {
      await dispatch(saveOCGSelections({
        ocgId,
        selections: selectedAlternatives,
        comments,
      }) as any).unwrap();
      toast.success('OCG selections saved as draft');
    } catch (error: any) {
      toast.error(`Failed to save OCG selections: ${error.message}`);
    } finally {
      setLoading(false);
    }
  }, [dispatch, ocgId, selectedAlternatives, comments]);

  /**
   * Submits the final OCG selections
   * @returns {Promise<void>} Promise resolving when submission is complete
   */
  const handleSubmit = useCallback(async () => {
    if (pointsUsed > (ocg?.totalPoints || 0)) {
      toast.error('Total points used exceeds the available point budget.');
      return;
    }

    setSubmitting(true);
    try {
      await dispatch(submitOCGNegotiation({
        ocgId,
        selections: selectedAlternatives,
        comments,
      }) as any).unwrap();
      toast.success('OCG selections submitted successfully');
    } catch (error: any) {
      toast.error(`Failed to submit OCG selections: ${error.message}`);
    } finally {
      setSubmitting(false);
    }
  }, [dispatch, ocgId, selectedAlternatives, comments, ocg?.totalPoints, pointsUsed]);

  // LD1: Render OCG title, version, and status information
  if (ocgLoading || !ocg) {
    return <div>Loading OCG...</div>;
  }

  return (
    <div>
      <h2>{ocg.title}</h2>
      <p>Version: {ocg.version}</p>
      <p>Status: {ocg.status}</p>

      {/* LD1: Render OCGPointBudget component */}
      <OCGPointBudget
        totalPoints={ocg.totalPoints}
        pointsUsed={pointsUsed}
      />

      {/* LD1: Render negotiable sections with OCGSectionView */}
      {ocg.sections.map((section: OCGSection) => (
        <OCGSectionView
          key={section.id}
          section={section}
          negotiationMode={true}
          selectedAlternativeId={selectedAlternatives[section.id]}
          remainingPoints={pointsRemaining}
          onAlternativeSelect={(sectionId, alternativeId) => handleSectionChange(sectionId, alternativeId)}
        />
      ))}

      {/* LD1: Render AI recommendations with RecommendationCard */}
      <RecommendationCard
        recommendation={{
          id: 'ai-recommendation-1',
          type: 'APPROVE',
          value: 0,
          rationale: 'Based on your selections, the OCG is within budget and aligns with industry standards.',
          confidence: 0.8,
          relatedRates: [],
        }}
        onApply={() => console.log('Apply recommendation')}
        onDismiss={() => console.log('Dismiss recommendation')}
        onViewExplanation={() => console.log('View explanation')}
      />

      {/* LD1: Render comments textarea and action buttons */}
      <TextField
        label="Comments"
        multiline
        rows={4}
        value={comments}
        onChange={handleCommentsChange}
        fullWidth
      />

      <Button onClick={handleSaveDraft} disabled={loading}>
        Save Draft
      </Button>
      <Button onClick={handleSubmit} disabled={submitting}>
        Submit
      </Button>
    </div>
  );
};