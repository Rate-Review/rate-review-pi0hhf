from fastapi import APIRouter, Depends, HTTPException, status
from uuid import UUID
from sqlalchemy.orm import Session
from typing import Dict, List, Optional, Any

from app.core.auth import get_current_user, check_permissions
from app.db.repositories import UserRepository
from app.schemas.user import UserCreate, UserUpdate, UserResponse, UserListResponse
from app.db.session import get_db
from app.models.user import User

# Create router for user endpoints
router = APIRouter(prefix='/users', tags=['users'])


@router.get('/', response_model=UserListResponse)
async def get_users(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    filters: Dict[str, Any] = {},
    current_user: User = Depends(get_current_user)
):
    """
    Get a list of users with optional filtering and pagination.
    
    Only users with appropriate permissions can access this endpoint.
    Administrators can see all users in their organization.
    """
    # Check if user has permission to list users
    check_permissions(current_user, "list_users")
    
    # Initialize the user repository
    user_repo = UserRepository(db)
    
    # Apply organization filter for non-system admins
    if not current_user.is_system_admin:
        filters["organization_id"] = current_user.organization_id
    
    # Get users from repository with pagination
    users, total = user_repo.get_users(
        skip=skip,
        limit=limit,
        filters=filters
    )
    
    # Return list of users with pagination info
    return UserListResponse(
        items=users,
        total=total,
        skip=skip,
        limit=limit
    )


@router.get('/{user_id}', response_model=UserResponse)
async def get_user(
    user_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get a specific user by ID.
    
    Users can only view others in their organization unless they are system admins.
    """
    # Initialize the user repository
    user_repo = UserRepository(db)
    
    # Get the user from repository
    user = user_repo.get_user(user_id)
    
    # If user not found, raise 404
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Check if user has permission to view the requested user
    if not current_user.is_system_admin and user.organization_id != current_user.organization_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this user"
        )
    
    return user


@router.post('/', response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_data: UserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create a new user.
    
    Organization admins can only create users in their organization.
    System admins can create users in any organization.
    """
    # Check if user has permission to create users
    check_permissions(current_user, "create_users")
    
    # Initialize the user repository
    user_repo = UserRepository(db)
    
    # Check organization access for non-system admins
    if not current_user.is_system_admin and user_data.organization_id != current_user.organization_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to create users for this organization"
        )
    
    try:
        # Create the user through repository
        user = user_repo.create_user(user_data)
        return user
    except ValueError as e:
        # Handle validation errors (e.g., email exists)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.put('/{user_id}', response_model=UserResponse)
async def update_user(
    user_id: UUID,
    user_data: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update an existing user.
    
    Organization admins can only update users in their organization.
    System admins can update users in any organization.
    """
    # Initialize the user repository
    user_repo = UserRepository(db)
    
    # Get the user to be updated
    user = user_repo.get_user(user_id)
    
    # If user not found, raise 404
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Check if user has permission to update the specified user
    if not current_user.is_system_admin and user.organization_id != current_user.organization_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this user"
        )
    
    check_permissions(current_user, "update_users")
    
    try:
        # Update the user through repository
        updated_user = user_repo.update_user(user_id, user_data)
        return updated_user
    except ValueError as e:
        # Handle validation errors
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.delete('/{user_id}', status_code=status.HTTP_200_OK)
async def delete_user(
    user_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Delete a user.
    
    Organization admins can only delete users in their organization.
    System admins can delete users in any organization.
    """
    # Check if user has permission to delete users
    check_permissions(current_user, "delete_users")
    
    # Initialize the user repository
    user_repo = UserRepository(db)
    
    # Get the user to be deleted
    user = user_repo.get_user(user_id)
    
    # If user not found, raise 404
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Check organization access for non-system admins
    if not current_user.is_system_admin and user.organization_id != current_user.organization_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this user"
        )
    
    # Prevent users from deleting themselves
    if user_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete your own user account"
        )
    
    # Delete the user through repository
    user_repo.delete_user(user_id)
    
    return {"message": "User successfully deleted"}


@router.get('/me', response_model=UserResponse)
async def get_current_user_details(
    current_user: User = Depends(get_current_user)
):
    """
    Get the current authenticated user's details.
    """
    return current_user


@router.put('/me', response_model=UserResponse)
async def update_current_user(
    user_data: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update the current authenticated user.
    
    Users can update their own details without special permissions.
    Cannot change organization or role through this endpoint.
    """
    # Initialize the user repository
    user_repo = UserRepository(db)
    
    # Prevent changing critical fields for self-update
    if hasattr(user_data, "role") and user_data.role is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot change your own role"
        )
    
    if hasattr(user_data, "organization_id") and user_data.organization_id is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Cannot change your own organization"
        )
    
    try:
        # Update the current user through repository
        updated_user = user_repo.update_user(current_user.id, user_data)
        return updated_user
    except ValueError as e:
        # Handle validation errors
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )