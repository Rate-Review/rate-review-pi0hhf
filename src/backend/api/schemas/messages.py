"""
Pydantic schema models for message-related API requests and responses, supporting the hierarchical messaging system for rate negotiations.
"""

from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Field, validator, constr

from ...utils.validators import validate_uuid, validate_non_empty_string
from ..schemas.users import UserBasicResponse


class AttachmentBase(BaseModel):
    """Base schema for message attachments"""
    file_name: str
    file_type: str
    file_size: int
    file_url: Optional[str] = None


class AttachmentCreate(BaseModel):
    """Schema for creating a new attachment"""
    file_content: bytes


class AttachmentResponse(BaseModel):
    """Schema for attachment response"""
    id: UUID
    file_name: str
    file_type: str
    file_size: int
    file_url: str


class MessageBase(BaseModel):
    """Base schema for message data"""
    content: str
    attachments: Optional[List[AttachmentBase]] = None
    related_entity_type: Optional[str] = None
    related_entity_id: Optional[UUID] = None

    @validator('content')
    def validate_content(cls, v):
        """Validates that message content is not empty"""
        if not v or v.strip() == '':
            raise ValueError('Message content cannot be empty')
        return v


class MessageCreate(BaseModel):
    """Schema for creating a new message"""
    content: str
    thread_id: Optional[UUID] = None
    parent_id: Optional[UUID] = None
    recipient_ids: List[UUID]
    attachments: Optional[List[AttachmentCreate]] = None
    related_entity_type: Optional[str] = None
    related_entity_id: Optional[UUID] = None

    @validator('recipient_ids')
    def validate_recipients(cls, v):
        """Validates recipient list is not empty"""
        if not v or len(v) == 0:
            raise ValueError('At least one recipient is required')
        return v


class MessageResponse(BaseModel):
    """Schema for message response"""
    id: UUID
    thread_id: UUID
    parent_id: Optional[UUID] = None
    sender_id: UUID
    sender: UserBasicResponse
    recipient_ids: List[UUID]
    content: str
    attachments: List[AttachmentResponse]
    related_entity_type: Optional[str] = None
    related_entity_id: Optional[UUID] = None
    is_read: bool
    created_at: datetime
    updated_at: datetime


class MessageUpdate(BaseModel):
    """Schema for updating a message"""
    is_read: bool


class MessageThreadCreate(BaseModel):
    """Schema for creating a new message thread"""
    title: str
    participant_ids: List[UUID]
    related_entity_type: Optional[str] = None
    related_entity_id: Optional[UUID] = None

    @validator('participant_ids')
    def validate_participants(cls, v):
        """Validates participant list is not empty"""
        if not v or len(v) == 0:
            raise ValueError('At least one participant is required')
        return v


class MessageThreadResponse(BaseModel):
    """Schema for message thread response"""
    id: UUID
    title: str
    participants: List[UserBasicResponse]
    related_entity_type: Optional[str] = None
    related_entity_id: Optional[UUID] = None
    message_count: int
    unread_count: int
    latest_message: Optional[MessageResponse] = None
    created_at: datetime
    updated_at: datetime


class MessageList(BaseModel):
    """Schema for paginated list of messages"""
    items: List[MessageResponse]
    total: int
    page: int
    size: int
    status: str


class MessageThreadList(BaseModel):
    """Schema for paginated list of message threads"""
    items: List[MessageThreadResponse]
    total: int
    page: int
    size: int
    status: str


class MessageFilterParams(BaseModel):
    """Schema for filtering messages in API requests"""
    thread_id: Optional[UUID] = None
    parent_id: Optional[UUID] = None
    sender_id: Optional[UUID] = None
    is_read: Optional[bool] = None
    related_entity_type: Optional[str] = None
    related_entity_id: Optional[UUID] = None
    from_date: Optional[datetime] = None
    to_date: Optional[datetime] = None