"""
Pydantic models for peer group-related API operations in the Justice Bid Rate Negotiation System.
These schemas handle validation and serialization for peer group creation, updates, member management, and responses.
"""

from pydantic import BaseModel, Field, validator
from uuid import UUID
from typing import Optional, List, Dict, Any
from datetime import datetime

from ...utils.validators import validate_required, validate_string, validate_uuid, validate_dict
from ...utils.constants import DEFAULT_PAGE_SIZE, MAX_PAGE_SIZE


class PeerGroupBase(BaseModel):
    """Base schema for peer group data with common fields"""
    name: str
    criteria: Optional[Dict[str, Any]] = None
    
    @validator('name')
    def validate_name(cls, value):
        """Validate peer group name"""
        validate_required(value, "name")
        validate_string(value, "name", min_length=1, max_length=100)
        return value
    
    @validator('criteria')
    def validate_criteria(cls, value):
        """Validate criteria if provided"""
        if value is None:
            return {}
        validate_dict(value, "criteria")
        return value
    
    class Config:
        extra = "forbid"


class PeerGroupCreate(PeerGroupBase):
    """Schema for creating a new peer group"""
    organization_id: UUID
    
    @validator('organization_id')
    def validate_organization_id(cls, value):
        """Validate organization ID"""
        validate_required(value, "organization_id")
        validate_uuid(value, "organization_id")
        return value
    
    class Config:
        extra = "forbid"


class PeerGroupUpdate(BaseModel):
    """Schema for updating an existing peer group"""
    name: Optional[str] = None
    criteria: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None
    
    @validator('name')
    def validate_name(cls, value):
        """Validate name if provided"""
        if value is None:
            return None
        validate_string(value, "name", min_length=1, max_length=100)
        return value
    
    @validator('criteria')
    def validate_criteria(cls, value):
        """Validate criteria if provided"""
        if value is None:
            return None
        validate_dict(value, "criteria")
        return value
    
    class Config:
        extra = "forbid"


class PeerGroupOut(BaseModel):
    """Schema for peer group data in API responses"""
    id: UUID
    name: str
    organization_id: UUID
    criteria: Dict[str, Any]
    member_count: int
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        orm_mode = True


class OrganizationBasic(BaseModel):
    """Minimal organization schema for peer group member listings"""
    id: UUID
    name: str
    type: str
    
    class Config:
        orm_mode = True


class PeerGroupWithMembers(BaseModel):
    """Extended peer group schema that includes member organizations"""
    id: UUID
    name: str
    organization_id: UUID
    criteria: Dict[str, Any]
    member_organizations: List['OrganizationBasic']
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        orm_mode = True


class PeerGroupList(BaseModel):
    """Schema for paginated list of peer groups"""
    items: List[PeerGroupOut]
    total: int
    page: int
    size: int
    pages: int


class PeerGroupSearchParams(BaseModel):
    """Schema for peer group search parameters"""
    name: Optional[str] = None
    organization_id: Optional[UUID] = None
    active_only: Optional[bool] = True
    page: int = 1
    page_size: int = DEFAULT_PAGE_SIZE
    
    class Config:
        extra = "forbid"


class PeerGroupMemberAdd(BaseModel):
    """Schema for adding a member to a peer group"""
    peer_group_id: UUID
    organization_id: UUID
    
    @validator('peer_group_id')
    def validate_peer_group_id(cls, value):
        """Validate peer group ID"""
        validate_required(value, "peer_group_id")
        validate_uuid(value, "peer_group_id")
        return value
    
    @validator('organization_id')
    def validate_organization_id(cls, value):
        """Validate organization ID"""
        validate_required(value, "organization_id")
        validate_uuid(value, "organization_id")
        return value
    
    class Config:
        extra = "forbid"


class PeerGroupMemberRemove(BaseModel):
    """Schema for removing a member from a peer group"""
    peer_group_id: UUID
    organization_id: UUID
    
    @validator('peer_group_id')
    def validate_peer_group_id(cls, value):
        """Validate peer group ID"""
        validate_required(value, "peer_group_id")
        validate_uuid(value, "peer_group_id")
        return value
    
    @validator('organization_id')
    def validate_organization_id(cls, value):
        """Validate organization ID"""
        validate_required(value, "organization_id")
        validate_uuid(value, "organization_id")
        return value
    
    class Config:
        extra = "forbid"


class PeerGroupMembersList(BaseModel):
    """Schema for list of peer group members"""
    peer_group_id: UUID
    members: List[OrganizationBasic]
    total: int


class CriteriaUpdate(BaseModel):
    """Schema for updating specific peer group criteria"""
    peer_group_id: UUID
    key: str
    value: Any
    
    @validator('peer_group_id')
    def validate_peer_group_id(cls, value):
        """Validate peer group ID"""
        validate_required(value, "peer_group_id")
        validate_uuid(value, "peer_group_id")
        return value
    
    @validator('key')
    def validate_key(cls, value):
        """Validate criteria key"""
        validate_required(value, "key")
        validate_string(value, "key", min_length=1, max_length=100)
        return value
    
    class Config:
        extra = "forbid"