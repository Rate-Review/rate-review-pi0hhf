import React, { useState, useCallback } from 'react'; //  ^18.0.0
import styled from 'styled-components'; //  ^5.3.10
import {
  Card,
  CardHeader,
  CardContent,
  CardFooter,
} from '../common/Card';
import Button from '../common/Button';
import Badge from '../common/Badge';
import { useAIContext } from '../../context/AIContext';
import {
  AIRecommendation,
  RecommendationType,
} from '../../types/ai';
import { CheckCircle, Cancel, CompareArrows, Info } from '@mui/icons-material';

/**
 * @interface RecommendationCardProps
 * @description Props interface for the RecommendationCard component
 */
interface RecommendationCardProps {
  recommendation: AIRecommendation;
  onApply: (recommendation: AIRecommendation) => void;
  onDismiss: (id: string) => void;
  onViewExplanation: (id: string) => void;
  compact?: boolean;
  showFeedback?: boolean;
  className?: string;
}

/**
 * @styledcomponent
 * @description Styles for the Card component
 */
const StyledCard = styled(Card)<{ recommendationType: RecommendationType }>`
  border-left: 4px solid ${props => getRecommendationColor(props.recommendationType)};
  margin-bottom: ${props => props.theme.spacing(2)};
  transition: all ${props => props.theme.transitions.normal};

  &:hover {
    box-shadow: ${props => props.theme.shadows[2]};
  }
`;

/**
 * @styledcomponent
 * @description Styles for the Recommendation Badge
 */
const RecommendationBadge = styled(Badge)<{ type: RecommendationType }>`
  background-color: ${props => getRecommendationColor(props.type)};
  color: white;
  text-transform: capitalize;
  font-size: 0.75rem;
  padding: ${props => props.theme.spacing(0.5)} ${props => props.theme.spacing(1)};
`;

/**
 * @styledcomponent
 * @description Styles for the Confidence Indicator
 */
const ConfidenceIndicator = styled.div`
  display: flex;
  align-items: center;
  font-size: 0.75rem;
  color: ${props => props.theme.colors.neutral.main};
`;

/**
 * @styledcomponent
 * @description Styles for the Feedback Buttons
 */
const FeedbackButtons = styled.div`
  display: flex;
  gap: ${props => props.theme.spacing(1)};
  margin-top: ${props => props.theme.spacing(1)};
`;

/**
 * @function getRecommendationIcon
 * @description Determines the appropriate icon based on recommendation type
 * @param {RecommendationType} RecommendationType
 * @returns {JSX.Element} Icon component for the recommendation type
 */
function getRecommendationIcon(RecommendationType: RecommendationType): JSX.Element {
  switch (RecommendationType) {
    case RecommendationType.APPROVE:
      return <CheckCircle />;
    case RecommendationType.REJECT:
      return <Cancel />;
    case RecommendationType.COUNTER:
      return <CompareArrows />;
    default:
      return <Info />;
  }
}

/**
 * @function getRecommendationColor
 * @description Determines the appropriate color based on recommendation type
 * @param {RecommendationType} RecommendationType
 * @returns {string} Color code matching the recommendation type
 */
function getRecommendationColor(RecommendationType: RecommendationType): string {
  switch (RecommendationType) {
    case RecommendationType.APPROVE:
      return '#38A169'; // Success color
    case RecommendationType.REJECT:
      return '#E53E3E'; // Error color
    case RecommendationType.COUNTER:
      return '#DD6B20'; // Warning color
    default:
      return '#3182CE'; // Info color
  }
}

/**
 * @component RecommendationCard
 * @description A card component that displays AI recommendations with actions for applying, dismissing, or viewing explanations
 */
export const RecommendationCard: React.FC<RecommendationCardProps> = ({
  recommendation,
  onApply,
  onDismiss,
  onViewExplanation,
  compact = false,
  showFeedback = false,
  className,
}) => {
  // LD1: Destructure props: recommendation, onApply, onDismiss, onViewExplanation, compact, showFeedback, className
  const { type, value, rationale, confidence, id } = recommendation;

  // LD1: Define state variable for tracking feedback submission
  const [feedbackSubmitted, setFeedbackSubmitted] = useState(false);

  // LD1: Access provideFeedback function from AIContext
  const { provideFeedback } = useAIContext();

  /**
   * @function handleProvideFeedback
   * @description Submits user feedback on the recommendation
   * @param {boolean} helpful - Whether the recommendation was helpful
   * @param {string} comments - Optional comments about the recommendation
   */
  const handleProvideFeedback = async (helpful: boolean, comments: string = '') => {
    // LD1: Call provideFeedback from AIContext with recommendation ID, helpful flag, and optional comments
    await provideFeedback({
      recommendationId: id,
      helpful: helpful,
      comments: comments,
    });

    // LD1: Set feedbackSubmitted state to true
    setFeedbackSubmitted(true);

    // LD1: Show toast notification confirming feedback submission
    // toast.success('Thank you for your feedback!');
  };

  // LD1: Render StyledCard with recommendationType prop
  return (
    <StyledCard recommendationType={type} className={className}>
      {/* LD1: Render CardHeader with RecommendationBadge for type and ConfidenceIndicator for confidence */}
      <CardHeader
        title={
          <>
            <RecommendationBadge type={type}>{type}</RecommendationBadge>
            {compact ? null : (
              <ConfidenceIndicator>
                Confidence: {Math.round(confidence * 100)}%
              </ConfidenceIndicator>
            )}
          </>
        }
        action={
          compact ? null : (
            <ConfidenceIndicator>
              Confidence: {Math.round(confidence * 100)}%
            </ConfidenceIndicator>
          )
        }
      />
      {/* LD1: Render CardContent with recommendation rationale */}
      <CardContent padding={compact ? '0' : undefined}>
        {rationale}
      </CardContent>
      {/* LD1: Render CardFooter with action buttons: Apply, Dismiss, View Explanation */}
      <CardFooter>
        <Button size="small" variant="text" color="primary" onClick={() => onApply(recommendation)}>
          Apply
        </Button>
        <Button size="small" variant="text" color="neutral" onClick={() => onDismiss(id)}>
          Dismiss
        </Button>
        <Button size="small" variant="text" color="info" onClick={() => onViewExplanation(id)}>
          View Explanation
        </Button>
      </CardFooter>
      {/* LD1: If showFeedback is true and feedback hasn't been submitted, render FeedbackButtons with thumbs up/down options */}
      {showFeedback && !feedbackSubmitted && (
        <FeedbackButtons>
          <Button size="small" variant="outlined" color="success" onClick={() => handleProvideFeedback(true)}>
            👍 Helpful
          </Button>
          <Button size="small" variant="outlined" color="error" onClick={() => handleProvideFeedback(false)}>
            👎 Not Helpful
          </Button>
        </FeedbackButtons>
      )}
    </StyledCard>
  );
};

// IE3: Be generous about your exports so long as it doesn't create a security risk.
export default RecommendationCard;