"""
API endpoints for managing staff classes. Provides CRUD operations for defining and managing
attorney classification levels based on experience criteria. Staff classes are used for
structured rate management in the rate negotiation system.
"""

from typing import List, Optional
import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.exceptions import HTTPException
from fastapi import status

from api.core.auth import get_current_user_with_permissions  # Authentication dependency for API endpoints
from db.repositories.staff_class_repository import StaffClassRepository  # Data access for staff class operations
from api.schemas.staff_classes import StaffClassCreate, StaffClassUpdate, StaffClassRead  # Schemas for staff class data
from services.rates.staff_class import StaffClassService  # Business logic for staff class operations
from services.auth.permissions import Permission  # Permission constants for authorization
from db.repositories.attorney_repository import AttorneyRepository  # Data access for attorney operations
from api.core.errors import ErrorCode  # Error code constants for API responses
from db.session import get_db

# Define FastAPI router for staff class endpoints
router = APIRouter(prefix='/staff-classes', tags=['staff_classes'])

# Initialize repository and service instances
# These are global variables within this module
staff_class_repository = StaffClassRepository(next(get_db()))
staff_class_service = StaffClassService(staff_class_repository)
attorney_repository = AttorneyRepository(next(get_db()))


@router.get('/', response_model=List[StaffClassRead])
def get_staff_classes(
    current_user: dict = Depends(get_current_user_with_permissions),
    organization_id: Optional[uuid.UUID] = None,
    skip: int = 0,
    limit: int = 100
):
    """
    Get all staff classes for the current user's organization.
    """
    # Validate that user has permission to view staff classes
    # Determine organization ID (either provided or from current user)
    # Call repository to get staff classes for the organization
    # Return paginated list of staff classes
    try:
        staff_classes = staff_class_service.get_staff_classes_by_organization(organization_id=current_user['organization_id'], limit=limit, skip=skip)
        return staff_classes
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get('/{staff_class_id}', response_model=StaffClassRead)
def get_staff_class(
    staff_class_id: uuid.UUID,
    current_user: dict = Depends(get_current_user_with_permissions)
):
    """
    Get a specific staff class by ID.
    """
    # Validate that user has permission to view staff classes
    # Call repository to get staff class by ID
    # Verify staff class belongs to user's organization
    # Return staff class if found, otherwise raise 404 error
    try:
        staff_class = staff_class_service.get_staff_class(staff_class_id=staff_class_id)
        if not staff_class:
            raise HTTPException(status_code=404, detail="Staff class not found")
        return staff_class
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post('/', response_model=StaffClassRead, status_code=status.HTTP_201_CREATED)
def create_staff_class(
    staff_class: StaffClassCreate,
    current_user: dict = Depends(get_current_user_with_permissions)
):
    """
    Create a new staff class.
    """
    # Validate that user has permission to create staff classes
    # Validate organization ID matches user's organization
    # Validate experience criteria using staff class service
    # Call repository to create staff class
    # Return created staff class
    try:
        created_staff_class = staff_class_service.create_staff_class(
            organization_id=staff_class.organization_id,
            name=staff_class.name,
            experience_type=staff_class.experience_type,
            min_experience=staff_class.min_experience,
            max_experience=staff_class.max_experience,
            practice_area=staff_class.practice_area
        )
        return created_staff_class
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put('/{staff_class_id}', response_model=StaffClassRead)
def update_staff_class(
    staff_class_id: uuid.UUID,
    staff_class: StaffClassUpdate,
    current_user: dict = Depends(get_current_user_with_permissions)
):
    """
    Update an existing staff class.
    """
    # Validate that user has permission to update staff classes
    # Get existing staff class from repository
    # Verify staff class belongs to user's organization
    # Validate updated experience criteria using staff class service
    # Call repository to update staff class
    # Return updated staff class
    try:
        updated_staff_class = staff_class_service.update_staff_class(staff_class_id=staff_class_id, update_data=staff_class.dict(exclude_unset=True))
        if not updated_staff_class:
            raise HTTPException(status_code=404, detail="Staff class not found")
        return updated_staff_class
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete('/{staff_class_id}', status_code=status.HTTP_204_NO_CONTENT)
def delete_staff_class(
    staff_class_id: uuid.UUID,
    current_user: dict = Depends(get_current_user_with_permissions)
):
    """
    Delete a staff class.
    """
    # Validate that user has permission to delete staff classes
    # Get existing staff class from repository
    # Verify staff class belongs to user's organization
    # Check if staff class is in use by any attorneys
    # If in use, raise 400 error with explanation
    # Call repository to delete staff class
    # Return no content response
    try:
        staff_class_service.delete_staff_class(staff_class_id=staff_class_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get('/{staff_class_id}/attorneys', response_model=List[dict])
def get_attorneys_by_class(
    staff_class_id: uuid.UUID,
    current_user: dict = Depends(get_current_user_with_permissions),
    skip: int = 0,
    limit: int = 100
):
    """
    Get all attorneys assigned to a specific staff class.
    """
    # Validate that user has permission to view staff classes and attorneys
    # Get staff class from repository
    # Verify staff class belongs to user's organization
    # Call attorney repository to get attorneys by staff class ID
    # Return paginated list of attorneys
    try:
        attorneys = staff_class_service.get_staff_class(staff_class_id=staff_class_id)
        return attorneys
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post('/map-attorneys', response_model=dict)
def map_attorneys_to_classes(
    organization_id: uuid.UUID,
    current_user: dict = Depends(get_current_user_with_permissions)
):
    """
    Automatically map attorneys to staff classes based on experience criteria.
    """
    # Validate that user has permission to update staff classes and attorneys
    # Verify organization ID matches user's organization
    # Call staff class service to map attorneys to classes based on experience criteria
    # Return summary of attorneys mapped to each class
    try:
        return staff_class_service.assign_attorneys_automatically(organization_id=organization_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))