import os
import json
import base64
from typing import Dict, Any, Optional
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives.ciphers.aead import AESGCM, ChaCha20Poly1305
import secrets

class EncryptionManager:
    """
    Handles encryption/decryption operations for the application.
    """
    
    def __init__(self, key_file: str = 'encryption_key.key'):
        """
        Initialize the encryption manager.
        
        Args:
            key_file: Name of the file to store the encryption key
        """
        # Get storage location from app settings
        self.app_settings = self._load_app_settings()
        self.storage_dir = self.app_settings.get('storage_location', './storage')
        
        # Ensure storage directory exists
        if not os.path.exists(self.storage_dir):
            os.makedirs(self.storage_dir, exist_ok=True)
        
        # Set key file path
        self.key_file = os.path.join(self.storage_dir, key_file)
        
        # Get encryption algorithm from settings
        self.encryption_algorithm = self.app_settings.get('encryption_algorithm', 'fernet')
        
        # Salt is stored with key material
        self.salt = None
        self.nonce = None
        
        # Initialize the cipher
        self.cipher = self._initialize_encryption()
    
    def _load_app_settings(self) -> Dict[str, Any]:
        """
        Load application settings from json file.
        
        Returns:
            Dictionary of application settings
        """
        app_settings_path = 'app_settings.json'
        if os.path.exists(app_settings_path):
            try:
                with open(app_settings_path, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading app settings: {e}")
        return {'storage_location': './storage'}
    
    def get_storage_directory(self) -> str:
        """
        Get the storage directory path.
        
        Returns:
            Path to the storage directory
        """
        return self.storage_dir
    
    def _initialize_encryption(self):
        """
        Initialize or load the encryption key.
        
        Returns:
            Encryption cipher for the selected algorithm
        """
        if os.path.exists(self.key_file):
            # Load existing key
            try:
                with open(self.key_file, 'rb') as f:
                    file_content = f.read()
                    
                try:
                    # Try to parse as JSON (new format)
                    key_data = json.loads(file_content.decode('utf-8'))
                    key = base64.b64decode(key_data['key'])
                    
                    # Load additional parameters if available
                    if 'salt' in key_data:
                        self.salt = base64.b64decode(key_data['salt'])
                    if 'nonce' in key_data:
                        self.nonce = base64.b64decode(key_data['nonce'])
                    
                    # For Fernet, we need the key in a specific format
                    if self.encryption_algorithm == 'fernet':
                        return Fernet(file_content if isinstance(file_content, bytes) else file_content.encode())
                    elif self.encryption_algorithm == 'aes-gcm':
                        return AESGCM(key)
                    elif self.encryption_algorithm == 'chacha20':
                        return ChaCha20Poly1305(key)
                    else:
                        # Default to Fernet
                        return Fernet(Fernet.generate_key())
                    
                except json.JSONDecodeError:
                    # This is the old format with just a raw Fernet key
                    print("Using existing Fernet key")
                    # Use the raw key directly with Fernet
                    return Fernet(file_content)
                    
            except Exception as e:
                print(f"Error loading encryption key: {e}, generating new key")
                # Generate a new key for the algorithm
                if self.encryption_algorithm == 'fernet':
                    key = Fernet.generate_key()
                    self._save_raw_key(key)
                    return Fernet(key)
                else:
                    # For other algorithms, generate appropriate keys
                    if self.encryption_algorithm == 'aes-gcm':
                        key = secrets.token_bytes(32)  # 256 bits for AES-GCM
                        self.salt = secrets.token_bytes(16)
                        self.nonce = secrets.token_bytes(12)
                    elif self.encryption_algorithm == 'chacha20':
                        key = secrets.token_bytes(32)  # 256 bits for ChaCha20
                        self.salt = secrets.token_bytes(16)
                        self.nonce = secrets.token_bytes(12)
                    
                    self._save_key_material(key, self.salt, self.nonce)
                    
                    if self.encryption_algorithm == 'aes-gcm':
                        return AESGCM(key)
                    elif self.encryption_algorithm == 'chacha20':
                        return ChaCha20Poly1305(key)
        else:
            # No existing key, generate a new one
            if self.encryption_algorithm == 'fernet':
                key = Fernet.generate_key()
                self._save_raw_key(key)
                return Fernet(key)
            else:
                # For other algorithms, generate appropriate keys
                if self.encryption_algorithm == 'aes-gcm':
                    key = secrets.token_bytes(32)  # 256 bits for AES-GCM
                    self.salt = secrets.token_bytes(16)
                    self.nonce = secrets.token_bytes(12)
                elif self.encryption_algorithm == 'chacha20':
                    key = secrets.token_bytes(32)  # 256 bits for ChaCha20
                    self.salt = secrets.token_bytes(16)
                    self.nonce = secrets.token_bytes(12)
                
                self._save_key_material(key, self.salt, self.nonce)
                
                if self.encryption_algorithm == 'aes-gcm':
                    return AESGCM(key)
                elif self.encryption_algorithm == 'chacha20':
                    return ChaCha20Poly1305(key)
    
    def _save_raw_key(self, key: bytes) -> None:
        """
        Save a raw encryption key to file.
        
        Args:
            key: The encryption key to save
        """
        try:
            with open(self.key_file, 'wb') as f:
                f.write(key)
        except IOError as e:
            print(f"Error saving encryption key: {e}")
    
    def _save_key_material(self, key: bytes, salt: bytes = None, nonce: bytes = None) -> None:
        """
        Save the encryption key and related material to file.
        
        Args:
            key: The encryption key to save
            salt: Salt for key derivation
            nonce: Nonce for encryption
        """
        try:
            # Store key material as JSON with base64 encoding
            key_data = {
                'key': base64.b64encode(key).decode('utf-8'),
                'algorithm': self.encryption_algorithm
            }
            
            if salt:
                key_data['salt'] = base64.b64encode(salt).decode('utf-8')
            if nonce:
                key_data['nonce'] = base64.b64encode(nonce).decode('utf-8')
            
            with open(self.key_file, 'wb') as f:
                f.write(json.dumps(key_data).encode('utf-8'))
        except IOError as e:
            print(f"Error saving encryption key: {e}")
    
    def encrypt(self, data: bytes) -> bytes:
        """
        Encrypt data using the current algorithm.
        
        Args:
            data: Data to encrypt
            
        Returns:
            Encrypted data
        """
        if not data:
            return b""
            
        if self.encryption_algorithm == 'fernet':
            # Use Fernet for encryption
            return self.cipher.encrypt(data)
        elif self.encryption_algorithm == 'aes-gcm':
            # Use AES-GCM for encryption
            # Generate a unique nonce for each encryption
            nonce = secrets.token_bytes(12)
            return nonce + self.cipher.encrypt(nonce, data, None)
        elif self.encryption_algorithm == 'chacha20':
            # Use ChaCha20Poly1305 for encryption
            # Generate a unique nonce for each encryption
            nonce = secrets.token_bytes(12)
            return nonce + self.cipher.encrypt(nonce, data, None)
        else:
            # Default to Fernet
            return self.cipher.encrypt(data)
    
    def decrypt(self, encrypted_data: bytes) -> bytes:
        """
        Decrypt data using the current algorithm.
        
        Args:
            encrypted_data: Encrypted data
            
        Returns:
            Decrypted data
        """
        if not encrypted_data:
            return b""
            
        if self.encryption_algorithm == 'fernet':
            # Use Fernet for decryption
            return self.cipher.decrypt(encrypted_data)
        elif self.encryption_algorithm == 'aes-gcm':
            # Use AES-GCM for decryption
            # First 12 bytes are the nonce
            nonce = encrypted_data[:12]
            ciphertext = encrypted_data[12:]
            return self.cipher.decrypt(nonce, ciphertext, None)
        elif self.encryption_algorithm == 'chacha20':
            # Use ChaCha20Poly1305 for decryption
            # First 12 bytes are the nonce
            nonce = encrypted_data[:12]
            ciphertext = encrypted_data[12:]
            return self.cipher.decrypt(nonce, ciphertext, None)
        else:
            # Default to Fernet
            return self.cipher.decrypt(encrypted_data)
