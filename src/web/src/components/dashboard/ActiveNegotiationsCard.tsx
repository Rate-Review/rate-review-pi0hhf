import React, { useState, useEffect, useCallback } from 'react'; //  ^18.0.0
import { Box, Typography } from '@mui/material'; // ^5.14.0
import { useNavigate } from 'react-router-dom'; // ^6.0.0
import Card, { CardHeader, CardContent, CardFooter } from '../common/Card';
import Button from '../common/Button';
import StatusIndicator from '../common/StatusIndicator';
import EmptyState from '../common/EmptyState';
import {
  NegotiationSummary,
  NegotiationStatus,
} from '../../types/negotiation';
import { formatDisplayDate, calculateDaysRemaining } from '../../utils/date';
import { ROUTES } from '../../constants/routes';
import useNegotiations from '../../hooks/useNegotiations';

/**
 * Component that displays a card with active negotiations on the dashboard
 * @param   {object} props - React props
 * @returns {JSX.Element} The rendered component
 */
const ActiveNegotiationsCard: React.FC = () => {
  // LD1: Initialize state for loading status
  const [isLoading, setIsLoading] = useState(true);

  // LD1: Setup navigation using useNavigate hook
  const navigate = useNavigate();

  // LD1: Fetch active negotiations using useNegotiations hook with filters for active status
  const { negotiations } = useNegotiations({ fetchOnMount: true });

  // LD1: Limit the displayed negotiations to a maximum of 5 for the dashboard view
  const activeNegotiations = React.useMemo(() => {
    return negotiations.filter(
      (negotiation) => negotiation.status !== NegotiationStatus.COMPLETED
    ).slice(0, 5);
  }, [negotiations]);

  // LD1: Handle click on View All button to navigate to the negotiations page
  const handleViewAllClick = () => {
    navigate(ROUTES.ACTIVE_NEGOTIATIONS);
  };

  // LD1: Render Card component with appropriate header, content, and styling
  return (
    <Card>
      <CardHeader
        title="Active Negotiations"
        action={<Button size="small" onClick={handleViewAllClick}>View All</Button>}
      />
      <CardContent>
        {/* LD1: Render EmptyState component if no active negotiations exist */}
        {activeNegotiations.length === 0 ? (
          <EmptyState
            title="No Active Negotiations"
            message="Start a new negotiation or view completed negotiations."
            icon={<Box />} // Replace with appropriate icon
          />
        ) : (
          <Box>
            {/* LD1: For each negotiation, render firm name, status indicator, and deadline */}
            {activeNegotiations.map((negotiation) => (
              <Box
                key={negotiation.id}
                sx={{
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center',
                  py: 1,
                  borderBottom: '1px solid rgba(0, 0, 0, 0.12)',
                  '&:last-child': {
                    borderBottom: 'none',
                  },
                }}
              >
                <Typography variant="body1">{negotiation.firmName}</Typography>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <StatusIndicator status={negotiation.status} />
                  <Typography variant="caption">
                    {formatDisplayDate(negotiation.submissionDeadline)}
                  </Typography>
                  {/* LD1: Add visual indicators for approaching deadlines */}
                  {calculateDaysRemaining(negotiation.submissionDeadline) <= 7 && (
                    <Typography variant="caption" color="warning.main">
                      (Due Soon)
                    </Typography>
                  )}
                </Box>
              </Box>
            ))}
          </Box>
        )}
      </CardContent>
    </Card>
  );
};

export default ActiveNegotiationsCard;