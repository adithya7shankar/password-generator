import flet as ft
from typing import Dict, List, Any, Optional
import time
import os
from datetime import datetime

from storage.notes_storage import NotesStorage, Note

class SecureNotesTab:
    """
    Tab for managing encrypted secure notes.
    """
    
    def __init__(self, main_window):
        """
        Initialize the secure notes tab.
        
        Args:
            main_window: Reference to the main window
        """
        self.main_window = main_window
        self.notes_storage = NotesStorage()
        self.notes_list = []
        self.selected_note = None
        self.search_term = ""
        self.is_editing = False
        
        # UI components
        self.search_field = ft.TextField(
            label="Search Notes",
            hint_text="Search by title or content",
            prefix_icon=ft.icons.SEARCH,
            on_change=self.search_notes,
            expand=True,
            height=50,
            border_radius=8,
            width=None
        )
        
        self.add_button = ft.FloatingActionButton(
            icon=ft.icons.ADD,
            tooltip="Add new note",
            on_click=self.add_new_note
        )
        
        self.notes_listview = ft.ListView(
            expand=True,
            spacing=10,
            padding=10
        )
        
        self.category_dropdown = ft.Dropdown(
            label="Category",
            hint_text="Select a category",
            options=[
                ft.dropdown.Option("Personal"),
                ft.dropdown.Option("Work"),
                ft.dropdown.Option("Financial"),
                ft.dropdown.Option("Medical"),
                ft.dropdown.Option("Travel"),
                ft.dropdown.Option("Other")
            ],
            value="Personal",
            expand=True,
            height=65,
            border_radius=8,
            width=None
        )
        
        self.title_field = ft.TextField(
            label="Title",
            hint_text="Enter note title",
            expand=True,
            height=65,
            border_radius=8,
            width=None
        )
        
        self.content_field = ft.TextField(
            label="Content",
            hint_text="Enter note content",
            multiline=True,
            min_lines=5,
            max_lines=20,
            expand=True,
            border_radius=8,
            width=None
        )
        
        # Create text fields for details view
        self.details_title_text = ft.Text(
            "Note Title",
            size=20,
            weight=ft.FontWeight.W_500
        )
        
        self.details_meta_text = ft.Text(
            "Category • Created on date",
            size=12,
            color=ft.colors.OUTLINE
        )
        
        self.details_content_text = ft.Text(
            "Note content goes here...",
            selectable=True
        )
        
        # Note editor container (initially hidden)
        self.editor_container = ft.Container(
            content=ft.Card(
                content=ft.Container(
                    content=ft.Column([
                        ft.Text("Add New Note", size=20, weight=ft.FontWeight.W_500),
                        ft.Divider(height=1, color=ft.colors.OUTLINE_VARIANT),
                        ft.Container(height=20),
                        
                        # Note form
                        self.title_field,
                        ft.Container(height=20),
                        self.category_dropdown,
                        ft.Container(height=20),
                        self.content_field,
                        ft.Container(height=20),
                        
                        # Actions row
                        ft.Row([
                            ft.OutlinedButton(
                                "Cancel",
                                icon=ft.icons.CANCEL,
                                on_click=self.cancel_edit
                            ),
                            ft.FilledButton(
                                "Save Note",
                                icon=ft.icons.SAVE,
                                on_click=self.save_note
                            )
                        ], alignment=ft.MainAxisAlignment.END)
                    ], scroll=ft.ScrollMode.AUTO),
                    padding=25
                ),
                elevation=0,
                color=ft.colors.SURFACE
            ),
            visible=False  # Initially hidden
        )
        
        # Note details container (initially hidden)
        self.details_container = ft.Container(
            content=ft.Card(
                content=ft.Container(
                    content=ft.Column([
                        self.details_title_text,
                        self.details_meta_text,
                        ft.Divider(height=1, color=ft.colors.OUTLINE_VARIANT),
                        ft.Container(height=20),
                        
                        # Note content
                        self.details_content_text,
                        
                        ft.Container(height=20),
                        
                        # Actions row
                        ft.Row([
                            ft.IconButton(
                                icon=ft.icons.DELETE,
                                tooltip="Delete Note",
                                on_click=self.delete_note
                            ),
                            ft.IconButton(
                                icon=ft.icons.EDIT,
                                tooltip="Edit Note",
                                on_click=self.edit_note
                            )
                        ], alignment=ft.MainAxisAlignment.END)
                    ], scroll=ft.ScrollMode.AUTO),
                    padding=25
                ),
                elevation=0,
                color=ft.colors.SURFACE
            ),
            visible=False  # Initially hidden
        )
        
    def build(self) -> ft.Container:
        """
        Build the secure notes tab UI.
        
        Returns:
            Container with the tab content
        """
        # Note: We'll add the floating action button to the page in main_window
        self.main_window.page.floating_action_button = self.add_button
        self.main_window.page.floating_action_button_location = ft.FloatingActionButtonLocation.END_FLOAT
        
        return ft.Container(
            content=ft.Column([
                # Header with search
                ft.Container(
                    content=ft.Row([
                        ft.Text("Secure Notes", size=28, weight=ft.FontWeight.W_300),
                        ft.Container(width=20),
                        self.search_field
                    ]),
                    margin=ft.margin.only(bottom=20, top=10)
                ),
                
                # Main content with responsive layout
                ft.Container(
                    content=ft.ResponsiveRow([
                        # Notes list column - takes 1/3 of width on large screens
                        ft.Container(
                            content=ft.Card(
                                content=ft.Container(
                                    content=ft.Column([
                                        ft.Text("My Notes", size=16, weight=ft.FontWeight.W_500),
                                        ft.Divider(height=1, color=ft.colors.OUTLINE_VARIANT),
                                        ft.Container(height=10),
                                        self.notes_listview
                                    ]),
                                    padding=ft.padding.only(top=25, left=25, right=25)
                                ),
                                elevation=0,
                                color=ft.colors.SURFACE
                            ),
                            col={"sm": 12, "md": 4, "lg": 4, "xl": 3},
                            margin=ft.margin.only(bottom=20)
                        ),
                        
                        # Note details/editor column - takes 2/3 of width on large screens
                        ft.Container(
                            content=ft.Column([
                                self.details_container,
                                self.editor_container
                            ]),
                            col={"sm": 12, "md": 8, "lg": 8, "xl": 9}
                        )
                    ], expand=True),
                    expand=True
                )
            ], expand=True),
            padding=20,
            expand=True
        )
    
    def on_tab_activate(self):
        """Called when the tab is activated."""
        # Load/refresh notes list
        self._load_notes()
        
    def _load_notes(self):
        """Load notes from storage and display in the list."""
        # Clear existing notes list
        self.notes_listview.controls.clear()
        
        # Load notes from storage
        self.notes_list = self.notes_storage.get_all_notes()
        
        # Filter by search term if needed
        if self.search_term:
            self.notes_list = [note for note in self.notes_list 
                              if self.search_term.lower() in note.title.lower() 
                              or (note.content and self.search_term.lower() in note.content.lower())]
        
        # Sort notes by created time (newest first)
        self.notes_list.sort(key=lambda x: x.created, reverse=True)
        
        # Add notes to the list
        for note in self.notes_list:
            # Create a list item for each note
            list_item = self._create_note_list_item(note)
            self.notes_listview.controls.append(list_item)
        
        # Update UI
        self.main_window.page.update()
    
    def _create_note_list_item(self, note):
        """Create a list item for a note."""
        # Format the created date
        created_date = datetime.fromtimestamp(note.created).strftime("%Y-%m-%d")
        
        return ft.Container(
            content=ft.Column([
                ft.Text(
                    note.title,
                    weight=ft.FontWeight.W_500,
                    size=14,
                    overflow=ft.TextOverflow.ELLIPSIS
                ),
                ft.Text(
                    f"{note.category} • {created_date}",
                    size=12,
                    color=ft.colors.OUTLINE
                )
            ]),
            padding=10,
            border_radius=8,
            bgcolor=ft.colors.SURFACE_VARIANT,
            on_click=lambda e, note=note: self.show_note_details(note)
        )
    
    def search_notes(self, e):
        """Handle note search."""
        self.search_term = e.control.value
        self._load_notes()
    
    def show_note_details(self, note):
        """Show details for a selected note."""
        self.selected_note = note
        
        # Hide editor if visible
        self.editor_container.visible = False
        
        # Update details view
        self.details_title_text.value = note.title
        created_date = datetime.fromtimestamp(note.created).strftime("%Y-%m-%d %H:%M")
        self.details_meta_text.value = f"{note.category} • Created on {created_date}"
        self.details_content_text.value = note.content
        
        # Show details container
        self.details_container.visible = True
        
        # Update UI
        self.main_window.page.update()
    
    def add_new_note(self, e):
        """Start adding a new note."""
        # Hide details if visible
        self.details_container.visible = False
        
        # Clear form fields
        self.title_field.value = ""
        self.category_dropdown.value = "Personal"
        self.content_field.value = ""
        
        # Update form title
        if hasattr(self.editor_container.content.content.content.controls[0], 'value'):
            self.editor_container.content.content.content.controls[0].value = "Add New Note"
        
        # Show editor
        self.is_editing = False
        self.selected_note = None
        self.editor_container.visible = True
        
        # Update UI
        self.main_window.page.update()
    
    def edit_note(self, e):
        """Edit the selected note."""
        if not self.selected_note:
            return
            
        # Hide details container
        self.details_container.visible = False
        
        # Populate form fields with selected note data
        self.title_field.value = self.selected_note.title
        self.category_dropdown.value = self.selected_note.category
        self.content_field.value = self.selected_note.content
        
        # Update form title
        if hasattr(self.editor_container.content.content.content.controls[0], 'value'):
            self.editor_container.content.content.content.controls[0].value = "Edit Note"
        
        # Show editor
        self.is_editing = True
        self.editor_container.visible = True
        
        # Update UI
        self.main_window.page.update()
    
    def save_note(self, e):
        """Save the current note."""
        # Validate inputs
        if not self.title_field.value:
            self.main_window.show_error("Please enter a title for your note")
            return
            
        try:
            if self.is_editing and self.selected_note:
                # Update existing note
                self.selected_note.title = self.title_field.value
                self.selected_note.category = self.category_dropdown.value
                self.selected_note.content = self.content_field.value
                self.selected_note.updated = int(time.time())
                
                # Save to storage
                self.notes_storage.update_note(self.selected_note)
                self.main_window.show_snackbar("Note updated successfully")
            else:
                # Create new note
                new_note = Note(
                    id=None,  # Will be assigned by storage
                    title=self.title_field.value,
                    content=self.content_field.value,
                    category=self.category_dropdown.value,
                    created=int(time.time()),
                    updated=int(time.time())
                )
                
                # Save to storage
                self.notes_storage.add_note(new_note)
                self.main_window.show_snackbar("Note saved successfully")
                
            # Hide editor
            self.editor_container.visible = False
            self.is_editing = False
            self.selected_note = None
            
            # Reload notes list
            self._load_notes()
                
        except Exception as e:
            self.main_window.show_error(f"Error saving note: {str(e)}")
    
    def cancel_edit(self, e):
        """Cancel note editing."""
        self.editor_container.visible = False
        
        # If we were editing a note, show the details view again
        if self.is_editing and self.selected_note:
            self.show_note_details(self.selected_note)
        else:
            self.selected_note = None
            
        self.is_editing = False
        self.main_window.page.update()
    
    def delete_note(self, e):
        """Delete the selected note."""
        if not self.selected_note:
            return
            
        def confirm_delete():
            try:
                # Delete from storage
                self.notes_storage.delete_note(self.selected_note.id)
                
                # Hide details
                self.details_container.visible = False
                self.selected_note = None
                
                # Show notification
                self.main_window.show_snackbar("Note deleted successfully")
                
                # Reload notes list
                self._load_notes()
                
            except Exception as e:
                self.main_window.show_error(f"Error deleting note: {str(e)}")
        
        # Show confirmation dialog
        self.main_window.show_confirm_dialog(
            "Delete Note?",
            "Are you sure you want to delete this note? This action cannot be undone.",
            confirm_delete
        )
