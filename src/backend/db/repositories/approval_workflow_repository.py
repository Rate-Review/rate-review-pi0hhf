"""
Repository class that provides data access layer for the ApprovalWorkflow, ApprovalStep, and ApprovalHistory 
models in the Justice Bid Rate Negotiation System. Handles CRUD operations, workflow queries, and facilitates 
approval processes with proper validation and error handling.
"""

import uuid
from typing import List, Dict, Optional, Any, Union
from datetime import datetime

from sqlalchemy import or_, and_, desc, asc
from sqlalchemy.orm import Session

from ..models.approval_workflow import ApprovalWorkflow, ApprovalStep, ApprovalHistory, WorkflowType
from ..session import session_scope, get_db
from ...utils.logging import get_logger
from ...utils.constants import ApprovalStatus
from ...utils.validators import validate_required, validate_string
from ..models.negotiation import Negotiation

# Set up logger
logger = get_logger(__name__, 'repository')

def get_applicable_workflows(
    db_session: Session,
    entity_id: uuid.UUID,
    conditions: dict,
    workflow_type: WorkflowType,
    organization_id: Optional[uuid.UUID] = None
) -> List[ApprovalWorkflow]:
    """
    Find approval workflows applicable to a given entity and conditions.
    
    Args:
        db_session: Database session
        entity_id: UUID of the entity (firm, client, etc.)
        conditions: Dictionary of conditions to match against workflow criteria
        workflow_type: Type of workflow to find (CLIENT or LAW_FIRM)
        organization_id: Optional organization ID to filter by
        
    Returns:
        List of applicable workflows sorted by priority
    """
    try:
        # Build query for workflow type
        query = db_session.query(ApprovalWorkflow).filter(
            ApprovalWorkflow.type == workflow_type,
            ApprovalWorkflow.is_active == True
        )
        
        # Filter by organization if provided
        if organization_id:
            query = query.filter(ApprovalWorkflow.organization_id == organization_id)
        
        # Execute query to get potential workflows
        potential_workflows = query.all()
        
        # Filter workflows where is_applicable returns True for the entity and conditions
        applicable_workflows = [
            workflow for workflow in potential_workflows 
            if workflow.is_applicable(entity_id, conditions)
        ]
        
        # Sort workflows by priority if available in criteria
        applicable_workflows.sort(
            key=lambda w: w.criteria.get('priority', 999) if w.criteria else 999
        )
        
        return applicable_workflows
        
    except Exception as e:
        logger.error(f"Error finding applicable workflows: {str(e)}")
        return []


def auto_assign_workflow(db_session: Session, negotiation: Negotiation) -> Optional[ApprovalWorkflow]:
    """
    Automatically assign the most appropriate workflow to a negotiation.
    
    Args:
        db_session: Database session
        negotiation: Negotiation instance to assign a workflow to
        
    Returns:
        The assigned workflow if successful, None otherwise
    """
    try:
        # Determine workflow type (typically CLIENT for rate approval)
        workflow_type = WorkflowType.CLIENT
        
        # Get client and firm IDs
        client_id = negotiation.client_id
        firm_id = negotiation.firm_id
        
        # Build conditions from negotiation attributes
        conditions = {
            'firm_id': str(firm_id),
            'rate_count': len(negotiation.rates) if negotiation.rates else 0,
            # Additional conditions could be added based on rates, amounts, etc.
        }
        
        # Find applicable workflows
        workflows = get_applicable_workflows(
            db_session, 
            client_id,  # Use client as the entity
            conditions,
            workflow_type,
            client_id   # Filter by client organization
        )
        
        if not workflows:
            logger.info(f"No applicable workflows found for negotiation {negotiation.id}")
            return None
        
        # Select the first (highest priority) workflow
        selected_workflow = workflows[0]
        
        # Assign to negotiation
        negotiation.approval_workflow_id = selected_workflow.id
        negotiation.approval_status = ApprovalStatus.PENDING
        
        # Commit the changes
        db_session.commit()
        
        logger.info(f"Auto-assigned workflow {selected_workflow.id} to negotiation {negotiation.id}")
        return selected_workflow
        
    except Exception as e:
        logger.error(f"Error auto-assigning workflow: {str(e)}")
        db_session.rollback()
        return None


