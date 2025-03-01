"""
SQLAlchemy ORM model for messages in the Justice Bid Rate Negotiation System.
This model supports the secure messaging system with hierarchical organization of 
communications related to rate negotiations, allowing messages to be attached to 
specific entities like negotiations, rates, or OCGs.
"""

import uuid
import datetime
import enum
from typing import List, Dict, Any, Optional

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey, Enum, func
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID, JSONB

from ..base import Base


class RelatedEntityType(enum.Enum):
    """Enumeration of entity types that messages can be related to."""
    Negotiation = "negotiation"
    Rate = "rate"
    OCG = "ocg"


class Message(Base):
    """
    SQLAlchemy model for messages in the Justice Bid system.
    Supports hierarchical messaging for rate negotiations, with relationships 
    to senders, recipients, and related entities.
    """
    __tablename__ = 'messages'

    # Primary key
    id = Column(UUID, primary_key=True, default=uuid.uuid4)
    
    # Thread and hierarchy
    thread_id = Column(UUID, nullable=False)  # Groups messages in a conversation
    parent_id = Column(UUID, ForeignKey('messages.id'), nullable=True)  # For replies
    
    # Sender and recipients
    sender_id = Column(UUID, ForeignKey('users.id'), nullable=False)
    recipient_ids = Column(JSONB, nullable=False)  # Array of user IDs
    
    # Content
    content = Column(Text, nullable=False)
    attachments = Column(JSONB, nullable=True)  # Array of attachment objects
    
    # Related entity (what the message is about)
    related_entity_type = Column(Enum(RelatedEntityType), nullable=True)
    related_entity_id = Column(UUID, nullable=True)
    
    # Status
    is_read = Column(Boolean, default=False, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, 
                         onupdate=datetime.datetime.utcnow, nullable=False)
    
    # Relationships
    sender = relationship("User", foreign_keys=[sender_id])
    replies = relationship("Message", 
                           backref=relationship("parent", remote_side=[id]),
                           cascade="all, delete-orphan")
    
    # Relationship with negotiation if related entity is a negotiation
    negotiation = relationship("Negotiation", 
                              foreign_keys=[related_entity_id],
                              primaryjoin="and_(Message.related_entity_type=='negotiation', "
                                          "Message.related_entity_id==Negotiation.id)",
                              back_populates="messages")

    def __init__(self, thread_id: uuid.UUID, sender_id: uuid.UUID, recipient_ids: List[uuid.UUID], 
                 content: str, parent_id: Optional[uuid.UUID] = None, attachments: List[Dict] = None,
                 related_entity_type: Optional[RelatedEntityType] = None, 
                 related_entity_id: Optional[uuid.UUID] = None):
        """
        Initialize a new Message object with the provided attributes
        
        Args:
            thread_id: ID grouping related messages together
            sender_id: ID of the user sending the message
            recipient_ids: List of user IDs who should receive the message
            content: The text content of the message
            parent_id: Optional ID of the parent message (for replies)
            attachments: Optional list of attachment objects
            related_entity_type: Optional type of entity this message is related to
            related_entity_id: Optional ID of the related entity
        """
        self.id = uuid.uuid4()
        self.thread_id = thread_id
        self.parent_id = parent_id
        self.sender_id = sender_id
        self.recipient_ids = recipient_ids
        self.content = content
        self.attachments = attachments or []
        self.related_entity_type = related_entity_type
        self.related_entity_id = related_entity_id
        self.is_read = False
        self.created_at = datetime.datetime.utcnow()
        self.updated_at = datetime.datetime.utcnow()

    def to_dict(self) -> Dict[str, Any]:
        """
        Converts the Message object to a dictionary representation
        
        Returns:
            Dictionary containing message attributes
        """
        return {
            'id': str(self.id),
            'thread_id': str(self.thread_id),
            'parent_id': str(self.parent_id) if self.parent_id else None,
            'sender_id': str(self.sender_id),
            'recipient_ids': self.recipient_ids,
            'content': self.content,
            'attachments': self.attachments,
            'related_entity_type': self.related_entity_type.value if self.related_entity_type else None,
            'related_entity_id': str(self.related_entity_id) if self.related_entity_id else None,
            'is_read': self.is_read,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

    def mark_as_read(self) -> None:
        """
        Marks the message as read
        """
        self.is_read = True
        self.updated_at = datetime.datetime.utcnow()

    def add_attachment(self, attachment: Dict) -> None:
        """
        Adds an attachment to the message
        
        Args:
            attachment: Dictionary containing attachment metadata
        """
        if self.attachments is None:
            self.attachments = []
        
        self.attachments.append(attachment)
        self.updated_at = datetime.datetime.utcnow()

    def get_thread(self) -> List["Message"]:
        """
        Gets all messages in the same thread
        
        Returns:
            List of Message objects in the same thread
        """
        from sqlalchemy.orm import Session
        from sqlalchemy import desc
        
        session = Session.object_session(self)
        if not session:
            return []
            
        return (session.query(Message)
                .filter(Message.thread_id == self.thread_id)
                .order_by(Message.created_at)
                .all())

    def get_children(self) -> List["Message"]:
        """
        Gets all direct reply messages
        
        Returns:
            List of Message objects that are direct replies to this message
        """
        from sqlalchemy.orm import Session
        from sqlalchemy import desc
        
        session = Session.object_session(self)
        if not session:
            return []
            
        return (session.query(Message)
                .filter(Message.parent_id == self.id)
                .order_by(Message.created_at)
                .all())