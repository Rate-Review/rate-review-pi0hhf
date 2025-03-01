"""
Cryptographic utilities for secure data encryption and decryption in the Justice Bid Rate Negotiation System.

Provides functions for encrypting sensitive data at rest, generating initialization vectors,
and managing encryption keys.
"""

import os
import base64
from typing import Union, Dict, List, Any, Optional

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes

from .logging import get_logger
from ..config import AppConfig

# Initialize logger
logger = get_logger(__name__)

# Constants
ENCRYPTION_KEY_ENV_VAR = "JUSTICE_BID_ENCRYPTION_KEY"
DEFAULT_ITERATIONS = 100000
AES_KEY_SIZE = 32  # 256 bits = 32 bytes
AES_BLOCK_SIZE = 16  # 128 bits = 16 bytes
ENCODING = "utf-8"


def get_encryption_key() -> bytes:
    """
    Retrieves the master encryption key from environment variables or generates a new one.
    
    Returns:
        bytes: The encryption key as bytes
    """
    key = os.environ.get(ENCRYPTION_KEY_ENV_VAR)
    
    if key:
        try:
            return base64.b64decode(key)
        except Exception as e:
            logger.error(f"Failed to decode encryption key: {str(e)}")
    
    # If no valid key found in environment, generate a warning and a new key
    logger.warning(
        "No encryption key found in environment. Using a generated key. "
        "This is not secure for production environments."
    )
    
    # Generate a new key
    return os.urandom(AES_KEY_SIZE)


def derive_key(password: str, salt: bytes, iterations: int = DEFAULT_ITERATIONS) -> bytes:
    """
    Derives an encryption key from a password and salt using PBKDF2.
    
    Args:
        password (str): The password to derive the key from
        salt (bytes): Random salt for key derivation
        iterations (int): Number of iterations for PBKDF2
    
    Returns:
        bytes: Derived key suitable for encryption
    """
    if isinstance(password, str):
        password = password.encode(ENCODING)
    
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=AES_KEY_SIZE,
        salt=salt,
        iterations=iterations,
        backend=default_backend()
    )
    
    return kdf.derive(password)


def generate_salt(size: int = 16) -> bytes:
    """
    Generates a random salt for key derivation.
    
    Args:
        size (int): Size of the salt in bytes
    
    Returns:
        bytes: Random salt of specified size
    """
    return os.urandom(size)


def generate_iv() -> bytes:
    """
    Generates a random initialization vector for encryption.
    
    Returns:
        bytes: Random initialization vector
    """
    return os.urandom(AES_BLOCK_SIZE)


def encrypt_string(plaintext: str) -> str:
    """
    Encrypts a string using AES-256 encryption.
    
    Args:
        plaintext (str): The string to encrypt
    
    Returns:
        str: Base64-encoded encrypted string with IV
    """
    if not plaintext:
        return None
    
    try:
        if isinstance(plaintext, str):
            plaintext = plaintext.encode(ENCODING)
        
        key = get_encryption_key()
        iv = generate_iv()
        
        # Create an encryptor with AES in CBC mode
        cipher = Cipher(
            algorithms.AES(key),
            modes.CBC(iv),
            backend=default_backend()
        )
        encryptor = cipher.encryptor()
        
        # Pad the plaintext to a multiple of AES_BLOCK_SIZE (PKCS7 padding)
        padding_length = AES_BLOCK_SIZE - (len(plaintext) % AES_BLOCK_SIZE)
        padded_data = plaintext + bytes([padding_length]) * padding_length
        
        # Encrypt the padded data
        ciphertext = encryptor.update(padded_data) + encryptor.finalize()
        
        # Combine IV and ciphertext for storage
        encrypted_data = iv + ciphertext
        
        # Base64 encode for safe storage
        return base64.b64encode(encrypted_data).decode(ENCODING)
    except Exception as e:
        logger.error(f"Failed to encrypt string: {str(e)}")
        return None


def decrypt_string(encrypted_text: str) -> Optional[str]:
    """
    Decrypts an encrypted string using AES-256 decryption.
    
    Args:
        encrypted_text (str): The encrypted text to decrypt
    
    Returns:
        str: Decrypted plaintext string
    """
    if not encrypted_text:
        return None
    
    try:
        # Base64 decode the encrypted text
        encrypted_data = base64.b64decode(encrypted_text)
        
        # Extract IV (first AES_BLOCK_SIZE bytes)
        iv = encrypted_data[:AES_BLOCK_SIZE]
        ciphertext = encrypted_data[AES_BLOCK_SIZE:]
        
        key = get_encryption_key()
        
        # Create a decryptor with AES in CBC mode
        cipher = Cipher(
            algorithms.AES(key),
            modes.CBC(iv),
            backend=default_backend()
        )
        decryptor = cipher.decryptor()
        
        # Decrypt the ciphertext
        padded_data = decryptor.update(ciphertext) + decryptor.finalize()
        
        # Remove PKCS7 padding
        padding_length = padded_data[-1]
        if padding_length > AES_BLOCK_SIZE:
            raise ValueError("Invalid padding")
        
        plaintext = padded_data[:-padding_length]
        
        # Convert to string
        return plaintext.decode(ENCODING)
    except Exception as e:
        logger.error(f"Failed to decrypt string: {str(e)}")
        return None


