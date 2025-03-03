import json
import os
from typing import Dict, List, Any, Optional
import uuid

class ConstraintSet:
    """
    Class representing a set of password constraints.
    """
    
    def __init__(self, 
                name: str,
                min_length: int = 8,
                max_length: int = 20,
                require_uppercase: bool = True,
                require_lowercase: bool = True,
                require_digits: bool = True,
                require_special: bool = True,
                included_chars: List[str] = None,
                excluded_chars: List[str] = None,
                id: str = None):
        """
        Initialize a constraint set with the given parameters.
        
        Args:
            name: Name of the constraint set
            min_length: Minimum password length
            max_length: Maximum password length
            require_uppercase: Whether uppercase letters are required
            require_lowercase: Whether lowercase letters are required
            require_digits: Whether digits are required
            require_special: Whether special characters are required
            included_chars: List of characters that must be included
            excluded_chars: List of characters that must be excluded
            id: Unique identifier for the constraint set (generated if not provided)
        """
        self.id = id if id else str(uuid.uuid4())
        self.name = name
        self.min_length = min_length
        self.max_length = max_length
        self.require_uppercase = require_uppercase
        self.require_lowercase = require_lowercase
        self.require_digits = require_digits
        self.require_special = require_special
        self.included_chars = included_chars if included_chars else []
        self.excluded_chars = excluded_chars if excluded_chars else []
        
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the constraint set to a dictionary.
        
        Returns:
            Dictionary representation of the constraint set
        """
        return {
            'id': self.id,
            'name': self.name,
            'min_length': self.min_length,
            'max_length': self.max_length,
            'require_uppercase': self.require_uppercase,
            'require_lowercase': self.require_lowercase,
            'require_digits': self.require_digits,
            'require_special': self.require_special,
            'included_chars': self.included_chars,
            'excluded_chars': self.excluded_chars
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ConstraintSet':
        """
        Create a constraint set from a dictionary.
        
        Args:
            data: Dictionary containing constraint set data
            
        Returns:
            A new ConstraintSet instance
        """
        return cls(
            id=data.get('id'),
            name=data.get('name', 'Unnamed Constraint Set'),
            min_length=data.get('min_length', 8),
            max_length=data.get('max_length', 20),
            require_uppercase=data.get('require_uppercase', True),
            require_lowercase=data.get('require_lowercase', True),
            require_digits=data.get('require_digits', True),
            require_special=data.get('require_special', True),
            included_chars=data.get('included_chars', []),
            excluded_chars=data.get('excluded_chars', [])
        )


class ConstraintManager:
    """
    Class for managing password constraint sets.
    """
    
    def __init__(self, storage_file: str = 'constraint_sets.json'):
        """
        Initialize the constraint manager.
        
        Args:
            storage_file: Path to the file where constraint sets are stored
        """
        self.storage_file = storage_file
        self.constraint_sets = []
        self._load_constraint_sets()
        
        # Create default constraint sets if none exist
        if not self.constraint_sets:
            self._create_default_constraint_sets()
    
    def _load_constraint_sets(self) -> None:
        """
        Load constraint sets from the storage file.
        """
        if os.path.exists(self.storage_file):
            try:
                with open(self.storage_file, 'r') as f:
                    data = json.load(f)
                    self.constraint_sets = [ConstraintSet.from_dict(cs) for cs in data]
            except (json.JSONDecodeError, IOError) as e:
                print(f"Error loading constraint sets: {e}")
                self.constraint_sets = []
    
    def _save_constraint_sets(self) -> None:
        """
        Save constraint sets to the storage file.
        """
        try:
            with open(self.storage_file, 'w') as f:
                json.dump([cs.to_dict() for cs in self.constraint_sets], f, indent=2)
        except IOError as e:
            print(f"Error saving constraint sets: {e}")
    
    def _create_default_constraint_sets(self) -> None:
        """
        Create default constraint sets.
        """
        default_sets = [
            ConstraintSet(
                name="Standard",
                min_length=8,
                max_length=16,
                require_uppercase=True,
                require_lowercase=True,
                require_digits=True,
                require_special=True
            ),
            ConstraintSet(
                name="Strong",
                min_length=12,
                max_length=24,
                require_uppercase=True,
                require_lowercase=True,
                require_digits=True,
                require_special=True,
                included_chars=['!', '@', '#', '$']
            ),
            ConstraintSet(
                name="Simple",
                min_length=6,
                max_length=12,
                require_uppercase=True,
                require_lowercase=True,
                require_digits=True,
                require_special=False,
                excluded_chars=['!', '@', '#', '$', '%', '^', '&', '*', '(', ')', '+', '=']
            )
        ]
        
        for cs in default_sets:
            self.add_constraint_set(cs)
    
    def get_all_constraint_sets(self) -> List[ConstraintSet]:
        """
        Get all constraint sets.
        
        Returns:
            List of all constraint sets
        """
        return self.constraint_sets
    
    def get_constraint_set_by_id(self, id: str) -> Optional[ConstraintSet]:
        """
        Get a constraint set by its ID.
        
        Args:
            id: ID of the constraint set to retrieve
            
        Returns:
            The constraint set if found, None otherwise
        """
        for cs in self.constraint_sets:
            if cs.id == id:
                return cs
        return None
    
    def get_constraint_set_by_name(self, name: str) -> Optional[ConstraintSet]:
        """
        Get a constraint set by its name.
        
        Args:
            name: Name of the constraint set to retrieve
            
        Returns:
            The constraint set if found, None otherwise
        """
        for cs in self.constraint_sets:
            if cs.name.lower() == name.lower():
                return cs
        return None
    
    def add_constraint_set(self, constraint_set: ConstraintSet) -> None:
        """
        Add a new constraint set.
        
        Args:
            constraint_set: The constraint set to add
        """
        self.constraint_sets.append(constraint_set)
        self._save_constraint_sets()
    
    def update_constraint_set(self, id: str, updated_set: ConstraintSet) -> bool:
        """
        Update an existing constraint set.
        
        Args:
            id: ID of the constraint set to update
            updated_set: The updated constraint set
            
        Returns:
            True if the update was successful, False otherwise
        """
        for i, cs in enumerate(self.constraint_sets):
            if cs.id == id:
                updated_set.id = id  # Ensure ID remains the same
                self.constraint_sets[i] = updated_set
                self._save_constraint_sets()
                return True
        return False
    
    def delete_constraint_set(self, id: str) -> bool:
        """
        Delete a constraint set.
        
        Args:
            id: ID of the constraint set to delete
            
        Returns:
            True if the deletion was successful, False otherwise
        """
        for i, cs in enumerate(self.constraint_sets):
            if cs.id == id:
                del self.constraint_sets[i]
                self._save_constraint_sets()
                return True
        return False
    
    def validate_constraints(self, constraints: Dict[str, Any]) -> List[str]:
        """
        Validate a set of constraints.
        
        Args:
            constraints: Dictionary of constraints to validate
            
        Returns:
            List of validation errors, empty if valid
        """
        errors = []
        
        # Check min/max length
        min_length = constraints.get('min_length', 0)
        max_length = constraints.get('max_length', 0)
        
        if min_length < 1:
            errors.append("Minimum length must be at least 1")
        
        if max_length < min_length:
            errors.append("Maximum length must be greater than or equal to minimum length")
        
        # Check character requirements
        require_any = (
            constraints.get('require_uppercase', False) or
            constraints.get('require_lowercase', False) or
            constraints.get('require_digits', False) or
            constraints.get('require_special', False)
        )
        
        if not require_any and not constraints.get('included_chars'):
            errors.append("At least one character type must be required")
        
        # Check for conflicts between included and excluded chars
        included = set(constraints.get('included_chars', []))
        excluded = set(constraints.get('excluded_chars', []))
        
        conflicts = included.intersection(excluded)
        if conflicts:
            errors.append(f"Characters {', '.join(conflicts)} cannot be both included and excluded")
        
        return errors
