"""
Repository module for the Negotiation entity in the Justice Bid Rate Negotiation System.
Provides data access methods and business logic for managing rate negotiations between law firms and clients,
including CRUD operations, filtering, and specialized queries.
"""

from typing import List, Optional, Dict, Any, Union
import uuid
from datetime import date, datetime

from sqlalchemy import and_, or_, func
from sqlalchemy.orm import joinedload

from ..session import session_scope, get_db, get_read_db
from ..models.negotiation import Negotiation
from ...utils.constants import NegotiationStatus, ApprovalStatus
from ...utils.pagination import paginate_query, PaginatedResponse


def create_negotiation(
    client_id: uuid.UUID,
    firm_id: uuid.UUID,
    request_date: date,
    submission_deadline: date = None
) -> Negotiation:
    """
    Creates a new negotiation between a client and a law firm.
    
    Args:
        client_id: UUID of the client organization
        firm_id: UUID of the law firm organization
        request_date: Date the negotiation was requested
        submission_deadline: Optional deadline for rate submission
        
    Returns:
        Negotiation: Newly created negotiation object
    """
    with session_scope() as session:
        # Create new negotiation object
        negotiation = Negotiation(
            client_id=client_id,
            firm_id=firm_id,
            status=NegotiationStatus.REQUESTED,
            request_date=request_date,
            submission_deadline=submission_deadline
        )
        
        # Add to session and commit
        session.add(negotiation)
        
        return negotiation


def get_negotiation_by_id(
    negotiation_id: uuid.UUID,
    include_rates: bool = False,
    include_messages: bool = False,
    include_approval_workflow: bool = False
) -> Optional[Negotiation]:
    """
    Retrieves a negotiation by its ID with optional related data.
    
    Args:
        negotiation_id: UUID of the negotiation to retrieve
        include_rates: Whether to include associated rates
        include_messages: Whether to include associated messages
        include_approval_workflow: Whether to include the approval workflow
        
    Returns:
        Optional[Negotiation]: Negotiation object if found, None otherwise
    """
    db = get_read_db()
    
    # Start building the query
    query = db.query(Negotiation)
    
    # Add optional eager loading based on parameters
    if include_rates:
        query = query.options(joinedload(Negotiation.rates))
    
    if include_messages:
        query = query.options(joinedload(Negotiation.messages))
    
    if include_approval_workflow:
        query = query.options(joinedload(Negotiation.approval_workflow))
    
    # Execute query with filtering
    negotiation = query.filter(Negotiation.id == negotiation_id).first()
    
    return negotiation


def get_negotiations(
    client_id: Optional[uuid.UUID] = None,
    firm_id: Optional[uuid.UUID] = None,
    status: Optional[NegotiationStatus] = None,
    approval_status: Optional[ApprovalStatus] = None,
    from_date: Optional[date] = None,
    to_date: Optional[date] = None,
    page: int = 1,
    page_size: int = 20
) -> PaginatedResponse[Negotiation]:
    """
    Retrieves a paginated list of negotiations with filtering options.
    
    Args:
        client_id: Optional client organization UUID to filter by
        firm_id: Optional law firm organization UUID to filter by
        status: Optional negotiation status to filter by
        approval_status: Optional approval status to filter by
        from_date: Optional start date for request_date filtering
        to_date: Optional end date for request_date filtering
        page: Page number for pagination
        page_size: Number of items per page
        
    Returns:
        PaginatedResponse[Negotiation]: Paginated list of negotiations matching criteria
    """
    db = get_read_db()
    
    # Start building the query
    query = db.query(Negotiation)
    
    # Apply filters based on provided parameters
    if client_id is not None:
        query = query.filter(Negotiation.client_id == client_id)
    
    if firm_id is not None:
        query = query.filter(Negotiation.firm_id == firm_id)
    
    if status is not None:
        query = query.filter(Negotiation.status == status)
    
    if approval_status is not None:
        query = query.filter(Negotiation.approval_status == approval_status)
    
    if from_date is not None:
        query = query.filter(Negotiation.request_date >= from_date)
    
    if to_date is not None:
        query = query.filter(Negotiation.request_date <= to_date)
    
    # Filter out deleted negotiations if model has soft delete
    if hasattr(Negotiation, 'is_deleted'):
        query = query.filter(Negotiation.is_deleted.is_(False))
    
    # Apply pagination
    items, pagination_metadata = paginate_query(query, page, page_size)
    
    # Create and return paginated response
    return PaginatedResponse(
        items=items,
        page=pagination_metadata['page'],
        page_size=pagination_metadata['page_size'],
        total_count=pagination_metadata['total_count']
    )


