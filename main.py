import flet as ft
import os
import sys

from ui.main_window import MainWindow

def main(page: ft.Page):
    """
    Main application entry point.
    
    Args:
        page: Flet page object
    """
    # Initialize the main window
    app = MainWindow(page)

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
    
    # Start the application
    ft.app(target=main, view=ft.AppView.FLET_APP)
