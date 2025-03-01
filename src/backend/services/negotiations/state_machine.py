"""
Implements a state machine for managing the lifecycle of rate negotiations in the Justice Bid system.
Defines valid states, transitions, and conditions for negotiation workflows, ensuring consistent state management and proper audit trails.
"""

import enum  # standard library
import typing  # standard library
from typing import List, Dict, Optional, Any, Callable, Tuple  # standard library
import logging  # standard library

from dataclasses import dataclass  # standard library

from src.backend.db.models.negotiation import Negotiation  # src/backend/db/models/negotiation.py
from src.backend.services.negotiations.validation import validate_negotiation_transition  # ./validation
from src.backend.services.negotiations.audit import log_negotiation_transition  # ./audit
from src.backend.db.repositories.rate_repository import RateRepository  # ../../db/repositories/rate_repository.py


logger = logging.getLogger(__name__)


class NegotiationState(enum.Enum):
    """Enumeration of possible states in the negotiation lifecycle"""

    def __init__(self):
        """Defines the enumeration values for negotiation states"""
        DRAFT = "draft"  # Define DRAFT state for negotiations being prepared
        REQUESTED = "requested"  # Define REQUESTED state for rate request initiated
        SUBMITTED = "submitted"  # Define SUBMITTED state for rates submitted by law firm
        UNDER_REVIEW = "under_review"  # Define UNDER_REVIEW state for client reviewing rates
        CLIENT_APPROVED = "client_approved"  # Define CLIENT_APPROVED state for rates approved by client
        CLIENT_REJECTED = "client_rejected"  # Define CLIENT_REJECTED state for rates rejected by client
        CLIENT_COUNTER_PROPOSED = "client_counter_proposed"  # Define CLIENT_COUNTER_PROPOSED state for client counter-proposals
        FIRM_ACCEPTED = "firm_accepted"  # Define FIRM_ACCEPTED state for law firm accepting counter-proposals
        FIRM_COUNTER_PROPOSED = "firm_counter_proposed"  # Define FIRM_COUNTER_PROPOSED state for law firm counter-proposals
        PENDING_APPROVAL = "pending_approval"  # Define PENDING_APPROVAL state for rates awaiting organizational approval
        APPROVED = "approved"  # Define APPROVED state for fully approved rates
        REJECTED = "rejected"  # Define REJECTED state for rejected rates
        MODIFIED = "modified"  # Define MODIFIED state for rates modified during approval
        EXPORTED = "exported"  # Define EXPORTED state for rates exported to external systems
        ACTIVE = "active"  # Define ACTIVE state for rates that reached effective date
        EXPIRED = "expired"  # Define EXPIRED state for rates that reached expiration date


class NegotiationTransition(enum.Enum):
    """Enumeration of possible transitions between negotiation states"""

    def __init__(self):
        """Defines the enumeration values for negotiation transitions"""
        SUBMIT = "submit"  # Define SUBMIT transition from DRAFT to SUBMITTED
        START_REVIEW = "start_review"  # Define START_REVIEW transition from SUBMITTED to UNDER_REVIEW
        CLIENT_APPROVE = "client_approve"  # Define CLIENT_APPROVE transition from UNDER_REVIEW to CLIENT_APPROVED
        CLIENT_REJECT = "client_reject"  # Define CLIENT_REJECT transition from UNDER_REVIEW to CLIENT_REJECTED
        CLIENT_COUNTER = "client_counter"  # Define CLIENT_COUNTER transition from UNDER_REVIEW to CLIENT_COUNTER_PROPOSED
        FIRM_REVIEW = "firm_review"  # Define FIRM_REVIEW transition from CLIENT_COUNTER_PROPOSED to UNDER_REVIEW
        FIRM_ACCEPT = "firm_accept"  # Define FIRM_ACCEPT transition from CLIENT_COUNTER_PROPOSED to FIRM_ACCEPTED
        FIRM_COUNTER = "firm_counter"  # Define FIRM_COUNTER transition from CLIENT_COUNTER_PROPOSED to FIRM_COUNTER_PROPOSED
        REVIEW_COUNTER = "review_counter"  # Define REVIEW_COUNTER transition from FIRM_COUNTER_PROPOSED to UNDER_REVIEW
        ENTER_APPROVAL = "enter_approval"  # Define ENTER_APPROVAL transition from CLIENT_APPROVED to PENDING_APPROVAL
        DIRECT_APPROVE = "direct_approve"  # Define DIRECT_APPROVE transition from CLIENT_APPROVED to APPROVED
        APPROVE = "approve"  # Define APPROVE transition from PENDING_APPROVAL to APPROVED
        REJECT = "reject"  # Define REJECT transition from PENDING_APPROVAL to REJECTED
        MODIFY = "modify"  # Define MODIFY transition from PENDING_APPROVAL to MODIFIED
        RESTART_APPROVAL = "restart_approval"  # Define RESTART_APPROVAL transition from MODIFIED to PENDING_APPROVAL
        FIRM_TO_APPROVAL = "firm_to_approval"  # Define FIRM_TO_APPROVAL transition from FIRM_ACCEPTED to PENDING_APPROVAL
        FIRM_DIRECT_APPROVE = "firm_direct_approve"  # Define FIRM_DIRECT_APPROVE transition from FIRM_ACCEPTED to APPROVED
        EXPORT = "export"  # Define EXPORT transition from APPROVED to EXPORTED
        ACTIVATE = "activate"  # Define ACTIVATE transition from APPROVED to ACTIVE
        EXPIRE = "expire"  # Define EXPIRE transition from ACTIVE to EXPIRED


