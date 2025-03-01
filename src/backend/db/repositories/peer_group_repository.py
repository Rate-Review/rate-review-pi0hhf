"""
Repository class for managing peer groups in the Justice Bid Rate Negotiation System.
Provides methods for creating, retrieving, updating, and managing peer groups which allow
organizations to create collections of similar organizations for benchmarking and comparative
analysis during rate negotiations.
"""

import uuid
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session

from ..models.peer_group import PeerGroup
from ..models.organization import Organization
from ..session import session_scope, get_db
from ...utils.logging import get_logger
from ...utils.validators import validate_required, validate_string, validate_uuid, validate_dict
from ...utils.constants import OrganizationType

# Set up logger
logger = get_logger(__name__, 'repository')


class PeerGroupRepository:
    """
    Repository class that handles database operations for PeerGroup entities,
    providing an abstraction layer over the data access logic.
    """
    
    def __init__(self, db_session: Session):
        """
        Initialize a new PeerGroupRepository with a database session
        
        Args:
            db_session: SQLAlchemy database session
        """
        self._db = db_session
    
    def get_by_id(self, peer_group_id: uuid.UUID) -> Optional[PeerGroup]:
        """
        Get a peer group by its ID
        
        Args:
            peer_group_id: UUID of the peer group to retrieve
        
        Returns:
            PeerGroup if found, None otherwise
        """
        try:
            return self._db.query(PeerGroup).filter(PeerGroup.id == peer_group_id).first()
        except Exception as e:
            logger.error(f"Error retrieving peer group by ID {peer_group_id}: {str(e)}")
            return None
    
    def get_by_organization_and_name(self, organization_id: uuid.UUID, name: str) -> Optional[PeerGroup]:
        """
        Get a peer group by organization ID and name
        
        Args:
            organization_id: UUID of the organization that owns the peer group
            name: Name of the peer group
        
        Returns:
            PeerGroup if found, None otherwise
        """
        try:
            return self._db.query(PeerGroup).filter(
                PeerGroup.organization_id == organization_id,
                PeerGroup.name == name
            ).first()
        except Exception as e:
            logger.error(f"Error retrieving peer group for organization {organization_id} with name '{name}': {str(e)}")
            return None
    
    def create(self, organization_id: uuid.UUID, name: str, criteria: Optional[dict] = None) -> Optional[PeerGroup]:
        """
        Create a new peer group
        
        Args:
            organization_id: UUID of the organization that owns the peer group
            name: Name of the peer group
            criteria: Optional criteria for peer group membership
        
        Returns:
            Created peer group or None if creation fails
        """
        try:
            # Validate required parameters
            validate_required(organization_id, "organization_id")
            validate_required(name, "name")
            validate_string(name, "name", max_length=255)
            
            # Check if a peer group with the same name already exists
            existing_group = self.get_by_organization_and_name(organization_id, name)
            if existing_group:
                logger.warning(f"Peer group with name '{name}' already exists for organization {organization_id}")
                return None
            
            # Create a new peer group
            criteria = criteria or {}
            peer_group = PeerGroup(organization_id, name, criteria)
            
            # Add to database and commit
            self._db.add(peer_group)
            self._db.commit()
            
            logger.info(f"Created new peer group '{name}' for organization {organization_id}")
            return peer_group
        except Exception as e:
            self._db.rollback()
            logger.error(f"Error creating peer group: {str(e)}")
            return None
    
    def update(self, peer_group_id: uuid.UUID, update_data: dict) -> Optional[PeerGroup]:
        """
        Update an existing peer group
        
        Args:
            peer_group_id: UUID of the peer group to update
            update_data: Dictionary of fields to update
        
        Returns:
            Updated PeerGroup if successful, None if not found
        """
        try:
            # Get the peer group
            peer_group = self.get_by_id(peer_group_id)
            if not peer_group:
                logger.warning(f"Peer group with ID {peer_group_id} not found for update")
                return None
            
            # Update the peer group fields
            if 'name' in update_data:
                # Validate name
                validate_string(update_data['name'], "name", max_length=255)
                
                # Check for duplicates if name is changing
                if peer_group.name != update_data['name']:
                    existing = self.get_by_organization_and_name(peer_group.organization_id, update_data['name'])
                    if existing and existing.id != peer_group_id:
                        logger.warning(f"Cannot update peer group: name '{update_data['name']}' already in use")
                        return None
                
                peer_group.name = update_data['name']
            
            if 'criteria' in update_data:
                validate_dict(update_data['criteria'], "criteria")
                peer_group.criteria = update_data['criteria']
            
            # Commit changes
            self._db.commit()
            
            logger.info(f"Updated peer group {peer_group_id}")
            return peer_group
        except Exception as e:
            self._db.rollback()
            logger.error(f"Error updating peer group {peer_group_id}: {str(e)}")
            return None
    
    def delete(self, peer_group_id: uuid.UUID) -> bool:
        """
        Delete a peer group
        
        Args:
            peer_group_id: UUID of the peer group to delete
        
        Returns:
            True if successful, False if peer group not found
        """
        try:
            # Get the peer group
            peer_group = self.get_by_id(peer_group_id)
            if not peer_group:
                logger.warning(f"Peer group with ID {peer_group_id} not found for deletion")
                return False
            
            # Remove the peer group
            self._db.delete(peer_group)
            self._db.commit()
            
            logger.info(f"Deleted peer group {peer_group_id}")
            return True
        except Exception as e:
            self._db.rollback()
            logger.error(f"Error deleting peer group {peer_group_id}: {str(e)}")
            return False
    
    def get_by_organization(self, organization_id: uuid.UUID, active_only: bool = True) -> List[PeerGroup]:
        """
        Get all peer groups for an organization
        
        Args:
            organization_id: UUID of the organization
            active_only: If True, only return active peer groups
        
        Returns:
            List of peer groups for the organization
        """
        try:
            query = self._db.query(PeerGroup).filter(PeerGroup.organization_id == organization_id)
            
            if active_only:
                query = query.filter(PeerGroup.is_active == True)
            
            return query.all()
        except Exception as e:
            logger.error(f"Error retrieving peer groups for organization {organization_id}: {str(e)}")
            return []
    
    def set_active_status(self, peer_group_id: uuid.UUID, is_active: bool) -> bool:
        """
        Activate or deactivate a peer group
        
        Args:
            peer_group_id: UUID of the peer group
            is_active: True to activate, False to deactivate
        
        Returns:
            True if successful, False if peer group not found
        """
        try:
            # Get the peer group
            peer_group = self.get_by_id(peer_group_id)
            if not peer_group:
                logger.warning(f"Peer group with ID {peer_group_id} not found for status update")
                return False
            
            # Update active status
            if is_active:
                peer_group.activate()
            else:
                peer_group.deactivate()
            
            # Commit changes
            self._db.commit()
            
            logger.info(f"Set peer group {peer_group_id} active status to {is_active}")
            return True
        except Exception as e:
            self._db.rollback()
            logger.error(f"Error updating peer group {peer_group_id} active status: {str(e)}")
            return False
    
    def add_member(self, peer_group_id: uuid.UUID, organization_id: uuid.UUID) -> bool:
        """
        Add an organization to a peer group
        
        Args:
            peer_group_id: UUID of the peer group
            organization_id: UUID of the organization to add
        
        Returns:
            True if successful, False if peer group not found or organization already a member
        """
        try:
            # Get the peer group
            peer_group = self.get_by_id(peer_group_id)
            if not peer_group:
                logger.warning(f"Peer group with ID {peer_group_id} not found for adding member")
                return False
            
            # Get the organization
            organization = self._db.query(Organization).filter(Organization.id == organization_id).first()
            if not organization:
                logger.warning(f"Organization with ID {organization_id} not found for adding to peer group")
                return False
            
            # Get the peer group owner organization
            owner_org = self._db.query(Organization).filter(Organization.id == peer_group.organization_id).first()
            if not owner_org:
                logger.warning(f"Owner organization with ID {peer_group.organization_id} not found for peer group {peer_group_id}")
                return False
            
            # Validate organization type - must match the peer group owner's type
            # Law firms can only be grouped with other law firms, and clients with other clients
            if owner_org.type != organization.type:
                logger.warning(
                    f"Cannot add organization {organization_id} to peer group {peer_group_id}: "
                    f"Type mismatch (owner: {owner_org.type.name}, member: {organization.type.name})"
                )
                return False
            
            # Add the organization to the peer group
            if peer_group.add_member(organization_id):
                self._db.commit()
                logger.info(f"Added organization {organization_id} to peer group {peer_group_id}")
                return True
            else:
                logger.warning(f"Organization {organization_id} is already a member of peer group {peer_group_id}")
                return False
        except Exception as e:
            self._db.rollback()
            logger.error(f"Error adding organization {organization_id} to peer group {peer_group_id}: {str(e)}")
            return False
    
    def remove_member(self, peer_group_id: uuid.UUID, organization_id: uuid.UUID) -> bool:
        """
        Remove an organization from a peer group
        
        Args:
            peer_group_id: UUID of the peer group
            organization_id: UUID of the organization to remove
        
        Returns:
            True if successful, False if peer group not found or organization not a member
        """
        try:
            # Get the peer group
            peer_group = self.get_by_id(peer_group_id)
            if not peer_group:
                logger.warning(f"Peer group with ID {peer_group_id} not found for removing member")
                return False
            
            # Remove the organization from the peer group
            if peer_group.remove_member(organization_id):
                self._db.commit()
                logger.info(f"Removed organization {organization_id} from peer group {peer_group_id}")
                return True
            else:
                logger.warning(f"Organization {organization_id} is not a member of peer group {peer_group_id}")
                return False
        except Exception as e:
            self._db.rollback()
            logger.error(f"Error removing organization {organization_id} from peer group {peer_group_id}: {str(e)}")
            return False
    
    def get_members(self, peer_group_id: uuid.UUID) -> List[Organization]:
        """
        Get all members of a peer group
        
        Args:
            peer_group_id: UUID of the peer group
        
        Returns:
            List of organizations in the peer group
        """
        try:
            # Get the peer group
            peer_group = self.get_by_id(peer_group_id)
            if not peer_group:
                logger.warning(f"Peer group with ID {peer_group_id} not found for getting members")
                return []
            
            # Return the member organizations
            return peer_group.member_organizations
        except Exception as e:
            logger.error(f"Error getting members of peer group {peer_group_id}: {str(e)}")
            return []
    
    def is_member(self, peer_group_id: uuid.UUID, organization_id: uuid.UUID) -> bool:
        """
        Check if an organization is a member of a peer group
        
        Args:
            peer_group_id: UUID of the peer group
            organization_id: UUID of the organization to check
        
        Returns:
            True if the organization is a member, False otherwise
        """
        try:
            # Get the peer group
            peer_group = self.get_by_id(peer_group_id)
            if not peer_group:
                logger.warning(f"Peer group with ID {peer_group_id} not found for checking membership")
                return False
            
            # Check if the organization is a member
            return peer_group.is_member(organization_id)
        except Exception as e:
            logger.error(f"Error checking if organization {organization_id} is a member of peer group {peer_group_id}: {str(e)}")
            return False
    
    def update_criteria(self, peer_group_id: uuid.UUID, criteria: dict) -> Optional[PeerGroup]:
        """
        Update the criteria for a peer group
        
        Args:
            peer_group_id: UUID of the peer group
            criteria: Dictionary of criteria for peer group membership
        
        Returns:
            Updated PeerGroup if successful, None if not found
        """
        try:
            # Get the peer group
            peer_group = self.get_by_id(peer_group_id)
            if not peer_group:
                logger.warning(f"Peer group with ID {peer_group_id} not found for criteria update")
                return None
            
            # Validate criteria
            validate_dict(criteria, "criteria")
            
            # Update criteria
            peer_group.criteria = criteria
            self._db.commit()
            
            logger.info(f"Updated criteria for peer group {peer_group_id}")
            return peer_group
        except Exception as e:
            self._db.rollback()
            logger.error(f"Error updating criteria for peer group {peer_group_id}: {str(e)}")
            return None
    
    def search(self, organization_id: uuid.UUID, query: str, limit: int = 20, offset: int = 0) -> List[PeerGroup]:
        """
        Search for peer groups by name
        
        Args:
            organization_id: UUID of the organization
            query: Search query string
            limit: Maximum number of results to return
            offset: Offset for pagination
        
        Returns:
            List of peer groups matching the search criteria
        """
        try:
            # Build search query
            search_query = self._db.query(PeerGroup).filter(
                PeerGroup.organization_id == organization_id,
                PeerGroup.name.ilike(f"%{query}%"),
                PeerGroup.is_active == True
            ).order_by(PeerGroup.name.asc())
            
            # Apply pagination
            search_query = search_query.limit(limit).offset(offset)
            
            # Execute query and return results
            return search_query.all()
        except Exception as e:
            logger.error(f"Error searching peer groups for organization {organization_id}: {str(e)}")
            return []
    
    def count(self, organization_id: uuid.UUID, active_only: bool = True) -> int:
        """
        Count peer groups for an organization
        
        Args:
            organization_id: UUID of the organization
            active_only: If True, only count active peer groups
        
        Returns:
            Count of peer groups
        """
        try:
            query = self._db.query(PeerGroup).filter(PeerGroup.organization_id == organization_id)
            
            if active_only:
                query = query.filter(PeerGroup.is_active == True)
            
            return query.count()
        except Exception as e:
            logger.error(f"Error counting peer groups for organization {organization_id}: {str(e)}")
            return 0
    
    def get_peer_groups_for_member(self, organization_id: uuid.UUID, active_only: bool = True) -> List[PeerGroup]:
        """
        Get all peer groups that an organization is a member of
        
        Args:
            organization_id: UUID of the organization
            active_only: If True, only return active peer groups
        
        Returns:
            List of peer groups the organization is a member of
        """
        try:
            # Ensure the organization exists
            org_exists = self._db.query(Organization.id).filter(Organization.id == organization_id).first()
            if not org_exists:
                logger.warning(f"Organization with ID {organization_id} not found for getting peer groups")
                return []
            
            # Query peer groups where the organization is a member
            # We use the any() method to filter by membership in the many-to-many relationship
            query = self._db.query(PeerGroup).filter(
                PeerGroup.member_organizations.any(Organization.id == organization_id)
            )
            
            if active_only:
                query = query.filter(PeerGroup.is_active == True)
            
            return query.all()
        except Exception as e:
            logger.error(f"Error getting peer groups for member organization {organization_id}: {str(e)}")
            return []