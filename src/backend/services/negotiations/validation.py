"""Provides validation functionality for the negotiation workflow, ensuring that state transitions and operations are valid according to business rules. This service implements validation for negotiation states, rate states within negotiations, and validates that operations comply with client-defined rate rules and approval requirements."""

import typing
import uuid
from datetime import datetime

from src.backend.db.repositories.negotiation_repository import NegotiationRepository
from src.backend.db.repositories.rate_repository import RateRepository
from src.backend.services.rates.rules import get_organization_rate_rules
from src.backend.services.rates.validation import validate_rate_against_rules
from src.backend.utils.constants import NegotiationStatus, RateStatus, ApprovalStatus
from src.backend.utils.logging import get_logger
from src.backend.api.core.errors import ValidationException

logger = get_logger(__name__, 'service')

STATE_TRANSITION_MAP = {
    'NEGOTIATION_TRANSITIONS': {
        NegotiationStatus.REQUESTED: [NegotiationStatus.IN_PROGRESS, NegotiationStatus.REJECTED],
        NegotiationStatus.IN_PROGRESS: [NegotiationStatus.COMPLETED, NegotiationStatus.REJECTED],
        NegotiationStatus.COMPLETED: [],
        NegotiationStatus.REJECTED: []
    },
    'RATE_TRANSITIONS': {
        RateStatus.DRAFT: [RateStatus.SUBMITTED],
        RateStatus.SUBMITTED: [RateStatus.UNDER_REVIEW, RateStatus.REJECTED],
        RateStatus.UNDER_REVIEW: [RateStatus.CLIENT_APPROVED, RateStatus.CLIENT_REJECTED, RateStatus.CLIENT_COUNTER_PROPOSED],
        RateStatus.CLIENT_COUNTER_PROPOSED: [RateStatus.FIRM_ACCEPTED, RateStatus.FIRM_COUNTER_PROPOSED, RateStatus.REJECTED],
        RateStatus.FIRM_COUNTER_PROPOSED: [RateStatus.CLIENT_APPROVED, RateStatus.CLIENT_REJECTED, RateStatus.CLIENT_COUNTER_PROPOSED],
        RateStatus.CLIENT_APPROVED: [RateStatus.PENDING_APPROVAL, RateStatus.APPROVED],
        RateStatus.FIRM_ACCEPTED: [RateStatus.PENDING_APPROVAL, RateStatus.APPROVED],
        RateStatus.PENDING_APPROVAL: [RateStatus.APPROVED, RateStatus.REJECTED],
        RateStatus.APPROVED: [RateStatus.EXPORTED, RateStatus.ACTIVE],
        RateStatus.ACTIVE: [RateStatus.EXPIRED],
        RateStatus.EXPORTED: [],
        RateStatus.REJECTED: [],
        RateStatus.EXPIRED: []
    },
    'APPROVAL_TRANSITIONS': {
        ApprovalStatus.PENDING: [ApprovalStatus.IN_PROGRESS],
        ApprovalStatus.IN_PROGRESS: [ApprovalStatus.APPROVED, ApprovalStatus.REJECTED],
        ApprovalStatus.APPROVED: [],
        ApprovalStatus.REJECTED: []
    }
}


def get_allowed_transitions(state_type: str, current_state: Enum) -> List[Enum]:
    """Gets the allowed state transitions for a given state type and current state"""
    if state_type == 'negotiation':
        transition_map = STATE_TRANSITION_MAP['NEGOTIATION_TRANSITIONS']
    elif state_type == 'rate':
        transition_map = STATE_TRANSITION_MAP['RATE_TRANSITIONS']
    elif state_type == 'approval':
        transition_map = STATE_TRANSITION_MAP['APPROVAL_TRANSITIONS']
    else:
        return []

    return transition_map.get(current_state, [])


def can_transition_to(state_type: str, current_state: Enum, target_state: Enum) -> bool:
    """Checks if a state transition is allowed"""
    allowed_transitions = get_allowed_transitions(state_type, current_state)
    return target_state in allowed_transitions


