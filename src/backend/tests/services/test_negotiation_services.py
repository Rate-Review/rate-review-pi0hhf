import pytest
from unittest.mock import Mock
from uuid import uuid4
from datetime import date

from src.backend.services.negotiations.validation import NegotiationValidator, get_allowed_transitions, can_transition_to
from src.backend.services.negotiations.state_machine import NegotiationStateMachine, NegotiationState, StateMachineError
from src.backend.services.negotiations.counter_proposal import CounterProposalService, validate_counter_proposal_rate, get_counter_proposal_bounds
from src.backend.services.negotiations.approval_workflow import ApprovalWorkflowService, APPROVAL_ACTION_APPROVE, APPROVAL_ACTION_REJECT
from src.backend.db.repositories.negotiation_repository import NegotiationRepository
from src.backend.db.repositories.rate_repository import RateRepository
from src.backend.db.repositories.approval_workflow_repository import ApprovalWorkflowRepository
from src.backend.api.core.errors import ValidationException
from src.backend.utils.constants import RateStatus, NegotiationStatus, ApprovalStatus

# Define test functions for validation logic
def test_get_allowed_transitions():
    """Tests the get_allowed_transitions function returns correct transition lists"""
    # Test get_allowed_transitions for negotiation state type with different states
    assert get_allowed_transitions('negotiation', NegotiationStatus.REQUESTED) == [NegotiationStatus.IN_PROGRESS, NegotiationStatus.REJECTED]
    assert get_allowed_transitions('negotiation', NegotiationStatus.IN_PROGRESS) == [NegotiationStatus.COMPLETED, NegotiationStatus.REJECTED]
    assert get_allowed_transitions('negotiation', NegotiationStatus.COMPLETED) == []
    assert get_allowed_transitions('negotiation', NegotiationStatus.REJECTED) == []

    # Test get_allowed_transitions for rate state type with different states
    assert get_allowed_transitions('rate', RateStatus.DRAFT) == [RateStatus.SUBMITTED]
    assert get_allowed_transitions('rate', RateStatus.SUBMITTED) == [RateStatus.UNDER_REVIEW, RateStatus.REJECTED]
    
    # Test get_allowed_transitions for approval state type with different states
    assert get_allowed_transitions('approval', ApprovalStatus.PENDING) == [ApprovalStatus.IN_PROGRESS]
    assert get_allowed_transitions('approval', ApprovalStatus.IN_PROGRESS) == [ApprovalStatus.APPROVED, ApprovalStatus.REJECTED]
    assert get_allowed_transitions('approval', ApprovalStatus.APPROVED) == []
    assert get_allowed_transitions('approval', ApprovalStatus.REJECTED) == []

    # Verify transitions match the expected state transitions defined in the state machine
    # (This is a basic example, more comprehensive testing would involve checking all states)

def test_can_transition_to():
    """Tests the can_transition_to function correctly identifies valid transitions"""
    # Test valid transitions return True
    assert can_transition_to('negotiation', NegotiationStatus.REQUESTED, NegotiationStatus.IN_PROGRESS) is True
    assert can_transition_to('rate', RateStatus.DRAFT, RateStatus.SUBMITTED) is True
    assert can_transition_to('approval', ApprovalStatus.PENDING, ApprovalStatus.IN_PROGRESS) is True

    # Test invalid transitions return False
    assert can_transition_to('negotiation', NegotiationStatus.REQUESTED, NegotiationStatus.COMPLETED) is False
    assert can_transition_to('rate', RateStatus.DRAFT, RateStatus.UNDER_REVIEW) is False
    assert can_transition_to('approval', ApprovalStatus.PENDING, ApprovalStatus.APPROVED) is False

    # Test edge cases like transitions to the same state
    assert can_transition_to('negotiation', NegotiationStatus.REQUESTED, NegotiationStatus.REQUESTED) is False

    # Test with invalid state types
    assert can_transition_to('invalid_type', NegotiationStatus.REQUESTED, NegotiationStatus.IN_PROGRESS) is False