def encrypt_dict(data: Dict, fields_to_encrypt: List[str]) -> Dict:
    """
    Encrypts specific fields in a dictionary based on a fields list.
    
    Args:
        data (dict): Dictionary containing data to encrypt
        fields_to_encrypt (list): List of field names to encrypt
    
    Returns:
        dict: Dictionary with specified fields encrypted
    """
    if not data or not fields_to_encrypt:
        return data
    
    # Create a copy to avoid modifying the original
    result = data.copy()
    
    for field in fields_to_encrypt:
        if field in result and result[field] is not None:
            result[field] = encrypt_string(str(result[field]))
    
    return result


def decrypt_dict(data: Dict, fields_to_decrypt: List[str]) -> Dict:
    """
    Decrypts specific fields in a dictionary based on a fields list.
    
    Args:
        data (dict): Dictionary containing encrypted data
        fields_to_decrypt (list): List of field names to decrypt
    
    Returns:
        dict: Dictionary with specified fields decrypted
    """
    if not data or not fields_to_decrypt:
        return data
    
    # Create a copy to avoid modifying the original
    result = data.copy()
    
    for field in fields_to_decrypt:
        if field in result and result[field] is not None:
            result[field] = decrypt_string(result[field])
    
    return result


def encrypt_file(file_path: str, output_path: str) -> bool:
    """
    Encrypts a file using AES-256 encryption.
    
    Args:
        file_path (str): Path to the file to encrypt
        output_path (str): Path where the encrypted file will be saved
    
    Returns:
        bool: True if encryption was successful, False otherwise
    """
    try:
        key = get_encryption_key()
        iv = generate_iv()
        
        # Create an encryptor with AES in CBC mode
        cipher = Cipher(
            algorithms.AES(key),
            modes.CBC(iv),
            backend=default_backend()
        )
        encryptor = cipher.encryptor()
        
        with open(file_path, 'rb') as infile, open(output_path, 'wb') as outfile:
            # Write the IV at the beginning of the output file
            outfile.write(iv)
            
            # Read the file in chunks to handle large files
            chunk_size = 64 * 1024  # 64KB chunks
            
            while True:
                chunk = infile.read(chunk_size)
                if len(chunk) == 0:
                    break
                
                # For all chunks except the last, encrypt as is
                if len(chunk) % AES_BLOCK_SIZE == 0:
                    outfile.write(encryptor.update(chunk))
                else:
                    # Pad the last chunk to a multiple of AES_BLOCK_SIZE
                    padding_length = AES_BLOCK_SIZE - (len(chunk) % AES_BLOCK_SIZE)
                    padded_chunk = chunk + bytes([padding_length]) * padding_length
                    outfile.write(encryptor.update(padded_chunk))
            
            # Finalize the encryption
            outfile.write(encryptor.finalize())
        
        return True
    except Exception as e:
        logger.error(f"Failed to encrypt file {file_path}: {str(e)}")
        return False


def decrypt_file(encrypted_file_path: str, output_path: str) -> bool:
    """
    Decrypts a file encrypted with AES-256.
    
    Args:
        encrypted_file_path (str): Path to the encrypted file
        output_path (str): Path where the decrypted file will be saved
    
    Returns:
        bool: True if decryption was successful, False otherwise
    """
    try:
        key = get_encryption_key()
        
        with open(encrypted_file_path, 'rb') as infile, open(output_path, 'wb') as outfile:
            # Read the IV from the beginning of the file
            iv = infile.read(AES_BLOCK_SIZE)
            
            # Create a decryptor with AES in CBC mode
            cipher = Cipher(
                algorithms.AES(key),
                modes.CBC(iv),
                backend=default_backend()
            )
            decryptor = cipher.decryptor()
            
            # Keep track of all decrypted data
            decrypted_data = b''
            
            # Process the file in chunks to handle large files
            chunk_size = 64 * 1024  # 64KB chunks
            
            while True:
                chunk = infile.read(chunk_size)
                if not chunk:
                    break
                
                decrypted_data += decryptor.update(chunk)
            
            # Add the final block
            decrypted_data += decryptor.finalize()
            
            # Remove padding from the last block
            padding_length = decrypted_data[-1]
            unpadded_data = decrypted_data[:-padding_length]
            
            # Write the unpadded data
            outfile.write(unpadded_data)
        
        return True
    except Exception as e:
        logger.error(f"Failed to decrypt file {encrypted_file_path}: {str(e)}")
        return False


