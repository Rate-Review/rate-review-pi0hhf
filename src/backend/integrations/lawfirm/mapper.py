"""
Provides mapper classes for transforming attorney and rate data between law firm billing systems and the Justice Bid system format.
This module implements the mapping functionality required for importing attorney profiles, standard rates, and exporting
approved rates back to law firm systems.
"""

import uuid
from datetime import date
from typing import Dict, Any, Optional, List, Union

from ..common.mapper import FieldMapper
from ...db.models.attorney import Attorney
from ...db.models.rate import Rate
from ...utils.logging import get_logger
from ...utils.constants import RATE_TYPES, RATE_STATUSES
from ...utils.datetime_utils import format_date, parse_date

# Set up logger for this module
logger = get_logger(__name__)

# Default mapping configuration for attorney data
DEFAULT_ATTORNEY_MAPPING = {
    'id': {'source_field': 'attorney_id', 'transform': 'uuid'},
    'name': {'source_field': 'name'},
    'bar_date': {'source_field': 'bar_admission_date', 'transform': 'date'},
    'graduation_date': {'source_field': 'law_school_graduation_date', 'transform': 'date'},
    'promotion_date': {'source_field': 'last_promotion_date', 'transform': 'date'},
    'office_ids': {'source_field': 'office_ids', 'transform': 'list_of_uuid'},
    'timekeeper_ids': {'source_field': 'timekeeper_ids', 'transform': 'dict'}
}

# Default mapping configuration for rate data
DEFAULT_RATE_MAPPING = {
    'id': {'source_field': 'rate_id', 'transform': 'uuid'},
    'amount': {'source_field': 'amount', 'transform': 'decimal'},
    'currency': {'source_field': 'currency', 'default': 'USD'},
    'effective_date': {'source_field': 'effective_date', 'transform': 'date'},
    'expiration_date': {'source_field': 'expiration_date', 'transform': 'date'},
    'type': {'source_field': 'type', 'default': 'Standard'},
    'status': {'source_field': 'status', 'default': 'Draft'}
}

def create_standard_mapping(entity_type: str, custom_mapping: Dict = None) -> Dict:
    """
    Creates a standard mapping configuration for law firm data fields.
    
    Args:
        entity_type: Type of entity ('attorney' or 'rate')
        custom_mapping: Optional custom mapping to merge with defaults
        
    Returns:
        Merged mapping configuration with defaults and customizations
    """
    # Select the appropriate default mapping based on entity type
    if entity_type.lower() == 'attorney':
        default_mapping = DEFAULT_ATTORNEY_MAPPING
    elif entity_type.lower() == 'rate':
        default_mapping = DEFAULT_RATE_MAPPING
    else:
        logger.warning(f"Unknown entity type: {entity_type}. Using empty default mapping.")
        default_mapping = {}
    
    # Merge with custom mapping if provided
    final_mapping = default_mapping.copy()
    if custom_mapping:
        for field, config in custom_mapping.items():
            final_mapping[field] = config
    
    logger.debug(f"Created standard mapping for {entity_type}: {final_mapping}")
    return final_mapping

