"""
Defines the abstract Adapter pattern interface and base implementation for third-party system integrations.
Provides a standardized way to connect, authenticate, retrieve, and send data to external systems like
eBilling platforms, law firm billing systems, and UniCourt.
"""

import abc
from typing import Any, Dict, List, Optional, Union, Tuple
import json
import os

from .client import BaseIntegrationClient
from .mapper import Mapper
from ...utils.logging import get_logger
from ...utils.constants import IntegrationType

# Set up logger
logger = get_logger(__name__)

def create_adapter(integration_type: str, config: Dict) -> 'APIAdapter':
    """
    Factory function that creates and returns an appropriate adapter instance based on integration type.
    
    Args:
        integration_type: Type of integration (e.g., 'onit', 'teamconnect', 'unicourt')
        config: Configuration dictionary with connection parameters
        
    Returns:
        APIAdapter: An initialized adapter instance for the specified integration type
        
    Raises:
        ValueError: If the integration type is not supported
    """
    # Validate integration type
    try:
        integration_enum = IntegrationType(integration_type)
    except ValueError:
        supported_types = [t.value for t in IntegrationType]
        error_msg = f"Unsupported integration type: {integration_type}. Supported types: {', '.join(supported_types)}"
        logger.error(error_msg)
        raise ValueError(error_msg)
    
    # Extract common configuration parameters
    base_url = config.get('base_url')
    auth_credentials = config.get('auth_credentials', {})
    headers = config.get('headers', {})
    timeout = config.get('timeout', 30)
    verify_ssl = config.get('verify_ssl', True)
    
    # Create the appropriate adapter based on integration type
    if integration_type == IntegrationType.ONIT.value:
        from ..ebilling.onit_adapter import OnitAdapter
        return OnitAdapter(
            name="Onit",
            integration_type=integration_type,
            base_url=base_url,
            auth_credentials=auth_credentials,
            headers=headers,
            timeout=timeout,
            verify_ssl=verify_ssl
        )
    elif integration_type == IntegrationType.TEAMCONNECT.value:
        from ..ebilling.teamconnect_adapter import TeamConnectAdapter
        return TeamConnectAdapter(
            name="TeamConnect",
            integration_type=integration_type,
            base_url=base_url,
            auth_credentials=auth_credentials,
            headers=headers,
            timeout=timeout,
            verify_ssl=verify_ssl
        )
    elif integration_type == IntegrationType.LEGAL_TRACKER.value:
        from ..ebilling.legal_tracker_adapter import LegalTrackerAdapter
        return LegalTrackerAdapter(
            name="Legal Tracker",
            integration_type=integration_type,
            base_url=base_url,
            auth_credentials=auth_credentials,
            headers=headers,
            timeout=timeout,
            verify_ssl=verify_ssl
        )
    elif integration_type == IntegrationType.BRIGHTFLAG.value:
        from ..ebilling.brightflag_adapter import BrightflagAdapter
        return BrightflagAdapter(
            name="Brightflag",
            integration_type=integration_type,
            base_url=base_url,
            auth_credentials=auth_credentials,
            headers=headers,
            timeout=timeout,
            verify_ssl=verify_ssl
        )
    elif integration_type == IntegrationType.LAW_FIRM.value:
        from ..lawfirm.lawfirm_adapter import LawFirmAdapter
        return LawFirmAdapter(
            name="Law Firm",
            integration_type=integration_type,
            base_url=base_url,
            auth_credentials=auth_credentials,
            headers=headers,
            timeout=timeout,
            verify_ssl=verify_ssl
        )
    elif integration_type == IntegrationType.UNICOURT.value:
        from ..unicourt.unicourt_adapter import UniCourtAdapter
        return UniCourtAdapter(
            name="UniCourt",
            integration_type=integration_type,
            base_url=base_url,
            auth_credentials=auth_credentials,
            headers=headers,
            timeout=timeout,
            verify_ssl=verify_ssl
        )
    else:
        error_msg = f"No adapter implementation for integration type: {integration_type}"
        logger.error(error_msg)
        raise ValueError(error_msg)


