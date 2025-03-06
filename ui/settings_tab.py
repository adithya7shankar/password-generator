import flet as ft
from typing import List, Dict, Any, Optional, Callable
import os
import json
import shutil
import datetime
from storage.password_storage import PasswordStorage

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
        
        # UI components with minimalist styling
        self.theme_dropdown = ft.Dropdown(
            label="Theme",
            hint_text="Select application theme",
            options=[
                ft.dropdown.Option("System", "system"),
                ft.dropdown.Option("Light", "light"),
                ft.dropdown.Option("Dark", "dark")
            ],
            value=self.settings.get("theme", "system"),
            on_change=self.save_theme_setting,
            expand=True,
            border_radius=8,
            width=None  # Allow the width to be determined by the parent container
        )
        
        self.auto_save_switch = ft.Switch(
            label="Auto-save generated passwords",
            value=self.settings.get("auto_save", False),
            on_change=self.save_auto_save_setting,
            active_color=ft.colors.BLUE_GREY,
            label_position=ft.LabelPosition.RIGHT
        )
        
        self.clipboard_timeout = ft.Slider(
            min=5,
            max=60,
            divisions=11,
            label="{value} seconds",
            value=self.settings.get("clipboard_timeout", 30),
            on_change=self.save_clipboard_timeout,
            active_color=ft.colors.BLUE_GREY,
            height=50,
            expand=True,
            width=None  # Allow the width to be determined by the parent container
        )
        
        # Auto logout feature
        self.auto_logout_switch = ft.Switch(
            label="Automatically log out after inactivity",
            value=self.settings.get("auto_logout", False),
            on_change=self.save_auto_logout_setting,
            active_color=ft.colors.BLUE_GREY,
            label_position=ft.LabelPosition.RIGHT
        )
        
        self.logout_timeout = ft.Slider(
            min=1,
            max=30,
            divisions=29,
            label="{value} minutes",
            value=self.settings.get("logout_timeout", 5),
            on_change=self.save_logout_timeout,
            active_color=ft.colors.BLUE_GREY,
            height=50,
            expand=True,
            disabled=not self.settings.get("auto_logout", False),
            width=None  # Allow the width to be determined by the parent container
        )
        
        self.storage_location = ft.TextField(
            label="Storage Location",
            value=self.settings.get("storage_location", ""),
            hint_text="Path to store password files",
            on_change=self.save_storage_location,
            expand=True,
            border_radius=8,
            width=None  # Allow the width to be determined by the parent container
        )
        
        self.browse_button = ft.FilledButton(
            "Browse",
            icon=ft.icons.FOLDER_OPEN,
            on_click=self.browse_storage_location,
            height=50
        )
        
        # Encryption settings
        self.encryption_algorithm = ft.Dropdown(
            label="Encryption Algorithm",
            hint_text="Select encryption algorithm",
            options=[
                ft.dropdown.Option("Fernet (Default)", "fernet"),
                ft.dropdown.Option("AES-GCM", "aes-gcm"),
                ft.dropdown.Option("ChaCha20-Poly1305", "chacha20"),
            ],
            value=self.settings.get("encryption_algorithm", "fernet"),
            on_change=self.save_encryption_algorithm,
            expand=True,
            border_radius=8,
            width=None  # Allow the width to be determined by the parent container
        )
        
        self.encryption_key_rotation = ft.Dropdown(
            label="Key Rotation Policy",
            hint_text="Select key rotation policy",
            options=[
                ft.dropdown.Option("Manual", "manual"),
                ft.dropdown.Option("Every month", "monthly"),
                ft.dropdown.Option("Every 3 months", "quarterly"),
                ft.dropdown.Option("Every year", "yearly"),
            ],
            value=self.settings.get("key_rotation", "manual"),
            on_change=self.save_key_rotation,
            expand=True,
            border_radius=8,
            width=None  # Allow the width to be determined by the parent container
        )
        
        self.rotate_key_button = ft.FilledButton(
            "Rotate Encryption Key",
            icon=ft.icons.REFRESH,
            on_click=self.rotate_encryption_key,
            height=50
        )
        
        self.backup_switch = ft.Switch(
            label="Create backups before saving",
            value=self.settings.get("create_backups", True),
            on_change=self.save_backup_setting,
            active_color=ft.colors.BLUE_GREY,
            label_position=ft.LabelPosition.RIGHT
        )
        
        self.max_backups = ft.Slider(
            min=1,
            max=10,
            divisions=9,
            label="{value} backups",
            value=self.settings.get("max_backups", 3),
            on_change=self.save_max_backups,
            active_color=ft.colors.BLUE_GREY,
            height=50,
            disabled=not self.settings.get("create_backups", True)
        )
        
        # Import/Export buttons
        self.export_button = ft.FilledButton(
            "Export Passwords",
            icon=ft.icons.UPLOAD_FILE,
            on_click=self.export_passwords,
            style=ft.ButtonStyle(
                color=ft.colors.PRIMARY
            ),
            height=50
        )
        
        self.import_button = ft.FilledButton(
            "Import Passwords",
            icon=ft.icons.DOWNLOAD_FILE,
            on_click=self.import_passwords,
            style=ft.ButtonStyle(
                color=ft.colors.PRIMARY
            ),
            height=50
        )
        
        # Backup/Restore buttons
        self.backup_button = ft.FilledButton(
            "Backup All Data",
            icon=ft.icons.BACKUP,
            on_click=self.backup_data,
            height=50
        )
        
        self.restore_button = ft.FilledButton(
            "Restore From Backup",
            icon=ft.icons.RESTORE,
            on_click=self.restore_data,
            height=50
        )
        
        # Reset button
        self.reset_button = ft.OutlinedButton(
            "Reset to Defaults",
            icon=ft.icons.RESTORE,
            on_click=self.reset_settings,
            style=ft.ButtonStyle(
                color=ft.colors.ERROR
            ),
            height=50
        )
    
    def build(self) -> ft.Container:
        """
        Build the settings tab UI with responsive minimalist design.
        
        Returns:
            Container with the tab content
        """
        return ft.Container(
            content=ft.Column([
                ft.Container(
                    content=ft.Text("Settings", size=28, weight=ft.FontWeight.W_300),
                    margin=ft.margin.only(bottom=20, top=10)
                ),
                
                # Responsive layout with two columns on larger screens
                ft.ResponsiveRow([
                    # Left column for theme and password generation
                    ft.Column([
                        # Appearance section
                        ft.Card(
                            content=ft.Container(
                                content=ft.Column([
                                    ft.Text("Appearance", size=16, weight=ft.FontWeight.W_500),
                                    ft.Divider(height=1, color=ft.colors.OUTLINE_VARIANT),
                                    ft.Container(height=20),
                                    ft.Text(
                                        "Choose how the application looks. System will match your device settings.",
                                        size=12,
                                        color=ft.colors.GREY_600
                                    ),
                                    ft.Container(height=10),
                                    self.theme_dropdown
                                ], spacing=10),
                                padding=25
                            ),
                            elevation=0,
                            color=ft.colors.SURFACE,
                            margin=ft.margin.only(bottom=20)
                        ),
                        
                        # Password Generation section
                        ft.Card(
                            content=ft.Container(
                                content=ft.Column([
                                    ft.Text("Password Generation", size=16, weight=ft.FontWeight.W_500),
                                    ft.Divider(height=1, color=ft.colors.OUTLINE_VARIANT),
                                    ft.Container(height=20),
                                    ft.Text(
                                        "Configure how passwords are generated and handled.",
                                        size=12,
                                        color=ft.colors.GREY_600
                                    ),
                                    ft.Container(height=10),
                                    self.auto_save_switch,
                                    ft.Container(height=20),
                                    ft.Text("Clear clipboard after:", size=14),
                                    ft.Container(height=10),
                                    self.clipboard_timeout,
                                    ft.Container(height=10),
                                    ft.Text(
                                        "For security, passwords in clipboard will be cleared automatically after this time.",
                                        size=12,
                                        color=ft.colors.GREY_600
                                    )
                                ], spacing=10),
                                padding=25
                            ),
                            elevation=0,
                            color=ft.colors.SURFACE,
                            margin=ft.margin.only(bottom=20)
                        ),
                        
                        # Security settings
                        ft.Card(
                            content=ft.Container(
                                content=ft.Column([
                                    ft.Text("Auto Logout", size=16, weight=ft.FontWeight.W_500),
                                    ft.Divider(height=1, color=ft.colors.OUTLINE_VARIANT),
                                    ft.Container(height=20),
                                    ft.Text(
                                        "Configure automatic logout for security.",
                                        size=12,
                                        color=ft.colors.GREY_600
                                    ),
                                    ft.Container(height=10),
                                    self.auto_logout_switch,
                                    ft.Container(height=20),
                                    ft.Text("Logout after inactivity:", size=14),
                                    ft.Container(height=10),
                                    self.logout_timeout,
                                    ft.Container(height=10),
                                    ft.Text(
                                        "The application will automatically lock after this period of inactivity.",
                                        size=12,
                                        color=ft.colors.GREY_600
                                    )
                                ], spacing=10),
                                padding=25
                            ),
                            elevation=0,
                            color=ft.colors.SURFACE
                        ),
                    ], col={"sm": 12, "md": 6, "lg": 6, "xl": 5}),
                    
                    # Right column for storage and security
                    ft.Column([
                        # Storage section
                        ft.Card(
                            content=ft.Container(
                                content=ft.Column([
                                    ft.Text("Storage", size=16, weight=ft.FontWeight.W_500),
                                    ft.Divider(height=1, color=ft.colors.OUTLINE_VARIANT),
                                    ft.Container(height=20),
                                    ft.Text(
                                        "Configure where your password data is stored.",
                                        size=12,
                                        color=ft.colors.GREY_600
                                    ),
                                    ft.Container(height=10),
                                    ft.Row([
                                        self.storage_location,
                                        ft.Container(width=15),
                                        self.browse_button
                                    ]),
                                    ft.Container(height=20),
                                    self.backup_switch,
                                    ft.Container(height=20),
                                    ft.Text("Maximum number of backups:", size=14),
                                    ft.Container(height=10),
                                    self.max_backups,
                                    ft.Container(height=10),
                                    ft.Text(
                                        "Old backups will be removed when this limit is reached.",
                                        size=12,
                                        color=ft.colors.GREY_600
                                    )
                                ], spacing=10),
                                padding=25
                            ),
                            elevation=0,
                            color=ft.colors.SURFACE,
                            margin=ft.margin.only(bottom=20)
                        ),
                        
                        # Security section
                        ft.Card(
                            content=ft.Container(
                                content=ft.Column([
                                    ft.Text("Security & Encryption", size=16, weight=ft.FontWeight.W_500),
                                    ft.Divider(height=1, color=ft.colors.OUTLINE_VARIANT),
                                    ft.Container(height=20),
                                    ft.Text(
                                        "Configure how your passwords are encrypted.",
                                        size=12,
                                        color=ft.colors.GREY_600
                                    ),
                                    ft.Container(height=10),
                                    self.encryption_algorithm,
                                    ft.Container(height=5),
                                    ft.Text(
                                        "Fernet: Fast and secure, good for most users\nAES-GCM: Advanced industry standard\nChaCha20: Best for older devices",
                                        size=12,
                                        color=ft.colors.GREY_600
                                    ),
                                    ft.Container(height=20),
                                    self.encryption_key_rotation,
                                    ft.Container(height=5),
                                    ft.Text(
                                        "Regularly rotating keys improves security. Manual gives you full control.",
                                        size=12,
                                        color=ft.colors.GREY_600
                                    ),
                                    ft.Container(
                                        content=self.rotate_key_button,
                                        alignment=ft.alignment.center,
                                        margin=ft.margin.only(top=20, bottom=15)
                                    ),
                                    ft.Text(
                                        "Note: Changing the encryption algorithm will re-encrypt all passwords.",
                                        size=12,
                                        color=ft.colors.RED_400,
                                        italic=True
                                    )
                                ], spacing=10),
                                padding=25
                            ),
                            elevation=0,
                            color=ft.colors.SURFACE,
                            margin=ft.margin.only(bottom=20)
                        ),
                        
                        # Import/Export section
                        ft.Card(
                            content=ft.Container(
                                content=ft.Column([
                                    ft.Text("Import & Export", size=16, weight=ft.FontWeight.W_500),
                                    ft.Divider(height=1, color=ft.colors.OUTLINE_VARIANT),
                                    ft.Container(height=20),
                                    ft.Text(
                                        "Transfer your passwords between devices or create backups.",
                                        size=12,
                                        color=ft.colors.GREY_600
                                    ),
                                    ft.Container(height=20),
                                    ft.Row([
                                        ft.Column([
                                            ft.Text("Passwords", size=14, weight=ft.FontWeight.W_500),
                                            ft.Row([
                                                self.export_button,
                                                ft.Container(width=10),
                                                self.import_button
                                            ])
                                        ], expand=True),
                                    ]),
                                    ft.Container(height=20),
                                    ft.Row([
                                        ft.Column([
                                            ft.Text("All Data", size=14, weight=ft.FontWeight.W_500),
                                            ft.Row([
                                                self.backup_button,
                                                ft.Container(width=10),
                                                self.restore_button
                                            ])
                                        ], expand=True),
                                    ])
                                ], spacing=10),
                                padding=25
                            ),
                            elevation=0,
                            color=ft.colors.SURFACE
                        ),
                    ], col={"sm": 12, "md": 6, "lg": 6, "xl": 7})
                ], spacing=20, expand=True),
                
                # Reset button (always at bottom)
                ft.Container(
                    content=self.reset_button,
                    alignment=ft.alignment.center_right,
                    margin=ft.margin.only(top=20, right=10, bottom=20)
                )
            ], spacing=10, scroll=ft.ScrollMode.AUTO),
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
            "max_backups": 3,
            "encryption_algorithm": "fernet",
            "key_rotation": "manual",
            "auto_logout": False,
            "logout_timeout": 5
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
        elif theme == "dark":
            self.main_window.page.theme_mode = ft.ThemeMode.DARK
        else:  # system
            self.main_window.page.theme_mode = ft.ThemeMode.SYSTEM
            
        # Update the theme toggle icon in the app bar
        for action in self.main_window.app_bar.actions:
            if isinstance(action, ft.IconButton) and action.tooltip == "Toggle Theme":
                if self.main_window.page.theme_mode == ft.ThemeMode.DARK:
                    action.icon = ft.icons.LIGHT_MODE
                else:
                    action.icon = ft.icons.DARK_MODE
        
        # Apply the theme change
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
    
    def save_auto_logout_setting(self, e):
        """
        Save the auto logout setting.
        
        Args:
            e: Change event
        """
        self.settings["auto_logout"] = self.auto_logout_switch.value
        self._save_settings()
        
        # Update logout timeout slider state
        self.logout_timeout.disabled = not self.auto_logout_switch.value
        self.main_window.page.update()
    
    def save_logout_timeout(self, e):
        """
        Save the logout timeout setting.
        
        Args:
            e: Change event
        """
        self.settings["logout_timeout"] = self.logout_timeout.value
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
    
    def save_encryption_algorithm(self, e):
        """
        Save the encryption algorithm setting.
        
        Args:
            e: Change event
        """
        new_algorithm = e.control.value
        old_algorithm = self.settings.get("encryption_algorithm", "fernet")
        
        if new_algorithm != old_algorithm:
            def confirm_algorithm_change():
                self.settings["encryption_algorithm"] = new_algorithm
                self._save_settings()
                
                # Re-encrypt all passwords with the new algorithm
                try:
                    storage = PasswordStorage()
                    storage.update_encryption_algorithm(new_algorithm)
                    self.main_window.show_snackbar(f"Encryption algorithm changed to {new_algorithm}")
                except Exception as ex:
                    self.main_window.show_error(f"Error changing encryption algorithm: {str(ex)}")
                    # Revert UI
                    e.control.value = old_algorithm
                    self.main_window.page.update()
            
            # Show confirmation dialog
            self.main_window.show_confirm_dialog(
                "Change Encryption Algorithm",
                "This will re-encrypt all your passwords with the new algorithm. This operation cannot be undone. Continue?",
                confirm_algorithm_change
            )
        else:
            # No change, just save
            self.settings["encryption_algorithm"] = new_algorithm
            self._save_settings()
    
    def save_key_rotation(self, e):
        """
        Save the key rotation policy setting.
        
        Args:
            e: Change event
        """
        self.settings["key_rotation"] = e.control.value
        self._save_settings()
    
    def rotate_encryption_key(self, e):
        """
        Rotate the encryption key immediately.
        
        Args:
            e: Click event
        """
        def confirm_key_rotation():
            try:
                storage = PasswordStorage()
                storage.rotate_encryption_key()
                self.main_window.show_snackbar("Encryption key rotated successfully")
            except Exception as ex:
                self.main_window.show_error(f"Error rotating encryption key: {str(ex)}")
        
        # Show confirmation dialog
        self.main_window.show_confirm_dialog(
            "Rotate Encryption Key",
            "This will generate a new encryption key and re-encrypt all passwords. Continue?",
            confirm_key_rotation
        )
    
    def export_passwords(self, e):
        """
        Export passwords to a file.
        
        Args:
            e: Click event
        """
        def pick_save_result(e: ft.FilePickerResultEvent):
            if e.path:
                try:
                    # Use the PasswordStorage class to export passwords
                    storage = PasswordStorage()
                    
                    # Ask whether to include password values
                    def export_with_values():
                        try:
                            result = storage.export_passwords(e.path, include_values=True)
                            if result:
                                self.main_window.show_snackbar(f"Passwords exported to {e.path}")
                            else:
                                self.main_window.show_error(f"Failed to export passwords")
                        except Exception as ex:
                            self.main_window.show_error(f"Error exporting passwords: {str(ex)}")
                    
                    def export_without_values():
                        try:
                            result = storage.export_passwords(e.path, include_values=False)
                            if result:
                                self.main_window.show_snackbar(f"Passwords exported to {e.path}")
                            else:
                                self.main_window.show_error(f"Failed to export passwords")
                        except Exception as ex:
                            self.main_window.show_error(f"Error exporting passwords: {str(ex)}")
                    
                    # Show dialog to ask about including values
                    self.main_window.page.dialog = ft.AlertDialog(
                        title=ft.Text("Export Options", weight=ft.FontWeight.W_300),
                        content=ft.Text("Do you want to include the actual password values in the export file?"),
                        actions=[
                            ft.TextButton("No (Safer)", on_click=lambda _: (self.main_window.close_dialog(_), export_without_values())),
                            ft.TextButton("Yes (Include passwords)", on_click=lambda _: (self.main_window.close_dialog(_), export_with_values()))
                        ],
                        actions_alignment=ft.MainAxisAlignment.END
                    )
                    self.main_window.page.dialog.open = True
                    self.main_window.page.update()
                    
                except Exception as ex:
                    self.main_window.show_error(f"Error exporting passwords: {str(ex)}")
        
        # Create file picker
        file_picker = ft.FilePicker(on_result=pick_save_result)
        self.main_window.page.overlay.append(file_picker)
        self.main_window.page.update()
        
        # Open save dialog
        file_picker.save_file(
            dialog_title="Export Passwords",
            file_name="passwords.json",
            allowed_extensions=["json"]
        )
    
    def import_passwords(self, e):
        """
        Import passwords from a file.
        
        Args:
            e: Click event
        """
        def pick_file_result(e: ft.FilePickerResultEvent):
            if e.path:
                def confirm_import():
                    try:
                        # Use the PasswordStorage class to import passwords
                        storage = PasswordStorage()
                        imported_count = storage.import_passwords(e.path)
                        
                        if imported_count > 0:
                            self.main_window.show_snackbar(f"Successfully imported {imported_count} passwords")
                            
                            # Refresh the storage tab
                            if hasattr(self.main_window, 'storage_tab') and hasattr(self.main_window.storage_tab, '_load_passwords'):
                                self.main_window.storage_tab._load_passwords()
                        else:
                            self.main_window.show_error("No passwords were imported")
                            
                    except Exception as ex:
                        self.main_window.show_error(f"Error importing passwords: {str(ex)}")
                
                # Show confirmation dialog
                self.main_window.show_confirm_dialog(
                    "Import Passwords",
                    "This will import passwords from the selected file. Continue?",
                    confirm_import
                )
        
        # Create file picker
        file_picker = ft.FilePicker(on_result=pick_file_result)
        self.main_window.page.overlay.append(file_picker)
        self.main_window.page.update()
        
        # Open file picker
        file_picker.pick_files(
            dialog_title="Import Passwords",
            allowed_extensions=["json"],
            allow_multiple=False
        )
    
    def backup_data(self, e):
        """
        Backup all application data.
        
        Args:
            e: Click event
        """
        def pick_directory_result(e: ft.FilePickerResultEvent):
            if e.path:
                try:
                    # Create backup directory with timestamp
                    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                    backup_dir = os.path.join(e.path, f"password_generator_backup_{timestamp}")
                    os.makedirs(backup_dir, exist_ok=True)
                    
                    # Get storage location
                    storage_dir = self.settings.get("storage_location", "./storage")
                    if not os.path.isabs(storage_dir):
                        storage_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", storage_dir)
                    
                    # Copy password files to backup directory
                    if os.path.exists(storage_dir):
                        for filename in os.listdir(storage_dir):
                            src_file = os.path.join(storage_dir, filename)
                            if os.path
