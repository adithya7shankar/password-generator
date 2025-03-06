import flet as ft
import os
import sys
import json
import shutil
import logging
from logging.handlers import RotatingFileHandler

# Configure logging
def setup_logging():
    """
    Set up logging with file rotation and console output.
    """
    log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logs')
    os.makedirs(log_dir, exist_ok=True)
    log_path = os.path.join(log_dir, 'password_generator.log')
    
    # Configure root logger
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            # File handler with rotation
            RotatingFileHandler(
                log_path, 
                maxBytes=10*1024*1024,  # 10 MB
                backupCount=5
            ),
            # Console handler
            logging.StreamHandler(sys.stdout)
        ]
    )

from ui.main_window import MainWindow

def main(page: ft.Page):
    """
    Main application entry point with error handling.
    
    Args:
        page: Flet page object
    """
    logger = logging.getLogger(__name__)
    try:
        # Initialize the main window
        app = MainWindow(page)
        logger.info("Application initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize application: {e}", exc_info=True)
        page.dialog = ft.AlertDialog(
            title=ft.Text("Initialization Error"),
            content=ft.Text(f"Could not start the application: {e}"),
            actions=[
                ft.TextButton("Close", on_click=lambda _: page.window_close())
            ]
        )
        page.dialog.open = True
        page.update()

def ensure_app_directories():
    """
    Ensure all required application directories exist and files are in the right places.
    Includes robust error handling and logging.
    """
    logger = logging.getLogger(__name__)
    
    # Load app settings
    app_settings_path = 'app_settings.json'
    try:
        if os.path.exists(app_settings_path):
            with open(app_settings_path, 'r') as f:
                app_settings = json.load(f)
        else:
            logger.warning("App settings file not found. Using default settings.")
            app_settings = {'storage_location': './storage'}
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in app settings: {e}")
        app_settings = {'storage_location': './storage'}
    except Exception as e:
        logger.error(f"Unexpected error reading app settings: {e}")
        app_settings = {'storage_location': './storage'}
    
    # Ensure storage directory exists
    storage_dir = app_settings.get('storage_location', './storage')
    if not os.path.isabs(storage_dir):
        # If relative path, make it absolute based on the application path
        storage_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), storage_dir)
    
    try:
        os.makedirs(storage_dir, exist_ok=True)
        logger.info(f"Ensured storage directory exists: {storage_dir}")
    except Exception as e:
        logger.error(f"Could not create storage directory: {e}")
        raise
    
    # Check if we need to migrate the encryption key
    old_key_path = 'encryption_key.key'
    new_key_path = os.path.join(storage_dir, 'encryption_key.key')
    
    try:
        if os.path.exists(old_key_path) and not os.path.exists(new_key_path):
            # Migrate the key to the storage directory
            shutil.copy2(old_key_path, new_key_path)
            logger.info(f"Migrated encryption key to {new_key_path}")
    except Exception as e:
        logger.error(f"Error migrating encryption key: {e}")

if __name__ == "__main__":
    # Set up logging first
    setup_logging()
    logger = logging.getLogger(__name__)
    
    try:
        # Set up environment
        if getattr(sys, 'frozen', False):
            # If the application is run as a bundle (e.g., PyInstaller)
            application_path = os.path.dirname(sys.executable)
        else:
            # If the application is run as a script
            application_path = os.path.dirname(os.path.abspath(__file__))
        
        # Change working directory to application path
        os.chdir(application_path)
        
        # Ensure application directories
        ensure_app_directories()
        
        # Start the application
        ft.app(target=main, view=ft.AppView.FLET_APP)
    
    except Exception as e:
        logger.critical(f"Unhandled exception in main application: {e}", exc_info=True)
        sys.exit(1)
