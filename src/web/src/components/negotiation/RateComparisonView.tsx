import React, { useState } from 'react'; //  ^18.2.0
import {
  Box,
  Typography,
  Grid,
  Divider,
  Paper,
  Tooltip,
  IconButton,
  Collapse,
} from '@mui/material'; //  ^5.14.0
import {
  CompareArrowsIcon,
  ArrowUpwardIcon,
  ArrowDownwardIcon,
  InfoOutlinedIcon,
  ExpandMoreIcon,
  ExpandLessIcon,
} from '@mui/icons-material'; //  ^5.14.0
import {
  RateWithDetails,
  RateStatus,
  RateType,
} from '../../types/rate';
import {
  formatCurrency,
  formatPercentage,
} from '../../utils/formatting';
import {
  RATE_FILTER,
  RATE_ACTION,
  DEFAULT_MAX_RATE_INCREASE,
} from '../../constants/rates';
import Button from '../common/Button';
import RecommendationCard from '../ai/RecommendationCard';

/**
 * @interface RateComparisonViewProps
 * @description Interface defining the props for the RateComparisonView component.
 */
interface RateComparisonViewProps {
  rate: RateWithDetails;
  isClientView: boolean;
  onRateAction: (rateId: string, action: 'approve' | 'reject' | 'counter', value?: number) => void;
  showRecommendation: boolean;
  onApplyRecommendation: () => void;
  expandedView: boolean;
  onToggleExpandedView: () => void;
}

/**
 * @function calculatePercentChange
 * @description Calculates the percentage change between two rate values.
 * @param {number} previousValue - The original rate value.
 * @param {number} newValue - The new rate value.
 * @returns {number} The percentage change value.
 */
const calculatePercentChange = (previousValue: number, newValue: number): number => {
  // Check if previousValue exists and is not zero
  if (!previousValue || previousValue === 0) {
    return 0;
  }
  // Calculate percentage change: ((newValue - previousValue) / previousValue) * 100
  const percentChange = ((newValue - previousValue) / previousValue) * 100;
  // Return the calculated percentage change rounded to one decimal place
  return parseFloat(percentChange.toFixed(1));
};

/**
 * @function getIncreaseThresholdColor
 * @description Determines the color to use based on the rate increase percentage.
 * @param {number} percentChange - The percentage change value.
 * @returns {string} Color string for styling.
 */
const getIncreaseThresholdColor = (percentChange: number): string => {
  // Compare the percentage change against the DEFAULT_MAX_RATE_INCREASE
  if (percentChange < 3) {
    // Return 'success.main' if below 3%
    return 'success.main';
  } else if (percentChange >= 3 && percentChange <= DEFAULT_MAX_RATE_INCREASE) {
    // Return 'warning.main' if between 3% and DEFAULT_MAX_RATE_INCREASE
    return 'warning.main';
  } else {
    // Return 'error.main' if above DEFAULT_MAX_RATE_INCREASE
    return 'error.main';
  }
};

/**
 * @function RateComparisonView
 * @description Component that displays a detailed comparison of rates during negotiation.
 * @param {RateComparisonViewProps} props - The props for the component.
 * @returns {JSX.Element} The rendered component.
 */
