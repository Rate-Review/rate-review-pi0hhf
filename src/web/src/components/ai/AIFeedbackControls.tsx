import React, { useState, useCallback } from 'react'; // ^18.0.0
import {
  ThumbUpOutlined,
  ThumbDownOutlined,
  ThumbUp,
  ThumbDown,
} from '@mui/icons-material'; // ^5.14.0
import styled from 'styled-components';
import { useAI } from '../../hooks/useAI';
import { AIFeedbackType } from '../../types/ai';
import { Button } from '../common/Button';
import { Tooltip } from '../common/Tooltip';

interface AIFeedbackControlsProps {
  contentId: string;
  contentType: string;
  initialFeedback?: AIFeedbackType | null;
  onFeedbackSubmit?: (feedbackType: AIFeedbackType) => void;
  size?: 'small' | 'medium' | 'large';
  className?: string;
}

const FeedbackContainer = styled.div`
  display: inline-flex;
  align-items: center;
  gap: ${(props) => props.theme.spacing.sm}px;
`;

const FeedbackButton = styled(Button)`
  padding: ${(props) => props.theme.spacing.xs}px;
  border-radius: 50%;
  min-width: auto;
  width: 32px;
  height: 32px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
`;

/**
 * Component that displays thumbs up/down controls for providing feedback on AI-generated content
 * @param {AIFeedbackControlsProps} props - Component props
 * @returns {ReactElement} The rendered component
 */
const AIFeedbackControls: React.FC<AIFeedbackControlsProps> = ({
  contentId,
  contentType,
  initialFeedback,
  onFeedbackSubmit,
  size = 'medium',
  className,
}) => {
  // LD1: Initialize feedback state with initialFeedback or null
  const [feedback, setFeedback] = useState<AIFeedbackType | null>(initialFeedback || null);
  // LD1: Initialize isSubmitting state as false
  const [isSubmitting, setIsSubmitting] = useState(false);
  // LD1: Get submitFeedback function from useAI hook
  const { provideFeedback: submitFeedback } = useAI();

  /**
   * Handles user feedback selection and submission
   * @param {AIFeedbackType} feedbackType - The type of feedback (thumbs up or thumbs down)
   * @returns {void} No return value
   */
  const handleFeedback = useCallback(
    async (feedbackType: AIFeedbackType) => {
      // LD1: Set feedback state to the selected type
      setFeedback(feedbackType);
      // LD1: Set isSubmitting to true
      setIsSubmitting(true);
      try {
        // LD1: Call submitFeedback from useAI hook with contentId, contentType, and feedbackType
        await submitFeedback({
          contentId: contentId,
          contentType: contentType,
          feedbackType: feedbackType,
        });
        // LD1: Call onFeedbackSubmit callback if provided
        onFeedbackSubmit?.(feedbackType);
      } finally {
        // LD1: Set isSubmitting to false when submission completes
        setIsSubmitting(false);
      }
    },
    [contentId, contentType, submitFeedback, onFeedbackSubmit]
  );

  // LD1: Render container div with appropriate className
  return (
    <FeedbackContainer className={className}>
      {/* LD1: Render Tooltip wrapped ThumbUp button */}
      <Tooltip content="This was helpful">
        <FeedbackButton
          variant="text"
          size={size}
          disabled={isSubmitting}
          onClick={() => handleFeedback('positive')}
          aria={{label: 'Helpful'}}
        >
          {/* LD1: Use conditional rendering to show filled or outlined icons based on current feedback state */}
          {feedback === 'positive' ? <ThumbUp /> : <ThumbUpOutlined />}
        </FeedbackButton>
      </Tooltip>

      {/* LD1: Render Tooltip wrapped ThumbDown button */}
      <Tooltip content="This was not helpful">
        <FeedbackButton
          variant="text"
          size={size}
          disabled={isSubmitting}
          onClick={() => handleFeedback('negative')}
          aria={{label: 'Not Helpful'}}
        >
          {/* LD1: Use conditional rendering to show filled or outlined icons based on current feedback state */}
          {feedback === 'negative' ? <ThumbDown /> : <ThumbDownOutlined />}
        </FeedbackButton>
      </Tooltip>
    </FeedbackContainer>
  );
};

export default AIFeedbackControls;