"""
SQLAlchemy ORM models for approval workflows in the Justice Bid Rate Negotiation System.

This module defines the database models for configurable approval workflows, allowing
both clients and law firms to define multi-step approval processes for rate negotiations.
The models track approval steps, criteria, and maintain a complete history of all approval actions.
"""

import uuid
import datetime
from typing import Optional, List, Dict, Any, Union
import enum

from sqlalchemy import Column, String, ForeignKey, Enum, Table, relationship
from sqlalchemy import DateTime, Boolean, Integer
from sqlalchemy.types import UUID
from sqlalchemy.dialects.postgresql import JSONB

from ..base import Base
from .common import BaseModel, TimestampMixin, AuditMixin, OrganizationScopedMixin
from ...utils.constants import ApprovalStatus, OrganizationType


class WorkflowType(enum.Enum):
    """Enumeration of workflow types in the system."""
    CLIENT = "client"
    LAW_FIRM = "law_firm"


class ApprovalWorkflow(BaseModel, TimestampMixin, AuditMixin, OrganizationScopedMixin):
    """
    SQLAlchemy model representing a configurable approval workflow for rate negotiations.
    
    Organizations can define custom approval flows with multiple steps, criteria, and approvers.
    Each workflow can be associated with specific entities (firms, clients, or groups) and
    will be triggered based on defined criteria during the rate negotiation process.
    """
    __tablename__ = "approval_workflows"

    id = Column(UUID, primary_key=True, default=uuid.uuid4)
    organization_id = Column(UUID, ForeignKey('organizations.id'), nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(String(1000), nullable=True)
    type = Column(Enum(WorkflowType), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    criteria = Column(JSONB, nullable=True)  # JSON defining when this workflow applies
    applicable_entities = Column(JSONB, nullable=True)  # JSON defining which entities this applies to
    
    # Relationships
    organization = relationship('Organization', back_populates='approval_workflows')
    steps = relationship('ApprovalStep', back_populates='workflow', cascade='all, delete-orphan')
    negotiations = relationship('Negotiation', back_populates='approval_workflow')

    def __init__(self, organization_id: uuid.UUID, name: str, type: WorkflowType, description: str = None):
        """
        Initialize a new ApprovalWorkflow instance.
        
        Args:
            organization_id: UUID of the organization that owns this workflow
            name: Name of the workflow
            type: Type of workflow (CLIENT or LAW_FIRM)
            description: Optional description of the workflow
        """
        self.organization_id = organization_id
        self.name = name
        self.type = type
        self.description = description
        self.criteria = {}
        self.applicable_entities = {}
        self.is_active = True

    def add_step(self, order: int, approver_id: Optional[uuid.UUID] = None, 
                 approver_role: Optional[str] = None, is_required: bool = True,
                 timeout_hours: Optional[int] = None) -> 'ApprovalStep':
        """
        Add a new approval step to the workflow.
        
        Args:
            order: Position of this step in the approval sequence
            approver_id: UUID of the user who should approve (if specific user)
            approver_role: Role that should approve (if role-based)
            is_required: Whether this step is required or optional
            timeout_hours: Number of hours before step times out
            
        Returns:
            The newly created approval step
        """
        step = ApprovalStep(
            workflow_id=self.id,
            order=order,
            approver_id=approver_id,
            approver_role=approver_role,
            is_required=is_required,
            timeout_hours=timeout_hours
        )
        self.steps.append(step)
        return step

    def remove_step(self, step_id: uuid.UUID) -> bool:
        """
        Remove an approval step from the workflow.
        
        Args:
            step_id: UUID of the step to remove
            
        Returns:
            True if step was removed, False if not found
        """
        for step in self.steps:
            if step.id == step_id:
                self.steps.remove(step)
                return True
        return False

    def set_criteria(self, criteria_dict: Dict[str, Any]) -> None:
        """
        Set the criteria that determine when this workflow applies.
        
        Args:
            criteria_dict: Dictionary containing criteria configurations
        """
        self.criteria = criteria_dict

    def set_applicable_entities(self, entities_dict: Dict[str, Any]) -> None:
        """
        Set the entities (firms, clients, or groups) this workflow applies to.
        
        Args:
            entities_dict: Dictionary mapping entity types to lists of entity IDs
        """
        self.applicable_entities = entities_dict

    def is_applicable(self, entity_id: uuid.UUID, conditions: Dict[str, Any]) -> bool:
        """
        Check if this workflow applies to a given entity and conditions.
        
        Args:
            entity_id: UUID of the entity (firm or client) to check
            conditions: Dictionary of conditions to check against criteria
            
        Returns:
            True if workflow applies, False otherwise
        """
        # First check if entity is in applicable entities
        entity_applies = False
        
        if not self.applicable_entities:
            return False
            
        # Check direct entity application
        entity_types = ["firms", "clients", "groups"]
        for entity_type in entity_types:
            if entity_type in self.applicable_entities:
                if str(entity_id) in self.applicable_entities[entity_type]:
                    entity_applies = True
                    break
                    
        if not entity_applies:
            # Check if entity belongs to any applicable group
            # This would require additional logic to check group membership
            pass
            
        if not entity_applies:
            return False
            
        # Then check if conditions match criteria
        if not self.criteria:
            # If no criteria defined, workflow applies to all conditions
            return True
            
        # Implement criteria matching logic here based on the criteria structure
        # This would vary based on the specific criteria schema implemented
        
        return True  # Simplified for now

    def get_steps_in_order(self) -> List['ApprovalStep']:
        """
        Get all workflow steps sorted by their order.
        
        Returns:
            List of ApprovalStep objects in order
        """
        return sorted(self.steps, key=lambda step: step.order)

    def activate(self) -> None:
        """Activate the workflow."""
        self.is_active = True

    def deactivate(self) -> None:
        """Deactivate the workflow."""
        self.is_active = False


class ApprovalStep(BaseModel, TimestampMixin):
    """
    SQLAlchemy model representing a step within an approval workflow.
    
    Each step identifies an approver (by user ID or role) and their position in the
    approval sequence. Steps can be required or optional and may have timeout periods.
    """
    __tablename__ = "approval_steps"

    id = Column(UUID, primary_key=True, default=uuid.uuid4)
    workflow_id = Column(UUID, ForeignKey('approval_workflows.id'), nullable=False)
    order = Column(Integer, nullable=False)
    approver_id = Column(UUID, ForeignKey('users.id'), nullable=True)
    approver_role = Column(String(255), nullable=True)  # Role-based approval
    is_required = Column(Boolean, default=True, nullable=False)
    timeout_hours = Column(Integer, nullable=True)  # Timeout before auto-skip/escalation
    
    # Relationships
    workflow = relationship('ApprovalWorkflow', back_populates='steps')
    approver = relationship('User', foreign_keys=[approver_id])
    histories = relationship('ApprovalHistory', back_populates='step')
    negotiations = relationship('Negotiation', back_populates='approval_steps')

    def __init__(self, workflow_id: uuid.UUID, order: int, 
                 approver_id: Optional[uuid.UUID] = None, 
                 approver_role: Optional[str] = None,
                 is_required: bool = True,
                 timeout_hours: Optional[int] = None):
        """
        Initialize a new ApprovalStep instance.
        
        Args:
            workflow_id: UUID of the parent workflow
            order: Position of this step in the approval sequence
            approver_id: UUID of the user who should approve (if specific user)
            approver_role: Role that should approve (if role-based)
            is_required: Whether this step is required or optional
            timeout_hours: Number of hours before step times out
        """
        self.workflow_id = workflow_id
        self.order = order
        self.approver_id = approver_id
        self.approver_role = approver_role
        
        # Ensure that at least one of approver_id or approver_role is provided
        if approver_id is None and approver_role is None:
            raise ValueError("Either approver_id or approver_role must be provided")
            
        self.is_required = is_required
        self.timeout_hours = timeout_hours


class ApprovalHistory(BaseModel, TimestampMixin):
    """
    SQLAlchemy model representing a historical record of approval actions within a workflow.
    
    Tracks approvals, rejections, and information requests with complete audit trail,
    including the user who took the action, timestamp, and any comments provided.
    """
    __tablename__ = "approval_histories"

    id = Column(UUID, primary_key=True, default=uuid.uuid4)
    negotiation_id = Column(UUID, ForeignKey('negotiations.id'), nullable=False)
    step_id = Column(UUID, ForeignKey('approval_steps.id'), nullable=False)
    user_id = Column(UUID, ForeignKey('users.id'), nullable=False)
    status = Column(Enum(ApprovalStatus), nullable=False)
    comments = Column(String(1000), nullable=True)
    action_date = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    
    # Relationships
    negotiation = relationship('Negotiation', back_populates='approval_histories')
    step = relationship('ApprovalStep', back_populates='histories')
    user = relationship('User', foreign_keys=[user_id])

    def __init__(self, negotiation_id: uuid.UUID, step_id: uuid.UUID, 
                 user_id: uuid.UUID, status: ApprovalStatus, comments: str = None):
        """
        Initialize a new ApprovalHistory instance.
        
        Args:
            negotiation_id: UUID of the associated negotiation
            step_id: UUID of the approval step this history relates to
            user_id: UUID of the user who took the action
            status: Status of the approval action (APPROVED, REJECTED, etc.)
            comments: Optional comments provided with the action
        """
        self.negotiation_id = negotiation_id
        self.step_id = step_id
        self.user_id = user_id
        self.status = status
        self.comments = comments
        self.action_date = datetime.datetime.utcnow()