class APIAdapter(abc.ABC):
    """
    Abstract base class for all integration adapters, defining the common interface.
    
    This class provides the interface that all specific adapters must implement to
    ensure consistent behavior across different third-party integrations.
    """
    
    @abc.abstractmethod
    def __init__(
        self, 
        name: str, 
        integration_type: str,
        base_url: str,
        auth_credentials: Dict,
        headers: Dict = None,
        timeout: int = 30,
        verify_ssl: bool = True
    ):
        """
        Initialize the adapter with connection parameters.
        
        Args:
            name: Human-readable name for the adapter
            integration_type: Type of integration (e.g., 'onit', 'teamconnect')
            base_url: Base URL for the external API
            auth_credentials: Authentication credentials (API keys, tokens, etc.)
            headers: Additional HTTP headers to include in requests
            timeout: Request timeout in seconds
            verify_ssl: Whether to verify SSL certificates
        """
        self.name = name
        self.integration_type = integration_type
        self.base_url = base_url
        self.auth_credentials = auth_credentials
        self.headers = headers or {}
        self.timeout = timeout
        self.verify_ssl = verify_ssl
        
        # Validate required parameters
        if not self.name:
            raise ValueError("Adapter name is required")
        if not self.integration_type:
            raise ValueError("Integration type is required")
        if not self.base_url:
            raise ValueError("Base URL is required")
        
        # Set up logger for this adapter instance
        self.logger = logger
        
        # Initialize client and mapper as None (to be set by subclasses)
        self.client = None
        self.mapper = None
    
    @abc.abstractmethod
    def authenticate(self) -> bool:
        """
        Authenticate with the external system.
        
        Returns:
            bool: True if authentication is successful, False otherwise
        """
        pass
    
    @abc.abstractmethod
    def validate_connection(self) -> bool:
        """
        Validate the connection to the external system.
        
        Returns:
            bool: True if connection is valid, False otherwise
        """
        pass
    
    @abc.abstractmethod
    def get_data(self, data_type: str, params: Dict = None, headers: Dict = None) -> Dict:
        """
        Retrieve data from the external system.
        
        Args:
            data_type: Type of data to retrieve (e.g., 'rates', 'attorneys')
            params: Query parameters for the request
            headers: Additional headers for the request
            
        Returns:
            Dict: Retrieved data, mapped to Justice Bid format
        """
        pass
    
    @abc.abstractmethod
    def send_data(self, data_type: str, data: Dict, params: Dict = None, headers: Dict = None) -> Dict:
        """
        Send data to the external system.
        
        Args:
            data_type: Type of data to send (e.g., 'rates', 'attorneys')
            data: Data to send in Justice Bid format
            params: Query parameters for the request
            headers: Additional headers for the request
            
        Returns:
            Dict: Response from the external system
        """
        pass
    
    @abc.abstractmethod
    def map_data(self, data: Dict, direction: str, data_type: str) -> Dict:
        """
        Map data between external system format and Justice Bid format.
        
        Args:
            data: Data to map
            direction: Direction of mapping ('to_external' or 'to_internal')
            data_type: Type of data being mapped
            
        Returns:
            Dict: Mapped data in target format
        """
        pass
    
    def import_file(self, file_path: str, data_type: str, mapping_config: Dict) -> Tuple[bool, str, List]:
        """
        Import data from a file exported from the external system.
        
        Args:
            file_path: Path to the file to import
            data_type: Type of data contained in the file (e.g., 'rates', 'attorneys')
            mapping_config: Configuration for mapping fields from file to internal format
            
        Returns:
            Tuple[bool, str, List]: Success flag, message, and imported data
        """
        # Check if file exists and is readable
        if not os.path.exists(file_path):
            error_msg = f"File does not exist: {file_path}"
            self.logger.error(error_msg)
            return False, error_msg, []
        
        if not os.access(file_path, os.R_OK):
            error_msg = f"File is not readable: {file_path}"
            self.logger.error(error_msg)
            return False, error_msg, []
        
        # Determine file format based on extension
        _, file_extension = os.path.splitext(file_path)
        file_extension = file_extension.lower()
        
        try:
            # Read file based on extension
            if file_extension == '.csv':
                import csv
                with open(file_path, 'r', newline='', encoding='utf-8') as file:
                    reader = csv.DictReader(file)
                    data = list(reader)
            elif file_extension in ['.xlsx', '.xls']:
                import pandas as pd
                df = pd.read_excel(file_path)
                data = df.to_dict('records')
            elif file_extension == '.json':
                with open(file_path, 'r', encoding='utf-8') as file:
                    data = json.load(file)
            else:
                error_msg = f"Unsupported file format: {file_extension}"
                self.logger.error(error_msg)
                return False, error_msg, []
            
            # Map data to internal format using mapping_config
            mapped_data = []
            for record in data:
                try:
                    mapped_record = self.map_data(record, 'to_internal', data_type)
                    mapped_data.append(mapped_record)
                except Exception as e:
                    self.logger.warning(f"Error mapping record: {str(e)}")
                    continue
            
            success_msg = f"Successfully imported {len(mapped_data)} records from {file_path}"
            self.logger.info(success_msg)
            return True, success_msg, mapped_data
            
        except Exception as e:
            error_msg = f"Error importing file {file_path}: {str(e)}"
            self.logger.error(error_msg)
            return False, error_msg, []
    
    def export_file(self, file_path: str, data_type: str, data: List, mapping_config: Dict) -> Tuple[bool, str]:
        """
        Export data to a file for import into the external system.
        
        Args:
            file_path: Path to save the exported file
            data_type: Type of data to export (e.g., 'rates', 'attorneys')
            data: Data to export in Justice Bid format
            mapping_config: Configuration for mapping fields from internal to file format
            
        Returns:
            Tuple[bool, str]: Success flag and message
        """
        # Determine output format based on file extension
        _, file_extension = os.path.splitext(file_path)
        file_extension = file_extension.lower()
        
        try:
            # Map data to external format using mapping_config
            mapped_data = []
            for record in data:
                try:
                    mapped_record = self.map_data(record, 'to_external', data_type)
                    mapped_data.append(mapped_record)
                except Exception as e:
                    self.logger.warning(f"Error mapping record: {str(e)}")
                    continue
            
            # Write to file based on extension
            if file_extension == '.csv':
                import csv
                if not mapped_data:
                    error_msg = "No data to export"
                    self.logger.error(error_msg)
                    return False, error_msg
                
                with open(file_path, 'w', newline='', encoding='utf-8') as file:
                    writer = csv.DictWriter(file, fieldnames=mapped_data[0].keys())
                    writer.writeheader()
                    writer.writerows(mapped_data)
            elif file_extension in ['.xlsx', '.xls']:
                import pandas as pd
                df = pd.DataFrame(mapped_data)
                df.to_excel(file_path, index=False)
            elif file_extension == '.json':
                with open(file_path, 'w', encoding='utf-8') as file:
                    json.dump(mapped_data, file, indent=2)
            else:
                error_msg = f"Unsupported file format: {file_extension}"
                self.logger.error(error_msg)
                return False, error_msg
            
            success_msg = f"Successfully exported {len(mapped_data)} records to {file_path}"
            self.logger.info(success_msg)
            return True, success_msg
            
        except Exception as e:
            error_msg = f"Error exporting to file {file_path}: {str(e)}"
            self.logger.error(error_msg)
            return False, error_msg


