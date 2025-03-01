"""
Provides a common base Mapper class and utilities for mapping data between external systems and Justice Bid's internal data models.
This file is essential for integration with eBilling systems, law firm billing systems, and third-party APIs like UniCourt.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Union, Tuple, Callable
import json

from ...utils.validators import validate_field
from ...utils.logging import get_logger

# Set up logger
logger = get_logger(__name__)


def map_field(field_name: str, source_data: Dict, mapping_config: Dict, default_values: Dict) -> Any:
    """
    Maps a single field value from source to target schema based on mapping configuration.
    
    Args:
        field_name: Name of the target field
        source_data: Source data dictionary
        mapping_config: Field mapping configuration
        default_values: Default values for missing fields
        
    Returns:
        Any: Transformed field value according to mapping rules
    """
    # Get mapping configuration for this field
    field_mapping = mapping_config.get(field_name)
    if not field_mapping:
        logger.debug(f"No mapping configuration found for field '{field_name}'")
        # Return default value if available
        return default_values.get(field_name)
    
    # Extract source field name from mapping configuration
    source_field = field_mapping.get('source_field')
    if not source_field:
        logger.warning(f"Source field not defined for target field '{field_name}'")
        return default_values.get(field_name)
    
    # Get value from source data
    value = source_data.get(source_field)
    
    # Apply transformation if specified
    if 'transform' in field_mapping:
        transform_type = field_mapping['transform'].get('type')
        transform_config = field_mapping['transform'].get('config', {})
        try:
            value = apply_transformation(value, transform_type, transform_config)
        except Exception as e:
            logger.error(f"Error applying transformation to field '{field_name}': {str(e)}")
            # If transformation fails, use default value
            value = default_values.get(field_name)
    
    # Apply default value if source value is None and default exists
    if value is None and field_name in default_values:
        value = default_values[field_name]
    
    # Validate the transformed value if validation rules exist
    if 'validation' in field_mapping:
        validation_rules = field_mapping['validation']
        is_valid, error_message = validate_mapped_value(value, validation_rules)
        if not is_valid:
            logger.warning(f"Validation failed for field '{field_name}': {error_message}")
            # If validation fails, use default value
            value = default_values.get(field_name)
    
    return value


def apply_transformation(value: Any, transform_type: str, transform_config: Dict) -> Any:
    """
    Applies a transformation function to a source value.
    
    Args:
        value: Value to transform
        transform_type: Type of transformation to apply
        transform_config: Configuration for the transformation
        
    Returns:
        Any: Transformed value
    """
    if value is None:
        return None
    
    try:
        if transform_type == 'string':
            return str(value)
        elif transform_type == 'integer':
            return int(float(value)) if value else 0
        elif transform_type == 'float':
            return float(value) if value else 0.0
        elif transform_type == 'boolean':
            if isinstance(value, bool):
                return value
            if isinstance(value, str):
                return value.lower() in ('true', 'yes', 'y', '1')
            return bool(value)
        elif transform_type == 'date':
            from datetime import datetime
            date_format = transform_config.get('format', '%Y-%m-%d')
            if isinstance(value, str):
                return datetime.strptime(value, date_format).date()
            return value
        elif transform_type == 'json':
            if isinstance(value, str):
                return json.loads(value)
            return value
        elif transform_type == 'list':
            delimiter = transform_config.get('delimiter', ',')
            if isinstance(value, str):
                return [item.strip() for item in value.split(delimiter)]
            if isinstance(value, list):
                return value
            return [value] if value is not None else []
        elif transform_type == 'uppercase':
            return str(value).upper() if value else ''
        elif transform_type == 'lowercase':
            return str(value).lower() if value else ''
        elif transform_type == 'replace':
            old = transform_config.get('old', '')
            new = transform_config.get('new', '')
            return str(value).replace(old, new) if value else ''
        elif transform_type == 'format':
            format_string = transform_config.get('format', '{}')
            return format_string.format(value) if value is not None else ''
        elif transform_type == 'map':
            mapping = transform_config.get('mapping', {})
            return mapping.get(str(value), value)
        elif transform_type == 'default':
            default = transform_config.get('default')
            return value if value is not None else default
        elif transform_type == 'custom':
            # Custom transformations would be implemented in subclasses
            logger.warning(f"Custom transformation requested but not implemented")
            return value
        else:
            logger.warning(f"Unknown transformation type: '{transform_type}'")
            return value
    except Exception as e:
        logger.error(f"Error in '{transform_type}' transformation: {str(e)}")
        raise


def validate_mapped_value(value: Any, validation_rules: Dict) -> Tuple[bool, Optional[str]]:
    """
    Validates a mapped value against specified validation rules.
    
    Args:
        value: Value to validate
        validation_rules: Dictionary of validation rules
        
    Returns:
        Tuple containing (is_valid: bool, error_message: str)
    """
    if not validation_rules:
        return True, None
    
    for rule_name, rule_config in validation_rules.items():
        try:
            # Call appropriate validator function from utils.validators
            if not validate_field(value, rule_name, rule_config):
                return False, f"Failed validation rule: {rule_name}"
        except Exception as e:
            return False, str(e)
    
    return True, None


class Mapper(ABC):
    """
    Abstract base class defining the interface for data mappers between external systems and Justice Bid.
    
    This class provides the core functionality for mapping data between external sources and the
    Justice Bid internal data model, with support for validation and transformation.
    """
    
    def __init__(self, mapping_config: Dict, default_values: Dict = None, validation_rules: Dict = None):
        """
        Initialize a new Mapper instance with provided configuration.
        
        Args:
            mapping_config: Dictionary defining field mappings between source and target
            default_values: Dictionary of default values for fields
            validation_rules: Dictionary of validation rules for fields
        """
        self.mapping_config = mapping_config
        self.default_values = default_values or {}
        self.validation_rules = validation_rules or {}
        self.logger = logger  # Use the module-level logger
        
        # Validate mapping configuration
        self.validate_mapping()
    
    @abstractmethod
    def map_data(self, source_data: Dict) -> Dict:
        """
        Maps data from source format to target format using the configured mappings.
        
        Args:
            source_data: Data in source format
            
        Returns:
            Dict: Mapped data in target format
        """
        pass
    
    @abstractmethod
    def reverse_map_data(self, target_data: Dict) -> Dict:
        """
        Maps data from target format back to source format.
        
        Args:
            target_data: Data in target format
            
        Returns:
            Dict: Mapped data in source format
        """
        pass
    
    def validate_mapping(self) -> bool:
        """
        Validates the mapping configuration for consistency and correctness.
        
        Returns:
            bool: True if mapping configuration is valid, False otherwise
        """
        if not isinstance(self.mapping_config, dict):
            logger.error("Mapping configuration must be a dictionary")
            return False
        
        # Check that all field mappings have source_field defined
        for field_name, field_mapping in self.mapping_config.items():
            if not isinstance(field_mapping, dict):
                logger.error(f"Mapping for field '{field_name}' must be a dictionary")
                return False
            
            if 'source_field' not in field_mapping:
                logger.error(f"Mapping for field '{field_name}' is missing 'source_field'")
                return False
            
            # Validate transformation configuration if present
            if 'transform' in field_mapping:
                transform = field_mapping['transform']
                if not isinstance(transform, dict):
                    logger.error(f"Transform for field '{field_name}' must be a dictionary")
                    return False
                
                if 'type' not in transform:
                    logger.error(f"Transform for field '{field_name}' is missing 'type'")
                    return False
        
        return True
    
    def get_field_mapping(self, field_name: str) -> Optional[Dict]:
        """
        Gets the mapping configuration for a specific field.
        
        Args:
            field_name: Name of the field
            
        Returns:
            Dict or None: Mapping configuration for the specified field
        """
        return self.mapping_config.get(field_name)


class FieldMapper(Mapper):
    """
    Concrete implementation of Mapper for field-by-field mapping with transformations.
    
    This class provides a field-by-field mapping implementation that can be used for
    most integration scenarios where there's a direct mapping between fields.
    """
    
    def __init__(self, mapping_config: Dict, default_values: Dict = None, validation_rules: Dict = None):
        """
        Initialize a new FieldMapper instance.
        
        Args:
            mapping_config: Dictionary defining field mappings between source and target
            default_values: Dictionary of default values for fields
            validation_rules: Dictionary of validation rules for fields
        """
        super().__init__(mapping_config, default_values, validation_rules)
    
    def map_data(self, source_data: Dict) -> Dict:
        """
        Maps data from source format to target format using field mappings.
        
        Args:
            source_data: Data in source format
            
        Returns:
            Dict: Mapped data in target format
        """
        if not source_data:
            logger.warning("Empty source data provided for mapping")
            return {}
        
        result = {}
        
        for field_name in self.mapping_config:
            try:
                mapped_value = map_field(field_name, source_data, self.mapping_config, self.default_values)
                # Only include non-None values in the result
                if mapped_value is not None:
                    result[field_name] = mapped_value
            except Exception as e:
                self.handle_mapping_error(field_name, e, False)
        
        # Apply any default values for fields that aren't in the result
        for field_name, default_value in self.default_values.items():
            if field_name not in result:
                result[field_name] = default_value
        
        return result
    
    def reverse_map_data(self, target_data: Dict) -> Dict:
        """
        Maps data from target format back to source format.
        
        Args:
            target_data: Data in target format
            
        Returns:
            Dict: Mapped data in source format
        """
        if not target_data:
            logger.warning("Empty target data provided for reverse mapping")
            return {}
        
        result = {}
        
        # Create a reverse mapping dictionary (target_field -> source_field)
        reverse_mapping = {}
        for target_field, mapping in self.mapping_config.items():
            source_field = mapping.get('source_field')
            if source_field:
                reverse_mapping[target_field] = source_field
        
        # Apply the reverse mapping
        for target_field, value in target_data.items():
            if target_field in reverse_mapping:
                source_field = reverse_mapping[target_field]
                
                # Apply reverse transformation if needed (not implemented in this version)
                # This would require additional configuration for bidirectional transformations
                
                result[source_field] = value
            else:
                # If no mapping exists, keep the original field name
                result[target_field] = value
        
        return result
    
    def handle_mapping_error(self, field_name: str, error: Exception, raise_exception: bool = False) -> None:
        """
        Handles errors that occur during mapping operations.
        
        Args:
            field_name: Name of the field where the error occurred
            error: The exception that was raised
            raise_exception: Whether to re-raise the exception
            
        Returns:
            None
        """
        error_message = f"Error mapping field '{field_name}': {str(error)}"
        logger.error(error_message)
        
        if raise_exception:
            raise type(error)(error_message) from error