import React, { useState, useCallback, useMemo } from 'react'; //  ^18.0.0
import { useDispatch, useSelector } from 'react-redux'; // ^7.2.0
import {
  Box,
  Stack,
  Typography,
  Tooltip,
} from '@mui/material'; //  ^5.14.0
import Button from '../common/Button';
import { ConfirmationDialog } from '../common/ConfirmationDialog';
import TextField from '../common/TextField';
import { RecommendationCard } from '../ai/RecommendationCard';
import { usePermissions } from '../../hooks/usePermissions';
import { useAIContext } from '../../context/AIContext';
import {
  approveRate,
  rejectRate,
  counterProposeRate,
} from '../../store/negotiations/negotiationsThunks';
import { selectRealTimeMode } from '../../store/negotiations/negotiationsSlice';
import { RateApprovalStatus, Rate, Negotiation } from '../../types/rate';

/**
 * @interface ApprovalActionsProps
 * @description Props interface for the ApprovalActions component
 */
interface ApprovalActionsProps {
  rateId: string;
  negotiationId: string;
  currentRate: number;
  proposedRate: number;
  rateType?: string;
  aiRecommendation?: string | null;
  aiRecommendedValue?: number | null;
  aiRecommendationRationale?: string | null;
  onCounterPropose: (rate: Rate) => void;
  disabled?: boolean;
  bulk?: boolean;
  rateIds?: string[];
  onActionComplete?: () => void;
  compact?: boolean;
  showAIRecommendation?: boolean;
}

/**
 * @component ApprovalActions
 * @description Component that renders approval action buttons and handles approval workflow for rates in negotiation
 */
