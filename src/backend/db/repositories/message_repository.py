"""
Repository class for managing message data with support for hierarchical messages,
attachments, and full history tracking.
"""

from typing import List, Dict, Any, Optional
import uuid
from datetime import datetime

from sqlalchemy import select, and_, func
from sqlalchemy.orm import Session

from db.session import Session
from db.models.message import Message, RelatedEntityType


class MessageRepository:
    """Repository class for handling operations related to messages in the system, including CRUD operations, thread management, and message searching."""

    def __init__(self, db_session: Session):
        """
        Initializes a new MessageRepository instance.
        
        Args:
            db_session: Database session for SQL operations
        """
        self.db_session = db_session

    def create_message(self, message_data: Dict) -> Message:
        """
        Creates a new message in the system.
        
        Args:
            message_data: Dictionary containing message data
            
        Returns:
            Newly created message object
        """
        # Generate thread_id if not provided (for new conversations)
        thread_id = message_data.get('thread_id')
        if not thread_id:
            thread_id = uuid.uuid4()
            
        # Create a new message instance using keyword arguments
        message = Message(
            thread_id=thread_id,
            sender_id=message_data['sender_id'],
            recipient_ids=message_data['recipient_ids'],
            content=message_data['content'],
            parent_id=message_data.get('parent_id'),
            attachments=message_data.get('attachments'),
            related_entity_type=message_data.get('related_entity_type'),
            related_entity_id=message_data.get('related_entity_id')
        )
        
        # Add to database and commit
        self.db_session.add(message)
        self.db_session.commit()
        
        return message

    def get_message_by_id(self, message_id: uuid.UUID) -> Optional[Message]:
        """
        Retrieves a message by its unique identifier.
        
        Args:
            message_id: UUID of the message to retrieve
            
        Returns:
            Message object if found, None otherwise
        """
        stmt = select(Message).where(Message.id == message_id)
        result = self.db_session.execute(stmt).scalars().first()
        return result

    def get_messages_by_thread_id(self, thread_id: uuid.UUID, skip: int = 0, limit: int = 100) -> List[Message]:
        """
        Retrieves all messages in a specific thread.
        
        Args:
            thread_id: UUID of the thread
            skip: Number of messages to skip for pagination
            limit: Maximum number of messages to return
            
        Returns:
            List of messages in the thread
        """
        stmt = (
            select(Message)
            .where(Message.thread_id == thread_id)
            .order_by(Message.created_at)
            .offset(skip)
            .limit(limit)
        )
        result = self.db_session.execute(stmt).scalars().all()
        return list(result)

    def get_thread_count(self, thread_id: uuid.UUID) -> int:
        """
        Retrieves the total count of messages in a thread.
        
        Args:
            thread_id: UUID of the thread
            
        Returns:
            Total number of messages in the thread
        """
        stmt = select(func.count()).select_from(Message).where(Message.thread_id == thread_id)
        result = self.db_session.execute(stmt).scalar()
        return result or 0

    def get_messages_by_negotiation_id(self, negotiation_id: uuid.UUID, skip: int = 0, limit: int = 100) -> List[Message]:
        """
        Retrieves all messages related to a specific negotiation.
        
        Args:
            negotiation_id: UUID of the negotiation
            skip: Number of messages to skip for pagination
            limit: Maximum number of messages to return
            
        Returns:
            List of messages related to the negotiation
        """
        stmt = (
            select(Message)
            .where(and_(
                Message.related_entity_type == RelatedEntityType.Negotiation,
                Message.related_entity_id == negotiation_id
            ))
            .order_by(Message.created_at)
            .offset(skip)
            .limit(limit)
        )
        result = self.db_session.execute(stmt).scalars().all()
        return list(result)

    def get_messages_by_rate_id(self, rate_id: uuid.UUID, skip: int = 0, limit: int = 100) -> List[Message]:
        """
        Retrieves all messages related to a specific rate.
        
        Args:
            rate_id: UUID of the rate
            skip: Number of messages to skip for pagination
            limit: Maximum number of messages to return
            
        Returns:
            List of messages related to the rate
        """
        stmt = (
            select(Message)
            .where(and_(
                Message.related_entity_type == RelatedEntityType.Rate,
                Message.related_entity_id == rate_id
            ))
            .order_by(Message.created_at)
            .offset(skip)
            .limit(limit)
        )
        result = self.db_session.execute(stmt).scalars().all()
        return list(result)

    def get_messages_by_ocg_id(self, ocg_id: uuid.UUID, skip: int = 0, limit: int = 100) -> List[Message]:
        """
        Retrieves all messages related to a specific OCG (Outside Counsel Guidelines).
        
        Args:
            ocg_id: UUID of the OCG
            skip: Number of messages to skip for pagination
            limit: Maximum number of messages to return
            
        Returns:
            List of messages related to the OCG
        """
        stmt = (
            select(Message)
            .where(and_(
                Message.related_entity_type == RelatedEntityType.OCG,
                Message.related_entity_id == ocg_id
            ))
            .order_by(Message.created_at)
            .offset(skip)
            .limit(limit)
        )
        result = self.db_session.execute(stmt).scalars().all()
        return list(result)

    def search_messages(self, search_term: str, filters: Dict = None, skip: int = 0, limit: int = 100) -> List[Message]:
        """
        Searches messages based on content, sender, or other criteria.
        
        Args:
            search_term: Text to search for in message content
            filters: Dictionary of additional filters like sender_id, thread_id, etc.
            skip: Number of messages to skip for pagination
            limit: Maximum number of messages to return
            
        Returns:
            List of messages matching the search criteria
        """
        filters = filters or {}
        
        # Start with base query
        stmt = select(Message)
        
        # Add content search
        if search_term:
            stmt = stmt.where(func.lower(Message.content).contains(func.lower(search_term)))
        
        # Add filters
        if filters.get('sender_id'):
            stmt = stmt.where(Message.sender_id == filters['sender_id'])
            
        if filters.get('thread_id'):
            stmt = stmt.where(Message.thread_id == filters['thread_id'])
            
        if filters.get('related_entity_type'):
            stmt = stmt.where(Message.related_entity_type == filters['related_entity_type'])
            
        if filters.get('related_entity_id'):
            stmt = stmt.where(Message.related_entity_id == filters['related_entity_id'])
            
        if filters.get('start_date'):
            stmt = stmt.where(Message.created_at >= filters['start_date'])
            
        if filters.get('end_date'):
            stmt = stmt.where(Message.created_at <= filters['end_date'])
        
        # Add sorting, pagination
        stmt = stmt.order_by(Message.created_at.desc()).offset(skip).limit(limit)
        
        # Execute query and return results
        result = self.db_session.execute(stmt).scalars().all()
        return list(result)

    def update_message(self, message_id: uuid.UUID, update_data: Dict) -> Optional[Message]:
        """
        Updates an existing message.
        
        Args:
            message_id: UUID of the message to update
            update_data: Dictionary containing fields to update
            
        Returns:
            Updated message if found and updated, None otherwise
        """
        # Get the message to update
        message = self.get_message_by_id(message_id)
        if not message:
            return None
            
        # Update fields
        for key, value in update_data.items():
            if hasattr(message, key):
                setattr(message, key, value)
        
        # Update timestamp and save
        message.updated_at = datetime.utcnow()
        self.db_session.commit()
        return message

    def mark_as_read(self, message_id: uuid.UUID, user_id: uuid.UUID) -> bool:
        """
        Marks a message as read by a specific user.
        
        Args:
            message_id: UUID of the message to mark as read
            user_id: UUID of the user who read the message
            
        Returns:
            True if marked as read, False otherwise
        """
        message = self.get_message_by_id(message_id)
        if not message:
            return False
            
        # Check if user is a recipient (convert UUIDs to strings for comparison)
        str_user_id = str(user_id)
        recipient_ids = [str(r_id) for r_id in message.recipient_ids]
        if str_user_id not in recipient_ids:
            return False
            
        # Use the model's method to mark as read
        message.mark_as_read()
        self.db_session.commit()
        return True

    def mark_thread_as_read(self, thread_id: uuid.UUID, user_id: uuid.UUID) -> bool:
        """
        Marks all messages in a thread as read by a specific user.
        
        Args:
            thread_id: UUID of the thread
            user_id: UUID of the user who read the messages
            
        Returns:
            True if all messages were marked as read, False otherwise
        """
        # Get all unread messages in thread
        stmt = (
            select(Message)
            .where(and_(
                Message.thread_id == thread_id,
                Message.is_read == False
            ))
        )
        messages = self.db_session.execute(stmt).scalars().all()
        
        # Filter messages where user is a recipient
        str_user_id = str(user_id)
        messages_to_update = []
        for message in messages:
            recipient_ids = [str(r_id) for r_id in message.recipient_ids]
            if str_user_id in recipient_ids:
                messages_to_update.append(message)
        
        if not messages_to_update:
            return False
            
        # Mark all matching messages as read
        for message in messages_to_update:
            message.mark_as_read()
            
        self.db_session.commit()
        return True

    def delete_message(self, message_id: uuid.UUID) -> bool:
        """
        Deletes a message from the system.
        
        Args:
            message_id: UUID of the message to delete
            
        Returns:
            True if deleted successfully, False otherwise
        """
        message = self.get_message_by_id(message_id)
        if not message:
            return False
            
        self.db_session.delete(message)
        self.db_session.commit()
        return True

    def get_unread_message_count(self, user_id: uuid.UUID) -> int:
        """
        Gets the count of unread messages for a specific user.
        
        Args:
            user_id: UUID of the user
            
        Returns:
            Count of unread messages
        """
        str_user_id = str(user_id)
        
        # Query for unread messages
        stmt = select(Message).where(Message.is_read == False)
        messages = self.db_session.execute(stmt).scalars().all()
        
        # Filter where user is in recipient_ids
        count = 0
        for message in messages:
            recipient_ids = [str(r_id) for r_id in message.recipient_ids]
            if str_user_id in recipient_ids:
                count += 1
                
        return count

    def get_thread_summary(self, thread_id: uuid.UUID) -> Dict:
        """
        Gets a summary of a message thread including latest message and count.
        
        Args:
            thread_id: UUID of the thread
            
        Returns:
            Summary information about the thread
        """
        # Get latest message in thread
        stmt = (
            select(Message)
            .where(Message.thread_id == thread_id)
            .order_by(Message.created_at.desc())
            .limit(1)
        )
        latest_message = self.db_session.execute(stmt).scalars().first()
        
        # Get count of messages
        count = self.get_thread_count(thread_id)
        
        return {
            'thread_id': str(thread_id),
            'message_count': count,
            'latest_message': latest_message.to_dict() if latest_message else None,
            'last_updated': latest_message.updated_at.isoformat() if latest_message else None
        }