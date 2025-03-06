import json
import os
import uuid
import base64
from typing import Dict, List, Any, Optional
from datetime import datetime

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives.ciphers.aead import AESGCM, ChaCha20Poly1305
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import secrets

class Password:
    """
    Class representing a stored password with metadata.
    """
    
    def __init__(self, 
                value: str,
                website: str = "",
                username: str = "",
                category: str = "General",
                notes: str = "",
                created: str = None,
                modified: str = None,
                id: str = None):
        """
        Initialize a password entry.
        
        Args:
            value: The password value (will be encrypted before storage)
            website: Associated website or service
            username: Associated username
            category: Category for organization
            notes: Additional notes
            created: Creation timestamp (generated if not provided)
            modified: Last modified timestamp (generated if not provided)
            id: Unique identifier (generated if not provided)
        """
        self.id = id if id else str(uuid.uuid4())
        self.value = value
        self.website = website
        self.username = username
        self.category = category
        self.notes = notes
        
        now = datetime.now().isoformat()
        self.created = created if created else now
        self.modified = modified if modified else now
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the password entry to a dictionary.
        
        Returns:
            Dictionary representation of the password entry
        """
        return {
            'id': self.id,
            'value': self.value,  # Note: This should be encrypted before storage
            'website': self.website,
            'username': self.username,
            'category': self.category,
            'notes': self.notes,
            'created': self.created,
            'modified': self.modified
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Password':
        """
        Create a password entry from a dictionary.
        
        Args:
            data: Dictionary containing password data
            
        Returns:
            A new Password instance
        """
        return cls(
            id=data.get('id'),
            value=data.get('value', ''),  # Note: This should be decrypted after retrieval
            website=data.get('website', ''),
            username=data.get('username', ''),
            category=data.get('category', 'General'),
            notes=data.get('notes', ''),
            created=data.get('created'),
            modified=data.get('modified')
        )
    
    def update(self, 
              value: str = None,
              website: str = None,
              username: str = None,
              category: str = None,
              notes: str = None) -> None:
        """
        Update the password entry.
        
        Args:
            value: New password value (if None, keep existing)
            website: New website (if None, keep existing)
            username: New username (if None, keep existing)
            category: New category (if None, keep existing)
            notes: New notes (if None, keep existing)
        """
        if value is not None:
            self.value = value
        if website is not None:
            self.website = website
        if username is not None:
            self.username = username
        if category is not None:
            self.category = category
        if notes is not None:
            self.notes = notes
            
        self.modified = datetime.now().isoformat()


class PasswordStorage:
    """
    Class for storing and retrieving password entries.
    """
    
    def __init__(self, 
                storage_file: str = 'passwords.json',
                key_file: str = 'encryption_key.key'):
        """
        Initialize the password storage.
        
        Args:
            storage_file: Name of the file to store passwords
            key_file: Name of the file to store the encryption key
        """
        # Get storage location from app settings
        self.app_settings = self._load_app_settings()
        storage_location = self.app_settings.get('storage_location', './storage')
        
        # Ensure storage directory exists
        if not os.path.exists(storage_location):
            os.makedirs(storage_location, exist_ok=True)
        
        # Set file paths
        self.storage_file = os.path.join(storage_location, storage_file)
        self.key_file = os.path.join(storage_location, key_file)
        
        # Initialize encryption
        self.cipher = self._initialize_encryption()
        
        # Load passwords
        self.passwords: List[Password] = []
        self._load_passwords()
    
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
    
    def _initialize_encryption(self):
        """
        Initialize or load the encryption key.
        
        Returns:
            Encryption cipher for the selected algorithm
        """
        # Get encryption algorithm from settings
        self.app_settings = self._load_app_settings()
        self.encryption_algorithm = self.app_settings.get('encryption_algorithm', 'fernet')
        
        # Salt is stored with key material
        self.salt = None
        self.nonce = None
        
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
    
    def _encrypt(self, data: str) -> str:
        """
        Encrypt a string with the current algorithm.
        
        Args:
            data: String to encrypt
            
        Returns:
            Base64-encoded encrypted string
        """
        if not data:
            return ""
            
        data_bytes = data.encode()
        encrypted = None
        
        if self.encryption_algorithm == 'fernet':
            # Use Fernet for encryption
            encrypted = self.cipher.encrypt(data_bytes)
        elif self.encryption_algorithm == 'aes-gcm':
            # Use AES-GCM for encryption
            # Generate a unique nonce for each encryption
            nonce = secrets.token_bytes(12)
            encrypted = nonce + self.cipher.encrypt(nonce, data_bytes, None)
        elif self.encryption_algorithm == 'chacha20':
            # Use ChaCha20Poly1305 for encryption
            # Generate a unique nonce for each encryption
            nonce = secrets.token_bytes(12)
            encrypted = nonce + self.cipher.encrypt(nonce, data_bytes, None)
        else:
            # Default to Fernet
            encrypted = self.cipher.encrypt(data_bytes)
        
        return base64.b64encode(encrypted).decode()
    
    def _decrypt(self, encrypted_data: str) -> str:
        """
        Decrypt data using the encryption key and current algorithm.
        
        Args:
            encrypted_data: Base64-encoded encrypted data
            
        Returns:
            Decrypted data
        """
        try:
            if not encrypted_data:
                return ""
                
            encrypted_bytes = base64.b64decode(encrypted_data)
            
            if self.encryption_algorithm == 'fernet':
                # Use Fernet for decryption
                decrypted_bytes = self.cipher.decrypt(encrypted_bytes)
            elif self.encryption_algorithm == 'aes-gcm':
                # Use AES-GCM for decryption
                # First 12 bytes are the nonce
                nonce = encrypted_bytes[:12]
                ciphertext = encrypted_bytes[12:]
                decrypted_bytes = self.cipher.decrypt(nonce, ciphertext, None)
            elif self.encryption_algorithm == 'chacha20':
                # Use ChaCha20Poly1305 for decryption
                # First 12 bytes are the nonce
                nonce = encrypted_bytes[:12]
                ciphertext = encrypted_bytes[12:]
                decrypted_bytes = self.cipher.decrypt(nonce, ciphertext, None)
            else:
                # Default to Fernet
                decrypted_bytes = self.cipher.decrypt(encrypted_bytes)
            
            return decrypted_bytes.decode()
        except Exception as e:
            print(f"Error decrypting data: {e}")
            return "[Error: Could not decrypt]"
    
    def update_encryption_algorithm(self, new_algorithm: str) -> None:
        """
        Change the encryption algorithm and re-encrypt all passwords.
        
        Args:
            new_algorithm: The new encryption algorithm to use
        """
        if new_algorithm not in ['fernet', 'aes-gcm', 'chacha20']:
            raise ValueError(f"Unsupported encryption algorithm: {new_algorithm}")
            
        # Get the current passwords (decrypted)
        current_passwords = self.get_all_passwords()
        
        # Change the algorithm
        old_algorithm = self.encryption_algorithm
        self.encryption_algorithm = new_algorithm
        
        # Initialize with new algorithm
        if new_algorithm == 'fernet':
            key = Fernet.generate_key()
            self._save_raw_key(key)
            self.cipher = Fernet(key)
        else:
            # For other algorithms, generate appropriate keys
            if new_algorithm == 'aes-gcm':
                key = secrets.token_bytes(32)  # 256 bits for AES-GCM
                self.salt = secrets.token_bytes(16)
                self.nonce = secrets.token_bytes(12)
                self.cipher = AESGCM(key)
            elif new_algorithm == 'chacha20':
                key = secrets.token_bytes(32)  # 256 bits for ChaCha20
                self.salt = secrets.token_bytes(16)
                self.nonce = secrets.token_bytes(12)
                self.cipher = ChaCha20Poly1305(key)
            
            self._save_key_material(key, self.salt, self.nonce)
        
        # Re-encrypt all passwords
        self.passwords = current_passwords
        self._save_passwords()
        
        # Update the app settings
        self.app_settings['encryption_algorithm'] = new_algorithm
        with open('app_settings.json', 'w') as f:
            json.dump(self.app_settings, f, indent=2)
    
    def rotate_encryption_key(self) -> None:
        """
        Rotate the encryption key while maintaining the same algorithm.
        """
        # Get the current passwords (decrypted)
        current_passwords = self.get_all_passwords()
        
        # Generate new key based on algorithm
        if self.encryption_algorithm == 'fernet':
            key = Fernet.generate_key()
            self._save_raw_key(key)
            self.cipher = Fernet(key)
        else:
            # For other algorithms, generate appropriate keys
            if self.encryption_algorithm == 'aes-gcm':
                key = secrets.token_bytes(32)  # 256 bits for AES-GCM
                self.salt = secrets.token_bytes(16)
                self.nonce = secrets.token_bytes(12)
                self.cipher = AESGCM(key)
            elif self.encryption_algorithm == 'chacha20':
                key = secrets.token_bytes(32)  # 256 bits for ChaCha20
                self.salt = secrets.token_bytes(16)
                self.nonce = secrets.token_bytes(12)
                self.cipher = ChaCha20Poly1305(key)
            
            self._save_key_material(key, self.salt, self.nonce)
        
        # Re-encrypt all passwords
        self.passwords = current_passwords
        self._save_passwords()
        
    def _load_passwords(self) -> None:
        """
        Load passwords from the storage file.
        """
        if os.path.exists(self.storage_file):
            try:
                with open(self.storage_file, 'r') as f:
                    data = json.load(f)
                    
                    # Decrypt password values
                    for entry in data:
                        if 'value' in entry:
                            try:
                                entry['value'] = self._decrypt(entry['value'])
                            except Exception:
                                entry['value'] = "[Decryption Error]"
                    
                    self.passwords = [Password.from_dict(entry) for entry in data]
            except (json.JSONDecodeError, IOError) as e:
                print(f"Error loading passwords: {e}")
                self.passwords = []
    
    def _save_passwords(self) -> None:
        """
        Save passwords to the storage file.
        """
        try:
            # Create a copy of the passwords with encrypted values
            encrypted_passwords = []
            for password in self.passwords:
                password_dict = password.to_dict()
                password_dict['value'] = self._encrypt(password_dict['value'])
                encrypted_passwords.append(password_dict)
            
            with open(self.storage_file, 'w') as f:
                json.dump(encrypted_passwords, f, indent=2)
        except IOError as e:
            print(f"Error saving passwords: {e}")
    
    def get_all_passwords(self) -> List[Password]:
        """
        Get all stored passwords.
        
        Returns:
            List of all password entries
        """
        return self.passwords
    
    def get_password_by_id(self, id: str) -> Optional[Password]:
        """
        Get a password by its ID.
        
        Args:
            id: ID of the password to retrieve
            
        Returns:
            The password entry if found, None otherwise
        """
        for password in self.passwords:
            if password.id == id:
                return password
        return None
    
    def search_passwords(self, 
                        query: str = None,
                        category: str = None,
                        website: str = None) -> List[Password]:
        """
        Search for passwords based on criteria.
        
        Args:
            query: Search query for website, username, or notes
            category: Filter by category
            website: Filter by website
            
        Returns:
            List of matching password entries
        """
        results = []
        
        for password in self.passwords:
            # Apply filters
            if query and not (
                query.lower() in password.website.lower() or
                query.lower() in password.username.lower() or
                query.lower() in password.notes.lower()
            ):
                continue
                
            if category and password.category.lower() != category.lower():
                continue
                
            if website and password.website.lower() != website.lower():
                continue
                
            results.append(password)
            
        return results
    
    def add_password(self, password: Password) -> None:
        """
        Add a new password.
        
        Args:
            password: The password entry to add
        """
        self.passwords.append(password)
        self._save_passwords()
    
    def update_password(self, id: str, updated_password: Password) -> bool:
        """
        Update an existing password.
        
        Args:
            id: ID of the password to update
            updated_password: The updated password entry
            
        Returns:
            True if the update was successful, False otherwise
        """
        for i, password in enumerate(self.passwords):
            if password.id == id:
                updated_password.id = id  # Ensure ID remains the same
                updated_password.created = password.created  # Preserve creation date
                updated_password.modified = datetime.now().isoformat()  # Update modification date
                self.passwords[i] = updated_password
                self._save_passwords()
                return True
        return False
    
    def delete_password(self, id: str) -> bool:
        """
        Delete a password.
        
        Args:
            id: ID of the password to delete
            
        Returns:
            True if the deletion was successful, False otherwise
        """
        for i, password in enumerate(self.passwords):
            if password.id == id:
                del self.passwords[i]
                self._save_passwords()
                return True
        return False
    
    def get_categories(self) -> List[str]:
        """
        Get all unique categories.
        
        Returns:
            List of unique category names
        """
        return sorted(list(set(password.category for password in self.passwords)))
    
    def get_websites(self) -> List[str]:
        """
        Get all unique websites.
        
        Returns:
            List of unique website names
        """
        return sorted(list(set(password.website for password in self.passwords if password.website)))
    
    def export_passwords(self, export_file: str, include_values: bool = False) -> bool:
        """
        Export passwords to a JSON file.
        
        Args:
            export_file: Path to the export file
            include_values: Whether to include password values in the export
            
        Returns:
            True if the export was successful, False otherwise
        """
        try:
            export_data = []
            
            for password in self.passwords:
                password_dict = password.to_dict()
                
                if not include_values:
                    password_dict['value'] = '[REDACTED]'
                
                export_data.append(password_dict)
            
            with open(export_file, 'w') as f:
                json.dump(export_data, f, indent=2)
                
            return True
        except IOError as e:
            print(f"Error exporting passwords: {e}")
            return False
    
    def import_passwords(self, import_file: str) -> int:
        """
        Import passwords from a JSON file.
        
        Args:
            import_file: Path to the import file
            
        Returns:
            Number of passwords imported
        """
        try:
            with open(import_file, 'r') as f:
                data = json.load(f)
            
            imported_count = 0
            
            for entry in data:
                # Skip entries with redacted values
                if 'value' in entry and entry['value'] == '[REDACTED]':
                    continue
                
                # Generate a new ID to avoid conflicts
                entry['id'] = str(uuid.uuid4())
                
                # Set creation and modification dates to now
                now = datetime.now().isoformat()
                entry['created'] = now
                entry['modified'] = now
                
                password = Password.from_dict(entry)
                self.add_password(password)
                imported_count += 1
            
            return imported_count
        except (json.JSONDecodeError, IOError) as e:
            print(f"Error importing passwords: {e}")
            return 0