def update_negotiation_status(
    negotiation_id: uuid.UUID,
    new_status: NegotiationStatus,
    updated_by_id: uuid.UUID,
    comment: Optional[str] = None
) -> bool:
    """
    Updates the status of a negotiation with validation.
    
    Args:
        negotiation_id: UUID of the negotiation to update
        new_status: New status to set
        updated_by_id: UUID of the user making the change
        comment: Optional comment explaining the status change
        
    Returns:
        bool: True if the status was updated successfully, False otherwise
    """
    try:
        with session_scope() as session:
            # Get negotiation
            negotiation = session.query(Negotiation).filter(
                Negotiation.id == negotiation_id
            ).first()
            
            if not negotiation:
                return False
            
            # Update status using model method which handles validation
            result = negotiation.update_status(new_status, updated_by_id, comment)
            
            return result
    except Exception:
        # Log the exception if needed
        return False


def set_negotiation_deadline(
    negotiation_id: uuid.UUID,
    deadline: date,
    updated_by_id: uuid.UUID
) -> bool:
    """
    Sets or updates the submission deadline for a negotiation.
    
    Args:
        negotiation_id: UUID of the negotiation to update
        deadline: New submission deadline
        updated_by_id: UUID of the user making the change
        
    Returns:
        bool: True if the deadline was updated successfully, False otherwise
    """
    try:
        with session_scope() as session:
            # Get negotiation
            negotiation = session.query(Negotiation).filter(
                Negotiation.id == negotiation_id
            ).first()
            
            if not negotiation:
                return False
            
            # Set deadline using model method
            negotiation.set_deadline(deadline, updated_by_id)
            
            return True
    except Exception:
        # Log the exception if needed
        return False


def add_rate_to_negotiation(
    negotiation_id: uuid.UUID,
    rate_id: uuid.UUID,
    updated_by_id: uuid.UUID
) -> bool:
    """
    Adds a rate to an existing negotiation.
    
    Args:
        negotiation_id: UUID of the negotiation
        rate_id: UUID of the rate to add
        updated_by_id: UUID of the user making the change
        
    Returns:
        bool: True if the rate was added successfully, False otherwise
    """
    try:
        with session_scope() as session:
            # Get negotiation
            negotiation = session.query(Negotiation).filter(
                Negotiation.id == negotiation_id
            ).first()
            
            if not negotiation:
                return False
            
            # Get the rate
            from ..models.rate import Rate
            rate = session.query(Rate).filter(Rate.id == rate_id).first()
            
            if not rate:
                return False
            
            # Add rate to negotiation using model method
            negotiation.add_rate(rate)
            
            # Add history entry with the user who made the change
            negotiation.add_history_entry(
                action="rate_added",
                user_id=updated_by_id,
                comment=f"Rate {rate_id} added to negotiation",
                metadata={"rate_id": str(rate_id)}
            )
            
            return True
    except Exception:
        # Log the exception if needed
        return False


def remove_rate_from_negotiation(
    negotiation_id: uuid.UUID,
    rate_id: uuid.UUID,
    updated_by_id: uuid.UUID
) -> bool:
    """
    Removes a rate from an existing negotiation.
    
    Args:
        negotiation_id: UUID of the negotiation
        rate_id: UUID of the rate to remove
        updated_by_id: UUID of the user making the change
        
    Returns:
        bool: True if the rate was removed successfully, False otherwise
    """
    try:
        with session_scope() as session:
            # Get negotiation
            negotiation = session.query(Negotiation).filter(
                Negotiation.id == negotiation_id
            ).first()
            
            if not negotiation:
                return False
            
            # Get the rate
            from ..models.rate import Rate
            rate = session.query(Rate).filter(Rate.id == rate_id).first()
            
            if not rate:
                return False
            
            # Remove rate from negotiation using model method
            negotiation.remove_rate(rate)
            
            # Add history entry with the user who made the change
            negotiation.add_history_entry(
                action="rate_removed",
                user_id=updated_by_id,
                comment=f"Rate {rate_id} removed from negotiation",
                metadata={"rate_id": str(rate_id)}
            )
            
            return True
    except Exception:
        # Log the exception if needed
        return False


def set_approval_workflow(
    negotiation_id: uuid.UUID,
    workflow_id: uuid.UUID,
    updated_by_id: uuid.UUID
) -> bool:
    """
    Assigns an approval workflow to a negotiation.
    
    Args:
        negotiation_id: UUID of the negotiation
        workflow_id: UUID of the approval workflow to assign
        updated_by_id: UUID of the user making the change
        
    Returns:
        bool: True if the workflow was assigned successfully, False otherwise
    """
    try:
        with session_scope() as session:
            # Get negotiation
            negotiation = session.query(Negotiation).filter(
                Negotiation.id == negotiation_id
            ).first()
            
            if not negotiation:
                return False
            
            # Get the approval workflow
            from ..models.approval import ApprovalWorkflow
            workflow = session.query(ApprovalWorkflow).filter(
                ApprovalWorkflow.id == workflow_id
            ).first()
            
            if not workflow:
                return False
            
            # Set approval workflow using model method
            negotiation.set_approval_workflow(workflow, updated_by_id)
            
            return True
    except Exception:
        # Log the exception if needed
        return False


