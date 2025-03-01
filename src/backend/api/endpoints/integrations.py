"""
API endpoints for managing external system integrations including eBilling systems, law firm billing systems, UniCourt, and file import/export functionality.
"""
# External dependencies
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status
from fastapi.responses import StreamingResponse
from typing import List, Dict, Optional, Any
import uuid
import json
import os
import shutil

# Fast API: 0.95.0
# Standard Library
# Internal imports
from src.backend.api.core.auth import get_current_user, check_permissions
from src.backend.db.repositories.organization_repository import OrganizationRepository
from src.backend.integrations.common.adapter import IntegrationAdapter
from src.backend.integrations.ebilling.teamconnect import TeamConnectClient
from src.backend.integrations.ebilling.onit import OnitClient
from src.backend.integrations.ebilling.legal_tracker import LegalTrackerClient
from src.backend.integrations.unicourt.client import UniCourtClient
from src.backend.integrations.file.excel_processor import ExcelProcessor
from src.backend.integrations.file.csv_processor import CSVProcessor
from src.backend.integrations.file.validators import FileValidator

# Define router for integration endpoints
router = APIRouter(prefix='/integrations', tags=['integrations'])

# Define temporary upload directory
TEMP_UPLOAD_DIR = os.getenv('TEMP_UPLOAD_DIR', '/tmp/justicebid/uploads')

# Define supported integration types
INTEGRATION_TYPES = {
    "ebilling_onit": {"display_name": "Onit eBilling", "description": "Integrate with Onit eBilling system"},
    "ebilling_teamconnect": {"display_name": "TeamConnect", "description": "Integrate with TeamConnect eBilling system"},
    "ebilling_legal_tracker": {"display_name": "Legal Tracker", "description": "Integrate with Legal Tracker eBilling system"},
    "unicourt": {"display_name": "UniCourt", "description": "Integrate with UniCourt for attorney data"}
}

@router.get('/types')
@check_permissions(['integrations:read'])
def get_integration_types(current_user: dict = Depends(get_current_user)):
    """
    Get a list of available integration types supported by the system
    """
    # Check user permissions
    # Return dictionary of supported integration types with metadata
    # Include information like display name, description, capabilities for each type
    # Return the dictionary as JSON response
    return INTEGRATION_TYPES

@router.get('/')
@check_permissions(['integrations:read'])
def get_integrations(current_user: dict = Depends(get_current_user),
                     org_repo: OrganizationRepository = Depends(OrganizationRepository)):
    """
    Get all integration configurations for the current user's organization
    """
    # Get organization ID from current user
    organization_id = current_user.get('organization_id')
    # Retrieve organization from repository
    organization = org_repo.get_by_id(organization_id)
    # Extract integration configurations from organization settings
    integration_configs = organization.settings.get('integrations', []) if organization and organization.settings else []
    # Mask sensitive information like passwords and API keys
    for config in integration_configs:
        if 'auth_credentials' in config:
            auth_credentials = config['auth_credentials']
            for key in auth_credentials:
                auth_credentials[key] = '******'  # Mask sensitive data
    # Return configurations as JSON response
    return integration_configs

@router.get('/{integration_id}')
@check_permissions(['integrations:read'])
def get_integration(integration_id: str,
                    current_user: dict = Depends(get_current_user),
                    org_repo: OrganizationRepository = Depends(OrganizationRepository)):
    """
    Get a specific integration configuration by ID
    """
    # Get organization ID from current user
    organization_id = current_user.get('organization_id')
    # Retrieve organization from repository
    organization = org_repo.get_by_id(organization_id)
    # Find integration configuration with matching ID
    integration_config = next((config for config in organization.settings.get('integrations', []) if config.get('id') == integration_id), None) if organization and organization.settings else None
    # If not found, raise HTTPException with 404 status
    if not integration_config:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Integration not found")
    # Mask sensitive information like passwords and API keys
    if 'auth_credentials' in integration_config:
        auth_credentials = integration_config['auth_credentials']
        for key in auth_credentials:
            auth_credentials[key] = '******'  # Mask sensitive data
    # Return configuration as JSON response
    return integration_config