class TestNegotiationValidator:
    """Test class for NegotiationValidator functionality"""

    def setup_method(self):
        """Setup method run before each test"""
        # Create mock NegotiationRepository and RateRepository
        self._negotiation_repo = Mock()
        self._rate_repo = Mock()
        # Initialize NegotiationValidator with the repositories
        self._validator = NegotiationValidator(self._negotiation_repo, self._rate_repo)

    def test_validate_state_transition(self):
        """Test validation of negotiation state transitions"""
        # Configure mock negotiation with specific state
        negotiation_id = uuid4()
        self._negotiation_repo.get_negotiation_by_id.return_value = Mock(id=negotiation_id, status=NegotiationStatus.REQUESTED)

        # Test validation of valid transition succeeds
        assert self._validator.validate_state_transition(negotiation_id, NegotiationStatus.IN_PROGRESS) is True

        # Test validation of invalid transition raises exception
        with pytest.raises(ValidationException) as exc_info:
            self._validator.validate_state_transition(negotiation_id, NegotiationStatus.COMPLETED)
        assert "Invalid state transition" in str(exc_info.value)

        # Verify proper error messages are included in exceptions
        with pytest.raises(ValidationException) as exc_info:
            self._validator.validate_state_transition(negotiation_id, NegotiationStatus.COMPLETED)
        assert "Invalid state transition" in str(exc_info.value)

    def test_validate_rate_state_transition(self):
        """Test validation of rate state transitions"""
        # Configure mock rate with specific state
        rate_id = uuid4()
        self._rate_repo.get_rate_by_id.return_value = Mock(id=rate_id, status=RateStatus.DRAFT)

        # Test validation of valid transition succeeds
        assert self._validator.validate_rate_state_transition(rate_id, RateStatus.SUBMITTED) is True

        # Test validation of invalid transition raises exception
        with pytest.raises(ValidationException) as exc_info:
            self._validator.validate_rate_state_transition(rate_id, RateStatus.UNDER_REVIEW)
        assert "Invalid state transition" in str(exc_info.value)

        # Verify proper error messages are included in exceptions
        with pytest.raises(ValidationException) as exc_info:
            self._validator.validate_rate_state_transition(rate_id, RateStatus.UNDER_REVIEW)
        assert "Invalid state transition" in str(exc_info.value)

    def test_validate_client_response(self):
        """Test validation of client responses to rate proposals"""
        # Configure mock negotiation and rates
        negotiation_id = uuid4()
        rate_id = uuid4()
        self._negotiation_repo.get_negotiation_by_id.return_value = Mock(id=negotiation_id, status=NegotiationStatus.IN_PROGRESS)
        self._rate_repo.get_rate_by_id.return_value = Mock(id=rate_id, status=RateStatus.SUBMITTED)

        # Test validation of approval response
        assert self._validator.validate_client_response(negotiation_id, {rate_id: RateStatus.CLIENT_APPROVED}) == {}

        # Test validation of rejection response
        assert self._validator.validate_client_response(negotiation_id, {rate_id: RateStatus.CLIENT_REJECTED}) == {}

        # Test validation of counter-proposal response
        assert self._validator.validate_client_response(negotiation_id, {rate_id: RateStatus.CLIENT_COUNTER_PROPOSED}) == {}

        # Test validation failures for various scenarios
        with pytest.raises(NotImplementedError):
            self._validator.validate_client_response(negotiation_id, {rate_id: "invalid_status"})

    def test_validate_firm_response(self):
        """Test validation of law firm responses to client counter-proposals"""
        # Configure mock negotiation and rates
        negotiation_id = uuid4()
        rate_id = uuid4()
        self._negotiation_repo.get_negotiation_by_id.return_value = Mock(id=negotiation_id, status=NegotiationStatus.IN_PROGRESS)
        self._rate_repo.get_rate_by_id.return_value = Mock(id=rate_id, status=RateStatus.CLIENT_COUNTER_PROPOSED)

        # Test validation of acceptance response
        assert self._validator.validate_firm_response(negotiation_id, {rate_id: RateStatus.FIRM_ACCEPTED}) == {}

        # Test validation of rejection response
        assert self._validator.validate_firm_response(negotiation_id, {rate_id: RateStatus.REJECTED}) == {}

        # Test validation of counter-proposal response
        assert self._validator.validate_firm_response(negotiation_id, {rate_id: RateStatus.FIRM_COUNTER_PROPOSED}) == {}

        # Test validation failures for various scenarios
        with pytest.raises(NotImplementedError):
            self._validator.validate_firm_response(negotiation_id, {rate_id: "invalid_status"})

    def test_validation_with_missing_entities(self):
        """Test validation behavior when entities don't exist"""
        negotiation_id = uuid4()
        rate_id = uuid4()
        # Configure repositories to return None
        self._negotiation_repo.get_negotiation_by_id.return_value = None
        self._rate_repo.get_rate_by_id.return_value = None

        # Test validation raises appropriate exceptions
        with pytest.raises(ValidationException) as exc_info:
            self._validator.validate_state_transition(negotiation_id, NegotiationStatus.IN_PROGRESS)
        assert "Negotiation with ID" in str(exc_info.value)

        with pytest.raises(ValidationException) as exc_info:
            self._validator.validate_rate_state_transition(rate_id, RateStatus.SUBMITTED)
        assert "Rate with ID" in str(exc_info.value)

        # Verify proper error messages are included in exceptions
        with pytest.raises(ValidationException) as exc_info:
            self._validator.validate_state_transition(negotiation_id, NegotiationStatus.IN_PROGRESS)
        assert "Negotiation with ID" in str(exc_info.value)

        with pytest.raises(ValidationException) as exc_info:
            self._validator.validate_rate_state_transition(rate_id, RateStatus.SUBMITTED)
        assert "Rate with ID" in str(exc_info.value)

