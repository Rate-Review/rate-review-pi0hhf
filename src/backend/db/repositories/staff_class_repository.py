"""
Repository class for managing staff classes in the Justice Bid Rate Negotiation System.
Provides data access methods for creating, retrieving, updating, and deleting staff class records,
as well as specialized operations for attorney assignments and staff class analysis.
"""

from typing import List, Optional, Tuple, Dict, Any
import uuid
from datetime import datetime

from sqlalchemy import select, func, and_, or_
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from ..models.staff_class import StaffClass, ExperienceType
from ..models.attorney import Attorney
from ...utils.logging import get_logger
from ...utils.validators import validate_uuid, validate_required
from ...utils.datetime_utils import calculate_years_since_date

# Set up logger
logger = get_logger(__name__, 'repository')

class StaffClassRepository:
    """
    Repository class for managing staff class records in the database,
    providing a data access layer for the staff class service.
    """
    
    def __init__(self, db_session: Session):
        """
        Initialize the StaffClassRepository with a database session.
        
        Args:
            db_session: SQLAlchemy database session
        """
        self._db = db_session
        logger.debug("StaffClassRepository initialized")
    
    def get_by_id(self, staff_class_id: uuid.UUID) -> Optional[StaffClass]:
        """
        Retrieve a staff class by its ID.
        
        Args:
            staff_class_id: UUID of the staff class to retrieve
            
        Returns:
            StaffClass if found, None otherwise
        """
        try:
            validate_uuid(staff_class_id, "staff_class_id")
            stmt = select(StaffClass).where(StaffClass.id == staff_class_id)
            result = self._db.execute(stmt).scalars().first()
            return result
        except Exception as e:
            logger.error(f"Error retrieving staff class by ID: {e}")
            raise
    
    def get_by_organization(self, organization_id: uuid.UUID, 
                           active_only: bool = True, 
                           limit: Optional[int] = None, 
                           offset: Optional[int] = None) -> List[StaffClass]:
        """
        Retrieve all staff classes for an organization with optional filtering.
        
        Args:
            organization_id: UUID of the organization
            active_only: Whether to return only active staff classes
            limit: Maximum number of records to return
            offset: Number of records to skip
            
        Returns:
            List of staff classes for the organization
        """
        try:
            validate_uuid(organization_id, "organization_id")
            
            # Build query for staff classes with the given organization_id
            stmt = select(StaffClass).where(StaffClass.organization_id == organization_id)
            
            # If active_only is True, filter for is_active = True
            if active_only:
                stmt = stmt.where(StaffClass.is_active == True)
                
            # Apply limit and offset for pagination
            if limit is not None:
                stmt = stmt.limit(limit)
            if offset is not None:
                stmt = stmt.offset(offset)
                
            # Execute query and return the results
            result = self._db.execute(stmt).scalars().all()
            return list(result)
        except Exception as e:
            logger.error(f"Error retrieving staff classes by organization: {e}")
            raise
    
    def create(self, organization_id: uuid.UUID, name: str, 
              experience_type: ExperienceType, min_experience: int, 
              max_experience: Optional[int] = None, 
              practice_area: Optional[str] = None) -> StaffClass:
        """
        Create a new staff class.
        
        Args:
            organization_id: UUID of the organization
            name: Name of the staff class
            experience_type: Type of experience metric
            min_experience: Minimum experience value
            max_experience: Maximum experience value (optional)
            practice_area: Practice area the staff class applies to (optional)
            
        Returns:
            Created staff class
        """
        try:
            # Validate required parameters
            validate_uuid(organization_id, "organization_id")
            validate_required(name, "name")
            validate_required(experience_type, "experience_type")
            validate_required(min_experience, "min_experience")
            
            # Create a new StaffClass instance
            staff_class = StaffClass(
                organization_id=organization_id,
                name=name,
                experience_type=experience_type,
                min_experience=min_experience,
                max_experience=max_experience,
                practice_area=practice_area
            )
            
            # Add to database and commit
            self._db.add(staff_class)
            self._db.commit()
            
            logger.info(f"Created new staff class: {name} for organization {organization_id}")
            return staff_class
        except Exception as e:
            self._db.rollback()
            logger.error(f"Error creating staff class: {e}")
            raise
    
    def update(self, staff_class_id: uuid.UUID, update_data: dict) -> Optional[StaffClass]:
        """
        Update an existing staff class.
        
        Args:
            staff_class_id: UUID of the staff class to update
            update_data: Dictionary of fields to update
            
        Returns:
            Updated staff class if successful, None if not found
        """
        try:
            validate_uuid(staff_class_id, "staff_class_id")
            
            # Get staff class by ID
            stmt = select(StaffClass).where(StaffClass.id == staff_class_id)
            staff_class = self._db.execute(stmt).scalars().first()
            
            if not staff_class:
                logger.warning(f"Staff class with ID {staff_class_id} not found for update")
                return None
            
            # Update allowed fields
            allowed_fields = [
                'name', 'experience_type', 'min_experience', 
                'max_experience', 'practice_area', 'is_active'
            ]
            
            for field in allowed_fields:
                if field in update_data:
                    setattr(staff_class, field, update_data[field])
            
            # Commit changes
            self._db.commit()
            
            logger.info(f"Updated staff class: {staff_class_id}")
            return staff_class
        except Exception as e:
            self._db.rollback()
            logger.error(f"Error updating staff class: {e}")
            raise
    
    def delete(self, staff_class_id: uuid.UUID) -> bool:
        """
        Delete a staff class (soft delete by deactivating).
        
        Args:
            staff_class_id: UUID of the staff class to delete
            
        Returns:
            True if successful, False if staff class not found
        """
        try:
            validate_uuid(staff_class_id, "staff_class_id")
            
            # Get staff class by ID
            stmt = select(StaffClass).where(StaffClass.id == staff_class_id)
            staff_class = self._db.execute(stmt).scalars().first()
            
            if not staff_class:
                logger.warning(f"Staff class with ID {staff_class_id} not found for deletion")
                return False
            
            # Set is_active to False (soft delete)
            staff_class.is_active = False
            self._db.commit()
            
            logger.info(f"Soft deleted (deactivated) staff class: {staff_class_id}")
            return True
        except Exception as e:
            self._db.rollback()
            logger.error(f"Error deleting staff class: {e}")
            raise
    
    def search(self, organization_id: Optional[uuid.UUID] = None, 
              name: Optional[str] = None, 
              experience_type: Optional[ExperienceType] = None,
              practice_area: Optional[str] = None,
              active_only: bool = True,
              limit: int = 20,
              offset: int = 0) -> Tuple[List[StaffClass], int]:
        """
        Search for staff classes with filtering criteria.
        
        Args:
            organization_id: Optional organization UUID to filter by
            name: Optional name to filter by (case-insensitive partial match)
            experience_type: Optional experience type to filter by
            practice_area: Optional practice area to filter by
            active_only: Whether to return only active staff classes
            limit: Maximum number of records to return
            offset: Number of records to skip
            
        Returns:
            Tuple containing list of staff classes and total count
        """
        try:
            # Build base query
            query = select(StaffClass)
            
            # Apply filters
            filters = []
            
            if organization_id:
                validate_uuid(organization_id, "organization_id")
                filters.append(StaffClass.organization_id == organization_id)
                
            if name:
                filters.append(StaffClass.name.ilike(f"%{name}%"))
                
            if experience_type:
                filters.append(StaffClass.experience_type == experience_type)
                
            if practice_area:
                filters.append(StaffClass.practice_area.ilike(f"%{practice_area}%"))
                
            if active_only:
                filters.append(StaffClass.is_active == True)
                
            # Apply all filters to the query
            if filters:
                query = query.where(and_(*filters))
                
            # Get total count
            count_query = select(func.count()).select_from(query.subquery())
            total_count = self._db.scalar(count_query)
            
            # Apply pagination
            query = query.limit(limit).offset(offset)
            
            # Execute query
            result = self._db.execute(query).scalars().all()
            
            return list(result), total_count
        except Exception as e:
            logger.error(f"Error searching staff classes: {e}")
            raise
    
    def count(self, organization_id: Optional[uuid.UUID] = None, 
             active_only: bool = True) -> int:
        """
        Count staff classes with optional filtering.
        
        Args:
            organization_id: Optional organization UUID to filter by
            active_only: Whether to count only active staff classes
            
        Returns:
            Number of staff classes matching criteria
        """
        try:
            # Build count query
            query = select(func.count()).select_from(StaffClass)
            
            # Apply filters
            if organization_id:
                validate_uuid(organization_id, "organization_id")
                query = query.where(StaffClass.organization_id == organization_id)
                
            if active_only:
                query = query.where(StaffClass.is_active == True)
                
            # Execute query and return result
            result = self._db.scalar(query)
            return result or 0
        except Exception as e:
            logger.error(f"Error counting staff classes: {e}")
            raise
    
    def get_eligible_attorneys(self, staff_class_id: uuid.UUID) -> List[Attorney]:
        """
        Get all attorneys eligible for a staff class based on experience criteria.
        
        Args:
            staff_class_id: UUID of the staff class
            
        Returns:
            List of eligible attorneys
        """
        try:
            validate_uuid(staff_class_id, "staff_class_id")
            
            # Get staff class by ID
            stmt = select(StaffClass).where(StaffClass.id == staff_class_id)
            staff_class = self._db.execute(stmt).scalars().first()
            
            if not staff_class:
                logger.warning(f"Staff class with ID {staff_class_id} not found")
                return []
            
            # Get all attorneys from the same organization
            org_id = staff_class.organization_id
            stmt = select(Attorney).where(Attorney.organization_id == org_id)
            attorneys = self._db.execute(stmt).scalars().all()
            
            # Filter attorneys based on eligibility
            eligible_attorneys = [
                attorney for attorney in attorneys 
                if staff_class.is_attorney_eligible(attorney)
            ]
            
            return eligible_attorneys
        except Exception as e:
            logger.error(f"Error getting eligible attorneys for staff class: {e}")
            raise
    
    def assign_attorney(self, staff_class_id: uuid.UUID, attorney_id: uuid.UUID) -> bool:
        """
        Assign an attorney to a staff class.
        
        Args:
            staff_class_id: UUID of the staff class
            attorney_id: UUID of the attorney
            
        Returns:
            True if successful, False if staff class or attorney not found or not eligible
        """
        try:
            validate_uuid(staff_class_id, "staff_class_id")
            validate_uuid(attorney_id, "attorney_id")
            
            # Get staff class
            staff_class_stmt = select(StaffClass).where(StaffClass.id == staff_class_id)
            staff_class = self._db.execute(staff_class_stmt).scalars().first()
            
            if not staff_class:
                logger.warning(f"Staff class with ID {staff_class_id} not found")
                return False
            
            # Get attorney
            attorney_stmt = select(Attorney).where(Attorney.id == attorney_id)
            attorney = self._db.execute(attorney_stmt).scalars().first()
            
            if not attorney:
                logger.warning(f"Attorney with ID {attorney_id} not found")
                return False
            
            # Verify staff class and attorney belong to same organization
            if attorney.organization_id != staff_class.organization_id:
                logger.warning(f"Attorney {attorney_id} and staff class {staff_class_id} belong to different organizations")
                return False
            
            # Verify attorney is eligible for the staff class
            if not staff_class.is_attorney_eligible(attorney):
                logger.warning(f"Attorney {attorney_id} is not eligible for staff class {staff_class_id}")
                return False
            
            # Update attorney's staff_class_id
            attorney.staff_class_id = staff_class_id
            self._db.commit()
            
            logger.info(f"Assigned attorney {attorney_id} to staff class {staff_class_id}")
            return True
        except Exception as e:
            self._db.rollback()
            logger.error(f"Error assigning attorney to staff class: {e}")
            raise
    
    def get_attorneys_by_staff_class(self, staff_class_id: uuid.UUID) -> List[Attorney]:
        """
        Get all attorneys assigned to a staff class.
        
        Args:
            staff_class_id: UUID of the staff class
            
        Returns:
            List of attorneys assigned to the staff class
        """
        try:
            validate_uuid(staff_class_id, "staff_class_id")
            
            # Query for attorneys where staff_class_id matches
            stmt = select(Attorney).where(Attorney.staff_class_id == staff_class_id)
            attorneys = self._db.execute(stmt).scalars().all()
            
            return list(attorneys)
        except Exception as e:
            logger.error(f"Error getting attorneys by staff class: {e}")
            raise
    
    def get_attorneys_without_staff_class(self, organization_id: uuid.UUID) -> List[Attorney]:
        """
        Get all attorneys in an organization that are not assigned to any staff class.
        
        Args:
            organization_id: UUID of the organization
            
        Returns:
            List of attorneys without staff class assignment
        """
        try:
            validate_uuid(organization_id, "organization_id")
            
            # Query for attorneys in organization with null staff_class_id
            stmt = select(Attorney).where(
                Attorney.organization_id == organization_id,
                Attorney.staff_class_id == None  # noqa: E711
            )
            attorneys = self._db.execute(stmt).scalars().all()
            
            return list(attorneys)
        except Exception as e:
            logger.error(f"Error getting attorneys without staff class: {e}")
            raise
    
    def calculate_experience(self, attorney: Attorney, experience_type: ExperienceType) -> int:
        """
        Calculate experience value for an attorney based on staff class experience type.
        
        Args:
            attorney: Attorney object
            experience_type: Type of experience to calculate
            
        Returns:
            Experience value in years
        """
        try:
            today = datetime.now().date()
            
            if experience_type == ExperienceType.GRADUATION_YEAR:
                if attorney.graduation_date:
                    return (today.year - attorney.graduation_date.year)
            elif experience_type == ExperienceType.BAR_YEAR:
                if attorney.bar_date:
                    return (today.year - attorney.bar_date.year)
            elif experience_type == ExperienceType.YEARS_IN_ROLE:
                if attorney.promotion_date:
                    return (today.year - attorney.promotion_date.year)
            
            # Return 0 if the relevant date is None
            logger.warning(f"Could not calculate experience for attorney {attorney.id} with experience type {experience_type}")
            return 0
        except Exception as e:
            logger.error(f"Error calculating attorney experience: {e}")
            raise
    
    def get_overlapping_classes(self, organization_id: uuid.UUID, experience_type: ExperienceType) -> List[Tuple[StaffClass, StaffClass]]:
        """
        Find staff classes with overlapping experience ranges.
        
        Args:
            organization_id: UUID of the organization
            experience_type: Type of experience to check for overlaps
            
        Returns:
            List of overlapping staff class pairs
        """
        try:
            validate_uuid(organization_id, "organization_id")
            
            # Get all staff classes for the organization with the given experience type
            stmt = select(StaffClass).where(
                StaffClass.organization_id == organization_id,
                StaffClass.experience_type == experience_type,
                StaffClass.is_active == True
            )
            staff_classes = self._db.execute(stmt).scalars().all()
            
            # Find overlapping pairs
            overlapping_pairs = []
            
            for i, class1 in enumerate(staff_classes):
                for class2 in staff_classes[i+1:]:
                    # Check for overlap
                    # Two classes overlap if: (A.min_experience <= B.max_experience AND A.max_experience >= B.min_experience)
                    if (class1.min_experience <= (class2.max_experience or float('inf')) and 
                        (class1.max_experience or float('inf')) >= class2.min_experience):
                        overlapping_pairs.append((class1, class2))
            
            return overlapping_pairs
        except Exception as e:
            logger.error(f"Error finding overlapping staff classes: {e}")
            raise
    
    def find_experience_gaps(self, organization_id: uuid.UUID, experience_type: ExperienceType) -> List[Dict[str, int]]:
        """
        Find gaps in experience coverage between staff classes.
        
        Args:
            organization_id: UUID of the organization
            experience_type: Type of experience to check for gaps
            
        Returns:
            List of experience gaps with min and max values
        """
        try:
            validate_uuid(organization_id, "organization_id")
            
            # Get all staff classes for the organization with the given experience type
            stmt = select(StaffClass).where(
                StaffClass.organization_id == organization_id,
                StaffClass.experience_type == experience_type,
                StaffClass.is_active == True
            )
            staff_classes = self._db.execute(stmt).scalars().all()
            
            # Sort classes by min_experience
            sorted_classes = sorted(staff_classes, key=lambda x: x.min_experience)
            
            gaps = []
            
            # Check for gaps between adjacent classes
            for i in range(len(sorted_classes) - 1):
                current_class = sorted_classes[i]
                next_class = sorted_classes[i + 1]
                
                # If current class has no max, there can't be a gap
                if current_class.max_experience is None:
                    continue
                    
                # A gap exists if: class2.min_experience > class1.max_experience + 1
                if next_class.min_experience > current_class.max_experience + 1:
                    gaps.append({
                        'min': current_class.max_experience + 1,
                        'max': next_class.min_experience - 1
                    })
            
            return gaps
        except Exception as e:
            logger.error(f"Error finding experience gaps in staff classes: {e}")
            raise
    
    def clone_staff_class(self, staff_class_id: uuid.UUID, target_organization_id: uuid.UUID) -> StaffClass:
        """
        Clone a staff class to a new organization.
        
        Args:
            staff_class_id: UUID of the staff class to clone
            target_organization_id: UUID of the target organization
            
        Returns:
            Newly created staff class clone
        """
        try:
            validate_uuid(staff_class_id, "staff_class_id")
            validate_uuid(target_organization_id, "target_organization_id")
            
            # Get source staff class
            stmt = select(StaffClass).where(StaffClass.id == staff_class_id)
            source_class = self._db.execute(stmt).scalars().first()
            
            if not source_class:
                logger.warning(f"Staff class with ID {staff_class_id} not found for cloning")
                raise ValueError(f"Staff class with ID {staff_class_id} not found")
            
            # Create new staff class with the same properties but for the target organization
            clone = StaffClass(
                organization_id=target_organization_id,
                name=source_class.name,
                experience_type=source_class.experience_type,
                min_experience=source_class.min_experience,
                max_experience=source_class.max_experience,
                practice_area=source_class.practice_area
            )
            
            # Add to database and commit
            self._db.add(clone)
            self._db.commit()
            
            logger.info(f"Cloned staff class {staff_class_id} to organization {target_organization_id}")
            return clone
        except Exception as e:
            self._db.rollback()
            logger.error(f"Error cloning staff class: {e}")
            raise