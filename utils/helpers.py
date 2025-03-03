import os
import json
import shutil
from datetime import datetime
from typing import Dict, Any, List, Optional

def create_backup(file_path: str, max_backups: int = 3) -> bool:
    """
    Create a backup of a file.
    
    Args:
        file_path: Path to the file to backup
        max_backups: Maximum number of backups to keep
        
    Returns:
        True if backup was successful, False otherwise
    """
    if not os.path.exists(file_path):
        return False
    
    # Create backup directory if it doesn't exist
    backup_dir = os.path.join(os.path.dirname(file_path), "backups")
    os.makedirs(backup_dir, exist_ok=True)
    
    # Generate backup filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_name = os.path.basename(file_path)
    backup_name = f"{os.path.splitext(file_name)[0]}_{timestamp}{os.path.splitext(file_name)[1]}"
    backup_path = os.path.join(backup_dir, backup_name)
    
    try:
        # Create backup
        shutil.copy2(file_path, backup_path)
        
        # Clean up old backups if needed
        cleanup_old_backups(backup_dir, file_name, max_backups)
        
        return True
    except Exception as e:
        print(f"Error creating backup: {e}")
        return False

def cleanup_old_backups(backup_dir: str, original_filename: str, max_backups: int) -> None:
    """
    Remove old backups to keep only the specified number of most recent backups.
    
    Args:
        backup_dir: Directory containing backups
        original_filename: Original filename (without timestamp)
        max_backups: Maximum number of backups to keep
    """
    if not os.path.exists(backup_dir):
        return
    
    # Get all backup files for this original file
    base_name = os.path.splitext(original_filename)[0]
    extension = os.path.splitext(original_filename)[1]
    
    backup_files = []
    for filename in os.listdir(backup_dir):
        if filename.startswith(base_name + "_") and filename.endswith(extension):
            backup_files.append(os.path.join(backup_dir, filename))
    
    # Sort by modification time (newest first)
    backup_files.sort(key=lambda x: os.path.getmtime(x), reverse=True)
    
    # Remove excess backups
    for old_backup in backup_files[max_backups:]:
        try:
            os.remove(old_backup)
        except Exception as e:
            print(f"Error removing old backup {old_backup}: {e}")

def load_json_file(file_path: str, default_value: Any = None) -> Any:
    """
    Load data from a JSON file.
    
    Args:
        file_path: Path to the JSON file
        default_value: Value to return if file doesn't exist or is invalid
        
    Returns:
        Loaded data or default value
    """
    if not os.path.exists(file_path):
        return default_value
    
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError) as e:
        print(f"Error loading JSON file {file_path}: {e}")
        return default_value

def save_json_file(file_path: str, data: Any, create_backup: bool = False, max_backups: int = 3) -> bool:
    """
    Save data to a JSON file.
    
    Args:
        file_path: Path to the JSON file
        data: Data to save
        create_backup: Whether to create a backup of the existing file
        max_backups: Maximum number of backups to keep
        
    Returns:
        True if save was successful, False otherwise
    """
    # Create backup if requested and file exists
    if create_backup and os.path.exists(file_path):
        create_backup(file_path, max_backups)
    
    # Create directory if it doesn't exist
    os.makedirs(os.path.dirname(os.path.abspath(file_path)), exist_ok=True)
    
    try:
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2)
        return True
    except IOError as e:
        print(f"Error saving JSON file {file_path}: {e}")
        return False

def format_date(date_str: str, format_str: str = "%Y-%m-%d %H:%M") -> str:
    """
    Format a date string.
    
    Args:
        date_str: ISO format date string
        format_str: Format string for output
        
    Returns:
        Formatted date string
    """
    try:
        date = datetime.fromisoformat(date_str)
        return date.strftime(format_str)
    except (ValueError, TypeError):
        return "Unknown date"

def generate_unique_filename(base_path: str, base_name: str, extension: str) -> str:
    """
    Generate a unique filename by appending a number if the file already exists.
    
    Args:
        base_path: Directory path
        base_name: Base filename
        extension: File extension (with dot)
        
    Returns:
        Unique filename
    """
    counter = 0
    filename = f"{base_name}{extension}"
    file_path = os.path.join(base_path, filename)
    
    while os.path.exists(file_path):
        counter += 1
        filename = f"{base_name}_{counter}{extension}"
        file_path = os.path.join(base_path, filename)
    
    return filename
