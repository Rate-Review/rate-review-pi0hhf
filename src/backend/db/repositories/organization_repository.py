"""
Repository class for organization data access in the Justice Bid Rate Negotiation System.

This module provides a comprehensive data access layer for managing organizations
(law firms and clients) with support for CRUD operations, organizational structure
management, and relationship handling between organizations.
"""

from typing import List, Dict, Optional, Tuple, Any, Union
import uuid
import datetime
import json

from sqlalchemy import or_, and_, not_, func
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from ..models.organization import Organization, OrganizationType, Office, Department
from ..session import session_scope, get_db
from ...utils.logging import get_logger
from ...utils.validators import validate_required, validate_string, validate_email, validate_enum_value

# Set up logger
logger = get_logger(__name__, 'repository')

class OrganizationRepository:
    """
    Repository class that handles database operations for Organization entities,
    providing an abstraction layer over the data access logic.
    """
    
    def __init__(self, db_session: Session):
        """
        Initialize a new OrganizationRepository with a database session.
        
        Args:
            db_session: SQLAlchemy database session
        """
        self._db = db_session
    
    def get_by_id(self, organization_id: uuid.UUID) -> Optional[Organization]:
        """
        Get an organization by its ID.
        
        Args:
            organization_id: UUID of the organization to retrieve
            
        Returns:
            Organization if found, None otherwise
        """
        try:
            return self._db.query(Organization).filter(
                Organization.id == organization_id,
                Organization.is_deleted == False
            ).first()
        except SQLAlchemyError as e:
            logger.error(f"Error retrieving organization by ID {organization_id}: {str(e)}")
            return None
    
    def get_by_domain(self, domain: str) -> Optional[Organization]:
        """
        Get an organization by its domain.
        
        Args:
            domain: Email domain of the organization
            
        Returns:
            Organization if found, None otherwise
        """
        try:
            return self._db.query(Organization).filter(
                func.lower(Organization.domain) == domain.lower(),
                Organization.is_deleted == False
            ).first()
        except SQLAlchemyError as e:
            logger.error(f"Error retrieving organization by domain {domain}: {str(e)}")
            return None
    
    def create(self, name: str, type: OrganizationType, domain: Optional[str] = None, 
               settings: Optional[Dict] = None) -> Optional[Organization]:
        """
        Create a new organization.
        
        Args:
            name: Name of the organization
            type: Type of organization (LAW_FIRM, CLIENT, ADMIN)
            domain: Optional email domain for the organization
            settings: Optional settings for the organization
            
        Returns:
            Created organization or None if creation fails
        """
        try:
            # Validate required fields
            validate_required(name, "name")
            validate_string(name, "name", min_length=2, max_length=255)
            validate_enum_value(type, OrganizationType, "type")
            
            # Validate domain if provided
            if domain:
                validate_string(domain, "domain", max_length=255)
                # Check if an organization with this domain already exists
                existing_org = self.get_by_domain(domain)
                if existing_org:
                    logger.warning(f"Organization with domain {domain} already exists")
                    raise ValueError(f"Organization with domain {domain} already exists")
            
            # Create new organization
            organization = Organization(name=name, type=type, domain=domain)
            
            # Apply settings if provided
            if settings:
                organization.settings = settings
            else:
                # Initialize with default settings
                organization.settings = {
                    "rate_rules": {},
                    "approval_workflow": {},
                    "law_firms": [] if type == OrganizationType.CLIENT else None,
                    "clients": [] if type == OrganizationType.LAW_FIRM else None
                }
            
            # Add to database and commit
            self._db.add(organization)
            self._db.commit()
            
            logger.info(f"Created organization: {name} ({type.value})")
            return organization
            
        except ValueError as e:
            logger.error(f"Validation error creating organization: {str(e)}")
            raise
        except SQLAlchemyError as e:
            self._db.rollback()
            logger.error(f"Database error creating organization: {str(e)}")
            return None
    
    def update(self, organization_id: uuid.UUID, update_data: Dict) -> Optional[Organization]:
        """
        Update an existing organization.
        
        Args:
            organization_id: UUID of the organization to update
            update_data: Dictionary of fields to update
            
        Returns:
            Updated organization if successful, None if not found
        """
        try:
            # Get the organization
            organization = self.get_by_id(organization_id)
            if not organization:
                logger.warning(f"Organization not found for update: {organization_id}")
                return None
            
            # Update name if provided
            if 'name' in update_data:
                validate_string(update_data['name'], "name", min_length=2, max_length=255)
                organization.name = update_data['name']
            
            # Update domain if provided
            if 'domain' in update_data:
                if update_data['domain']:
                    validate_string(update_data['domain'], "domain", max_length=255)
                    
                    # Check if another organization is using this domain
                    existing_org = self.get_by_domain(update_data['domain'])
                    if existing_org and existing_org.id != organization_id:
                        logger.warning(f"Domain {update_data['domain']} already in use by another organization")
                        raise ValueError(f"Domain {update_data['domain']} already in use by another organization")
                    
                organization.domain = update_data['domain']
            
            # Update settings if provided
            if 'settings' in update_data and update_data['settings']:
                # Merge with existing settings to avoid overwriting unrelated settings
                if organization.settings is None:
                    organization.settings = {}
                
                # Update only provided settings keys
                for key, value in update_data['settings'].items():
                    organization.settings[key] = value
            
            # Commit changes
            self._db.commit()
            logger.info(f"Updated organization: {organization_id}")
            return organization
            
        except ValueError as e:
            logger.error(f"Validation error updating organization: {str(e)}")
            raise
        except SQLAlchemyError as e:
            self._db.rollback()
            logger.error(f"Database error updating organization: {str(e)}")
            return None
    
    def delete(self, organization_id: uuid.UUID, deleted_by_id: Optional[uuid.UUID] = None) -> bool:
        """
        Delete an organization (soft delete).
        
        Args:
            organization_id: UUID of the organization to delete
            deleted_by_id: Optional UUID of the user performing the deletion
            
        Returns:
            True if successful, False if not found
        """
        try:
            # Get the organization
            organization = self.get_by_id(organization_id)
            if not organization:
                logger.warning(f"Organization not found for deletion: {organization_id}")
                return False
            
            # Soft delete
            organization.delete(deleted_by_id)
            
            # Commit changes
            self._db.commit()
            logger.info(f"Deleted organization: {organization_id}")
            return True
            
        except SQLAlchemyError as e:
            self._db.rollback()
            logger.error(f"Error deleting organization {organization_id}: {str(e)}")
            return False
    
    def restore(self, organization_id: uuid.UUID) -> bool:
        """
        Restore a soft-deleted organization.
        
        Args:
            organization_id: UUID of the organization to restore
            
        Returns:
            True if successful, False if not found
        """
        try:
            # Get the organization including soft-deleted
            organization = self._db.query(Organization).filter(
                Organization.id == organization_id
            ).first()
            
            if not organization:
                logger.warning(f"Organization not found for restoration: {organization_id}")
                return False
            
            # Restore the organization
            organization.restore()
            
            # Commit changes
            self._db.commit()
            logger.info(f"Restored organization: {organization_id}")
            return True
            
        except SQLAlchemyError as e:
            self._db.rollback()
            logger.error(f"Error restoring organization {organization_id}: {str(e)}")
            return False
    
    def get_all(self, active_only: bool = True, limit: int = 100, offset: int = 0) -> List[Organization]:
        """
        Get all organizations with optional filtering.
        
        Args:
            active_only: Whether to return only active organizations
            limit: Maximum number of organizations to return
            offset: Number of organizations to skip
            
        Returns:
            List of organizations matching criteria
        """
        try:
            query = self._db.query(Organization).filter(
                Organization.is_deleted == False
            )
            
            if active_only:
                query = query.filter(Organization.is_active == True)
            
            # Apply pagination
            query = query.order_by(Organization.name).limit(limit).offset(offset)
            
            return query.all()
            
        except SQLAlchemyError as e:
            logger.error(f"Error retrieving organizations: {str(e)}")
            return []
    
    def get_all_clients(self, active_only: bool = True, limit: int = 100, offset: int = 0) -> List[Organization]:
        """
        Get all client organizations with optional filtering.
        
        Args:
            active_only: Whether to return only active organizations
            limit: Maximum number of organizations to return
            offset: Number of organizations to skip
            
        Returns:
            List of client organizations matching criteria
        """
        try:
            query = self._db.query(Organization).filter(
                Organization.is_deleted == False,
                Organization.type == OrganizationType.CLIENT
            )
            
            if active_only:
                query = query.filter(Organization.is_active == True)
            
            # Apply pagination
            query = query.order_by(Organization.name).limit(limit).offset(offset)
            
            return query.all()
            
        except SQLAlchemyError as e:
            logger.error(f"Error retrieving client organizations: {str(e)}")
            return []
    
    def get_all_law_firms(self, active_only: bool = True, limit: int = 100, offset: int = 0) -> List[Organization]:
        """
        Get all law firm organizations with optional filtering.
        
        Args:
            active_only: Whether to return only active organizations
            limit: Maximum number of organizations to return
            offset: Number of organizations to skip
            
        Returns:
            List of law firm organizations matching criteria
        """
        try:
            query = self._db.query(Organization).filter(
                Organization.is_deleted == False,
                Organization.type == OrganizationType.LAW_FIRM
            )
            
            if active_only:
                query = query.filter(Organization.is_active == True)
            
            # Apply pagination
            query = query.order_by(Organization.name).limit(limit).offset(offset)
            
            return query.all()
            
        except SQLAlchemyError as e:
            logger.error(f"Error retrieving law firm organizations: {str(e)}")
            return []
    
    def search(self, query: str, type: Optional[OrganizationType] = None, 
               limit: int = 100, offset: int = 0) -> List[Organization]:
        """
        Search for organizations by name.
        
        Args:
            query: Search string to match against organization names
            type: Optional organization type to filter by
            limit: Maximum number of organizations to return
            offset: Number of organizations to skip
            
        Returns:
            List of organizations matching the search criteria
        """
        try:
            # Build search query
            search_term = f"%{query}%"
            db_query = self._db.query(Organization).filter(
                Organization.name.ilike(search_term),
                Organization.is_deleted == False,
                Organization.is_active == True
            )
            
            # Filter by type if provided
            if type:
                db_query = db_query.filter(Organization.type == type)
            
            # Apply pagination
            db_query = db_query.order_by(Organization.name).limit(limit).offset(offset)
            
            return db_query.all()
            
        except SQLAlchemyError as e:
            logger.error(f"Error searching organizations with query '{query}': {str(e)}")
            return []
    
    def set_active_status(self, organization_id: uuid.UUID, is_active: bool) -> bool:
        """
        Activate or deactivate an organization.
        
        Args:
            organization_id: UUID of the organization
            is_active: Whether to activate (True) or deactivate (False)
            
        Returns:
            True if successful, False if organization not found
        """
        try:
            # Get the organization
            organization = self.get_by_id(organization_id)
            if not organization:
                logger.warning(f"Organization not found for status update: {organization_id}")
                return False
            
            # Update active status
            if is_active:
                organization.activate()
            else:
                organization.deactivate()
            
            # Commit changes
            self._db.commit()
            logger.info(f"Updated active status for organization {organization_id} to {is_active}")
            return True
            
        except SQLAlchemyError as e:
            self._db.rollback()
            logger.error(f"Error updating active status for organization {organization_id}: {str(e)}")
            return False
    
    def add_office(self, organization_id: uuid.UUID, name: str, city: str, country: str,
                  state: Optional[str] = None, region: Optional[str] = None) -> Optional[Office]:
        """
        Add a new office to an organization.
        
        Args:
            organization_id: UUID of the organization
            name: Name of the office
            city: City where the office is located
            country: Country where the office is located
            state: Optional state/province where the office is located
            region: Optional region/area where the office is located
            
        Returns:
            Created office if successful, None if organization not found
        """
        try:
            # Get the organization
            organization = self.get_by_id(organization_id)
            if not organization:
                logger.warning(f"Organization not found for adding office: {organization_id}")
                return None
            
            # Validate required fields
            validate_required(name, "name")
            validate_string(name, "name", max_length=255)
            validate_required(city, "city")
            validate_string(city, "city", max_length=255)
            validate_required(country, "country")
            validate_string(country, "country", max_length=100)
            
            if state:
                validate_string(state, "state", max_length=100)
            
            if region:
                validate_string(region, "region", max_length=100)
            
            # Create new office
            office = organization.add_office(
                name=name,
                city=city,
                state=state,
                country=country,
                region=region
            )
            
            # Commit changes
            self._db.commit()
            logger.info(f"Added office {name} to organization {organization_id}")
            return office
            
        except ValueError as e:
            logger.error(f"Validation error adding office: {str(e)}")
            raise
        except SQLAlchemyError as e:
            self._db.rollback()
            logger.error(f"Error adding office to organization {organization_id}: {str(e)}")
            return None
    
    def get_offices(self, organization_id: uuid.UUID, active_only: bool = True) -> List[Office]:
        """
        Get all offices for an organization.
        
        Args:
            organization_id: UUID of the organization
            active_only: Whether to return only active offices
            
        Returns:
            List of offices for the organization
        """
        try:
            # Get the organization
            organization = self.get_by_id(organization_id)
            if not organization:
                logger.warning(f"Organization not found for retrieving offices: {organization_id}")
                return []
            
            # Query for offices
            query = self._db.query(Office).filter(
                Office.organization_id == organization_id
            )
            
            if active_only:
                query = query.filter(Office.is_active == True)
            
            return query.order_by(Office.name).all()
            
        except SQLAlchemyError as e:
            logger.error(f"Error retrieving offices for organization {organization_id}: {str(e)}")
            return []
    
    def add_department(self, organization_id: uuid.UUID, name: str, 
                      metadata: Optional[Dict] = None) -> Optional[Department]:
        """
        Add a new department to an organization.
        
        Args:
            organization_id: UUID of the organization
            name: Name of the department
            metadata: Optional metadata for the department
            
        Returns:
            Created department if successful, None if organization not found
        """
        try:
            # Get the organization
            organization = self.get_by_id(organization_id)
            if not organization:
                logger.warning(f"Organization not found for adding department: {organization_id}")
                return None
            
            # Validate required fields
            validate_required(name, "name")
            validate_string(name, "name", max_length=255)
            
            # Create new department
            department = organization.add_department(
                name=name,
                metadata=metadata
            )
            
            # Commit changes
            self._db.commit()
            logger.info(f"Added department {name} to organization {organization_id}")
            return department
            
        except ValueError as e:
            logger.error(f"Validation error adding department: {str(e)}")
            raise
        except SQLAlchemyError as e:
            self._db.rollback()
            logger.error(f"Error adding department to organization {organization_id}: {str(e)}")
            return None
    
    def get_departments(self, organization_id: uuid.UUID, active_only: bool = True) -> List[Department]:
        """
        Get all departments for an organization.
        
        Args:
            organization_id: UUID of the organization
            active_only: Whether to return only active departments
            
        Returns:
            List of departments for the organization
        """
        try:
            # Get the organization
            organization = self.get_by_id(organization_id)
            if not organization:
                logger.warning(f"Organization not found for retrieving departments: {organization_id}")
                return []
            
            # Query for departments
            query = self._db.query(Department).filter(
                Department.organization_id == organization_id
            )
            
            if active_only:
                query = query.filter(Department.is_active == True)
            
            return query.order_by(Department.name).all()
            
        except SQLAlchemyError as e:
            logger.error(f"Error retrieving departments for organization {organization_id}: {str(e)}")
            return []
    
    def update_settings(self, organization_id: uuid.UUID, settings: Dict) -> Optional[Organization]:
        """
        Update an organization's settings.
        
        Args:
            organization_id: UUID of the organization
            settings: Dictionary of settings to update
            
        Returns:
            Updated organization if successful, None if not found
        """
        try:
            # Get the organization
            organization = self.get_by_id(organization_id)
            if not organization:
                logger.warning(f"Organization not found for updating settings: {organization_id}")
                return None
            
            # Update settings
            if organization.settings is None:
                organization.settings = settings
            else:
                # Merge with existing settings to preserve unrelated settings
                for key, value in settings.items():
                    organization.settings[key] = value
            
            # Commit changes
            self._db.commit()
            logger.info(f"Updated settings for organization {organization_id}")
            return organization
            
        except SQLAlchemyError as e:
            self._db.rollback()
            logger.error(f"Error updating settings for organization {organization_id}: {str(e)}")
            return None
    
    def update_rate_rules(self, organization_id: uuid.UUID, rate_rules: Dict) -> Optional[Organization]:
        """
        Update an organization's rate rules.
        
        Args:
            organization_id: UUID of the organization
            rate_rules: Dictionary of rate rules to update
            
        Returns:
            Updated organization if successful, None if not found
        """
        try:
            # Get the organization
            organization = self.get_by_id(organization_id)
            if not organization:
                logger.warning(f"Organization not found for updating rate rules: {organization_id}")
                return None
            
            # Validate that this is a client organization
            if not organization.is_client():
                logger.error(f"Cannot update rate rules for non-client organization: {organization_id}")
                raise ValueError("Rate rules can only be updated for client organizations")
            
            # Update rate rules
            organization.set_rate_rules(rate_rules)
            
            # Commit changes
            self._db.commit()
            logger.info(f"Updated rate rules for organization {organization_id}")
            return organization
            
        except ValueError as e:
            logger.error(f"Validation error updating rate rules: {str(e)}")
            raise
        except SQLAlchemyError as e:
            self._db.rollback()
            logger.error(f"Error updating rate rules for organization {organization_id}: {str(e)}")
            return None
    
    def get_rate_rules(self, organization_id: uuid.UUID) -> Optional[Dict]:
        """
        Get an organization's rate rules.
        
        Args:
            organization_id: UUID of the organization
            
        Returns:
            Rate rules if organization found, None otherwise
        """
        try:
            # Get the organization
            organization = self.get_by_id(organization_id)
            if not organization:
                logger.warning(f"Organization not found for retrieving rate rules: {organization_id}")
                return None
            
            # Validate that this is a client organization
            if not organization.is_client():
                logger.error(f"Cannot get rate rules for non-client organization: {organization_id}")
                raise ValueError("Rate rules are only available for client organizations")
            
            # Get rate rules
            return organization.get_rate_rules()
            
        except ValueError as e:
            logger.error(f"Validation error getting rate rules: {str(e)}")
            raise
        except SQLAlchemyError as e:
            logger.error(f"Error retrieving rate rules for organization {organization_id}: {str(e)}")
            return None
    
    def update_approval_workflow(self, organization_id: uuid.UUID, 
                               approval_workflow: Dict) -> Optional[Organization]:
        """
        Update an organization's approval workflow settings.
        
        Args:
            organization_id: UUID of the organization
            approval_workflow: Dictionary of approval workflow settings
            
        Returns:
            Updated organization if successful, None if not found
        """
        try:
            # Get the organization
            organization = self.get_by_id(organization_id)
            if not organization:
                logger.warning(f"Organization not found for updating approval workflow: {organization_id}")
                return None
            
            # Update approval workflow in settings
            if organization.settings is None:
                organization.settings = {"approval_workflow": approval_workflow}
            else:
                organization.settings["approval_workflow"] = approval_workflow
            
            # Commit changes
            self._db.commit()
            logger.info(f"Updated approval workflow for organization {organization_id}")
            return organization
            
        except SQLAlchemyError as e:
            self._db.rollback()
            logger.error(f"Error updating approval workflow for organization {organization_id}: {str(e)}")
            return None
    
    def get_client_law_firm_relationships(self, client_id: uuid.UUID) -> List[Dict]:
        """
        Get all law firms associated with a client organization.
        
        Args:
            client_id: UUID of the client organization
            
        Returns:
            List of law firm relationships with details
        """
        try:
            # Get the client organization
            client = self.get_by_id(client_id)
            if not client or not client.is_client():
                logger.warning(f"Client organization not found: {client_id}")
                return []
            
            # Extract law firm relationships from settings
            relationships = []
            if client.settings and "law_firms" in client.settings:
                law_firms = client.settings.get("law_firms", [])
                
                for firm_rel in law_firms:
                    firm_id = firm_rel.get("firm_id")
                    if firm_id:
                        # Get additional firm details
                        firm = self.get_by_id(uuid.UUID(firm_id))
                        if firm:
                            relationship = {
                                "firm_id": firm_id,
                                "firm_name": firm.name,
                                "relationship_type": firm_rel.get("relationship_type", "standard"),
                                "status": firm_rel.get("status", "active"),
                                "settings": firm_rel.get("settings", {}),
                                "established_date": firm_rel.get("established_date")
                            }
                            relationships.append(relationship)
            
            return relationships
            
        except SQLAlchemyError as e:
            logger.error(f"Error retrieving law firm relationships for client {client_id}: {str(e)}")
            return []
    
    def get_law_firm_client_relationships(self, firm_id: uuid.UUID) -> List[Dict]:
        """
        Get all clients associated with a law firm organization.
        
        Args:
            firm_id: UUID of the law firm organization
            
        Returns:
            List of client relationships with details
        """
        try:
            # Get the law firm organization
            firm = self.get_by_id(firm_id)
            if not firm or not firm.is_law_firm():
                logger.warning(f"Law firm organization not found: {firm_id}")
                return []
            
            # Extract client relationships from settings
            relationships = []
            if firm.settings and "clients" in firm.settings:
                clients = firm.settings.get("clients", [])
                
                for client_rel in clients:
                    client_id = client_rel.get("client_id")
                    if client_id:
                        # Get additional client details
                        client = self.get_by_id(uuid.UUID(client_id))
                        if client:
                            relationship = {
                                "client_id": client_id,
                                "client_name": client.name,
                                "relationship_type": client_rel.get("relationship_type", "standard"),
                                "status": client_rel.get("status", "active"),
                                "settings": client_rel.get("settings", {}),
                                "established_date": client_rel.get("established_date")
                            }
                            relationships.append(relationship)
            
            return relationships
            
        except SQLAlchemyError as e:
            logger.error(f"Error retrieving client relationships for law firm {firm_id}: {str(e)}")
            return []
    
    def add_relationship(self, client_id: uuid.UUID, firm_id: uuid.UUID, 
                        relationship_settings: Optional[Dict] = None) -> Tuple[Optional[Organization], Optional[Organization]]:
        """
        Add a relationship between a client and a law firm.
        
        Args:
            client_id: UUID of the client organization
            firm_id: UUID of the law firm organization
            relationship_settings: Optional settings for the relationship
            
        Returns:
            Tuple of (client, firm) organizations if successful, or (None, None) if failed
        """
        try:
            # Get the client and firm organizations
            client = self.get_by_id(client_id)
            firm = self.get_by_id(firm_id)
            
            if not client or not firm:
                logger.warning(f"Client or firm not found: client_id={client_id}, firm_id={firm_id}")
                return (None, None)
            
            # Validate organization types
            if not client.is_client():
                logger.error(f"Organization {client_id} is not a client type")
                raise ValueError(f"Organization {client_id} must be a client type")
            
            if not firm.is_law_firm():
                logger.error(f"Organization {firm_id} is not a law firm type")
                raise ValueError(f"Organization {firm_id} must be a law firm type")
            
            # Set default relationship settings if not provided
            if relationship_settings is None:
                relationship_settings = {
                    "relationship_type": "standard",
                    "status": "active",
                    "established_date": datetime.datetime.utcnow().isoformat()
                }
            
            # Update client settings to include the law firm relationship
            if client.settings is None:
                client.settings = {}
            
            if "law_firms" not in client.settings:
                client.settings["law_firms"] = []
            
            # Check if relationship already exists
            existing_relationship = next(
                (rel for rel in client.settings["law_firms"] if rel.get("firm_id") == str(firm_id)),
                None
            )
            
            if existing_relationship:
                # Update existing relationship
                existing_relationship.update(relationship_settings)
                existing_relationship["firm_id"] = str(firm_id)
            else:
                # Add new relationship
                relationship = {"firm_id": str(firm_id), **relationship_settings}
                client.settings["law_firms"].append(relationship)
            
            # Update firm settings to include the client relationship
            if firm.settings is None:
                firm.settings = {}
            
            if "clients" not in firm.settings:
                firm.settings["clients"] = []
            
            # Check if relationship already exists
            existing_relationship = next(
                (rel for rel in firm.settings["clients"] if rel.get("client_id") == str(client_id)),
                None
            )
            
            if existing_relationship:
                # Update existing relationship
                existing_relationship.update(relationship_settings)
                existing_relationship["client_id"] = str(client_id)
            else:
                # Add new relationship
                relationship = {"client_id": str(client_id), **relationship_settings}
                firm.settings["clients"].append(relationship)
            
            # Commit changes
            self._db.commit()
            logger.info(f"Added relationship between client {client_id} and firm {firm_id}")
            return (client, firm)
            
        except ValueError as e:
            logger.error(f"Validation error adding relationship: {str(e)}")
            raise
        except SQLAlchemyError as e:
            self._db.rollback()
            logger.error(f"Error adding relationship between client {client_id} and firm {firm_id}: {str(e)}")
            return (None, None)
    
    def count(self, type: Optional[OrganizationType] = None, active_only: bool = True) -> int:
        """
        Count organizations with optional type filtering.
        
        Args:
            type: Optional organization type to filter by
            active_only: Whether to count only active organizations
            
        Returns:
            Count of organizations matching criteria
        """
        try:
            # Build query
            query = self._db.query(func.count(Organization.id)).filter(
                Organization.is_deleted == False
            )
            
            # Filter by type if provided
            if type:
                query = query.filter(Organization.type == type)
            
            # Filter by active status if requested
            if active_only:
                query = query.filter(Organization.is_active == True)
            
            # Execute count query
            return query.scalar() or 0
            
        except SQLAlchemyError as e:
            logger.error(f"Error counting organizations: {str(e)}")
            return 0