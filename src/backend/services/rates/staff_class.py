"""
Service module for managing staff classes in the Justice Bid Rate Negotiation System.
Provides business logic for creating, updating, and assigning attorneys to staff classes
based on experience criteria, as well as analyzing staff class structures for overlaps and gaps.
"""

from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime

from ...db.repositories.staff_class_repository import StaffClassRepository
from ...utils.constants import ExperienceType
from ...utils.logging import get_logger
from ...utils.validators import validate_uuid, validate_required, validate_string, validate_integer, validate_enum_value
from ...utils.datetime_utils import calculate_years_since_date

# Initialize logger
logger = get_logger(__name__, 'service')

class StaffClassService:
    """
    Service class implementing business logic for staff class management, including creation, 
    updates, analysis, and attorney assignment.
    """
    
    def __init__(self, repository: StaffClassRepository):
        """
        Initialize the StaffClassService with a repository.
        
        Args:
            repository: Repository for data access operations
        """
        self._repository = repository
        logger.info("StaffClassService initialized")
    
    def get_staff_class(self, staff_class_id: uuid.UUID) -> Optional[dict]:
        """
        Retrieve a staff class by its ID.
        
        Args:
            staff_class_id: UUID of the staff class to retrieve
            
        Returns:
            Staff class data dictionary if found, None otherwise
        """
        try:
            validate_uuid(staff_class_id, "staff_class_id")
            
            staff_class = self._repository.get_by_id(staff_class_id)
            if not staff_class:
                logger.warning(f"Staff class with ID {staff_class_id} not found")
                return None
            
            return staff_class.to_dict() if hasattr(staff_class, 'to_dict') else vars(staff_class)
        except Exception as e:
            logger.error(f"Error retrieving staff class: {e}")
            raise
    
    def get_staff_classes_by_organization(
        self, 
        organization_id: uuid.UUID, 
        active_only: bool = True, 
        limit: Optional[int] = None, 
        offset: Optional[int] = None
    ) -> List[dict]:
        """
        Retrieve all staff classes for an organization with optional filtering.
        
        Args:
            organization_id: UUID of the organization
            active_only: Whether to return only active staff classes
            limit: Maximum number of records to return
            offset: Number of records to skip
            
        Returns:
            List of staff class dictionaries
        """
        try:
            validate_uuid(organization_id, "organization_id")
            
            staff_classes = self._repository.get_by_organization(
                organization_id=organization_id,
                active_only=active_only,
                limit=limit,
                offset=offset
            )
            
            # Convert staff classes to dictionaries
            result = []
            for staff_class in staff_classes:
                if hasattr(staff_class, 'to_dict'):
                    result.append(staff_class.to_dict())
                else:
                    result.append(vars(staff_class))
            
            return result
        except Exception as e:
            logger.error(f"Error retrieving staff classes by organization: {e}")
            raise
    
    def create_staff_class(
        self, 
        organization_id: uuid.UUID, 
        name: str, 
        experience_type: ExperienceType, 
        min_experience: int, 
        max_experience: Optional[int] = None,
        practice_area: Optional[str] = None
    ) -> dict:
        """
        Create a new staff class.
        
        Args:
            organization_id: UUID of the organization
            name: Name of the staff class
            experience_type: Type of experience metric (GRADUATION_YEAR, BAR_YEAR, YEARS_IN_ROLE)
            min_experience: Minimum experience value
            max_experience: Maximum experience value (optional)
            practice_area: Practice area the staff class applies to (optional)
            
        Returns:
            Created staff class as a dictionary
            
        Raises:
            ValueError: If validation fails or a class with the same name already exists
        """
        try:
            # Validate required fields
            validate_uuid(organization_id, "organization_id")
            validate_required(name, "name")
            validate_string(name, "name", min_length=1, max_length=255)
            validate_enum_value(experience_type, ExperienceType, "experience_type")
            validate_integer(min_experience, "min_experience", min_value=0)
            
            # Validate max_experience if provided
            if max_experience is not None:
                validate_integer(max_experience, "max_experience", min_value=min_experience)
            
            # Check for existing staff class with the same name in the organization
            existing_classes = self._repository.get_by_organization(organization_id)
            for cls in existing_classes:
                if cls.name.lower() == name.lower() and cls.is_active:
                    raise ValueError(f"A staff class with name '{name}' already exists for this organization")
            
            # Create the staff class
            staff_class = self._repository.create(
                organization_id=organization_id,
                name=name,
                experience_type=experience_type,
                min_experience=min_experience,
                max_experience=max_experience,
                practice_area=practice_area
            )
            
            logger.info(f"Created staff class '{name}' for organization {organization_id}")
            
            return staff_class.to_dict() if hasattr(staff_class, 'to_dict') else vars(staff_class)
        except Exception as e:
            logger.error(f"Error creating staff class: {e}")
            raise
    
    def update_staff_class(self, staff_class_id: uuid.UUID, update_data: dict) -> Optional[dict]:
        """
        Update an existing staff class.
        
        Args:
            staff_class_id: UUID of the staff class to update
            update_data: Dictionary of fields to update
            
        Returns:
            Updated staff class as a dictionary if successful, None if not found
            
        Raises:
            ValueError: If validation fails
        """
        try:
            validate_uuid(staff_class_id, "staff_class_id")
            
            # Validate update_data structure
            if not isinstance(update_data, dict):
                raise ValueError("update_data must be a dictionary")
            
            # Validate specific fields if present
            if 'name' in update_data:
                validate_string(update_data['name'], "name", min_length=1, max_length=255)
            
            if 'experience_type' in update_data:
                validate_enum_value(update_data['experience_type'], ExperienceType, "experience_type")
            
            if 'min_experience' in update_data:
                validate_integer(update_data['min_experience'], "min_experience", min_value=0)
                
                # If max_experience is in the update_data, check it's greater than min_experience
                if 'max_experience' in update_data and update_data['max_experience'] is not None:
                    if update_data['max_experience'] < update_data['min_experience']:
                        raise ValueError("max_experience must be greater than or equal to min_experience")
                # If max_experience is not in update_data but exists in staff class, need to check against that
                else:
                    staff_class = self._repository.get_by_id(staff_class_id)
                    if staff_class and staff_class.max_experience is not None:
                        if staff_class.max_experience < update_data['min_experience']:
                            raise ValueError("min_experience cannot be greater than existing max_experience")
            
            if 'max_experience' in update_data:
                # If min_experience is in the update_data, we already checked above
                if 'min_experience' not in update_data:
                    staff_class = self._repository.get_by_id(staff_class_id)
                    if staff_class and update_data['max_experience'] is not None:
                        validate_integer(update_data['max_experience'], "max_experience", min_value=staff_class.min_experience)
            
            # Update the staff class
            updated_staff_class = self._repository.update(staff_class_id, update_data)
            if not updated_staff_class:
                logger.warning(f"Staff class with ID {staff_class_id} not found for update")
                return None
            
            logger.info(f"Updated staff class {staff_class_id}")
            
            return updated_staff_class.to_dict() if hasattr(updated_staff_class, 'to_dict') else vars(updated_staff_class)
        except Exception as e:
            logger.error(f"Error updating staff class: {e}")
            raise
    
    def delete_staff_class(self, staff_class_id: uuid.UUID) -> bool:
        """
        Delete a staff class (soft delete by deactivating).
        
        Args:
            staff_class_id: UUID of the staff class to delete
            
        Returns:
            True if successful, False if staff class not found
            
        Raises:
            ValueError: If the staff class has assigned attorneys
        """
        try:
            validate_uuid(staff_class_id, "staff_class_id")
            
            # Check if staff class has assigned attorneys
            attorneys = self._repository.get_attorneys_by_staff_class(staff_class_id)
            if attorneys:
                attorney_count = len(attorneys)
                raise ValueError(
                    f"Cannot delete staff class with {attorney_count} attorneys assigned. "
                    "Reassign attorneys to a different staff class first."
                )
            
            # Delete the staff class
            result = self._repository.delete(staff_class_id)
            
            if result:
                logger.info(f"Deleted staff class {staff_class_id}")
            else:
                logger.warning(f"Staff class with ID {staff_class_id} not found for deletion")
                
            return result
        except Exception as e:
            logger.error(f"Error deleting staff class: {e}")
            raise
    
    def get_eligible_attorneys(self, staff_class_id: uuid.UUID) -> List[dict]:
        """
        Get all attorneys eligible for a staff class based on experience criteria.
        
        Args:
            staff_class_id: UUID of the staff class
            
        Returns:
            List of eligible attorney dictionaries
        """
        try:
            validate_uuid(staff_class_id, "staff_class_id")
            
            eligible_attorneys = self._repository.get_eligible_attorneys(staff_class_id)
            
            # Convert attorneys to dictionaries
            result = []
            for attorney in eligible_attorneys:
                if hasattr(attorney, 'to_dict'):
                    result.append(attorney.to_dict())
                else:
                    result.append(vars(attorney))
            
            logger.info(f"Found {len(result)} eligible attorneys for staff class {staff_class_id}")
            return result
        except Exception as e:
            logger.error(f"Error getting eligible attorneys: {e}")
            raise
    
    def assign_attorney(self, staff_class_id: uuid.UUID, attorney_id: uuid.UUID) -> bool:
        """
        Assign an attorney to a staff class.
        
        Args:
            staff_class_id: UUID of the staff class
            attorney_id: UUID of the attorney
            
        Returns:
            True if successful, False if staff class or attorney not found
            
        Raises:
            ValueError: If the attorney is not eligible for the staff class
        """
        try:
            validate_uuid(staff_class_id, "staff_class_id")
            validate_uuid(attorney_id, "attorney_id")
            
            # Get the staff class
            staff_class = self._repository.get_by_id(staff_class_id)
            if not staff_class:
                logger.warning(f"Staff class with ID {staff_class_id} not found")
                return False
            
            # Get all eligible attorneys for the staff class
            eligible_attorneys = self._repository.get_eligible_attorneys(staff_class_id)
            eligible_attorney_ids = [attorney.id for attorney in eligible_attorneys]
            
            # Check if the attorney is in the eligible list
            if attorney_id not in eligible_attorney_ids:
                raise ValueError(f"Attorney {attorney_id} is not eligible for staff class {staff_class_id}")
            
            # Assign the attorney to the staff class
            result = self._repository.assign_attorney(staff_class_id, attorney_id)
            
            if result:
                logger.info(f"Assigned attorney {attorney_id} to staff class {staff_class_id}")
            else:
                logger.warning(f"Failed to assign attorney {attorney_id} to staff class {staff_class_id}")
                
            return result
        except Exception as e:
            logger.error(f"Error assigning attorney to staff class: {e}")
            raise
    
    def assign_attorneys_automatically(
        self, 
        organization_id: uuid.UUID, 
        attorney_ids: Optional[List[uuid.UUID]] = None
    ) -> dict:
        """
        Automatically assign attorneys to appropriate staff classes based on experience.
        
        Args:
            organization_id: UUID of the organization
            attorney_ids: Optional list of attorney IDs to focus on (if None, processes all unassigned attorneys)
            
        Returns:
            Dictionary with successful and failed assignments
        """
        try:
            validate_uuid(organization_id, "organization_id")
            
            # Get all active staff classes for the organization
            staff_classes = self._repository.get_by_organization(organization_id, active_only=True)
            if not staff_classes:
                logger.warning(f"No active staff classes found for organization {organization_id}")
                return {"success": [], "failure": []}
            
            # Get attorneys to process
            if attorney_ids:
                # Validate each attorney ID
                for attorney_id in attorney_ids:
                    validate_uuid(attorney_id, "attorney_id")
                
                # Get specific attorneys (could be assigned or unassigned)
                attorneys = []
                for attorney_id in attorney_ids:
                    # This is a simplified approach - the repository would need a method to get attorneys by ID
                    # For now, we'll assume there's a method to get an attorney by ID
                    attorney = self._repository._db.execute(
                        f"SELECT * FROM attorneys WHERE id = '{attorney_id}' AND organization_id = '{organization_id}'"
                    ).fetchone()
                    if attorney:
                        attorneys.append(attorney)
            else:
                # Get all unassigned attorneys in the organization
                attorneys = self._repository.get_attorneys_without_staff_class(organization_id)
            
            # Process each attorney
            successes = []
            failures = []
            
            for attorney in attorneys:
                # Convert staff classes to dictionaries for the helper method
                staff_class_dicts = [
                    staff_class.to_dict() if hasattr(staff_class, 'to_dict') else vars(staff_class)
                    for staff_class in staff_classes
                ]
                
                attorney_dict = attorney.to_dict() if hasattr(attorney, 'to_dict') else vars(attorney)
                
                # Find the best staff class for this attorney
                best_staff_class = self.get_best_staff_class_for_attorney(attorney_dict, staff_class_dicts)
                
                if best_staff_class:
                    # Try to assign the attorney to the staff class
                    try:
                        result = self._repository.assign_attorney(
                            uuid.UUID(best_staff_class["id"]), 
                            attorney.id
                        )
                        
                        if result:
                            successes.append({
                                "attorney_id": str(attorney.id),
                                "attorney_name": attorney.name,
                                "staff_class_id": best_staff_class["id"],
                                "staff_class_name": best_staff_class["name"]
                            })
                        else:
                            failures.append({
                                "attorney_id": str(attorney.id),
                                "attorney_name": attorney.name,
                                "reason": "Assignment failed in repository"
                            })
                    except Exception as e:
                        failures.append({
                            "attorney_id": str(attorney.id),
                            "attorney_name": attorney.name,
                            "reason": str(e)
                        })
                else:
                    failures.append({
                        "attorney_id": str(attorney.id),
                        "attorney_name": attorney.name,
                        "reason": "No eligible staff class found"
                    })
            
            logger.info(f"Automatic assignment: {len(successes)} attorneys assigned, {len(failures)} failed")
            
            return {
                "success": successes,
                "failure": failures
            }
        except Exception as e:
            logger.error(f"Error in automatic attorney assignment: {e}")
            raise
    
    def get_best_staff_class_for_attorney(self, attorney: dict, staff_classes: List[dict]) -> Optional[dict]:
        """
        Determine the most appropriate staff class for an attorney based on experience.
        
        Args:
            attorney: Attorney dictionary
            staff_classes: List of staff class dictionaries
            
        Returns:
            Best matching staff class or None if no match
        """
        try:
            # Filter staff classes to only include those the attorney is eligible for
            eligible_classes = []
            
            for staff_class in staff_classes:
                # Calculate the attorney's experience value for this staff class's experience type
                experience_type = staff_class["experience_type"]
                if isinstance(experience_type, str):
                    experience_type = ExperienceType(experience_type)
                
                experience_value = self.calculate_experience(attorney, experience_type)
                
                # Check if the attorney's experience falls within the staff class's range
                min_experience = staff_class["min_experience"]
                max_experience = staff_class.get("max_experience")
                
                if experience_value >= min_experience and (max_experience is None or experience_value <= max_experience):
                    eligible_classes.append({
                        "staff_class": staff_class,
                        "experience_value": experience_value
                    })
            
            if not eligible_classes:
                return None
            
            if len(eligible_classes) == 1:
                return eligible_classes[0]["staff_class"]
            
            # For multiple eligible classes, calculate a fit score
            # The fit score is higher for classes where the attorney's experience is closer to the center of the range
            best_fit_score = -1
            best_class = None
            
            for eligible in eligible_classes:
                staff_class = eligible["staff_class"]
                experience_value = eligible["experience_value"]
                min_experience = staff_class["min_experience"]
                max_experience = staff_class.get("max_experience")
                
                if max_experience is None:
                    # For open-ended ranges, the fit score decreases as the experience increases beyond the minimum
                    fit_score = 1.0 / (1.0 + (experience_value - min_experience))
                else:
                    # For closed ranges, calculate how centered the experience is in the range
                    range_center = (min_experience + max_experience) / 2
                    range_width = max_experience - min_experience
                    if range_width == 0:
                        # If min and max are the same, the score is 1 if the experience matches exactly, 0 otherwise
                        fit_score = 1.0 if experience_value == min_experience else 0.0
                    else:
                        # The score is higher when closer to the center
                        distance_from_center = abs(experience_value - range_center)
                        normalized_distance = distance_from_center / (range_width / 2)
                        fit_score = 1.0 - normalized_distance
                
                if fit_score > best_fit_score:
                    best_fit_score = fit_score
                    best_class = staff_class
            
            return best_class
        except Exception as e:
            logger.error(f"Error finding best staff class for attorney: {e}")
            return None
    
    def calculate_experience(self, attorney: dict, experience_type: ExperienceType) -> int:
        """
        Calculate experience value for an attorney based on experience type.
        
        Args:
            attorney: Attorney dictionary
            experience_type: Type of experience to calculate
            
        Returns:
            Experience value in years
        """
        try:
            today = datetime.now().date()
            
            if experience_type == ExperienceType.GRADUATION_YEAR:
                if "graduation_date" in attorney and attorney["graduation_date"]:
                    graduation_date = attorney["graduation_date"]
                    if isinstance(graduation_date, str):
                        graduation_date = datetime.strptime(graduation_date, "%Y-%m-%d").date()
                    return calculate_years_since_date(graduation_date)
            
            elif experience_type == ExperienceType.BAR_YEAR:
                if "bar_date" in attorney and attorney["bar_date"]:
                    bar_date = attorney["bar_date"]
                    if isinstance(bar_date, str):
                        bar_date = datetime.strptime(bar_date, "%Y-%m-%d").date()
                    return calculate_years_since_date(bar_date)
            
            elif experience_type == ExperienceType.YEARS_IN_ROLE:
                if "promotion_date" in attorney and attorney["promotion_date"]:
                    promotion_date = attorney["promotion_date"]
                    if isinstance(promotion_date, str):
                        promotion_date = datetime.strptime(promotion_date, "%Y-%m-%d").date()
                    return calculate_years_since_date(promotion_date)
            
            # Return 0 if the relevant date is None or not available
            logger.warning(f"Could not calculate experience for attorney with experience type {experience_type}")
            return 0
        except Exception as e:
            logger.error(f"Error calculating attorney experience: {e}")
            return 0
    
    def analyze_staff_class_structure(self, organization_id: uuid.UUID) -> Dict[str, Any]:
        """
        Analyze staff class structure for overlaps and gaps.
        
        Args:
            organization_id: UUID of the organization
            
        Returns:
            Analysis results including overlaps and gaps
        """
        try:
            validate_uuid(organization_id, "organization_id")
            
            # Get all staff classes for the organization
            staff_classes = self._repository.get_by_organization(organization_id, active_only=True)
            if not staff_classes:
                logger.warning(f"No active staff classes found for organization {organization_id}")
                return {
                    "organization_id": str(organization_id),
                    "experience_types": {},
                    "total_classes": 0,
                    "has_overlaps": False,
                    "has_gaps": False
                }
            
            # Group staff classes by experience type
            classes_by_type = {}
            for staff_class in staff_classes:
                exp_type = staff_class.experience_type
                if exp_type not in classes_by_type:
                    classes_by_type[exp_type] = []
                classes_by_type[exp_type].append(staff_class)
            
            result = {
                "organization_id": str(organization_id),
                "experience_types": {},
                "total_classes": len(staff_classes),
                "has_overlaps": False,
                "has_gaps": False
            }
            
            # Analyze each experience type group
            for exp_type, classes in classes_by_type.items():
                # Find overlaps
                overlaps = self._repository.get_overlapping_classes(organization_id, exp_type)
                
                # Find gaps
                gaps = self._repository.find_experience_gaps(organization_id, exp_type)
                
                # Calculate coverage statistics
                min_exp = min(cls.min_experience for cls in classes)
                max_exp = max(cls.max_experience if cls.max_experience is not None else float('inf') for cls in classes)
                
                # A perfect coverage would have no gaps and no overlaps
                has_perfect_coverage = len(overlaps) == 0 and len(gaps) == 0
                
                # Update result
                result["experience_types"][exp_type.value] = {
                    "class_count": len(classes),
                    "overlaps": [
                        {
                            "class1": {
                                "id": str(overlap[0].id),
                                "name": overlap[0].name,
                                "min_experience": overlap[0].min_experience,
                                "max_experience": overlap[0].max_experience
                            },
                            "class2": {
                                "id": str(overlap[1].id),
                                "name": overlap[1].name,
                                "min_experience": overlap[1].min_experience,
                                "max_experience": overlap[1].max_experience
                            }
                        }
                        for overlap in overlaps
                    ],
                    "gaps": [
                        {
                            "min": gap["min"],
                            "max": gap["max"]
                        }
                        for gap in gaps
                    ],
                    "min_experience": min_exp,
                    "max_experience": float('inf') if max_exp == float('inf') else max_exp,
                    "has_perfect_coverage": has_perfect_coverage
                }
                
                if len(overlaps) > 0:
                    result["has_overlaps"] = True
                
                if len(gaps) > 0:
                    result["has_gaps"] = True
            
            logger.info(f"Analyzed staff class structure for organization {organization_id}")
            return result
        except Exception as e:
            logger.error(f"Error analyzing staff class structure: {e}")
            raise
    
    def get_overlapping_classes(self, organization_id: uuid.UUID, experience_type: ExperienceType) -> List[dict]:
        """
        Find staff classes with overlapping experience ranges.
        
        Args:
            organization_id: UUID of the organization
            experience_type: Type of experience to check for overlaps
            
        Returns:
            List of overlapping class pair dictionaries
        """
        try:
            validate_uuid(organization_id, "organization_id")
            validate_enum_value(experience_type, ExperienceType, "experience_type")
            
            overlapping_pairs = self._repository.get_overlapping_classes(organization_id, experience_type)
            
            # Format the results
            result = []
            for pair in overlapping_pairs:
                class1, class2 = pair
                
                # Calculate the overlap range
                overlap_min = max(class1.min_experience, class2.min_experience)
                overlap_max = min(
                    class1.max_experience if class1.max_experience is not None else float('inf'),
                    class2.max_experience if class2.max_experience is not None else float('inf')
                )
                
                if overlap_max == float('inf'):
                    overlap_range = f"{overlap_min}+"
                else:
                    overlap_range = f"{overlap_min}-{overlap_max}"
                
                result.append({
                    "class1": {
                        "id": str(class1.id),
                        "name": class1.name,
                        "min_experience": class1.min_experience,
                        "max_experience": class1.max_experience
                    },
                    "class2": {
                        "id": str(class2.id),
                        "name": class2.name,
                        "min_experience": class2.min_experience,
                        "max_experience": class2.max_experience
                    },
                    "overlap_range": overlap_range
                })
            
            logger.info(f"Found {len(result)} overlapping class pairs for organization {organization_id}")
            return result
        except Exception as e:
            logger.error(f"Error finding overlapping classes: {e}")
            raise
    
    def find_experience_gaps(self, organization_id: uuid.UUID, experience_type: ExperienceType) -> List[dict]:
        """
        Find gaps in experience coverage between staff classes.
        
        Args:
            organization_id: UUID of the organization
            experience_type: Type of experience to check for gaps
            
        Returns:
            List of experience gap dictionaries
        """
        try:
            validate_uuid(organization_id, "organization_id")
            validate_enum_value(experience_type, ExperienceType, "experience_type")
            
            gaps = self._repository.find_experience_gaps(organization_id, experience_type)
            
            # Format the results
            result = []
            for gap in gaps:
                result.append({
                    "min": gap["min"],
                    "max": gap["max"],
                    "range": f"{gap['min']}-{gap['max']}",
                    "size": gap["max"] - gap["min"] + 1
                })
            
            logger.info(f"Found {len(result)} experience gaps for organization {organization_id}")
            return result
        except Exception as e:
            logger.error(f"Error finding experience gaps: {e}")
            raise
    
    def clone_staff_class_structure(self, source_organization_id: uuid.UUID, target_organization_id: uuid.UUID) -> dict:
        """
        Clone an organization's entire staff class structure to another organization.
        
        Args:
            source_organization_id: UUID of the source organization
            target_organization_id: UUID of the target organization
            
        Returns:
            Results including cloned classes count and any errors
        """
        try:
            validate_uuid(source_organization_id, "source_organization_id")
            validate_uuid(target_organization_id, "target_organization_id")
            
            # Get all staff classes from source organization
            source_classes = self._repository.get_by_organization(source_organization_id, active_only=True)
            
            if not source_classes:
                logger.warning(f"No active staff classes found for source organization {source_organization_id}")
                return {
                    "source_organization_id": str(source_organization_id),
                    "target_organization_id": str(target_organization_id),
                    "cloned_count": 0,
                    "failures": []
                }
            
            # Clone each staff class to the target organization
            successful_clones = []
            failures = []
            
            for source_class in source_classes:
                try:
                    # Create a new staff class in the target organization with the same properties
                    clone = self._repository.create(
                        organization_id=target_organization_id,
                        name=source_class.name,
                        experience_type=source_class.experience_type,
                        min_experience=source_class.min_experience,
                        max_experience=source_class.max_experience,
                        practice_area=source_class.practice_area
                    )
                    
                    successful_clones.append({
                        "source_id": str(source_class.id),
                        "source_name": source_class.name,
                        "clone_id": str(clone.id),
                        "clone_name": clone.name
                    })
                except Exception as e:
                    failures.append({
                        "source_id": str(source_class.id),
                        "source_name": source_class.name,
                        "error": str(e)
                    })
            
            logger.info(f"Cloned {len(successful_clones)} staff classes from {source_organization_id} to {target_organization_id}")
            
            return {
                "source_organization_id": str(source_organization_id),
                "target_organization_id": str(target_organization_id),
                "cloned_count": len(successful_clones),
                "successful_clones": successful_clones,
                "failures": failures
            }
        except Exception as e:
            logger.error(f"Error cloning staff class structure: {e}")
            raise