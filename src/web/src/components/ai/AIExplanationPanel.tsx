import React, { useState } from 'react';
import { 
  Card, 
  CardContent, 
  Typography, 
  Button, 
  Collapse, 
  Box, 
  Divider, 
  Chip, 
  Tooltip 
} from '@mui/material';
import { 
  InfoOutlined, 
  ExpandMore, 
  ExpandLess, 
  HelpOutline 
} from '@mui/icons-material';
import { useTheme } from '@mui/material/styles';
import { AIRecommendation } from '../../types/ai';

/**
 * Interface for detailed explanation factors
 * This should align with the backend API response structure
 */
interface AIExplanationDetail {
  factor: string;      // The name of the factor
  explanation: string; // The explanation of how this factor affects the recommendation
  impact?: number;     // Optional numeric impact (percentage) of this factor
}

/**
 * Props for the AIExplanationPanel component
 */
interface AIExplanationPanelProps {
  recommendation: AIRecommendation;
  onRequestMoreDetail?: () => void;
  isDetailed?: boolean;
  title?: string;
  className?: string;
}

/**
 * Props for the DetailedExplanation sub-component
 */
interface DetailedExplanationProps {
  details: AIExplanationDetail[];
}

/**
 * Determines the appropriate color for the confidence indicator based on the confidence level
 */
const getConfidenceColor = (confidence: number): string => {
  const theme = useTheme();
  
  if (confidence >= 0.8) {
    return theme.palette.success.main;
  } else if (confidence >= 0.6) {
    return theme.palette.info.main;
  } else if (confidence >= 0.4) {
    return theme.palette.warning.main;
  } else {
    return theme.palette.error.main;
  }
};

/**
 * Sub-component that renders the detailed explanation factors
 */
const DetailedExplanation: React.FC<DetailedExplanationProps> = ({ details }) => {
  const theme = useTheme();
  
  return (
    <Box sx={{ mt: 2 }}>
      {details.map((detail, index) => (
        <Box key={index} sx={{ mb: 2 }}>
          <Box display="flex" alignItems="flex-start">
            <InfoOutlined 
              fontSize="small" 
              color="info" 
              sx={{ mt: 0.5, mr: 1 }} 
            />
            <Box>
              <Typography variant="subtitle2" fontWeight="medium">
                {detail.factor}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                {detail.explanation}
              </Typography>
              {detail.impact !== undefined && (
                <Typography 
                  variant="body2" 
                  sx={{ 
                    color: detail.impact > 0 
                      ? theme.palette.success.main 
                      : theme.palette.error.main,
                    fontWeight: 'medium',
                    mt: 0.5
                  }}
                >
                  Impact: {detail.impact > 0 ? '+' : ''}{detail.impact}%
                </Typography>
              )}
            </Box>
          </Box>
        </Box>
      ))}
    </Box>
  );
};

/**
 * Component that displays AI recommendations with explanations and allows users to view detailed rationales
 */
export const AIExplanationPanel: React.FC<AIExplanationPanelProps> = ({
  recommendation,
  onRequestMoreDetail,
  isDetailed = false,
  title = 'AI Recommendation',
  className = '',
}) => {
  const [expanded, setExpanded] = useState(false);
  const theme = useTheme();
  
  /**
   * Handles the click event on the expand/collapse button
   */
  const handleExpandClick = () => {
    if (!expanded && !isDetailed && onRequestMoreDetail) {
      onRequestMoreDetail();
    }
    setExpanded(!expanded);
  };
  
  return (
    <Card 
      className={className}
      variant="outlined"
      sx={{ 
        mb: 2,
        borderColor: theme.palette.primary.light,
        borderWidth: '1px'
      }}
    >
      <CardContent>
        <Box display="flex" alignItems="center" justifyContent="space-between" mb={1}>
          <Typography variant="h6" color="primary">
            {title}
          </Typography>
          {recommendation.confidence !== undefined && (
            <Tooltip title={`Confidence level: ${Math.round(recommendation.confidence * 100)}%`}>
              <Chip 
                label={`${Math.round(recommendation.confidence * 100)}% Confidence`} 
                size="small"
                sx={{
                  backgroundColor: getConfidenceColor(recommendation.confidence),
                  color: 'white',
                  fontWeight: 'medium'
                }}
              />
            </Tooltip>
          )}
        </Box>
        
        <Typography variant="body1" paragraph>
          <strong>{recommendation.type}</strong> 
          {recommendation.value && `: ${recommendation.value}`}
        </Typography>
        
        <Typography variant="body2" color="text.secondary">
          {recommendation.rationale}
        </Typography>
        
        {(isDetailed || (recommendation as any).details) && (
          <>
            <Divider sx={{ my: 2 }} />
            
            <Button
              onClick={handleExpandClick}
              endIcon={expanded ? <ExpandLess /> : <ExpandMore />}
              sx={{ textTransform: 'none' }}
              aria-expanded={expanded}
              aria-controls="detailed-explanation-section"
            >
              {expanded ? 'Hide detailed explanation' : 'Show detailed explanation'}
            </Button>
            
            <Collapse in={expanded} timeout="auto" unmountOnExit id="detailed-explanation-section">
              {isDetailed && (recommendation as any).details ? (
                <DetailedExplanation details={(recommendation as any).details} />
              ) : (
                <Box display="flex" alignItems="center" p={2}>
                  <HelpOutline color="action" sx={{ mr: 1 }} />
                  <Typography variant="body2" color="text.secondary">
                    {onRequestMoreDetail 
                      ? 'Fetching detailed explanation...' 
                      : 'Detailed explanation not available for this recommendation.'}
                  </Typography>
                </Box>
              )}
            </Collapse>
          </>
        )}
      </CardContent>
    </Card>
  );
};

export default AIExplanationPanel;