class BaseAPIAdapter(APIAdapter):
    """
    Base implementation of APIAdapter providing common functionality for concrete adapters.
    
    This class provides common implementations for file import/export and other shared
    functionality that can be inherited by specific adapters.
    """
    
    def __init__(
        self, 
        name: str, 
        integration_type: str,
        base_url: str,
        auth_credentials: Dict,
        headers: Dict = None,
        timeout: int = 30,
        verify_ssl: bool = True
    ):
        """
        Initialize the base adapter with connection parameters.
        
        Args:
            name: Human-readable name for the adapter
            integration_type: Type of integration (e.g., 'onit', 'teamconnect')
            base_url: Base URL for the external API
            auth_credentials: Authentication credentials (API keys, tokens, etc.)
            headers: Additional HTTP headers to include in requests
            timeout: Request timeout in seconds
            verify_ssl: Whether to verify SSL certificates
        """
        super().__init__(
            name=name,
            integration_type=integration_type,
            base_url=base_url,
            auth_credentials=auth_credentials,
            headers=headers,
            timeout=timeout,
            verify_ssl=verify_ssl
        )
        
        # Initialize client and mapper as None (to be set by subclasses)
        self.client = None
        self.mapper = None
    
    def import_file(self, file_path: str, data_type: str, mapping_config: Dict) -> Tuple[bool, str, List]:
        """
        Common implementation of file import functionality.
        
        Args:
            file_path: Path to the file to import
            data_type: Type of data contained in the file
            mapping_config: Configuration for mapping fields from file to internal format
            
        Returns:
            Tuple[bool, str, List]: Success flag, message, and imported data
        """
        # Check if file exists and is readable
        if not os.path.exists(file_path):
            error_msg = f"File does not exist: {file_path}"
            self.logger.error(error_msg)
            return False, error_msg, []
        
        if not os.access(file_path, os.R_OK):
            error_msg = f"File is not readable: {file_path}"
            self.logger.error(error_msg)
            return False, error_msg, []
        
        try:
            # Determine file format based on extension and read file
            _, file_extension = os.path.splitext(file_path)
            file_extension = file_extension.lower()
            
            if file_extension == '.csv':
                data = self.read_csv_file(file_path)
            elif file_extension in ['.xlsx', '.xls']:
                data = self.read_excel_file(file_path)
            elif file_extension == '.json':
                with open(file_path, 'r', encoding='utf-8') as file:
                    data = json.load(file)
            else:
                error_msg = f"Unsupported file format: {file_extension}"
                self.logger.error(error_msg)
                return False, error_msg, []
            
            if not data:
                error_msg = f"No data found in file: {file_path}"
                self.logger.error(error_msg)
                return False, error_msg, []
            
            # Apply mapping to transform data to Justice Bid format
            mapped_data = []
            error_count = 0
            
            for record in data:
                try:
                    if self.mapper:
                        # Use the adapter's mapper if available
                        mapped_record = self.mapper.map_data(record)
                    else:
                        # Use generic mapping based on mapping_config
                        mapped_record = {}
                        for target_field, source_config in mapping_config.items():
                            source_field = source_config.get('source_field')
                            if source_field and source_field in record:
                                mapped_record[target_field] = record[source_field]
                    
                    mapped_data.append(mapped_record)
                except Exception as e:
                    self.logger.warning(f"Error mapping record: {str(e)}")
                    error_count += 1
            
            if error_count:
                warning_msg = f"Successfully imported {len(mapped_data)} records from {file_path} with {error_count} errors"
                self.logger.warning(warning_msg)
                return True, warning_msg, mapped_data
            else:
                success_msg = f"Successfully imported {len(mapped_data)} records from {file_path}"
                self.logger.info(success_msg)
                return True, success_msg, mapped_data
            
        except Exception as e:
            error_msg = f"Error importing file {file_path}: {str(e)}"
            self.logger.error(error_msg)
            return False, error_msg, []
    
    def export_file(self, file_path: str, data_type: str, data: List, mapping_config: Dict) -> Tuple[bool, str]:
        """
        Common implementation of file export functionality.
        
        Args:
            file_path: Path to save the exported file
            data_type: Type of data to export
            data: Data to export in Justice Bid format
            mapping_config: Configuration for mapping fields from internal to file format
            
        Returns:
            Tuple[bool, str]: Success flag and message
        """
        try:
            # Map data to external format
            mapped_data = []
            
            for record in data:
                try:
                    if self.mapper:
                        # Use the adapter's mapper if available
                        mapped_record = self.mapper.reverse_map_data(record)
                    else:
                        # Use generic mapping based on mapping_config
                        mapped_record = {}
                        for target_field, source_config in mapping_config.items():
                            source_field = source_config.get('source_field')
                            if source_field and source_field in record:
                                mapped_record[source_field] = record[target_field]
                    
                    mapped_data.append(mapped_record)
                except Exception as e:
                    self.logger.warning(f"Error mapping record for export: {str(e)}")
                    continue
            
            if not mapped_data:
                error_msg = "No data to export after mapping"
                self.logger.error(error_msg)
                return False, error_msg
            
            # Determine output format based on file extension and write file
            _, file_extension = os.path.splitext(file_path)
            file_extension = file_extension.lower()
            
            if file_extension == '.csv':
                success = self.write_csv_file(file_path, mapped_data)
            elif file_extension in ['.xlsx', '.xls']:
                success = self.write_excel_file(file_path, mapped_data)
            elif file_extension == '.json':
                with open(file_path, 'w', encoding='utf-8') as file:
                    json.dump(mapped_data, file, indent=2)
                success = True
            else:
                error_msg = f"Unsupported file format: {file_extension}"
                self.logger.error(error_msg)
                return False, error_msg
            
            if success:
                success_msg = f"Successfully exported {len(mapped_data)} records to {file_path}"
                self.logger.info(success_msg)
                return True, success_msg
            else:
                error_msg = f"Failed to export data to {file_path}"
                self.logger.error(error_msg)
                return False, error_msg
            
        except Exception as e:
            error_msg = f"Error exporting to file {file_path}: {str(e)}"
            self.logger.error(error_msg)
            return False, error_msg
    
    def read_csv_file(self, file_path: str) -> List[Dict]:
        """
        Helper method to read and parse CSV files.
        
        Args:
            file_path: Path to the CSV file
            
        Returns:
            List[Dict]: List of dictionaries representing the CSV rows
        """
        import csv
        
        try:
            with open(file_path, 'r', newline='', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                return list(reader)
        except Exception as e:
            self.logger.error(f"Error reading CSV file {file_path}: {str(e)}")
            raise
    
    def read_excel_file(self, file_path: str) -> List[Dict]:
        """
        Helper method to read and parse Excel files.
        
        Args:
            file_path: Path to the Excel file
            
        Returns:
            List[Dict]: List of dictionaries representing the Excel rows
        """
        try:
            import pandas as pd
            df = pd.read_excel(file_path)
            return df.to_dict('records')
        except Exception as e:
            self.logger.error(f"Error reading Excel file {file_path}: {str(e)}")
            raise
    
    def write_csv_file(self, file_path: str, data: List[Dict]) -> bool:
        """
        Helper method to write data to a CSV file.
        
        Args:
            file_path: Path to the CSV file to write
            data: List of dictionaries to write as CSV rows
            
        Returns:
            bool: True if successful, False otherwise
        """
        import csv
        
        try:
            if not data:
                return False
            
            with open(file_path, 'w', newline='', encoding='utf-8') as file:
                writer = csv.DictWriter(file, fieldnames=data[0].keys())
                writer.writeheader()
                writer.writerows(data)
            
            return True
        except Exception as e:
            self.logger.error(f"Error writing CSV file {file_path}: {str(e)}")
            return False
    
    def write_excel_file(self, file_path: str, data: List[Dict]) -> bool:
        """
        Helper method to write data to an Excel file.
        
        Args:
            file_path: Path to the Excel file to write
            data: List of dictionaries to write as Excel rows
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            import pandas as pd
            
            if not data:
                return False
            
            df = pd.DataFrame(data)
            df.to_excel(file_path, index=False)
            
            return True
        except Exception as e:
            self.logger.error(f"Error writing Excel file {file_path}: {str(e)}")
            return False