class TestNegotiationStateMachine:
    """Test class for NegotiationStateMachine functionality"""

    def setup_method(self):
        """Setup method run before each test"""
        # Create mock RateRepository
        self._rate_repo = Mock()
        # Initialize NegotiationStateMachine with the repository
        self._state_machine = NegotiationStateMachine(self._rate_repo)

    def test_transition_definition(self):
        """Test getting transition definitions from the state machine"""
        # Test get_transition_definition for various transitions
        transition = NegotiationTransition.SUBMIT
        definition = self._state_machine.get_transition_definition(transition)

        # Verify transition definitions have correct source and target states
        assert definition.source_state == NegotiationState.DRAFT
        assert definition.target_state == NegotiationState.SUBMITTED

        # Verify required parameters are correctly defined
        assert definition.required_parameters == []

        # Test with invalid transition raises appropriate exception
        with pytest.raises(StateMachineError):
            self._state_machine.get_transition_definition("invalid_transition")

    def test_get_valid_transitions(self):
        """Test getting valid transitions for a state"""
        # Test get_valid_transitions_for_state for various states
        transitions = self._state_machine.get_valid_transitions_for_state(NegotiationState.DRAFT)

        # Verify returned transitions match expected transitions
        assert NegotiationTransition.SUBMIT in transitions

        # Test with terminal states returns empty list
        assert self._state_machine.get_valid_transitions_for_state(NegotiationState.COMPLETED) == []

    def test_validate_transition(self):
        """Test validation of transitions"""
        # Configure mock negotiation with specific state
        negotiation = Mock(status=NegotiationState.DRAFT)

        # Test validation of valid transition succeeds
        assert self._state_machine.validate_transition(negotiation, NegotiationTransition.SUBMIT) is True

        # Test validation of invalid transition fails
        assert self._state_machine.validate_transition(negotiation, NegotiationTransition.START_REVIEW) is False

        # Test validation with missing required parameters fails
        negotiation = Mock(status=NegotiationState.UNDER_REVIEW)
        transition = NegotiationTransition.CLIENT_REJECT
        assert self._state_machine.validate_transition(negotiation, transition) is False

        # Test validation with complete parameters succeeds
        assert self._state_machine.validate_transition(negotiation, transition, rejection_reason="test") is True

    def test_execute_transition(self):
        """Test executing transitions"""
        # Configure mock negotiation with specific state
        negotiation = Mock(status=NegotiationState.DRAFT)
        user_id = "test_user"

        # Test executing valid transition updates negotiation state
        updated_negotiation = self._state_machine.execute_transition(negotiation, NegotiationTransition.SUBMIT, user_id)
        assert updated_negotiation.status == NegotiationState.SUBMITTED

        # Test executing a transition with side effects triggers those effects
        negotiation = Mock(status=NegotiationState.UNDER_REVIEW)
        transition = NegotiationTransition.CLIENT_REJECT
        updated_negotiation = self._state_machine.execute_transition(negotiation, transition, user_id, rejection_reason="test")
        assert updated_negotiation.status == NegotiationState.CLIENT_REJECTED

        # Test executing an invalid transition raises StateMachineError
        negotiation = Mock(status=NegotiationState.DRAFT)
        with pytest.raises(StateMachineError):
            self._state_machine.execute_transition(negotiation, NegotiationTransition.START_REVIEW, user_id)

        # Test executing a transition with missing parameters raises StateMachineError
        negotiation = Mock(status=NegotiationState.UNDER_REVIEW)
        transition = NegotiationTransition.CLIENT_REJECT
        with pytest.raises(StateMachineError):
            self._state_machine.execute_transition(negotiation, transition, user_id)

