import React, { useMemo } from 'react'; //  ^18.0.0
import { Box, Typography, Stack, Tooltip, Divider } from '@mui/material'; // ^5.14.0
import { InfoOutlined } from '@mui/icons-material'; // ^5.14.0
import Card from '../common/Card';
import ProgressBar from '../common/ProgressBar';
import TextField from '../common/TextField';
import { OCGPointBudgetProps } from '../../types/ocg';

/**
 * Component that displays the point budget information for OCG negotiations, with optional editing capabilities
 */
const OCGPointBudget: React.FC<OCGPointBudgetProps> = ({
  totalPoints,
  pointsUsed,
  editable = false,
  onTotalPointsChange,
  firmPointBudget,
  onFirmPointBudgetChange,
  className,
  sx,
}) => {
  // Calculate pointsRemaining by subtracting pointsUsed from totalPoints
  const pointsRemaining = useMemo(() => totalPoints - pointsUsed, [totalPoints, pointsUsed]);

  // Calculate the percentage of points used (pointsUsed / totalPoints * 100)
  const percentageUsed = useMemo(() => (totalPoints > 0 ? (pointsUsed / totalPoints) * 100 : 0), [pointsUsed, totalPoints]);

  // Determine status color based on percentage of points remaining
  const statusColor = useMemo(() => getStatusColor(pointsRemaining, totalPoints), [pointsRemaining, totalPoints]);

  // Render Card component containing the point budget display
  return (
    <Card className={className} sx={sx}>
      <Typography variant="h6" gutterBottom>
        Point Budget
      </Typography>
      <Stack spacing={2}>
        {/* If editable is true, render input fields for totalPoints and firmPointBudget */}
        {editable ? (
          <>
            <TextField
              label="Total Points Available"
              type="number"
              value={String(totalPoints)}
              onChange={handleTotalPointsChange(onTotalPointsChange)}
              required
              fullWidth
              inputProps={{ min: 1, step: 1 }}
              helpText="Total points that can be allocated"
            />
            <TextField
              label="Firm Point Budget"
              type="number"
              value={String(firmPointBudget)}
              onChange={handleFirmPointBudgetChange(onFirmPointBudgetChange, totalPoints)}
              required
              fullWidth
              inputProps={{ min: 0, max: totalPoints, step: 1 }}
              helpText="Points allocated to the law firm"
            />
          </>
        ) : (
          <>
            {/* If editable is false, render read-only display with totalPoints, pointsUsed, and pointsRemaining */}
            <Box display="flex" justifyContent="space-between" alignItems="center">
              <Typography variant="body1">Total Points Available:</Typography>
              <Typography variant="body1">{totalPoints}</Typography>
            </Box>
            <Box display="flex" justifyContent="space-between" alignItems="center">
              <Typography variant="body1">Points Used:</Typography>
              <Typography variant="body1">{pointsUsed}</Typography>
            </Box>
            <Box display="flex" justifyContent="space-between" alignItems="center">
              <Typography variant="body1">Points Remaining:</Typography>
              <Typography variant="body1">{pointsRemaining}</Typography>
            </Box>
          </>
        )}

        {/* Include ProgressBar to visualize points used vs. total points */}
        <ProgressBar value={percentageUsed} color={statusColor} />

        {/* Add Tooltips with info icons to explain point budget concepts */}
        <Box display="flex" alignItems="center">
          <Tooltip title="Total points available for OCG negotiation">
            <InfoOutlined sx={{ mr: 1 }} />
          </Tooltip>
          <Typography variant="caption">Total Points Available</Typography>
        </Box>
        <Box display="flex" alignItems="center">
          <Tooltip title="Points currently used by the law firm">
            <InfoOutlined sx={{ mr: 1 }} />
          </Tooltip>
          <Typography variant="caption">Points Used</Typography>
        </Box>
        <Box display="flex" alignItems="center">
          <Tooltip title="Points remaining for the law firm to use">
            <InfoOutlined sx={{ mr: 1 }} />
          </Tooltip>
          <Typography variant="caption">Points Remaining</Typography>
        </Box>
      </Stack>
    </Card>
  );
};

/**
 * Helper function to determine the color to use based on the percentage of points remaining
 */
const getStatusColor = (pointsRemaining: number, totalPoints: number): string => {
  // Calculate percentage of points remaining (pointsRemaining / totalPoints * 100)
  const percentageRemaining = (pointsRemaining / totalPoints) * 100;

  // Return 'error' if percentage is less than 10%
  if (percentageRemaining < 10) {
    return 'error';
  }

  // Return 'warning' if percentage is less than 30%
  if (percentageRemaining < 30) {
    return 'warning';
  }

  // Return 'success' otherwise
  return 'success';
};

/**
 * Handles changes to the total points input when in editable mode
 */
const handleTotalPointsChange = (onTotalPointsChange?: (value: number) => void) => (event: React.ChangeEvent<HTMLInputElement>) => {
  // Parse input value to number
  const newValue = Number(event.target.value);

  // Validate that the number is positive and an integer
  if (newValue > 0 && Number.isInteger(newValue)) {
    // Call onTotalPointsChange prop with new value if valid
    onTotalPointsChange?.(newValue);
  }
};

/**
 * Handles changes to the firm point budget input when in editable mode
 */
const handleFirmPointBudgetChange = (onFirmPointBudgetChange?: (value: number) => void, totalPoints?: number) => (event: React.ChangeEvent<HTMLInputElement>) => {
  // Parse input value to number
  const newValue = Number(event.target.value);

  // Validate that the number is positive, an integer, and does not exceed total points
  if (newValue >= 0 && Number.isInteger(newValue) && newValue <= (totalPoints || 0)) {
    // Call onFirmPointBudgetChange prop with new value if valid
    onFirmPointBudgetChange?.(newValue);
  }
};

export default OCGPointBudget;