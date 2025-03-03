import flet as ft
from typing import List, Dict, Any, Optional, Callable

from constraints.constraint_manager import ConstraintManager, ConstraintSet

class ConstraintsTab:
    """
    Tab for managing password constraint sets.
    """
    
    def __init__(self, main_window):
        """
        Initialize the constraints tab.
        
        Args:
            main_window: Reference to the main window
        """
        self.main_window = main_window
        self.constraint_manager = ConstraintManager()
        
        # UI components
        self.constraint_list = ft.ListView(
            expand=True,
            spacing=10,
            padding=10,
            auto_scroll=False
        )
        
        # Selected constraint set
        self.selected_constraint = None
        
        # Constraint details components
        self.name_value = ft.TextField(
            label="Name",
            read_only=True
        )
        
        self.min_length_value = ft.TextField(
            label="Minimum Length",
            read_only=True
        )
        
        self.max_length_value = ft.TextField(
            label="Maximum Length",
            read_only=True
        )
        
        self.require_uppercase_value = ft.TextField(
            label="Require Uppercase",
            read_only=True
        )
        
        self.require_lowercase_value = ft.TextField(
            label="Require Lowercase",
            read_only=True
        )
        
        self.require_digits_value = ft.TextField(
            label="Require Digits",
            read_only=True
        )
        
        self.require_special_value = ft.TextField(
            label="Require Special Characters",
            read_only=True
        )
        
        self.included_chars_value = ft.TextField(
            label="Included Characters",
            read_only=True
        )
        
        self.excluded_chars_value = ft.TextField(
            label="Excluded Characters",
            read_only=True
        )
        
        # Constraint details card
        self.constraint_details = ft.Card(
            content=ft.Container(
                content=ft.Column([
                    ft.ListTile(
                        title=ft.Text("Constraint Set Details", size=20),
                        subtitle=ft.Text("Select a constraint set to view details")
                    ),
                    ft.Divider(),
                    self.name_value,
                    ft.Row([
                        self.min_length_value,
                        self.max_length_value
                    ]),
                    ft.Row([
                        self.require_uppercase_value,
                        self.require_lowercase_value
                    ]),
                    ft.Row([
                        self.require_digits_value,
                        self.require_special_value
                    ]),
                    self.included_chars_value,
                    self.excluded_chars_value,
                    ft.Row([
                        ft.ElevatedButton(
                            "Edit",
                            icon=ft.icons.EDIT,
                            on_click=self.edit_constraint_set,
                            disabled=True,
                            ref=ft.Ref()
                        ),
                        ft.ElevatedButton(
                            "Delete",
                            icon=ft.icons.DELETE,
                            on_click=self.delete_constraint_set,
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
        
        # Load initial data
        self._load_constraint_sets()
    
    def build(self) -> ft.Container:
        """
        Build the constraints tab UI.
        
        Returns:
            Container with the tab content
        """
        return ft.Container(
            content=ft.Column([
                ft.Text("Constraint Sets", size=24, weight=ft.FontWeight.BOLD),
                ft.Divider(),
                
                # Add new constraint set button
                ft.Container(
                    content=ft.ElevatedButton(
                        "Add New Constraint Set",
                        icon=ft.icons.ADD,
                        on_click=self.add_constraint_set,
                        style=ft.ButtonStyle(
                            shape=ft.RoundedRectangleBorder(radius=10)
                        )
                    ),
                    alignment=ft.alignment.center_right,
                    margin=ft.margin.only(bottom=10)
                ),
                
                # Constraint list and details section
                ft.Row([
                    # Constraint list
                    ft.Container(
                        content=ft.Column([
                            ft.Text("Constraint Sets", size=18, weight=ft.FontWeight.BOLD),
                            ft.Container(
                                content=self.constraint_list,
                                border=ft.border.all(1, ft.colors.OUTLINE),
                                border_radius=10,
                                padding=10,
                                expand=True
                            )
                        ]),
                        expand=True,
                        margin=ft.margin.only(right=10)
                    ),
                    
                    # Constraint details
                    ft.Container(
                        content=ft.Column([
                            self.constraint_details
                        ]),
                        expand=True,
                        margin=ft.margin.only(left=10)
                    )
                ], expand=True)
            ], expand=True),
            padding=20,
            expand=True
        )
    
    def _load_constraint_sets(self):
        """
        Load constraint sets into the constraint list.
        """
        self.constraint_list.controls.clear()
        
        constraint_sets = self.constraint_manager.get_all_constraint_sets()
        
        if not constraint_sets:
            self.constraint_list.controls.append(
                ft.Text("No constraint sets found", italic=True, color=ft.colors.GREY_500)
            )
        else:
            for cs in constraint_sets:
                self._add_constraint_to_list(cs)
        
        self.main_window.page.update()
    
    def _add_constraint_to_list(self, constraint_set: ConstraintSet):
        """
        Add a constraint set to the constraint list.
        
        Args:
            constraint_set: Constraint set to add
        """
        # Create a card for the constraint set
        card_content = ft.Container(
            content=ft.Column([
                ft.ListTile(
                    title=ft.Text(
                        constraint_set.name,
                        weight=ft.FontWeight.BOLD
                    ),
                    subtitle=ft.Text(f"Length: {constraint_set.min_length}-{constraint_set.max_length}"),
                    trailing=ft.Icon(ft.icons.ARROW_FORWARD_IOS)
                ),
                ft.Container(
                    content=ft.Row([
                        ft.Container(
                            content=ft.Text(
                                "Uppercase" if constraint_set.require_uppercase else "",
                                size=12,
                                color=ft.colors.ON_SURFACE_VARIANT
                            ),
                            padding=ft.padding.only(left=10, right=10, top=5, bottom=5),
                            border_radius=15,
                            bgcolor=ft.colors.SURFACE_VARIANT if constraint_set.require_uppercase else ft.colors.TRANSPARENT
                        ),
                        ft.Container(
                            content=ft.Text(
                                "Lowercase" if constraint_set.require_lowercase else "",
                                size=12,
                                color=ft.colors.ON_SURFACE_VARIANT
                            ),
                            padding=ft.padding.only(left=10, right=10, top=5, bottom=5),
                            border_radius=15,
                            bgcolor=ft.colors.SURFACE_VARIANT if constraint_set.require_lowercase else ft.colors.TRANSPARENT
                        ),
                        ft.Container(
                            content=ft.Text(
                                "Digits" if constraint_set.require_digits else "",
                                size=12,
                                color=ft.colors.ON_SURFACE_VARIANT
                            ),
                            padding=ft.padding.only(left=10, right=10, top=5, bottom=5),
                            border_radius=15,
                            bgcolor=ft.colors.SURFACE_VARIANT if constraint_set.require_digits else ft.colors.TRANSPARENT
                        ),
                        ft.Container(
                            content=ft.Text(
                                "Special" if constraint_set.require_special else "",
                                size=12,
                                color=ft.colors.ON_SURFACE_VARIANT
                            ),
                            padding=ft.padding.only(left=10, right=10, top=5, bottom=5),
                            border_radius=15,
                            bgcolor=ft.colors.SURFACE_VARIANT if constraint_set.require_special else ft.colors.TRANSPARENT
                        )
                    ], alignment=ft.MainAxisAlignment.START, spacing=5),
                    padding=ft.padding.only(left=15, right=15, bottom=10)
                )
            ])
        )
        
        # Create a gesture detector to handle clicks
        cs_id = constraint_set.id
        gesture_detector = ft.GestureDetector(
            content=card_content,
            on_tap=lambda e: self._show_constraint_details(cs_id)
        )
        
        # Add the card to the list
        self.constraint_list.controls.append(
            ft.Card(
                content=gesture_detector
            )
        )
    
    def _show_constraint_details(self, constraint_id: str):
        """
        Show details for a selected constraint set.
        
        Args:
            constraint_id: ID of the constraint set to show
        """
        constraint_set = self.constraint_manager.get_constraint_set_by_id(constraint_id)
        
        if not constraint_set:
            return
        
        self.selected_constraint = constraint_set
        
        # Update UI fields
        self.name_value.value = constraint_set.name
        self.min_length_value.value = str(constraint_set.min_length)
        self.max_length_value.value = str(constraint_set.max_length)
        self.require_uppercase_value.value = "Yes" if constraint_set.require_uppercase else "No"
        self.require_lowercase_value.value = "Yes" if constraint_set.require_lowercase else "No"
        self.require_digits_value.value = "Yes" if constraint_set.require_digits else "No"
        self.require_special_value.value = "Yes" if constraint_set.require_special else "No"
        self.included_chars_value.value = ", ".join(constraint_set.included_chars) if constraint_set.included_chars else "None"
        self.excluded_chars_value.value = ", ".join(constraint_set.excluded_chars) if constraint_set.excluded_chars else "None"
        
        # Get button references
        edit_button = None
        delete_button = None
        
        for control in self.constraint_details.content.content.controls[-1].controls:
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
    
    def add_constraint_set(self, e):
        """
        Add a new constraint set.
        
        Args:
            e: Click event
        """
        self._show_constraint_dialog("Add Constraint Set", None)
    
    def edit_constraint_set(self, e):
        """
        Edit the selected constraint set.
        
        Args:
            e: Click event
        """
        if not self.selected_constraint:
            return
        
        self._show_constraint_dialog("Edit Constraint Set", self.selected_constraint)
    
    def _show_constraint_dialog(self, title: str, constraint_set: Optional[ConstraintSet]):
        """
        Show a dialog for adding or editing a constraint set.
        
        Args:
            title: Dialog title
            constraint_set: Constraint set to edit, or None for a new constraint set
        """
        # Create form fields
        name_input = ft.TextField(
            label="Name",
            value=constraint_set.name if constraint_set else "",
            hint_text="Enter a name for this constraint set"
        )
        
        min_length_input = ft.TextField(
            label="Minimum Length",
            value=str(constraint_set.min_length) if constraint_set else "8",
            hint_text="Enter minimum password length",
            keyboard_type=ft.KeyboardType.NUMBER
        )
        
        max_length_input = ft.TextField(
            label="Maximum Length",
            value=str(constraint_set.max_length) if constraint_set else "20",
            hint_text="Enter maximum password length",
            keyboard_type=ft.KeyboardType.NUMBER
        )
        
        require_uppercase_checkbox = ft.Checkbox(
            label="Require uppercase letters",
            value=constraint_set.require_uppercase if constraint_set else True
        )
        
        require_lowercase_checkbox = ft.Checkbox(
            label="Require lowercase letters",
            value=constraint_set.require_lowercase if constraint_set else True
        )
        
        require_digits_checkbox = ft.Checkbox(
            label="Require digits",
            value=constraint_set.require_digits if constraint_set else True
        )
        
        require_special_checkbox = ft.Checkbox(
            label="Require special characters",
            value=constraint_set.require_special if constraint_set else True
        )
        
        included_chars_input = ft.TextField(
            label="Included Characters (comma-separated)",
            value=", ".join(constraint_set.included_chars) if constraint_set and constraint_set.included_chars else "",
            hint_text="Characters that must be included"
        )
        
        excluded_chars_input = ft.TextField(
            label="Excluded Characters (comma-separated)",
            value=", ".join(constraint_set.excluded_chars) if constraint_set and constraint_set.excluded_chars else "",
            hint_text="Characters that must be excluded"
        )
        
        # Validation error text
        error_text = ft.Text("", color=ft.colors.ERROR)
        
        def save_constraint(e):
            # Validate inputs
            errors = []
            
            if not name_input.value:
                errors.append("Name is required")
            
            try:
                min_length = int(min_length_input.value)
                if min_length < 1:
                    errors.append("Minimum length must be at least 1")
            except ValueError:
                errors.append("Minimum length must be a number")
            
            try:
                max_length = int(max_length_input.value)
                if max_length < min_length:
                    errors.append("Maximum length must be greater than or equal to minimum length")
            except ValueError:
                errors.append("Maximum length must be a number")
            
            if not (require_uppercase_checkbox.value or 
                   require_lowercase_checkbox.value or 
                   require_digits_checkbox.value or 
                   require_special_checkbox.value):
                errors.append("At least one character type must be required")
            
            # Parse included and excluded characters
            included_chars = [c.strip() for c in included_chars_input.value.split(",") if c.strip()]
            excluded_chars = [c.strip() for c in excluded_chars_input.value.split(",") if c.strip()]
            
            # Check for conflicts
            conflicts = set(included_chars).intersection(set(excluded_chars))
            if conflicts:
                errors.append(f"Characters {', '.join(conflicts)} cannot be both included and excluded")
            
            if errors:
                error_text.value = "\n".join(errors)
                self.main_window.page.update()
                return
            
            # Create or update constraint set
            if constraint_set:
                # Update existing constraint set
                updated_cs = ConstraintSet(
                    name=name_input.value,
                    min_length=int(min_length_input.value),
                    max_length=int(max_length_input.value),
                    require_uppercase=require_uppercase_checkbox.value,
                    require_lowercase=require_lowercase_checkbox.value,
                    require_digits=require_digits_checkbox.value,
                    require_special=require_special_checkbox.value,
                    included_chars=included_chars,
                    excluded_chars=excluded_chars
                )
                
                self.constraint_manager.update_constraint_set(constraint_set.id, updated_cs)
                message = "Constraint set updated successfully"
            else:
                # Create new constraint set
                new_cs = ConstraintSet(
                    name=name_input.value,
                    min_length=int(min_length_input.value),
                    max_length=int(max_length_input.value),
                    require_uppercase=require_uppercase_checkbox.value,
                    require_lowercase=require_lowercase_checkbox.value,
                    require_digits=require_digits_checkbox.value,
                    require_special=require_special_checkbox.value,
                    included_chars=included_chars,
                    excluded_chars=excluded_chars
                )
                
                self.constraint_manager.add_constraint_set(new_cs)
                message = "Constraint set added successfully"
            
            # Close dialog
            self.main_window.close_dialog(e)
            
            # Refresh UI
            self._load_constraint_sets()
            
            # Show success message
            self.main_window.show_snackbar(message)
        
        # Show dialog
        self.main_window.page.dialog = ft.AlertDialog(
            title=ft.Text(title),
            content=ft.Column([
                name_input,
                ft.Row([
                    min_length_input,
                    max_length_input
                ]),
                require_uppercase_checkbox,
                require_lowercase_checkbox,
                require_digits_checkbox,
                require_special_checkbox,
                included_chars_input,
                excluded_chars_input,
                error_text
            ], tight=True, spacing=10, scroll=ft.ScrollMode.AUTO),
            actions=[
                ft.TextButton("Cancel", on_click=self.main_window.close_dialog),
                ft.TextButton("Save", on_click=save_constraint)
            ],
            actions_alignment=ft.MainAxisAlignment.END
        )
        
        self.main_window.page.dialog.open = True
        self.main_window.page.update()
    
    def delete_constraint_set(self, e):
        """
        Delete the selected constraint set.
        
        Args:
            e: Click event
        """
        if not self.selected_constraint:
            return
        
        def confirm_delete():
            # Delete from storage
            self.constraint_manager.delete_constraint_set(self.selected_constraint.id)
            
            # Clear selection
            self.selected_constraint = None
            
            # Clear details
            self.name_value.value = ""
            self.min_length_value.value = ""
            self.max_length_value.value = ""
            self.require_uppercase_value.value = ""
            self.require_lowercase_value.value = ""
            self.require_digits_value.value = ""
            self.require_special_value.value = ""
            self.included_chars_value.value = ""
            self.excluded_chars_value.value = ""
            
            # Disable buttons
            for control in self.constraint_details.content.content.controls[-1].controls:
                if isinstance(control, ft.ElevatedButton):
                    control.disabled = True
            
            # Refresh constraint list
            self._load_constraint_sets()
            
            # Show success message
            self.main_window.show_snackbar("Constraint set deleted successfully")
        
        # Show confirmation dialog
        self.main_window.show_confirm_dialog(
            "Delete Constraint Set",
            f"Are you sure you want to delete the constraint set '{self.selected_constraint.name}'?",
            confirm_delete
        )