class LawFirmAttorneyMapper(FieldMapper):
    """
    Mapper for transforming attorney data between law firm billing systems and Justice Bid.
    
    This class handles the transformation of attorney data during import from and export to
    law firm billing systems, ensuring proper field mapping and data type conversions.
    """
    
    def __init__(self, organization_id: uuid.UUID, mapping_config: Dict = None, 
                 default_values: Dict = None, validation_rules: Dict = None):
        """
        Initialize the attorney mapper with organization ID and mapping configuration.
        
        Args:
            organization_id: UUID of the law firm
            mapping_config: Custom field mapping configuration
            default_values: Default values for missing fields
            validation_rules: Validation rules for fields
        """
        self.organization_id = organization_id
        
        # Use default mapping if none provided, otherwise merge with default
        if mapping_config is None:
            mapping_config = DEFAULT_ATTORNEY_MAPPING
        else:
            mapping_config = create_standard_mapping('attorney', mapping_config)
        
        # Initialize FieldMapper parent class with the merged mapping
        super().__init__(mapping_config, default_values or {}, validation_rules or {})
        
        logger.debug(f"Initialized LawFirmAttorneyMapper for organization {organization_id}")
    
    def map_data(self, source_data: Dict) -> Dict:
        """
        Maps attorney data from law firm format to Justice Bid format.
        
        Args:
            source_data: Attorney data in law firm format
            
        Returns:
            Attorney data in Justice Bid format
        """
        # Call parent FieldMapper.map_data method
        mapped_data = super().map_data(source_data)
        
        # Add organization_id to the mapped data
        mapped_data['organization_id'] = self.organization_id
        
        # Apply any additional transformations specific to attorneys
        
        logger.debug(f"Mapped attorney data: {mapped_data}")
        return mapped_data
    
    def reverse_map_data(self, target_data: Dict) -> Dict:
        """
        Maps attorney data from Justice Bid format to law firm format.
        
        Args:
            target_data: Attorney data in Justice Bid format
            
        Returns:
            Attorney data in law firm format
        """
        # Remove Justice Bid specific fields not needed by law firm system
        if 'organization_id' in target_data:
            target_data = {k: v for k, v in target_data.items() if k != 'organization_id'}
        
        # Call parent FieldMapper.reverse_map_data method
        mapped_data = super().reverse_map_data(target_data)
        
        # Apply any additional transformations for the law firm format
        
        logger.debug(f"Reverse mapped attorney data for law firm: {mapped_data}")
        return mapped_data
    
    def create_attorney(self, mapped_data: Dict) -> Attorney:
        """
        Creates an Attorney model instance from mapped data.
        
        Args:
            mapped_data: Attorney data in Justice Bid format
            
        Returns:
            New Attorney instance
        """
        try:
            # Convert any string UUIDs to UUID objects
            if isinstance(mapped_data.get('id'), str):
                mapped_data['id'] = uuid.UUID(mapped_data['id'])
            
            if isinstance(mapped_data.get('organization_id'), str):
                mapped_data['organization_id'] = uuid.UUID(mapped_data['organization_id'])
            
            # Convert any date strings to date objects
            for date_field in ['bar_date', 'graduation_date', 'promotion_date']:
                if date_field in mapped_data and isinstance(mapped_data[date_field], str):
                    mapped_data[date_field] = parse_date(mapped_data[date_field])
            
            # Convert office_ids to list of UUIDs if needed
            if 'office_ids' in mapped_data and mapped_data['office_ids']:
                if isinstance(mapped_data['office_ids'][0], str):
                    mapped_data['office_ids'] = [uuid.UUID(id_str) for id_str in mapped_data['office_ids']]
            
            # Create and return a new Attorney instance using mapped_data
            attorney = Attorney.from_dict(mapped_data)
            return attorney
            
        except Exception as e:
            logger.error(f"Error creating Attorney from mapped data: {str(e)}")
            raise

