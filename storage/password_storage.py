import json
import os
import uuid
from typing import Dict, List, Any, Optional
from datetime import datetime
from cryptography.fernet import Fernet

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
    
    def _initialize_encryption(self) -> Fernet:
        """
        Initialize or load the encryption key.
        
        Returns:
            Fernet cipher for encryption/decryption
        """
        if os.path.exists(self.key_file):
            # Load existing key
            try:
                with open(self.key_file, 'rb') as f:
                    key = f.read()
            except IOError as e:
                print(f"Error loading encryption key: {e}")
                key = Fernet.generate_key()
                self._save_key(key)
        else:
            # Generate new key
            key = Fernet.generate_key()
            self._save_key(key)
        
        return Fernet(key)
    
    def _save_key(self, key: bytes) -> None:
        """
        Save the encryption key to file.
        
        Args:
            key: The encryption key to save
        """
        try:
            with open(self.key_file, 'wb') as f:
                f.write(key)
        except IOError as e:
            print(f"Error saving encryption key: {e}")
    
    def _encrypt(self, data: str) -> str:
        """
        Encrypt a string.
        
        Args:
            data: String to encrypt
            
        Returns:
            Base64-encoded encrypted string
        """
        return self.cipher.encrypt(data.encode()).decode()
    
    def _decrypt(self, encrypted_data: str) -> str:
        """
        Decrypt a string.
        
        Args:
            encrypted_data: Base64-encoded encrypted string
            
        Returns:
            Decrypted string
        """
        try:
            return self.cipher.decrypt(encrypted_data.encode()).decode()
        except Exception as e:
            print(f"Error decrypting data: {e}")
            return "[Decryption Error]"
    
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
