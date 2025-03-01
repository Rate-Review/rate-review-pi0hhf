"""Initialization file for the negotiations service module that orchestrates rate negotiation workflows between law firms and clients in the Justice Bid system. This module exposes key components for validation, state management, counter-proposals, approval workflows, and audit functionality."""

from .validation import NegotiationValidator  # Import validation class for negotiation operations
from .validation import validate_negotiation_request  # Import standalone validation function for negotiation requests
from .validation import validate_rate_submission  # Import standalone validation function for rate submissions
from .validation import validate_counter_proposal  # Import standalone validation function for counter-proposals
from .state_machine import NegotiationStateMachine  # Import state machine for negotiation lifecycle management
from .state_machine import get_allowed_transitions  # Import utility function for retrieving allowed state transitions
from .state_machine import can_transition_to  # Import utility function for checking if a state transition is allowed
from .counter_proposal import CounterProposalService  # Import service for counter-proposal functionality
from .counter_proposal import CounterProposalRequest  # Import data validation model for counter-proposal requests
from .counter_proposal import CounterProposalResponse  # Import response model for counter-proposal operations
from .approval_workflow import ApprovalWorkflowService  # Import service for approval workflow management
from .audit import *  # Import all audit functions for negotiation activities


__all__ = [
    "NegotiationValidator",
    "validate_negotiation_request",
    "validate_rate_submission",
    "validate_counter_proposal",
    "NegotiationStateMachine",
    "get_allowed_transitions",
    "can_transition_to",
    "CounterProposalService",
    "CounterProposalRequest",
    "CounterProposalResponse",
    "ApprovalWorkflowService",
    "audit_negotiation_status_change",
    "audit_rate_status_change",
    "audit_counter_proposal",
    "get_negotiation_audit_trail"
]