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
        
        # UI components
        self.keywords_input = ft.TextField(
            label="Keywords (comma-separated)",
            hint_text="Enter keywords to include in the password",
            expand=True,
            tooltip="Add words that will be incorporated into your password"
        )
        
        self.constraint_dropdown = ft.Dropdown(
            label="Constraint Set",
            hint_text="Select a constraint set",
            expand=True,
            tooltip="Choose predefined password requirements"
        )
        
        # Password length slider
        self.length_slider = ft.Slider(
            min=6,
            max=30,
            divisions=24,
            label="{value}",
            value=12,
            expand=True,
            on_change=self.update_length_text
        )
        
        self.length_text = ft.Text(
            "Password Length: 12",
            size=14
        )
        
        self.generated_password = ft.TextField(
            label="Generated Password",
            read_only=True,
            password=False,  # Initialize as visible
            expand=True,
            suffix=ft.Row([
                ft.IconButton(
                    icon=ft.icons.VISIBILITY_OFF,  # Start with visibility off icon since password is visible
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
        
        # Visual password strength meter
        self.strength_indicators = [
            ft.Container(
                bgcolor=ft.colors.RED,
                border_radius=5,
                height=10,
                width=25
            ),
            ft.Container(
                bgcolor=ft.colors.ORANGE,
                border_radius=5,
                height=10,
                width=25,
                visible=False
            ),
            ft.Container(
                bgcolor=ft.colors.YELLOW,
                border_radius=5,
                height=10,
                width=25,
                visible=False
            ),
            ft.Container(
                bgcolor=ft.colors.GREEN,
                border_radius=5,
                height=10,
                width=25,
                visible=False
            )
        ]
        
        self.password_strength_meter = ft.Row(
            self.strength_indicators,
            spacing=5
        )
        
        self.password_strength_bar = ft.ProgressBar(
            width=400,
            color=ft.colors.GREEN,
            bgcolor=ft.colors.GREY_300,
            value=0
        )
        
        self.strength_label = ft.Text(
            "Password Strength: 0%",
            size=14
        )
        
        self.feedback_text = ft.Text(
            "",
            size=14,
            color=ft.colors.GREY_700
        )
        
        # Password history section
        self.history_list = ft.ListView(
            height=150,
            spacing=10,  # Increased spacing between history items
            padding=10,
            auto_scroll=True
        )
        
        # Save password fields
        self.website_input = ft.TextField(
            label="Website/Service",
            hint_text="Enter website or service name",
            expand=True,
            tooltip="Website or service this password is for",
            height=65  # Fixed height to prevent overlap
        )
        
        self.username_input = ft.TextField(
            label="Username/Email",
            hint_text="Enter username or email",
            expand=True,
            tooltip="Username or email associated with this password",
            height=65  # Fixed height to prevent overlap
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
            width=400,  # Set a fixed width to prevent layout issues
            height=65  # Fixed height to prevent overlap
        )
        
        self.notes_input = ft.TextField(
            label="Notes",
            hint_text="Enter any additional notes",
            multiline=True,
            min_lines=2,
            max_lines=4,
            expand=True,
            tooltip="Additional information about this password"
        )
        
        # Create history container
        self.history_container = ft.Container(
            content=ft.Column([
                ft.Text("Recently Generated Passwords", size=16, weight=ft.FontWeight.BOLD),
                ft.Container(height=10),  # Spacing
                self.history_list
            ], spacing=10),
            visible=False,  # Initially hidden until passwords are generated
            padding=20,  # Increased padding
            border=ft.border.all(1, ft.colors.OUTLINE),
            border_radius=10,
            margin=ft.margin.only(bottom=30)
        )
        
        # Load constraint sets
        self._load_constraint_sets()
    
    def build(self) -> ft.Container:
        """
        Build the generator tab UI.
        
        Returns:
            Container with the tab content
        """
        return ft.Container(
            content=ft.Column([
                # Header
                ft.Container(
                    content=ft.Text("Generate Password", size=24, weight=ft.FontWeight.BOLD),
                    margin=ft.margin.only(bottom=15)
                ),
                ft.Divider(height=2),
                ft.Container(height=20),  # Added top spacing
                
                # Keywords and constraints section
                ft.Container(
                    content=ft.Column([
                        ft.Text("Password Options", size=16, weight=ft.FontWeight.BOLD),
                        ft.Container(height=10),  # Spacing
                        ft.Container(  # Wrapped in container for better spacing
                            content=ft.Row([
                                self.keywords_input,
                            ]),
                            margin=ft.margin.only(bottom=15)
                        ),
                        ft.Container(height=15),  # Spacing
                        ft.Container(  # Wrapped in container for better spacing
                            content=ft.Row([
                                self.constraint_dropdown,
                            ]),
                            margin=ft.margin.only(bottom=15)
                        ),
                    ]),
                    margin=ft.margin.only(top=20, bottom=15)
                ),
                
                # Password length section
                ft.Container(
                    content=ft.Column([
                        self.length_text,
                        ft.Container(height=5),  # Spacing
                        ft.Row([
                            ft.Text("6", size=12),
                            self.length_slider,
                            ft.Text("30", size=12)
                        ])
                    ]),
                    margin=ft.margin.only(top=10, bottom=20)
                ),
                
                # Generate button
                ft.Container(
                    content=ft.ElevatedButton(
                        "Generate Password",
                        icon=ft.icons.REFRESH,
                        on_click=self.generate_password,
                        style=ft.ButtonStyle(
                            shape=ft.RoundedRectangleBorder(radius=10)
                        )
                    ),
                    alignment=ft.alignment.center,
                    margin=ft.margin.only(top=10, bottom=25)
                ),
                
                # Generated password section
                ft.Container(
                    content=ft.Column([
                        ft.Text("Generated Password", size=16, weight=ft.FontWeight.BOLD),
                        ft.Container(height=15),
                        ft.Container(  # Wrapped password field
                            content=self.generated_password,
                            height=65,  # Fixed height
                            margin=ft.margin.only(bottom=15)
                        ),
                        ft.Container(height=20),
                        ft.Container(  # Wrapped strength row
                            content=ft.Row([
                                ft.Column([
                                    ft.Text("Strength:", size=14),
                                    self.strength_label,
                                ], spacing=5),
                                ft.Container(width=30),  # Increased spacing
                                ft.Column([
                                    ft.Text("Strength Meter:", size=14),
                                    ft.Container(
                                        content=self.password_strength_meter,
                                        margin=ft.margin.only(left=10)
                                    )
                                ], spacing=5),
                            ]),
                            margin=ft.margin.only(bottom=15)
                        ),
                        ft.Container(height=15),  # Spacing
                        self.password_strength_bar,
                        ft.Container(height=15),  # Spacing
                        ft.Text("Feedback:", size=14),
                        self.feedback_text
                    ], spacing=5),  # Spacing between all column elements
                    padding=25,  # Increased padding
                    border=ft.border.all(1, ft.colors.OUTLINE),
                    border_radius=10,
                    margin=ft.margin.only(bottom=30)
                ),
                
                # Password history section (using the stored reference)
                ft.Container(  # Wrapped history section
                    content=self.history_container,
                    margin=ft.margin.only(top=20, bottom=30)
                ),
                
                # Save password section
                ft.Container(
                    content=ft.Text("Save Password", size=18, weight=ft.FontWeight.BOLD),
                    margin=ft.margin.only(top=10, bottom=5)
                ),
                ft.Divider(height=2),
                
                # Save password form - adjusted spacing
                ft.Container(
                    content=ft.Column([
                        ft.Text("Save Password Details", size=16, weight=ft.FontWeight.BOLD),
                        ft.Container(height=15),
                        ft.Container(
                            content=self.website_input,
                            margin=ft.margin.only(bottom=25)
                        ),
                        
                        ft.Container(
                            content=self.username_input,
                            margin=ft.margin.only(bottom=25)
                        ),
                        
                        ft.Container(
                            content=ft.Row([
                                self.category_dropdown
                            ]),
                            margin=ft.margin.only(bottom=25)
                        ),
                        
                        ft.Container(
                            content=self.notes_input,
                            margin=ft.margin.only(bottom=25)
                        ),
                    ]),
                    margin=ft.margin.only(top=20, bottom=20),
                    padding=10
                ),
                
                ft.Container(
                    content=ft.ElevatedButton(
                        "Save Password",
                        icon=ft.icons.SAVE,
                        on_click=self.save_password,
                        style=ft.ButtonStyle(
                            shape=ft.RoundedRectangleBorder(radius=10)
                        )
                    ),
                    alignment=ft.alignment.center,
                    margin=ft.margin.only(top=10, bottom=30)
                )
            ], 
            spacing=0,  # We're using explicit spacing with Container height
            scroll=ft.ScrollMode.AUTO),
            padding=30,  # Increased overall padding
            expand=True
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
        
        password = self.password_generator.generate_password(keywords, constraints)
        
        # Update UI
        self.generated_password.value = password
        
        # Check password strength
        strength = self.password_generator.check_password_strength(password)
        
        # Update strength indicators
        self.password_strength_bar.value = strength['score'] / 100
        self.strength_label.value = f"{strength['score']}%"
        
        # Set color based on strength
        if strength['score'] < 50:
            self.password_strength_bar.color = ft.colors.RED
        elif strength['score'] < 80:
            self.password_strength_bar.color = ft.colors.ORANGE
        else:
            self.password_strength_bar.color = ft.colors.GREEN
        
        # Update visual strength meter
        for i, indicator in enumerate(self.strength_indicators):
            if i == 0:  # First indicator always visible
                indicator.visible = True
            else:
                # Show indicators based on strength score
                indicator.visible = strength['score'] >= (i * 25)
        
        # Update feedback
        if strength['feedback']:
            self.feedback_text.value = ", ".join(strength['feedback'])
        else:
            self.feedback_text.value = "No issues found"
        
        # Add to history
        self._add_to_history(password, strength['score'])
        
        # Update the UI
        self.main_window.page.update()
    
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
            # Create a history item
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
                bgcolor=ft.colors.SURFACE_VARIANT,  # Fixed: removed with_opacity
                margin=ft.margin.only(bottom=5)  # Add margin between items
            )
            
            self.history_list.controls.append(history_item)
        
        # Make history section visible if it has items
        if self.password_history:
            self.history_container.visible = True
    
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
        self.main_window.show_snackbar("Password saved successfully")
        
        # Clear input fields
        self.website_input.value = ""
        self.username_input.value = ""
        self.notes_input.value = ""
        
        # Update the UI
        self.main_window.page.update()
        
        # Navigate to the passwords tab
        self.main_window.navigate_to_tab(1)  # Index 1 is the passwords tab
    
    def toggle_password_visibility(self, e):
        """
        Toggle the visibility of the generated password.
        
        Args:
            e: Click event
        """
        # Toggle the password visibility state
        self.generated_password.password = not self.generated_password.password
        
        # Update the icon based on the current state
        # When password=True (hidden), show VISIBILITY icon (eye open)
        # When password=False (visible), show VISIBILITY_OFF icon (eye with slash)
        if self.generated_password.password:
            e.control.icon = ft.icons.VISIBILITY
        else:
            e.control.icon = ft.icons.VISIBILITY_OFF
            
        # Update the UI
        self.main_window.page.update()
