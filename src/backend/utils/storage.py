import boto3  # boto3 v1.26.0
import botocore  # botocore v1.29.0
import os
import uuid
import datetime
import mimetypes
import logging
from typing import Dict, List, Union, Optional, BinaryIO, Any, Tuple

logger = logging.getLogger(__name__)

class StorageClient:
    """Base class for storage backend implementations providing a consistent interface."""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize the storage client with configuration.
        
        Args:
            config: Configuration dictionary for the storage client
        """
        self.config = config
    
    def upload_file(self, file_data: Union[bytes, str, BinaryIO], destination_path: str, 
                   content_type: Optional[str] = None, metadata: Optional[Dict[str, str]] = None) -> str:
        """Abstract method to upload a file.
        
        Args:
            file_data: The file data to upload (bytes, string, or file-like object)
            destination_path: The path where the file should be stored
            content_type: The MIME type of the file (optional)
            metadata: Additional metadata to store with the file (optional)
            
        Returns:
            URL or path to the uploaded file
        """
        raise NotImplementedError("Subclasses must implement upload_file")
    
    def download_file(self, file_path: str, local_path: Optional[str] = None) -> Union[bytes, str]:
        """Abstract method to download a file.
        
        Args:
            file_path: Path to the file in the storage backend
            local_path: Local path where the file should be saved (optional)
            
        Returns:
            File data (if local_path is None) or path to the downloaded file
        """
        raise NotImplementedError("Subclasses must implement download_file")
    
    def delete_file(self, file_path: str) -> bool:
        """Abstract method to delete a file.
        
        Args:
            file_path: Path to the file in the storage backend
            
        Returns:
            Success status
        """
        raise NotImplementedError("Subclasses must implement delete_file")
    
    def list_files(self, directory_path: str, prefix: Optional[str] = None, 
                  recursive: Optional[bool] = False) -> List[str]:
        """Abstract method to list files.
        
        Args:
            directory_path: Path to the directory in the storage backend
            prefix: Filter files by this prefix (optional)
            recursive: If True, include files in subdirectories (optional)
            
        Returns:
            List of file paths
        """
        raise NotImplementedError("Subclasses must implement list_files")
    
    def get_file_metadata(self, file_path: str) -> Dict[str, Any]:
        """Abstract method to get file metadata.
        
        Args:
            file_path: Path to the file in the storage backend
            
        Returns:
            File metadata
        """
        raise NotImplementedError("Subclasses must implement get_file_metadata")
    
    def check_file_exists(self, file_path: str) -> bool:
        """Abstract method to check if a file exists.
        
        Args:
            file_path: Path to the file in the storage backend
            
        Returns:
            True if file exists, False otherwise
        """
        raise NotImplementedError("Subclasses must implement check_file_exists")
    
    def generate_presigned_url(self, file_path: str, expiration_seconds: int, 
                              http_method: str = 'GET') -> str:
        """Abstract method to generate a pre-signed URL.
        
        Args:
            file_path: Path to the file in the storage backend
            expiration_seconds: Number of seconds until the URL expires
            http_method: HTTP method allowed for the URL (optional)
            
        Returns:
            Pre-signed URL
        """
        raise NotImplementedError("Subclasses must implement generate_presigned_url")


class S3StorageClient(StorageClient):
    """AWS S3 implementation of the storage client."""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize the S3 storage client.
        
        Args:
            config: Configuration dictionary containing S3-specific settings
                   (bucket_name, region_name, aws_access_key_id, aws_secret_access_key)
        """
        super().__init__(config)
        self.bucket_name = config.get('bucket_name')
        self.region_name = config.get('region_name', 'us-east-1')
        
        if not self.bucket_name:
            raise ValueError("S3 bucket name is required in config")
        
        # Initialize the S3 client
        session_kwargs = {
            'region_name': self.region_name
        }
        
        # Add credentials if provided
        if 'aws_access_key_id' in config and 'aws_secret_access_key' in config:
            session_kwargs['aws_access_key_id'] = config['aws_access_key_id']
            session_kwargs['aws_secret_access_key'] = config['aws_secret_access_key']
        
        # Create session and client
        session = boto3.session.Session(**session_kwargs)
        self.s3_client = session.client('s3')
        
        # Validate bucket existence
        try:
            self.s3_client.head_bucket(Bucket=self.bucket_name)
            logger.info(f"Successfully connected to S3 bucket: {self.bucket_name}")
        except botocore.exceptions.ClientError as e:
            error_code = e.response.get('Error', {}).get('Code')
            if error_code == '404':
                logger.error(f"Bucket {self.bucket_name} does not exist")
            elif error_code == '403':
                logger.error(f"Access denied to bucket {self.bucket_name}")
            else:
                logger.error(f"Error accessing bucket {self.bucket_name}: {str(e)}")
            raise
    
    def upload_file(self, file_data: Union[bytes, str, BinaryIO], destination_path: str, 
                   content_type: Optional[str] = None, metadata: Optional[Dict[str, str]] = None) -> str:
        """Upload a file to S3.
        
        Args:
            file_data: The file data to upload (bytes, string, or file-like object)
            destination_path: The path/key where the file should be stored in S3
            content_type: The MIME type of the file (optional)
            metadata: Additional metadata to store with the file (optional)
            
        Returns:
            S3 URL to the uploaded file
            
        Raises:
            botocore.exceptions.ClientError: If there's an error uploading to S3
        """
        try:
            # Ensure destination_path doesn't start with /
            if destination_path.startswith('/'):
                destination_path = destination_path[1:]
            
            # Prepare file data
            if isinstance(file_data, str) and os.path.isfile(file_data):
                # It's a file path
                self.s3_client.upload_file(
                    Filename=file_data,
                    Bucket=self.bucket_name,
                    Key=destination_path,
                    ExtraArgs={
                        'ContentType': content_type or mimetypes.guess_type(file_data)[0] or 'application/octet-stream',
                        'Metadata': metadata or {}
                    }
                )
            else:
                # It's file content (bytes or file-like object)
                if isinstance(file_data, str):
                    file_data = file_data.encode('utf-8')
                
                # Determine content type if not provided
                if not content_type and isinstance(destination_path, str):
                    content_type = mimetypes.guess_type(destination_path)[0]
                
                extra_args = {
                    'ContentType': content_type or 'application/octet-stream'
                }
                
                if metadata:
                    extra_args['Metadata'] = metadata
                
                self.s3_client.put_object(
                    Body=file_data,
                    Bucket=self.bucket_name,
                    Key=destination_path,
                    **extra_args
                )
            
            # Generate and return the S3 URL
            url = f"https://{self.bucket_name}.s3.{self.region_name}.amazonaws.com/{destination_path}"
            logger.info(f"File uploaded successfully to {url}")
            return url
            
        except botocore.exceptions.ClientError as e:
            logger.error(f"Error uploading file to S3: {str(e)}")
            raise
    
    def download_file(self, file_path: str, local_path: Optional[str] = None) -> Union[bytes, str]:
        """Download a file from S3.
        
        Args:
            file_path: Path/key to the file in S3
            local_path: Local path where the file should be saved (optional)
            
        Returns:
            File data (if local_path is None) or path to the downloaded file
            
        Raises:
            botocore.exceptions.ClientError: If there's an error downloading from S3
        """
        try:
            # Ensure file_path doesn't start with /
            if file_path.startswith('/'):
                file_path = file_path[1:]
            
            if local_path:
                # Ensure the directory exists
                os.makedirs(os.path.dirname(os.path.abspath(local_path)), exist_ok=True)
                
                # Download to local file
                self.s3_client.download_file(
                    Bucket=self.bucket_name,
                    Key=file_path,
                    Filename=local_path
                )
                logger.info(f"File downloaded from S3 to {local_path}")
                return local_path
            else:
                # Download to memory
                response = self.s3_client.get_object(
                    Bucket=self.bucket_name,
                    Key=file_path
                )
                file_data = response['Body'].read()
                logger.info(f"File downloaded from S3 to memory, size: {len(file_data)} bytes")
                return file_data
                
        except botocore.exceptions.ClientError as e:
            error_code = e.response.get('Error', {}).get('Code')
            if error_code == 'NoSuchKey':
                logger.error(f"File {file_path} not found in bucket {self.bucket_name}")
            else:
                logger.error(f"Error downloading file from S3: {str(e)}")
            raise
    
    def delete_file(self, file_path: str) -> bool:
        """Delete a file from S3.
        
        Args:
            file_path: Path/key to the file in S3
            
        Returns:
            True if the file was deleted successfully, False otherwise
        """
        try:
            # Ensure file_path doesn't start with /
            if file_path.startswith('/'):
                file_path = file_path[1:]
            
            self.s3_client.delete_object(
                Bucket=self.bucket_name,
                Key=file_path
            )
            logger.info(f"File {file_path} deleted from S3")
            return True
            
        except botocore.exceptions.ClientError as e:
            logger.error(f"Error deleting file from S3: {str(e)}")
            return False
    
    def list_files(self, directory_path: str, prefix: Optional[str] = None, 
                  recursive: bool = False) -> List[str]:
        """List files in an S3 directory.
        
        Args:
            directory_path: Path/prefix to the directory in S3
            prefix: Additional prefix to filter results (optional)
            recursive: If True, include files in subdirectories (optional, default: False)
            
        Returns:
            List of file paths/keys
        """
        try:
            # Ensure directory_path doesn't start with /
            if directory_path.startswith('/'):
                directory_path = directory_path[1:]
            
            # Ensure directory_path ends with /
            if directory_path and not directory_path.endswith('/'):
                directory_path += '/'
            
            # Combine directory_path and prefix
            combined_prefix = directory_path
            if prefix:
                combined_prefix += prefix
            
            # List objects
            result = []
            paginator = self.s3_client.get_paginator('list_objects_v2')
            page_iterator = paginator.paginate(
                Bucket=self.bucket_name,
                Prefix=combined_prefix
            )
            
            for page in page_iterator:
                if 'Contents' in page:
                    for obj in page['Contents']:
                        key = obj['Key']
                        
                        # If not recursive, skip files in subdirectories
                        if not recursive:
                            # Count the number of / characters after the directory_path
                            relative_key = key[len(directory_path):]
                            if '/' in relative_key:
                                continue
                        
                        result.append(key)
            
            logger.info(f"Listed {len(result)} files in S3 directory {directory_path}")
            return result
            
        except botocore.exceptions.ClientError as e:
            logger.error(f"Error listing files from S3: {str(e)}")
            return []
    
    def get_file_metadata(self, file_path: str) -> Dict[str, Any]:
        """Get metadata for a file in S3.
        
        Args:
            file_path: Path/key to the file in S3
            
        Returns:
            Dictionary of file metadata
            
        Raises:
            botocore.exceptions.ClientError: If there's an error getting metadata from S3
        """
        try:
            # Ensure file_path doesn't start with /
            if file_path.startswith('/'):
                file_path = file_path[1:]
            
            response = self.s3_client.head_object(
                Bucket=self.bucket_name,
                Key=file_path
            )
            
            # Format metadata into a standardized structure
            metadata = {
                'size': response.get('ContentLength', 0),
                'last_modified': response.get('LastModified', datetime.datetime.now()).isoformat(),
                'content_type': response.get('ContentType', 'application/octet-stream'),
                'etag': response.get('ETag', '').strip('"'),
            }
            
            # Add any custom metadata
            for key, value in response.get('Metadata', {}).items():
                metadata[key] = value
            
            logger.info(f"Retrieved metadata for file {file_path}")
            return metadata
            
        except botocore.exceptions.ClientError as e:
            error_code = e.response.get('Error', {}).get('Code')
            if error_code == 'NoSuchKey' or error_code == '404':
                logger.error(f"File {file_path} not found in bucket {self.bucket_name}")
            else:
                logger.error(f"Error getting file metadata from S3: {str(e)}")
            raise
    
    def check_file_exists(self, file_path: str) -> bool:
        """Check if a file exists in S3.
        
        Args:
            file_path: Path/key to the file in S3
            
        Returns:
            True if the file exists, False otherwise
        """
        try:
            # Ensure file_path doesn't start with /
            if file_path.startswith('/'):
                file_path = file_path[1:]
            
            self.s3_client.head_object(
                Bucket=self.bucket_name,
                Key=file_path
            )
            return True
            
        except botocore.exceptions.ClientError as e:
            error_code = e.response.get('Error', {}).get('Code')
            if error_code == 'NoSuchKey' or error_code == '404':
                return False
            else:
                logger.error(f"Error checking if file exists in S3: {str(e)}")
                raise
    
    def generate_presigned_url(self, file_path: str, expiration_seconds: int, 
                              http_method: str = 'GET') -> str:
        """Generate a pre-signed URL for an S3 object.
        
        Args:
            file_path: Path/key to the file in S3
            expiration_seconds: Number of seconds until the URL expires
            http_method: HTTP method allowed for the URL (optional, default: 'GET')
            
        Returns:
            Pre-signed URL
            
        Raises:
            botocore.exceptions.ClientError: If there's an error generating the URL
            ValueError: If the file doesn't exist
        """
        try:
            # Ensure file_path doesn't start with /
            if file_path.startswith('/'):
                file_path = file_path[1:]
            
            # Verify the file exists
            if not self.check_file_exists(file_path):
                raise ValueError(f"File {file_path} does not exist in bucket {self.bucket_name}")
            
            # Generate the URL
            url = self.s3_client.generate_presigned_url(
                ClientMethod='get_object',
                Params={
                    'Bucket': self.bucket_name,
                    'Key': file_path
                },
                ExpiresIn=expiration_seconds,
                HttpMethod=http_method
            )
            
            logger.info(f"Generated pre-signed URL for {file_path}, expires in {expiration_seconds} seconds")
            return url
            
        except botocore.exceptions.ClientError as e:
            logger.error(f"Error generating pre-signed URL: {str(e)}")
            raise


