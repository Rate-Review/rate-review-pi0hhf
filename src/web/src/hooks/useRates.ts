import { useCallback, useMemo } from 'react'; //  ^18.0.0
import { useSelector, useDispatch } from 'react-redux'; //  ^8.0.0
import { toast } from 'react-toastify'; //  ^8.0.0
import {
  Rate,
  RateStatus,
  RateType,
  StaffClassRate,
  AttorneyRate,
  RateSubmission,
  CounterProposal,
  RateRule
} from '../types/rate';
import {
  RootState
} from '../store';
import {
  ratesSelectors,
  fetchRates,
  fetchRateById,
  submitRateProposal,
  submitCounterProposal,
  approveRate,
  rejectRate,
  updateRate
} from '../store/rates/ratesThunks';
import useOrganization from './useOrganizations';
import useAuth from './useAuth';
import usePermissions from './usePermissions';
import {
  calculateRateIncrease,
  formatRateAmount
} from '../utils/calculations';
import {
  formatCurrency,
  convertCurrency
} from '../utils/currency';
import {
  MAX_RATE_INCREASE,
  RATE_STATUSES,
  RATE_TYPES
} from '../constants/rates';

/**
 * Custom hook that provides functionality for managing attorney and staff class rates,
 * including fetching, submitting, updating, and counter-proposing rates.
 * Supports rate validation against client rules, currency handling, and permission-based operations.
 * @returns {object} An object containing rate data and functions for managing rates
 */
const useRates = () => {
  // LD1: Initialize Redux hooks for accessing store state and dispatching actions
  const dispatch = useDispatch();

  // LD1: Access organization context for current organization information
  const { currentOrganization } = useOrganization();

  // LD1: Access auth context for current user role (law firm or client)
  const { userRole } = useAuth();

  // LD1: Check user permissions for rate-related actions
  const { can } = usePermissions();

  // LD1: Select rate-related data from Redux store using selectors
  const rates = useSelector(ratesSelectors.selectRates);
  const loading = useSelector(ratesSelectors.selectRateStatus) === 'loading';
  const error = useSelector(ratesSelectors.selectRateError);

  // LD1: Define function for loading rates based on filters
  const loadRates = useCallback((filters: any = {}) => {
    dispatch(fetchRates(filters));
  }, [dispatch]);

  // LD1: Define function for loading attorney rates
  const loadAttorneyRates = useCallback((attorneyId: string) => {
    dispatch(fetchRates({ attorneyId }));
  }, [dispatch]);

  // LD1: Define function for loading staff class rates
  const loadStaffClassRates = useCallback((staffClassId: string) => {
    dispatch(fetchRates({ staffClassId }));
  }, [dispatch]);

  // LD1: Define function for submitting rate proposals
  const submitRateProposal = useCallback((submissionData: RateSubmission) => {
    dispatch(submitRateProposal(submissionData));
  }, [dispatch]);

  // LD1: Define function for submitting counter-proposals
  const submitCounterProposal = useCallback((counterProposal: CounterProposal) => {
    dispatch(submitCounterProposal(counterProposal));
  }, [dispatch]);

  // LD1: Define function for approving rates
  const approveRate = useCallback((rateId: string) => {
    dispatch(approveRate(rateId));
  }, [dispatch]);

  // LD1: Define function for rejecting rates
  const rejectRate = useCallback((rateId: string) => {
    dispatch(rejectRate(rateId));
  }, [dispatch]);

  // LD1: Define functions for rate calculations and formatting
  // These functions are imported from utils/calculations.ts and utils/currency.ts
  // LD1: Define function for validating rates against client rules
  const validateRate = useCallback((rate: Rate, rateRules: RateRule) => {
    // Implement rate validation logic here
    // This is a placeholder and needs to be adapted to your specific validation logic
    return true;
  }, []);

  // LD1: Define function for checking if rates can be edited based on status and permissions
  const canEditRate = useCallback((rate: Rate) => {
    // Implement permission checking logic here
    // This is a placeholder and needs to be adapted to your specific permission logic
    return true;
  }, []);

    const isLawFirm = useMemo(() => userRole === 'lawFirm', [userRole]);
    const isClient = useMemo(() => userRole === 'client', [userRole]);

  // LD1: Return object with rate data and functions
  return {
    rates,
    loading,
    error,
    loadRates,
    loadAttorneyRates,
    loadStaffClassRates,
    submitRateProposal,
    submitCounterProposal,
    approveRate,
    rejectRate,
    calculateRateIncrease,
    formatRateAmount,
    validateRate,
        convertCurrency,
        formatCurrency,
    canEditRate,
        isLawFirm,
        isClient
  };
};

export default useRates;