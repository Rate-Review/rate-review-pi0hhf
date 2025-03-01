"""
SQLAlchemy ORM model defining the negotiation entity in the Justice Bid Rate Negotiation System.
This model represents the core rate negotiation process between law firms and clients,
tracking the negotiation status, associated rates, approval workflows, and messaging.
"""

import uuid
from datetime import datetime, date
from typing import List, Dict, Any, Optional, Union

from sqlalchemy import Column, String, ForeignKey, Enum, Table, relationship
from sqlalchemy.types import UUID
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy import DateTime, Date

from ..base import Base
from .common import BaseModel, TimestampMixin, AuditMixin
from ...utils.constants import NegotiationStatus, ApprovalStatus


# Association table for the many-to-many relationship between negotiations and rates
negotiation_rates = Table(
    'negotiation_rates',
    Base.metadata,
    Column('negotiation_id', UUID, ForeignKey('negotiations.id'), primary_key=True),
    Column('rate_id', UUID, ForeignKey('rates.id'), primary_key=True)
)


class Negotiation(BaseModel, TimestampMixin, AuditMixin):
    """
    SQLAlchemy model representing a rate negotiation between a client and a law firm.
    Tracks the entire negotiation process from request through submission, approval, and completion.
    """
    __tablename__ = 'negotiations'
    
    # Foreign keys
    client_id = Column(UUID, ForeignKey('organizations.id'), nullable=False)
    firm_id = Column(UUID, ForeignKey('organizations.id'), nullable=False)
    
    # Status tracking
    status = Column(Enum(NegotiationStatus), nullable=False, default=NegotiationStatus.REQUESTED)
    
    # Dates
    request_date = Column(Date, nullable=False)
    submission_deadline = Column(Date, nullable=True)
    completion_date = Column(Date, nullable=True)
    
    # Approval workflow
    approval_workflow_id = Column(UUID, ForeignKey('approval_workflows.id'), nullable=True)
    approval_status = Column(Enum(ApprovalStatus), nullable=True)
    
    # Flexible data storage
    metadata = Column(JSONB, nullable=True)  # Additional configurable fields
    history = Column(JSONB, nullable=True)   # Audit history of changes
    
    # Relationships
    client = relationship('Organization', foreign_keys=[client_id], back_populates='client_negotiations')
    firm = relationship('Organization', foreign_keys=[firm_id], back_populates='firm_negotiations')
    rates = relationship('Rate', secondary=negotiation_rates, back_populates='negotiations')
    messages = relationship('Message', back_populates='negotiation')
    approval_workflow = relationship('ApprovalWorkflow', back_populates='negotiations')
    approval_steps = relationship('ApprovalStep', back_populates='negotiation')
    
    def __init__(
        self,
        client_id: uuid.UUID,
        firm_id: uuid.UUID,
        status: NegotiationStatus = NegotiationStatus.REQUESTED,
        request_date: date = None,
        submission_deadline: date = None
    ):
        """
        Initialize a new Negotiation instance.
        
        Args:
            client_id: UUID of the client organization
            firm_id: UUID of the law firm organization
            status: Initial negotiation status (defaults to REQUESTED)
            request_date: Date the negotiation was requested (defaults to today)
            submission_deadline: Optional deadline for rate submission
        """
        super().__init__()
        self.client_id = client_id
        self.firm_id = firm_id
        self.status = status
        self.request_date = request_date or date.today()
        self.submission_deadline = submission_deadline
        self.history = []
        self.metadata = {}
    
    def add_rate(self, rate: 'Rate') -> None:
        """
        Add a rate to this negotiation.
        
        Args:
            rate: The Rate object to add to the negotiation
            
        Raises:
            ValueError: If the rate doesn't match the client and firm
        """
        # Validate that rate belongs to this client and firm
        if rate.client_id != self.client_id or rate.firm_id != self.firm_id:
            raise ValueError("Rate must belong to the same client and firm as the negotiation")
        
        # Add to rates if not already present
        if rate not in self.rates:
            self.rates.append(rate)
            self.add_history_entry(
                action="rate_added",
                user_id=None,
                comment=f"Added rate for attorney {rate.attorney_id}",
                metadata={"rate_id": str(rate.id)}
            )
    
    def remove_rate(self, rate: 'Rate') -> None:
        """
        Remove a rate from this negotiation.
        
        Args:
            rate: The Rate object to remove from the negotiation
        """
        if rate in self.rates:
            self.rates.remove(rate)
            self.add_history_entry(
                action="rate_removed",
                user_id=None,
                comment=f"Removed rate for attorney {rate.attorney_id}",
                metadata={"rate_id": str(rate.id)}
            )
    
    def update_status(self, new_status: NegotiationStatus, updated_by_id: uuid.UUID, comment: str = None) -> bool:
        """
        Update the negotiation status with validation of state transitions.
        
        Args:
            new_status: The new status to set
            updated_by_id: UUID of the user making the change
            comment: Optional comment explaining the status change
            
        Returns:
            bool: True if the status was updated successfully
        """
        # Define valid status transitions
        valid_transitions = {
            NegotiationStatus.REQUESTED: [NegotiationStatus.IN_PROGRESS, NegotiationStatus.REJECTED],
            NegotiationStatus.IN_PROGRESS: [NegotiationStatus.COMPLETED, NegotiationStatus.REJECTED],
            NegotiationStatus.COMPLETED: [],  # Terminal state
            NegotiationStatus.REJECTED: []    # Terminal state
        }
        
        # Check if transition is valid
        if new_status not in valid_transitions.get(self.status, []):
            return False
        
        # Update status
        old_status = self.status
        self.status = new_status
        
        # If completing, set completion date
        if new_status == NegotiationStatus.COMPLETED:
            self.completion_date = date.today()
        
        # Record history
        self.add_history_entry(
            action="status_updated",
            user_id=updated_by_id,
            comment=comment or f"Status changed from {old_status.value} to {new_status.value}",
            metadata={"old_status": old_status.value, "new_status": new_status.value}
        )
        
        return True
    
    def set_deadline(self, deadline: date, updated_by_id: uuid.UUID) -> None:
        """
        Set or update the submission deadline.
        
        Args:
            deadline: The new deadline date
            updated_by_id: UUID of the user making the change
            
        Raises:
            ValueError: If the deadline is in the past
        """
        if deadline < date.today():
            raise ValueError("Deadline cannot be in the past")
        
        old_deadline = self.submission_deadline
        self.submission_deadline = deadline
        
        self.add_history_entry(
            action="deadline_updated",
            user_id=updated_by_id,
            comment=f"Submission deadline updated to {deadline}",
            metadata={
                "old_deadline": old_deadline.isoformat() if old_deadline else None,
                "new_deadline": deadline.isoformat()
            }
        )
    
    def is_overdue(self) -> bool:
        """
        Check if the negotiation is past its submission deadline.
        
        Returns:
            bool: True if past deadline, False otherwise
        """
        if not self.submission_deadline:
            return False
        
        return date.today() > self.submission_deadline
    
    def set_approval_workflow(self, workflow: 'ApprovalWorkflow', updated_by_id: uuid.UUID) -> None:
        """
        Assign an approval workflow to this negotiation.
        
        Args:
            workflow: The ApprovalWorkflow instance to assign
            updated_by_id: UUID of the user making the change
            
        Raises:
            ValueError: If the workflow doesn't belong to the client organization
        """
        # Validate workflow belongs to the client
        if workflow.organization_id != self.client_id:
            raise ValueError("Approval workflow must belong to the client organization")
        
        self.approval_workflow = workflow
        self.approval_workflow_id = workflow.id
        self.approval_status = ApprovalStatus.PENDING
        
        self.add_history_entry(
            action="workflow_assigned",
            user_id=updated_by_id,
            comment=f"Approval workflow assigned: {workflow.name}",
            metadata={"workflow_id": str(workflow.id)}
        )
    
    def update_approval_status(self, new_status: ApprovalStatus, updated_by_id: uuid.UUID, comment: str = None) -> bool:
        """
        Update the approval status of the negotiation.
        
        Args:
            new_status: The new approval status to set
            updated_by_id: UUID of the user making the change
            comment: Optional comment explaining the status change
            
        Returns:
            bool: True if the status was updated successfully
            
        Raises:
            ValueError: If no approval workflow is assigned
        """
        if not self.approval_workflow_id:
            raise ValueError("No approval workflow assigned to this negotiation")
        
        # Define valid status transitions
        valid_transitions = {
            ApprovalStatus.PENDING: [ApprovalStatus.IN_PROGRESS, ApprovalStatus.REJECTED],
            ApprovalStatus.IN_PROGRESS: [ApprovalStatus.APPROVED, ApprovalStatus.REJECTED],
            ApprovalStatus.APPROVED: [],  # Terminal state
            ApprovalStatus.REJECTED: []   # Terminal state
        }
        
        # Check if transition is valid
        if new_status not in valid_transitions.get(self.approval_status, []):
            return False
        
        # Update status
        old_status = self.approval_status
        self.approval_status = new_status
        
        # If approved or rejected, update negotiation status accordingly
        if new_status == ApprovalStatus.APPROVED:
            self.update_status(NegotiationStatus.COMPLETED, updated_by_id, "Approved through workflow")
        elif new_status == ApprovalStatus.REJECTED:
            self.update_status(NegotiationStatus.REJECTED, updated_by_id, "Rejected through workflow")
        
        # Record history
        self.add_history_entry(
            action="approval_status_updated",
            user_id=updated_by_id,
            comment=comment or f"Approval status changed from {old_status.value} to {new_status.value}",
            metadata={"old_status": old_status.value, "new_status": new_status.value}
        )
        
        return True
    
    def create_approval_step(self, level: int, approver_id: uuid.UUID) -> 'ApprovalStep':
        """
        Create a new approval step for this negotiation.
        
        Args:
            level: The approval level (order of approval)
            approver_id: UUID of the user who will approve this step
            
        Returns:
            ApprovalStep: The newly created approval step
            
        Raises:
            ValueError: If no approval workflow is assigned
        """
        if not self.approval_workflow_id:
            raise ValueError("No approval workflow assigned to this negotiation")
        
        # This would normally import the ApprovalStep model, but for demonstration:
        from .approval import ApprovalStep
        
        step = ApprovalStep(
            negotiation_id=self.id,
            workflow_id=self.approval_workflow_id,
            level=level,
            approver_id=approver_id
        )
        
        self.approval_steps.append(step)
        return step
    
    def get_current_approval_step(self) -> Optional['ApprovalStep']:
        """
        Get the current active approval step.
        
        Returns:
            ApprovalStep: The current approval step or None if no active steps
        """
        if self.approval_status != ApprovalStatus.IN_PROGRESS:
            return None
        
        # Find the first pending step ordered by level
        from sqlalchemy import asc
        from .approval import ApprovalStep, ApprovalStepStatus
        
        # This would normally be a query, but for demonstration:
        for step in sorted(self.approval_steps, key=lambda s: s.level):
            if step.status == ApprovalStepStatus.PENDING:
                return step
        
        return None
    
    def add_message(
        self,
        sender_id: uuid.UUID,
        recipient_ids: List[uuid.UUID],
        content: str,
        attachments: List[Dict] = None
    ) -> 'Message':
        """
        Add a message to this negotiation.
        
        Args:
            sender_id: UUID of the message sender
            recipient_ids: List of UUIDs of the message recipients
            content: The message text content
            attachments: Optional list of attachment metadata
            
        Returns:
            Message: The newly created message
        """
        # This would normally import the Message model, but for demonstration:
        from .message import Message, RelatedEntityType
        
        message = Message(
            thread_id=self.id,  # Use negotiation ID as thread ID
            sender_id=sender_id,
            recipient_ids=recipient_ids,
            content=content,
            attachments=attachments or [],
            related_entity_type=RelatedEntityType.NEGOTIATION,
            related_entity_id=self.id
        )
        
        self.messages.append(message)
        return message
    
    def get_history(self) -> List[Dict[str, Any]]:
        """
        Get the complete history of this negotiation.
        
        Returns:
            list: List of historical events for this negotiation
        """
        if not self.history:
            return []
        
        # Sort by timestamp
        return sorted(self.history, key=lambda entry: entry.get('timestamp', ''))
    
    def add_history_entry(
        self,
        action: str,
        user_id: Optional[uuid.UUID],
        comment: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Add an entry to the negotiation history.
        
        Args:
            action: The type of action that occurred
            user_id: UUID of the user who performed the action (can be None for system actions)
            comment: Optional description of the action
            metadata: Optional additional data about the action
        """
        if self.history is None:
            self.history = []
        
        entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "action": action,
            "user_id": str(user_id) if user_id else None,
            "comment": comment,
            "metadata": metadata or {}
        }
        
        self.history.append(entry)
    
    def get_rates_by_status(self, status: 'RateStatus') -> List['Rate']:
        """
        Get rates filtered by their status.
        
        Args:
            status: The rate status to filter by
            
        Returns:
            list: List of rates with the specified status
        """
        return [rate for rate in self.rates if rate.status == status]