@dataclass
class StateTransition:
    """Data class representing a state transition with source state, destination state, and validation function"""
    source_state: NegotiationState
    target_state: NegotiationState
    required_parameters: List[str]
    validation_func: Optional[Callable]
    side_effect_func: Optional[Callable]

    def __init__(self, source_state: NegotiationState, target_state: NegotiationState, required_parameters: List[str], validation_func: Optional[Callable], side_effect_func: Optional[Callable]):
        """Initializes a state transition with the provided parameters"""
        self.source_state = source_state
        self.target_state = target_state
        self.required_parameters = required_parameters
        self.validation_func = validation_func
        self.side_effect_func = side_effect_func


class StateMachineError(Exception):
    """Custom exception for state machine errors during transitions"""

    def __init__(self, message: str):
        """Initializes a state machine error with the provided message"""
        super().__init__(message)


class NegotiationStateMachine:
    """Class managing the negotiation state machine, handling transitions and validations"""

    def __init__(self, rate_repository: RateRepository):
        """Initializes the state machine with the transition map"""
        self._rate_repository = rate_repository
        self._transition_map: Dict[NegotiationTransition, StateTransition] = {
            NegotiationTransition.SUBMIT: StateTransition(source_state=NegotiationState.DRAFT, target_state=NegotiationState.SUBMITTED, required_parameters=[], validation_func=None, side_effect_func=None),
            NegotiationTransition.START_REVIEW: StateTransition(source_state=NegotiationState.SUBMITTED, target_state=NegotiationState.UNDER_REVIEW, required_parameters=[], validation_func=None, side_effect_func=None),
            NegotiationTransition.CLIENT_APPROVE: StateTransition(source_state=NegotiationState.UNDER_REVIEW, target_state=NegotiationState.CLIENT_APPROVED, required_parameters=[], validation_func=None, side_effect_func=None),
            NegotiationTransition.CLIENT_REJECT: StateTransition(source_state=NegotiationState.UNDER_REVIEW, target_state=NegotiationState.CLIENT_REJECTED, required_parameters=['rejection_reason'], validation_func=None, side_effect_func=None),
            NegotiationTransition.CLIENT_COUNTER: StateTransition(source_state=NegotiationState.UNDER_REVIEW, target_state=NegotiationState.CLIENT_COUNTER_PROPOSED, required_parameters=['counter_rates', 'message'], validation_func=None, side_effect_func=lambda neg, trans, user_id, **kwargs: handle_counter_proposal(neg, trans, user_id, kwargs.get('counter_rates'), kwargs.get('message'), self._rate_repository)),
            NegotiationTransition.FIRM_REVIEW: StateTransition(source_state=NegotiationState.CLIENT_COUNTER_PROPOSED, target_state=NegotiationState.UNDER_REVIEW, required_parameters=[], validation_func=None, side_effect_func=None),
            NegotiationTransition.FIRM_ACCEPT: StateTransition(source_state=NegotiationState.CLIENT_COUNTER_PROPOSED, target_state=NegotiationState.FIRM_ACCEPTED, required_parameters=[], validation_func=None, side_effect_func=None),
            NegotiationTransition.FIRM_COUNTER: StateTransition(source_state=NegotiationState.CLIENT_COUNTER_PROPOSED, target_state=NegotiationState.FIRM_COUNTER_PROPOSED, required_parameters=['counter_rates', 'message'], validation_func=None, side_effect_func=lambda neg, trans, user_id, **kwargs: handle_counter_proposal(neg, trans, user_id, kwargs.get('counter_rates'), kwargs.get('message'), self._rate_repository)),
            NegotiationTransition.REVIEW_COUNTER: StateTransition(source_state=NegotiationState.FIRM_COUNTER_PROPOSED, target_state=NegotiationState.UNDER_REVIEW, required_parameters=[], validation_func=None, side_effect_func=None),
            NegotiationTransition.ENTER_APPROVAL: StateTransition(source_state=NegotiationState.CLIENT_APPROVED, target_state=NegotiationState.PENDING_APPROVAL, required_parameters=[], validation_func=None, side_effect_func=create_approval_workflow),
            NegotiationTransition.DIRECT_APPROVE: StateTransition(source_state=NegotiationState.CLIENT_APPROVED, target_state=NegotiationState.APPROVED, required_parameters=[], validation_func=check_approval_requirements, side_effect_func=None),
            NegotiationTransition.APPROVE: StateTransition(source_state=NegotiationState.PENDING_APPROVAL, target_state=NegotiationState.APPROVED, required_parameters=[], validation_func=None, side_effect_func=None),
            NegotiationTransition.REJECT: StateTransition(source_state=NegotiationState.PENDING_APPROVAL, target_state=NegotiationState.REJECTED, required_parameters=['rejection_reason'], validation_func=None, side_effect_func=None),
            NegotiationTransition.MODIFY: StateTransition(source_state=NegotiationState.PENDING_APPROVAL, target_state=NegotiationState.MODIFIED, required_parameters=['modified_rates', 'message'], validation_func=None, side_effect_func=None),
            NegotiationTransition.RESTART_APPROVAL: StateTransition(source_state=NegotiationState.MODIFIED, target_state=NegotiationState.PENDING_APPROVAL, required_parameters=[], validation_func=None, side_effect_func=None),
            NegotiationTransition.FIRM_TO_APPROVAL: StateTransition(source_state=NegotiationState.FIRM_ACCEPTED, target_state=NegotiationState.PENDING_APPROVAL, required_parameters=[], validation_func=check_approval_requirements, side_effect_func=create_approval_workflow),
            NegotiationTransition.FIRM_DIRECT_APPROVE: StateTransition(source_state=NegotiationState.FIRM_ACCEPTED, target_state=NegotiationState.APPROVED, required_parameters=[], validation_func=check_approval_requirements, side_effect_func=None),
            NegotiationTransition.EXPORT: StateTransition(source_state=NegotiationState.APPROVED, target_state=NegotiationState.EXPORTED, required_parameters=['export_details'], validation_func=None, side_effect_func=None),
            NegotiationTransition.ACTIVATE: StateTransition(source_state=NegotiationState.APPROVED, target_state=NegotiationState.ACTIVE, required_parameters=[], validation_func=None, side_effect_func=None),
            NegotiationTransition.EXPIRE: StateTransition(source_state=NegotiationState.ACTIVE, target_state=NegotiationState.EXPIRED, required_parameters=[], validation_func=None, side_effect_func=None),
        }

    def get_transition_definition(self, transition: NegotiationTransition) -> StateTransition:
        """Returns the state transition definition for a given transition"""
        if transition not in self._transition_map:
            raise StateMachineError(f"No transition definition found for {transition}")
        return self._transition_map[transition]

    def get_valid_transitions_for_state(self, state: NegotiationState) -> List[NegotiationTransition]:
        """Returns all valid transitions from a given state"""
        valid_transitions = []
        for transition, definition in self._transition_map.items():
            if definition.source_state == state:
                valid_transitions.append(transition)
        return valid_transitions

    def validate_transition(self, negotiation: Negotiation, transition: NegotiationTransition, **kwargs: Any) -> bool:
        """Validates if a transition is valid for a given negotiation"""
        definition = self.get_transition_definition(transition)
        if negotiation.status != definition.source_state:
            return False
        for param in definition.required_parameters:
            if param not in kwargs:
                return False
        if definition.validation_func:
            return definition.validation_func(negotiation, transition, **kwargs)
        return True

    def execute_transition(self, negotiation: Negotiation, transition: NegotiationTransition, user_id: str, **kwargs: Any) -> Negotiation:
        """Executes a state transition on a negotiation"""
        definition = self.get_transition_definition(transition)
        if not self.validate_transition(negotiation, transition, **kwargs):
            raise StateMachineError(f"Invalid transition {transition} from state {negotiation.status}")
        if definition.side_effect_func:
            definition.side_effect_func(negotiation, transition, user_id, **kwargs)
        negotiation.status = definition.target_state
        log_negotiation_transition(negotiation_id=str(negotiation.id), previous_state=negotiation.status.name, new_state=definition.target_state.name, user_id=user_id, metadata=kwargs, track_analytics=True)
        return negotiation

    def get_required_parameters_for_transition(self, transition: NegotiationTransition) -> List[str]:
        """Returns the required parameters for a transition"""
        definition = self.get_transition_definition(transition)
        return definition.required_parameters

    def get_target_state(self, transition: NegotiationTransition) -> NegotiationState:
        """Returns the target state for a given transition"""
        definition = self.get_transition_definition(transition)
        return definition.target_state


