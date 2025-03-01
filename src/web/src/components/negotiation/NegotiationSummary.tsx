import React, { useMemo } from 'react'; // React v18.0.0
import { Box, Typography, Button, Divider, Grid } from '@mui/material'; // @mui/material v5.14.0
import AccessTimeIcon from '@mui/icons-material/AccessTime'; // @mui/icons-material v5.14.0
import AttachMoneyIcon from '@mui/icons-material/AttachMoney'; // @mui/icons-material v5.14.0
import PeopleIcon from '@mui/icons-material/People'; // @mui/icons-material v5.14.0
import ArrowForwardIcon from '@mui/icons-material/ArrowForward'; // @mui/icons-material v5.14.0
import StatusIndicator from '../common/StatusIndicator';
import Card from '../common/Card';
import RateImpactChart from '../charts/RateImpactChart';
import { formatCurrency } from '../../utils/formatting';
import { formatDate } from '../../utils/date';
import { calculateRateImpact } from '../../utils/calculations';
import { Negotiation } from '../../types/negotiation';
import { useNegotiations } from '../../hooks/useNegotiations';

/**
 * @interface NegotiationSummaryProps
 * @description Props for the NegotiationSummary component
 */
interface NegotiationSummaryProps {
  negotiation: Negotiation;
  onViewDetails?: (id: string) => void;
  showActions?: boolean;
  compact?: boolean;
}

/**
 * @function calculateProgress
 * @description Calculates the progress percentage of a negotiation based on rates that have been acted upon
 * @param {Negotiation} negotiation - Negotiation
 * @returns {number} Percentage of completion (0-100)
 */
const calculateProgress = (negotiation: Negotiation): number => {
  // LD1: Count total number of rates in the negotiation
  const totalRates = negotiation.rateIds.length;

  // LD1: Count rates with status other than 'Submitted' (approved, rejected, countered)
  const actedUponRates = negotiation.rateIds.filter(rateId => {
    // TODO: Replace with actual rate status check
    return true;
  }).length;

  // LD1: Calculate percentage of rates that have been acted upon
  const progress = totalRates > 0 ? (actedUponRates / totalRates) * 100 : 0;

  // LD1: Return the percentage, or 0 if no rates exist
  return progress;
};

/**
 * @function getRateStatusCounts
 * @description Returns counts of rates by status (approved, rejected, countered, pending)
 * @param {Negotiation} negotiation - Negotiation
 * @returns {object} { approved: number, rejected: number, countered: number, pending: number }
 */
const getRateStatusCounts = (negotiation: Negotiation): { approved: number, rejected: number, countered: number, pending: number } => {
  // LD1: Initialize counters for each status type
  let approved = 0;
  let rejected = 0;
  let countered = 0;
  let pending = 0;

  // LD1: Iterate through rates in the negotiation
  negotiation.rateIds.forEach(rateId => {
    // TODO: Replace with actual rate status check
    const status = 'pending';

    // LD1: Increment appropriate counter based on rate status
    if (status === 'approved') {
      approved++;
    } else if (status === 'rejected') {
      rejected++;
    } else if (status === 'countered') {
      countered++;
    } else {
      pending++;
    }
  });

  // LD1: Return object with all counters
  return { approved, rejected, countered, pending };
};

/**
 * @class NegotiationSummary
 * @description A component that displays a summary of a rate negotiation with key metrics and status information
 */
const NegotiationSummary: React.FC<NegotiationSummaryProps> = ({ negotiation, onViewDetails, showActions, compact }) => {
  // IE1: Access the useNegotiations hook to get access to the functions
  const { fetchNegotiation } = useNegotiations({});

  // LD1: Calculate progress and rate status counts using helper functions
  const progress = useMemo(() => calculateProgress(negotiation), [negotiation]);
  const { approved, rejected, countered, pending } = useMemo(() => getRateStatusCounts(negotiation), [negotiation]);

  return (
    // LD1: Card container with padding and box-shadow
    <Card style={{ marginBottom: '16px' }}>
      {/* LD1: Header section with negotiation title and status indicator */}
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
        <Typography variant="h6">{negotiation.type} Negotiation</Typography>
        <StatusIndicator status={negotiation.status} />
      </Box>

      {/* LD1: Dates section showing request date, submission deadline, and completion date */}
      <Grid container spacing={2}>
        <Grid item xs={4}>
          <Box display="flex" alignItems="center">
            <AccessTimeIcon sx={{ mr: 1 }} />
            <Typography variant="body2">Request Date: {formatDate(negotiation.requestDate)}</Typography>
          </Box>
        </Grid>
        <Grid item xs={4}>
          <Box display="flex" alignItems="center">
            <AccessTimeIcon sx={{ mr: 1 }} />
            <Typography variant="body2">Submission Deadline: {formatDate(negotiation.submissionDeadline)}</Typography>
          </Box>
        </Grid>
        <Grid item xs={4}>
          <Box display="flex" alignItems="center">
            <AccessTimeIcon sx={{ mr: 1 }} />
            <Typography variant="body2">Completion Date: {formatDate(negotiation.completionDate)}</Typography>
          </Box>
        </Grid>
      </Grid>

      <Divider style={{ margin: '16px 0' }} />

      {/* LD1: Parties section showing client and law firm information */}
      <Grid container spacing={2}>
        <Grid item xs={6}>
          <Box display="flex" alignItems="center">
            <PeopleIcon sx={{ mr: 1 }} />
            <Typography variant="body2">Client: {negotiation.client.name}</Typography>
          </Box>
        </Grid>
        <Grid item xs={6}>
          <Box display="flex" alignItems="center">
            <PeopleIcon sx={{ mr: 1 }} />
            <Typography variant="body2">Law Firm: {negotiation.firm.name}</Typography>
          </Box>
        </Grid>
      </Grid>

      <Divider style={{ margin: '16px 0' }} />

      {/* LD1: Financial impact section showing total impact amount and percentage */}
      <Box display="flex" justifyContent="space-between" alignItems="center">
        <Box display="flex" alignItems="center">
          <AttachMoneyIcon sx={{ mr: 1 }} />
          <Typography variant="body1">
            Total Impact: {formatCurrency(1000, 'USD')} (+10%)
          </Typography>
        </Box>
        <Typography variant="caption">Progress: {progress}%</Typography>
      </Box>

      {/* LD1: Rate statistics section showing counts of approved, rejected, countered, and pending rates */}
      <Box display="flex" justifyContent="space-around" mt={2}>
        <Typography variant="caption">Approved: {approved}</Typography>
        <Typography variant="caption">Rejected: {rejected}</Typography>
        <Typography variant="caption">Countered: {countered}</Typography>
        <Typography variant="caption">Pending: {pending}</Typography>
      </Box>

      {/* LD1: Action buttons (when showActions is true) for viewing details or taking next steps */}
      {showActions && (
        <Box mt={2} display="flex" justifyContent="flex-end">
          <Button
            variant="contained"
            endIcon={<ArrowForwardIcon />}
            onClick={() => onViewDetails && onViewDetails(negotiation.id)}
          >
            View Details
          </Button>
        </Box>
      )}

      {/* LD1: RateImpactChart component (when not in compact mode) showing impact by staff class */}
      {!compact && (
        <Box mt={3}>
          <RateImpactChart
            data={[]}
            groupBy="staffClass"
            currency="USD"
          />
        </Box>
      )}
    </Card>
  );
};

export default NegotiationSummary;