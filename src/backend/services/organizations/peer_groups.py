"""
Service module that provides business logic for managing peer groups, enabling organizations to create collections of similar entities (law firms or clients) for benchmarking and comparative analysis during rate negotiations.
"""

import typing
import uuid
from typing import List, Optional

from ...db.repositories.peer_group_repository import PeerGroupRepository  # PeerGroupRepository: Repository for peer group data access
from ...db.repositories.organization_repository import OrganizationRepository  # OrganizationRepository: Repository for organization data access
from ...db.models.peer_group import PeerGroup  # PeerGroup: Peer Group data model
from ...utils.logging import get_logger  # get_logger: Logging utility for service operations
from ...utils.validators import validate_required, validate_string, validate_uuid, validate_dict  # validate_required, validate_string, validate_uuid, validate_dict: Validation utilities for input parameters
from ...db.session import get_db  # get_db: Database session management

# Set up logger
logger = get_logger(__name__, 'service')


def validate_peer_group_criteria(dict: typing.Dict) -> typing.Tuple[bool, list[str]]:
    """Validates the structure and content of peer group criteria

    Args:
        dict: criteria

    Returns:
        tuple[bool, list[str]]: Validation result (success/failure) and list of error messages
    """
    errors = []  # Initialize empty list for error messages

    if dict is not None and not isinstance(dict, typing.Dict):  # Validate criteria is a dictionary if provided
        errors.append("Criteria must be a dictionary")

    # Add more specific checks based on the criteria type if needed
    # Example: Check for required fields based on criteria type
    # Example: Validate that criteria values are of correct types

    if errors:
        return False, errors  # Return validation result (False if errors) and errors list
    else:
        return True, []  # Return validation result (True if no errors) and errors list