const ApprovalActions: React.FC<ApprovalActionsProps> = ({
  rateId,
  negotiationId,
  currentRate,
  proposedRate,
  rateType,
  aiRecommendation,
  aiRecommendedValue,
  aiRecommendationRationale,
  onCounterPropose,
  disabled = false,
  bulk = false,
  rateIds,
  onActionComplete,
  compact = false,
  showAIRecommendation = true,
}) => {
  // LD1: Define state variables for confirmation dialogs and comment input
  const [approveDialogOpen, setApproveDialogOpen] = useState(false);
  const [rejectDialogOpen, setRejectDialogOpen] = useState(false);
  const [comment, setComment] = useState('');

  // LD1: Access Redux dispatch function
  const dispatch = useDispatch();

  // LD1: Access realTimeMode from Redux store
  const realTimeMode = useSelector(selectRealTimeMode);

  // LD1: Access permission checking functions using usePermissions hook
  const { can } = usePermissions();

  // LD1: Access AI context for recommendations
  const { recommendations } = useAIContext();

  // LD1: Memoize the hasApprovePermission check to prevent unnecessary re-renders
  const hasApprovePermission = useMemo(
    () => can('approve', 'rates', 'organization'),
    [can]
  );

  // LD1: Memoize the hasRejectPermission check to prevent unnecessary re-renders
  const hasRejectPermission = useMemo(
    () => can('reject', 'rates', 'organization'),
    [can]
  );

  /**
   * @function handleApprove
   * @description Handles the approval action for a rate or multiple rates
   * @param {MouseEvent} event - The click event
   * @returns {void} No return value
   */
  const handleApprove = useCallback((event: React.MouseEvent<HTMLButtonElement>) => {
    event.preventDefault();
    setApproveDialogOpen(true);
  }, []);

  /**
   * @function handleReject
   * @description Handles the rejection action for a rate or multiple rates
   * @param {MouseEvent} event - The click event
   * @returns {void} No return value
   */
  const handleReject = useCallback((event: React.MouseEvent<HTMLButtonElement>) => {
    event.preventDefault();
    setRejectDialogOpen(true);
  }, []);

  /**
   * @function handleCounterPropose
   * @description Handles the counter-proposal action by showing the counter proposal panel
   * @param {MouseEvent} event - The click event
   * @returns {void} No return value
   */
  const handleCounterPropose = useCallback((event: React.MouseEvent<HTMLButtonElement>) => {
    event.preventDefault();
    onCounterPropose({
      id: rateId,
      amount: aiRecommendedValue || proposedRate,
      currency: 'USD',
      effectiveDate: new Date().toISOString(),
      expirationDate: null,
      type: 'PROPOSED',
      status: 'SUBMITTED',
      attorneyId: '123',
      clientId: '456',
      firmId: '789',
      staffClassId: '101',
      history: [],
    });
  }, [aiRecommendedValue, onCounterPropose, proposedRate, rateId]);

  /**
   * @function handleConfirmationClose
   * @description Closes any open confirmation dialogs without taking action
   * @returns {void} No return value
   */
  const handleConfirmationClose = useCallback(() => {
    setApproveDialogOpen(false);
    setRejectDialogOpen(false);
    setComment('');
  }, []);

  /**
   * @function handleCommentChange
   * @description Updates the comment state when user types in comment field
   * @param {ChangeEvent} event - The change event
   * @returns {void} No return value
   */
  const handleCommentChange = useCallback((event: React.ChangeEvent<HTMLInputElement>) => {
    setComment(event.target.value);
  }, []);

  // LD1: Render the ApprovalActions component with action buttons and confirmation dialogs
  return (
    <Box>
      {showAIRecommendation && aiRecommendation && (
        <RecommendationCard
          recommendation={{
            id: rateId,
            type: aiRecommendation as any,
            value: aiRecommendedValue,
            rationale: aiRecommendationRationale || 'AI Recommendation',
            confidence: 0.8,
            relatedRates: [],
          }}
          onApply={() => {
            if (aiRecommendedValue) {
              dispatch(
                counterProposeRate({
                  rateId: rateId,
                  amount: aiRecommendedValue,
                  message: 'AI Recommendation',
                })
              );
            }
          }}
          onDismiss={() => {}}
          onViewExplanation={() => {}}
          compact={compact}
        />
      )}
      <Stack direction="row" spacing={2}>
        <Tooltip title={!hasApprovePermission ? 'Missing approve permission' : ''}>
          <span>
            <Button
              variant="contained"
              color="primary"
              onClick={handleApprove}
              disabled={disabled || !hasApprovePermission}
            >
              Approve
            </Button>
          </span>
        </Tooltip>
        <Tooltip title={!hasRejectPermission ? 'Missing reject permission' : ''}>
          <span>
            <Button
              variant="outlined"
              color="error"
              onClick={handleReject}
              disabled={disabled || !hasRejectPermission}
            >
              Reject
            </Button>
          </span>
        </Tooltip>
        <Button
          variant="text"
          color="secondary"
          onClick={handleCounterPropose}
          disabled={disabled}
        >
          Counter Propose
        </Button>
      </Stack>

      {/* LD1: Confirmation dialog for approving rates */}
      <ConfirmationDialog
        isOpen={approveDialogOpen}
        title="Approve Rate"
        message="Are you sure you want to approve this rate?"
        confirmText="Approve"
        onConfirm={() => {
          dispatch(
            approveRate({
              rateIds: rateIds || [rateId],
              approvalData: { message: comment },
            })
          ).then(() => {
            handleConfirmationClose();
            onActionComplete?.();
          });
        }}
        onCancel={handleConfirmationClose}
      >
        <TextField
          label="Approval Comment"
          value={comment}
          onChange={handleCommentChange}
          fullWidth
          multiline
          rows={4}
        />
      </ConfirmationDialog>

      {/* LD1: Confirmation dialog for rejecting rates */}
      <ConfirmationDialog
        isOpen={rejectDialogOpen}
        title="Reject Rate"
        message="Are you sure you want to reject this rate?"
        confirmText="Reject"
        confirmButtonVariant="danger"
        onConfirm={() => {
          dispatch(
            rejectRate({
              rateIds: rateIds || [rateId],
              rejectionData: { message: comment },
            })
          ).then(() => {
            handleConfirmationClose();
            onActionComplete?.();
          });
        }}
        onCancel={handleConfirmationClose}
      >
        <TextField
          label="Rejection Comment"
          value={comment}
          onChange={handleCommentChange}
          fullWidth
          multiline
          rows={4}
        />
      </ConfirmationDialog>
    </Box>
  );
};

// IE3: Be generous about your exports so long as it doesn't create a security risk.
export default ApprovalActions;