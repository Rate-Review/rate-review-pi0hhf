import { useCallback, useEffect, useMemo, useState } from 'react'; //  ^18.2.0
import { useDispatch, useSelector } from 'react-redux'; // ^8.0.5
import { useToast } from '@chakra-ui/react'; // ^2.0.0
import {
  Negotiation,
  NegotiationStatus,
  Rate,
  CounterProposal,
  BulkNegotiationAction,
  NegotiationFilters,
} from '../types/negotiation';
import { RootState } from '../store';
import {
  fetchNegotiations,
  fetchNegotiationById,
  updateNegotiationStatus,
  submitCounterProposal,
  approveRate,
  rejectRate,
  submitBulkAction,
  sendMessage,
} from '../store/negotiations/negotiationsThunks';
import {
  selectNegotiations,
  selectNegotiationById,
  selectNegotiationStatus,
  selectNegotiationRates,
  selectNegotiationLoading,
  selectNegotiationError,
  selectNegotiationMessages,
} from '../store/negotiations/negotiationsSlice';
import { calculateRateImpact } from '../utils/calculations';
import useAI from './useAI';
import usePermissions from './usePermissions';

/**
 * A custom React hook that provides functions and state for managing rate negotiations
 * @param   {object} options - Object containing negotiation state and functions for interacting with negotiations
 * @returns {object} Object containing negotiation state and functions for interacting with negotiations
 */
const useNegotiations = (options: any = {}) => {
  // LD1: Initialize local state for selected rates, real-time mode, and filter criteria
  const [selectedRates, setSelectedRates] = useState<string[]>([]);
  const [realTimeMode, setRealTimeMode] = useState(false);
  const [filters, setFilters] = useState<NegotiationFilters>({
    status: [],
    type: [],
    clientId: '',
    firmId: '',
    startDate: '',
    endDate: '',
    search: '',
    sortBy: '',
    sortDirection: '',
    page: 1,
    pageSize: 10,
  });

  // LD1: Get dispatch function from Redux
  const dispatch = useDispatch();

  // LD1: Select negotiation state from Redux store using selectors
  const negotiations = useSelector((state: RootState) => selectNegotiations(state));
  const negotiation = useSelector((state: RootState) => selectNegotiationById(state, options.negotiationId));
  const negotiationStatus = useSelector((state: RootState) => selectNegotiationStatus(state, options.negotiationId));
  const negotiationRates = useSelector((state: RootState) => selectNegotiationRates(state, options.negotiationId));
  const negotiationLoading = useSelector((state: RootState) => selectNegotiationLoading(state));
  const negotiationError = useSelector((state: RootState) => selectNegotiationError(state));
    const negotiationMessages = useSelector((state: RootState) => selectNegotiationMessages(state, options.negotiationId));

  // LD1: Get AI recommendation functions from useAI hook
  const { getRateRecommendations } = useAI();

  // LD1: Get user permissions from usePermissions hook
  const { can } = usePermissions();

  // LD1: Define function for fetching negotiations with optional filters
  const fetchNegotiationsData = useCallback(
    (newFilters?: NegotiationFilters) => {
      const mergedFilters = { ...filters, ...newFilters };
      dispatch(fetchNegotiations(mergedFilters));
    },
    [dispatch, filters]
  );

  // LD1: Define function for fetching a single negotiation by ID
  const fetchSingleNegotiation = useCallback(
    (negotiationId: string) => {
      dispatch(fetchNegotiationById(negotiationId));
    },
    [dispatch]
  );

  // LD1: Define function for updating negotiation status
  const updateStatus = useCallback(
    (negotiationId: string, status: NegotiationStatus) => {
      dispatch(updateNegotiationStatus({ id: negotiationId, status }));
    },
    [dispatch]
  );

  // LD1: Define function for submitting a counter-proposal for a rate
  const submitCounter = useCallback(
    (negotiationId: string, rateId: string, counterAmount: number, message: string) => {
      const counterProposal: SubmitCounterProposalRequest = {
        negotiationId,
        rateId,
        counterAmount,
        message,
      };
      dispatch(submitCounterProposal(counterProposal));
    },
    [dispatch]
  );

  // LD1: Define function for approving a rate
  const approve = useCallback(
    (negotiationId: string, rateId: string, message: string) => {
      const approvalData: NegotiationApprovalRequest = {
        negotiationId,
        rateId,
        message,
      };
      dispatch(approveRate(approvalData));
    },
    [dispatch]
  );

  // LD1: Define function for rejecting a rate
  const reject = useCallback(
    (negotiationId: string, rateId: string, message: string) => {
      dispatch(rejectRate({ rateId, rejectionData: { message } }));
    },
    [dispatch]
  );

  // LD1: Define function for applying bulk actions to multiple rates
  const submitBulk = useCallback(
    (negotiationId: string, action: string, rateIds: string[], message: string, counterAmounts: Record<string, number>) => {
      const bulkAction: BulkNegotiationAction = {
        negotiationId,
        action,
        rateIds,
        message,
        counterAmounts,
      };
      dispatch(submitBulkAction(bulkAction));
    },
    [dispatch]
  );

  // LD1: Define function for toggling real-time mode
  const toggleRealTime = useCallback(() => {
    setRealTimeMode((prev) => !prev);
  }, []);

  // LD1: Define function for selecting/deselecting rates
  const selectRate = useCallback((rateId: string) => {
    setSelectedRates((prevSelected) =>
      prevSelected.includes(rateId)
        ? prevSelected.filter((id) => id !== rateId)
        : [...prevSelected, rateId]
    );
  }, []);

  // LD1: Define function for calculating rate impact
  const calculateImpact = useCallback(() => {
    // TODO: Implement calculate rate impact logic
  }, []);

  // LD1: Define function for getting AI recommendations for rates
  const getAIRecommendationsForRate = useCallback((rateId: string) => {
    // TODO: Implement get AI recommendations for rates logic
  }, []);

    // LD1: Define function for sending messages within a negotiation
    const sendNegotiationMessage = useCallback((negotiationId: string, content: string, recipientIds: string[]) => {
        dispatch(sendMessage({ negotiationId, content, recipientIds }));
    }, [dispatch]);

  // LD1: Define function for checking if current user can approve rates based on approval workflow
  const canApproveRates = useCallback(() => {
    // TODO: Implement can approve rates logic
  }, []);

  // LD1: Define function for getting negotiation history
  const getNegotiationHistory = useCallback(() => {
    // TODO: Implement get negotiation history logic
  }, []);

  // LD1: Use useEffect to fetch negotiation data based on options
  useEffect(() => {
    if (options.fetchOnMount) {
      fetchNegotiationsData();
    }
  }, [fetchNegotiationsData, options.fetchOnMount]);

  // LD1: Use useEffect to check for real-time updates if realTimeMode is enabled
  useEffect(() => {
    if (realTimeMode) {
      // TODO: Implement real-time update logic
    }
  }, [realTimeMode]);

  // LD1: Return object with negotiation state and all interaction functions
  return {
    negotiations,
    negotiation,
    negotiationStatus,
    negotiationRates,
    negotiationLoading,
    negotiationError,
      negotiationMessages,
    selectedRates,
    realTimeMode,
    filters,
    fetchNegotiations: fetchNegotiationsData,
    fetchNegotiation: fetchSingleNegotiation,
    updateNegotiationStatus: updateStatus,
    submitCounterProposal: submitCounter,
    approveRate: approve,
    rejectRate: reject,
    submitBulkAction: submitBulk,
    toggleRealTime: toggleRealTime,
    selectRate: selectRate,
    calculateRateImpact: calculateImpact,
    getAIRecommendationsForRate: getAIRecommendationsForRate,
      sendNegotiationMessage,
    canApproveRates,
    getNegotiationHistory,
  };
};