def create_fernet() -> Fernet:
    """
    Creates a Fernet symmetric encryption instance with the system key.
    
    Returns:
        Fernet: Fernet instance for symmetric encryption
    """
    key = get_encryption_key()
    
    # Fernet requires a URL-safe base64-encoded 32-byte key
    fernet_key = base64.urlsafe_b64encode(key)
    
    return Fernet(fernet_key)


def fernet_encrypt(data: Union[str, bytes]) -> str:
    """
    Encrypts data using Fernet symmetric encryption (simpler than raw AES but with authentication).
    
    Args:
        data (Union[str, bytes]): Data to encrypt
    
    Returns:
        str: Base64-encoded encrypted data
    """
    fernet = create_fernet()
    
    if isinstance(data, str):
        data = data.encode(ENCODING)
    
    encrypted_data = fernet.encrypt(data)
    return encrypted_data.decode(ENCODING)


def fernet_decrypt(encrypted_data: str) -> Optional[str]:
    """
    Decrypts data using Fernet symmetric encryption.
    
    Args:
        encrypted_data (str): Encrypted data to decrypt
    
    Returns:
        str: Decrypted data as string
    """
    try:
        fernet = create_fernet()
        
        if isinstance(encrypted_data, str):
            encrypted_data = encrypted_data.encode(ENCODING)
        
        decrypted_data = fernet.decrypt(encrypted_data)
        return decrypted_data.decode(ENCODING)
    except Exception as e:
        logger.error(f"Failed to decrypt data with Fernet: {str(e)}")
        return None


def mask_pii(value: str, pii_type: str = "default") -> str:
    """
    Masks personally identifiable information for display while preserving some recognizable characters.
    
    Args:
        value (str): The value to mask
        pii_type (str): Type of PII (email, phone, name, etc.)
    
    Returns:
        str: Masked value appropriate for the PII type
    """
    if not value:
        return value
    
    if pii_type == "email":
        # Show first character, mask middle, show domain
        if "@" in value:
            username, domain = value.split("@", 1)
            
            if len(username) > 2:
                return f"{username[0]}{'*' * (len(username) - 2)}{username[-1]}@{domain}"
            else:
                return f"{'*' * len(username)}@{domain}"
        
    elif pii_type == "phone":
        # Show only last 4 digits
        clean_value = ''.join(c for c in value if c.isdigit())
        
        if len(clean_value) > 4:
            return f"{'*' * (len(clean_value) - 4)}{clean_value[-4:]}"
        
    elif pii_type == "name":
        # Show first character of each word, mask the rest
        words = value.split()
        masked_words = []
        
        for word in words:
            if len(word) > 1:
                masked_words.append(f"{word[0]}{'*' * (len(word) - 1)}")
            else:
                masked_words.append(word)
        
        return " ".join(masked_words)
    
    # Default masking: show first and last character, mask middle
    if len(value) > 2:
        return f"{value[0]}{'*' * (len(value) - 2)}{value[-1]}"
    else:
        return '*' * len(value)


class EncryptedField:
    """
    Descriptor class for automatically encrypting/decrypting model fields.
    """
    
    def __init__(self):
        self.name = None
        self.private_name = None
    
    def __set_name__(self, owner, name):
        """
        Set the descriptor name when used in a class.
        
        Args:
            owner (object): The owner class
            name (str): The field name
        """
        self.name = name
        self.private_name = f"_{name}"
    
    def __get__(self, instance, owner):
        """
        Get method that automatically decrypts the stored value.
        
        Args:
            instance (object): The instance being accessed
            owner (object): The owner class
            
        Returns:
            Any: Decrypted value or None
        """
        if instance is None:
            return self
        
        encrypted_value = getattr(instance, self.private_name, None)
        
        if not encrypted_value:
            return None
        
        return decrypt_string(encrypted_value)
    
    def __set__(self, instance, value):
        """
        Set method that automatically encrypts the assigned value.
        
        Args:
            instance (object): The instance being accessed
            value (Any): The value to encrypt and store
        """
        if value is None:
            setattr(instance, self.private_name, None)
        else:
            encrypted_value = encrypt_string(str(value))
            setattr(instance, self.private_name, encrypted_value)