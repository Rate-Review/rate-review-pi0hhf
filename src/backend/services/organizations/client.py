"""
Service module that provides high-level business logic for client organization management in the Justice Bid Rate Negotiation System.
This service acts as an intermediary between API endpoints and data repositories, implementing client-specific functionality such as
rate rules, eBilling integration, Outside Counsel Guidelines management, approval workflow configuration, and law firm relationship management.
"""

import typing
import uuid
from typing import List, Optional

from src.backend.db.models.organization import Organization, OrganizationType, Office, Department
from src.backend.db.repositories.organization_repository import OrganizationRepository
from src.backend.db.repositories.ocg_repository import OCGRepository
from src.backend.db.repositories.approval_workflow_repository import ApprovalWorkflowRepository
from src.backend.services.organizations.peer_groups import PeerGroupService
from src.backend.services.organizations.user_management import UserManagementService
from src.backend.integrations.ebilling import create_ebilling_adapter
from src.backend.utils.constants import IntegrationType
from src.backend.services.rates.rules import get_organization_rate_rules, validate_rate_rules, get_default_rate_rules
from src.backend.utils.logging import get_logger
from src.backend.db.session import get_db

logger = get_logger(__name__, 'service')


def validate_client_settings(settings: dict) -> typing.Tuple[bool, list[str]]:
    """Validates client organization settings including eBilling integration and rate rules"""
    errors = []  # Initialize empty list for error messages

    # Validate eBilling system integration settings if present
    if 'ebilling_integration' in settings:
        ebilling_settings = settings['ebilling_integration']
        # Check for required fields based on integration type
        # Add more specific checks based on the integration type

        if 'type' not in ebilling_settings:
            errors.append("eBilling integration type is required")
        else:
            integration_type = ebilling_settings['type']
            if integration_type not in [e.value for e in IntegrationType]:
                errors.append(f"Invalid eBilling integration type: {integration_type}")

    # Validate rate rules if present
    if 'rate_rules' in settings:
        rate_rules = settings['rate_rules']
        # Check for required fields in rate rules
        # Add more specific checks based on the rate rule types
        if not isinstance(rate_rules, dict):
            errors.append("Rate rules must be a dictionary")

    # Validate approval workflow settings if present
    if 'approval_workflow' in settings:
        approval_workflow = settings['approval_workflow']
        # Check for required fields in approval workflow
        # Add more specific checks based on the workflow type
        if not isinstance(approval_workflow, dict):
            errors.append("Approval workflow must be a dictionary")

    if errors:
        return False, errors  # Return validation result (False if errors) and errors list
    else:
        return True, []  # Return validation result (True if no errors) and errors list