@router.post('/')
@check_permissions(['integrations:create'])
def create_integration(integration_data: dict,
                       current_user: dict = Depends(get_current_user),
                       org_repo: OrganizationRepository = Depends(OrganizationRepository)):
    """
    Create a new integration configuration
    """
    # Get organization ID from current user
    organization_id = current_user.get('organization_id')
    # Retrieve organization from repository
    organization = org_repo.get_by_id(organization_id)
    # Validate integration data based on integration type
    integration_type = integration_data.get('integration_type')
    if integration_type not in INTEGRATION_TYPES:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid integration type")
    # Ensure integration type is supported
    # Generate a unique ID for the new integration configuration
    integration_id = str(uuid.uuid4())
    integration_data['id'] = integration_id
    # Set default field mappings based on integration type
    integration_data['field_mappings'] = {}  # Implement default mappings
    # Add the configuration to organization settings
    if 'integrations' not in organization.settings:
        organization.settings['integrations'] = []
    organization.settings['integrations'].append(integration_data)
    # Save organization changes
    org_repo._db.commit()
    # Return new configuration with status 201
    return integration_data

@router.put('/{integration_id}')
@check_permissions(['integrations:update'])
def update_integration(integration_id: str,
                       integration_data: dict,
                       current_user: dict = Depends(get_current_user),
                       org_repo: OrganizationRepository = Depends(OrganizationRepository)):
    """
    Update an existing integration configuration
    """
    # Get organization ID from current user
    organization_id = current_user.get('organization_id')
    # Retrieve organization from repository
    organization = org_repo.get_by_id(organization_id)
    # Find integration configuration with matching ID
    integration_config = next((config for config in organization.settings.get('integrations', []) if config.get('id') == integration_id), None) if organization and organization.settings else None
    # If not found, raise HTTPException with 404 status
    if not integration_config:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Integration not found")
    # Validate updated integration data
    # Update the configuration in organization settings
    integration_config.update(integration_data)
    # Save organization changes
    org_repo._db.commit()
    # Return updated configuration
    return integration_config

@router.delete('/{integration_id}')
@check_permissions(['integrations:delete'])
def delete_integration(integration_id: str,
                       current_user: dict = Depends(get_current_user),
                       org_repo: OrganizationRepository = Depends(OrganizationRepository)):
    """
    Delete an integration configuration
    """
    # Get organization ID from current user
    organization_id = current_user.get('organization_id')
    # Retrieve organization from repository
    organization = org_repo.get_by_id(organization_id)
    # Find integration configuration with matching ID
    integration_config = next((config for config in organization.settings.get('integrations', []) if config.get('id') == integration_id), None) if organization and organization.settings else None
    # If not found, raise HTTPException with 404 status
    if not integration_config:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Integration not found")
    # Remove the configuration from organization settings
    organization.settings['integrations'] = [config for config in organization.settings['integrations'] if config.get('id') != integration_id]
    # Save organization changes
    org_repo._db.commit()
    # Return success message with status 200
    return {"message": "Integration deleted successfully"}

@router.post('/{integration_id}/test')
@check_permissions(['integrations:read'])
def test_connection(integration_id: str,
                    current_user: dict = Depends(get_current_user),
                    org_repo: OrganizationRepository = Depends(OrganizationRepository)):
    """
    Test connection to an integration endpoint
    """
    # Get organization ID from current user
    organization_id = current_user.get('organization_id')
    # Retrieve organization from repository
    organization = org_repo.get_by_id(organization_id)
    # Find integration configuration with matching ID
    integration_config = next((config for config in organization.settings.get('integrations', []) if config.get('id') == integration_id), None) if organization and organization.settings else None
    # If not found, raise HTTPException with 404 status
    if not integration_config:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Integration not found")
    # Create appropriate client based on integration type using _get_client_for_integration
    try:
        client = _get_client_for_integration(integration_config)
        # Attempt to establish connection with provided credentials
        is_valid = client.test_connection()
        # If connection fails, catch exception and return error details
        return {"success": is_valid, "message": "Connection successful"}
    except Exception as e:
        return {"success": False, "message": str(e)}
    # Return test results including success status and connection details