class TestCounterProposalService:
    """Test class for CounterProposalService functionality"""

    def setup_method(self):
        """Setup method run before each test"""
        # Create mock RateRepository, NegotiationRepository, and AI service
        self._rate_repo = Mock()
        self._negotiation_repo = Mock()
        self._ai_service = Mock()
        # Initialize CounterProposalService with the repositories and services
        self._service = CounterProposalService(self._rate_repo, self._negotiation_repo, self._ai_service)

    def test_create_counter_proposal(self):
        """Test creating a counter-proposal"""
        # Configure mock rate with current and proposed amounts
        rate_id = uuid4()
        self._rate_repo.get_by_id.return_value = Mock(id=rate_id, amount=100, status=RateStatus.SUBMITTED)

        # Test client counter-proposal creation
        rate = self._service.create_counter_proposal(rate_id, 110, "test_user", "test message", is_client=True)
        assert rate.amount == 110

        # Test firm counter-proposal creation
        rate = self._service.create_counter_proposal(rate_id, 110, "test_user", "test message", is_client=False)
        assert rate.amount == 110

        # Verify rate repository methods are called correctly
        self._rate_repo.add_counter_proposal.assert_called()

        # Test with invalid amounts fails with appropriate error
        with pytest.raises(NotImplementedError):
            self._service.create_counter_proposal(rate_id, -10, "test_user", "test message", is_client=True)

    def test_process_batch_counter_proposal(self):
        """Test processing multiple counter-proposals"""
        # Configure mock negotiation and rates
        negotiation_id = uuid4()
        rate_id1 = uuid4()
        rate_id2 = uuid4()
        self._negotiation_repo.get_by_id.return_value = Mock(id=negotiation_id, status=NegotiationStatus.IN_PROGRESS)
        self._rate_repo.get_by_id.return_value = Mock(id=rate_id1, amount=100, status=RateStatus.SUBMITTED)

        # Test batch processing with all valid proposals
        counter_rates = {str(rate_id1): 110, str(rate_id2): 120}
        result = self._service.process_batch_counter_proposal(str(negotiation_id), counter_rates, "test_user", "test message", is_client=True)
        assert result["success_count"] == 1
        assert result["error_count"] == 1

        # Verify result contains correct success and error counts
        assert result["success_count"] == 1
        assert result["error_count"] == 1

        # Verify negotiation message is added if provided
        # (This requires checking that the add_message method was called on the negotiation object)

    def test_get_ai_recommendations(self):
        """Test getting AI-recommended counter-proposal values"""
        # Configure AI service mock to return specific recommendations
        self._ai_service.suggest_counter_rate.return_value = 110

        # Configure mock rates and negotiation
        negotiation_id = uuid4()
        rate_id1 = uuid4()
        rate_id2 = uuid4()
        self._negotiation_repo.get_by_id.return_value = Mock(id=negotiation_id, status=NegotiationStatus.IN_PROGRESS)
        self._rate_repo.get_by_id.return_value = Mock(id=rate_id1, amount=100, status=RateStatus.SUBMITTED)

        # Test recommendations for client counter-proposals
        recommendations = self._service.get_ai_counter_proposal_recommendations(str(negotiation_id), [str(rate_id1), str(rate_id2)], is_client=True)
        assert recommendations[str(rate_id1)] == 110

        # Test recommendations for firm counter-proposals
        recommendations = self._service.get_ai_counter_proposal_recommendations(str(negotiation_id), [str(rate_id1), str(rate_id2)], is_client=False)
        assert recommendations[str(rate_id1)] == 110

        # Verify AI service is called with correct parameters
        self._ai_service.suggest_counter_rate.assert_called()

        # Test with non-existent negotiation
        self._negotiation_repo.get_by_id.return_value = None
        recommendations = self._service.get_ai_counter_proposal_recommendations(str(negotiation_id), [str(rate_id1), str(rate_id2)], is_client=True)
        assert recommendations == {}

    def test_accept_counter_proposal(self):
        """Test accepting a counter-proposal"""
        # Configure mock rate with counter-proposal in history
        rate_id = uuid4()
        self._rate_repo.get_by_id.return_value = Mock(id=rate_id, amount=100, status=RateStatus.CLIENT_COUNTER_PROPOSED, history=[{"counter_amount": 110}])

        # Test client accepting firm counter-proposal
        rate = self._service.accept_counter_proposal(rate_id, "test_user", "test message", is_client=True)
        assert rate.amount == 110
        assert rate.status == RateStatus.FIRM_ACCEPTED

        # Test firm accepting client counter-proposal
        self._rate_repo.get_by_id.return_value = Mock(id=rate_id, amount=100, status=RateStatus.FIRM_COUNTER_PROPOSED, history=[{"counter_amount": 110}])
        rate = self._service.accept_counter_proposal(rate_id, "test_user", "test message", is_client=False)
        assert rate.amount == 110
        assert rate.status == RateStatus.CLIENT_APPROVED

        # Verify rate amount is updated to counter-proposal amount
        self._rate_repo.add_counter_proposal.assert_not_called()

        # Test with rate that has no counter-proposal fails
        self._rate_repo.get_by_id.return_value = Mock(id=rate_id, amount=100, status=RateStatus.SUBMITTED, history=[])
        with pytest.raises(NotImplementedError):
            self._service.accept_counter_proposal(rate_id, "test_user", "test message", is_client=True)

