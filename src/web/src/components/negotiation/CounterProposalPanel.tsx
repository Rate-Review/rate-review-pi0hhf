import React, { useState, useCallback, useEffect, useMemo } from 'react'; //  ^18.0.0
import { useSelector, useDispatch } from 'react-redux'; // ^8.0.0
import {
  Box,
  Grid,
  Typography,
  Divider,
  Paper
} from '@mui/material'; //  5.14.0
import Button from '../common/Button';
import TextField from '../common/TextField';
import Alert from '../common/Alert';
import RecommendationCard from '../ai/RecommendationCard';
import { RateType, RateWithDetails } from '../../types/rate';
import { NegotiationType } from '../../types/negotiation';
import { counterProposeRates } from '../../store/negotiations/negotiationsThunks';
import useAI from '../../hooks/useAI';
import { calculatePercentage } from '../../utils/calculations';
import { formatCurrency } from '../../utils/formatting';
import { validateRateValue } from '../../utils/validation';
import { CounterProposalPanelProps } from '../../types/index';

/**
 * A component for displaying and submitting counter-proposals during rate negotiations
 */
const CounterProposalPanel: React.FC<CounterProposalPanelProps> = ({
  rates,
  negotiationId,
  isRealTimeMode,
  readOnly,
  onSubmit,
  onCancel,
}) => {
  // LD1: Initialize state for counter-proposal values, justification text, errors, and loading state
  const [counterProposalValues, setCounterProposalValues] = useState<Record<string, number>>({});
  const [justification, setJustification] = useState<string>('');
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [isSubmitting, setIsSubmitting] = useState<boolean>(false);
  const [aiRecommendations, setAiRecommendations] = useState<Record<string, number>>({});
  const [showRecommendations, setShowRecommendations] = useState<boolean>(false);

  // LD1: Fetch AI recommendations using the useAI hook when rates change
  const { getRateRecommendations } = useAI();

  // LD1: Calculate percentage changes between original and counter-proposal values
  const percentageChanges = useMemo(() => {
    const changes: Record<string, number> = {};
    rates.forEach(rate => {
      const originalRate = rate.amount;
      const counterRate = counterProposalValues[rate.id] || originalRate;
      changes[rate.id] = calculatePercentage(originalRate, counterRate);
    });
    return changes;
  }, [rates, counterProposalValues]);

  // LD1: Handle input changes for counter-proposal values and justification
  const handleValueChange = (rateId: string, value: number) => {
    setCounterProposalValues(prevValues => ({
      ...prevValues,
      [rateId]: value,
    }));
  };

  const handleJustificationChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    setJustification(event.target.value);
  };

  // LD1: Validate inputs based on business rules
  const validateForm = useCallback(() => {
    const newErrors: Record<string, string> = {};
    rates.forEach(rate => {
      const value = counterProposalValues[rate.id] || rate.amount;
      if (!validateRateValue(value)) {
        newErrors[rate.id] = 'Invalid rate value';
      }
    });
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  }, [counterProposalValues, rates, validateRateValue]);

  // LD1: Submit counter-proposals to the Redux store
  const dispatch = useDispatch();
  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    if (!validateForm()) {
      return;
    }

    setIsSubmitting(true);
    try {
      const counterProposals = rates.map(rate => ({
        rateId: rate.id,
        amount: counterProposalValues[rate.id] || rate.amount,
        message: justification,
      }));
      await dispatch(counterProposeRates(counterProposals) as any).unwrap();
      onSubmit();
    } catch (error: any) {
      console.error('Failed to submit counter-proposals:', error);
      // Handle error appropriately (e.g., display an error message)
    } finally {
      setIsSubmitting(false);
    }
  };

  // LD1: Render the counter-proposal form with inputs for each rate
  return (
    <Paper elevation={3} style={{ padding: '16px', marginBottom: '16px' }}>
      <Typography variant="h6" gutterBottom>
        Enter Counter-Proposals
      </Typography>
      <form onSubmit={handleSubmit}>
        <Grid container spacing={2}>
          {rates.map(rate => (
            <Grid item xs={12} sm={6} key={rate.id}>
              <TextField
                label={rate.attorneyName}
                type="number"
                value={counterProposalValues[rate.id] !== undefined ? counterProposalValues[rate.id] : rate.amount}
                onChange={(e) => handleValueChange(rate.id, parseFloat(e.target.value))}
                error={errors[rate.id]}
                disabled={readOnly}
                helperText={
                  percentageChanges[rate.id] !== undefined
                    ? `Change: ${percentageChanges[rate.id].toFixed(2)}%`
                    : ''
                }
              />
            </Grid>
          ))}
          <Grid item xs={12}>
            <TextField
              label="Justification"
              multiline
              rows={4}
              fullWidth
              value={justification}
              onChange={handleJustificationChange}
              disabled={readOnly}
            />
          </Grid>
        </Grid>
        <Box mt={2} display="flex" justifyContent="flex-end">
          <Button onClick={onCancel} disabled={isSubmitting}>
            Cancel
          </Button>
          <Button type="submit" variant="contained" color="primary" disabled={isSubmitting}>
            Submit
          </Button>
        </Box>
      </form>
    </Paper>
  );
};

export default CounterProposalPanel;