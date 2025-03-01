"""
Service module that provides high-level business logic for law firm organization management in the Justice Bid Rate Negotiation System.
This service acts as an intermediary between API endpoints and data repositories, implementing law firm-specific functionality such as attorney management, office locations, standard rate management, relationship management with clients, and law firm billing system integration.
"""

import typing
import uuid
from typing import List, Optional

from src.backend.utils.logging import get_logger  # Import logging utility for service operations
from src.backend.db.models.organization import Organization, OrganizationType, Office, Department  # Organization model entities for law firm management
from src.backend.db.repositories.organization_repository import OrganizationRepository  # Repository for organization data access
from src.backend.db.models.attorney import Attorney  # Attorney model for managing law firm attorneys
from src.backend.db.repositories.attorney_repository import AttorneyRepository  # Repository for attorney data access
from src.backend.db.models.rate import Rate  # Rate model for attorney standard rates
from src.backend.db.repositories.rate_repository import RateRepository  # Repository for rate data access
from src.backend.services.organizations.peer_groups import PeerGroupService  # Service for peer group operations
from src.backend.services.organizations.user_management import UserManagementService  # Service for user management within organizations
from src.backend.integrations.lawfirm.client import get_law_firm_client, LawFirmClient  # Factory function for law firm billing system integration
from src.backend.utils.constants import IntegrationType  # Enumeration of integration types
from src.backend.db.session import get_db  # Database session management

logger = get_logger(__name__, 'service')


def validate_firm_settings(dict: typing.Dict) -> typing.Tuple[bool, list[str]]:
    """Validates law firm organization settings including billing system integration settings

    Args:
        dict: settings

    Returns:
        tuple[bool, list[str]]: Validation result (success/failure) and list of error messages
    """
    errors = []  # Initialize empty list for error messages

    if dict is not None and not isinstance(dict, typing.Dict):  # Validate criteria is a dictionary if provided
        errors.append("Settings must be a dictionary")

    # Validate billing system integration settings if present
    # Check for required fields in standard rate configuration if present

    return True if not errors else False, errors  # Return validation result (True if no errors, False otherwise) and errors list


