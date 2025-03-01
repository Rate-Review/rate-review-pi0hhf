import React, { useState, useCallback, useEffect } from 'react'; //  ^18.2.0
import { useDispatch, useSelector } from 'react-redux'; //  ^8.0.5
import styled from 'styled-components'; //  ^5.3.6

import Button from '../common/Button';
import TextField from '../common/TextField';
import Alert from '../common/Alert';
import RecommendationCard from '../ai/RecommendationCard';

import { RateInterface } from '../../types/rate';
import { selectRateRules } from '../../store/rates/ratesSlice';
import { calculatePercentChange } from '../../utils/calculations';
import { formatCurrency } from '../../utils/formatting';

// LD1: Define interface for CounterProposalForm props
interface CounterProposalFormProps {
  rate: RateInterface;
  currentRate: number;
  proposedRate: number;
  negotiationId: string;
  onSubmit: (rate: RateInterface, counterRate: number, message: string) => void;
  onCancel: () => void;
  recommendedRate?: number;
  currency: string;
}

// Styled Components for layout and styling
const FormContainer = styled.div`
  padding: 24px;
  display: flex;
  flex-direction: column;
  gap: 16px;
`;

const RateInfoContainer = styled.div`
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin-bottom: 16px;
`;

const RateRow = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
`;

const RateLabel = styled.span`
  font-weight: 500;
  color: ${props => props.theme.colors.neutral};
`;

const RateValue = styled.span`
  font-weight: 500;
`;

interface PercentageChangeProps {
  increase: number;
}

const PercentageChange = styled.span<PercentageChangeProps>`
  font-size: 14px;
  margin-left: 8px;
  color: ${props => props.increase > 0 ? props.theme.colors.error : props.theme.colors.success};
`;

const InputContainer = styled.div`
  margin-bottom: 16px;
`;

const ActionContainer = styled.div`
  display: flex;
  justify-content: flex-end;
  gap: 16px;
  margin-top: 24px;
`;

const RecommendationContainer = styled.div`
  margin-top: 16px;
  margin-bottom: 16px;
`;

// LD1: Define CounterProposalForm functional component
const CounterProposalForm: React.FC<CounterProposalFormProps> = ({
  rate,
  currentRate,
  proposedRate,
  negotiationId,
  onSubmit,
  onCancel,
  recommendedRate,
  currency
}) => {
  // LD1: Initialize state for counter rate value and message
  const [counterRate, setCounterRate] = useState<number>(recommendedRate || proposedRate);
  const [message, setMessage] = useState<string>('');
  const [error, setError] = useState<string | null>(null);

  // LD1: Access rate rules from Redux store
  const rateRules = useSelector(selectRateRules);

  // LD1: Calculate percentage change between counter rate and current rate
  const percentChange = calculatePercentChange(currentRate, counterRate);

  // LD1: Validate counter rate against client rules
  const validateCounterRate = useCallback((counterRate: number, currentRate: number, rateRules: any) => {
    if (isNaN(counterRate) || counterRate <= 0) {
      return { valid: false, errorMessage: 'Counter rate must be a valid positive number' };
    }

    const percentageChange = ((counterRate - currentRate) / currentRate) * 100;
    if (rateRules && rateRules.maxIncreasePercent && percentageChange > rateRules.maxIncreasePercent) {
      return { valid: false, errorMessage: `Counter rate exceeds maximum allowed increase of ${rateRules.maxIncreasePercent}%` };
    }

    return { valid: true, errorMessage: null };
  }, []);

  // LD1: Handle counter rate change
  const handleCounterRateChange = useCallback((event: React.ChangeEvent<HTMLInputElement>) => {
    const newValue = parseFloat(event.target.value);
    setCounterRate(newValue);

    const validationResult = validateCounterRate(newValue, currentRate, rateRules);
    if (!validationResult.valid) {
      setError(validationResult.errorMessage);
    } else {
      setError(null);
    }
  }, [currentRate, rateRules, validateCounterRate]);

  // LD1: Handle message change
  const handleMessageChange = useCallback((event: React.ChangeEvent<HTMLInputElement>) => {
    setMessage(event.target.value);
  }, []);

  // LD1: Handle form submission
  const handleSubmit = useCallback((event: React.FormEvent) => {
    event.preventDefault();

    const validationResult = validateCounterRate(counterRate, currentRate, rateRules);
    if (validationResult.valid) {
      onSubmit(rate, counterRate, message);
    } else {
      setError(validationResult.errorMessage);
    }
  }, [counterRate, currentRate, rate, rateRules, onSubmit, validateCounterRate, message]);

  // LD1: Handle use recommendation
  const handleUseRecommendation = useCallback(() => {
    if (recommendedRate) {
      setCounterRate(recommendedRate);
      setError(null);
    }
  }, [recommendedRate]);

  // LD1: Render the form
  return (
    <FormContainer>
      <RateInfoContainer>
        <RateRow>
          <RateLabel>Current Rate:</RateLabel>
          <RateValue>{formatCurrency(currentRate, currency)}</RateValue>
        </RateRow>
        <RateRow>
          <RateLabel>Proposed Rate:</RateLabel>
          <RateValue>{formatCurrency(proposedRate, currency)}</RateValue>
        </RateRow>
      </RateInfoContainer>

      <InputContainer>
        <TextField
          label="Counter Rate"
          type="number"
          value={counterRate}
          onChange={handleCounterRateChange}
          error={error}
          fullWidth
        />
        {percentChange !== null && (
          <PercentageChange increase={percentChange}>
            ({percentChange > 0 ? '+' : ''}{percentChange.toFixed(2)}%)
          </PercentageChange>
        )}
      </InputContainer>

      <InputContainer>
        <TextField
          label="Message"
          type="text"
          placeholder="Enter justification for counter-proposal"
          value={message}
          onChange={handleMessageChange}
          fullWidth
        />
      </InputContainer>

      {recommendedRate && (
        <RecommendationContainer>
          <RecommendationCard
            recommendation={{
              id: 'recommendation-1',
              type: 'COUNTER',
              value: recommendedRate,
              rationale: 'This rate aligns with market standards and client budget',
              confidence: 0.8,
              relatedRates: []
            }}
            onApply={handleUseRecommendation}
            onDismiss={() => { }}
            onViewExplanation={() => { }}
          />
        </RecommendationContainer>
      )}

      {error && <Alert severity="error" message={error} />}

      <ActionContainer>
        <Button onClick={onCancel}>Cancel</Button>
        <Button variant="primary" onClick={handleSubmit}>Submit</Button>
      </ActionContainer>
    </FormContainer>
  );
};

// IE3: Be generous about your exports so long as it doesn't create a security risk.
export default CounterProposalForm;