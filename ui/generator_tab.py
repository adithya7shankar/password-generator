import flet as ft
from typing import List, Dict, Any, Optional, Callable
import random

from generator.password_generator import PasswordGenerator
from constraints.constraint_manager import ConstraintManager, ConstraintSet
from storage.password_storage import PasswordStorage, Password

class GeneratorTab:
    """
    Tab for generating passwords with user keywords and constraints.
    """
    
    def __init__(self, main_window):
        """
        Initialize the generator tab.
        
        Args:
            main_window: Reference to the main window
        """
        self.main_window = main_window
        self.password_generator = PasswordGenerator()
        self.constraint_manager = ConstraintManager()
        self.password_storage = PasswordStorage()
        self.password_history = []  # Store recently generated passwords
        self.history_visible = False  # Track history visibility state
        
        # UI components
        self.keywords_input = ft.TextField(
            label="Keywords (comma-separated)",
            hint_text="Enter keywords to include in the password",
            expand=True,
            tooltip="Add words that will be incorporated into your password",
            border_radius=8,
            width=None  # Allow the width to be determined by the parent container
        )
        
        self.constraint_dropdown = ft.Dropdown(
            label="Constraint Set",
            hint_text="Select a constraint set",
            expand=True,
            tooltip="Choose predefined password requirements",
            border_radius=8,
            width=None  # Allow the width to be determined by the parent container
        )
        
        # Password length slider
        self.length_slider = ft.Slider(
            min=6,
            max=30,
            divisions=24,
            label="{value}",
            value=12,
            expand=True,
            on_change=self.update_length_text,
            active_color=ft.colors.BLUE_GREY,
            width=None  # Allow the width to be determined by the parent container
        )
        
        self.length_text = ft.Text(
            "Password Length: 12",
            size=14,
            weight=ft.FontWeight.W_400
        )
        
        # Main password field with actions
        self.generated_password = ft.TextField(
            label="Generated Password",
            read_only=True,
            password=False,
            expand=True,
            value="",
            text_size=16,
            border_radius=8,
            width=None,  # Allow the width to be determined by the parent container
            suffix=ft.Row([
                ft.IconButton(
                    icon=ft.icons.VISIBILITY_OFF,
                    tooltip="Show/Hide Password",
                    on_click=self.toggle_password_visibility
                ),
                ft.IconButton(
                    icon=ft.icons.REFRESH,
                    tooltip="Generate new password",
                    on_click=self.generate_password
                ),
                ft.IconButton(
                    icon=ft.icons.COPY,
                    tooltip="Copy to clipboard",
                    on_click=self.copy_password
                )
            ], spacing=0)
        )
        
        # Simplified strength meter - just using progress bar
        self.password_strength_bar = ft.ProgressBar(
            width=None,  # Will expand to fill container width
            height=8,
            color=ft.colors.GREEN,
            bgcolor=ft.colors.GREY_300,
            value=0
        )
        
        self.strength_label = ft.Text(
            "Strength: 0%",
            size=14,
            weight=ft.FontWeight.W_400
        )
        
        self.feedback_text = ft.Text(
            "",
            size=14,
            color=ft.colors.GREY_700
        )
        
        # Password history section
        self.history_list = ft.ListView(
            height=150,
            spacing=10,
            padding=10,
            auto_scroll=True
        )
        
        # Save password fields with minimalist styling
        self.website_input = ft.TextField(
            label="Website/Service",
            hint_text="Enter website or service name",
            expand=True,
            tooltip="Website or service this password is for",
            border_radius=8,
            width=None  # Allow the width to be determined by the parent container
        )
        
        self.username_input = ft.TextField(
            label="Username/Email",
            hint_text="Enter username or email",
            expand=True,
            tooltip="Username or email associated with this password",
            border_radius=8,
            width=None  # Allow the width to be determined by the parent container
        )
        
        self.category_dropdown = ft.Dropdown(
            label="Category",
            hint_text="Select a category",
            options=[
                ft.dropdown.Option("General"),
                ft.dropdown.Option("Work"),
                ft.dropdown.Option("Personal"),
                ft.dropdown.Option("Finance"),
                ft.dropdown.Option("Social"),
                ft.dropdown.Option("Other")
            ],
            value="General",
            tooltip="Category for organizing your passwords",
            expand=True,
            border_radius=8,
            width=None  # Allow the width to be determined by the parent container
        )
        
        self.notes_input = ft.TextField(
            label="Notes",
            hint_text="Enter any additional notes",
            multiline=True,
            min_lines=2,
            max_lines=4,
            expand=True,
            tooltip="Additional information about this password",
            border_radius=8,
            width=None  # Allow the width to be determined by the parent container
        )
        
        # Create history container - legacy reference kept for compatibility
        self.history_container = ft.Container(
            content=ft.Column([
                ft.Text("Recently Generated Passwords", size=16, weight=ft.FontWeight.BOLD),
                ft.Container(height=10),
                self.history_list
            ]),
            visible=False
        )
        
        # Load constraint sets
        self._load_constraint_sets()
    
    def build(self) -> ft.Container:
        """
        Build the generator tab UI with a dark theme, responsive design.
        
        Returns:
            Container with the tab content
        """
        # Update UI components to match the dark theme
        self.keywords_input.border_radius = 4
        self.keywords_input.bgcolor = ft.colors.with_opacity(0.2, ft.colors.BLACK)
        self.keywords_input.label_style = ft.TextStyle(color=ft.colors.WHITE)
        self.keywords_input.hint_style = ft.TextStyle(color=ft.colors.with_opacity(0.6, ft.colors.WHITE))
        self.keywords_input.text_style = ft.TextStyle(color=ft.colors.WHITE)
        
        self.constraint_dropdown.border_radius = 4
        self.constraint_dropdown.bgcolor = ft.colors.with_opacity(0.2, ft.colors.BLACK)
        self.constraint_dropdown.label_style = ft.TextStyle(color=ft.colors.WHITE)
        
        self.generated_password.border_radius = 4
        self.generated_password.bgcolor = ft.colors.with_opacity(0.2, ft.colors.BLACK)
        self.generated_password.label_style = ft.TextStyle(color=ft.colors.WHITE)
        self.generated_password.text_style = ft.TextStyle(color=ft.colors.WHITE)
        
        return ft.Container(
            content=ft.Column([
                # Header
                ft.Container(
                    content=ft.Column([
                        ft.Text(
                            "Password Generator",
                            size=24,
                            weight=ft.FontWeight.BOLD,
                            color=ft.colors.WHITE
                        ),
                        ft.Text(
                            "Create strong, customized passwords with keywords and constraints",
                            size=14,
                            color=ft.colors.with_opacity(0.7, ft.colors.WHITE)
                        )
                    ], spacing=5),
                    margin=ft.margin.only(bottom=30, top=10)
                ),
                
                # Main content in two columns
                ft.ResponsiveRow([
                    # LEFT COLUMN - Password Options
                    ft.Container(
                        content=ft.Column([
                            # Keywords section
                            ft.Row([
                                ft.Icon(ft.icons.KEY, color=ft.colors.BLUE_300),
                                ft.Text(
                                    "Include Keywords",
                                    size=16,
                                    weight=ft.FontWeight.W_500,
                                    color=ft.colors.WHITE
                                )
                            ]),
                            ft.Text(
                                "Add words that will be incorporated into your password",
                                size=12,
                                color=ft.colors.with_opacity(0.7, ft.colors.WHITE)
                            ),
                            ft.Container(
                                content=self.keywords_input,
                                margin=ft.margin.only(top=5, bottom=30)
                            ),
                            
                            # Constraint Sets section
                            ft.Row([
                                ft.Icon(ft.icons.RULE, color=ft.colors.LIGHT_GREEN_300),
                                ft.Text(
                                    "Password Requirements",
                                    size=16,
                                    weight=ft.FontWeight.W_500,
                                    color=ft.colors.WHITE
                                )
                            ]),
                            ft.Container(
                                content=self.constraint_dropdown,
                                margin=ft.margin.only(top=5, bottom=30)
                            ),
                            
                            # Password Length section
                            ft.Text(
                                self.length_text.value,
                                size=14,
                                color=ft.colors.WHITE
                            ),
                            ft.Container(
                                content=ft.Row([
                                    ft.Text("6", size=12, color=ft.colors.with_opacity(0.7, ft.colors.WHITE)),
                                    self.length_slider,
                                    ft.Text("30", size=12, color=ft.colors.with_opacity(0.7, ft.colors.WHITE))
                                ]),
                                margin=ft.margin.only(bottom=30)
                            ),
                            
                            # Generate button
                            ft.FilledButton(
                                "Generate",
                                icon=ft.icons.PASSWORD,
                                on_click=self.generate_password,
                                style=ft.ButtonStyle(
                                    shape=ft.RoundedRectangleBorder(radius=4),
                                    color=ft.colors.BLUE_200
                                )
                            )
                        ]),
                        col={"sm": 12, "md": 6},
                        padding=10,
                        expand=True
                    ),
                    
                    # RIGHT COLUMN - Generated Password
                    ft.Container(
                        content=ft.Column([
                            # Generated Password section
                            ft.Row([
                                ft.Icon(ft.icons.PASSWORD, color=ft.colors.BLUE_300),
                                ft.Text(
                                    "Your Generated Password",
                                    size=16,
                                    weight=ft.FontWeight.W_500,
                                    color=ft.colors.WHITE
                                )
                            ]),
                            ft.Container(
                                content=self.generated_password,
                                margin=ft.margin.only(top=5, bottom=20)
                            ),
                            
                            # Strength meter
                            self.password_strength_bar,
                            ft.Container(
                                content=ft.Row([
                                    self.strength_label,
                                    self.feedback_text
                                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                                margin=ft.margin.only(top=5, bottom=20)
                            ),
                            
                            # Password actions
                            ft.Row([
                                ft.IconButton(
                                    icon=ft.icons.VISIBILITY_OFF,
                                    tooltip="Show/Hide Password",
                                    on_click=self.toggle_password_visibility,
                                    icon_color=ft.colors.WHITE
                                ),
                                ft.IconButton(
                                    icon=ft.icons.COPY,
                                    tooltip="Copy to Clipboard",
                                    on_click=self.copy_password,
                                    icon_color=ft.colors.WHITE
                                ),
                            ], alignment=ft.MainAxisAlignment.END),
                            
                            # Save password section
                            ft.Container(
                                content=ft.Column([
                                    ft.Text(
                                        "Save Password",
                                        size=16,
                                        weight=ft.FontWeight.W_500,
                                        color=ft.colors.WHITE
                                    ),
                                    ft.ResponsiveRow([
                                        ft.Container(
                                            content=self.website_input,
                                            col={"sm": 12, "md": 6},
                                            padding=5
                                        ),
                                        ft.Container(
                                            content=self.username_input,
                                            col={"sm": 12, "md": 6},
                                            padding=5
                                        ),
                                        ft.Container(
                                            content=self.category_dropdown,
                                            col={"sm": 12},
                                            padding=5
                                        ),
                                        ft.Container(
                                            content=self.notes_input,
                                            col={"sm": 12},
                                            padding=5
                                        ),
                                    ]),
                                    ft.Container(
                                        content=ft.FilledButton(
                                            "Save",
                                            icon=ft.icons.SAVE,
                                            on_click=self.save_password,
                                            style=ft.ButtonStyle(
                                                shape=ft.RoundedRectangleBorder(radius=4),
                                                color=ft.colors.TEAL_ACCENT_400
                                            ),
                                        ),
                                        margin=ft.margin.only(top=10),
                                        alignment=ft.alignment.center
                                    )
                                ]),
                                margin=ft.margin.only(top=30),
                                padding=ft.padding.all(0)
                            )
                        ]),
                        col={"sm": 12, "md": 6},
                        padding=10,
                        expand=True
                    ),
                ], expand=True),
            ], expand=True),
            padding=20,
            expand=True,
            bgcolor=ft.colors.with_opacity(0.9, ft.colors.BLACK)
        )
    
    def update_length_text(self, e):
        """
        Update the length text when the slider changes.
        
        Args:
            e: Change event
        """
        self.length_text.value = f"Password Length: {int(e.control.value)}"
        self.main_window.page.update()
    
    def _load_constraint_sets(self):
        """
        Load constraint sets into the dropdown.
        """
        constraint_sets = self.constraint_manager.get_all_constraint_sets()
        
        options = []
        for cs in constraint_sets:
            options.append(ft.dropdown.Option(cs.name))
        
        self.constraint_dropdown.options = options
        
        # Set default value if available
        if options:
            self.constraint_dropdown.value = options[0].key
    
    def generate_password(self, e):
        """
        Generate a password based on user input.
        
        Args:
            e: Click event
        """
        # Get keywords
        keywords_text = self.keywords_input.value or ""
        keywords = [k.strip() for k in keywords_text.split(",") if k.strip()]
        
        # Get selected constraint set
        constraint_set_name = self.constraint_dropdown.value
        constraint_set = self.constraint_manager.get_constraint_set_by_name(constraint_set_name)
        
        if not constraint_set:
            self.main_window.show_error("Please select a valid constraint set")
            return
        
        # Get custom length if specified
        custom_length = int(self.length_slider.value)
        
        # Generate password
        constraints = constraint_set.to_dict()
        
        # Override length constraints with slider value
        constraints['min_length'] = custom_length
        constraints['max_length'] = custom_length
        
        try:
            password = self.password_generator.generate_password(keywords, constraints)
            
            # Update UI
            self.generated_password.value = password
            self.generated_password.password = False  # Ensure password is visible initially
            
            # Update the visibility icon (first icon in the suffix row)
            for control in self.generated_password.suffix.controls:
                if isinstance(control, ft.IconButton) and control.tooltip == "Show/Hide Password":
                    control.icon = ft.icons.VISIBILITY_OFF  # Show the "visibility_off" icon when password is visible
            
            # Check password strength
            strength = self.password_generator.check_password_strength(password)
            
            # Update strength indicators
            self.password_strength_bar.value = strength['score'] / 100
            self.strength_label.value = f"Strength: {strength['score']}%"
            
            # Set color based on strength
            if strength['score'] < 50:
                self.password_strength_bar.color = ft.colors.RED
            elif strength['score'] < 80:
                self.password_strength_bar.color = ft.colors.ORANGE
            else:
                self.password_strength_bar.color = ft.colors.GREEN
            
            # Update feedback
            if strength['feedback']:
                self.feedback_text.value = ", ".join(strength['feedback'])
            else:
                self.feedback_text.value = "No issues found"
            
            # Add to history
            self._add_to_history(password, strength['score'])
            
            # Ensure the UI is updated immediately
            self.main_window.page.update()
        except Exception as e:
            self.main_window.show_error(f"Error generating password: {str(e)}")
    
    def _add_to_history(self, password, strength_score):
        """
        Add a password to the history list.
        
        Args:
            password: The generated password
            strength_score: The password strength score
        """
        # Add to history list (max 5 items)
        self.password_history.insert(0, password)
        if len(self.password_history) > 5:
            self.password_history.pop()
        
        # Clear the history list
        self.history_list.controls.clear()
        
        # Add history items to the list
        for pwd in self.password_history:
            # Create a history item with modern, minimalist design
            history_item = ft.Container(
                content=ft.Row([
                    ft.Text(
                        pwd,
                        expand=True,
                        overflow=ft.TextOverflow.ELLIPSIS,
                        size=14
                    ),
                    ft.IconButton(
                        icon=ft.icons.COPY,
                        tooltip="Copy to clipboard",
                        on_click=lambda e, p=pwd: self._copy_history_password(p)
                    )
                ]),
                padding=10,
                border_radius=5,
                bgcolor=ft.colors.SURFACE_VARIANT,
                margin=ft.margin.only(bottom=5)
            )
            
            self.history_list.controls.append(history_item)
        
        # Make history section visible if it has items
        self.history_visible = len(self.password_history) > 0
        
        # Update the UI
        self.main_window.page.update()
    
    def _copy_history_password(self, password):
        """
        Copy a password from history to clipboard.
        
        Args:
            password: The password to copy
        """
        self.main_window.page.set_clipboard(password)
        self.main_window.show_snackbar("Password copied to clipboard")
    
    def copy_password(self, e):
        """
        Copy the generated password to clipboard.
        
        Args:
            e: Click event
        """
        if self.generated_password.value:
            self.main_window.page.set_clipboard(self.generated_password.value)
            self.main_window.show_snackbar("Password copied to clipboard")
    
    def save_password(self, e):
        """
        Save the generated password.
        
        Args:
            e: Click event
        """
        # Check if a password has been generated
        if not self.generated_password.value:
            self.main_window.show_error("Please generate a password first")
            return
        
        # Create a new password entry
        password = Password(
            value=self.generated_password.value,
            website=self.website_input.value or "",
            username=self.username_input.value or "",
            category=self.category_dropdown.value or "General",
            notes=self.notes_input.value or ""
        )
        
        # Save the password
        self.password_storage.add_password(password)
        
        # Show success message
        self.main_window.show_snackbar("Password saved")
        
        # Clear input fields
        self.website_input.value = ""
        self.username_input.value = ""
        self.notes_input.value = ""
        
        # Refresh the storage tab password list
        if hasattr(self.main_window, 'storage_tab') and hasattr(self.main_window.storage_tab, '_load_passwords'):
            self.main_window.storage_tab._load_passwords()
            
            # Show a minimalist dialog to navigate to the passwords tab
            def navigate_to_passwords(e):
                self.main_window.navigate_to_tab(1)  # Index 1 is the passwords tab
                self.main_window.page.update()
                
            refresh_dialog = ft.AlertDialog(
                title=ft.Text("Saved", weight=ft.FontWeight.W_300),
                content=ft.Text("Password saved. View your stored passwords?"),
                actions=[
                    ft.TextButton("Later", on_click=lambda e: self.main_window.close_dialog(e)),
                    ft.TextButton("View", on_click=navigate_to_passwords)
                ]
            )
            
            self.main_window.page.dialog = refresh_dialog
            refresh_dialog.open = True
        
        # Update the UI
        self.main_window.page.update()
    
    def toggle_password_visibility(self, e):
        """
        Toggle the visibility of the generated password.
        
        Args:
            e: Click event
        """
        # Toggle the password visibility state
        self.generated_password.password = not self.generated_password.password
        
        # Update the icon based on the current state
        if self.generated_password.password:
            e.control.icon = ft.icons.VISIBILITY  # Show the "visibility" icon when password is hidden
        else:
            e.control.icon = ft.icons.VISIBILITY_OFF  # Show the "visibility_off" icon when password is visible
        
        # Update the page
        self.main_window.page.update()