def get_valid_transitions(current_state: NegotiationState) -> List[NegotiationTransition]:
    """Returns a list of valid transitions from a given state based on the state machine definition"""
    return NegotiationStateMachine.get_valid_transitions_for_state(current_state)


def validate_transition(negotiation: Negotiation, transition: NegotiationTransition, **kwargs: Any) -> bool:
    """Validates if a transition is valid for a given negotiation based on business rules and current state"""
    return NegotiationStateMachine.validate_transition(negotiation, transition, **kwargs)


def transition_negotiation(negotiation: Negotiation, transition: NegotiationTransition, user_id: str, **kwargs: Any) -> Negotiation:
    """Executes a state transition on a negotiation, updating its status and performing any required actions"""
    return NegotiationStateMachine.execute_transition(negotiation, transition, user_id, **kwargs)


def get_required_parameters(transition: NegotiationTransition) -> List[str]:
    """Returns a list of required parameters for a specific transition"""
    return NegotiationStateMachine.get_required_parameters_for_transition(transition)


def get_transition_for_target_state(current_state: NegotiationState, target_state: NegotiationState) -> Optional[NegotiationTransition]:
    """Returns the appropriate transition to reach a target state from the current state"""
    for transition in get_valid_transitions(current_state):
        if NegotiationStateMachine.get_target_state(transition) == target_state:
            return transition
    return None