class ClientService:
    """Service class that provides business logic for client organization management in the Justice Bid system"""

    def __init__(
        self,
        org_repository: Optional[OrganizationRepository] = None,
        ocg_repository: Optional[OCGRepository] = None,
        approval_workflow_repository: Optional[ApprovalWorkflowRepository] = None,
        peer_group_service: Optional[PeerGroupService] = None,
        user_management_service: Optional[UserManagementService] = None
    ):
        """Initialize the ClientService with necessary repositories and services"""
        self._org_repository = org_repository or OrganizationRepository(get_db())
        self._ocg_repository = ocg_repository or OCGRepository(get_db())
        self._approval_workflow_repository = approval_workflow_repository or ApprovalWorkflowRepository(get_db())
        self._peer_group_service = peer_group_service or PeerGroupService()
        self._user_management_service = user_management_service or UserManagementService()

    def get_client_by_id(self, client_id: uuid.UUID) -> Optional[dict]:
        """Get a client organization by its ID"""
        organization = self._org_repository.get_by_id(client_id)
        if not organization:
            return None
        if not organization.is_client():
            return None
        return organization.as_dict()

    def create_client(self, name: str, domain: str, settings: Optional[dict] = None) -> Optional[dict]:
        """Create a new client organization"""
        is_valid, errors = validate_client_settings(settings) if settings else (True, [])
        if not is_valid:
            logger.error(f"Invalid client settings: {errors}")
            return None
        organization = self._org_repository.create(name=name, type=OrganizationType.CLIENT, domain=domain, settings=settings)
        if not organization:
            return None
        return organization.as_dict()

    def update_client(self, client_id: uuid.UUID, update_data: dict) -> Optional[dict]:
        """Update an existing client organization"""
        organization = self._org_repository.get_by_id(client_id)
        if not organization or not organization.is_client():
            return None
        if 'settings' in update_data:
            is_valid, errors = validate_client_settings(update_data['settings'])
            if not is_valid:
                logger.error(f"Invalid client settings: {errors}")
                return None
        organization = self._org_repository.update(client_id, update_data)
        if not organization:
            return None
        return organization.as_dict()

    def get_all_clients(self, active_only: bool, limit: int, offset: int) -> List[dict]:
        """Get all client organizations with optional filtering"""
        clients = self._org_repository.get_all_clients(active_only=active_only, limit=limit, offset=offset)
        return [client.as_dict() for client in clients]

    def add_client_office(self, client_id: uuid.UUID, name: str, city: str, country: str, state: Optional[str] = None, region: Optional[str] = None) -> Optional[dict]:
        """Add a new office to a client organization"""
        office = self._org_repository.add_office(client_id, name, city, country, state, region)
        if not office:
            return None
        return office.as_dict()

    def add_client_department(self, client_id: uuid.UUID, name: str, metadata: Optional[dict] = None) -> Optional[dict]:
        """Add a new department to a client organization"""
        department = self._org_repository.add_department(client_id, name, metadata)
        if not department:
            return None
        return department.as_dict()

    def get_rate_rules(self, client_id: uuid.UUID) -> dict:
        """Get the rate rules for a client organization"""
        return self._org_repository.get_rate_rules(client_id)

    def update_rate_rules(self, client_id: uuid.UUID, rate_rules: dict) -> Optional[dict]:
        """Update the rate rules for a client organization"""
        organization = self._org_repository.update_rate_rules(client_id, rate_rules)
        if not organization:
            return None
        return organization.as_dict()

    def configure_ebilling_integration(self, client_id: uuid.UUID, system_type: str, base_url: str, auth_config: dict, auth_method: str, mapping_config: dict) -> Optional[dict]:
        """Configure an eBilling system integration for a client"""
        organization = self._org_repository.get_by_id(client_id)
        if not organization or not organization.is_client():
            return None
        # TODO: Implement eBilling integration logic
        return organization.as_dict()

    def test_ebilling_connection(self, client_id: uuid.UUID) -> dict:
        """Test connection to a client's eBilling system"""
        organization = self._org_repository.get_by_id(client_id)
        if not organization or not organization.is_client():
            return {'success': False, 'message': 'Client not found'}
        # TODO: Implement eBilling connection test logic
        return {'success': True, 'message': 'Connection successful'}

    def import_historical_data(self, client_id: uuid.UUID, filters: Optional[dict] = None) -> dict:
        """Import historical rate and billing data from a client's eBilling system"""
        organization = self._org_repository.get_by_id(client_id)
        if not organization or not organization.is_client():
            return {'success': False, 'message': 'Client not found'}
        # TODO: Implement historical data import logic
        return {'success': True, 'message': 'Data import started'}

    def export_approved_rates(self, client_id: uuid.UUID, rate_ids: List[uuid.UUID]) -> dict:
        """Export approved rates to a client's eBilling system"""
        organization = self._org_repository.get_by_id(client_id)
        if not organization or not organization.is_client():
            return {'success': False, 'message': 'Client not found'}
        # TODO: Implement approved rates export logic
        return {'success': True, 'message': 'Rates export started'}

    def create_ocg(self, client_id: uuid.UUID, name: str, total_points: Optional[int] = None, default_firm_point_budget: Optional[int] = None, settings: Optional[dict] = None) -> Optional[dict]:
        """Create a new Outside Counsel Guidelines document"""
        organization = self._org_repository.get_by_id(client_id)
        if not organization or not organization.is_client():
            return None
        ocg = self._ocg_repository.create(client_id=client_id, name=name, total_points=total_points, default_firm_point_budget=default_firm_point_budget, settings=settings)
        if not ocg:
            return None
        return ocg.as_dict()

    def get_ocg(self, ocg_id: uuid.UUID, client_id: uuid.UUID) -> Optional[dict]:
        """Get an OCG by its ID"""
        ocg = self._ocg_repository.get_by_id(ocg_id)
        if not ocg:
            return None
        if ocg.client_id != client_id:
            logger.warning(f"Unauthorized access attempt: OCG {ocg_id} does not belong to client {client_id}")
            return None
        return ocg.as_dict()

    def get_client_ocgs(self, client_id: uuid.UUID, limit: Optional[int] = None, offset: Optional[int] = None) -> List[dict]:
        """Get all OCGs for a client"""
        organization = self._org_repository.get_by_id(client_id)
        if not organization or not organization.is_client():
            return []
        ocgs = self._ocg_repository.get_by_client(client_id, limit=limit, offset=offset)
        return [ocg.as_dict() for ocg in ocgs]

    def update_ocg(self, ocg_id: uuid.UUID, client_id: uuid.UUID, update_data: dict) -> Optional[dict]:
        """Update an OCG"""
        ocg = self._ocg_repository.get_by_id(ocg_id)
        if not ocg:
            return None
        if ocg.client_id != client_id:
            logger.warning(f"Unauthorized access attempt: OCG {ocg_id} does not belong to client {client_id}")
            return None
        ocg = self._ocg_repository.update(ocg_id, update_data)
        if not ocg:
            return None
        return ocg.as_dict()

    def add_ocg_section(self, ocg_id: uuid.UUID, client_id: uuid.UUID, title: str, content: str, is_negotiable: bool, parent_id: Optional[uuid.UUID] = None) -> Optional[dict]:
        """Add a section to an OCG"""
        ocg = self._ocg_repository.get_by_id(ocg_id)
        if not ocg:
            return None
        if ocg.client_id != client_id:
            logger.warning(f"Unauthorized access attempt: OCG {ocg_id} does not belong to client {client_id}")
            return None
        section = self._ocg_repository.add_section(ocg_id, title, content, is_negotiable, parent_id)
        if not section:
            return None
        return section.as_dict()

    def add_section_alternative(self, section_id: uuid.UUID, client_id: uuid.UUID, title: str, content: str, points: int) -> Optional[dict]:
        """Add an alternative to an OCG section"""
        section = self._ocg_repository.get_section(section_id)
        if not section:
            return None
        ocg = self._ocg_repository.get_by_id(section.ocg_id)
        if ocg.client_id != client_id:
            logger.warning(f"Unauthorized access attempt: OCG {ocg.id} does not belong to client {client_id}")
            return None
        alternative = self._ocg_repository.add_alternative(section_id, title, content, points)
        if not alternative:
            return None
        return alternative.as_dict()

    def set_firm_point_budget(self, ocg_id: uuid.UUID, client_id: uuid.UUID, firm_id: uuid.UUID, points: int) -> bool:
        """Set a custom point budget for a law firm's OCG negotiation"""
        ocg = self._ocg_repository.get_by_id(ocg_id)
        if not ocg:
            return False
        if ocg.client_id != client_id:
            logger.warning(f"Unauthorized access attempt: OCG {ocg_id} does not belong to client {client_id}")
            return False
        return self._ocg_repository.set_firm_point_budget(ocg_id, firm_id, points)

    def create_approval_workflow(self, client_id: uuid.UUID, name: str, workflow_type: str, description: Optional[str] = None, criteria: Optional[dict] = None, applicable_entities: Optional[dict] = None) -> Optional[dict]:
        """Create a new approval workflow for a client"""
        organization = self._org_repository.get_by_id(client_id)
        if not organization or not organization.is_client():
            return None
        workflow = self._approval_workflow_repository.create(client_id, name, workflow_type, description, criteria, applicable_entities)
        if not workflow:
            return None
        return workflow.as_dict()

    def get_approval_workflows(self, client_id: uuid.UUID, workflow_type: Optional[str] = None) -> List[dict]:
        """Get all approval workflows for a client"""
        organization = self._org_repository.get_by_id(client_id)
        if not organization or not organization.is_client():
            return []
        workflows = self._approval_workflow_repository.get_approval_workflows(client_id, workflow_type)
        return [workflow.as_dict() for workflow in workflows]

    def add_workflow_step(self, workflow_id: uuid.UUID, client_id: uuid.UUID, order: int, approver_id: Optional[uuid.UUID] = None, approver_role: Optional[str] = None, is_required: bool = True) -> Optional[dict]:
        """Add a step to an approval workflow"""
        workflow = self._approval_workflow_repository.get_by_id(workflow_id)
        if not workflow:
            return None
        if workflow.organization_id != client_id:
            logger.warning(f"Unauthorized access attempt: Workflow {workflow_id} does not belong to client {client_id}")
            return None
        step = self._approval_workflow_repository.add_step(workflow_id, order, approver_id, approver_role, is_required)
        if not step:
            return None
        return step.as_dict()

    def get_law_firm_relationships(self, client_id: uuid.UUID) -> List[dict]:
        """Get all law firm relationships for a client"""
        organization = self._org_repository.get_by_id(client_id)
        if not organization or not organization.is_client():
            return []
        return self._org_repository.get_client_law_firm_relationships(client_id)

    def add_law_firm_relationship(self, client_id: uuid.UUID, firm_id: uuid.UUID, relationship_settings: Optional[dict] = None) -> Optional[dict]:
        """Add a relationship between a client and a law firm"""
        client, firm = self._org_repository.add_relationship(client_id, firm_id, relationship_settings)
        if not client or not firm:
            return None
        return client.as_dict()

    def create_peer_group(self, client_id: uuid.UUID, name: str, criteria: dict, description: Optional[str] = None) -> Optional[dict]:
        """Create a peer group for a client organization"""
        organization = self._org_repository.get_by_id(client_id)
        if not organization or not organization.is_client():
            return None
        peer_group = self._peer_group_service.create_peer_group(client_id, name, criteria)
        if not peer_group:
            return None
        return peer_group

    def get_peer_groups(self, client_id: uuid.UUID) -> List[dict]:
        """Get all peer groups for a client organization"""
        organization = self._org_repository.get_by_id(client_id)
        if not organization or not organization.is_client():
            return []
        return self._peer_group_service.get_peer_groups(client_id)