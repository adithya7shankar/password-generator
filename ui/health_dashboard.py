import flet as ft
from typing import Dict, List, Any
import time
from datetime import datetime, timedelta
import zxcvbn

class HealthDashboard:
    """
    Dashboard showing password health metrics and improvement suggestions.
    """
    
    def __init__(self, main_window):
        """
        Initialize the health dashboard.
        
        Args:
            main_window: Reference to the main window
        """
        self.main_window = main_window
        self.password_storage = main_window.storage_tab.password_storage
        
        # Dashboard metrics
        self.overall_score = 0
        self.weak_passwords = []
        self.reused_passwords = []
        self.old_passwords = []
        self.breached_passwords = []
        
        # UI components
        self.overall_health_progress = ft.ProgressBar(
            width=None,
            height=8,
            color=ft.colors.GREEN,
            bgcolor=ft.colors.GREY_300,
            value=0
        )
        
        self.health_score_text = ft.Text(
            "Overall Health: 0%",
            size=16,
            weight=ft.FontWeight.W_500
        )
        
        self.weak_passwords_list = ft.ListView(
            height=200,
            spacing=10,
            padding=10
        )
        
        self.reused_passwords_list = ft.ListView(
            height=200,
            spacing=10,
            padding=10
        )
        
        self.old_passwords_list = ft.ListView(
            height=200,
            spacing=10,
            padding=10
        )
        
        self.suggestion_list = ft.ListView(
            height=200,
            spacing=10,
            padding=10
        )
        
    def build(self) -> ft.Container:
        """
        Build the health dashboard UI.
        
        Returns:
            Container with the tab content
        """
        return ft.Container(
            content=ft.Column([
                # Header
                ft.Container(
                    content=ft.Text("Password Health Dashboard", size=28, weight=ft.FontWeight.W_300),
                    margin=ft.margin.only(bottom=20, top=10)
                ),
                
                # Main content with responsive layout
                ft.Container(
                    content=ft.Column([
                        # Overall health score card
                        ft.Card(
                            content=ft.Container(
                                content=ft.Column([
                                    ft.Text("Overall Password Health", size=16, weight=ft.FontWeight.W_500),
                                    ft.Divider(height=1, color=ft.colors.OUTLINE_VARIANT),
                                    ft.Container(height=20),
                                    
                                    self.health_score_text,
                                    ft.Container(height=15),
                                    self.overall_health_progress,
                                    
                                    ft.Container(
                                        content=ft.FilledButton(
                                            "Refresh Analysis",
                                            icon=ft.icons.REFRESH,
                                            on_click=self.analyze_passwords
                                        ),
                                        alignment=ft.alignment.center,
                                        margin=ft.margin.only(top=25)
                                    ),
                                ], spacing=10),
                                padding=25
                            ),
                            elevation=0,
                            color=ft.colors.SURFACE
                        ),
                        
                        ft.Container(height=20),
                        
                        # Issue cards in responsive layout
                        ft.ResponsiveRow([
                            # Weak passwords column
                            ft.Container(
                                content=ft.Card(
                                    content=ft.Container(
                                        content=ft.Column([
                                            ft.Text("Weak Passwords", size=16, weight=ft.FontWeight.W_500),
                                            ft.Divider(height=1, color=ft.colors.OUTLINE_VARIANT),
                                            ft.Container(height=20),
                                            self.weak_passwords_list
                                        ], spacing=10),
                                        padding=25
                                    ),
                                    elevation=0,
                                    color=ft.colors.SURFACE
                                ),
                                col={"sm": 12, "md": 6, "lg": 6, "xl": 6},
                                margin=ft.margin.only(bottom=20)
                            ),
                            
                            # Reused passwords column
                            ft.Container(
                                content=ft.Card(
                                    content=ft.Container(
                                        content=ft.Column([
                                            ft.Text("Reused Passwords", size=16, weight=ft.FontWeight.W_500),
                                            ft.Divider(height=1, color=ft.colors.OUTLINE_VARIANT),
                                            ft.Container(height=20),
                                            self.reused_passwords_list
                                        ], spacing=10),
                                        padding=25
                                    ),
                                    elevation=0,
                                    color=ft.colors.SURFACE
                                ),
                                col={"sm": 12, "md": 6, "lg": 6, "xl": 6},
                                margin=ft.margin.only(bottom=20)
                            ),
                        ], expand=True),
                        
                        # Old passwords and suggestions
                        ft.ResponsiveRow([
                            # Old passwords column
                            ft.Container(
                                content=ft.Card(
                                    content=ft.Container(
                                        content=ft.Column([
                                            ft.Text("Old Passwords", size=16, weight=ft.FontWeight.W_500),
                                            ft.Divider(height=1, color=ft.colors.OUTLINE_VARIANT),
                                            ft.Container(height=20),
                                            self.old_passwords_list
                                        ], spacing=10),
                                        padding=25
                                    ),
                                    elevation=0,
                                    color=ft.colors.SURFACE
                                ),
                                col={"sm": 12, "md": 6, "lg": 6, "xl": 6},
                                margin=ft.margin.only(bottom=20)
                            ),
                            
                            # Suggestions column
                            ft.Container(
                                content=ft.Card(
                                    content=ft.Container(
                                        content=ft.Column([
                                            ft.Text("Improvement Suggestions", size=16, weight=ft.FontWeight.W_500),
                                            ft.Divider(height=1, color=ft.colors.OUTLINE_VARIANT),
                                            ft.Container(height=20),
                                            self.suggestion_list
                                        ], spacing=10),
                                        padding=25
                                    ),
                                    elevation=0,
                                    color=ft.colors.SURFACE
                                ),
                                col={"sm": 12, "md": 6, "lg": 6, "xl": 6},
                                margin=ft.margin.only(bottom=20)
                            ),
                        ], expand=True),
                    ], spacing=0, expand=True),
                    expand=True
                )
            ], spacing=0, expand=True),
            padding=20,
            expand=True
        )
    
    def analyze_passwords(self, e=None):
        """
        Analyze all stored passwords and update the health metrics.
        """
        passwords = self.password_storage.get_all_passwords()
        
        # Clear previous analysis
        self.weak_passwords = []
        self.reused_passwords = []
        self.old_passwords = []
        self.suggestion_list.controls.clear()
        self.weak_passwords_list.controls.clear()
        self.reused_passwords_list.controls.clear()
        self.old_passwords_list.controls.clear()
        
        if not passwords:
            self.overall_score = 0
            self.overall_health_progress.value = 0
            self.health_score_text.value = "Overall Health: 0%"
            self.main_window.page.update()
            return
        
        # Analyze password strength
        password_texts = {}
        password_strengths = {}
        
        for pwd in passwords:
            # Check for weak passwords
            result = zxcvbn.zxcvbn(pwd.password)
            score = result["score"]
            password_strengths[pwd.id] = score
            
            if pwd.password not in password_texts:
                password_texts[pwd.password] = [pwd]
            else:
                password_texts[pwd.password].append(pwd)
            
            if score < 3:
                self.weak_passwords.append(pwd)
            
            # Check for old passwords (older than 180 days)
            created_date = datetime.fromtimestamp(pwd.created)
            if datetime.now() - created_date > timedelta(days=180):
                self.old_passwords.append(pwd)
        
        # Check for reused passwords
        for password_text, pwd_list in password_texts.items():
            if len(pwd_list) > 1:
                self.reused_passwords.extend(pwd_list)
        
        # Calculate overall score
        total_issues = len(self.weak_passwords) + len(self.reused_passwords) + len(self.old_passwords)
        if total_issues == 0 and len(passwords) > 0:
            self.overall_score = 100
        else:
            max_possible_issues = len(passwords) * 3  # Each password could be weak, reused, and old
            self.overall_score = max(0, 100 - (total_issues / max_possible_issues * 100))
        
        # Update health score display
        health_color = ft.colors.RED
        if self.overall_score >= 80:
            health_color = ft.colors.GREEN
        elif self.overall_score >= 60:
            health_color = ft.colors.AMBER
        elif self.overall_score >= 40:
            health_color = ft.colors.ORANGE
            
        self.overall_health_progress.value = self.overall_score / 100
        self.overall_health_progress.color = health_color
        self.health_score_text.value = f"Overall Health: {int(self.overall_score)}%"
        
        # Populate lists
        self._populate_weak_passwords_list()
        self._populate_reused_passwords_list()
        self._populate_old_passwords_list()
        self._generate_suggestions()
        
        self.main_window.page.update()
    
    def _populate_weak_passwords_list(self):
        """Populate the weak passwords list."""
        for pwd in self.weak_passwords:
            self.weak_passwords_list.controls.append(
                self._create_password_list_item(
                    pwd, 
                    "Strength is too low", 
                    ft.colors.RED_400,
                    self._create_fix_action(pwd, "fix_weak")
                )
            )
    
    def _populate_reused_passwords_list(self):
        """Populate the reused passwords list."""
        added_ids = set()
        for pwd in self.reused_passwords:
            if pwd.id not in added_ids:
                self.reused_passwords_list.controls.append(
                    self._create_password_list_item(
                        pwd, 
                        "Used in multiple accounts", 
                        ft.colors.AMBER_400,
                        self._create_fix_action(pwd, "fix_reused")
                    )
                )
                added_ids.add(pwd.id)
    
    def _populate_old_passwords_list(self):
        """Populate the old passwords list."""
        for pwd in self.old_passwords:
            created_date = datetime.fromtimestamp(pwd.created).strftime("%Y-%m-%d")
            self.old_passwords_list.controls.append(
                self._create_password_list_item(
                    pwd, 
                    f"Created on {created_date}", 
                    ft.colors.BLUE_400,
                    self._create_fix_action(pwd, "fix_old")
                )
            )
    
    def _generate_suggestions(self):
        """Generate improvement suggestions."""
        suggestions = []
        
        if self.weak_passwords:
            suggestions.append(
                f"You have {len(self.weak_passwords)} weak passwords that should be strengthened."
            )
        
        if self.reused_passwords:
            unique_reused = set()
            for pwd in self.reused_passwords:
                unique_reused.add(pwd.password)
            suggestions.append(
                f"You have {len(unique_reused)} passwords that are used across multiple accounts."
            )
        
        if self.old_passwords:
            suggestions.append(
                f"You have {len(self.old_passwords)} passwords that are older than 180 days."
            )
        
        # Add general suggestions
        if not suggestions:
            suggestions.append("Your password health looks good! Continue maintaining good practices.")
        else:
            suggestions.append("Consider enabling regular password rotation for important accounts.")
            suggestions.append("Use the password generator to create strong, unique passwords.")
        
        # Add suggestions to UI
        for suggestion in suggestions:
            self.suggestion_list.controls.append(
                ft.Container(
                    content=ft.Text(suggestion, size=14),
                    padding=10,
                    border_radius=8,
                    bgcolor=ft.colors.SURFACE_VARIANT
                )
            )
    
    def _create_password_list_item(self, password, issue_text, color, action_button):
        """Create a list item for a password issue."""
        return ft.Container(
            content=ft.Column([
                ft.Text(
                    f"{password.website or 'Unknown'} ({password.username or 'No username'})",
                    weight=ft.FontWeight.W_500
                ),
                ft.Container(height=5),
                ft.Text(issue_text, size=12, color=color)
            ]),
            padding=10,
            border_radius=8,
            bgcolor=ft.colors.SURFACE_VARIANT,
            width=None
        )
    
    def _create_fix_action(self, password, fix_type):
        """Create an action button to fix password issues."""
        return ft.IconButton(
            icon=ft.icons.BUILD_CIRCLE_OUTLINED,
            tooltip="Fix Issue",
            on_click=lambda e: self.fix_password_issue(e, password, fix_type)
        )
    
    def fix_password_issue(self, e, password, fix_type):
        """Fix a password issue based on the type."""
        if fix_type == "fix_weak":
            # Navigate to generator tab and pre-fill fields
            self.main_window.navigate_to_tab(0)  # Generator tab
            generator_tab = self.main_window.generator_tab
            generator_tab.length_slider.value = 16
            generator_tab.update_length_text(None)
            generator_tab.generate_password(None)
            generator_tab.website_input.value = password.website
            generator_tab.username_input.value = password.username
            generator_tab.category_dropdown.value = password.category
            generator_tab.notes_input.value = password.notes
            
        elif fix_type == "fix_reused" or fix_type == "fix_old":
            # Navigate to generator tab and pre-fill fields
            self.main_window.navigate_to_tab(0)  # Generator tab
            generator_tab = self.main_window.generator_tab
            generator_tab.length_slider.value = 16
            generator_tab.update_length_text(None)
            generator_tab.generate_password(None)
            generator_tab.website_input.value = password.website
            generator_tab.username_input.value = password.username
            generator_tab.category_dropdown.value = password.category
            generator_tab.notes_input.value = password.notes
        
        self.main_window.page.update() 