@router.get('/{integration_id}/mappings')
@check_permissions(['integrations:read'])
def get_field_mappings(integration_id: str,
                       current_user: dict = Depends(get_current_user),
                       org_repo: OrganizationRepository = Depends(OrganizationRepository)):
    """
    Get field mapping configuration for an integration
    """
    # Get organization ID from current user
    organization_id = current_user.get('organization_id')
    # Retrieve organization from repository
    organization = org_repo.get_by_id(organization_id)
    # Find integration configuration with matching ID
    integration_config = next((config for config in organization.settings.get('integrations', []) if config.get('id') == integration_id), None) if organization and organization.settings else None
    # If not found, raise HTTPException with 404 status
    if not integration_config:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Integration not found")
    # Extract field mappings from integration configuration
    field_mappings = integration_config.get('field_mappings', {})
    # Return mappings as JSON response
    return field_mappings

@router.post('/{integration_id}/mappings')
@check_permissions(['integrations:update'])
def update_field_mappings(integration_id: str,
                          mapping_data: dict,
                          current_user: dict = Depends(get_current_user),
                          org_repo: OrganizationRepository = Depends(OrganizationRepository)):
    """
    Update field mapping configuration for an integration
    """
    # Get organization ID from current user
    organization_id = current_user.get('organization_id')
    # Retrieve organization from repository
    organization = org_repo.get_by_id(organization_id)
    # Find integration configuration with matching ID
    integration_config = next((config for config in organization.settings.get('integrations', []) if config.get('id') == integration_id), None) if organization and organization.settings else None
    # If not found, raise HTTPException with 404 status
    if not integration_config:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Integration not found")
    # Validate field mapping data using _validate_field_mappings
    _validate_field_mappings(mapping_data, integration_config)
    # Update mappings in integration configuration
    integration_config['field_mappings'] = mapping_data
    # Save organization changes
    org_repo._db.commit()
    # Return updated mappings as JSON response
    return integration_config['field_mappings']

@router.get('/{integration_id}/fields')
@check_permissions(['integrations:read'])
def get_integration_fields(integration_id: str,
                           current_user: dict = Depends(get_current_user),
                           org_repo: OrganizationRepository = Depends(OrganizationRepository)):
    """
    Get available fields from external system for mapping
    """
    # Get organization ID from current user
    organization_id = current_user.get('organization_id')
    # Retrieve organization from repository
    organization = org_repo.get_by_id(organization_id)
    # Find integration configuration with matching ID
    integration_config = next((config for config in organization.settings.get('integrations', []) if config.get('id') == integration_id), None) if organization and organization.settings else None
    # If not found, raise HTTPException with 404 status
    if not integration_config:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Integration not found")
    # Create appropriate client based on integration type using _get_client_for_integration
    client = _get_client_for_integration(integration_config)
    # Connect to external system and retrieve available fields metadata
    fields_metadata = client.get_fields_metadata()  # Implement get_fields_metadata
    # Return fields metadata as JSON response with name, type, and description
    return fields_metadata

@router.post('/{integration_id}/import')
@check_permissions(['integrations:import'])
def import_data(integration_id: str,
                import_config: dict,
                current_user: dict = Depends(get_current_user),
                org_repo: OrganizationRepository = Depends(OrganizationRepository)):
    """
    Import data from external system or file
    """
    # Get organization ID from current user
    organization_id = current_user.get('organization_id')
    # Retrieve organization from repository
    organization = org_repo.get_by_id(organization_id)
    # Find integration configuration with matching ID
    integration_config = next((config for config in organization.settings.get('integrations', []) if config.get('id') == integration_id), None) if organization and organization.settings else None
    # If not found, raise HTTPException with 404 status
    if not integration_config:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Integration not found")
    # Create appropriate client based on integration type using _get_client_for_integration
    client = _get_client_for_integration(integration_config)
    # Configure import parameters (date range, data types, etc.) from import_config
    # Execute import operation
    import_results = client.import_data(import_config)  # Implement import_data
    # Return import results including success count, error count, and summary statistics
    return import_results

@router.post('/{integration_id}/export')
@check_permissions(['integrations:export'])
def export_data(integration_id: str,
                export_config: dict,
                current_user: dict = Depends(get_current_user),
                org_repo: OrganizationRepository = Depends(OrganizationRepository)):
    """
    Export data to external system
    """
    # Get organization ID from current user
    organization_id = current_user.get('organization_id')
    # Retrieve organization from repository
    organization = org_repo.get_by_id(organization_id)
    # Find integration configuration with matching ID
    integration_config = next((config for config in organization.settings.get('integrations', []) if config.get('id') == integration_id), None) if organization and organization.settings else None
    # If not found, raise HTTPException with 404 status
    if not integration_config:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Integration not found")
    # Create appropriate client based on integration type using _get_client_for_integration
    client = _get_client_for_integration(integration_config)
    # Configure export parameters (data types, format, etc.) from export_config
    # Execute export operation
    export_results = client.export_data(export_config)  # Implement export_data
    # Return export results including success count, error count, and summary statistics
    return export_results