class ApprovalWorkflowRepository:
    """
    Repository class for managing ApprovalWorkflow, ApprovalStep, and ApprovalHistory entities in the database.
    
    Provides methods for creating, retrieving, updating, and deleting approval workflows,
    as well as managing approval steps, processing approvals, and tracking approval history.
    """
    
    def __init__(self, db_session: Session):
        """
        Initialize a new ApprovalWorkflowRepository with a database session.
        
        Args:
            db_session: SQLAlchemy database session
        """
        self._db = db_session
    
    def get_by_id(self, workflow_id: uuid.UUID) -> Optional[ApprovalWorkflow]:
        """
        Get an approval workflow by its ID.
        
        Args:
            workflow_id: UUID of the workflow to retrieve
            
        Returns:
            Workflow if found, None otherwise
        """
        try:
            return self._db.query(ApprovalWorkflow).filter(
                ApprovalWorkflow.id == workflow_id
            ).first()
        except Exception as e:
            logger.error(f"Error retrieving workflow {workflow_id}: {str(e)}")
            return None
    
    def get_by_organization(
        self,
        organization_id: uuid.UUID,
        workflow_type: Optional[WorkflowType] = None,
        active_only: bool = True,
        limit: int = 100,
        offset: int = 0
    ) -> List[ApprovalWorkflow]:
        """
        Get all approval workflows for an organization.
        
        Args:
            organization_id: UUID of the organization
            workflow_type: Optional filter by workflow type
            active_only: Whether to return only active workflows
            limit: Maximum number of workflows to return
            offset: Offset for pagination
            
        Returns:
            List of workflows belonging to the organization
        """
        try:
            query = self._db.query(ApprovalWorkflow).filter(
                ApprovalWorkflow.organization_id == organization_id
            )
            
            if workflow_type:
                query = query.filter(ApprovalWorkflow.type == workflow_type)
                
            if active_only:
                query = query.filter(ApprovalWorkflow.is_active == True)
            
            # Apply pagination
            query = query.limit(limit).offset(offset)
            
            return query.all()
        except Exception as e:
            logger.error(f"Error retrieving workflows for organization {organization_id}: {str(e)}")
            return []
    
    def create(
        self,
        organization_id: uuid.UUID,
        name: str,
        workflow_type: WorkflowType,
        description: Optional[str] = None,
        criteria: Optional[dict] = None,
        applicable_entities: Optional[dict] = None
    ) -> ApprovalWorkflow:
        """
        Create a new approval workflow.
        
        Args:
            organization_id: UUID of the organization that owns the workflow
            name: Name of the workflow
            workflow_type: Type of workflow (CLIENT or LAW_FIRM)
            description: Optional description of the workflow
            criteria: Optional criteria for when this workflow applies
            applicable_entities: Optional dict of entities this workflow applies to
            
        Returns:
            Newly created workflow
            
        Raises:
            ValueError: If validation fails
        """
        try:
            # Validate required fields
            validate_required(organization_id, "organization_id")
            validate_required(name, "name")
            validate_required(workflow_type, "workflow_type")
            validate_string(name, "name", min_length=3, max_length=255)
            
            if description:
                validate_string(description, "description", max_length=1000)
            
            # Create workflow
            workflow = ApprovalWorkflow(
                organization_id=organization_id,
                name=name,
                type=workflow_type,
                description=description
            )
            
            # Set criteria if provided
            if criteria:
                workflow.criteria = criteria
            
            # Set applicable entities if provided
            if applicable_entities:
                workflow.applicable_entities = applicable_entities
            
            # Add to database and commit
            self._db.add(workflow)
            self._db.commit()
            
            logger.info(f"Created approval workflow {workflow.id} for organization {organization_id}")
            return workflow
            
        except ValueError as e:
            logger.error(f"Validation error creating workflow: {str(e)}")
            self._db.rollback()
            raise
        except Exception as e:
            logger.error(f"Error creating workflow: {str(e)}")
            self._db.rollback()
            raise ValueError(f"Failed to create workflow: {str(e)}")
    
    def update(self, workflow_id: uuid.UUID, update_data: dict) -> Optional[ApprovalWorkflow]:
        """
        Update an existing approval workflow.
        
        Args:
            workflow_id: UUID of the workflow to update
            update_data: Dictionary of fields to update
            
        Returns:
            Updated workflow if successful, None if not found
            
        Raises:
            ValueError: If validation fails
        """
        try:
            workflow = self.get_by_id(workflow_id)
            if not workflow:
                logger.warning(f"Workflow {workflow_id} not found for update")
                return None
            
            # Update allowed fields
            if 'name' in update_data:
                validate_string(update_data['name'], "name", min_length=3, max_length=255)
                workflow.name = update_data['name']
                
            if 'description' in update_data:
                if update_data['description']:
                    validate_string(update_data['description'], "description", max_length=1000)
                workflow.description = update_data['description']
                
            if 'criteria' in update_data:
                workflow.criteria = update_data['criteria'] or {}
                
            if 'applicable_entities' in update_data:
                workflow.applicable_entities = update_data['applicable_entities'] or {}
                
            if 'is_active' in update_data:
                workflow.is_active = bool(update_data['is_active'])
            
            # Commit changes
            self._db.commit()
            
            logger.info(f"Updated workflow {workflow_id}")
            return workflow
            
        except ValueError as e:
            logger.error(f"Validation error updating workflow {workflow_id}: {str(e)}")
            self._db.rollback()
            raise
        except Exception as e:
            logger.error(f"Error updating workflow {workflow_id}: {str(e)}")
            self._db.rollback()
            raise ValueError(f"Failed to update workflow: {str(e)}")
    
    def delete(self, workflow_id: uuid.UUID) -> bool:
        """
        Delete an approval workflow.
        
        Args:
            workflow_id: UUID of the workflow to delete
            
        Returns:
            True if successful, False if not found
        """
        try:
            workflow = self.get_by_id(workflow_id)
            if not workflow:
                logger.warning(f"Workflow {workflow_id} not found for deletion")
                return False
            
            self._db.delete(workflow)
            self._db.commit()
            
            logger.info(f"Deleted workflow {workflow_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting workflow {workflow_id}: {str(e)}")
            self._db.rollback()
            return False
    
    def activate(self, workflow_id: uuid.UUID) -> bool:
        """
        Activate an approval workflow.
        
        Args:
            workflow_id: UUID of the workflow to activate
            
        Returns:
            True if successful, False if not found
        """
        try:
            workflow = self.get_by_id(workflow_id)
            if not workflow:
                logger.warning(f"Workflow {workflow_id} not found for activation")
                return False
            
            workflow.is_active = True
            self._db.commit()
            
            logger.info(f"Activated workflow {workflow_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error activating workflow {workflow_id}: {str(e)}")
            self._db.rollback()
            return False
    
    def deactivate(self, workflow_id: uuid.UUID) -> bool:
        """
        Deactivate an approval workflow.
        
        Args:
            workflow_id: UUID of the workflow to deactivate
            
        Returns:
            True if successful, False if not found
        """
        try:
            workflow = self.get_by_id(workflow_id)
            if not workflow:
                logger.warning(f"Workflow {workflow_id} not found for deactivation")
                return False
            
            workflow.is_active = False
            self._db.commit()
            
            logger.info(f"Deactivated workflow {workflow_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error deactivating workflow {workflow_id}: {str(e)}")
            self._db.rollback()
            return False
    
    def add_step(
        self,
        workflow_id: uuid.UUID,
        order: int,
        approver_id: Optional[uuid.UUID] = None,
        approver_role: Optional[str] = None,
        is_required: bool = True,
        timeout_hours: Optional[int] = None
    ) -> Optional[ApprovalStep]:
        """
        Add a new approval step to a workflow.
        
        Args:
            workflow_id: UUID of the workflow to add a step to
            order: Position of this step in the approval sequence
            approver_id: UUID of the user who should approve (if specific user)
            approver_role: Role that should approve (if role-based)
            is_required: Whether this step is required or optional
            timeout_hours: Number of hours before step times out
            
        Returns:
            Created step if successful, None if workflow not found
            
        Raises:
            ValueError: If neither approver_id nor approver_role is provided
        """
        try:
            workflow = self.get_by_id(workflow_id)
            if not workflow:
                logger.warning(f"Workflow {workflow_id} not found for adding step")
                return None
            
            # Validate that at least one of approver_id or approver_role is provided
            if not approver_id and not approver_role:
                raise ValueError("Either approver_id or approver_role must be provided")
            
            # Create step using workflow's add_step method
            step = workflow.add_step(
                order=order,
                approver_id=approver_id,
                approver_role=approver_role,
                is_required=is_required,
                timeout_hours=timeout_hours
            )
            
            # Commit changes
            self._db.commit()
            
            logger.info(f"Added step {step.id} to workflow {workflow_id}")
            return step
            
        except ValueError as e:
            logger.error(f"Validation error adding step to workflow {workflow_id}: {str(e)}")
            self._db.rollback()
            raise
        except Exception as e:
            logger.error(f"Error adding step to workflow {workflow_id}: {str(e)}")
            self._db.rollback()
            raise ValueError(f"Failed to add step: {str(e)}")
    
    def remove_step(self, step_id: uuid.UUID) -> bool:
        """
        Remove an approval step from a workflow.
        
        Args:
            step_id: UUID of the step to remove
            
        Returns:
            True if successful, False if not found
        """
        try:
            step = self.get_step_by_id(step_id)
            if not step:
                logger.warning(f"Step {step_id} not found for removal")
                return False
            
            # Get parent workflow
            workflow = self.get_by_id(step.workflow_id)
            if not workflow:
                logger.warning(f"Parent workflow not found for step {step_id}")
                return False
            
            # Remove the step
            result = workflow.remove_step(step_id)
            if result:
                self._db.commit()
                logger.info(f"Removed step {step_id} from workflow {workflow.id}")
            return result
            
        except Exception as e:
            logger.error(f"Error removing step {step_id}: {str(e)}")
            self._db.rollback()
            return False
    
    def update_step(self, step_id: uuid.UUID, update_data: dict) -> Optional[ApprovalStep]:
        """
        Update an existing approval step.
        
        Args:
            step_id: UUID of the step to update
            update_data: Dictionary of fields to update
            
        Returns:
            Updated step if successful, None if not found
        """
        try:
            step = self.get_step_by_id(step_id)
            if not step:
                logger.warning(f"Step {step_id} not found for update")
                return None
            
            # Update allowed fields
            if 'order' in update_data:
                step.order = int(update_data['order'])
                
            if 'approver_id' in update_data:
                step.approver_id = update_data['approver_id']
                
            if 'approver_role' in update_data:
                step.approver_role = update_data['approver_role']
                
            if 'is_required' in update_data:
                step.is_required = bool(update_data['is_required'])
                
            if 'timeout_hours' in update_data:
                step.timeout_hours = update_data['timeout_hours']
            
            # Ensure at least one of approver_id or approver_role is set
            if not step.approver_id and not step.approver_role:
                raise ValueError("Either approver_id or approver_role must be set")
            
            # Commit changes
            self._db.commit()
            
            logger.info(f"Updated step {step_id}")
            return step
            
        except ValueError as e:
            logger.error(f"Validation error updating step {step_id}: {str(e)}")
            self._db.rollback()
            raise
        except Exception as e:
            logger.error(f"Error updating step {step_id}: {str(e)}")
            self._db.rollback()
            return None
    
    def get_step_by_id(self, step_id: uuid.UUID) -> Optional[ApprovalStep]:
        """
        Get an approval step by its ID.
        
        Args:
            step_id: UUID of the step to retrieve
            
        Returns:
            Step if found, None otherwise
        """
        try:
            return self._db.query(ApprovalStep).filter(
                ApprovalStep.id == step_id
            ).first()
        except Exception as e:
            logger.error(f"Error retrieving step {step_id}: {str(e)}")
            return None
    
    def get_steps_for_workflow(self, workflow_id: uuid.UUID) -> List[ApprovalStep]:
        """
        Get all approval steps for a workflow in order.
        
        Args:
            workflow_id: UUID of the workflow
            
        Returns:
            Ordered list of approval steps
        """
        try:
            workflow = self.get_by_id(workflow_id)
            if not workflow:
                logger.warning(f"Workflow {workflow_id} not found for getting steps")
                return []
            
            # Use the workflow's method to get steps in order
            return workflow.get_steps_in_order()
            
        except Exception as e:
            logger.error(f"Error retrieving steps for workflow {workflow_id}: {str(e)}")
            return []
    
    def create_approval_steps(self, negotiation_id: uuid.UUID, workflow_id: uuid.UUID) -> bool:
        """
        Create approval steps for a specific negotiation based on a workflow.
        
        Args:
            negotiation_id: UUID of the negotiation
            workflow_id: UUID of the workflow to use
            
        Returns:
            True if successful, False if workflow not found
        """
        try:
            # Get the workflow
            workflow = self.get_by_id(workflow_id)
            if not workflow:
                logger.warning(f"Workflow {workflow_id} not found for creating steps")
                return False
            
            # Get workflow steps in order
            steps = self.get_steps_for_workflow(workflow_id)
            
            # Get the negotiation
            negotiation = self._db.query(Negotiation).filter(
                Negotiation.id == negotiation_id
            ).first()
            
            if not negotiation:
                logger.warning(f"Negotiation {negotiation_id} not found for creating approval steps")
                return False
            
            # Create approval history entries for each step
            for step in steps:
                history = ApprovalHistory(
                    negotiation_id=negotiation_id,
                    step_id=step.id,
                    user_id=step.approver_id,  # May be None if role-based
                    status=ApprovalStatus.PENDING
                )
                self._db.add(history)
            
            # Commit changes
            self._db.commit()
            
            logger.info(f"Created approval steps for negotiation {negotiation_id} using workflow {workflow_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error creating approval steps: {str(e)}")
            self._db.rollback()
            return False
    
    def process_approval(
        self,
        step_id: uuid.UUID,
        negotiation_id: uuid.UUID,
        user_id: uuid.UUID,
        status: ApprovalStatus,
        comments: Optional[str] = None
    ) -> bool:
        """
        Process an approval or rejection for a specific step.
        
        Args:
            step_id: UUID of the approval step
            negotiation_id: UUID of the negotiation
            user_id: UUID of the user taking the action
            status: New status (APPROVED or REJECTED)
            comments: Optional comments provided with the action
            
        Returns:
            True if successful, False if validation fails
        """
        try:
            # Get the step
            step = self.get_step_by_id(step_id)
            if not step:
                logger.warning(f"Step {step_id} not found for approval processing")
                return False
            
            # Validate that the user is authorized to approve this step
            if not self.check_approver_permission(step_id, user_id):
                logger.warning(f"User {user_id} not authorized to approve step {step_id}")
                return False
            
            # Get the approval history entry for this step and negotiation
            history = self._db.query(ApprovalHistory).filter(
                ApprovalHistory.negotiation_id == negotiation_id,
                ApprovalHistory.step_id == step_id
            ).first()
            
            # If not found, create a new one
            if not history:
                history = ApprovalHistory(
                    negotiation_id=negotiation_id,
                    step_id=step_id,
                    user_id=user_id,
                    status=status,
                    comments=comments
                )
                self._db.add(history)
            else:
                # Update existing history entry
                history.status = status
                history.user_id = user_id
                if comments:
                    history.comments = comments
                history.action_date = datetime.utcnow()
            
            # Commit changes
            self._db.commit()
            
            # Check if this updates the overall negotiation status
            negotiation = self._db.query(Negotiation).filter(
                Negotiation.id == negotiation_id
            ).first()
            
            if negotiation:
                overall_status = self.check_workflow_status(negotiation_id)
                if overall_status != negotiation.approval_status:
                    negotiation.approval_status = overall_status
                    self._db.commit()
            
            logger.info(f"Processed {status.value} for step {step_id} on negotiation {negotiation_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error processing approval: {str(e)}")
            self._db.rollback()
            return False
    
    def check_workflow_status(self, negotiation_id: uuid.UUID) -> ApprovalStatus:
        """
        Check the overall status of a workflow for a negotiation.
        
        Args:
            negotiation_id: UUID of the negotiation
            
        Returns:
            Overall status of the workflow
        """
        try:
            # Get all approval history entries for the negotiation
            histories = self._db.query(ApprovalHistory).filter(
                ApprovalHistory.negotiation_id == negotiation_id
            ).all()
            
            if not histories:
                return ApprovalStatus.PENDING
            
            # Check if any step is rejected
            if any(h.status == ApprovalStatus.REJECTED for h in histories):
                return ApprovalStatus.REJECTED
            
            # Check if all steps are approved
            if all(h.status == ApprovalStatus.APPROVED for h in histories):
                return ApprovalStatus.APPROVED
            
            # Check if any step is in progress
            if any(h.status == ApprovalStatus.IN_PROGRESS for h in histories):
                return ApprovalStatus.IN_PROGRESS
            
            # Default to pending
            return ApprovalStatus.PENDING
            
        except Exception as e:
            logger.error(f"Error checking workflow status: {str(e)}")
            return ApprovalStatus.PENDING
    
    def get_pending_for_negotiation(self, negotiation_id: uuid.UUID) -> List[ApprovalHistory]:
        """
        Get all pending approval steps for a negotiation.
        
        Args:
            negotiation_id: UUID of the negotiation
            
        Returns:
            List of pending approval history entries
        """
        try:
            # Join ApprovalHistory with ApprovalStep to get the order
            query = self._db.query(ApprovalHistory).join(
                ApprovalStep, ApprovalHistory.step_id == ApprovalStep.id
            ).filter(
                ApprovalHistory.negotiation_id == negotiation_id,
                ApprovalHistory.status == ApprovalStatus.PENDING
            ).order_by(
                ApprovalStep.order.asc()
            )
            
            return query.all()
            
        except Exception as e:
            logger.error(f"Error getting pending approvals for negotiation {negotiation_id}: {str(e)}")
            return []
    
    def get_pending_for_approver(
        self,
        user_id: uuid.UUID,
        role: Optional[str] = None
    ) -> List[ApprovalHistory]:
        """
        Get all pending approval steps assigned to a specific user.
        
        Args:
            user_id: UUID of the user
            role: Optional role of the user
            
        Returns:
            List of pending approval history entries for the approver
        """
        try:
            # Build base query
            query = self._db.query(ApprovalHistory).join(
                ApprovalStep, ApprovalHistory.step_id == ApprovalStep.id
            ).filter(
                ApprovalHistory.status == ApprovalStatus.PENDING
            )
            
            # Add user or role criteria
            if role:
                query = query.filter(
                    or_(
                        ApprovalStep.approver_id == user_id,
                        ApprovalStep.approver_role == role
                    )
                )
            else:
                query = query.filter(ApprovalStep.approver_id == user_id)
            
            # Order by creation date
            query = query.order_by(ApprovalHistory.created_at.asc())
            
            return query.all()
            
        except Exception as e:
            logger.error(f"Error getting pending approvals for approver {user_id}: {str(e)}")
            return []
    
    def request_additional_info(
        self,
        step_id: uuid.UUID,
        negotiation_id: uuid.UUID,
        user_id: uuid.UUID,
        request_message: str
    ) -> bool:
        """
        Record a request for additional information before approval.
        
        Args:
            step_id: UUID of the approval step
            negotiation_id: UUID of the negotiation
            user_id: UUID of the user making the request
            request_message: Message describing what additional info is needed
            
        Returns:
            True if successful, False if validation fails
        """
        try:
            # Get the step
            step = self.get_step_by_id(step_id)
            if not step:
                logger.warning(f"Step {step_id} not found for additional info request")
                return False
            
            # Validate that the user is authorized to approve this step
            if not self.check_approver_permission(step_id, user_id):
                logger.warning(f"User {user_id} not authorized for step {step_id}")
                return False
            
            # Get the approval history entry
            history = self._db.query(ApprovalHistory).filter(
                ApprovalHistory.negotiation_id == negotiation_id,
                ApprovalHistory.step_id == step_id
            ).first()
            
            if not history:
                logger.warning(f"Approval history not found for step {step_id} and negotiation {negotiation_id}")
                return False
            
            # Update status and add message
            history.status = ApprovalStatus.IN_PROGRESS
            history.comments = request_message
            history.action_date = datetime.utcnow()
            
            # Commit changes
            self._db.commit()
            
            # Also update negotiation status
            negotiation = self._db.query(Negotiation).filter(
                Negotiation.id == negotiation_id
            ).first()
            
            if negotiation and negotiation.approval_status != ApprovalStatus.IN_PROGRESS:
                negotiation.approval_status = ApprovalStatus.IN_PROGRESS
                self._db.commit()
            
            logger.info(f"Requested additional info for step {step_id} on negotiation {negotiation_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error requesting additional info: {str(e)}")
            self._db.rollback()
            return False
    
    def get_approval_history(self, negotiation_id: uuid.UUID) -> List[ApprovalHistory]:
        """
        Get the complete approval history for a negotiation.
        
        Args:
            negotiation_id: UUID of the negotiation
            
        Returns:
            Complete list of approval history entries
        """
        try:
            # Query approval history with step information
            query = self._db.query(ApprovalHistory).join(
                ApprovalStep, ApprovalHistory.step_id == ApprovalStep.id
            ).filter(
                ApprovalHistory.negotiation_id == negotiation_id
            ).order_by(
                ApprovalStep.order.asc(),
                ApprovalHistory.action_date.asc()
            )
            
            return query.all()
            
        except Exception as e:
            logger.error(f"Error getting approval history for negotiation {negotiation_id}: {str(e)}")
            return []
    
    def set_criteria(self, workflow_id: uuid.UUID, criteria: dict) -> bool:
        """
        Set the criteria for when a workflow applies.
        
        Args:
            workflow_id: UUID of the workflow
            criteria: Dictionary of criteria defining when the workflow applies
            
        Returns:
            True if successful, False if workflow not found
        """
        try:
            workflow = self.get_by_id(workflow_id)
            if not workflow:
                logger.warning(f"Workflow {workflow_id} not found for setting criteria")
                return False
            
            workflow.criteria = criteria
            self._db.commit()
            
            logger.info(f"Updated criteria for workflow {workflow_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error setting criteria for workflow {workflow_id}: {str(e)}")
            self._db.rollback()
            return False
    
    def set_applicable_entities(self, workflow_id: uuid.UUID, entities: dict) -> bool:
        """
        Set the entities this workflow applies to.
        
        Args:
            workflow_id: UUID of the workflow
            entities: Dictionary mapping entity types to lists of entity IDs
            
        Returns:
            True if successful, False if workflow not found
        """
        try:
            workflow = self.get_by_id(workflow_id)
            if not workflow:
                logger.warning(f"Workflow {workflow_id} not found for setting applicable entities")
                return False
            
            workflow.applicable_entities = entities
            self._db.commit()
            
            logger.info(f"Updated applicable entities for workflow {workflow_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error setting applicable entities for workflow {workflow_id}: {str(e)}")
            self._db.rollback()
            return False
    
    def search(
        self,
        query: str,
        organization_id: Optional[uuid.UUID] = None,
        workflow_type: Optional[WorkflowType] = None,
        active_only: bool = True,
        limit: int = 100,
        offset: int = 0
    ) -> List[ApprovalWorkflow]:
        """
        Search for workflows by name or description.
        
        Args:
            query: Search query string
            organization_id: Optional organization ID to filter by
            workflow_type: Optional workflow type to filter by
            active_only: Whether to return only active workflows
            limit: Maximum number of workflows to return
            offset: Offset for pagination
            
        Returns:
            List of workflows matching the search criteria
        """
        try:
            # Build base query with search criteria
            search_query = self._db.query(ApprovalWorkflow).filter(
                or_(
                    ApprovalWorkflow.name.ilike(f"%{query}%"),
                    ApprovalWorkflow.description.ilike(f"%{query}%")
                )
            )
            
            # Apply filters
            if organization_id:
                search_query = search_query.filter(ApprovalWorkflow.organization_id == organization_id)
                
            if workflow_type:
                search_query = search_query.filter(ApprovalWorkflow.type == workflow_type)
                
            if active_only:
                search_query = search_query.filter(ApprovalWorkflow.is_active == True)
            
            # Apply pagination
            search_query = search_query.limit(limit).offset(offset)
            
            return search_query.all()
            
        except Exception as e:
            logger.error(f"Error searching workflows: {str(e)}")
            return []
    
    def count_by_organization(
        self,
        organization_id: uuid.UUID,
        workflow_type: Optional[WorkflowType] = None,
        active_only: bool = True
    ) -> int:
        """
        Count the number of workflows for an organization.
        
        Args:
            organization_id: UUID of the organization
            workflow_type: Optional workflow type to filter by
            active_only: Whether to count only active workflows
            
        Returns:
            Number of workflows for the organization
        """
        try:
            query = self._db.query(ApprovalWorkflow).filter(
                ApprovalWorkflow.organization_id == organization_id
            )
            
            if workflow_type:
                query = query.filter(ApprovalWorkflow.type == workflow_type)
                
            if active_only:
                query = query.filter(ApprovalWorkflow.is_active == True)
            
            return query.count()
            
        except Exception as e:
            logger.error(f"Error counting workflows for organization {organization_id}: {str(e)}")
            return 0
    
    def get_workflows_by_negotiation(self, negotiation_id: uuid.UUID) -> Optional[ApprovalWorkflow]:
        """
        Get all workflows associated with a negotiation.
        
        Args:
            negotiation_id: UUID of the negotiation
            
        Returns:
            The assigned workflow if found, None otherwise
        """
        try:
            negotiation = self._db.query(Negotiation).filter(
                Negotiation.id == negotiation_id
            ).first()
            
            if not negotiation or not negotiation.approval_workflow_id:
                return None
                
            return self.get_by_id(negotiation.approval_workflow_id)
            
        except Exception as e:
            logger.error(f"Error getting workflow for negotiation {negotiation_id}: {str(e)}")
            return None
    
    def check_approver_permission(
        self,
        step_id: uuid.UUID,
        user_id: uuid.UUID,
        user_roles: Optional[List[str]] = None
    ) -> bool:
        """
        Check if a user is authorized to approve a specific step.
        
        Args:
            step_id: UUID of the approval step
            user_id: UUID of the user
            user_roles: Optional list of user roles
            
        Returns:
            True if authorized, False otherwise
        """
        try:
            step = self.get_step_by_id(step_id)
            if not step:
                return False
            
            # Direct assignment to user
            if step.approver_id == user_id:
                return True
            
            # Role-based assignment
            if user_roles and step.approver_role and step.approver_role in user_roles:
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error checking approver permission: {str(e)}")
            return False