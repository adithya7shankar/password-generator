import flet as ft
import os
import sys
import json
import shutil

from ui.main_window import MainWindow

def main(page: ft.Page):
    """
    Main application entry point.
    
    Args:
        page: Flet page object
    """
    # Initialize the main window
    app = MainWindow(page)

def ensure_app_directories():
    """
    Ensure all required application directories exist and files are in the right places.
    """
    # Load app settings
    app_settings_path = 'app_settings.json'
    if os.path.exists(app_settings_path):
        try:
            with open(app_settings_path, 'r') as f:
                app_settings = json.load(f)
        except Exception as e:
            print(f"Error loading app settings: {e}")
            app_settings = {'storage_location': './storage'}
    else:
        app_settings = {'storage_location': './storage'}
    
    # Ensure storage directory exists
    storage_dir = app_settings.get('storage_location', './storage')
    if not os.path.isabs(storage_dir):
        # If relative path, make it absolute based on the application path
        storage_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), storage_dir)
    
    if not os.path.exists(storage_dir):
        os.makedirs(storage_dir, exist_ok=True)
    
    # Check if we need to migrate the encryption key
    old_key_path = 'encryption_key.key'
    new_key_path = os.path.join(storage_dir, 'encryption_key.key')
    
    if os.path.exists(old_key_path) and not os.path.exists(new_key_path):
        # Migrate the key to the storage directory
        shutil.copy2(old_key_path, new_key_path)
        print(f"Migrated encryption key to {new_key_path}")

if __name__ == "__main__":
    # Set up environment
    if getattr(sys, 'frozen', False):
        # If the application is run as a bundle (e.g., PyInstaller)
        application_path = os.path.dirname(sys.executable)
    else:
        # If the application is run as a script
        application_path = os.path.dirname(os.path.abspath(__file__))
    
    # Change working directory to application path
    os.chdir(application_path)
    
    # Ensure application directories and files
    ensure_app_directories()
    
    # Start the application
    ft.app(target=main, view=ft.AppView.FLET_APP)