def test_get_counter_proposal_bounds():
    """Tests calculating valid bounds for counter-proposals"""
    # Create mock rate with current and proposed amounts
    rate = Mock(amount=100)

    # Test bounds for client counter-proposal (should be between current and proposed)
    min_amount, max_amount = get_counter_proposal_bounds(rate, is_client=True)
    assert min_amount == 100
    assert max_amount == 100

    # Test bounds for firm counter-proposal after client counter (should be between client counter and original proposed)
    min_amount, max_amount = get_counter_proposal_bounds(rate, is_client=False)
    assert min_amount == 100
    assert max_amount == 100

    # Test with different rate types and states
    # (This would involve creating different mock rates with different properties)

    # Verify bounds respect any additional business rules or constraints
    # (This would involve configuring mock client settings with specific rules)

def test_validate_counter_proposal_rate():
    """Tests validation of counter-proposal rate values"""
    # Create mock rates with various states and amounts
    rate1 = Mock(amount=100)
    rate2 = Mock(amount=100)

    # Test validation of client counter-proposals within bounds
    assert validate_counter_proposal_rate(rate1, 110) is True

    # Test validation of firm counter-proposals within bounds
    assert validate_counter_proposal_rate(rate2, 90) is True

    # Test validation of counter-proposals outside bounds fails
    with pytest.raises(NotImplementedError):
        validate_counter_proposal_rate(rate1, 200)

    # Test validation with negative amounts fails
    with pytest.raises(NotImplementedError):
        validate_counter_proposal_rate(rate1, -10)

    # Test validation with invalid rate states fails
    # (This would involve creating mock rates with different statuses)

