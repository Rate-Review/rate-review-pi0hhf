import { useCallback, useEffect, useState } from 'react'; //  ^18.0.0
import { useAppDispatch, useAppSelector } from '../store';
import {
  fetchOCGs,
  fetchOCGById,
  createOCG,
  updateOCG,
  deleteOCG,
  submitOCGNegotiation,
  respondToOCGNegotiation,
  finalizeOCG,
} from '../store/ocg/ocgThunks';
import {
  ocgSlice,
  selectOCGs,
  selectCurrentOCG,
  selectOCGLoading,
  selectOCGErrors,
  selectOCGById,
  selectTotalPointsUsed,
  selectPointsRemaining,
} from '../store/ocg/ocgSlice';
import {
  OCGDocument,
  OCGSection,
  OCGAlternative,
  OCGNegotiation,
  OCGFirmSelection,
  CreateOCGRequest,
  UpdateOCGRequest,
  StartOCGNegotiationRequest,
  SubmitOCGSelectionsRequest,
} from '../types/ocg';
import ocgService from '../services/ocg';
import { useAuth } from './useAuth';
import { useOrganizations } from './useOrganizations';
import { canPerformAction } from '../utils/permissions';

/**
 * Custom hook for managing Outside Counsel Guidelines (OCGs) within the application
 * @returns Object containing OCG state and functions for OCG management
 */