class LocalStorageClient(StorageClient):
    """Local filesystem implementation of the storage client, primarily for development and testing."""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize the local storage client.
        
        Args:
            config: Configuration dictionary containing local storage settings
                   (base_directory, base_url)
        """
        super().__init__(config)
        self.base_directory = config.get('base_directory')
        self.base_url = config.get('base_url', f'file://{self.base_directory}')
        
        if not self.base_directory:
            raise ValueError("Local storage base directory is required in config")
        
        # Ensure base directory exists
        os.makedirs(self.base_directory, exist_ok=True)
        
        # Check if base directory is writable
        if not os.access(self.base_directory, os.W_OK):
            raise ValueError(f"Base directory {self.base_directory} is not writable")
        
        logger.info(f"Local storage client initialized with base directory: {self.base_directory}")
    
    def upload_file(self, file_data: Union[bytes, str, BinaryIO], destination_path: str, 
                   content_type: Optional[str] = None, metadata: Optional[Dict[str, str]] = None) -> str:
        """Upload a file to local storage.
        
        Args:
            file_data: The file data to upload (bytes, string, or file-like object)
            destination_path: The path where the file should be stored
            content_type: The MIME type of the file (optional)
            metadata: Additional metadata to store with the file (optional)
            
        Returns:
            URL or path to the uploaded file
        """
        try:
            # Ensure destination_path doesn't start with /
            if destination_path.startswith('/'):
                destination_path = destination_path[1:]
            
            # Create the full local path
            full_path = os.path.join(self.base_directory, destination_path)
            
            # Ensure the directory exists
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            
            # Write the file
            if isinstance(file_data, str) and os.path.isfile(file_data):
                # It's a file path, copy the file
                with open(file_data, 'rb') as src, open(full_path, 'wb') as dst:
                    dst.write(src.read())
            else:
                # It's file content
                mode = 'wb'
                if isinstance(file_data, str):
                    file_data = file_data.encode('utf-8')
                    
                with open(full_path, mode) as f:
                    if hasattr(file_data, 'read'):
                        # It's a file-like object
                        f.write(file_data.read())
                    else:
                        # It's bytes
                        f.write(file_data)
            
            # Store metadata if provided
            if metadata:
                metadata_path = f"{full_path}.metadata"
                with open(metadata_path, 'w') as f:
                    for key, value in metadata.items():
                        f.write(f"{key}={value}\n")
            
            # Generate and return the URL
            url = f"{self.base_url}/{destination_path}"
            logger.info(f"File uploaded successfully to {url}")
            return url
            
        except Exception as e:
            logger.error(f"Error uploading file to local storage: {str(e)}")
            raise
    
    def download_file(self, file_path: str, local_path: Optional[str] = None) -> Union[bytes, str]:
        """Download a file from local storage.
        
        Args:
            file_path: Path to the file in local storage
            local_path: Local path where the file should be saved (optional)
            
        Returns:
            File data (if local_path is None) or path to the downloaded file
            
        Raises:
            FileNotFoundError: If the file doesn't exist
        """
        try:
            # Ensure file_path doesn't start with /
            if file_path.startswith('/'):
                file_path = file_path[1:]
            
            # Create the full source path
            full_source_path = os.path.join(self.base_directory, file_path)
            
            # Check if the file exists
            if not os.path.isfile(full_source_path):
                raise FileNotFoundError(f"File {file_path} not found in local storage")
            
            if local_path:
                # Ensure the directory exists
                os.makedirs(os.path.dirname(os.path.abspath(local_path)), exist_ok=True)
                
                # Copy the file
                with open(full_source_path, 'rb') as src, open(local_path, 'wb') as dst:
                    dst.write(src.read())
                
                logger.info(f"File downloaded from local storage to {local_path}")
                return local_path
            else:
                # Read the file into memory
                with open(full_source_path, 'rb') as f:
                    file_data = f.read()
                
                logger.info(f"File downloaded from local storage to memory, size: {len(file_data)} bytes")
                return file_data
                
        except Exception as e:
            logger.error(f"Error downloading file from local storage: {str(e)}")
            raise
    
    def delete_file(self, file_path: str) -> bool:
        """Delete a file from local storage.
        
        Args:
            file_path: Path to the file in local storage
            
        Returns:
            True if the file was deleted successfully, False otherwise
        """
        try:
            # Ensure file_path doesn't start with /
            if file_path.startswith('/'):
                file_path = file_path[1:]
            
            # Create the full path
            full_path = os.path.join(self.base_directory, file_path)
            
            # Check if the file exists
            if not os.path.isfile(full_path):
                logger.warning(f"File {file_path} not found in local storage")
                return False
            
            # Delete the file
            os.remove(full_path)
            
            # Delete metadata file if it exists
            metadata_path = f"{full_path}.metadata"
            if os.path.isfile(metadata_path):
                os.remove(metadata_path)
            
            logger.info(f"File {file_path} deleted from local storage")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting file from local storage: {str(e)}")
            return False
    
    def list_files(self, directory_path: str, prefix: Optional[str] = None, 
                  recursive: bool = False) -> List[str]:
        """List files in a local directory.
        
        Args:
            directory_path: Path to the directory in local storage
            prefix: Filter files by this prefix (optional)
            recursive: If True, include files in subdirectories (optional, default: False)
            
        Returns:
            List of file paths
        """
        try:
            # Ensure directory_path doesn't start with /
            if directory_path.startswith('/'):
                directory_path = directory_path[1:]
            
            # Create the full directory path
            full_dir_path = os.path.join(self.base_directory, directory_path)
            
            # Check if the directory exists
            if not os.path.isdir(full_dir_path):
                logger.warning(f"Directory {directory_path} not found in local storage")
                return []
            
            result = []
            
            if recursive:
                # Use os.walk for recursive listing
                for root, _, files in os.walk(full_dir_path):
                    for file in files:
                        # Skip metadata files
                        if file.endswith('.metadata'):
                            continue
                        
                        # Get the full path and convert to relative path
                        full_file_path = os.path.join(root, file)
                        rel_path = os.path.relpath(full_file_path, self.base_directory)
                        
                        # Apply prefix filter if provided
                        if prefix and not os.path.basename(rel_path).startswith(prefix):
                            continue
                        
                        result.append(rel_path)
            else:
                # Use os.listdir for non-recursive listing
                for file in os.listdir(full_dir_path):
                    # Skip metadata files
                    if file.endswith('.metadata'):
                        continue
                    
                    # Get the full path
                    full_file_path = os.path.join(full_dir_path, file)
                    
                    # Skip directories
                    if os.path.isdir(full_file_path):
                        continue
                    
                    # Apply prefix filter if provided
                    if prefix and not file.startswith(prefix):
                        continue
                    
                    # Get the relative path
                    rel_path = os.path.join(directory_path, file)
                    result.append(rel_path)
            
            logger.info(f"Listed {len(result)} files in local directory {directory_path}")
            return result
            
        except Exception as e:
            logger.error(f"Error listing files from local storage: {str(e)}")
            return []
    
    def get_file_metadata(self, file_path: str) -> Dict[str, Any]:
        """Get metadata for a file in local storage.
        
        Args:
            file_path: Path to the file in local storage
            
        Returns:
            Dictionary of file metadata
            
        Raises:
            FileNotFoundError: If the file doesn't exist
        """
        try:
            # Ensure file_path doesn't start with /
            if file_path.startswith('/'):
                file_path = file_path[1:]
            
            # Create the full path
            full_path = os.path.join(self.base_directory, file_path)
            
            # Check if the file exists
            if not os.path.isfile(full_path):
                raise FileNotFoundError(f"File {file_path} not found in local storage")
            
            # Get file stats
            stat_result = os.stat(full_path)
            
            # Get content type
            content_type, _ = mimetypes.guess_type(full_path)
            
            # Create metadata dictionary
            metadata = {
                'size': stat_result.st_size,
                'last_modified': datetime.datetime.fromtimestamp(stat_result.st_mtime).isoformat(),
                'content_type': content_type or 'application/octet-stream',
                'etag': f"{stat_result.st_mtime}-{stat_result.st_size}",
            }
            
            # Read custom metadata if it exists
            metadata_path = f"{full_path}.metadata"
            if os.path.isfile(metadata_path):
                with open(metadata_path, 'r') as f:
                    for line in f:
                        if '=' in line:
                            key, value = line.strip().split('=', 1)
                            metadata[key] = value
            
            logger.info(f"Retrieved metadata for file {file_path}")
            return metadata
            
        except FileNotFoundError:
            logger.error(f"File {file_path} not found in local storage")
            raise
        except Exception as e:
            logger.error(f"Error getting file metadata from local storage: {str(e)}")
            raise
    
    def check_file_exists(self, file_path: str) -> bool:
        """Check if a file exists in local storage.
        
        Args:
            file_path: Path to the file in local storage
            
        Returns:
            True if the file exists, False otherwise
        """
        try:
            # Ensure file_path doesn't start with /
            if file_path.startswith('/'):
                file_path = file_path[1:]
            
            # Create the full path
            full_path = os.path.join(self.base_directory, file_path)
            
            # Check if the file exists
            return os.path.isfile(full_path)
            
        except Exception as e:
            logger.error(f"Error checking if file exists in local storage: {str(e)}")
            return False
    
    def generate_presigned_url(self, file_path: str, expiration_seconds: int, 
                              http_method: str = 'GET') -> str:
        """Generate a URL for a local file with a temporary access token.
        
        Args:
            file_path: Path to the file in local storage
            expiration_seconds: Number of seconds until the URL expires
            http_method: HTTP method allowed for the URL (optional, default: 'GET')
            
        Returns:
            URL with access token
            
        Raises:
            ValueError: If the file doesn't exist
        """
        try:
            # Ensure file_path doesn't start with /
            if file_path.startswith('/'):
                file_path = file_path[1:]
            
            # Create the full path
            full_path = os.path.join(self.base_directory, file_path)
            
            # Check if the file exists
            if not os.path.isfile(full_path):
                raise ValueError(f"File {file_path} not found in local storage")
            
            # For local storage, we'll generate a simple token and include it in the URL
            # In a real implementation, this would be stored in a secure token store with expiration
            token = str(uuid.uuid4())
            
            # In a real implementation, this would store the token in a database or cache with expiration
            # For simplicity, we'll just log it
            expiration = datetime.datetime.now() + datetime.timedelta(seconds=expiration_seconds)
            logger.info(f"Generated token {token} for {file_path}, expires at {expiration}")
            
            # Generate the URL
            url = f"{self.base_url}/{file_path}?token={token}&expires={int(expiration.timestamp())}"
            return url
            
        except Exception as e:
            logger.error(f"Error generating URL for local file: {str(e)}")
            raise
    
    def create_directory(self, directory_path: str) -> bool:
        """Create a directory in local storage.
        
        Args:
            directory_path: Path to the directory to create
            
        Returns:
            True if the directory was created successfully, False otherwise
        """
        try:
            # Ensure directory_path doesn't start with /
            if directory_path.startswith('/'):
                directory_path = directory_path[1:]
            
            # Create the full path
            full_path = os.path.join(self.base_directory, directory_path)
            
            # Create the directory
            os.makedirs(full_path, exist_ok=True)
            
            logger.info(f"Directory {directory_path} created in local storage")
            return True
            
        except Exception as e:
            logger.error(f"Error creating directory in local storage: {str(e)}")
            return False


def initialize_storage(config: Dict[str, Any]) -> StorageClient:
    """Initialize the storage backend connection based on configuration.
    
    Args:
        config: Configuration dictionary for the storage client
        
    Returns:
        Storage client instance
        
    Raises:
        ValueError: If the storage backend type is not supported
    """
    backend_type = config.get('backend_type', 's3').lower()
    
    if backend_type == 's3':
        return S3StorageClient(config)
    elif backend_type == 'local':
        return LocalStorageClient(config)
    else:
        raise ValueError(f"Unsupported storage backend type: {backend_type}")


def upload_file(file_data: Union[bytes, str, BinaryIO], destination_path: str, 
               content_type: Optional[str] = None, metadata: Optional[Dict[str, str]] = None,
               public: bool = False) -> str:
    """Upload a file to the storage backend.
    
    Args:
        file_data: The file data to upload (bytes, string, or file-like object)
        destination_path: The path where the file should be stored
        content_type: The MIME type of the file (optional)
        metadata: Additional metadata to store with the file (optional)
        public: If True, make the file publicly accessible (optional, default: False)
        
    Returns:
        URL or path to the uploaded file
    """
    from flask import current_app
    
    # Get the storage client from the Flask app
    storage_client = current_app.config.get('STORAGE_CLIENT')
    
    if not storage_client:
        # Initialize the storage client if not already done
        storage_config = current_app.config.get('STORAGE_CONFIG', {})
        storage_client = initialize_storage(storage_config)
        current_app.config['STORAGE_CLIENT'] = storage_client
    
    # Determine content type if not provided
    if not content_type and isinstance(destination_path, str):
        content_type = mimetypes.guess_type(destination_path)[0]
    
    # Add public access metadata if requested
    if public:
        if not metadata:
            metadata = {}
        metadata['public'] = 'true'
    
    # Upload the file
    return storage_client.upload_file(file_data, destination_path, content_type, metadata)


def download_file(file_path: str, local_path: Optional[str] = None) -> Union[bytes, str]:
    """Download a file from the storage backend.
    
    Args:
        file_path: Path to the file in the storage backend
        local_path: Local path where the file should be saved (optional)
        
    Returns:
        File data (if local_path is None) or path to the downloaded file
    """
    from flask import current_app
    
    # Get the storage client from the Flask app
    storage_client = current_app.config.get('STORAGE_CLIENT')
    
    if not storage_client:
        # Initialize the storage client if not already done
        storage_config = current_app.config.get('STORAGE_CONFIG', {})
        storage_client = initialize_storage(storage_config)
        current_app.config['STORAGE_CLIENT'] = storage_client
    
    # Download the file
    return storage_client.download_file(file_path, local_path)


def generate_presigned_url(file_path: str, expiration_seconds: int, 
                          http_method: str = 'GET') -> str:
    """Generate a pre-signed URL for temporary access to a file.
    
    Args:
        file_path: Path to the file in the storage backend
        expiration_seconds: Number of seconds until the URL expires
        http_method: HTTP method allowed for the URL (optional, default: 'GET')
        
    Returns:
        Pre-signed URL
    """
    from flask import current_app
    
    # Get the storage client from the Flask app
    storage_client = current_app.config.get('STORAGE_CLIENT')
    
    if not storage_client:
        # Initialize the storage client if not already done
        storage_config = current_app.config.get('STORAGE_CONFIG', {})
        storage_client = initialize_storage(storage_config)
        current_app.config['STORAGE_CLIENT'] = storage_client
    
    # Generate the URL
    return storage_client.generate_presigned_url(file_path, expiration_seconds, http_method)


def delete_file(file_path: str) -> bool:
    """Delete a file from the storage backend.
    
    Args:
        file_path: Path to the file in the storage backend
        
    Returns:
        True if the file was deleted successfully, False otherwise
    """
    from flask import current_app
    
    # Get the storage client from the Flask app
    storage_client = current_app.config.get('STORAGE_CLIENT')
    
    if not storage_client:
        # Initialize the storage client if not already done
        storage_config = current_app.config.get('STORAGE_CONFIG', {})
        storage_client = initialize_storage(storage_config)
        current_app.config['STORAGE_CLIENT'] = storage_client
    
    # Delete the file
    return storage_client.delete_file(file_path)


def list_files(directory_path: str, prefix: Optional[str] = None, 
              recursive: bool = False) -> List[str]:
    """List files in a directory in the storage backend.
    
    Args:
        directory_path: Path to the directory in the storage backend
        prefix: Filter files by this prefix (optional)
        recursive: If True, include files in subdirectories (optional, default: False)
        
    Returns:
        List of file paths
    """
    from flask import current_app
    
    # Get the storage client from the Flask app
    storage_client = current_app.config.get('STORAGE_CLIENT')
    
    if not storage_client:
        # Initialize the storage client if not already done
        storage_config = current_app.config.get('STORAGE_CONFIG', {})
        storage_client = initialize_storage(storage_config)
        current_app.config['STORAGE_CLIENT'] = storage_client
    
    # List the files
    return storage_client.list_files(directory_path, prefix, recursive)


def get_file_metadata(file_path: str) -> Dict[str, Any]:
    """Get metadata for a file in the storage backend.
    
    Args:
        file_path: Path to the file in the storage backend
        
    Returns:
        Dictionary of file metadata
    """
    from flask import current_app
    
    # Get the storage client from the Flask app
    storage_client = current_app.config.get('STORAGE_CLIENT')
    
    if not storage_client:
        # Initialize the storage client if not already done
        storage_config = current_app.config.get('STORAGE_CONFIG', {})
        storage_client = initialize_storage(storage_config)
        current_app.config['STORAGE_CLIENT'] = storage_client
    
    # Get the metadata
    return storage_client.get_file_metadata(file_path)


def check_file_exists(file_path: str) -> bool:
    """Check if a file exists in the storage backend.
    
    Args:
        file_path: Path to the file in the storage backend
        
    Returns:
        True if the file exists, False otherwise
    """
    from flask import current_app
    
    # Get the storage client from the Flask app
    storage_client = current_app.config.get('STORAGE_CLIENT')
    
    if not storage_client:
        # Initialize the storage client if not already done
        storage_config = current_app.config.get('STORAGE_CONFIG', {})
        storage_client = initialize_storage(storage_config)
        current_app.config['STORAGE_CLIENT'] = storage_client
    
    # Check if the file exists
    return storage_client.check_file_exists(file_path)


def get_file_url(file_path: str, public: bool = False) -> str:
    """Get a URL for a file without generating a pre-signed URL.
    
    Args:
        file_path: Path to the file in the storage backend
        public: If True, return a URL for a public file, otherwise return a pre-signed URL
                (optional, default: False)
        
    Returns:
        URL to the file
    """
    from flask import current_app
    
    # Get the storage client from the Flask app
    storage_client = current_app.config.get('STORAGE_CLIENT')
    
    if not storage_client:
        # Initialize the storage client if not already done
        storage_config = current_app.config.get('STORAGE_CONFIG', {})
        storage_client = initialize_storage(storage_config)
        current_app.config['STORAGE_CLIENT'] = storage_client
    
    # If it's a public file, construct a direct URL
    if public:
        if isinstance(storage_client, S3StorageClient):
            # Ensure file_path doesn't start with /
            if file_path.startswith('/'):
                file_path = file_path[1:]
            
            return f"https://{storage_client.bucket_name}.s3.{storage_client.region_name}.amazonaws.com/{file_path}"
        elif isinstance(storage_client, LocalStorageClient):
            # Ensure file_path doesn't start with /
            if file_path.startswith('/'):
                file_path = file_path[1:]
            
            return f"{storage_client.base_url}/{file_path}"
    
    # Otherwise, return a pre-signed URL with a default expiration
    return storage_client.generate_presigned_url(file_path, 3600)  # 1 hour


def copy_file(source_path: str, destination_path: str) -> bool:
    """Copy a file within the storage backend.
    
    Args:
        source_path: Path to the source file in the storage backend
        destination_path: Path where the file should be copied
        
    Returns:
        True if the file was copied successfully, False otherwise
    """
    from flask import current_app
    
    # Get the storage client from the Flask app
    storage_client = current_app.config.get('STORAGE_CLIENT')
    
    if not storage_client:
        # Initialize the storage client if not already done
        storage_config = current_app.config.get('STORAGE_CONFIG', {})
        storage_client = initialize_storage(storage_config)
        current_app.config['STORAGE_CLIENT'] = storage_client
    
    try:
        # For S3, use the copy_object method
        if isinstance(storage_client, S3StorageClient):
            # Ensure paths don't start with /
            if source_path.startswith('/'):
                source_path = source_path[1:]
            if destination_path.startswith('/'):
                destination_path = destination_path[1:]
            
            storage_client.s3_client.copy_object(
                Bucket=storage_client.bucket_name,
                CopySource={'Bucket': storage_client.bucket_name, 'Key': source_path},
                Key=destination_path
            )
            logger.info(f"File copied from {source_path} to {destination_path}")
            return True
        
        # For local storage, download and then upload
        else:
            file_data = storage_client.download_file(source_path)
            
            # Get content type and metadata from source
            metadata = {}
            try:
                source_metadata = storage_client.get_file_metadata(source_path)
                metadata = {k: v for k, v in source_metadata.items() 
                            if k not in ['size', 'last_modified', 'content_type', 'etag']}
                content_type = source_metadata.get('content_type')
            except:
                content_type = None
            
            storage_client.upload_file(file_data, destination_path, content_type, metadata)
            logger.info(f"File copied from {source_path} to {destination_path}")
            return True
            
    except Exception as e:
        logger.error(f"Error copying file: {str(e)}")
        return False


def create_directory(directory_path: str) -> bool:
    """Create a directory in the storage backend (if supported).
    
    Args:
        directory_path: Path to the directory to create
        
    Returns:
        True if the directory was created successfully, False otherwise
    """
    from flask import current_app
    
    # Get the storage client from the Flask app
    storage_client = current_app.config.get('STORAGE_CLIENT')
    
    if not storage_client:
        # Initialize the storage client if not already done
        storage_config = current_app.config.get('STORAGE_CONFIG', {})
        storage_client = initialize_storage(storage_config)
        current_app.config['STORAGE_CLIENT'] = storage_client
    
    # For S3, directories don't really exist, so this is a no-op
    if isinstance(storage_client, S3StorageClient):
        logger.info(f"S3 doesn't use directories, no action needed for {directory_path}")
        return True
    
    # For local storage, create the directory
    elif isinstance(storage_client, LocalStorageClient):
        return storage_client.create_directory(directory_path)
    
    return False


def generate_temp_download_token(file_path: str, expiration_seconds: int) -> str:
    """Generate a temporary token for downloading a file.
    
    Args:
        file_path: Path to the file in the storage backend
        expiration_seconds: Number of seconds until the token expires
        
    Returns:
        Temporary download token
    """
    from flask import current_app
    import secrets
    import time
    
    # Validate the file exists
    if not check_file_exists(file_path):
        raise ValueError(f"File {file_path} does not exist")
    
    # Generate a secure token
    token = secrets.token_hex(16)
    
    # Create a token record with expiration
    token_data = {
        'file_path': file_path,
        'expires_at': time.time() + expiration_seconds
    }
    
    # Store in app config for simplicity (in a real app, use a proper token store)
    if 'DOWNLOAD_TOKENS' not in current_app.config:
        current_app.config['DOWNLOAD_TOKENS'] = {}
    
    current_app.config['DOWNLOAD_TOKENS'][token] = token_data
    
    logger.info(f"Generated download token for {file_path}, expires in {expiration_seconds} seconds")
    return token


def get_storage_usage(directory_path: Optional[str] = None) -> Dict[str, Any]:
    """Get storage usage statistics.
    
    Args:
        directory_path: Path to the directory to analyze (optional, default: entire storage)
        
    Returns:
        Dictionary with storage usage statistics
    """
    from flask import current_app
    
    # Get the storage client from the Flask app
    storage_client = current_app.config.get('STORAGE_CLIENT')
    
    if not storage_client:
        # Initialize the storage client if not already done
        storage_config = current_app.config.get('STORAGE_CONFIG', {})
        storage_client = initialize_storage(storage_config)
        current_app.config['STORAGE_CLIENT'] = storage_client
    
    # Initialize statistics
    stats = {
        'total_size': 0,
        'file_count': 0,
        'average_file_size': 0,
        'largest_file': {'path': None, 'size': 0},
        'newest_file': {'path': None, 'timestamp': 0},
        'oldest_file': {'path': None, 'timestamp': float('inf')},
    }
    
    # List all files in the directory (or entire storage)
    files = storage_client.list_files(directory_path or '', recursive=True)
    
    # Gather statistics
    for file_path in files:
        try:
            metadata = storage_client.get_file_metadata(file_path)
            
            size = metadata.get('size', 0)
            stats['total_size'] += size
            stats['file_count'] += 1
            
            # Check if this is the largest file
            if size > stats['largest_file']['size']:
                stats['largest_file']['path'] = file_path
                stats['largest_file']['size'] = size
            
            # Check timestamp
            if 'last_modified' in metadata:
                try:
                    # Parse ISO 8601 timestamp
                    timestamp = datetime.datetime.fromisoformat(metadata['last_modified']).timestamp()
                    
                    # Check if this is the newest file
                    if timestamp > stats['newest_file']['timestamp']:
                        stats['newest_file']['path'] = file_path
                        stats['newest_file']['timestamp'] = timestamp
                    
                    # Check if this is the oldest file
                    if timestamp < stats['oldest_file']['timestamp']:
                        stats['oldest_file']['path'] = file_path
                        stats['oldest_file']['timestamp'] = timestamp
                except:
                    # Skip timestamp calculation if parsing fails
                    pass
        except:
            # Skip files that can't be analyzed
            continue
    
    # Calculate average file size
    if stats['file_count'] > 0:
        stats['average_file_size'] = stats['total_size'] / stats['file_count']
    
    # Convert timestamps to ISO format
    if stats['newest_file']['path']:
        stats['newest_file']['timestamp'] = datetime.datetime.fromtimestamp(
            stats['newest_file']['timestamp']).isoformat()
    else:
        stats['newest_file'] = None
    
    if stats['oldest_file']['path']:
        stats['oldest_file']['timestamp'] = datetime.datetime.fromtimestamp(
            stats['oldest_file']['timestamp']).isoformat()
    else:
        stats['oldest_file'] = None
    
    logger.info(f"Storage usage analyzed: {stats['file_count']} files, {stats['total_size']} bytes total")
    return stats