class PeerGroupService:
    """Service class that provides business logic for managing peer groups in the Justice Bid system"""

    def __init__(self, peer_group_repository: Optional[PeerGroupRepository] = None,
                 organization_repository: Optional[OrganizationRepository] = None):
        """Initialize the PeerGroupService with necessary repositories

        Args:
            Optional[PeerGroupRepository]: peer_group_repository
            Optional[OrganizationRepository]: organization_repository
        """
        self._peer_group_repository = peer_group_repository or PeerGroupRepository(get_db())  # Initialize peer_group_repository if provided, otherwise create new instance with get_db()
        self._organization_repository = organization_repository or OrganizationRepository(get_db())  # Initialize organization_repository if provided, otherwise create new instance with get_db()

    def get_peer_group_by_id(self, peer_group_id: uuid.UUID) -> Optional[dict]:
        """Get a peer group by its ID

        Args:
            UUID: peer_group_id

        Returns:
            Optional[dict]: Peer group data as dictionary or None if not found
        """
        validate_uuid(str(peer_group_id), "peer_group_id")  # Validate peer_group_id parameter
        peer_group = self._peer_group_repository.get_by_id(peer_group_id)  # Get peer group from repository using peer_group_id
        if not peer_group:  # If not found, return None
            return None
        return self.peer_group_to_dict(peer_group)  # Convert peer group to dictionary format

    def get_peer_groups_for_organization(self, organization_id: uuid.UUID, active_only: bool) -> List[dict]:
        """Get all peer groups for an organization

        Args:
            UUID: organization_id
            bool: active_only

        Returns:
            List[dict]: List of peer groups as dictionaries
        """
        validate_uuid(str(organization_id), "organization_id")  # Validate organization_id parameter
        peer_groups = self._peer_group_repository.get_by_organization(organization_id, active_only)  # Query repository for peer groups with organization_id
        peer_group_list = []
        for peer_group in peer_groups:  # Convert each peer group to dictionary format
            peer_group_list.append(self.peer_group_to_dict(peer_group))
        return peer_group_list  # Return the list of peer group dictionaries

    def create_peer_group(self, organization_id: uuid.UUID, name: str, criteria: Optional[dict]) -> Optional[dict]:
        """Create a new peer group for an organization

        Args:
            UUID: organization_id
            str: name
            Optional[dict]: criteria

        Returns:
            Optional[dict]: Created peer group data as dictionary or None if creation fails
        """
        validate_required(str(organization_id), "organization_id")  # Validate required parameters (organization_id, name)
        validate_required(name, "name")
        validate_string(name, "name")
        organization = self._organization_repository.get_by_id(organization_id)  # Verify organization exists
        if not organization:
            logger.error(f"Organization with id {organization_id} not found")
            return None
        existing_peer_group = self._peer_group_repository.get_by_organization_and_name(organization_id, name)  # Check if a peer group with the same name already exists for the organization
        if existing_peer_group:  # If exists, log error and return None
            logger.error(f"Peer group with name '{name}' already exists for organization {organization_id}")
            return None
        is_valid, errors = validate_peer_group_criteria(criteria)  # Validate criteria if provided using validate_peer_group_criteria
        if not is_valid:
            logger.error(f"Invalid peer group criteria: {errors}")
            return None
        peer_group = self._peer_group_repository.create(organization_id, name, criteria)  # Create a new peer group using repository
        if not peer_group:  # If creation fails, log error and return None
            logger.error(f"Failed to create peer group for organization {organization_id}")
            return None
        return self.peer_group_to_dict(peer_group)  # Convert created peer group to dictionary format

    def update_peer_group(self, peer_group_id: uuid.UUID, update_data: dict) -> Optional[dict]:
        """Update an existing peer group

        Args:
            UUID: peer_group_id
            dict: update_data

        Returns:
            Optional[dict]: Updated peer group data as dictionary or None if update fails
        """
        validate_required(str(peer_group_id), "peer_group_id")  # Validate required parameters (peer_group_id, update_data)
        validate_required(update_data, "update_data")
        peer_group = self._peer_group_repository.get_by_id(peer_group_id)  # Get peer group from repository
        if not peer_group:  # If not found, log error and return None
            logger.error(f"Peer group with id {peer_group_id} not found")
            return None
        if 'name' in update_data:  # If name is being updated, check for duplicates
            validate_string(update_data['name'], "name")
            existing_peer_group = self._peer_group_repository.get_by_organization_and_name(peer_group.organization_id, update_data['name'])
            if existing_peer_group and existing_peer_group.id != peer_group_id:
                logger.error(f"Peer group with name '{update_data['name']}' already exists for organization {peer_group.organization_id}")
                return None
        if 'criteria' in update_data:  # If criteria is being updated, validate using validate_peer_group_criteria
            is_valid, errors = validate_peer_group_criteria(update_data['criteria'])
            if not is_valid:
                logger.error(f"Invalid peer group criteria: {errors}")
                return None
        peer_group = self._peer_group_repository.update(peer_group_id, update_data)  # Update the peer group using repository
        if not peer_group:  # If update fails, log error and return None
            logger.error(f"Failed to update peer group with id {peer_group_id}")
            return None
        return self.peer_group_to_dict(peer_group)  # Convert updated peer group to dictionary format

    def delete_peer_group(self, peer_group_id: uuid.UUID) -> bool:
        """Delete a peer group

        Args:
            UUID: peer_group_id

        Returns:
            bool: True if successful, False if peer group not found
        """
        validate_uuid(str(peer_group_id), "peer_group_id")  # Validate peer_group_id parameter
        deleted = self._peer_group_repository.delete(peer_group_id)  # Delete peer group using repository
        if deleted:
            logger.info(f"Peer group with id {peer_group_id} deleted successfully")  # Log the deletion result
        else:
            logger.info(f"Peer group with id {peer_group_id} not found")
        return deleted  # Return True if successful, False otherwise

    def add_organization_to_peer_group(self, peer_group_id: uuid.UUID, organization_id: uuid.UUID) -> bool:
        """Add an organization to a peer group

        Args:
            UUID: peer_group_id
            UUID: organization_id

        Returns:
            bool: True if successful, False if peer group not found or addition fails
        """
        validate_uuid(str(peer_group_id), "peer_group_id")  # Validate required parameters (peer_group_id, organization_id)
        validate_uuid(str(organization_id), "organization_id")
        peer_group = self._peer_group_repository.get_by_id(peer_group_id)  # Verify peer group exists
        if not peer_group:
            logger.error(f"Peer group with id {peer_group_id} not found")
            return False
        organization = self._organization_repository.get_by_id(organization_id)  # Verify organization exists
        if not organization:
            logger.error(f"Organization with id {organization_id} not found")
            return False
        added = self._peer_group_repository.add_member(peer_group_id, organization_id)  # Add organization to peer group using repository
        if added:
            logger.info(f"Organization with id {organization_id} added to peer group with id {peer_group_id}")  # Log the addition result
        else:
            logger.info(f"Organization with id {organization_id} already a member of peer group with id {peer_group_id}")
        return added  # Return True if successful, False otherwise

    def remove_organization_from_peer_group(self, peer_group_id: uuid.UUID, organization_id: uuid.UUID) -> bool:
        """Remove an organization from a peer group

        Args:
            UUID: peer_group_id
            UUID: organization_id

        Returns:
            bool: True if successful, False if peer group not found or removal fails
        """
        validate_uuid(str(peer_group_id), "peer_group_id")  # Validate required parameters (peer_group_id, organization_id)
        validate_uuid(str(organization_id), "organization_id")
        removed = self._peer_group_repository.remove_member(peer_group_id, organization_id)  # Remove organization from peer group using repository
        if removed:
            logger.info(f"Organization with id {organization_id} removed from peer group with id {peer_group_id}")  # Log the removal result
        else:
            logger.info(f"Organization with id {organization_id} not a member of peer group with id {peer_group_id}")
        return removed  # Return True if successful, False otherwise

    def get_peer_group_members(self, peer_group_id: uuid.UUID) -> List[dict]:
        """Get all members of a peer group

        Args:
            UUID: peer_group_id

        Returns:
            List[dict]: List of organization members as dictionaries
        """
        validate_uuid(str(peer_group_id), "peer_group_id")  # Validate peer_group_id parameter
        members = self._peer_group_repository.get_members(peer_group_id)  # Get members from repository
        member_list = []
        if members:
            for member in members:  # Convert each organization to dictionary format
                member_list.append(self._organization_repository.get_by_id(member.id).__dict__)
        return member_list  # Return the list of organization dictionaries

    def check_organization_in_peer_group(self, peer_group_id: uuid.UUID, organization_id: uuid.UUID) -> bool:
        """Check if an organization is a member of a peer group

        Args:
            UUID: peer_group_id
            UUID: organization_id

        Returns:
            bool: True if the organization is a member, False otherwise
        """
        validate_uuid(str(peer_group_id), "peer_group_id")  # Validate required parameters (peer_group_id, organization_id)
        validate_uuid(str(organization_id), "organization_id")
        is_member = self._peer_group_repository.is_member(peer_group_id, organization_id)  # Check membership using repository is_member method
        return is_member  # Return True if member, False otherwise

    def update_peer_group_criteria(self, peer_group_id: uuid.UUID, criteria: dict) -> Optional[dict]:
        """Update the criteria for a peer group

        Args:
            UUID: peer_group_id
            dict: criteria

        Returns:
            Optional[dict]: Updated peer group data as dictionary or None if update fails
        """
        validate_required(str(peer_group_id), "peer_group_id")  # Validate required parameters (peer_group_id, criteria)
        validate_required(criteria, "criteria")
        is_valid, errors = validate_peer_group_criteria(criteria)  # Validate criteria using validate_peer_group_criteria
        if not is_valid:
            logger.error(f"Invalid peer group criteria: {errors}")
            return None
        peer_group = self._peer_group_repository.update_criteria(peer_group_id, criteria)  # Update criteria using repository
        if not peer_group:  # If update fails, log error and return None
            logger.error(f"Failed to update peer group criteria with id {peer_group_id}")
            return None
        return self.peer_group_to_dict(peer_group)  # Convert updated peer group to dictionary format

    def set_peer_group_active_status(self, peer_group_id: uuid.UUID, is_active: bool) -> bool:
        """Activate or deactivate a peer group

        Args:
            UUID: peer_group_id
            bool: is_active

        Returns:
            bool: True if successful, False if peer group not found
        """
        validate_uuid(str(peer_group_id), "peer_group_id")  # Validate peer_group_id parameter
        status = self._peer_group_repository.set_active_status(peer_group_id, is_active)  # Set active status using repository
        if status:
            logger.info(f"Peer group with id {peer_group_id} set to active={is_active}")  # Log the status change result
        else:
            logger.info(f"Peer group with id {peer_group_id} not found")
        return status  # Return True if successful, False otherwise

    def search_peer_groups(self, organization_id: uuid.UUID, query: str, limit: int, offset: int) -> List[dict]:
        """Search for peer groups by name

        Args:
            UUID: organization_id
            str: query
            int: limit
            int: offset

        Returns:
            List[dict]: List of peer groups matching the search criteria
        """
        validate_required(str(organization_id), "organization_id")  # Validate required parameters (organization_id, query)
        validate_required(query, "query")
        peer_groups = self._peer_group_repository.search(organization_id, query, limit, offset)  # Search for peer groups using repository
        peer_group_list = []
        for peer_group in peer_groups:  # Convert each peer group to dictionary format
            peer_group_list.append(self.peer_group_to_dict(peer_group))
        return peer_group_list  # Return the list of peer group dictionaries

    def get_peer_groups_for_member(self, organization_id: uuid.UUID, active_only: bool) -> List[dict]:
        """Get all peer groups that an organization is a member of

        Args:
            UUID: organization_id
            bool: active_only

        Returns:
            List[dict]: List of peer groups the organization is a member of
        """
        validate_uuid(str(organization_id), "organization_id")  # Validate organization_id parameter
        peer_groups = self._peer_group_repository.get_peer_groups_for_member(organization_id, active_only)  # Get peer groups using repository get_peer_groups_for_member method
        peer_group_list = []
        for peer_group in peer_groups:  # Convert each peer group to dictionary format
            peer_group_list.append(self.peer_group_to_dict(peer_group))
        return peer_group_list  # Return the list of peer group dictionaries

    def peer_group_to_dict(self, peer_group: PeerGroup) -> dict:
        """Convert a PeerGroup model instance to a dictionary representation

        Args:
            PeerGroup: peer_group

        Returns:
            dict: Dictionary representation of the peer group
        """
        return {
            "id": peer_group.id,  # Extract attributes from PeerGroup model (id, name, criteria, etc.)
            "name": peer_group.name,
            "criteria": peer_group.criteria,
            "organization_id": peer_group.organization_id,
            "is_active": peer_group.is_active
        }  # Build a dictionary with the extracted attributes