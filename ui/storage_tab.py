import flet as ft
from typing import List, Dict, Any, Optional, Callable
from datetime import datetime

from storage.password_storage import PasswordStorage, Password

class StorageTab:
    """
    Tab for viewing and managing stored passwords.
    """
    
    def __init__(self, main_window):
        """
        Initialize the storage tab.
        
        Args:
            main_window: Reference to the main window
        """
        self.main_window = main_window
        self.password_storage = PasswordStorage()
        
        # UI components
        self.search_input = ft.TextField(
            label="Search",
            hint_text="Search by website, username, or notes",
            prefix_icon=ft.icons.SEARCH,
            on_change=self.search_passwords,
            expand=True,
            border_radius=8  # Add border radius for consistent styling
        )
        
        self.category_filter = ft.Dropdown(
            label="Category",
            hint_text="Filter by category",
            on_change=self.search_passwords,
            options=[ft.dropdown.Option("All Categories")],
            value="All Categories"
        )
        
        # Add refresh button
        self.refresh_button = ft.IconButton(
            icon=ft.icons.REFRESH,
            tooltip="Refresh password list",
            on_click=self.refresh_passwords
        )
        
        self.password_list = ft.ListView(
            expand=True,
            spacing=10,
            padding=10,
            auto_scroll=False
        )
        
        # Password details components
        self.selected_password = None
        
        self.password_value = ft.TextField(
            label="Password",
            read_only=True,
            password=True,
            suffix=ft.Row([
                ft.IconButton(
                    icon=ft.icons.VISIBILITY,
                    tooltip="Show/Hide Password",
                    on_click=self.toggle_password_visibility
                ),
                ft.IconButton(
                    icon=ft.icons.COPY,
                    tooltip="Copy to Clipboard",
                    on_click=self.copy_password_value
                )
            ], spacing=0)
        )
        
        self.website_value = ft.TextField(
            label="Website/Service",
            read_only=True
        )
        
        self.username_value = ft.TextField(
            label="Username/Email",
            read_only=True,
            suffix=ft.IconButton(
                icon=ft.icons.COPY,
                tooltip="Copy to Clipboard",
                on_click=self.copy_username_value
            )
        )
        
        self.category_value = ft.TextField(
            label="Category",
            read_only=True
        )
        
        self.notes_value = ft.TextField(
            label="Notes",
            read_only=True,
            multiline=True,
            min_lines=2,
            max_lines=4
        )
        
        self.created_value = ft.TextField(
            label="Created",
            read_only=True
        )
        
        self.modified_value = ft.TextField(
            label="Last Modified",
            read_only=True
        )
        
        # Password details card
        self.password_details = ft.Card(
            content=ft.Container(
                content=ft.Column([
                    ft.ListTile(
                        title=ft.Text("Password Details", size=20),
                        subtitle=ft.Text("Select a password to view details")
                    ),
                    ft.Divider(),
                    self.password_value,
                    ft.Row([
                        self.website_value,
                        self.username_value
                    ]),
                    self.category_value,
                    self.notes_value,
                    ft.Row([
                        self.created_value,
                        self.modified_value
                    ]),
                    ft.Row([
                        ft.ElevatedButton(
                            "Edit",
                            icon=ft.icons.EDIT,
                            on_click=self.edit_password,
                            disabled=True,
                            ref=ft.Ref()
                        ),
                        ft.ElevatedButton(
                            "Delete",
                            icon=ft.icons.DELETE,
                            on_click=self.delete_password,
                            disabled=True,
                            ref=ft.Ref(),
                            style=ft.ButtonStyle(
                                color=ft.colors.ERROR
                            )
                        )
                    ], alignment=ft.MainAxisAlignment.END)
                ]),
                padding=20
            )
        )
        
        # Export/Import buttons
        self.export_button = ft.ElevatedButton(
            "Export Passwords",
            icon=ft.icons.UPLOAD,
            on_click=self.export_passwords
        )
        
        self.import_button = ft.ElevatedButton(
            "Import Passwords",
            icon=ft.icons.DOWNLOAD,
            on_click=self.import_passwords
        )
        
        # Load initial data
        self._load_categories()
        self._load_passwords()
    
    def build(self) -> ft.Container:
        """
        Build the storage tab UI.
        
        Returns:
            Container with the tab content
        """
        return ft.Container(
            content=ft.Column([
                ft.Text("Stored Passwords", size=24, weight=ft.FontWeight.BOLD),
                ft.Divider(),
                
                # Search and filter section
                ft.Row([
                    self.search_input,
                    self.category_filter,
                    self.refresh_button
                ]),
                
                # Password list and details section
                ft.ResponsiveRow([
                    # Password list
                    ft.Container(
                        content=ft.Column([
                            ft.Text("Passwords", size=18, weight=ft.FontWeight.BOLD),
                            ft.Container(
                                content=self.password_list,
                                border=ft.border.all(1, ft.colors.OUTLINE),
                                border_radius=10,
                                padding=10,
                                expand=True
                            )
                        ], expand=True),
                        expand=True,
                        margin=ft.margin.only(right=10),
                        col={"sm": 12, "md": 6, "lg": 5, "xl": 4}
                    ),
                    
                    # Password details
                    ft.Container(
                        content=ft.Column([
                            self.password_details
                        ], expand=True),
                        expand=True,
                        margin=ft.margin.only(left=10),
                        col={"sm": 12, "md": 6, "lg": 7, "xl": 8}
                    )
                ], expand=True),
                
                # Export/Import section
                ft.Row([
                    self.export_button,
                    self.import_button
                ], alignment=ft.MainAxisAlignment.END)
            ], expand=True),
            padding=20,
            expand=True
        )
    
    def _load_categories(self):
        """
        Load categories into the category filter dropdown.
        """
        categories = self.password_storage.get_categories()
        
        options = [ft.dropdown.Option("All Categories")]
        for category in categories:
            options.append(ft.dropdown.Option(category))
        
        self.category_filter.options = options
    
    def _load_passwords(self):
        """
        Load passwords into the password list.
        """
        self.password_list.controls.clear()
        
        passwords = self.password_storage.get_all_passwords()
        
        if not passwords:
            self.password_list.controls.append(
                ft.Text("No passwords found", italic=True, color=ft.colors.GREY_500)
            )
        else:
            for password in passwords:
                self._add_password_to_list(password)
        
        self.main_window.page.update()
    
    def _add_password_to_list(self, password: Password):
        """
        Add a password to the password list.
        
        Args:
            password: Password to add
        """
        # Create a card for the password
        card_content = ft.Container(
            content=ft.Column([
                ft.ListTile(
                    title=ft.Text(
                        password.website or "Unnamed Password",
                        weight=ft.FontWeight.BOLD
                    ),
                    subtitle=ft.Text(password.username or "No username"),
                    trailing=ft.Icon(ft.icons.ARROW_FORWARD_IOS)
                ),
                ft.Container(
                    content=ft.Row([
                        ft.Container(
                            content=ft.Text(
                                password.category,
                                size=12,
                                color=ft.colors.ON_SURFACE_VARIANT
                            ),
                            padding=ft.padding.only(left=15, right=15, top=5, bottom=5),
                            border_radius=15,
                            bgcolor=ft.colors.SURFACE_VARIANT
                        ),
                        ft.Text(
                            self._format_date(password.modified),
                            size=12,
                            color=ft.colors.GREY_600
                        )
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    padding=ft.padding.only(left=15, right=15, bottom=10)
                )
            ])
        )
        
        # Create a gesture detector to handle clicks
        password_id = password.id
        gesture_detector = ft.GestureDetector(
            content=card_content,
            on_tap=lambda e: self._show_password_details(password_id)
        )
        
        # Add the card to the list
        self.password_list.controls.append(
            ft.Card(
                content=gesture_detector
            )
        )
    
    def _format_date(self, date_str: str) -> str:
        """
        Format a date string for display.
        
        Args:
            date_str: ISO format date string
            
        Returns:
            Formatted date string
        """
        try:
            date = datetime.fromisoformat(date_str)
            return date.strftime("%Y-%m-%d %H:%M")
        except (ValueError, TypeError):
            return "Unknown date"
    
    def _show_password_details(self, password_id: str):
        """
        Show details for a selected password.
        
        Args:
            password_id: ID of the password to show
        """
        password = self.password_storage.get_password_by_id(password_id)
        
        if not password:
            return
        
        self.selected_password = password
        
        # Update UI fields
        self.password_value.value = password.value
        self.password_value.password = True  # Ensure password is initially hidden
        
        # Make sure buttons associated with password field have correct icons
        for control in self.password_value.suffix.controls:
            if isinstance(control, ft.IconButton) and control.tooltip == "Show/Hide Password":
                control.icon = ft.icons.VISIBILITY  # Show the "visibility" icon when password is hidden
        
        self.website_value.value = password.website
        self.username_value.value = password.username
        self.category_value.value = password.category
        self.notes_value.value = password.notes
        self.created_value.value = self._format_date(password.created)
        self.modified_value.value = self._format_date(password.modified)
        
        # Get button references
        edit_button = None
        delete_button = None
        
        for control in self.password_details.content.content.controls[-1].controls:
            if isinstance(control, ft.ElevatedButton):
                if control.text == "Edit":
                    edit_button = control
                elif control.text == "Delete":
                    delete_button = control
        
        # Enable buttons if found
        if edit_button:
            edit_button.disabled = False
        if delete_button:
            delete_button.disabled = False
        
        # Update UI
        self.main_window.page.update()
    
    def search_passwords(self, e):
        """
        Search passwords based on search input and category filter.
        
        Args:
            e: Change event
        """
        self.password_list.controls.clear()
        
        query = self.search_input.value or ""
        category = self.category_filter.value
        
        if category == "All Categories":
            category = None
        
        passwords = self.password_storage.search_passwords(query=query, category=category)
        
        if not passwords:
            self.password_list.controls.append(
                ft.Text("No passwords found", italic=True, color=ft.colors.GREY_500)
            )
        else:
            for password in passwords:
                self._add_password_to_list(password)
        
        self.main_window.page.update()
    
    def toggle_password_visibility(self, e):
        """
        Toggle password visibility.
        
        Args:
            e: Click event
        """
        self.password_value.password = not self.password_value.password
        
        if self.password_value.password:
            e.control.icon = ft.icons.VISIBILITY
        else:
            e.control.icon = ft.icons.VISIBILITY_OFF
        
        self.main_window.page.update()
    
    def copy_password_value(self, e):
        """
        Copy password value to clipboard.
        
        Args:
            e: Click event
        """
        if self.password_value.value:
            self.main_window.page.set_clipboard(self.password_value.value)
            self.main_window.show_snackbar("Password copied to clipboard")
    
    def copy_username_value(self, e):
        """
        Copy username value to clipboard.
        
        Args:
            e: Click event
        """
        if self.username_value.value:
            self.main_window.page.set_clipboard(self.username_value.value)
            self.main_window.show_snackbar("Username copied to clipboard")
    
    def edit_password(self, e):
        """
        Edit the selected password.
        
        Args:
            e: Click event
        """
        if not self.selected_password:
            return
        
        # Create edit dialog
        website_input = ft.TextField(
            label="Website/Service",
            value=self.selected_password.website
        )
        
        username_input = ft.TextField(
            label="Username/Email",
            value=self.selected_password.username
        )
        
        category_input = ft.Dropdown(
            label="Category",
            options=[
                ft.dropdown.Option("General"),
                ft.dropdown.Option("Work"),
                ft.dropdown.Option("Personal"),
                ft.dropdown.Option("Finance"),
                ft.dropdown.Option("Social"),
                ft.dropdown.Option("Other")
            ],
            value=self.selected_password.category
        )
        
        notes_input = ft.TextField(
            label="Notes",
            multiline=True,
            min_lines=2,
            max_lines=4,
            value=self.selected_password.notes
        )
        
        def save_changes(e):
            # Update password
            self.selected_password.update(
                website=website_input.value,
                username=username_input.value,
                category=category_input.value,
                notes=notes_input.value
            )
            
            # Save to storage
            self.password_storage.update_password(
                self.selected_password.id,
                self.selected_password
            )
            
            # Close dialog
            self.main_window.close_dialog(e)
            
            # Refresh UI
            self._show_password_details(self.selected_password.id)
            self._load_passwords()
            
            # Show success message
            self.main_window.show_snackbar("Password updated successfully")
        
        # Show dialog
        self.main_window.page.dialog = ft.AlertDialog(
            title=ft.Text("Edit Password"),
            content=ft.Column([
                website_input,
                username_input,
                category_input,
                notes_input
            ], tight=True, spacing=10),
            actions=[
                ft.TextButton("Cancel", on_click=self.main_window.close_dialog),
                ft.TextButton("Save", on_click=save_changes)
            ],
            actions_alignment=ft.MainAxisAlignment.END
        )
        
        self.main_window.page.dialog.open = True
        self.main_window.page.update()
    
    def delete_password(self, e):
        """
        Delete the selected password.
        
        Args:
            e: Click event
        """
        if not self.selected_password:
            return
        
        def confirm_delete():
            # Delete from storage
            self.password_storage.delete_password(self.selected_password.id)
            
            # Clear selection
            self.selected_password = None
            
            # Clear details
            self.password_value.value = ""
            self.website_value.value = ""
            self.username_value.value = ""
            self.category_value.value = ""
            self.notes_value.value = ""
            self.created_value.value = ""
            self.modified_value.value = ""
            
            # Disable buttons
            for control in self.password_details.content.content.controls[-1].controls:
                if isinstance(control, ft.ElevatedButton):
                    control.disabled = True
            
            # Refresh password list
            self._load_passwords()
            
            # Show success message
            self.main_window.show_snackbar("Password deleted successfully")
        
        # Show confirmation dialog
        self.main_window.show_confirm_dialog(
            "Delete Password",
            f"Are you sure you want to delete the password for '{self.selected_password.website}'?",
            confirm_delete
        )
    
    def export_passwords(self, e):
        """
        Export passwords to a file.
        
        Args:
            e: Click event
        """
        # Create export dialog
        filename_input = ft.TextField(
            label="Filename",
            value="passwords_export.json"
        )
        
        include_values_checkbox = ft.Checkbox(
            label="Include password values (security risk)",
            value=False
        )
        
        def do_export(e):
            # Export passwords
            success = self.password_storage.export_passwords(
                filename_input.value,
                include_values_checkbox.value
            )
            
            # Close dialog
            self.main_window.close_dialog(e)
            
            # Show result
            if success:
                self.main_window.show_snackbar(f"Passwords exported to {filename_input.value}")
            else:
                self.main_window.show_error("Failed to export passwords")
        
        # Show dialog
        self.main_window.page.dialog = ft.AlertDialog(
            title=ft.Text("Export Passwords"),
            content=ft.Column([
                ft.Text("Export your passwords to a JSON file."),
                filename_input,
                include_values_checkbox
            ], tight=True, spacing=10),
            actions=[
                ft.TextButton("Cancel", on_click=self.main_window.close_dialog),
                ft.TextButton("Export", on_click=do_export)
            ],
            actions_alignment=ft.MainAxisAlignment.END
        )
        
        self.main_window.page.dialog.open = True
        self.main_window.page.update()
    
    def import_passwords(self, e):
        """
        Import passwords from a file.
        
        Args:
            e: Click event
        """
        # Create import dialog
        filename_input = ft.TextField(
            label="Filename",
            hint_text="Enter the path to the JSON file"
        )
        
        def do_import(e):
            # Import passwords
            count = self.password_storage.import_passwords(filename_input.value)
            
            # Close dialog
            self.main_window.close_dialog(e)
            
            # Refresh categories and passwords
            self._load_categories()
            self._load_passwords()
            
            # Show result
            if count > 0:
                self.main_window.show_snackbar(f"Imported {count} passwords successfully")
            else:
                self.main_window.show_error("No passwords were imported")
        
        # Show dialog
        self.main_window.page.dialog = ft.AlertDialog(
            title=ft.Text("Import Passwords"),
            content=ft.Column([
                ft.Text("Import passwords from a JSON file."),
                filename_input,
                ft.Text(
                    "Note: This will not overwrite existing passwords.",
                    size=12,
                    color=ft.colors.GREY_700
                )
            ], tight=True, spacing=10),
            actions=[
                ft.TextButton("Cancel", on_click=self.main_window.close_dialog),
                ft.TextButton("Import", on_click=do_import)
            ],
            actions_alignment=ft.MainAxisAlignment.END
        )
        
        self.main_window.page.dialog.open = True
        self.main_window.page.update()

    def refresh_passwords(self, e):
        """
        Refresh the password list when the refresh button is clicked.
        
        Args:
            e: Click event
        """
        # Reload categories
        self._load_categories()
        
        # Reload passwords
        self._load_passwords()
        
        # Show confirmation
        self.main_window.show_snackbar("Password list refreshed")
