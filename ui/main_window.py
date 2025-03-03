import flet as ft
from typing import List, Dict, Any, Optional, Callable

from ui.generator_tab import GeneratorTab
from ui.storage_tab import StorageTab
from ui.constraints_tab import ConstraintsTab
from ui.settings_tab import SettingsTab

class MainWindow:
    """
    Main application window that contains all UI tabs.
    """
    
    def __init__(self, page: ft.Page):
        """
        Initialize the main window.
        
        Args:
            page: Flet page object
        """
        self.page = page
        self.page.title = "Password Generator"
        self.page.theme_mode = ft.ThemeMode.SYSTEM
        self.page.window_width = 900
        self.page.window_height = 700
        self.page.window_min_width = 600
        self.page.window_min_height = 500
        
        # Initialize tabs
        self.generator_tab = GeneratorTab(self)
        self.storage_tab = StorageTab(self)
        self.constraints_tab = ConstraintsTab(self)
        self.settings_tab = SettingsTab(self)
        
        # Create tab navigation
        self.tabs = ft.Tabs(
            selected_index=0,
            animation_duration=300,
            tabs=[
                ft.Tab(
                    text="Generator",
                    icon=ft.icons.PASSWORD,
                    content=self.generator_tab.build()
                ),
                ft.Tab(
                    text="Passwords",
                    icon=ft.icons.LIST,
                    content=self.storage_tab.build()
                ),
                ft.Tab(
                    text="Constraints",
                    icon=ft.icons.RULE,
                    content=self.constraints_tab.build()
                ),
                ft.Tab(
                    text="Settings",
                    icon=ft.icons.SETTINGS,
                    content=self.settings_tab.build()
                )
            ],
            expand=1
        )
        
        # Create app bar
        self.app_bar = ft.AppBar(
            title=ft.Text("Password Generator"),
            center_title=True,
            bgcolor=ft.colors.SURFACE_VARIANT,
            actions=[
                ft.IconButton(
                    icon=ft.icons.LIGHT_MODE,
                    tooltip="Toggle theme",
                    on_click=self.toggle_theme
                ),
                ft.IconButton(
                    icon=ft.icons.INFO,
                    tooltip="About",
                    on_click=self.show_about
                )
            ]
        )
        
        # Set up the page layout
        self.page.add(
            ft.Container(
                content=self.tabs,
                expand=True
            )
        )
        
        # Set the app bar
        self.page.appbar = self.app_bar
        
        # Update the page
        self.page.update()
    
    def toggle_theme(self, e):
        """
        Toggle between light and dark theme.
        
        Args:
            e: Click event
        """
        if self.page.theme_mode == ft.ThemeMode.DARK:
            self.page.theme_mode = ft.ThemeMode.LIGHT
            e.control.icon = ft.icons.DARK_MODE
        else:
            self.page.theme_mode = ft.ThemeMode.DARK
            e.control.icon = ft.icons.LIGHT_MODE
        
        self.page.update()
    
    def show_about(self, e):
        """
        Show the about dialog.
        
        Args:
            e: Click event
        """
        self.page.dialog = ft.AlertDialog(
            title=ft.Text("About Password Generator"),
            content=ft.Column([
                ft.Text("A secure password generator and manager."),
                ft.Text("Version 1.0.0"),
                ft.Text("© 2025"),
            ], tight=True),
            actions=[
                ft.TextButton("OK", on_click=self.close_dialog)
            ],
            actions_alignment=ft.MainAxisAlignment.END
        )
        
        self.page.dialog.open = True
        self.page.update()
    
    def close_dialog(self, e):
        """
        Close the current dialog.
        
        Args:
            e: Click event
        """
        self.page.dialog.open = False
        self.page.update()
    
    def show_snackbar(self, message: str):
        """
        Show a snackbar message.
        
        Args:
            message: Message to display
        """
        self.page.snack_bar = ft.SnackBar(
            content=ft.Text(message),
            action="Dismiss",
            action_color=ft.colors.PRIMARY
        )
        self.page.snack_bar.open = True
        self.page.update()
    
    def show_error(self, message: str):
        """
        Show an error dialog.
        
        Args:
            message: Error message to display
        """
        self.page.dialog = ft.AlertDialog(
            title=ft.Text("Error"),
            content=ft.Text(message),
            actions=[
                ft.TextButton("OK", on_click=self.close_dialog)
            ],
            actions_alignment=ft.MainAxisAlignment.END
        )
        
        self.page.dialog.open = True
        self.page.update()
    
    def show_confirm_dialog(self, title: str, message: str, on_confirm: Callable):
        """
        Show a confirmation dialog.
        
        Args:
            title: Dialog title
            message: Dialog message
            on_confirm: Function to call when confirmed
        """
        def confirm(e):
            self.close_dialog(e)
            on_confirm()
        
        self.page.dialog = ft.AlertDialog(
            title=ft.Text(title),
            content=ft.Text(message),
            actions=[
                ft.TextButton("Cancel", on_click=self.close_dialog),
                ft.TextButton("Confirm", on_click=confirm)
            ],
            actions_alignment=ft.MainAxisAlignment.END
        )
        
        self.page.dialog.open = True
        self.page.update()
    
    def navigate_to_tab(self, index: int):
        """
        Navigate to a specific tab.
        
        Args:
            index: Tab index to navigate to
        """
        self.tabs.selected_index = index
        self.page.update()