def validate_counter_proposal_values(original_rate: Dict, counter_rate: Dict) -> Dict:
    """Validates that counter-proposed rate values are within acceptable ranges"""
    # TODO: Implement validation logic
    return {}


def validate_bulk_rate_submissions(negotiation_id: uuid.UUID, rate_submissions: List[Dict]) -> Dict:
    """Validates a bulk submission of rates for a negotiation"""
    # TODO: Implement validation logic
    return {}


class NegotiationValidator:
    """Validates operations and state transitions in the negotiation workflow"""

    def __init__(self, negotiation_repo: NegotiationRepository, rate_repo: RateRepository):
        """Initializes the validator with required repositories"""
        self._negotiation_repo = negotiation_repo
        self._rate_repo = rate_repo
        logger.info("NegotiationValidator initialized")

    def validate_state_transition(self, negotiation_id: uuid.UUID, target_state: NegotiationStatus) -> bool:
        """Validates if a negotiation state transition is allowed"""
        logger.info(f"Validating state transition for negotiation {negotiation_id} to {target_state}")

        negotiation = self._negotiation_repo.get_negotiation_by_id(negotiation_id)
        if not negotiation:
            raise ValidationException(f"Negotiation with ID {negotiation_id} not found", errors=[])

        current_state = negotiation.status
        if not can_transition_to('negotiation', current_state, target_state):
            raise ValidationException(
                f"Invalid state transition for negotiation {negotiation_id} from {current_state} to {target_state}",
                errors=[]
            )

        return True

    def validate_rate_state_transition(self, rate_id: uuid.UUID, target_state: RateStatus) -> bool:
        """Validates if a rate state transition is allowed"""
        logger.info(f"Validating state transition for rate {rate_id} to {target_state}")

        rate = self._rate_repo.get_rate_by_id(rate_id)
        if not rate:
            raise ValidationException(f"Rate with ID {rate_id} not found", errors=[])

        current_state = rate.status
        if not can_transition_to('rate', current_state, target_state):
            raise ValidationException(
                f"Invalid state transition for rate {rate_id} from {current_state} to {target_state}",
                errors=[]
            )

        return True
    
    def validate_approval_state_transition(self, negotiation_id: uuid.UUID, target_state: ApprovalStatus) -> bool:
        """Validates if an approval workflow state transition is allowed"""
        logger.info(f"Validating approval state transition for negotiation {negotiation_id} to {target_state}")

        negotiation = self._negotiation_repo.get_negotiation_by_id(negotiation_id)
        if not negotiation:
            raise ValidationException(f"Negotiation with ID {negotiation_id} not found", errors=[])
        
        if not negotiation.approval_workflow_id:
             raise ValidationException(f"Negotiation with ID {negotiation_id} does not have an approval workflow", errors=[])

        current_state = negotiation.approval_status
        if not can_transition_to('approval', current_state, target_state):
            raise ValidationException(
                f"Invalid approval state transition for negotiation {negotiation_id} from {current_state} to {target_state}",
                errors=[]
            )

        return True

    def validate_rate_submission(self, negotiation_id: uuid.UUID, rate_id: uuid.UUID) -> bool:
        """Validates if a rate can be submitted to a negotiation"""
        # TODO: Implement validation logic
        return True

    def validate_client_response(self, negotiation_id: uuid.UUID, rate_decisions: Dict[uuid.UUID, RateStatus]) -> Dict:
        """Validates a client's response to submitted rates (approve/reject/counter)"""
        # TODO: Implement validation logic
        return {}

    def validate_firm_response(self, negotiation_id: uuid.UUID, rate_decisions: Dict[uuid.UUID, RateStatus]) -> Dict:
        """Validates a law firm's response to client counter-proposals"""
        # TODO: Implement validation logic
        return {}

    def validate_approval_action(self, negotiation_id: uuid.UUID, approver_id: uuid.UUID, action: str) -> bool:
        """Validates an approval action within an approval workflow"""
        # TODO: Implement validation logic
        return True

    def validate_can_finalize(self, negotiation_id: uuid.UUID, final_state: NegotiationStatus) -> bool:
        """Validates if a negotiation can be finalized"""
        # TODO: Implement validation logic
        return True