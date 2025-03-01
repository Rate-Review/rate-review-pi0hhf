"""
Initialization file for the file integration module that serves as the entry point for file-based imports and exports.
Exposes key classes and functions for processing CSV and Excel files and provides a unified adapter for file-based data exchange in the Justice Bid Rate Negotiation System.
"""

from .validators import FileValidator  # internal
from .csv_processor import CSVProcessor  # internal
from .excel_processor import ExcelProcessor  # internal
from ..common.adapter import BaseAPIAdapter  # internal
from ..common.mapper import FieldMapper  # internal
from '../../utils/logging' import get_logger  # internal

# Initialize logger
logger = get_logger(__name__)

# Define supported file formats
SUPPORTED_FILE_FORMATS = {'csv', 'xlsx', 'xls'}


class FileIntegrationAdapter(BaseAPIAdapter):
    """
    Adapter class for file-based integrations that handles file processing and data transformation.
    """

    def __init__(self, file_path: str, file_format: str, mapping_config: dict):
        """
        Initializes the file integration adapter with the specified file path, format, and mapping configuration.

        Args:
            file_path (str): Path to the file to be processed.
            file_format (str): Format of the file (e.g., 'csv', 'xlsx').
            mapping_config (dict): Configuration for mapping fields from the file to internal data structures.
        """
        # IE1: Call the parent constructor (BaseAPIAdapter)
        super().__init__(
            name="FileIntegration",
            integration_type="file",
            base_url="",  # No base URL for file-based integrations
            auth_credentials={},  # No authentication for file-based integrations
        )

        # LD1: Store the file_path parameter
        self.file_path = file_path
        # LD1: Store the file_format parameter (or detect from file extension if not provided)
        self.file_format = file_format
        # LD1: Store the mapping_config parameter
        self.mapping_config = mapping_config

        # LD1: Initialize the mapper with the mapping configuration
        self.mapper = FieldMapper(self.mapping_config)

        # LD1: Select the appropriate processor (CSVProcessor or ExcelProcessor) based on file_format
        if self.file_format == 'csv':
            self.processor = CSVProcessor()
        elif self.file_format in ('xlsx', 'xls'):
            self.processor = ExcelProcessor()
        else:
            raise ValueError(f"Unsupported file format: {self.file_format}")

        # LD1: Initialize the processor
        logger.info(f"Initialized FileIntegrationAdapter for {self.file_path} with format {self.file_format}")

    def validate_file(self) -> bool:
        """
        Validates the file format and content using the FileValidator.

        Returns:
            bool: True if the file is valid, False otherwise
        """
        # LD1: Create a FileValidator instance
        validator = FileValidator()
        # LD1: Call the validate method on the validator with the file_path
        try:
            validation_result = validator.validate_file(self.file_path, file_type=self.file_format)
            # LD1: Return the validation result
            return validation_result['valid']
        except Exception as e:
            logger.error(f"File validation failed: {str(e)}")
            return False

    def import_data(self, validation_rules: dict, options: dict) -> tuple:
        """
        Imports data from the file using the appropriate processor and mapper.

        Args:
            validation_rules (dict): Rules for validating the data being imported.
            options (dict): Options to configure the import process.

        Returns:
            tuple: (pandas.DataFrame, dict) - Processed data and validation details
        """
        # LD1: Validate the file using validate_file method
        if not self.validate_file():
            raise Exception("File validation failed")

        # LD1: Determine import type based on file content or options
        import_type = options.get('import_type', 'generic')

        # LD1: Call the appropriate processor's process_import method
        if self.file_format == 'csv':
            processed_data = self.processor.process_import(self.file_path, is_content=False, validation_schema=validation_rules, field_mapping=self.mapping_config)
        elif self.file_format in ('xlsx', 'xls'):
            processed_data = self.processor.process_import(self.file_path, sheet_name=options.get('sheet_name'), import_type=import_type, field_mapping=self.mapping_config, validation_rules=validation_rules)
        else:
            raise ValueError(f"Unsupported file format: {self.file_format}")

        # LD1: Apply mapping transformation using the mapper
        # This step is already included in the processor's process_import method

        # LD1: Return the processed data and validation details
        return processed_data['data'], {'validation_results': processed_data.get('errors', [])}

    def export_data(self, df, export_type: str, output_path: str, options: dict) -> str:
        """
        Exports data to a file using the appropriate processor and mapper.

        Args:
            df (pandas.DataFrame): Data to export.
            export_type (str): Type of export (e.g., 'csv', 'xlsx').
            output_path (str): Path to the output file.
            options (dict): Options to configure the export process.

        Returns:
            str: Path to the exported file
        """
        # LD1: Determine the file format from output_path extension
        file_format = get_file_extension(output_path)

        # LD1: Transform the data using the mapper
        # This step is not needed as the data is already a pandas DataFrame

        # LD1: Select the appropriate processor based on file format
        if file_format == 'csv':
            # LD1: Call the processor's process_export method
            self.processor.process_export(df.to_dict(orient='records'), field_mapping=self.mapping_config, delimiter=options.get('delimiter', ','))
        elif file_format in ('xlsx', 'xls'):
            # LD1: Call the processor's process_export method
            self.processor.process_export(df.to_dict(orient='records'), file_path=output_path, sheet_name=options.get('sheet_name'), field_mapping=self.mapping_config, style_options=options.get('style_options'))
        else:
            raise ValueError(f"Unsupported file format: {file_format}")

        # LD1: Return the path to the exported file
        return output_path

    def generate_template(self, import_type: str, output_path: str, options: dict) -> str:
        """
        Generates a template file for data import.

        Args:
            import_type (str): Type of import (e.g., 'rate', 'attorney', 'billing').
            output_path (str): Path to the output file.
            options (dict): Options to configure the template generation process.

        Returns:
            str: Path to the generated template
        """
        # LD1: Determine the file format from output_path extension
        file_format = get_file_extension(output_path)

        # LD1: Select the appropriate processor based on file format
        if file_format == 'csv':
            # LD1: Call the processor's generate_template method
            template_content = self.processor.create_template(required_fields=[], optional_fields=[], delimiter=options.get('delimiter', ','))
            # Save the template content to the output path
            with open(output_path, 'w') as f:
                f.write(template_content)
        elif file_format in ('xlsx', 'xls'):
            # LD1: Call the processor's generate_template method
            self.processor.create_template(file_path=output_path, import_type=import_type, include_sample_data=options.get('include_sample_data', False), style_options=options.get('style_options'))
        else:
            raise ValueError(f"Unsupported file format: {file_format}")

        # LD1: Return the path to the generated template
        return output_path

    def authenticate(self) -> bool:
        """
        Authenticates with the external system.

        Returns:
            bool: True if authentication is successful, False otherwise
        """
        # No authentication needed for file-based integrations
        return True

    def validate_connection(self) -> bool:
        """
        Validates the connection to the external system.

        Returns:
            bool: True if connection is valid, False otherwise
        """
        # No connection validation needed for file-based integrations
        return True

    def get_data(self, data_type: str, params: dict = None, headers: dict = None) -> dict:
        """
        Retrieves data from the external system.

        Args:
            data_type (str): Type of data to retrieve (e.g., 'rates', 'attorneys').
            params (dict, optional): Query parameters for the request. Defaults to None.
            headers (dict, optional): Additional headers for the request. Defaults to None.

        Returns:
            dict: Retrieved data, mapped to Justice Bid format
        """
        raise NotImplementedError("get_data is not supported for file-based integrations")

    def send_data(self, data_type: str, data: dict, params: dict = None, headers: dict = None) -> dict:
        """
        Sends data to the external system.

        Args:
            data_type (str): Type of data to send (e.g., 'rates', 'attorneys').
            data (dict): Data to send in Justice Bid format.
            params (dict, optional): Query parameters for the request. Defaults to None.
            headers (dict, optional): Additional headers for the request. Defaults to None.

        Returns:
            dict: Response from the external system
        """
        raise NotImplementedError("send_data is not supported for file-based integrations")

    def map_data(self, data: dict, direction: str, data_type: str) -> dict:
        """
        Maps data between external system format and Justice Bid format.

        Args:
            data (dict): Data to map.
            direction (str): Direction of mapping ('to_external' or 'to_internal').
            data_type (str): Type of data being mapped.

        Returns:
            dict: Mapped data in target format
        """
        raise NotImplementedError("map_data is not supported, use FieldMapper directly")


# IE3: Expose file validation utilities
# IE3: Expose CSV file processing
# IE3: Expose Excel file processing
# IE3: Expose adapter for file integrations
# IE3: Expose the list of supported file formats
__all__ = [
    "FileValidator",
    "CSVProcessor",
    "ExcelProcessor",
    "FileIntegrationAdapter",
    "SUPPORTED_FILE_FORMATS"
]