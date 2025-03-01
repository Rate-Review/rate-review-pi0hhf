import React, { useState, useEffect } from 'react'; //  ^18.2.0
import { useDispatch } from 'react-redux'; // ^8.0.5
import { toast } from 'react-toastify'; // ^9.1.1
import Card from '../common/Card';
import Button from '../common/Button';
import TextField from '../common/TextField';
import Select from '../common/Select';
import {
  bulkApproveRates,
  bulkRejectRates,
  bulkCounterRates,
} from '../../store/rates/ratesThunks';
import { calculatePercentChange } from '../../utils/calculations';
import { Rate, RateAction, BulkActionPanelProps } from '../../types/rate';

/**
 * Component for applying bulk actions to selected rates in a negotiation
 */
const BulkActionPanel: React.FC<BulkActionPanelProps> = ({
  selectedRates,
  selectedRateIds,
  negotiationId,
  onClose,
  isClient,
}) => {
  // Initialize Redux dispatch
  const dispatch = useDispatch();

  // Set up state for selectedAction, counterRates, percentChanges, message, and isSubmitting
  const [selectedAction, setSelectedAction] = useState<RateAction | ''>('');
  const [counterRates, setCounterRates] = useState<Record<string, string>>({});
  const [percentChanges, setPercentChanges] = useState<Record<string, number>>({});
  const [message, setMessage] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  // Initialize counterRates and percentChanges when selectedRates change
  useEffect(() => {
    const initialCounterRates: Record<string, string> = {};
    const initialPercentChanges: Record<string, number> = {};

    selectedRates.forEach((rate) => {
      initialCounterRates[rate.id] = rate.amount.toString();
      initialPercentChanges[rate.id] = 0;
    });

    setCounterRates(initialCounterRates);
    setPercentChanges(initialPercentChanges);
  }, [selectedRates]);

  /**
   * Handles changes to the selected bulk action dropdown
   * @param {React.ChangeEvent<HTMLSelectElement>} event
   * @returns {void} No return value
   */
  const handleActionChange = (event: React.ChangeEvent<HTMLSelectElement>) => {
    // Get the new action value from event.target.value
    const newAction = event.target.value as RateAction | '';

    // Update the selectedAction state
    setSelectedAction(newAction);

    // Reset counterRates and percentChanges if the action is not COUNTER
    if (newAction !== 'COUNTER_PROPOSE') {
      setCounterRates({});
      setPercentChanges({});
    }
  };

  /**
   * Handles changes to individual counter rate values
   * @param {string} rateId
   * @param {React.ChangeEvent<HTMLInputElement>} event
   * @returns {void} No return value
   */
  const handleCounterRateChange = (rateId: string, event: React.ChangeEvent<HTMLInputElement>) => {
    // Get the new rate value from event.target.value
    const newRateValue = event.target.value;

    // Update the counterRates state with the new value for the specific rate
    setCounterRates((prevCounterRates) => ({
      ...prevCounterRates,
      [rateId]: newRateValue,
    }));

    // Find the current rate object from selectedRates using rateId
    const currentRate = selectedRates.find((rate) => rate.id === rateId);

    if (currentRate) {
      // Calculate percentage change between original rate and counter rate
      const originalRate = currentRate.amount;
      const counterRate = parseFloat(newRateValue);
      const percentageChange = calculatePercentChange(originalRate, counterRate);

      // Update percentChanges state with the calculated value
      setPercentChanges((prevPercentChanges) => ({
        ...prevPercentChanges,
        [rateId]: percentageChange,
      }));
    }
  };

  /**
   * Handles changes to the message textarea
   * @param {React.ChangeEvent<HTMLInputElement>} event
   * @returns {void} No return value
   */
  const handleMessageChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    // Get the new message value from event.target.value
    const newMessage = event.target.value;

    // Update the message state
    setMessage(newMessage);
  };

  /**
   * Validates counter rates to ensure they are valid numbers
   * @returns {boolean} True if all counter rates are valid
   */
  const validateCounterRates = (): boolean => {
    for (const rateId in counterRates) {
      if (!counterRates.hasOwnProperty(rateId)) continue;
      const counterRate = counterRates[rateId];

      // Check if any counterRate is empty or not numeric
      if (!counterRate || isNaN(Number(counterRate))) {
        toast.error('Please enter valid counter rates.');
        return false;
      }

      // Check if any counterRate is negative or zero
      if (Number(counterRate) <= 0) {
        toast.error('Counter rates must be greater than zero.');
        return false;
      }
    }

    // Return true if all counter rates are valid
    return true;
  };

  /**
   * Handles form submission for the bulk action
   * @param {React.FormEvent<HTMLFormElement>} event
   * @returns {void} No return value
   */
  const handleSubmit = (event: React.FormEvent<HTMLFormElement>) => {
    // Prevent default form submission behavior
    event.preventDefault();

    // Set isSubmitting state to true
    setIsSubmitting(true);

    if (selectedAction === 'APPROVE') {
      // For APPROVE action: dispatch bulkApproveRates with selectedRateIds, negotiationId, and message
      dispatch(
        bulkApproveRates({
          rateIds: selectedRateIds,
          approvalData: { message },
        })
      )
        .then(() => {
          // Show success toast notification on successful dispatch
          toast.success('Rates approved successfully!');
        })
        .catch(() => {
          // Show error toast notification if dispatch fails
          toast.error('Failed to approve rates. Please try again.');
        })
        .finally(() => {
          // Set isSubmitting state to false
          setIsSubmitting(false);

          // Call onClose to close the panel
          onClose();
        });
    } else if (selectedAction === 'REJECT') {
      // For REJECT action: dispatch bulkRejectRates with selectedRateIds, negotiationId, and message
      dispatch(
        bulkRejectRates({
          rateIds: selectedRateIds,
          rejectionData: { message },
        })
      )
        .then(() => {
          // Show success toast notification on successful dispatch
          toast.success('Rates rejected successfully!');
        })
        .catch(() => {
          // Show error toast notification if dispatch fails
          toast.error('Failed to reject rates. Please try again.');
        })
        .finally(() => {
          // Set isSubmitting state to false
          setIsSubmitting(false);

          // Call onClose to close the panel
          onClose();
        });
    } else if (selectedAction === 'COUNTER_PROPOSE') {
      // For COUNTER action: validate counter rates, then dispatch bulkCounterRates with selectedRateIds, counterRates, negotiationId, and message
      if (validateCounterRates()) {
        const counterProposals = selectedRateIds.map((rateId) => ({
          rateId,
          amount: parseFloat(counterRates[rateId]),
          message: message,
        }));

        dispatch(bulkCounterRates(counterProposals))
          .then(() => {
            // Show success toast notification on successful dispatch
            toast.success('Rates counter-proposed successfully!');
          })
          .catch(() => {
            // Show error toast notification if dispatch fails
            toast.error('Failed to counter-propose rates. Please try again.');
          })
          .finally(() => {
            // Set isSubmitting state to false
            setIsSubmitting(false);

            // Call onClose to close the panel
            onClose();
          });
      } else {
        setIsSubmitting(false);
      }
    }
  };

  // Render Card component containing the form
  return (
    <Card>
      <form onSubmit={handleSubmit}>
        {/* Render Select dropdown for action selection */}
        <Select
          name="bulkAction"
          label="Select Action"
          value={selectedAction}
          onChange={handleActionChange}
          options={[
            { value: 'APPROVE', label: 'Approve Selected' },
            { value: 'REJECT', label: 'Reject Selected' },
            { value: 'COUNTER_PROPOSE', label: 'Counter Propose Selected' },
          ]}
          required
        />

        {/* Conditionally render counter rate inputs when COUNTER action is selected */}
        {selectedAction === 'COUNTER_PROPOSE' && (
          <div>
            {selectedRates.map((rate) => (
              <TextField
                key={rate.id}
                label={`Counter Rate for ${rate.attorneyName}`}
                type="number"
                value={counterRates[rate.id] || ''}
                onChange={(event) => handleCounterRateChange(rate.id, event)}
                placeholder="Enter counter rate"
                required
              />
            ))}
          </div>
        )}

        {/* Render TextField for message input */}
        <TextField
          label="Message"
          placeholder="Enter message"
          value={message}
          onChange={handleMessageChange}
          multiline
          rows={4}
        />

        {/* Render action buttons (Cancel and Submit) */}
        <Button onClick={onClose} disabled={isSubmitting}>
          Cancel
        </Button>
        <Button type="submit" variant="primary" disabled={isSubmitting}>
          {isSubmitting ? 'Submitting...' : 'Submit'}
        </Button>
      </form>
    </Card>
  );
};

export default BulkActionPanel;