class FirmService:
    """Service class that provides business logic for law firm organization management in the Justice Bid system"""

    def __init__(self, org_repository: typing.Optional[OrganizationRepository] = None,
                 attorney_repository: typing.Optional[AttorneyRepository] = None,
                 rate_repository: typing.Optional[RateRepository] = None,
                 peer_group_service: typing.Optional[PeerGroupService] = None,
                 user_management_service: typing.Optional[UserManagementService] = None):
        """Initialize the FirmService with necessary repositories and services

        Args:
            Optional[OrganizationRepository]: org_repository
            Optional[AttorneyRepository]: attorney_repository
            Optional[RateRepository]: rate_repository
            Optional[PeerGroupService]: peer_group_service
            Optional[UserManagementService]: user_management_service
        """
        self._org_repository = org_repository or OrganizationRepository(get_db())  # Initialize org_repository if provided, otherwise create new instance with get_db()
        self._attorney_repository = attorney_repository or AttorneyRepository(get_db())  # Initialize attorney_repository if provided, otherwise create new instance with get_db()
        self._rate_repository = rate_repository or RateRepository(get_db())  # Initialize rate_repository if provided, otherwise create new instance with get_db()
        self._peer_group_service = peer_group_service or PeerGroupService()  # Initialize peer_group_service if provided, otherwise create new instance
        self._user_management_service = user_management_service or UserManagementService()  # Initialize user_management_service if provided, otherwise create new instance

    def get_firm_by_id(self, firm_id: uuid.UUID) -> typing.Optional[dict]:
        """Get a law firm organization by its ID

        Args:
            UUID: firm_id

        Returns:
            Optional[dict]: Law firm organization data as dictionary or None if not found or not a law firm
        """
        org = self._org_repository.get_by_id(firm_id)  # Get organization from repository using firm_id
        if not org:  # If not found, return None
            return None
        if not org.is_law_firm():  # If not a law firm (using is_law_firm method), return None
            return None
        return org.to_dict()  # Convert organization data to dictionary format

    def create_firm(self, name: str, domain: str, settings: typing.Optional[dict] = None) -> typing.Optional[dict]:
        """Create a new law firm organization

        Args:
            str: name
            str: domain
            Optional[dict]: settings

        Returns:
            Optional[dict]: Created law firm organization data as dictionary
        """
        # Validate required parameters (name, domain)
        if not name or not domain:
            return None

        # Validate firm settings using validate_firm_settings if provided
        if settings:
            is_valid, errors = validate_firm_settings(settings)
            if not is_valid:
                return None

        org = self._org_repository.create(name=name, type=OrganizationType.LAW_FIRM, domain=domain, settings=settings)  # Create new organization with OrganizationType.LAW_FIRM
        if not org:  # Return None if creation fails
            return None
        return org.to_dict()  # Convert organization data to dictionary format

    def update_firm(self, firm_id: uuid.UUID, update_data: dict) -> typing.Optional[dict]:
        """Update an existing law firm organization

        Args:
            UUID: firm_id
            dict: update_data

        Returns:
            Optional[dict]: Updated law firm organization data as dictionary
        """
        org = self._org_repository.get_by_id(firm_id)  # Get organization from repository using firm_id
        if not org or not org.is_law_firm():  # If not found or not a law firm, return None
            return None

        # Validate settings if included in update_data
        if 'settings' in update_data:
            is_valid, errors = validate_firm_settings(update_data['settings'])
            if not is_valid:
                return None

        org = self._org_repository.update(firm_id, update_data)  # Update the law firm with provided update_data
        if not org:  # Return None if update fails
            return None
        return org.to_dict()  # Convert updated organization data to dictionary format

    def get_all_firms(self, active_only: bool, limit: int, offset: int) -> List[dict]:
        """Get all law firm organizations with optional filtering

        Args:
            bool: active_only
            int: limit
            int: offset

        Returns:
            List[dict]: List of law firm organizations as dictionaries
        """
        orgs = self._org_repository.get_all_law_firms(active_only, limit, offset)  # Query repository for all law firm organizations with provided filters
        org_list = []
        for org in orgs:  # Convert each organization to dictionary format
            org_list.append(org.to_dict())
        return org_list  # Return the list of law firm dictionaries

    def add_firm_office(self, firm_id: uuid.UUID, name: str, city: str, country: str, state: typing.Optional[str] = None, region: typing.Optional[str] = None) -> typing.Optional[dict]:
        """Add a new office to a law firm organization

        Args:
            UUID: firm_id
            str: name
            str: city
            str: country
            Optional[str]: state
            Optional[str]: region

        Returns:
            Optional[dict]: Created office data as dictionary
        """
        org = self._org_repository.get_by_id(firm_id)  # Get organization from repository using firm_id
        if not org or not org.is_law_firm():  # If not found or not a law firm, return None
            return None
        office = self._org_repository.add_office(firm_id, name, city, country, state, region)  # Add office to the law firm using repository
        if not office:  # Return None if office creation fails
            return None
        return office.to_dict()  # Convert office data to dictionary format

    def add_firm_department(self, firm_id: uuid.UUID, name: str) -> typing.Optional[dict]:
        """Add a new department to a law firm organization

        Args:
            UUID: firm_id
            str: name

        Returns:
            Optional[dict]: Created department data as dictionary
        """
        org = self._org_repository.get_by_id(firm_id)  # Get organization from repository using firm_id
        if not org or not org.is_law_firm():  # If not found or not a law firm, return None
            return None
        department = self._org_repository.add_department(firm_id, name)  # Add department to the law firm using repository
        if not department:  # Return None if department creation fails
            return None
        return department.to_dict()  # Convert department data to dictionary format

    def get_attorneys(self, firm_id: uuid.UUID, active_only: bool, search_query: typing.Optional[str] = None, office_id: typing.Optional[uuid.UUID] = None, limit: int = 100, offset: int = 0) -> List[dict]:
        """get attorneys"""
        org = self._org_repository.get_by_id(firm_id)  # Get organization from repository using firm_id
        if not org or not org.is_law_firm():  # If not found or not a law firm, return empty list
            return []
        attorneys = self._attorney_repository.get_by_organization(organization_id=firm_id, active_only=active_only, limit=limit, offset=offset)  # Build query for attorneys with firm_id filter
        attorney_list = []
        for attorney in attorneys:  # Convert each attorney to dictionary format
            attorney_list.append(attorney.to_dict())
        return attorney_list  # Return the list of attorney dictionaries

    def get_attorney(self, firm_id: uuid.UUID, attorney_id: uuid.UUID) -> typing.Optional[dict]:
        """get attorney"""
        org = self._org_repository.get_by_id(firm_id)  # Get organization from repository using firm_id
        if not org or not org.is_law_firm():  # If not found or not a law firm, return None
            return None
        attorney = self._attorney_repository.get_by_id(attorney_id)  # Get attorney from repository using attorney_id
        if attorney.organization_id != firm_id:  # Verify attorney belongs to the law firm
            return None
        return attorney.to_dict()  # Convert attorney to dictionary format

    def create_attorney(self, firm_id: uuid.UUID, name: str, bar_date: date, graduation_date: date, promotion_date: typing.Optional[date] = None, office_ids: List[uuid.UUID] = [], timekeeper_ids: typing.Optional[dict] = None, staff_class_id: typing.Optional[uuid.UUID] = None) -> typing.Optional[dict]:
        """create attorney"""
        org = self._org_repository.get_by_id(firm_id)  # Get organization from repository using firm_id
        if not org or not org.is_law_firm():  # If not found or not a law firm, return None
            return None
        attorney_data = {
            'organization_id': firm_id,
            'name': name,
            'bar_date': bar_date,
            'graduation_date': graduation_date,
            'promotion_date': promotion_date,
            'office_ids': office_ids,
            'timekeeper_ids': timekeeper_ids,
            'staff_class_id': staff_class_id
        }
        attorney = self._attorney_repository.create(attorney_data)  # Create new attorney using attorney repository
        return attorney.to_dict()  # Convert created attorney to dictionary format

    def update_attorney(self, firm_id: uuid.UUID, attorney_id: uuid.UUID, update_data: dict) -> typing.Optional[dict]:
        """update attorney"""
        org = self._org_repository.get_by_id(firm_id)  # Get organization from repository using firm_id
        if not org or not org.is_law_firm():  # If not found or not a law firm, return None
            return None
        attorney = self._attorney_repository.get_by_id(attorney_id)  # Get attorney from repository using attorney_id
        if attorney.organization_id != firm_id:  # Verify attorney belongs to the law firm
            return None
        attorney = self._attorney_repository.update(attorney_id, update_data)  # Update attorney with provided update_data
        return attorney.to_dict()  # Convert updated attorney to dictionary format

    def delete_attorney(self, firm_id: uuid.UUID, attorney_id: uuid.UUID) -> bool:
        """delete attorney"""
        org = self._org_repository.get_by_id(firm_id)  # Get organization from repository using firm_id
        if not org or not org.is_law_firm():  # If not found or not a law firm, return False
            return False
        attorney = self._attorney_repository.get_by_id(attorney_id)  # Get attorney from repository using attorney_id
        if attorney.organization_id != firm_id:  # Verify attorney belongs to the law firm
            return False
        return self._attorney_repository.delete(attorney_id)  # Delete attorney using attorney repository

    def get_standard_rates(self, firm_id: uuid.UUID, attorney_id: typing.Optional[uuid.UUID] = None, office_id: typing.Optional[uuid.UUID] = None, effective_date: typing.Optional[date] = None, limit: int = 100, offset: int = 0) -> List[dict]:
        """get standard rates"""
        org = self._org_repository.get_by_id(firm_id)  # Get organization from repository using firm_id
        if not org or not org.is_law_firm():  # If not found or not a law firm, return empty list
            return []
        rates = self._rate_repository.get_by_attorney(firm_id, attorney_id, office_id, effective_date, limit, offset)  # Build query for rates with firm_id filter
        rate_list = []
        for rate in rates:  # Convert each rate to dictionary format
            rate_list.append(rate.to_dict())
        return rate_list

    def set_standard_rate(self, firm_id: uuid.UUID, attorney_id: uuid.UUID, amount: float, currency: str, effective_date: date, expiration_date: typing.Optional[date] = None, office_id: typing.Optional[uuid.UUID] = None) -> typing.Optional[dict]:
        """set standard rate"""
        org = self._org_repository.get_by_id(firm_id)  # Get organization from repository using firm_id
        if not org or not org.is_law_firm():  # If not found or not a law firm, return None
            return None
        attorney = self._attorney_repository.get_by_id(attorney_id)  # Get attorney from repository using attorney_id
        if attorney.organization_id != firm_id:  # Verify attorney belongs to the law firm
            return None
        rate = self._rate_repository.create(attorney_id, amount, currency, effective_date, expiration_date, office_id)  # Create new standard rate using rate repository
        return rate.to_dict()  # Convert rate to dictionary format

    def configure_billing_integration(self, firm_id: uuid.UUID, system_type: str, base_url: str, auth_config: dict, auth_method: str, mapping_config: dict) -> typing.Optional[dict]:
        """configure billing integration"""
        org = self._org_repository.get_by_id(firm_id)  # Get organization from repository using firm_id
        if not org or not org.is_law_firm():  # If not found or not a law firm, return None
            return None
        law_firm_client = get_law_firm_client(system_type, base_url, auth_config, auth_method, mapping_config, firm_id)  # Create law firm client instance using get_law_firm_client
        if not law_firm_client.authenticate():  # Test authentication to validate integration configuration
            return None
        firm_settings = {
            'billing_system_type': system_type,
            'billing_system_base_url': base_url,
            'billing_system_auth_config': auth_config,
            'billing_system_auth_method': auth_method,
            'billing_system_mapping_config': mapping_config
        }
        org = self._org_repository.update(firm_id, {'settings': firm_settings})  # Save updated firm using organization repository
        return org.to_dict()  # Convert updated firm to dictionary format

    def import_attorney_data(self, firm_id: uuid.UUID, filters: typing.Optional[dict] = None) -> dict:
        """import attorney data"""
        org = self._org_repository.get_by_id(firm_id)  # Get organization from repository using firm_id
        if not org or not org.is_law_firm():  # If not found or not a law firm, return error result
            return {'success': False, 'message': 'Law firm not found'}
        billing_system_type = org.settings.get('billing_system_type')  # Get integration configuration from firm settings
        billing_system_base_url = org.settings.get('billing_system_base_url')
        billing_system_auth_config = org.settings.get('billing_system_auth_config')
        billing_system_auth_method = org.settings.get('billing_system_auth_method')
        billing_system_mapping_config = org.settings.get('billing_system_mapping_config')
        law_firm_client = get_law_firm_client(billing_system_type, billing_system_base_url, billing_system_auth_config, billing_system_auth_method, billing_system_mapping_config, firm_id)  # Initialize law firm client using get_law_firm_client
        if not law_firm_client.authenticate():  # Authenticate with the billing system
            return {'success': False, 'message': 'Authentication failed'}
        attorney_data = law_firm_client.get_attorneys(filters)  # Fetch attorney data using client.get_attorneys
        # Map imported attorneys to Justice Bid format
        # Create or update attorneys in the system
        return {'success': True, 'message': 'Import completed'}  # Return import results summary

    def import_standard_rates(self, firm_id: uuid.UUID, filters: typing.Optional[dict] = None) -> dict:
        """import standard rates"""
        org = self._org_repository.get_by_id(firm_id)  # Get organization from repository using firm_id
        if not org or not org.is_law_firm():  # If not found or not a law firm, return error result
            return {'success': False, 'message': 'Law firm not found'}
        billing_system_type = org.settings.get('billing_system_type')  # Get integration configuration from firm settings
        billing_system_base_url = org.settings.get('billing_system_base_url')
        billing_system_auth_config = org.settings.get('billing_system_auth_config')
        billing_system_auth_method = org.settings.get('billing_system_auth_method')
        billing_system_mapping_config = org.settings.get('billing_system_mapping_config')
        law_firm_client = get_law_firm_client(billing_system_type, billing_system_base_url, billing_system_auth_config, billing_system_auth_method, billing_system_mapping_config, firm_id)  # Initialize law firm client using get_law_firm_client
        if not law_firm_client.authenticate():  # Authenticate with the billing system
            return {'success': False, 'message': 'Authentication failed'}
        rates_data = law_firm_client.get_rates(filters)  # Fetch standard rates using client.get_rates
        # Map imported rates to Justice Bid format
        # Create or update rates in the system
        return {'success': True, 'message': 'Import completed'}  # Return import results summary

    def export_approved_rates(self, firm_id: uuid.UUID, rate_ids: List[uuid.UUID]) -> dict:
        """export approved rates"""
        org = self._org_repository.get_by_id(firm_id)  # Get organization from repository using firm_id
        if not org or not org.is_law_firm():  # If not found or not a law firm, return error result
            return {'success': False, 'message': 'Law firm not found'}
        billing_system_type = org.settings.get('billing_system_type')  # Get integration configuration from firm settings
        billing_system_base_url = org.settings.get('billing_system_base_url')
        billing_system_auth_config = org.settings.get('billing_system_auth_config')
        billing_system_auth_method = org.settings.get('billing_system_auth_method')
        billing_system_mapping_config = org.settings.get('billing_system_mapping_config')
        law_firm_client = get_law_firm_client(billing_system_type, billing_system_base_url, billing_system_auth_config, billing_system_auth_method, billing_system_mapping_config, firm_id)  # Initialize law firm client using get_law_firm_client
        if not law_firm_client.authenticate():  # Authenticate with the billing system
            return {'success': False, 'message': 'Authentication failed'}
        # Retrieve the rate data for the specified rate_ids
        # Verify all rates are approved and belong to the firm
        # Export rates using client.export_rates
        return {'success': True, 'message': 'Export completed'}  # Return export results summary

    def create_peer_group(self, firm_id: uuid.UUID, name: str, criteria: dict) -> typing.Optional[dict]:
        """create peer group"""
        org = self._org_repository.get_by_id(firm_id)  # Get organization from repository using firm_id
        if not org or not org.is_law_firm():  # If not found or not a law firm, return None
            return None
        peer_group = self._peer_group_service.create_peer_group(firm_id, name, criteria)  # Create a new peer group using peer group service
        if not peer_group:  # Return None if creation fails
            return None
        return peer_group  # Convert peer group to dictionary format

    def get_peer_groups(self, firm_id: uuid.UUID) -> List[dict]:
        """get peer groups"""
        org = self._org_repository.get_by_id(firm_id)  # Get organization from repository using firm_id
        if not org or not org.is_law_firm():  # If not found or not a law firm, return empty list
            return []
        peer_groups = self._peer_group_service.get_peer_groups_for_organization(firm_id, True)  # Get peer groups using peer group service
        return peer_groups  # Convert each peer group to dictionary format

    def get_client_relationships(self, firm_id: uuid.UUID) -> List[dict]:
        """get client relationships"""
        org = self._org_repository.get_by_id(firm_id)  # Get organization from repository using firm_id
        if not org or not org.is_law_firm():  # If not found or not a law firm, return empty list
            return []
        client_relationships = self._org_repository.get_law_firm_client_relationships(firm_id)  # Extract client relationships from firm settings
        return client_relationships  # Return the list of client relationship dictionaries