class LawFirmRateMapper(FieldMapper):
    """
    Mapper for transforming rate data between law firm billing systems and Justice Bid.
    
    This class handles the transformation of rate data during import from and export to
    law firm billing systems, ensuring proper field mapping and data type conversions.
    """
    
    def __init__(self, organization_id: uuid.UUID, client_id: uuid.UUID = None, 
                 mapping_config: Dict = None, default_values: Dict = None, 
                 validation_rules: Dict = None):
        """
        Initialize the rate mapper with organization ID, client ID, and mapping configuration.
        
        Args:
            organization_id: UUID of the law firm
            client_id: UUID of the client (optional)
            mapping_config: Custom field mapping configuration
            default_values: Default values for missing fields
            validation_rules: Validation rules for fields
        """
        self.organization_id = organization_id
        self.client_id = client_id
        
        # Use default mapping if none provided, otherwise merge with default
        if mapping_config is None:
            mapping_config = DEFAULT_RATE_MAPPING
        else:
            mapping_config = create_standard_mapping('rate', mapping_config)
        
        # Initialize FieldMapper parent class with the merged mapping
        super().__init__(mapping_config, default_values or {}, validation_rules or {})
        
        logger.debug(f"Initialized LawFirmRateMapper for organization {organization_id}")
    
    def map_data(self, source_data: Dict) -> Dict:
        """
        Maps rate data from law firm format to Justice Bid format.
        
        Args:
            source_data: Rate data in law firm format
            
        Returns:
            Rate data in Justice Bid format
        """
        # Call parent FieldMapper.map_data method
        mapped_data = super().map_data(source_data)
        
        # Add organization_id as firm_id to the mapped data
        mapped_data['firm_id'] = self.organization_id
        
        # Add client_id to the mapped data if provided
        if self.client_id:
            mapped_data['client_id'] = self.client_id
        
        # Ensure rate type and status are valid enum values
        if 'type' in mapped_data and mapped_data['type'] not in RATE_TYPES:
            logger.warning(f"Invalid rate type: {mapped_data['type']}. Using default.")
            mapped_data['type'] = 'Standard'
        
        if 'status' in mapped_data and mapped_data['status'] not in RATE_STATUSES:
            logger.warning(f"Invalid rate status: {mapped_data['status']}. Using default.")
            mapped_data['status'] = 'Draft'
        
        logger.debug(f"Mapped rate data: {mapped_data}")
        return mapped_data
    
    def reverse_map_data(self, target_data: Dict) -> Dict:
        """
        Maps rate data from Justice Bid format to law firm format.
        
        Args:
            target_data: Rate data in Justice Bid format
            
        Returns:
            Rate data in law firm format
        """
        # Remove Justice Bid specific fields not needed by law firm system
        for field in ['firm_id', 'client_id']:
            if field in target_data:
                target_data = {k: v for k, v in target_data.items() if k != field}
        
        # Call parent FieldMapper.reverse_map_data method
        mapped_data = super().reverse_map_data(target_data)
        
        # Format dates according to law firm system requirements
        for date_field in ['effective_date', 'expiration_date']:
            if date_field in mapped_data and mapped_data[date_field]:
                if isinstance(mapped_data[date_field], date):
                    mapped_data[date_field] = format_date(mapped_data[date_field])
        
        logger.debug(f"Reverse mapped rate data for law firm: {mapped_data}")
        return mapped_data
    
    def create_rate(self, mapped_data: Dict) -> Rate:
        """
        Creates a Rate model instance from mapped data.
        
        Args:
            mapped_data: Rate data in Justice Bid format
            
        Returns:
            New Rate instance
        """
        try:
            # Convert any string UUIDs to UUID objects
            for uuid_field in ['id', 'attorney_id', 'client_id', 'firm_id', 'office_id', 'staff_class_id']:
                if uuid_field in mapped_data and isinstance(mapped_data[uuid_field], str):
                    mapped_data[uuid_field] = uuid.UUID(mapped_data[uuid_field])
            
            # Convert any date strings to date objects
            for date_field in ['effective_date', 'expiration_date']:
                if date_field in mapped_data and isinstance(mapped_data[date_field], str):
                    mapped_data[date_field] = parse_date(mapped_data[date_field])
            
            # Ensure all required fields are present
            required_fields = ['attorney_id', 'client_id', 'firm_id', 'office_id', 'staff_class_id', 
                              'amount', 'currency', 'effective_date']
            missing_fields = [field for field in required_fields if field not in mapped_data]
            
            if missing_fields:
                raise ValueError(f"Missing required fields for Rate: {', '.join(missing_fields)}")
            
            # Create and return a new Rate instance using mapped_data
            rate = Rate(**mapped_data)
            return rate
            
        except Exception as e:
            logger.error(f"Error creating Rate from mapped data: {str(e)}")
            raise