def update_approval_status(
    negotiation_id: uuid.UUID,
    new_status: ApprovalStatus,
    updated_by_id: uuid.UUID,
    comment: Optional[str] = None
) -> bool:
    """
    Updates the approval status of a negotiation.
    
    Args:
        negotiation_id: UUID of the negotiation
        new_status: New approval status to set
        updated_by_id: UUID of the user making the change
        comment: Optional comment explaining the status change
        
    Returns:
        bool: True if the status was updated successfully, False otherwise
    """
    try:
        with session_scope() as session:
            # Get negotiation
            negotiation = session.query(Negotiation).filter(
                Negotiation.id == negotiation_id
            ).first()
            
            if not negotiation:
                return False
            
            # Update approval status using model method
            result = negotiation.update_approval_status(new_status, updated_by_id, comment)
            
            return result
    except Exception:
        # Log the exception if needed
        return False


def add_message_to_negotiation(
    negotiation_id: uuid.UUID,
    sender_id: uuid.UUID,
    recipient_ids: List[uuid.UUID],
    content: str,
    attachments: Optional[List[dict]] = None
) -> Optional[uuid.UUID]:
    """
    Adds a message to an existing negotiation.
    
    Args:
        negotiation_id: UUID of the negotiation
        sender_id: UUID of the message sender
        recipient_ids: List of UUIDs of the message recipients
        content: The message text content
        attachments: Optional list of attachment metadata
        
    Returns:
        Optional[UUID]: ID of the created message if successful, None otherwise
    """
    try:
        with session_scope() as session:
            # Get negotiation
            negotiation = session.query(Negotiation).filter(
                Negotiation.id == negotiation_id
            ).first()
            
            if not negotiation:
                return None
            
            # Add message using model method
            message = negotiation.add_message(
                sender_id=sender_id,
                recipient_ids=recipient_ids,
                content=content,
                attachments=attachments
            )
            
            return message.id
    except Exception:
        # Log the exception if needed
        return None


def get_negotiation_history(
    negotiation_id: uuid.UUID
) -> List[dict]:
    """
    Retrieves the history of a negotiation.
    
    Args:
        negotiation_id: UUID of the negotiation
        
    Returns:
        List[dict]: List of historical events for the negotiation
    """
    db = get_read_db()
    
    # Get negotiation
    negotiation = db.query(Negotiation).filter(
        Negotiation.id == negotiation_id
    ).first()
    
    if not negotiation:
        return []
    
    # Get history using model method
    return negotiation.get_history()


def get_overdue_negotiations(
    client_id: Optional[uuid.UUID] = None,
    firm_id: Optional[uuid.UUID] = None,
    page: int = 1,
    page_size: int = 20
) -> PaginatedResponse[Negotiation]:
    """
    Retrieves a list of negotiations that are past their submission deadline.
    
    Args:
        client_id: Optional client organization UUID to filter by
        firm_id: Optional law firm organization UUID to filter by
        page: Page number for pagination
        page_size: Number of items per page
        
    Returns:
        PaginatedResponse[Negotiation]: Paginated list of overdue negotiations
    """
    db = get_read_db()
    
    # Start building the query
    query = db.query(Negotiation)
    
    # Current date for comparison
    current_date = date.today()
    
    # Filter for overdue negotiations
    query = query.filter(Negotiation.submission_deadline < current_date)
    
    # Exclude completed and rejected negotiations
    terminal_statuses = [NegotiationStatus.COMPLETED, NegotiationStatus.REJECTED]
    query = query.filter(~Negotiation.status.in_(terminal_statuses))
    
    # Apply additional filters based on provided parameters
    if client_id is not None:
        query = query.filter(Negotiation.client_id == client_id)
    
    if firm_id is not None:
        query = query.filter(Negotiation.firm_id == firm_id)
    
    # Filter out deleted negotiations if model has soft delete
    if hasattr(Negotiation, 'is_deleted'):
        query = query.filter(Negotiation.is_deleted.is_(False))
    
    # Apply pagination
    items, pagination_metadata = paginate_query(query, page, page_size)
    
    # Create and return paginated response
    return PaginatedResponse(
        items=items,
        page=pagination_metadata['page'],
        page_size=pagination_metadata['page_size'],
        total_count=pagination_metadata['total_count']
    )


def delete_negotiation(
    negotiation_id: uuid.UUID
) -> bool:
    """
    Soft-deletes a negotiation.
    
    Args:
        negotiation_id: UUID of the negotiation to delete
        
    Returns:
        bool: True if the negotiation was deleted successfully, False otherwise
    """
    try:
        with session_scope() as session:
            # Get negotiation
            negotiation = session.query(Negotiation).filter(
                Negotiation.id == negotiation_id
            ).first()
            
            if not negotiation:
                return False
            
            # Check if model has soft delete functionality
            if hasattr(negotiation, 'is_deleted'):
                negotiation.is_deleted = True
                return True
            else:
                # Alternatively, just mark with a custom flag
                negotiation.metadata = negotiation.metadata or {}
                negotiation.metadata['deleted'] = True
                negotiation.metadata['deleted_at'] = datetime.utcnow().isoformat()
                return True
    except Exception:
        # Log the exception if needed
        return False