@router.post('/upload')
@check_permissions(['integrations:import'])
async def upload_file(file: UploadFile = File(...),
                      file_type: str = Form(...),
                      current_user: dict = Depends(get_current_user)):
    """
    Upload a file for data import
    """
    # Ensure upload directory exists
    if not os.path.exists(TEMP_UPLOAD_DIR):
        os.makedirs(TEMP_UPLOAD_DIR)
    # Validate file type (excel, csv) and extension using FileValidator
    file_validator = FileValidator()
    try:
        file_validator.validate_file(file.filename, file_type)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    # Generate unique file ID using uuid
    file_id = str(uuid.uuid4())
    # Create a safe file path in the temporary directory
    file_path = os.path.join(TEMP_UPLOAD_DIR, f"{file_id}_{file.filename}")
    # Save uploaded file to temporary location
    try:
        with open(file_path, "wb") as f:
            shutil.copyfileobj(file.file, f)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    finally:
        file.file.close()
    # Return file identifier and metadata for later processing
    return {"file_id": file_id, "filename": file.filename, "file_path": file_path}

@router.post('/files/{file_id}/import')
@check_permissions(['integrations:import'])
def process_file_import(file_id: str,
                        mapping_config: dict,
                        current_user: dict = Depends(get_current_user)):
    """
    Process imported file with field mappings
    """
    # Construct temporary file path using file_id
    file_path = os.path.join(TEMP_UPLOAD_DIR, f"{file_id}")  # Correct the file path construction
    # Verify file exists at the temporary location
    if not os.path.exists(file_path):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File not found")
    # If file not found, raise HTTPException with 404 status
    # Determine file type from extension and create appropriate processor using _get_file_processor
    file_extension = os.path.splitext(file_path)[1].lower()
    if file_extension == '.csv':
        file_processor = CSVProcessor()
    elif file_extension in ['.xlsx', '.xls']:
        file_processor = ExcelProcessor()
    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Unsupported file type")
    # Apply field mappings to imported data
    file_processor.set_field_mapping(mapping_config)
    # Validate data according to target schema
    # Process and transform data into appropriate format
    # Return processing results including success count, error count, and summary
    try:
        with open(file_path, 'r') as f:
            file_content = f.read()
        return file_processor.process_import(file_content, is_content=True, validation_schema={}, field_mapping=mapping_config)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.get('/files/{file_id}/preview')
@check_permissions(['integrations:import'])
def get_file_preview(file_id: str,
                     rows: int = 10,
                     current_user: dict = Depends(get_current_user)):
    """
    Get a preview of data from an uploaded file
    """
    # Construct temporary file path using file_id
    file_path = os.path.join(TEMP_UPLOAD_DIR, f"{file_id}")  # Correct the file path construction
    # Verify file exists at the temporary location
    if not os.path.exists(file_path):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File not found")
    # If file not found, raise HTTPException with 404 status
    # Determine file type from extension and create appropriate processor using _get_file_processor
    file_extension = os.path.splitext(file_path)[1].lower()
    if file_extension == '.csv':
        file_processor = CSVProcessor()
    elif file_extension in ['.xlsx', '.xls']:
        file_processor = ExcelProcessor()
    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Unsupported file type")
    # Read the specified number of rows from the file
    try:
        with open(file_path, 'r') as f:
            file_content = f.read()
        headers, data = file_processor.read_csv(file_content, is_content=True)
        preview_data = data[:rows]
        # Return column names and preview rows as structured data
        return {"columns": headers, "rows": preview_data}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    # Include file metadata in the response