export const RateComparisonView: React.FC<RateComparisonViewProps> = ({
  rate,
  isClientView,
  onRateAction,
  showRecommendation,
  onApplyRecommendation,
  expandedView,
  onToggleExpandedView,
}) => {
  // LD1: Destructure props to access rate, isClientView, onRateAction, showRecommendation, etc.
  const [isExpanded, setIsExpanded] = useState(expandedView);

  // LD1: Extract rate details including current, proposed, and counter-proposed values
  const currentRate = rate.currentRate || 0;
  const proposedRate = rate.rate.amount;
  const counterRate = 0; // TODO: Replace with actual counter rate

  // LD1: Calculate percentage changes between different rate values
  const proposedChange = calculatePercentChange(currentRate, proposedRate);
  const counterChange = calculatePercentChange(currentRate, counterRate);

  // LD1: Determine appropriate colors for percentage changes based on thresholds
  const proposedColor = getIncreaseThresholdColor(proposedChange);
  const counterColor = getIncreaseThresholdColor(counterChange);

  // LD1: Prepare AI recommendation data if available
  const hasRecommendation = showRecommendation && rate.rate.id;

  // LD1: Render a Paper component with the rate comparison
  return (
    <Paper elevation={3} sx={{ padding: 2, margin: 1 }}>
      {/* LD1: Show attorney name and staff class in the header */}
      <Typography variant="h6" component="div">
        {rate.attorneyName} - {rate.staffClassName}
      </Typography>
      <Divider sx={{ my: 1 }} />

      {/* LD1: Display current, proposed, and counter-proposed rates in a grid layout */}
      <Grid container spacing={2} alignItems="center">
        <Grid item xs={4}>
          <Typography variant="subtitle1">Current Rate:</Typography>
          <Typography variant="body1">{formatCurrency(currentRate, rate.rate.currency)}</Typography>
        </Grid>
        <Grid item xs={4}>
          <Typography variant="subtitle1">Proposed Rate:</Typography>
          <Typography variant="body1">
            {formatCurrency(proposedRate, rate.rate.currency)}
            {/* LD1: Show percentage changes with appropriate colors and icons */}
            <Box component="span" sx={{ color: proposedColor, display: 'inline-flex', alignItems: 'center', ml: 1 }}>
              {proposedChange > 0 ? <ArrowUpwardIcon fontSize="small" /> : <ArrowDownwardIcon fontSize="small" />}
              {formatPercentage(proposedChange / 100)}
            </Box>
          </Typography>
        </Grid>
        <Grid item xs={4}>
          <Typography variant="subtitle1">Counter Rate:</Typography>
          <Typography variant="body1">
            {formatCurrency(counterRate, rate.rate.currency)}
            <Box component="span" sx={{ color: counterColor, display: 'inline-flex', alignItems: 'center', ml: 1 }}>
              {counterChange > 0 ? <ArrowUpwardIcon fontSize="small" /> : <ArrowDownwardIcon fontSize="small" />}
              {formatPercentage(counterChange / 100)}
            </Box>
          </Typography>
        </Grid>
      </Grid>

      {/* LD1: Conditionally render AI recommendation card */}
      {hasRecommendation && (
        <RecommendationCard
          recommendation={{
            id: '1',
            type: 'APPROVE',
            value: 787,
            rationale: 'Based on performance',
            confidence: 0.8,
            relatedRates: []
          }}
          onApply={() => onApplyRecommendation()}
          onDismiss={() => {}}
          onViewExplanation={() => {}}
          showFeedback={true}
        />
      )}

      {/* LD1: Provide action buttons based on user role and rate status */}
      {isClientView ? (
        <Box sx={{ mt: 2, display: 'flex', justifyContent: 'flex-end' }}>
          <Button variant="contained" color="primary" onClick={() => onRateAction(rate.rate.id, 'approve')}>
            Approve
          </Button>
          <Button variant="outlined" color="secondary" onClick={() => onRateAction(rate.rate.id, 'reject')}>
            Reject
          </Button>
          <Button variant="text" color="info" onClick={() => onRateAction(rate.rate.id, 'counter', 700)}>
            Counter
          </Button>
        </Box>
      ) : (
        <Box sx={{ mt: 2, display: 'flex', justifyContent: 'flex-end' }}>
          <Button variant="contained" color="primary" onClick={() => onRateAction(rate.rate.id, 'submit')}>
            Submit
          </Button>
        </Box>
      )}

      {/* LD1: Include expandable section with historical rate details */}
      <Box sx={{ mt: 2 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', cursor: 'pointer' }} onClick={() => setIsExpanded(!isExpanded)}>
          <Typography variant="subtitle2">
            Historical Rate Details
          </Typography>
          <IconButton aria-label="expand" size="small">
            {isExpanded ? <ExpandLessIcon /> : <ExpandMoreIcon />}
          </IconButton>
        </Box>
        <Collapse in={isExpanded} timeout="auto" unmountOnExit>
          <Box sx={{ mt: 1, p: 2, bgcolor: 'background.paper' }}>
            <Typography variant="body2">
              TODO: Implement historical rate details display
            </Typography>
          </Box>
        </Collapse>
      </Box>
    </Paper>
  );
};

export default RateComparisonView;