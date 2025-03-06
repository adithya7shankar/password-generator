import os
import json
import time
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, asdict
import uuid

from storage.encryption import EncryptionManager

@dataclass
class Note:
    """
    Data class for a secure note.
    """
    id: Optional[str]  # UUID
    title: str
    content: str
    category: str
    created: int  # Unix timestamp
    updated: int  # Unix timestamp

class NotesStorage:
    """
    Storage manager for encrypted secure notes.
    """
    
    def __init__(self):
        """Initialize notes storage."""
        self.encryption_manager = EncryptionManager()
        self.notes_file = self._get_notes_file_path()
        self.notes = self._load_notes()
    
    def _get_notes_file_path(self) -> str:
        """
        Get the path to the notes storage file.
        
        Returns:
            Path to the notes file
        """
        # Use the same storage location as passwords
        storage_dir = self.encryption_manager.get_storage_directory()
        return os.path.join(storage_dir, "secure_notes.json")
    
    def _load_notes(self) -> Dict[str, Note]:
        """
        Load notes from storage.
        
        Returns:
            Dictionary of notes indexed by ID
        """
        notes = {}
        
        if not os.path.exists(self.notes_file):
            return notes
            
        try:
            encrypted_data = None
            with open(self.notes_file, "rb") as f:
                encrypted_data = f.read()
                
            if not encrypted_data:
                return notes
                
            decrypted_data = self.encryption_manager.decrypt(encrypted_data)
            notes_data = json.loads(decrypted_data.decode("utf-8"))
            
            for note_data in notes_data:
                note = Note(
                    id=note_data.get("id"),
                    title=note_data.get("title", ""),
                    content=note_data.get("content", ""),
                    category=note_data.get("category", ""),
                    created=note_data.get("created", int(time.time())),
                    updated=note_data.get("updated", int(time.time()))
                )
                notes[note.id] = note
                
        except Exception as e:
            print(f"Error loading notes: {str(e)}")
            
        return notes
    
    def _save_notes(self):
        """Save notes to storage."""
        try:
            notes_list = [asdict(note) for note in self.notes.values()]
            json_data = json.dumps(notes_list)
            
            encrypted_data = self.encryption_manager.encrypt(json_data.encode("utf-8"))
            
            # Ensure directory exists
            os.makedirs(os.path.dirname(self.notes_file), exist_ok=True)
            
            with open(self.notes_file, "wb") as f:
                f.write(encrypted_data)
                
        except Exception as e:
            print(f"Error saving notes: {str(e)}")
            raise
    
    def get_all_notes(self) -> List[Note]:
        """
        Get all notes.
        
        Returns:
            List of all notes
        """
        return list(self.notes.values())
    
    def get_note(self, note_id: str) -> Optional[Note]:
        """
        Get a note by ID.
        
        Args:
            note_id: ID of the note to retrieve
            
        Returns:
            The note if found, None otherwise
        """
        return self.notes.get(note_id)
    
    def add_note(self, note: Note) -> str:
        """
        Add a new note.
        
        Args:
            note: Note to add
            
        Returns:
            ID of the added note
        """
        # Generate ID if needed
        if not note.id:
            note.id = str(uuid.uuid4())
            
        # Ensure timestamps
        if not note.created:
            note.created = int(time.time())
        if not note.updated:
            note.updated = int(time.time())
            
        # Add to collection
        self.notes[note.id] = note
        
        # Save changes
        self._save_notes()
        
        return note.id
    
    def update_note(self, note: Note) -> bool:
        """
        Update an existing note.
        
        Args:
            note: Note to update
            
        Returns:
            True if successful, False otherwise
        """
        if not note.id or note.id not in self.notes:
            return False
            
        # Update timestamp
        note.updated = int(time.time())
        
        # Update in collection
        self.notes[note.id] = note
        
        # Save changes
        self._save_notes()
        
        return True
    
    def delete_note(self, note_id: str) -> bool:
        """
        Delete a note.
        
        Args:
            note_id: ID of the note to delete
            
        Returns:
            True if successful, False otherwise
        """
        if note_id not in self.notes:
            return False
            
        # Remove from collection
        del self.notes[note_id]
        
        # Save changes
        self._save_notes()
        
        return True
    
    def search_notes(self, term: str) -> List[Note]:
        """
        Search notes by title and content.
        
        Args:
            term: Search term
            
        Returns:
            List of matching notes
        """
        if not term:
            return list(self.notes.values())
            
        term = term.lower()
        matches = []
        
        for note in self.notes.values():
            if term in note.title.lower() or term in note.content.lower():
                matches.append(note)
                
        return matches 