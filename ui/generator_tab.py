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
        
        # UI components
        self.keywords_input = ft.TextField(
            label="Keywords (comma-separated)",
            hint_text="Enter keywords to include in the password",
            expand=True
        )
        
        self.constraint_dropdown = ft.Dropdown(
            label="Constraint Set",
            hint_text="Select a constraint set",
            expand=True
        )
        
        self.generated_password = ft.TextField(
            label="Generated Password",
            read_only=True,
            expand=True,
            suffix=ft.IconButton(
                icon=ft.icons.COPY,
                tooltip="Copy to clipboard",
                on_click=self.copy_password
            )
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
        
        # Save password fields
        self.website_input = ft.TextField(
            label="Website/Service",
            hint_text="Enter website or service name",
            expand=True
        )
        
        self.username_input = ft.TextField(
            label="Username/Email",
            hint_text="Enter username or email",
            expand=True
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
            expand=True
        )
        
        self.notes_input = ft.TextField(
            label="Notes",
            hint_text="Enter any additional notes",
            multiline=True,
            min_lines=2,
            max_lines=4,
            expand=True
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
                ft.Text("Generate Password", size=24, weight=ft.FontWeight.BOLD),
                ft.Divider(),
                
                # Keywords and constraints section
                ft.Row([
                    self.keywords_input,
                    self.constraint_dropdown
                ]),
                
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
                    margin=ft.margin.only(top=10, bottom=20)
                ),
                
                # Generated password section
                ft.Container(
                    content=ft.Column([
                        self.generated_password,
                        ft.Row([
                            self.strength_label,
                            ft.Container(width=10),
                            self.password_strength_bar
                        ]),
                        self.feedback_text
                    ]),
                    padding=10,
                    border=ft.border.all(1, ft.colors.OUTLINE),
                    border_radius=10,
                    margin=ft.margin.only(bottom=20)
                ),
                
                # Save password section
                ft.Text("Save Password", size=18, weight=ft.FontWeight.BOLD),
                ft.Divider(),
                
                ft.Row([
                    self.website_input,
                    self.username_input
                ]),
                
                ft.Row([
                    self.category_dropdown
                ]),
                
                self.notes_input,
                
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
                    margin=ft.margin.only(top=10)
                )
            ], scroll=ft.ScrollMode.AUTO),
            padding=20,
            expand=True
        )
    
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
        
        # Generate password
        constraints = constraint_set.to_dict()
        password = self.password_generator.generate_password(keywords, constraints)
        
        # Update UI
        self.generated_password.value = password
        
        # Check password strength
        strength = self.password_generator.check_password_strength(password)
        
        # Update strength indicators
        self.password_strength_bar.value = strength['score'] / 100
        self.strength_label.value = f"Password Strength: {strength['score']}%"
        
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
            self.feedback_text.value = ""
        
        # Update the UI
        self.main_window.page.update()
    
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
