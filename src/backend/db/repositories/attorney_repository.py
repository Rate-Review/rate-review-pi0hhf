"""
Repository class for managing attorney data access in the Justice Bid Rate Negotiation System.
Provides CRUD operations, search capabilities, and specialized methods for attorney management.
"""

from typing import List, Dict, Any, Tuple, Optional
import uuid
from datetime import datetime

from sqlalchemy import select, and_, or_, func
from sqlalchemy.exc import SQLAlchemyError

from ..models.attorney import Attorney
from ..models.organization import Organization
from ..models.staff_class import StaffClass
from ..models.rate import Rate
from ..session import Session
from ...utils.logging import get_logger
from ...utils.validators import validate_uuid

# Initialize logger
logger = get_logger(__name__)

class AttorneyRepository:
    """Repository class for managing attorney data in the Justice Bid system"""
    
    def __init__(self, session: Session):
        """
        Initialize the AttorneyRepository with a database session
        
        Args:
            session: SQLAlchemy session for database operations
        """
        self._session = session
        self._logger = logger
    
    def get_by_id(self, attorney_id: str) -> Optional[Attorney]:
        """
        Retrieve an attorney by their ID
        
        Args:
            attorney_id: UUID of the attorney to retrieve
            
        Returns:
            Attorney instance if found, None otherwise
        """
        try:
            validate_uuid(attorney_id, "attorney_id")
            
            stmt = select(Attorney).where(Attorney.id == uuid.UUID(attorney_id))
            result = self._session.execute(stmt).scalar_one_or_none()
            
            return result
        except Exception as e:
            self._logger.error(f"Error retrieving attorney by ID {attorney_id}: {str(e)}")
            raise
    
    def get_by_name(self, name: str, organization_id: str) -> Optional[Attorney]:
        """
        Retrieve an attorney by their name within an organization
        
        Args:
            name: Name of the attorney to retrieve
            organization_id: UUID of the organization (law firm)
            
        Returns:
            Attorney instance if found, None otherwise
        """
        try:
            validate_uuid(organization_id, "organization_id")
            
            stmt = select(Attorney).where(
                and_(
                    Attorney.name == name,
                    Attorney.organization_id == uuid.UUID(organization_id)
                )
            )
            result = self._session.execute(stmt).scalar_one_or_none()
            
            return result
        except Exception as e:
            self._logger.error(f"Error retrieving attorney by name {name} in organization {organization_id}: {str(e)}")
            raise
    
    def get_by_organization(self, organization_id: str, page: Optional[int] = None, 
                           page_size: Optional[int] = None) -> Tuple[List[Attorney], int]:
        """
        Retrieve all attorneys for a specific organization with optional pagination
        
        Args:
            organization_id: UUID of the organization (law firm)
            page: Page number for pagination (1-based)
            page_size: Number of records per page
            
        Returns:
            Tuple containing list of attorneys and total count
        """
        try:
            validate_uuid(organization_id, "organization_id")
            
            # Build base query
            stmt = select(Attorney).where(Attorney.organization_id == uuid.UUID(organization_id))
            
            # Get total count
            count_stmt = select(func.count()).select_from(Attorney).where(
                Attorney.organization_id == uuid.UUID(organization_id)
            )
            total_count = self._session.execute(count_stmt).scalar()
            
            # Apply pagination if requested
            if page is not None and page_size is not None:
                offset = (page - 1) * page_size if page > 0 else 0
                stmt = stmt.offset(offset).limit(page_size)
            
            # Execute query
            result = self._session.execute(stmt).scalars().all()
            
            return result, total_count
        except Exception as e:
            self._logger.error(f"Error retrieving attorneys for organization {organization_id}: {str(e)}")
            raise
    
    def create(self, attorney_data: Dict[str, Any]) -> Attorney:
        """
        Create a new attorney record
        
        Args:
            attorney_data: Dictionary containing attorney attributes
            
        Returns:
            Newly created Attorney instance
        """
        try:
            # Validate required fields
            required_fields = ['organization_id', 'name']
            for field in required_fields:
                if field not in attorney_data:
                    raise ValueError(f"Missing required field: {field}")
            
            # Convert string IDs to UUID objects if necessary
            if isinstance(attorney_data['organization_id'], str):
                attorney_data['organization_id'] = uuid.UUID(attorney_data['organization_id'])
            
            if 'staff_class_id' in attorney_data and attorney_data['staff_class_id'] and isinstance(attorney_data['staff_class_id'], str):
                attorney_data['staff_class_id'] = uuid.UUID(attorney_data['staff_class_id'])
            
            if 'office_ids' in attorney_data and attorney_data['office_ids']:
                attorney_data['office_ids'] = [
                    uuid.UUID(office_id) if isinstance(office_id, str) else office_id
                    for office_id in attorney_data['office_ids']
                ]
            
            # Create new attorney instance
            attorney = Attorney(
                organization_id=attorney_data['organization_id'],
                name=attorney_data['name'],
                bar_date=attorney_data.get('bar_date'),
                graduation_date=attorney_data.get('graduation_date'),
                promotion_date=attorney_data.get('promotion_date'),
                office_ids=attorney_data.get('office_ids', []),
                timekeeper_ids=attorney_data.get('timekeeper_ids', {}),
                unicourt_id=attorney_data.get('unicourt_id'),
                staff_class_id=attorney_data.get('staff_class_id')
            )
            
            # Add to session and commit
            self._session.add(attorney)
            self._session.commit()
            
            self._logger.info(f"Created new attorney: {attorney.name} in organization {attorney.organization_id}")
            return attorney
        except Exception as e:
            self._session.rollback()
            self._logger.error(f"Error creating attorney: {str(e)}")
            raise
    
    def update(self, attorney_id: str, attorney_data: Dict[str, Any]) -> Attorney:
        """
        Update an existing attorney record
        
        Args:
            attorney_id: UUID of the attorney to update
            attorney_data: Dictionary containing updated attorney attributes
            
        Returns:
            Updated Attorney instance
        """
        try:
            validate_uuid(attorney_id, "attorney_id")
            
            # Get the attorney to update
            attorney = self.get_by_id(attorney_id)
            if not attorney:
                raise ValueError(f"Attorney with ID {attorney_id} not found")
            
            # Convert UUID strings to UUID objects if needed
            if 'staff_class_id' in attorney_data and attorney_data['staff_class_id'] and isinstance(attorney_data['staff_class_id'], str):
                attorney_data['staff_class_id'] = uuid.UUID(attorney_data['staff_class_id'])
            
            if 'office_ids' in attorney_data and attorney_data['office_ids']:
                attorney_data['office_ids'] = [
                    uuid.UUID(office_id) if isinstance(office_id, str) else office_id
                    for office_id in attorney_data['office_ids']
                ]
            
            # Update attributes
            for key, value in attorney_data.items():
                if hasattr(attorney, key) and key != 'id':
                    setattr(attorney, key, value)
            
            # Commit changes
            self._session.commit()
            
            self._logger.info(f"Updated attorney: {attorney.name} (ID: {attorney_id})")
            return attorney
        except Exception as e:
            self._session.rollback()
            self._logger.error(f"Error updating attorney {attorney_id}: {str(e)}")
            raise
    
    def delete(self, attorney_id: str) -> bool:
        """
        Delete an attorney record
        
        Args:
            attorney_id: UUID of the attorney to delete
            
        Returns:
            True if deletion was successful, False otherwise
        """
        try:
            validate_uuid(attorney_id, "attorney_id")
            
            # Get the attorney to delete
            attorney = self.get_by_id(attorney_id)
            if not attorney:
                self._logger.warning(f"Attempted to delete non-existent attorney: {attorney_id}")
                return False
            
            # Delete the attorney
            self._session.delete(attorney)
            self._session.commit()
            
            self._logger.info(f"Deleted attorney: {attorney.name} (ID: {attorney_id})")
            return True
        except Exception as e:
            self._session.rollback()
            self._logger.error(f"Error deleting attorney {attorney_id}: {str(e)}")
            return False
    
    def search(self, search_params: Dict[str, Any], page: Optional[int] = None, 
              page_size: Optional[int] = None) -> Tuple[List[Attorney], int]:
        """
        Search for attorneys based on various criteria
        
        Args:
            search_params: Dictionary of search parameters
            page: Page number for pagination (1-based)
            page_size: Number of records per page
            
        Returns:
            Tuple containing list of matching attorneys and total count
        """
        try:
            # Build base query
            query = select(Attorney)
            filters = []
            
            # Apply filters based on search parameters
            if 'name' in search_params and search_params['name']:
                filters.append(Attorney.name.ilike(f"%{search_params['name']}%"))
            
            if 'organization_id' in search_params and search_params['organization_id']:
                org_id = search_params['organization_id']
                if isinstance(org_id, str):
                    org_id = uuid.UUID(org_id)
                filters.append(Attorney.organization_id == org_id)
            
            if 'staff_class_id' in search_params and search_params['staff_class_id']:
                class_id = search_params['staff_class_id']
                if isinstance(class_id, str):
                    class_id = uuid.UUID(class_id)
                filters.append(Attorney.staff_class_id == class_id)
            
            if 'bar_date_after' in search_params and search_params['bar_date_after']:
                filters.append(Attorney.bar_date >= search_params['bar_date_after'])
            
            if 'bar_date_before' in search_params and search_params['bar_date_before']:
                filters.append(Attorney.bar_date <= search_params['bar_date_before'])
            
            if 'graduation_date_after' in search_params and search_params['graduation_date_after']:
                filters.append(Attorney.graduation_date >= search_params['graduation_date_after'])
            
            if 'graduation_date_before' in search_params and search_params['graduation_date_before']:
                filters.append(Attorney.graduation_date <= search_params['graduation_date_before'])
            
            if 'has_unicourt_data' in search_params:
                if search_params['has_unicourt_data']:
                    filters.append(Attorney.unicourt_id.is_not(None))
                else:
                    filters.append(Attorney.unicourt_id.is_(None))
            
            # Apply all filters to query
            if filters:
                query = query.where(and_(*filters))
            
            # Get total count
            count_query = select(func.count()).select_from(query.subquery())
            total_count = self._session.execute(count_query).scalar()
            
            # Apply pagination if requested
            if page is not None and page_size is not None:
                offset = (page - 1) * page_size if page > 0 else 0
                query = query.offset(offset).limit(page_size)
            
            # Execute query
            result = self._session.execute(query).scalars().all()
            
            return result, total_count
        except Exception as e:
            self._logger.error(f"Error searching for attorneys: {str(e)}")
            raise
    
    def get_with_rates(self, attorney_id: str, client_id: Optional[str] = None) -> Tuple[Attorney, List[Rate]]:
        """
        Retrieve an attorney with their associated rates
        
        Args:
            attorney_id: UUID of the attorney
            client_id: Optional UUID of specific client to filter rates
            
        Returns:
            Tuple containing the attorney and their rates
        """
        try:
            validate_uuid(attorney_id, "attorney_id")
            
            # Get the attorney
            attorney = self.get_by_id(attorney_id)
            if not attorney:
                raise ValueError(f"Attorney with ID {attorney_id} not found")
            
            # Query for rates
            query = select(Rate).where(Rate.attorney_id == uuid.UUID(attorney_id))
            
            # Filter by client if specified
            if client_id:
                validate_uuid(client_id, "client_id")
                query = query.where(Rate.client_id == uuid.UUID(client_id))
            
            # Execute query and return results
            rates = self._session.execute(query).scalars().all()
            
            return attorney, rates
        except Exception as e:
            self._logger.error(f"Error retrieving attorney {attorney_id} with rates: {str(e)}")
            raise
    
    def update_unicourt_data(self, attorney_id: str, unicourt_id: str, performance_data: Dict[str, Any]) -> Attorney:
        """
        Update attorney data with information from UniCourt
        
        Args:
            attorney_id: UUID of the attorney
            unicourt_id: UniCourt identifier for the attorney
            performance_data: Dictionary of performance metrics from UniCourt
            
        Returns:
            Updated Attorney instance
        """
        try:
            validate_uuid(attorney_id, "attorney_id")
            
            # Get the attorney
            attorney = self.get_by_id(attorney_id)
            if not attorney:
                raise ValueError(f"Attorney with ID {attorney_id} not found")
            
            # Update UniCourt ID
            if isinstance(unicourt_id, str) and not unicourt_id.startswith('00000000-'):
                attorney.unicourt_id = uuid.UUID(unicourt_id)
            
            # Update performance data
            attorney.update_performance_data(performance_data)
            
            # Commit changes
            self._session.commit()
            
            self._logger.info(f"Updated UniCourt data for attorney: {attorney.name} (ID: {attorney_id})")
            return attorney
        except Exception as e:
            self._session.rollback()
            self._logger.error(f"Error updating UniCourt data for attorney {attorney_id}: {str(e)}")
            raise
    
    def add_timekeeper_id(self, attorney_id: str, client_id: str, timekeeper_id: str) -> Attorney:
        """
        Add a client-specific timekeeper ID for an attorney
        
        Args:
            attorney_id: UUID of the attorney
            client_id: UUID of the client
            timekeeper_id: Timekeeper ID used by the client for this attorney
            
        Returns:
            Updated Attorney instance
        """
        try:
            validate_uuid(attorney_id, "attorney_id")
            validate_uuid(client_id, "client_id")
            
            # Get the attorney
            attorney = self.get_by_id(attorney_id)
            if not attorney:
                raise ValueError(f"Attorney with ID {attorney_id} not found")
            
            # Add timekeeper ID
            attorney.add_timekeeper_id(str(client_id), timekeeper_id)
            
            # Commit changes
            self._session.commit()
            
            self._logger.info(f"Added timekeeper ID {timekeeper_id} for attorney {attorney.name} with client {client_id}")
            return attorney
        except Exception as e:
            self._session.rollback()
            self._logger.error(f"Error adding timekeeper ID for attorney {attorney_id}: {str(e)}")
            raise
    
    def assign_staff_class(self, attorney_id: str, staff_class_id: str) -> Attorney:
        """
        Assign a staff class to an attorney
        
        Args:
            attorney_id: UUID of the attorney
            staff_class_id: UUID of the staff class
            
        Returns:
            Updated Attorney instance
        """
        try:
            validate_uuid(attorney_id, "attorney_id")
            validate_uuid(staff_class_id, "staff_class_id")
            
            # Get the attorney
            attorney = self.get_by_id(attorney_id)
            if not attorney:
                raise ValueError(f"Attorney with ID {attorney_id} not found")
            
            # Get the staff class
            stmt = select(StaffClass).where(StaffClass.id == uuid.UUID(staff_class_id))
            staff_class = self._session.execute(stmt).scalar_one_or_none()
            
            if not staff_class:
                raise ValueError(f"Staff class with ID {staff_class_id} not found")
            
            # Verify the attorney is eligible for this staff class
            if not staff_class.is_attorney_eligible(attorney):
                raise ValueError(f"Attorney {attorney.name} is not eligible for staff class {staff_class.name}")
            
            # Assign the staff class
            attorney.staff_class_id = uuid.UUID(staff_class_id)
            
            # Commit changes
            self._session.commit()
            
            self._logger.info(f"Assigned staff class {staff_class.name} to attorney {attorney.name}")
            return attorney
        except Exception as e:
            self._session.rollback()
            self._logger.error(f"Error assigning staff class to attorney {attorney_id}: {str(e)}")
            raise
    
    def find_eligible_staff_class(self, attorney_id: str, organization_id: str) -> Optional[StaffClass]:
        """
        Find an appropriate staff class for an attorney based on their experience
        
        Args:
            attorney_id: UUID of the attorney
            organization_id: UUID of the organization defining staff classes
            
        Returns:
            Eligible staff class if found, None otherwise
        """
        try:
            validate_uuid(attorney_id, "attorney_id")
            validate_uuid(organization_id, "organization_id")
            
            # Get the attorney
            attorney = self.get_by_id(attorney_id)
            if not attorney:
                raise ValueError(f"Attorney with ID {attorney_id} not found")
            
            # Query for staff classes in the organization
            stmt = select(StaffClass).where(StaffClass.organization_id == uuid.UUID(organization_id))
            staff_classes = self._session.execute(stmt).scalars().all()
            
            # Find eligible staff class
            for staff_class in staff_classes:
                if staff_class.is_attorney_eligible(attorney):
                    self._logger.info(f"Found eligible staff class {staff_class.name} for attorney {attorney.name}")
                    return staff_class
            
            self._logger.info(f"No eligible staff class found for attorney {attorney.name}")
            return None
        except Exception as e:
            self._logger.error(f"Error finding eligible staff class for attorney {attorney_id}: {str(e)}")
            raise
    
    def get_without_staff_class(self, organization_id: str) -> List[Attorney]:
        """
        Retrieve attorneys that have not been assigned to a staff class
        
        Args:
            organization_id: UUID of the organization (law firm)
            
        Returns:
            List of attorneys without staff classes
        """
        try:
            validate_uuid(organization_id, "organization_id")
            
            # Query for attorneys without staff class
            stmt = select(Attorney).where(
                and_(
                    Attorney.organization_id == uuid.UUID(organization_id),
                    Attorney.staff_class_id.is_(None)
                )
            )
            result = self._session.execute(stmt).scalars().all()
            
            return result
        except Exception as e:
            self._logger.error(f"Error retrieving attorneys without staff class in organization {organization_id}: {str(e)}")
            raise
    
    def bulk_import(self, attorneys_data: List[Dict[str, Any]], organization_id: str,
                   auto_assign_staff_class: bool = False) -> Tuple[List[Attorney], List[Dict]]:
        """
        Import multiple attorney records in a single operation
        
        Args:
            attorneys_data: List of dictionaries containing attorney data
            organization_id: UUID of the organization (law firm)
            auto_assign_staff_class: Whether to automatically find and assign staff classes
            
        Returns:
            Tuple containing successfully imported attorneys and error records
        """
        try:
            validate_uuid(organization_id, "organization_id")
            
            imported_attorneys = []
            error_records = []
            
            # Start a transaction
            try:
                # Process each attorney record
                for idx, attorney_data in enumerate(attorneys_data):
                    try:
                        # Add organization ID if not provided
                        if 'organization_id' not in attorney_data:
                            attorney_data['organization_id'] = organization_id

                        # Create the attorney
                        attorney = self.create(attorney_data)
                        
                        # Auto-assign staff class if requested
                        if auto_assign_staff_class and not attorney.staff_class_id:
                            staff_class = self.find_eligible_staff_class(str(attorney.id), organization_id)
                            if staff_class:
                                attorney = self.assign_staff_class(str(attorney.id), str(staff_class.id))
                        
                        imported_attorneys.append(attorney)
                    except Exception as e:
                        # Log the error and continue with next record
                        error_info = {
                            'index': idx,
                            'data': attorney_data,
                            'error': str(e)
                        }
                        error_records.append(error_info)
                        self._logger.warning(f"Error importing attorney record {idx}: {str(e)}")
                
                # Commit the transaction if any attorneys were successfully imported
                if imported_attorneys:
                    self._session.commit()
                    self._logger.info(f"Successfully imported {len(imported_attorneys)} attorneys")
                
                return imported_attorneys, error_records
            except Exception as e:
                # Roll back the transaction on any error
                self._session.rollback()
                self._logger.error(f"Error during bulk import: {str(e)}")
                raise
        except Exception as e:
            self._logger.error(f"Failed to perform bulk import: {str(e)}")
            raise