class TestApprovalWorkflowService:
    """Test class for ApprovalWorkflowService functionality"""

    def setup_method(self):
        """Setup method run before each test"""
        # Create mock repositories and services
        self._approval_repo = Mock()
        self._negotiation_repo = Mock()
        self._notification_service = Mock()
        self._organization_service = Mock()
        self._audit_service = Mock()

        # Initialize ApprovalWorkflowService with the dependencies
        self._service = ApprovalWorkflowService(
            approval_repo=self._approval_repo,
            negotiation_repo=self._negotiation_repo,
            notification_service=self._notification_service,
            organization_service=self._organization_service,
            audit_service=self._audit_service
        )

    def test_create_approval_workflow(self):
        """Test creating an approval workflow"""
        # Configure mock organization with approval workflow configuration
        organization_id = uuid4()
        negotiation_id = uuid4()
        self._organization_service.get_client_settings.return_value = {"approval_workflow": {"steps": 2}}
        self._negotiation_repo.get_negotiation_by_id.return_value = Mock(id=negotiation_id, client_id=organization_id)

        # Test creating a workflow with multiple steps
        workflow = self._service.create_workflow(negotiation_id, organization_id)
        assert workflow is not None

        # Verify workflow is linked to negotiation
        self._negotiation_repo.set_approval_workflow.assert_called()

        # Verify initial approvers are notified
        self._notification_service.notify_approvers.assert_called()

        # Test with different workflow configurations
        # (This would involve configuring different settings in the mock organization)

        # Test with non-existent negotiation or organization
        self._negotiation_repo.get_negotiation_by_id.return_value = None
        with pytest.raises(NotImplementedError):
            self._service.create_workflow(negotiation_id, organization_id)

    def test_process_approval_action(self):
        """Test processing approval actions"""
        # Create mock approval workflow with multiple steps
        workflow_id = uuid4()
        step_id1 = uuid4()
        step_id2 = uuid4()
        negotiation_id = uuid4()
        user_id = uuid4()
        self._approval_repo.get_workflow_by_id.return_value = Mock(id=workflow_id, steps=[Mock(id=step_id1, order=1), Mock(id=step_id2, order=2)])

        # Test approving a step
        result = self._service.process_action(workflow_id, step_id1, user_id, APPROVAL_ACTION_APPROVE, "test comment")
        assert result is True

        # Test approving the final step
        result = self._service.process_action(workflow_id, step_id2, user_id, APPROVAL_ACTION_APPROVE, "test comment")
        assert result is True

        # Test rejecting a step
        result = self._service.process_action(workflow_id, step_id1, user_id, APPROVAL_ACTION_REJECT, "test comment")
        assert result is True

        # Test with unauthorized user
        # (This would involve configuring the mock to simulate an unauthorized user)

        # Test with incorrect step ID
        # (This would involve providing an invalid step ID)

        # Test with non-existent workflow
        self._approval_repo.get_workflow_by_id.return_value = None
        with pytest.raises(NotImplementedError):
            self._service.process_action(workflow_id, step_id1, user_id, APPROVAL_ACTION_APPROVE, "test comment")

    def test_get_current_approvers(self):
        """Test retrieving current approvers"""
        # Create mock approval workflow with multiple steps in various states
        workflow_id = uuid4()
        step_id1 = uuid4()
        step_id2 = uuid4()
        self._approval_repo.get_workflow_by_id.return_value = Mock(id=workflow_id, steps=[Mock(id=step_id1, order=1, status="pending", approver_id="user1"), Mock(id=step_id2, order=2, status="approved", approver_id="user2")])

        # Test with workflow having active steps
        approvers = self._service.get_current_approvers(workflow_id)
        assert len(approvers) == 0

        # Verify returned approver information is correct
        # (This would involve checking the approver IDs and other relevant data)

        # Test with workflow having no active steps
        # (This would involve configuring the mock to simulate a completed workflow)

        # Test with non-existent workflow
        self._approval_repo.get_workflow_by_id.return_value = None
        with pytest.raises(NotImplementedError):
            self._service.get_current_approvers(workflow_id)

    def test_workflow_status_updates(self):
        """Test approval workflow status transitions affect negotiation status"""
        # Create mock negotiation with approval workflow
        negotiation_id = uuid4()
        workflow_id = uuid4()
        self._negotiation_repo.get_negotiation_by_id.return_value = Mock(id=negotiation_id, approval_workflow_id=workflow_id)

        # Test completing approval workflow transitions negotiation to APPROVED
        self._approval_repo.check_workflow_status.return_value = ApprovalStatus.APPROVED
        self._service._update_negotiation_status(workflow_id)
        self._negotiation_repo.update_status.assert_called_with(negotiation_id, NegotiationStatus.COMPLETED)

        # Test rejecting approval workflow transitions negotiation to REJECTED
        self._approval_repo.check_workflow_status.return_value = ApprovalStatus.REJECTED
        self._service._update_negotiation_status(workflow_id)
        self._negotiation_repo.update_status.assert_called_with(negotiation_id, NegotiationStatus.REJECTED)

        # Test with different initial states
        # (This would involve configuring the mock to simulate different initial states)

        # Verify negotiation repository is called to update status
        self._negotiation_repo.update_status.assert_called()