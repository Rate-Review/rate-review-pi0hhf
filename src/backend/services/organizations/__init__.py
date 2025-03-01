"""
Initializes the organizations service module and exposes key functionality for managing law firms, clients, user management, and peer groups.
"""

import logging  # Import logging module for creating logger
from typing import Dict, List, Optional  # Import typing for annotations
import uuid  # Import uuid for handling unique identifiers

from .firm import (  # Import law firm management functions
    create_law_firm,
    get_law_firm,
    update_law_firm,
    delete_law_firm,
    get_law_firms,
    create_office,
    get_office,
    update_office,
    delete_office,
    get_offices,
)
from .client import (  # Import client management functions
    create_client,
    get_client,
    update_client,
    delete_client,
    get_clients,
    create_department,
    get_department,
    update_department,
    delete_department,
    get_departments,
)
from .peer_groups import (  # Import peer group management functions
    create_peer_group,
    get_peer_group,
    update_peer_group,
    delete_peer_group,
    get_peer_groups,
    add_organization_to_peer_group,
    remove_organization_from_peer_group,
)
from .user_management import (  # Import user management functions
    create_user,
    get_user,
    update_user,
    delete_user,
    get_users,
    assign_user_role,
    get_user_permissions,
)

logger = logging.getLogger(__name__)  # Get logger instance for this module


def create_organization(organization_data: dict) -> dict:
    """Creates a new organization (either law firm or client) in the system"""
    org_type = organization_data.get("type")  # Determine organization type from data (law firm or client)
    if org_type == "law_firm":  # If organization type is law_firm
        org = create_law_firm(organization_data)  # Call create_law_firm
    elif org_type == "client":  # If organization type is client
        org = create_client(organization_data)  # Call create_client
    else:  # If organization type is neither law_firm nor client
        raise ValueError("Invalid organization type")  # Raise ValueError
    logger.info(f"Organization created with id {org.id}")  # Log the organization creation
    return org  # Return the created organization


def get_organization(organization_id: str) -> dict:
    """Retrieves an organization by ID"""
    org_type = get_organization(organization_id)  # Determine organization type from database
    if org_type == "law_firm":  # If organization type is law_firm
        org = get_law_firm(organization_id)  # Call get_law_firm
    elif org_type == "client":  # If organization type is client
        org = get_client(organization_id)  # Call get_client
    else:  # If organization type is neither law_firm nor client
        raise ValueError("Invalid organization type")  # Raise ValueError
    return org  # Return the organization


def update_organization(organization_id: str, organization_data: dict) -> dict:
    """Updates an organization's information"""
    org_type = get_organization(organization_id)  # Determine organization type from database
    if org_type == "law_firm":  # If organization type is law_firm
        org = update_law_firm(organization_id, organization_data)  # Call update_law_firm
    elif org_type == "client":  # If organization type is client
        org = update_client(organization_id, organization_data)  # Call update_client
    else:  # If organization type is neither law_firm nor client
        raise ValueError("Invalid organization type")  # Raise ValueError
    logger.info(f"Organization updated with id {organization_id}")  # Log the organization update
    return org  # Return the updated organization


def delete_organization(organization_id: str) -> bool:
    """Deletes an organization from the system"""
    org_type = get_organization(organization_id)  # Determine organization type from database
    if org_type == "law_firm":  # If organization type is law_firm
        deleted = delete_law_firm(organization_id)  # Call delete_law_firm
    elif org_type == "client":  # If organization type is client
        deleted = delete_client(organization_id)  # Call delete_client
    else:  # If organization type is neither law_firm nor client
        raise ValueError("Invalid organization type")  # Raise ValueError
    logger.info(f"Organization deleted with id {organization_id}")  # Log the organization deletion
    return deleted  # Return success status


def get_organizations(organization_type: str, filters: dict, page: int, page_size: int) -> list:
    """Retrieves a list of organizations with optional filtering"""
    if organization_type == "law_firm":  # If organization type is law_firm
        orgs = get_law_firms(filters, page, page_size)  # Call get_law_firms
    elif organization_type == "client":  # If organization type is client
        orgs = get_clients(filters, page, page_size)  # Call get_clients
    elif organization_type == "both":  # If organization type is both
        law_firms = get_law_firms(filters, page, page_size)  # Call get_law_firms
        clients = get_clients(filters, page, page_size)  # Call get_clients
        orgs = law_firms + clients  # Combine results
    else:  # If organization type is invalid
        raise ValueError("Invalid organization type")  # Raise ValueError
    return orgs  # Return the organization list


__all__ = [  # List of all functions to be exported
    "create_organization",
    "get_organization",
    "update_organization",
    "delete_organization",
    "get_organizations",
    "create_law_firm",
    "get_law_firm",
    "update_law_firm",
    "delete_law_firm",
    "get_law_firms",
    "create_client",
    "get_client",
    "update_client",
    "delete_client",
    "get_clients",
    "create_user",
    "get_user",
    "update_user",
    "delete_user",
    "get_users",
    "assign_user_role",
    "get_user_permissions",
    "create_peer_group",
    "get_peer_group",
    "update_peer_group",
    "delete_peer_group",
    "get_peer_groups",
    "add_organization_to_peer_group",
    "remove_organization_from_peer_group",
    "create_department",
    "get_department",
    "update_department",
    "delete_department",
    "get_departments",
    "create_office",
    "get_office",
    "update_office",
    "delete_office",
    "get_offices",
]