export const useOCG = () => {
  // Get authenticated user and org information using useAuth
  const { currentUser } = useAuth();

  // Get organization information using useOrganizations
  const { currentOrganization } = useOrganizations();

  // Get Redux dispatch function and selectors for OCG state
  const dispatch = useAppDispatch();
  const ocgs = useAppSelector(selectOCGs);
  const currentOCG = useAppSelector(selectCurrentOCG);
  const loading = useAppSelector(selectOCGLoading);
  const errors = useAppSelector(selectOCGErrors);

  // Define state for version history and document generation
  const [versionHistory, setVersionHistory] = useState<any[]>([]);
  const [documentGenerating, setDocumentGenerating] = useState(false);

  // Define getOCGs function to fetch and filter OCGs
  const getOCGs = useCallback(() => {
    dispatch(fetchOCGs({}));
  }, [dispatch]);

  // Define getOCGById function to fetch a specific OCG
  const getOCGById = useCallback((id: string) => {
    dispatch(fetchOCGById(id));
  }, [dispatch]);

  // Define createOCG function to create a new OCG
  const createOCG = useCallback((ocgData: CreateOCGRequest) => {
    return dispatch(createOCG(ocgData)) as any;
  }, [dispatch]);

  // Define updateOCG function to update an existing OCG
  const updateOCG = useCallback((id: string, ocgData: UpdateOCGRequest) => {
    return dispatch(updateOCG({ id, ocgData })) as any;
  }, [dispatch]);

  // Define deleteOCG function to delete an OCG
  const deleteOCG = useCallback((id: string) => {
    dispatch(deleteOCG(id));
  }, [dispatch]);

  // Define setCurrentOCG function to set the active OCG
  const setCurrentOCG = useCallback((ocg: OCGDocument) => {
    dispatch(ocgSlice.actions.setCurrentOCG(ocg));
  }, [dispatch]);

  // Define clearCurrentOCG function to clear the active OCG
  const clearCurrentOCG = useCallback(() => {
    dispatch(ocgSlice.actions.clearCurrentOCG());
  }, [dispatch]);

  // Define addSection function to add a section to an OCG
  const addSection = useCallback((section: OCGSection) => {
    dispatch(ocgSlice.actions.addSection(section));
  }, [dispatch]);

  // Define updateSection function to update a section
  const updateSection = useCallback((sectionId: string, updates: Partial<OCGSection>) => {
    dispatch(ocgSlice.actions.updateSection({ sectionId, updates }));
  }, [dispatch]);

  // Define removeSection function to remove a section
  const removeSection = useCallback((sectionId: string) => {
    dispatch(ocgSlice.actions.removeSection(sectionId));
  }, [dispatch]);

  // Define reorderSections function to reorder sections
  const reorderSections = useCallback((sectionIds: string[]) => {
    dispatch(ocgSlice.actions.reorderSections(sectionIds));
  }, [dispatch]);

  // Define addAlternative function to add an alternative to a section
  const addAlternative = useCallback((sectionId: string, alternative: OCGAlternative) => {
    dispatch(ocgSlice.actions.addAlternative({ sectionId, alternative }));
  }, [dispatch]);

  // Define updateAlternative function to update an alternative
  const updateAlternative = useCallback((sectionId: string, alternativeId: string, updates: Partial<OCGAlternative>) => {
    dispatch(ocgSlice.actions.updateAlternative({ sectionId, alternativeId, updates }));
  }, [dispatch]);

  // Define removeAlternative function to remove an alternative
  const removeAlternative = useCallback((sectionId: string, alternativeId: string) => {
    dispatch(ocgSlice.actions.removeAlternative({ sectionId, alternativeId }));
  }, [dispatch]);

  // Define setTotalPoints function to set total points for an OCG
  const setTotalPoints = useCallback((totalPoints: number) => {
    dispatch(ocgSlice.actions.setTotalPoints(totalPoints));
  }, [dispatch]);

  // Define setDefaultPointBudget function to set default point budget
  const setDefaultPointBudget = useCallback((defaultPointBudget: number) => {
    dispatch(ocgSlice.actions.setDefaultPointBudget(defaultPointBudget));
  }, [dispatch]);

   // Define startNegotiation function to start OCG negotiation with a firm
  const startNegotiation = useCallback((negotiationData: StartOCGNegotiationRequest) => {
    return dispatch(submitOCGNegotiation(negotiationData)) as any;
  }, [dispatch]);

  // Define submitSelections function for law firms to submit selections
  const submitSelections = useCallback((selectionsData: SubmitOCGSelectionsRequest) => {
    return dispatch(submitOCGNegotiation(selectionsData)) as any;
  }, [dispatch]);

  // Define approveSelections function for clients to approve firm selections
  const approveSelections = useCallback((negotiationId: string, comments?: string) => {
    return dispatch(respondToOCGNegotiation({ negotiationId, approved: true, comments })) as any;
  }, [dispatch]);

  // Define rejectSelections function for clients to reject firm selections
  const rejectSelections = useCallback((negotiationId: string, feedback: string) => {
    return dispatch(respondToOCGNegotiation({ negotiationId, approved: false, feedback })) as any;
  }, [dispatch]);

  // Define selectAlternative function to record alternative selection
  const selectAlternative = useCallback((firmId: string, sectionId: string, alternativeId: string) => {
    dispatch(ocgSlice.actions.selectAlternative({ firmId, sectionId, alternativeId }));
  }, [dispatch]);

  // Define getPointsUsed function to calculate points used by a firm
  const getPointsUsed = useCallback((firmId: string) => {
    return useAppSelector(() => selectTotalPointsUsed(firmId));
  }, []);

  // Define getPointsRemaining function to calculate remaining points
  const getPointsRemaining = useCallback((firmId: string) => {
    return useAppSelector(() => selectPointsRemaining(firmId));
  }, []);

  // Define finalizeOCGDocument function to finalize an OCG
  const finalizeOCG = useCallback((id: string) => {
    return dispatch(finalizeOCG(id)) as any;
  }, [dispatch]);

  // Define generateDocument function to generate OCG document in different formats
  const generateDocument = useCallback(async (ocgId: string, format: 'pdf' | 'docx') => {
    setDocumentGenerating(true);
    try {
      const document = await ocgService.generateOCGDocument(ocgId, { format });
      return document;
    } catch (error) {
      console.error('Error generating document:', error);
      throw error;
    } finally {
      setDocumentGenerating(false);
    }
  }, []);

  // Define downloadDocument function to download OCG document
  const downloadDocument = useCallback(async (ocgId: string, format: 'pdf' | 'docx', filename: string) => {
    try {
      await ocgService.downloadOCGDocument(ocgId, format, filename);
    } catch (error) {
      console.error('Error downloading document:', error);
      throw error;
    }
  }, []);

  // Define signDocument function to electronically sign an OCG
  const signDocument = useCallback(async (ocgId: string, name: string, title: string, date: string) => {
    try {
      const signedDocument = await ocgService.signOCG(ocgId, { name, title, date });
      return signedDocument;
    } catch (error) {
      console.error('Error signing document:', error);
      throw error;
    }
  }, []);

  // Define getVersionHistory function to get OCG version history
  const getVersionHistory = useCallback(async (ocgId: string) => {
    try {
      const history = await ocgService.getOCGVersionHistory(ocgId);
      setVersionHistory(history);
      return history;
    } catch (error) {
      console.error('Error getting version history:', error);
      throw error;
    }
  }, []);

  // Check user permissions to determine available actions
  const canCreate = canPerformAction(currentUser, 'create', 'ocg', 'organization');
  const canEdit = canPerformAction(currentUser, 'update', 'ocg', 'organization');
  const canDelete = canPerformAction(currentUser, 'delete', 'ocg', 'organization');
  const canNegotiate = canPerformAction(currentUser, 'negotiate', 'ocg', 'organization');
  const canApprove = canPerformAction(currentUser, 'approve', 'ocg', 'organization');
  const canSign = canPerformAction(currentUser, 'sign', 'ocg', 'organization');

  // Return object with OCG state and management functions
  return {
    ocgs,
    currentOCG,
    loading,
    errors,
    versionHistory,
    documentGenerating,
    getOCGs,
    getOCGById,
    createOCG,
    updateOCG,
    deleteOCG,
    setCurrentOCG,
    clearCurrentOCG,
    addSection,
    updateSection,
    removeSection,
    reorderSections,
    addAlternative,
    updateAlternative,
    removeAlternative,
    setTotalPoints,
    setDefaultPointBudget,
    startNegotiation,
    submitSelections,
    approveSelections,
    rejectSelections,
    selectAlternative,
    getPointsUsed,
    getPointsRemaining,
    finalizeOCG,
    generateDocument,
    downloadDocument,
    signDocument,
    getVersionHistory,
    canCreate,
    canEdit,
    canDelete,
    canNegotiate,
    canApprove,
    canSign,
  };
};