"""
Repository class for handling database operations related to Outside Counsel Guidelines (OCGs).

This module provides a comprehensive set of methods for managing OCGs, sections, alternatives,
and firm selections, supporting the negotiation workflow between clients and law firms.
"""

import uuid
import datetime
from typing import List, Dict, Optional, Union, Any, Tuple

import sqlalchemy
from sqlalchemy import and_, or_, desc, asc, func, select, update, delete
from sqlalchemy.orm import Session, joinedload, selectinload

from ..session import get_db
from ..models.ocg import (
    OCG, OCGSection, OCGAlternative, OCGFirmSelection, 
    OCGStatus, ocg_firm_point_budgets
)
from ...utils.logging import get_logger

# Set up logger
logger = get_logger(__name__, 'repository')


class OCGRepository:
    """
    Repository class for handling database operations for OCG entities, providing
    CRUD operations and specialized queries for OCG management and negotiation.
    """

    def __init__(self, db_session: Session = None):
        """
        Initialize a new OCGRepository with a database session.
        
        Args:
            db_session: SQLAlchemy database session. If not provided, a new session will be created.
        """
        self._db = db_session or get_db()
        logger.debug("OCGRepository initialized")

    def create(self, client_id: uuid.UUID, name: str, version: int = 1, 
               total_points: Optional[int] = 10, default_firm_point_budget: Optional[int] = 5,
               settings: Optional[dict] = None) -> OCG:
        """
        Create a new OCG record.
        
        Args:
            client_id: UUID of the client organization
            name: Name of the OCG
            version: Version number (defaults to 1)
            total_points: Total points available for negotiations (defaults to 10)
            default_firm_point_budget: Default point budget for firms (defaults to 5)
            settings: Optional OCG settings (document template, notification settings, etc.)
            
        Returns:
            The newly created OCG
        """
        try:
            # Create new OCG instance
            ocg = OCG(
                client_id=client_id,
                name=name,
                version=version,
                total_points=total_points,
                default_firm_point_budget=default_firm_point_budget
            )
            
            # Set custom settings if provided
            if settings:
                ocg.settings = settings
                
            # Add OCG to database session
            self._db.add(ocg)
            self._db.commit()
            
            logger.info(f"Created new OCG: {name}, version {version} for client {client_id}")
            return ocg
        except Exception as e:
            self._db.rollback()
            logger.error(f"Error creating OCG: {str(e)}")
            raise

    def get_by_id(self, ocg_id: uuid.UUID) -> Optional[OCG]:
        """
        Get an OCG by its ID.
        
        Args:
            ocg_id: The UUID of the OCG to retrieve
            
        Returns:
            OCG if found, None otherwise
        """
        try:
            query = select(OCG).where(OCG.id == ocg_id)
            result = self._db.execute(query).scalars().first()
            return result
        except Exception as e:
            logger.error(f"Error retrieving OCG by ID {ocg_id}: {str(e)}")
            return None

    def get_by_client(self, client_id: uuid.UUID, limit: Optional[int] = None, 
                     offset: Optional[int] = 0) -> List[OCG]:
        """
        Get all OCGs for a client.
        
        Args:
            client_id: The UUID of the client organization
            limit: Maximum number of OCGs to return
            offset: Number of OCGs to skip (for pagination)
            
        Returns:
            List of OCGs for the client
        """
        try:
            query = select(OCG).where(OCG.client_id == client_id)
            
            # Apply pagination if specified
            if limit is not None:
                query = query.limit(limit).offset(offset or 0)
                
            # Execute query
            result = self._db.execute(query).scalars().all()
            return list(result)
        except Exception as e:
            logger.error(f"Error retrieving OCGs for client {client_id}: {str(e)}")
            return []

    def get_by_status(self, status: OCGStatus, client_id: Optional[uuid.UUID] = None,
                      limit: Optional[int] = None, offset: Optional[int] = 0) -> List[OCG]:
        """
        Get OCGs with a specific status.
        
        Args:
            status: The OCG status to filter by
            client_id: Optional client ID to filter by
            limit: Maximum number of OCGs to return
            offset: Number of OCGs to skip (for pagination)
            
        Returns:
            List of OCGs with the specified status
        """
        try:
            query = select(OCG).where(OCG.status == status)
            
            # Add client filter if provided
            if client_id:
                query = query.where(OCG.client_id == client_id)
                
            # Apply pagination if specified
            if limit is not None:
                query = query.limit(limit).offset(offset or 0)
                
            # Execute query
            result = self._db.execute(query).scalars().all()
            return list(result)
        except Exception as e:
            logger.error(f"Error retrieving OCGs with status {status}: {str(e)}")
            return []

    def get_current_version(self, client_id: uuid.UUID, name: str) -> Optional[OCG]:
        """
        Get the current (latest) version of an OCG.
        
        Args:
            client_id: The UUID of the client organization
            name: The name of the OCG
            
        Returns:
            Latest version of the OCG if found, None otherwise
        """
        try:
            query = (
                select(OCG)
                .where(OCG.client_id == client_id, OCG.name == name)
                .order_by(desc(OCG.version))
                .limit(1)
            )
            
            result = self._db.execute(query).scalars().first()
            return result
        except Exception as e:
            logger.error(f"Error retrieving current version of OCG {name} for client {client_id}: {str(e)}")
            return None

    def update(self, ocg_id: uuid.UUID, ocg_data: dict) -> Optional[OCG]:
        """
        Update an OCG record.
        
        Args:
            ocg_id: The UUID of the OCG to update
            ocg_data: Dictionary of fields to update
            
        Returns:
            Updated OCG if found, None otherwise
        """
        try:
            # Get the OCG by ID
            ocg = self.get_by_id(ocg_id)
            if not ocg:
                logger.warning(f"OCG with ID {ocg_id} not found for update")
                return None
                
            # Update allowed fields
            allowed_fields = ['name', 'status', 'total_points', 'default_firm_point_budget', 'settings']
            for field in allowed_fields:
                if field in ocg_data:
                    setattr(ocg, field, ocg_data[field])
                    
            # Update timestamp
            ocg.updated_at = datetime.datetime.utcnow()
            
            # Commit changes
            self._db.commit()
            
            logger.info(f"Updated OCG with ID {ocg_id}")
            return ocg
        except Exception as e:
            self._db.rollback()
            logger.error(f"Error updating OCG with ID {ocg_id}: {str(e)}")
            return None

    def delete(self, ocg_id: uuid.UUID) -> bool:
        """
        Delete an OCG record.
        
        Args:
            ocg_id: The UUID of the OCG to delete
            
        Returns:
            True if deleted, False if not found
        """
        try:
            # Get the OCG by ID
            ocg = self.get_by_id(ocg_id)
            if not ocg:
                logger.warning(f"OCG with ID {ocg_id} not found for deletion")
                return False
                
            # Delete the OCG
            self._db.delete(ocg)
            self._db.commit()
            
            logger.info(f"Deleted OCG with ID {ocg_id}")
            return True
        except Exception as e:
            self._db.rollback()
            logger.error(f"Error deleting OCG with ID {ocg_id}: {str(e)}")
            return False

    def add_section(self, ocg_id: uuid.UUID, title: str, content: str, 
                   is_negotiable: bool = False, parent_id: Optional[uuid.UUID] = None,
                   order: Optional[int] = None) -> Optional[OCGSection]:
        """
        Add a section to an OCG.
        
        Args:
            ocg_id: The UUID of the OCG
            title: Section title
            content: Section content text
            is_negotiable: Whether the section can be negotiated
            parent_id: ID of parent section if this is a subsection
            order: Order of this section within its parent (if not provided, will be placed last)
            
        Returns:
            Created section if successful, None otherwise
        """
        try:
            # Get the OCG by ID
            ocg = self.get_by_id(ocg_id)
            if not ocg:
                logger.warning(f"OCG with ID {ocg_id} not found for adding section")
                return None
                
            # Calculate order if not provided
            if order is None:
                if parent_id:
                    # Get the maximum order within the parent section
                    query = (
                        select(func.max(OCGSection.order))
                        .where(OCGSection.ocg_id == ocg_id, OCGSection.parent_id == parent_id)
                    )
                    max_order = self._db.execute(query).scalar() or -1
                    order = max_order + 1
                else:
                    # Get the maximum order for top-level sections
                    query = (
                        select(func.max(OCGSection.order))
                        .where(OCGSection.ocg_id == ocg_id, OCGSection.parent_id == None)
                    )
                    max_order = self._db.execute(query).scalar() or -1
                    order = max_order + 1
                    
            # Create new section
            section = OCGSection(
                ocg_id=ocg_id,
                title=title,
                content=content,
                is_negotiable=is_negotiable,
                parent_id=parent_id,
                order=order
            )
            
            # Add to database and commit
            self._db.add(section)
            self._db.commit()
            
            logger.info(f"Added section '{title}' to OCG {ocg_id}")
            return section
        except Exception as e:
            self._db.rollback()
            logger.error(f"Error adding section to OCG {ocg_id}: {str(e)}")
            return None

    def get_section(self, section_id: uuid.UUID) -> Optional[OCGSection]:
        """
        Get an OCG section by ID.
        
        Args:
            section_id: The UUID of the section to retrieve
            
        Returns:
            Section if found, None otherwise
        """
        try:
            query = select(OCGSection).where(OCGSection.id == section_id)
            result = self._db.execute(query).scalars().first()
            return result
        except Exception as e:
            logger.error(f"Error retrieving section with ID {section_id}: {str(e)}")
            return None

    def update_section(self, section_id: uuid.UUID, section_data: dict) -> Optional[OCGSection]:
        """
        Update an OCG section.
        
        Args:
            section_id: The UUID of the section to update
            section_data: Dictionary of fields to update
            
        Returns:
            Updated section if found, None otherwise
        """
        try:
            # Get the section by ID
            section = self.get_section(section_id)
            if not section:
                logger.warning(f"Section with ID {section_id} not found for update")
                return None
                
            # Update allowed fields
            allowed_fields = ['title', 'content', 'is_negotiable', 'order', 'parent_id']
            for field in allowed_fields:
                if field in section_data:
                    setattr(section, field, section_data[field])
                    
            # Update timestamp
            section.updated_at = datetime.datetime.utcnow()
            
            # Commit changes
            self._db.commit()
            
            logger.info(f"Updated section with ID {section_id}")
            return section
        except Exception as e:
            self._db.rollback()
            logger.error(f"Error updating section with ID {section_id}: {str(e)}")
            return None

    def delete_section(self, section_id: uuid.UUID) -> bool:
        """
        Delete an OCG section.
        
        Args:
            section_id: The UUID of the section to delete
            
        Returns:
            True if deleted, False if not found
        """
        try:
            # Get the section by ID
            section = self.get_section(section_id)
            if not section:
                logger.warning(f"Section with ID {section_id} not found for deletion")
                return False
                
            # Delete the section
            self._db.delete(section)
            self._db.commit()
            
            logger.info(f"Deleted section with ID {section_id}")
            return True
        except Exception as e:
            self._db.rollback()
            logger.error(f"Error deleting section with ID {section_id}: {str(e)}")
            return False

    def add_alternative(self, section_id: uuid.UUID, title: str, content: str, 
                        points: int, is_default: Optional[bool] = False,
                        order: Optional[int] = None) -> Optional[OCGAlternative]:
        """
        Add an alternative to an OCG section.
        
        Args:
            section_id: The UUID of the section
            title: Alternative title
            content: Alternative content text
            points: Point cost of this alternative
            is_default: Whether this is the default alternative
            order: Order of this alternative within the section (if not provided, will be placed last)
            
        Returns:
            Created alternative if successful, None otherwise
        """
        try:
            # Get the section by ID
            section = self.get_section(section_id)
            if not section:
                logger.warning(f"Section with ID {section_id} not found for adding alternative")
                return None
                
            # Ensure section is negotiable
            if not section.is_negotiable:
                section.is_negotiable = True
                logger.info(f"Section {section_id} marked as negotiable")
                
            # Calculate order if not provided
            if order is None:
                query = (
                    select(func.max(OCGAlternative.order))
                    .where(OCGAlternative.section_id == section_id)
                )
                max_order = self._db.execute(query).scalar() or -1
                order = max_order + 1
                
            # If this is the first alternative and is_default not specified, make it default
            if is_default is None:
                query = (
                    select(func.count())
                    .where(OCGAlternative.section_id == section_id)
                )
                count = self._db.execute(query).scalar() or 0
                is_default = (count == 0)
                
            # Create new alternative
            alternative = OCGAlternative(
                section_id=section_id,
                title=title,
                content=content,
                points=points,
                is_default=is_default,
                order=order
            )
            
            # Add to database and commit
            self._db.add(alternative)
            
            # If this is set as default, ensure no other alternatives are default
            if is_default:
                query = (
                    update(OCGAlternative)
                    .where(
                        OCGAlternative.section_id == section_id,
                        OCGAlternative.id != alternative.id
                    )
                    .values(is_default=False)
                )
                self._db.execute(query)
                
            self._db.commit()
            
            logger.info(f"Added alternative '{title}' to section {section_id}")
            return alternative
        except Exception as e:
            self._db.rollback()
            logger.error(f"Error adding alternative to section {section_id}: {str(e)}")
            return None

    def get_alternative(self, alternative_id: uuid.UUID) -> Optional[OCGAlternative]:
        """
        Get an OCG alternative by ID.
        
        Args:
            alternative_id: The UUID of the alternative to retrieve
            
        Returns:
            Alternative if found, None otherwise
        """
        try:
            query = select(OCGAlternative).where(OCGAlternative.id == alternative_id)
            result = self._db.execute(query).scalars().first()
            return result
        except Exception as e:
            logger.error(f"Error retrieving alternative with ID {alternative_id}: {str(e)}")
            return None

    def update_alternative(self, alternative_id: uuid.UUID, 
                          alternative_data: dict) -> Optional[OCGAlternative]:
        """
        Update an OCG alternative.
        
        Args:
            alternative_id: The UUID of the alternative to update
            alternative_data: Dictionary of fields to update
            
        Returns:
            Updated alternative if found, None otherwise
        """
        try:
            # Get the alternative by ID
            alternative = self.get_alternative(alternative_id)
            if not alternative:
                logger.warning(f"Alternative with ID {alternative_id} not found for update")
                return None
                
            # Update allowed fields
            allowed_fields = ['title', 'content', 'points', 'order', 'is_default']
            for field in allowed_fields:
                if field in alternative_data:
                    setattr(alternative, field, alternative_data[field])
            
            # If this is marked as default, update other alternatives in the section
            if alternative_data.get('is_default', False):
                query = (
                    update(OCGAlternative)
                    .where(
                        OCGAlternative.section_id == alternative.section_id,
                        OCGAlternative.id != alternative.id
                    )
                    .values(is_default=False)
                )
                self._db.execute(query)
                    
            # Update timestamp
            alternative.updated_at = datetime.datetime.utcnow()
            
            # Commit changes
            self._db.commit()
            
            logger.info(f"Updated alternative with ID {alternative_id}")
            return alternative
        except Exception as e:
            self._db.rollback()
            logger.error(f"Error updating alternative with ID {alternative_id}: {str(e)}")
            return None

    def delete_alternative(self, alternative_id: uuid.UUID) -> bool:
        """
        Delete an OCG alternative.
        
        Args:
            alternative_id: The UUID of the alternative to delete
            
        Returns:
            True if deleted, False if not found
        """
        try:
            # Get the alternative by ID
            alternative = self.get_alternative(alternative_id)
            if not alternative:
                logger.warning(f"Alternative with ID {alternative_id} not found for deletion")
                return False
            
            # Check if this is the default alternative
            if alternative.is_default:
                # Find another alternative to make default
                query = (
                    select(OCGAlternative)
                    .where(
                        OCGAlternative.section_id == alternative.section_id,
                        OCGAlternative.id != alternative.id
                    )
                    .limit(1)
                )
                other_alternative = self._db.execute(query).scalars().first()
                
                if other_alternative:
                    other_alternative.is_default = True
                else:
                    # If this was the only alternative, mark section as not negotiable
                    section = self.get_section(alternative.section_id)
                    if section:
                        section.is_negotiable = False
                
            # Delete the alternative
            self._db.delete(alternative)
            self._db.commit()
            
            logger.info(f"Deleted alternative with ID {alternative_id}")
            return True
        except Exception as e:
            self._db.rollback()
            logger.error(f"Error deleting alternative with ID {alternative_id}: {str(e)}")
            return False

    def create_firm_selection(self, ocg_id: uuid.UUID, firm_id: uuid.UUID, 
                              section_id: uuid.UUID, alternative_id: uuid.UUID) -> Optional[OCGFirmSelection]:
        """
        Create a firm selection for an OCG section alternative.
        
        Args:
            ocg_id: The UUID of the OCG
            firm_id: The UUID of the law firm
            section_id: The UUID of the section
            alternative_id: The UUID of the selected alternative
            
        Returns:
            Created selection if successful, None otherwise
        """
        try:
            # Get the OCG, section, and alternative by ID
            ocg = self.get_by_id(ocg_id)
            section = self.get_section(section_id)
            alternative = self.get_alternative(alternative_id)
            
            if not ocg or not section or not alternative:
                logger.warning(f"OCG {ocg_id}, section {section_id}, or alternative {alternative_id} not found")
                return None
                
            # Check if the section belongs to the OCG
            if section.ocg_id != ocg_id:
                logger.warning(f"Section {section_id} does not belong to OCG {ocg_id}")
                return None
                
            # Check if the alternative belongs to the section
            if alternative.section_id != section_id:
                logger.warning(f"Alternative {alternative_id} does not belong to section {section_id}")
                return None
                
            # Check if there's already a selection for this firm and section
            query = (
                select(OCGFirmSelection)
                .where(
                    OCGFirmSelection.ocg_id == ocg_id,
                    OCGFirmSelection.firm_id == firm_id,
                    OCGFirmSelection.section_id == section_id
                )
            )
            existing_selection = self._db.execute(query).scalars().first()
            
            if existing_selection:
                # Update existing selection
                existing_selection.alternative_id = alternative_id
                existing_selection.points_used = alternative.points
                existing_selection.updated_at = datetime.datetime.utcnow()
                selection = existing_selection
                logger.info(f"Updated firm selection for firm {firm_id}, section {section_id}")
            else:
                # Create new selection
                selection = OCGFirmSelection(
                    ocg_id=ocg_id,
                    firm_id=firm_id,
                    section_id=section_id,
                    alternative_id=alternative_id,
                    points_used=alternative.points
                )
                self._db.add(selection)
                logger.info(f"Created firm selection for firm {firm_id}, section {section_id}")
                
            # Commit changes
            self._db.commit()
            
            return selection
        except Exception as e:
            self._db.rollback()
            logger.error(f"Error creating firm selection: {str(e)}")
            return None

    def get_selections_by_firm(self, ocg_id: uuid.UUID, firm_id: uuid.UUID) -> List[OCGFirmSelection]:
        """
        Get all selections made by a firm for an OCG.
        
        Args:
            ocg_id: The UUID of the OCG
            firm_id: The UUID of the law firm
            
        Returns:
            List of selections made by the firm
        """
        try:
            query = (
                select(OCGFirmSelection)
                .where(
                    OCGFirmSelection.ocg_id == ocg_id,
                    OCGFirmSelection.firm_id == firm_id
                )
                .options(
                    joinedload(OCGFirmSelection.section),
                    joinedload(OCGFirmSelection.alternative)
                )
            )
            
            result = self._db.execute(query).scalars().all()
            return list(result)
        except Exception as e:
            logger.error(f"Error retrieving selections for firm {firm_id}, OCG {ocg_id}: {str(e)}")
            return []

    def delete_firm_selection(self, selection_id: uuid.UUID) -> bool:
        """
        Delete a firm selection.
        
        Args:
            selection_id: The UUID of the selection to delete
            
        Returns:
            True if deleted, False if not found
        """
        try:
            # Get the selection by ID
            query = select(OCGFirmSelection).where(OCGFirmSelection.id == selection_id)
            selection = self._db.execute(query).scalars().first()
            
            if not selection:
                logger.warning(f"Selection with ID {selection_id} not found for deletion")
                return False
                
            # Delete the selection
            self._db.delete(selection)
            self._db.commit()
            
            logger.info(f"Deleted selection with ID {selection_id}")
            return True
        except Exception as e:
            self._db.rollback()
            logger.error(f"Error deleting selection with ID {selection_id}: {str(e)}")
            return False

    def clear_firm_selections(self, ocg_id: uuid.UUID, firm_id: uuid.UUID) -> bool:
        """
        Clear all selections made by a firm for an OCG.
        
        Args:
            ocg_id: The UUID of the OCG
            firm_id: The UUID of the law firm
            
        Returns:
            True if successful
        """
        try:
            # Delete all selections for this firm and OCG
            query = (
                delete(OCGFirmSelection)
                .where(
                    OCGFirmSelection.ocg_id == ocg_id,
                    OCGFirmSelection.firm_id == firm_id
                )
            )
            
            self._db.execute(query)
            self._db.commit()
            
            logger.info(f"Cleared all selections for firm {firm_id}, OCG {ocg_id}")
            return True
        except Exception as e:
            self._db.rollback()
            logger.error(f"Error clearing selections for firm {firm_id}, OCG {ocg_id}: {str(e)}")
            return False

    def update_ocg_status(self, ocg_id: uuid.UUID, status: OCGStatus) -> Optional[OCG]:
        """
        Update the status of an OCG.
        
        Args:
            ocg_id: The UUID of the OCG
            status: The new status
            
        Returns:
            Updated OCG if found, None otherwise
        """
        try:
            # Get the OCG by ID
            ocg = self.get_by_id(ocg_id)
            if not ocg:
                logger.warning(f"OCG with ID {ocg_id} not found for status update")
                return None
                
            # Update status
            ocg.status = status
            
            # Update timestamp based on status
            if status == OCGStatus.PUBLISHED:
                ocg.published_at = datetime.datetime.utcnow()
            elif status == OCGStatus.SIGNED:
                ocg.signed_at = datetime.datetime.utcnow()
                
            # Commit changes
            self._db.commit()
            
            logger.info(f"Updated OCG {ocg_id} status to {status}")
            return ocg
        except Exception as e:
            self._db.rollback()
            logger.error(f"Error updating OCG {ocg_id} status: {str(e)}")
            return None

    def create_new_version(self, ocg_id: uuid.UUID) -> Optional[OCG]:
        """
        Create a new version of an OCG.
        
        Args:
            ocg_id: The UUID of the OCG to version
            
        Returns:
            New OCG version if successful, None otherwise
        """
        try:
            # Get the OCG by ID
            ocg = self.get_by_id(ocg_id)
            if not ocg:
                logger.warning(f"OCG with ID {ocg_id} not found for versioning")
                return None
                
            # Create new OCG with incremented version
            new_ocg = OCG(
                client_id=ocg.client_id,
                name=ocg.name,
                version=ocg.version + 1,
                total_points=ocg.total_points,
                default_firm_point_budget=ocg.default_firm_point_budget
            )
            
            # Copy settings
            if ocg.settings:
                new_ocg.settings = ocg.settings.copy()
                
            # Add to database
            self._db.add(new_ocg)
            self._db.flush()  # Flush to get new_ocg.id
            
            # Create mappings from old section IDs to new section objects
            section_map = {}
            
            # Copy sections
            for old_section in ocg.sections:
                # Create new section (without parent_id for now)
                new_section = OCGSection(
                    ocg_id=new_ocg.id,
                    title=old_section.title,
                    content=old_section.content,
                    is_negotiable=old_section.is_negotiable,
                    order=old_section.order
                )
                self._db.add(new_section)
                self._db.flush()  # Flush to get new_section.id
                
                # Store mapping
                section_map[old_section.id] = new_section
                
                # Copy alternatives if negotiable
                if old_section.is_negotiable:
                    for old_alt in old_section.alternatives:
                        new_alt = OCGAlternative(
                            section_id=new_section.id,
                            title=old_alt.title,
                            content=old_alt.content,
                            points=old_alt.points,
                            is_default=old_alt.is_default,
                            order=old_alt.order
                        )
                        self._db.add(new_alt)
            
            # Set parent_id for subsections
            for old_section in ocg.sections:
                if old_section.parent_id and old_section.parent_id in section_map:
                    new_section = section_map[old_section.id]
                    parent_section = section_map[old_section.parent_id]
                    new_section.parent_id = parent_section.id
            
            # Commit changes
            self._db.commit()
            
            logger.info(f"Created new version {new_ocg.version} of OCG {ocg.name}")
            return new_ocg
        except Exception as e:
            self._db.rollback()
            logger.error(f"Error creating new version of OCG {ocg_id}: {str(e)}")
            return None

    def get_versions(self, client_id: uuid.UUID, name: str) -> List[OCG]:
        """
        Get all versions of an OCG.
        
        Args:
            client_id: The UUID of the client organization
            name: The name of the OCG
            
        Returns:
            List of OCG versions ordered by version number
        """
        try:
            query = (
                select(OCG)
                .where(OCG.client_id == client_id, OCG.name == name)
                .order_by(asc(OCG.version))
            )
            
            result = self._db.execute(query).scalars().all()
            return list(result)
        except Exception as e:
            logger.error(f"Error retrieving versions of OCG {name} for client {client_id}: {str(e)}")
            return []

    def set_firm_point_budget(self, ocg_id: uuid.UUID, firm_id: uuid.UUID, points: int) -> bool:
        """
        Set a custom point budget for a firm.
        
        Args:
            ocg_id: The UUID of the OCG
            firm_id: The UUID of the law firm
            points: Point budget to set (must be >= 0)
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Check points value
            if points < 0:
                logger.warning(f"Cannot set negative point budget: {points}")
                return False
                
            # Get the OCG by ID to ensure it exists
            ocg = self.get_by_id(ocg_id)
            if not ocg:
                logger.warning(f"OCG with ID {ocg_id} not found for setting point budget")
                return False
                
            # Check if record exists
            query = (
                select(ocg_firm_point_budgets)
                .where(
                    ocg_firm_point_budgets.c.ocg_id == ocg_id,
                    ocg_firm_point_budgets.c.firm_id == firm_id
                )
            )
            existing = self._db.execute(query).first()
            
            if existing:
                # Update existing record
                update_stmt = (
                    ocg_firm_point_budgets.update()
                    .where(
                        ocg_firm_point_budgets.c.ocg_id == ocg_id,
                        ocg_firm_point_budgets.c.firm_id == firm_id
                    )
                    .values(
                        points=points,
                        updated_at=datetime.datetime.utcnow()
                    )
                )
                self._db.execute(update_stmt)
            else:
                # Insert new record
                insert_stmt = ocg_firm_point_budgets.insert().values(
                    ocg_id=ocg_id,
                    firm_id=firm_id,
                    points=points,
                    created_at=datetime.datetime.utcnow(),
                    updated_at=datetime.datetime.utcnow()
                )
                self._db.execute(insert_stmt)
                
            # Commit changes
            self._db.commit()
            
            logger.info(f"Set point budget of {points} for firm {firm_id}, OCG {ocg_id}")
            return True
        except Exception as e:
            self._db.rollback()
            logger.error(f"Error setting point budget for firm {firm_id}, OCG {ocg_id}: {str(e)}")
            return False

    def get_firm_point_budget(self, ocg_id: uuid.UUID, firm_id: uuid.UUID) -> int:
        """
        Get a firm's point budget for an OCG.
        
        Args:
            ocg_id: The UUID of the OCG
            firm_id: The UUID of the law firm
            
        Returns:
            Point budget for the firm, or default if not set
        """
        try:
            # Get the OCG by ID to access default_firm_point_budget
            ocg = self.get_by_id(ocg_id)
            if not ocg:
                logger.warning(f"OCG with ID {ocg_id} not found for getting point budget")
                return 0
                
            # Check for custom budget
            query = (
                select(ocg_firm_point_budgets.c.points)
                .where(
                    ocg_firm_point_budgets.c.ocg_id == ocg_id,
                    ocg_firm_point_budgets.c.firm_id == firm_id
                )
            )
            result = self._db.execute(query).scalar_one_or_none()
            
            # Return custom budget if found, otherwise default
            if result is not None:
                return result
            else:
                return ocg.default_firm_point_budget
        except Exception as e:
            logger.error(f"Error getting point budget for firm {firm_id}, OCG {ocg_id}: {str(e)}")
            return 0

    def calculate_points_used(self, ocg_id: uuid.UUID, firm_id: uuid.UUID) -> int:
        """
        Calculate the total points used by a firm in an OCG.
        
        Args:
            ocg_id: The UUID of the OCG
            firm_id: The UUID of the law firm
            
        Returns:
            Total points used by the firm
        """
        try:
            # Get all selections for this firm and OCG
            selections = self.get_selections_by_firm(ocg_id, firm_id)
            
            # Sum points_used from all selections
            total_points = sum(selection.points_used for selection in selections)
            
            return total_points
        except Exception as e:
            logger.error(f"Error calculating points used for firm {firm_id}, OCG {ocg_id}: {str(e)}")
            return 0

    def get_remaining_point_budget(self, ocg_id: uuid.UUID, firm_id: uuid.UUID) -> int:
        """
        Calculate the remaining point budget for a firm.
        
        Args:
            ocg_id: The UUID of the OCG
            firm_id: The UUID of the law firm
            
        Returns:
            Remaining point budget
        """
        try:
            # Get total budget
            total_budget = self.get_firm_point_budget(ocg_id, firm_id)
            
            # Get points used
            points_used = self.calculate_points_used(ocg_id, firm_id)
            
            # Calculate remaining points (never go below 0)
            remaining = max(0, total_budget - points_used)
            
            return remaining
        except Exception as e:
            logger.error(f"Error calculating remaining budget for firm {firm_id}, OCG {ocg_id}: {str(e)}")
            return 0

    def get_negotiable_sections(self, ocg_id: uuid.UUID) -> List[OCGSection]:
        """
        Get all negotiable sections for an OCG.
        
        Args:
            ocg_id: The UUID of the OCG
            
        Returns:
            List of negotiable sections
        """
        try:
            # Get the OCG by ID
            ocg = self.get_by_id(ocg_id)
            if not ocg:
                logger.warning(f"OCG with ID {ocg_id} not found for getting negotiable sections")
                return []
                
            # Filter sections
            negotiable_sections = [section for section in ocg.sections if section.is_negotiable]
            
            return negotiable_sections
        except Exception as e:
            logger.error(f"Error getting negotiable sections for OCG {ocg_id}: {str(e)}")
            return []

    def get_section_hierarchy(self, ocg_id: uuid.UUID) -> List[OCGSection]:
        """
        Get the hierarchical structure of sections for an OCG.
        
        Args:
            ocg_id: The UUID of the OCG
            
        Returns:
            List of top-level sections with their subsections
        """
        try:
            # Get the OCG by ID with eager loading of sections
            query = (
                select(OCG)
                .where(OCG.id == ocg_id)
                .options(
                    selectinload(OCG.sections).selectinload(OCGSection.subsections),
                    selectinload(OCG.sections).selectinload(OCGSection.alternatives)
                )
            )
            ocg = self._db.execute(query).scalars().first()
            
            if not ocg:
                logger.warning(f"OCG with ID {ocg_id} not found for getting section hierarchy")
                return []
                
            # Get top-level sections (those with no parent)
            top_level_sections = [section for section in ocg.sections if section.parent_id is None]
            
            # Sort by order
            top_level_sections.sort(key=lambda s: s.order)
            
            return top_level_sections
        except Exception as e:
            logger.error(f"Error getting section hierarchy for OCG {ocg_id}: {str(e)}")
            return []