@router.get('/templates/{template_type}')
@check_permissions(['integrations:read'])
def get_template(template_type: str,
                 file_format: str,
                 current_user: dict = Depends(get_current_user)):
    """
    Get import template file for a specific data type
    """
    # Validate template_type is supported (rates, attorneys, etc.)
    if template_type not in ['rates', 'attorneys', 'billing']:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Unsupported template type")
    # Validate file_format is supported (excel, csv)
    if file_format not in ['excel', 'csv']:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Unsupported file format")
    # Generate template file based on template_type
    # For Excel format, use ExcelProcessor to create template
    if file_format == 'excel':
        file_processor = ExcelProcessor()
        template_content = file_processor.create_template(import_type=template_type, file_path="template.xlsx")
        file_extension = "xlsx"
        mime_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    # For CSV format, use CSVProcessor to create template
    elif file_format == 'csv':
        file_processor = CSVProcessor()
        template_content = file_processor.create_template(import_type=template_type, required_fields=[], optional_fields=[])
        file_extension = "csv"
        mime_type = "text/csv"
    # Set appropriate content type and headers for file download
    headers = {
        "Content-Disposition": f"attachment; filename=template.{file_extension}"
    }
    # Return StreamingResponse with template file
    return StreamingResponse(
        content=iter([template_content.encode('utf-8')]),
        media_type=mime_type,
        headers=headers
    )

@router.get('/{integration_id}/operations/{operation_id}')
@check_permissions(['integrations:read'])
def get_integration_status(integration_id: str,
                           operation_id: str,
                           current_user: dict = Depends(get_current_user)):
    """
    Get status of current import/export operations
    """
    # Get organization ID from current user
    organization_id = current_user.get('organization_id')
    # Retrieve operation status from database or cache
    # If operation not found, raise HTTPException with 404 status
    # Return operation status including progress percentage, errors, and completion status
    return {"status": "pending", "progress": 50, "errors": []}

def _get_client_for_integration(integration_config: dict) -> IntegrationAdapter:
    """
    Helper function to create appropriate client for integration type
    """
    # Extract integration type from configuration
    integration_type = integration_config.get('integration_type')
    # Check if integration type is supported
    if integration_type not in INTEGRATION_TYPES:
        raise ValueError(f"Unsupported integration type: {integration_type}")
    # Create appropriate client instance based on type:
    # - 'teamconnect': Return TeamConnectClient
    if integration_type == 'ebilling_teamconnect':
        return TeamConnectClient(config=integration_config)
    # - 'onit': Return OnitClient
    elif integration_type == 'ebilling_onit':
        return OnitClient(config=integration_config)
    # - 'legal_tracker': Return LegalTrackerClient
    elif integration_type == 'ebilling_legal_tracker':
        return LegalTrackerClient(config=integration_config)
    # - 'unicourt': Return UniCourtClient
    elif integration_type == 'unicourt':
        return UniCourtClient(api_key=integration_config.get('auth_credentials', {}).get('api_key'), base_url=integration_config.get('base_url'))
    # Configure client with credentials and settings from integration config
    # If integration type not recognized, raise ValueError
    else:
        raise ValueError(f"Invalid integration type: {integration_type}")
    # Return configured client instance

def _get_file_processor(file_path: str, file_type: str = None) -> Union[ExcelProcessor, CSVProcessor]:
    """
    Helper function to create appropriate file processor
    """
    # If file_type is not provided, determine from file extension
    if not file_type:
        file_extension = os.path.splitext(file_path)[1].lower()
    # For .xlsx or .xls extensions or file_type='excel', create ExcelProcessor
        if file_extension in ['.xlsx', '.xls']:
            file_type = 'excel'
        # For .csv extension or file_type='csv', create CSVProcessor
        elif file_extension == '.csv':
            file_type = 'csv'
        else:
            raise ValueError("Could not determine file type from extension")
    # If file type cannot be determined, raise ValueError
    # Configure processor with file path
    # Return configured processor instance
    if file_type == 'excel':
        return ExcelProcessor()
    elif file_type == 'csv':
        return CSVProcessor()
    else:
        raise ValueError(f"Invalid file type: {file_type}")

def _validate_field_mappings(mapping_data: dict, integration_config: dict):
    """
    Helper function to validate field mappings
    """
    # Check if mapping_data has required structure
    if not isinstance(mapping_data, dict):
        raise ValueError("Mapping data must be a dictionary")
    # Ensure each mapping has source and target fields
    # Validate source fields exist in external system based on integration type
    # Validate target fields exist in Justice Bid system
    # Check for required mappings based on integration type
    # Normalize field names and mapping structure
    # Return validated mapping data
    return True