/**
 * Internal function to filter negotiations based on criteria
 * @param   {array} negotiations - Filtered negotiations array
 * @param   {object} filters - Filtered negotiations array
 * @returns {array} Filtered negotiations array
 */
const getFilteredNegotiations = (negotiations: Negotiation[], filters: NegotiationFilters): Negotiation[] => {
  let filtered = [...negotiations];

  // Apply status filter if present
  if (filters.status && filters.status.length > 0) {
    filtered = filtered.filter((negotiation) => filters.status.includes(negotiation.status));
  }

  // Apply date range filter if present
  if (filters.startDate && filters.endDate) {
    filtered = filtered.filter((negotiation) => {
      const startDate = new Date(filters.startDate);
      const endDate = new Date(filters.endDate);
      const requestDate = new Date(negotiation.requestDate);
      return requestDate >= startDate && requestDate <= endDate;
    });
  }

  // Apply firm/client filter if present
  if (filters.firmId) {
    filtered = filtered.filter((negotiation) => negotiation.firmId === filters.firmId);
  }
  if (filters.clientId) {
    filtered = filtered.filter((negotiation) => negotiation.clientId === filters.clientId);
  }

  // Apply search term filter if present
  if (filters.search) {
    filtered = filtered.filter((negotiation) => {
      const searchTerm = filters.search.toLowerCase();
      return (
        negotiation.firm.name.toLowerCase().includes(searchTerm) ||
        negotiation.client.name.toLowerCase().includes(searchTerm)
      );
    });
  }

  return filtered;
};

export default useNegotiations;