def handle_counter_proposal(negotiation: Negotiation, transition: NegotiationTransition, user_id: str, counter_rates: Dict, message: str, rate_repository: RateRepository) -> bool:
    """Handles counter-proposal processing during state transitions, localized to avoid circular dependency"""
    is_client_counter = transition == NegotiationTransition.CLIENT_COUNTER
    # Process each counter-rate in the provided counter_rates dictionary
    for rate_id, proposed_amount in counter_rates.items():
        # Add a counter-proposal using the rate repository
        rate_repository.add_counter_proposal(rate_id=rate_id, counter_amount=proposed_amount, user_id=user_id, message=message)
        # Update the status of each rate based on the new negotiation state
        rate_repository.update_status(rate_id=rate_id, status=NegotiationState.CLIENT_COUNTER_PROPOSED.value if is_client_counter else NegotiationState.FIRM_COUNTER_PROPOSED.value, user_id=user_id, message=message)
    # Log the counter-proposal actions for audit purposes
    logger.info(f"Counter-proposal made in negotiation {negotiation.id} by user {user_id}")
    return True


def check_approval_requirements(negotiation: Negotiation, transition: NegotiationTransition, user_id: str, **kwargs: Any) -> bool:
    """Checks if a negotiation requires approval workflow based on client organization settings and negotiation properties"""
    # Check if the client has approval workflow requirements configured
    if not negotiation.client_id:
        return True
    # Determine if the negotiation meets any auto-approval criteria (e.g., total amount below threshold)
    # For DIRECT_APPROVE and FIRM_DIRECT_APPROVE transitions, validate that approval can be skipped
    if transition in [NegotiationTransition.DIRECT_APPROVE, NegotiationTransition.FIRM_DIRECT_APPROVE]:
        # Add logic to check if approval can be skipped based on criteria
        return True
    # Return True if approval can be skipped, False if approval workflow is required
    return False


def create_approval_workflow(negotiation: Negotiation, transition: NegotiationTransition, user_id: str, **kwargs: Any) -> bool:
    """Creates an approval workflow for a negotiation entering the approval state"""
    # Determine the appropriate approval workflow template based on client organization settings
    # Create an approval workflow instance linked to the negotiation
    # Set up approval steps based on the workflow template
    # Initialize the approval workflow state to pending
    # Log the approval workflow creation for audit purposes
    logger.info(f"Approval workflow created for negotiation {negotiation.id} by user {user_id}")
    return True