import flet as ft
from typing import List, Dict, Any, Optional, Callable
import os
import json

class SettingsTab:
    """
    Tab for configuring application settings.
    """
    
    def __init__(self, main_window):
        """
        Initialize the settings tab.
        
        Args:
            main_window: Reference to the main window
        """
        self.main_window = main_window
        self.settings_file = "app_settings.json"
        self.settings = self._load_settings()
        
        # UI components
        self.theme_dropdown = ft.Dropdown(
            label="Theme",
            hint_text="Select application theme",
            options=[
                ft.dropdown.Option("System", "system"),
                ft.dropdown.Option("Light", "light"),
                ft.dropdown.Option("Dark", "dark")
            ],
            value=self.settings.get("theme", "system"),
            on_change=self.save_theme_setting
        )
        
        self.auto_save_switch = ft.Switch(
            label="Auto-save generated passwords",
            value=self.settings.get("auto_save", False),
            on_change=self.save_auto_save_setting
        )
        
        self.clipboard_timeout = ft.Slider(
            min=5,
            max=60,
            divisions=11,
            label="{value} seconds",
            value=self.settings.get("clipboard_timeout", 30),
            on_change=self.save_clipboard_timeout
        )
        
        self.storage_location = ft.TextField(
            label="Storage Location",
            value=self.settings.get("storage_location", ""),
            hint_text="Path to store password files",
            on_change=self.save_storage_location
        )
        
        self.browse_button = ft.ElevatedButton(
            "Browse",
            icon=ft.icons.FOLDER_OPEN,
            on_click=self.browse_storage_location
        )
        
        self.backup_switch = ft.Switch(
            label="Create backups before saving",
            value=self.settings.get("create_backups", True),
            on_change=self.save_backup_setting
        )
        
        self.max_backups = ft.Slider(
            min=1,
            max=10,
            divisions=9,
            label="{value} backups",
            value=self.settings.get("max_backups", 3),
            on_change=self.save_max_backups
        )
        
        self.reset_button = ft.ElevatedButton(
            "Reset to Defaults",
            icon=ft.icons.RESTORE,
            on_click=self.reset_settings,
            style=ft.ButtonStyle(
                color=ft.colors.ERROR
            )
        )
    
    def build(self) -> ft.Container:
        """
        Build the settings tab UI.
        
        Returns:
            Container with the tab content
        """
        return ft.Container(
            content=ft.Column([
                ft.Text("Settings", size=24, weight=ft.FontWeight.BOLD),
                ft.Divider(),
                
                # Appearance section
                ft.Text("Appearance", size=18, weight=ft.FontWeight.BOLD),
                ft.Container(
                    content=ft.Column([
                        self.theme_dropdown
                    ]),
                    padding=10,
                    border=ft.border.all(1, ft.colors.OUTLINE),
                    border_radius=10,
                    margin=ft.margin.only(bottom=20)
                ),
                
                # Password Generation section
                ft.Text("Password Generation", size=18, weight=ft.FontWeight.BOLD),
                ft.Container(
                    content=ft.Column([
                        self.auto_save_switch,
                        ft.Text("Clear clipboard after:"),
                        self.clipboard_timeout
                    ]),
                    padding=10,
                    border=ft.border.all(1, ft.colors.OUTLINE),
                    border_radius=10,
                    margin=ft.margin.only(bottom=20)
                ),
                
                # Storage section
                ft.Text("Storage", size=18, weight=ft.FontWeight.BOLD),
                ft.Container(
                    content=ft.Column([
                        ft.Row([
                            self.storage_location,
                            self.browse_button
                        ]),
                        self.backup_switch,
                        ft.Text("Maximum number of backups:"),
                        self.max_backups
                    ]),
                    padding=10,
                    border=ft.border.all(1, ft.colors.OUTLINE),
                    border_radius=10,
                    margin=ft.margin.only(bottom=20)
                ),
                
                # Reset button
                ft.Container(
                    content=self.reset_button,
                    alignment=ft.alignment.center_right
                )
            ], scroll=ft.ScrollMode.AUTO),
            padding=20,
            expand=True
        )
    
    def _load_settings(self) -> Dict[str, Any]:
        """
        Load settings from the settings file.
        
        Returns:
            Dictionary of settings
        """
        default_settings = {
            "theme": "system",
            "auto_save": False,
            "clipboard_timeout": 30,
            "storage_location": "",
            "create_backups": True,
            "max_backups": 3
        }
        
        if os.path.exists(self.settings_file):
            try:
                with open(self.settings_file, 'r') as f:
                    settings = json.load(f)
                    
                    # Ensure all default settings exist
                    for key, value in default_settings.items():
                        if key not in settings:
                            settings[key] = value
                    
                    return settings
            except (json.JSONDecodeError, IOError) as e:
                print(f"Error loading settings: {e}")
        
        return default_settings
    
    def _save_settings(self):
        """
        Save settings to the settings file.
        """
        try:
            with open(self.settings_file, 'w') as f:
                json.dump(self.settings, f, indent=2)
        except IOError as e:
            print(f"Error saving settings: {e}")
            self.main_window.show_error(f"Error saving settings: {e}")
    
    def save_theme_setting(self, e):
        """
        Save the theme setting and update the application theme.
        
        Args:
            e: Change event
        """
        theme = e.control.value
        self.settings["theme"] = theme
        self._save_settings()
        
        # Update the main window theme
        if theme == "light":
            self.main_window.page.theme_mode = ft.ThemeMode.LIGHT
            self.main_window.app_bar.actions[0].icon = ft.icons.DARK_MODE
        elif theme == "dark":
            self.main_window.page.theme_mode = ft.ThemeMode.DARK
            self.main_window.app_bar.actions[0].icon = ft.icons.LIGHT_MODE
        else:  # system
            self.main_window.page.theme_mode = ft.ThemeMode.SYSTEM
            # Set icon based on system theme
            is_dark = self.main_window.page.platform_brightness == ft.ThemeMode.DARK
            self.main_window.app_bar.actions[0].icon = ft.icons.LIGHT_MODE if is_dark else ft.icons.DARK_MODE
        
        self.main_window.page.update()
    
    def save_auto_save_setting(self, e):
        """
        Save the auto-save setting.
        
        Args:
            e: Change event
        """
        self.settings["auto_save"] = self.auto_save_switch.value
        self._save_settings()
    
    def save_clipboard_timeout(self, e):
        """
        Save the clipboard timeout setting.
        
        Args:
            e: Change event
        """
        self.settings["clipboard_timeout"] = self.clipboard_timeout.value
        self._save_settings()
    
    def save_storage_location(self, e):
        """
        Save the storage location setting.
        
        Args:
            e: Change event
        """
        self.settings["storage_location"] = self.storage_location.value
        self._save_settings()
    
    def browse_storage_location(self, e):
        """
        Open a dialog to browse for a storage location.
        
        Args:
            e: Click event
        """
        def pick_directory_result(e: ft.FilePickerResultEvent):
            if e.path:
                self.storage_location.value = e.path
                self.settings["storage_location"] = e.path
                self._save_settings()
                self.main_window.page.update()
        
        # Create file picker
        file_picker = ft.FilePicker(on_result=pick_directory_result)
        self.main_window.page.overlay.append(file_picker)
        self.main_window.page.update()
        
        # Open directory picker
        file_picker.get_directory_path()
    
    def save_backup_setting(self, e):
        """
        Save the backup setting.
        
        Args:
            e: Change event
        """
        self.settings["create_backups"] = self.backup_switch.value
        self._save_settings()
        
        # Update max backups slider state
        self.max_backups.disabled = not self.backup_switch.value
        self.main_window.page.update()
    
    def save_max_backups(self, e):
        """
        Save the max backups setting.
        
        Args:
            e: Change event
        """
        self.settings["max_backups"] = self.max_backups.value
        self._save_settings()
    
    def reset_settings(self, e):
        """
        Reset settings to defaults.
        
        Args:
            e: Click event
        """
        def confirm_reset():
            # Reset to defaults
            self.settings = {
                "theme": "system",
                "auto_save": False,
                "clipboard_timeout": 30,
                "storage_location": "",
                "create_backups": True,
                "max_backups": 3
            }
            
            # Save settings
            self._save_settings()
            
            # Update UI
            self.theme_dropdown.value = self.settings["theme"]
            self.auto_save_switch.value = self.settings["auto_save"]
            self.clipboard_timeout.value = self.settings["clipboard_timeout"]
            self.storage_location.value = self.settings["storage_location"]
            self.backup_switch.value = self.settings["create_backups"]
            self.max_backups.value = self.settings["max_backups"]
            
            # Apply theme
            self.main_window.page.theme_mode = ft.ThemeMode.SYSTEM
            
            # Update UI
            self.main_window.page.update()
            
            # Show success message
            self.main_window.show_snackbar("Settings reset to defaults")
        
        # Show confirmation dialog
        self.main_window.show_confirm_dialog(
            "Reset Settings",
            "Are you sure you want to reset all settings to their default values?",
            confirm_reset
        )
