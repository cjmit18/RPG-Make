#!/usr/bin/env python3
"""
New Refactored Game Demo
=======================

A completely refactored demo utilizing the UI service layer architecture 
and focusing on character creation as the primary feature.
"""


import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from typing import Dict, Any, Optional, List
import json
import os
import asyncio
from datetime import datetime

# Import the UI service layer
from ui.demo_ui import DemoUI
from ui.character_creation_ui import CharacterCreationUI
from game_sys.config.config_manager import ConfigManager
from game_sys.logging import get_logger
from game_sys.character.character_creation_service import CharacterCreationService
# Import the new AdminPanelController
from ui.controllers.admin_panel_controller import AdminPanelController


class NewGameDemo:
    """
    New refactored game demo focusing on character creation.
    Uses service layer architecture exclusively.
    """
    
    def __init__(self):
        """Initialize the new game demo."""
        # Set up logging and configuration
        self.config = ConfigManager()
        self.logger = get_logger(__name__)
        
        # Initialize services
        self.character_creation_service = CharacterCreationService()
        
        # Initialize main UI service
        self.ui = DemoUI(title="Character Creation Demo", geometry="1200x900")
        
        # Character creation UI service (will be initialized after main UI)
        self.char_creation_ui: Optional[CharacterCreationUI] = None
        
        # UI state
        self.selected_template_var = tk.StringVar()
        self.character_name_var = tk.StringVar()

        # Admin panel controller (initialized on demand)
        self.admin_panel_controller: Optional[AdminPanelController] = None
        
        self.logger.info("NewGameDemo initialized")
    
    def setup_ui(self) -> None:
        """Set up the user interface using dedicated UI services."""
        try:
            # Set up basic UI structure
            ui_result = self.ui.setup_ui()
            
            if not ui_result['success']:
                raise RuntimeError(f"UI setup failed: {ui_result.get('error')}")
            
            # Get the character creation container
            char_creation_container = self._get_character_creation_container()
            
            # Prepare callbacks for character creation UI
            callbacks = {
                'template_selected': self._on_template_selected,
                'stat_allocated': self._allocate_stat_point,
                'preview_character': self._preview_character,
                'finalize_character': self._finalize_character,
                'reset_stats': self._reset_character_stats,
                'cancel_creation': self._cancel_creation,
                'save_character': self._save_character_to_library,
                'load_character': self._load_character_from_library,
                'show_character_library': self._show_character_library,
                'delete_saved_character': self._delete_saved_character,
                'toggle_admin_mode': self._toggle_admin_mode,
                'show_admin_panel': self._show_admin_panel,
                'copy_to_clipboard': self._copy_character_info,
                'set_character_grade': self._set_character_grade,
                'set_character_rarity': self._set_character_rarity,
                'add_stat_points': self._add_stat_points,
                'toggle_infinite_stat_points': self._toggle_infinite_stat_points,
                'reload_templates': self._reload_templates,
                'get_current_character': self._get_current_character
            }
            
            # Initialize character creation UI service with callbacks
            self.char_creation_ui = CharacterCreationUI(char_creation_container, callbacks)
            
            self.logger.info("Character creation callbacks registered")
            
            # Create the character creation interface
            templates = list(self.character_creation_service.get_available_templates().keys())
            interface_result = self.char_creation_ui.create_interface(
                templates, 
                self.selected_template_var, 
                self.character_name_var
            )
            
            if interface_result['status'] != 'success':
                raise RuntimeError(f"Character creation interface setup failed: {interface_result.get('error')}")
            
            self.logger.info("UI setup completed")
            
        except Exception as e:
            self.logger.error(f"Failed to setup UI: {e}")
            raise
    
    def _get_character_creation_container(self) -> tk.Widget:
        """Get or create the container for character creation UI."""
        try:
            # Use the stats tab as our character creation container
            if hasattr(self.ui, 'tabs') and 'stats' in self.ui.tabs:
                return self.ui.tabs['stats']
            else:
                # Create a new tab if needed
                char_tab = ttk.Frame(self.ui.tab_control)
                self.ui.tab_control.add(char_tab, text="Character Creation")
                return char_tab
                
        except Exception as e:
            self.logger.error(f"Failed to get character creation container: {e}")
            # Fallback to main frame
            return self.ui.main_frame
    
    def _register_character_creation_callbacks(self) -> None:
        """Register callbacks with the character creation UI service."""
        if not self.char_creation_ui:
            return
        
        # Register all character creation callbacks
        callbacks = {
            'template_selected': self._on_template_selected,
            'stat_allocated': self._allocate_stat_point,
            'preview_character': self._preview_character,
            'finalize_character': self._finalize_character,
            'reset_stats': self._reset_character_stats,
            'cancel_creation': self._cancel_creation,
            # Character library callbacks
            'save_character': self._save_character_to_library,
            'load_character': self._load_character_from_library,
            'show_character_library': self._show_character_library,
            'delete_saved_character': self._delete_saved_character,
            # Admin/cheat callbacks
            'toggle_admin_mode': self._toggle_admin_mode,
            'show_admin_panel': self._show_admin_panel,
            # Utility callbacks
            'get_current_character': self._get_current_character
        }
        
        for callback_name, callback_func in callbacks.items():
            self.char_creation_ui.register_callback(callback_name, callback_func)
        
        self.logger.info("Character creation callbacks registered")
    
    def _log_to_ui(self, message: str, tag: str = "info") -> None:
        """Log message to UI without causing recursion."""
        try:
            # Direct logging without using UI service to avoid recursion
            if hasattr(self.ui, 'log') and self.ui.log:
                self.ui.log.config(state=tk.NORMAL)
                self.ui.log.insert(tk.END, f"[{tag.upper()}] {message}\n")
                self.ui.log.see(tk.END)
                self.ui.log.config(state=tk.DISABLED)
        except Exception as e:
            # Fallback to console logging
            self.logger.info(f"[{tag.upper()}] {message}")
            self.logger.error(f"UI Log Error: {e}")
    
    # Event handlers
    def _on_template_selected(self, event=None) -> None:
        """Handle template selection."""
        template_id = self.selected_template_var.get()
        if not template_id:
            return
        
        try:
            # Update status to show template selected
            if self.char_creation_ui:
                self.char_creation_ui.update_status(f"📋 Template '{template_id}' selected - Click 'New Character' to generate", "#3498db")
            
            result = self.character_creation_service.select_template(template_id)
            
            if result.get('success', False):
                # Update template info display
                template_data = result.get('template')
                if template_data:
                    self._update_template_info(template_data)
                
                # Create preview character
                self._preview_character()
                
                self._log_to_ui(result.get('message', 'Template selected'), "info")
            else:
                if self.char_creation_ui:
                    self.char_creation_ui.update_status("❌ Failed to select template", "#e74c3c")
                self._log_to_ui(result.get('message', 'Failed to select template'), "error")
                
        except Exception as e:
            self.logger.error(f"Template selection error: {e}")
            if self.char_creation_ui:
                self.char_creation_ui.update_status("❌ Error selecting template", "#e74c3c")
            self._log_to_ui(f"Error selecting template: {e}", "error")
    
    def _allocate_stat_point(self, stat_name: str) -> None:
        """Allocate a stat point."""
        try:
            result = self.character_creation_service.allocate_stat_point(stat_name)
            
            if result['success']:
                # Update displays
                self._update_character_display()
                self._update_stat_labels()
                self._update_points_display()
                
                self._log_to_ui(result['message'], "info")
            else:
                self._log_to_ui(result['message'], "error")
                
        except Exception as e:
            self.logger.error(f"Stat allocation error: {e}")
            self._log_to_ui(f"Error allocating stat: {e}", "error")
    
    def _reset_character_stats(self) -> None:
        """Reset character stats to base template values while preserving grade/rarity."""
        try:
            result = self.character_creation_service.reset_stat_allocation()
            
            if result['success']:
                self._update_character_display()
                self._update_stat_labels()
                self._update_points_display()
                
                self._log_to_ui(result['message'], "info")
            else:
                self._log_to_ui(result['message'], "error")
                
        except Exception as e:
            self.logger.error(f"Reset stats error: {e}")
            self._log_to_ui(f"Error resetting stats: {e}", "error")
    
    def _preview_character(self) -> None:
        """Generate a completely new character with random grade/rarity."""
        template_id = self.selected_template_var.get()
        if not template_id:
            self._log_to_ui("Please select a character template first", "error")
            # Update status
            if self.char_creation_ui:
                self.char_creation_ui.update_status("❌ Please select a template first", "#e74c3c")
            return
        
        try:
            # Update status to show generation in progress
            if self.char_creation_ui:
                self.char_creation_ui.update_status("🎲 Generating new character...", "#f39c12")
            
            result = self.character_creation_service.create_character_preview(template_id)
            
            if result['success']:
                self._update_character_display()
                self._update_stat_labels()
                self._update_points_display()
                
                # Update status to show success
                if self.char_creation_ui:
                    char = self.character_creation_service.current_character
                    grade = getattr(char, 'grade_name', 'UNKNOWN')
                    rarity = getattr(char, 'rarity', 'COMMON')
                    self.char_creation_ui.update_status(
                        f"✅ {char.name} created! Grade: {grade}, Rarity: {rarity}", 
                        "#27ae60"
                    )
                
                self._log_to_ui(result['message'], "info")
            else:
                # Update status to show error
                if self.char_creation_ui:
                    self.char_creation_ui.update_status("❌ Failed to create character", "#e74c3c")
                self._log_to_ui(result['message'], "error")
                
        except Exception as e:
            self.logger.error(f"Character preview error: {e}")
            if self.char_creation_ui:
                self.char_creation_ui.update_status("❌ Error creating character", "#e74c3c")
            self._log_to_ui(f"Error creating preview: {e}", "error")
    
    def _copy_character_info(self) -> None:
        """Copy current character information to clipboard."""
        try:
            if not hasattr(self.character_creation_service, 'current_character') or not self.character_creation_service.current_character:
                self._log_to_ui("No character to copy", "warning")
                if self.char_creation_ui:
                    self.char_creation_ui.update_status("❌ No character to copy", "#f39c12")
                return
            
            # Get character info
            character = self.character_creation_service.current_character
            info_lines = [
                f"Character: {character.name}",
                f"Level: {character.level}",
                f"Job: {character.job_id}",
                f"Template: {character.template_id}",
                f"Grade: {character.grade}",
                f"Rarity: {character.rarity.name}",
                "",
                "Base Stats:",
                f"Strength: {character.strength}",
                f"Intelligence: {character.intelligence}",
                f"Dexterity: {character.dexterity}",
                f"Constitution: {character.constitution}",
                f"Wisdom: {character.wisdom}",
                f"Luck: {character.luck}",
                f"Agility: {character.agility}",
                "",
                "Derived Stats:",
                f"Health Points: {character.hp}/{character.max_hp}",
                f"Mana Points: {character.mp}/{character.max_mp}",
                f"Stamina Points: {character.sp}/{character.max_sp}",
                "",
                f"Combat stats:",
                f"Attack: {character.attack}",
                f"Defense: {character.defense}",
                f"Accuracy: {character.accuracy:.1%}",
                f"Dodge Chance: {character.dodge_chance:.1%}",
                f"Block Chance: {character.block_chance:.1%}",
                f"Critical Chance: {character.critical_chance:.1%}",
                "",
                f"Magic Power: {character.magic_power}",
                f"Magic Resistance: {character.magic_resistance:.1f}",
                f"Resilience: {character.resilience:.1f}"
            ]
            
            character_info = "\n".join(info_lines)
            
            # Copy to clipboard using tkinter
            self.ui.root.clipboard_clear()
            self.ui.root.clipboard_append(character_info)
            self.ui.root.update()  # Required for clipboard to work
            
            self._log_to_ui("Character information copied to clipboard", "info")
            if self.char_creation_ui:
                self.char_creation_ui.update_status("📋 Character info copied!", "#27ae60")
                
        except Exception as e:
            self.logger.error(f"Error copying character info: {e}")
            self._log_to_ui(f"Error copying character info: {e}", "error")
            if self.char_creation_ui:
                self.char_creation_ui.update_status("❌ Copy failed", "#e74c3c")
    
    def _finalize_character(self) -> None:
        """Finalize character creation."""
        try:
            custom_name = self.character_name_var.get()
            result = self.character_creation_service.finalize_character(custom_name)
            
            if result['success']:
                self._log_to_ui(result['message'], "info")
                
                # Show success dialog
                messagebox.showinfo(
                    "Character Created!",
                    f"Successfully created {result['character'].name}!\n\n"
                    f"Level: {result['stats']['level']}\n"
                    f"Grade: {result['stats']['grade']}\n"
                    f"Rarity: {result['stats']['rarity']}"
                )
                
                # Reset for next character
                self._reset_creation_ui()
            else:
                self._log_to_ui(result['message'], "error")
                
        except Exception as e:
            self.logger.error(f"Character finalization error: {e}")
            self._log_to_ui(f"Error finalizing character: {e}", "error")
    
    def _cancel_creation(self) -> None:
        """Cancel character creation."""
        if messagebox.askyesno("Cancel Creation", "Are you sure you want to cancel character creation?"):
            self._reset_creation_ui()
            self._log_to_ui("Character creation cancelled", "info")
    
    # ===== CHARACTER LIBRARY UI METHODS =====
    
    def _save_character_to_library(self) -> None:
        """Save current character to the library with custom name."""
        try:
            if not self.character_creation_service.current_character:
                messagebox.showwarning("No Character", "No character to save! Create a character first.")
                return
            
            # Get custom save name from user
            save_name = tk.simpledialog.askstring(
                "Save Character",
                f"Enter a name for saving '{self.character_creation_service.current_character.name}':",
                initialvalue=self.character_creation_service.current_character.name
            )
            
            if save_name is None:  # User cancelled
                return
            
            if not save_name.strip():
                messagebox.showwarning("Invalid Name", "Please enter a valid save name!")
                return
            
            # Save the character
            result = self.character_creation_service.save_current_character(save_name)
            
            if result['success']:
                messagebox.showinfo(
                    "Character Saved!",
                    f"Successfully saved '{self.character_creation_service.current_character.name}' as '{result['save_name']}'"
                )
                self._log_to_ui(result['message'], "info")
            else:
                messagebox.showerror("Save Failed", result['message'])
                self._log_to_ui(result['message'], "error")
                
        except Exception as e:
            self.logger.error(f"Save character error: {e}")
            self._log_to_ui(f"Error saving character: {e}", "error")
    
    def _load_character_from_library(self) -> None:
        """Load a character from the library."""
        try:
            # Get list of saved characters
            result = self.character_creation_service.get_saved_character_list()
            
            if not result['success']:
                messagebox.showerror("Library Error", result['message'])
                return
            
            if result['count'] == 0:
                messagebox.showinfo("Empty Library", "No saved characters found!")
                return
            
            # Create selection dialog
            self._show_character_selection_dialog(result['characters'], 'load')
                
        except Exception as e:
            self.logger.error(f"Load character error: {e}")
            self._log_to_ui(f"Error loading character: {e}", "error")
    
    def _show_character_library(self) -> None:
        """Show the character library management window."""
        try:
            # Get list of saved characters
            result = self.character_creation_service.get_saved_character_list()
            
            if not result['success']:
                messagebox.showerror("Library Error", result['message'])
                return
            
            # Create library management window
            self._show_library_management_window(result['characters'])
                
        except Exception as e:
            self.logger.error(f"Library display error: {e}")
            self._log_to_ui(f"Error displaying library: {e}", "error")
    
    def _delete_saved_character(self, save_name: str) -> None:
        """Delete a character from the library."""
        try:
            if messagebox.askyesno(
                "Delete Character", 
                f"Are you sure you want to permanently delete '{save_name}'?\n\nThis action cannot be undone!"
            ):
                result = self.character_creation_service.delete_saved_character(save_name)
                
                if result['success']:
                    messagebox.showinfo("Character Deleted", result['message'])
                    self._log_to_ui(result['message'], "info")
                else:
                    messagebox.showerror("Delete Failed", result['message'])
                    self._log_to_ui(result['message'], "error")
                
        except Exception as e:
            self.logger.error(f"Delete character error: {e}")
            self._log_to_ui(f"Error deleting character: {e}", "error")
    
    def _show_character_selection_dialog(self, characters: List[Dict[str, Any]], action: str) -> None:
        """Show character selection dialog for load/delete actions."""
        root_window = self.ui.get_root()
        if not root_window:
            messagebox.showerror("UI Error", "Main window not available")
            return
            
        dialog = tk.Toplevel(root_window)
        dialog.title(f"{action.title()} Character")
        dialog.geometry("600x400")
        dialog.transient(root_window)
        dialog.grab_set()
        
        # Center the dialog
        dialog.geometry("+%d+%d" % (
            root_window.winfo_rootx() + 50,
            root_window.winfo_rooty() + 50
        ))
        
        # Title
        title_label = tk.Label(dialog, text=f"Select Character to {action.title()}:", font=("Arial", 12, "bold"))
        title_label.pack(pady=10)
        
        # Character list frame
        list_frame = tk.Frame(dialog)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Scrollable listbox
        scrollbar = tk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        listbox = tk.Listbox(list_frame, yscrollcommand=scrollbar.set, font=("Consolas", 10))
        listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=listbox.yview)
        
        # Populate listbox
        for char in characters:
            display_text = (
                f"{char['save_name']} | "
                f"'{char['character_name']}' | "
                f"Level {char.get('level', '?')} | "
                f"Template: {char.get('template_id', 'Unknown')}"
            )
            listbox.insert(tk.END, display_text)
        
        # Button frame
        button_frame = tk.Frame(dialog)
        button_frame.pack(fill=tk.X, padx=10, pady=10)
        
        def on_action():
            selection = listbox.curselection()
            if not selection:
                messagebox.showwarning("No Selection", f"Please select a character to {action}!")
                return
            
            selected_char = characters[selection[0]]
            save_name = selected_char['save_name']
            
            if action == 'load':
                # Load the character
                result = self.character_creation_service.load_saved_character(save_name)
                
                if result['success']:
                    # Update UI displays
                    self._update_character_display()
                    self._update_stat_labels()
                    self._update_points_display()
                    
                    # Update template selection
                    if hasattr(self, 'selected_template_var'):
                        self.selected_template_var.set(result.get('template_id', ''))
                    
                    messagebox.showinfo("Character Loaded", result['message'])
                    self._log_to_ui(result['message'], "info")
                    dialog.destroy()
                else:
                    messagebox.showerror("Load Failed", result['message'])
                    self._log_to_ui(result['message'], "error")
            
            elif action == 'delete':
                dialog.destroy()  # Close dialog first
                self._delete_saved_character(save_name)
        
        def on_cancel():
            dialog.destroy()
        
        # Buttons
        action_btn = tk.Button(button_frame, text=action.title(), command=on_action, bg="#3498db", fg="white", padx=20)
        action_btn.pack(side=tk.LEFT, padx=5)
        
        cancel_btn = tk.Button(button_frame, text="Cancel", command=on_cancel, bg="#95a5a6", fg="white", padx=20)
        cancel_btn.pack(side=tk.RIGHT, padx=5)
        
        # Enable double-click to select
        def on_double_click(event):
            on_action()
        
        listbox.bind("<Double-Button-1>", on_double_click)
    
    def _show_library_management_window(self, characters: List[Dict[str, Any]]) -> None:
        """Show the complete library management window."""
        root_window = self.ui.get_root()
        if not root_window:
            messagebox.showerror("UI Error", "Main window not available")
            return
            
        window = tk.Toplevel(root_window)
        window.title("Character Library Manager")
        window.geometry("800x500")
        window.transient(root_window)
        
        # Center the window
        window.geometry("+%d+%d" % (
            root_window.winfo_rootx() + 25,
            root_window.winfo_rooty() + 25
        ))
        
        # Title
        title_label = tk.Label(window, text="Character Library Manager", font=("Arial", 14, "bold"))
        title_label.pack(pady=10)
        
        # Character list frame
        list_frame = tk.Frame(window)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Create Treeview for better display
        columns = ('Save Name', 'Character Name', 'Level', 'Template', 'Created Date')
        tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=15)
        
        # Configure columns
        tree.heading('Save Name', text='Save Name')
        tree.heading('Character Name', text='Character Name')  
        tree.heading('Level', text='Level')
        tree.heading('Template', text='Template')
        tree.heading('Created Date', text='Created Date')
        
        tree.column('Save Name', width=120)
        tree.column('Character Name', width=120)
        tree.column('Level', width=60)
        tree.column('Template', width=100)
        tree.column('Created Date', width=150)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Populate tree
        for char in characters:
            created_date = char.get('created_date', 'Unknown')
            if created_date != 'Unknown':
                try:
                    # Format the date nicely
                    from datetime import datetime
                    dt = datetime.fromisoformat(created_date.replace('Z', '+00:00'))
                    created_date = dt.strftime('%Y-%m-%d %H:%M')
                except:
                    pass
            
            tree.insert('', tk.END, values=(
                char['save_name'],
                char['character_name'],
                char.get('level', '?'),
                char.get('template_id', 'Unknown'),
                created_date
            ))
        
        # Button frame
        button_frame = tk.Frame(window)
        button_frame.pack(fill=tk.X, padx=10, pady=10)
        
        def load_selected():
            selection = tree.selection()
            if not selection:
                messagebox.showwarning("No Selection", "Please select a character to load!")
                return
                
            item = tree.item(selection[0])
            save_name = item['values'][0]
            
            # Load the character
            result = self.character_creation_service.load_saved_character(save_name)
            
            if result['success']:
                # Update UI displays
                self._update_character_display()
                self._update_stat_labels()
                self._update_points_display()
                
                # Update template selection
                if hasattr(self, 'selected_template_var'):
                    self.selected_template_var.set(result.get('template_id', ''))
                
                messagebox.showinfo("Character Loaded", result['message'])
                self._log_to_ui(result['message'], "info")
                window.destroy()
            else:
                messagebox.showerror("Load Failed", result['message'])
                self._log_to_ui(result['message'], "error")
        
        def delete_selected():
            selection = tree.selection()
            if not selection:
                messagebox.showwarning("No Selection", "Please select a character to delete!")
                return
                
            item = tree.item(selection[0])
            save_name = item['values'][0]
            
            if messagebox.askyesno(
                "Delete Character", 
                f"Are you sure you want to permanently delete '{save_name}'?\n\nThis action cannot be undone!"
            ):
                result = self.character_creation_service.delete_saved_character(save_name)
                
                if result['success']:
                    # Remove from tree
                    tree.delete(selection[0])
                    messagebox.showinfo("Character Deleted", result['message'])
                    self._log_to_ui(result['message'], "info")
                else:
                    messagebox.showerror("Delete Failed", result['message'])
                    self._log_to_ui(result['message'], "error")
        
        def refresh_library():
            # Clear current items
            for item in tree.get_children():
                tree.delete(item)
            
            # Reload character list
            result = self.character_creation_service.get_saved_character_list()
            if result['success']:
                characters = result['characters']
                for char in characters:
                    created_date = char.get('created_date', 'Unknown')
                    if created_date != 'Unknown':
                        try:
                            from datetime import datetime
                            dt = datetime.fromisoformat(created_date.replace('Z', '+00:00'))
                            created_date = dt.strftime('%Y-%m-%d %H:%M')
                        except:
                            pass
                    
                    tree.insert('', tk.END, values=(
                        char['save_name'],
                        char['character_name'],
                        char.get('level', '?'),
                        char.get('template_id', 'Unknown'),
                        created_date
                    ))
        
        def close_window():
            window.destroy()
        
        # Buttons
        tk.Button(button_frame, text="Load Character", command=load_selected, bg="#3498db", fg="white", padx=20).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Delete Character", command=delete_selected, bg="#e74c3c", fg="white", padx=20).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Refresh", command=refresh_library, bg="#f39c12", fg="white", padx=20).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Close", command=close_window, bg="#95a5a6", fg="white", padx=20).pack(side=tk.RIGHT, padx=5)
        
        # Enable double-click to load
        def on_double_click(event):
            load_selected()
        
        tree.bind("<Double-Button-1>", on_double_click)
    
    # ===== ADMIN/CHEAT UI METHODS =====
    
    def _toggle_admin_mode(self) -> None:
        """Toggle admin mode on/off."""
        try:
            result = self.character_creation_service.toggle_admin_mode()
            
            if result['success']:
                # Update UI to reflect admin mode state
                admin_enabled = result.get('admin_mode', False)
                if self.char_creation_ui:
                    self.char_creation_ui.update_admin_mode(admin_enabled)
                
                self._log_to_ui(result['message'], "info")
            else:
                self._log_to_ui(result['message'], "error")
                
        except Exception as e:
            self.logger.error(f"Toggle admin mode error: {e}")
            self._log_to_ui(f"Error toggling admin mode: {e}", "error")
    
    def _show_admin_panel(self) -> None:
        """Show the admin/cheat panel using AdminPanelController."""
        try:
            # Check if admin mode is enabled
            status = self.character_creation_service.get_admin_status()
            if not status['success'] or not status['admin_mode']:
                messagebox.showwarning("Admin Mode Required", "Admin mode must be enabled to access the admin panel!")
                return
            # Lazy init controller
            if not self.admin_panel_controller:
                self.admin_panel_controller = AdminPanelController(
                    parent_window=self.ui.get_root(),
                    admin_service=self.character_creation_service.admin_service,
                    character_service=self.character_creation_service,
                    ui_callbacks={}
                )
            self.admin_panel_controller.show_admin_panel()
        except Exception as e:
            self.logger.error(f"Show admin panel error: {e}")
            self._log_to_ui(f"Error showing admin panel: {e}", "error")
    
    def _set_character_grade(self, grade: str) -> None:
        """Set character grade via admin controls."""
        try:
            # Convert grade string to number
            grade_map = {"ONE": 0, "TWO": 1, "THREE": 2, "FOUR": 3, "FIVE": 4, "SIX": 5, "SEVEN": 6}
            grade_num = grade_map.get(grade, 2)  # Default to THREE (grade 2)
            
            result = self.character_creation_service.set_character_grade(grade_num, grade)
            if result['success']:
                self._log_to_ui(f"🎭 Character grade set to {grade}", "info")
                self._update_character_display()
            else:
                self._log_to_ui(result['message'], "error")
        except Exception as e:
            self.logger.error(f"Failed to set character grade: {e}")
            self._log_to_ui(f"Error setting grade: {e}", "error")
    
    def _set_character_rarity(self, rarity: str) -> None:
        """Set character rarity via admin controls."""
        try:
            result = self.character_creation_service.set_character_rarity(rarity)
            if result['success']:
                self._log_to_ui(f"💎 Character rarity set to {rarity}", "info")
                self._update_character_display()
            else:
                self._log_to_ui(result['message'], "error")
        except Exception as e:
            self.logger.error(f"Failed to set character rarity: {e}")
            self._log_to_ui(f"Error setting rarity: {e}", "error")
    
    def _add_stat_points(self, amount: int) -> None:
        """Add stat points via admin controls."""
        try:
            result = self.character_creation_service.add_stat_points(amount)
            if result['success']:
                self._log_to_ui(f"📊 Added {amount} stat points", "info")
                self._update_points_display()
            else:
                self._log_to_ui(result['message'], "error")
        except Exception as e:
            self.logger.error(f"Failed to add stat points: {e}")
            self._log_to_ui(f"Error adding stat points: {e}", "error")
    
    def _toggle_infinite_stat_points(self) -> None:
        """Toggle infinite stat points via admin controls."""
        try:
            result = self.character_creation_service.toggle_infinite_stat_points()
            if result['success']:
                infinite_enabled = result.get('infinite_enabled', False)
                if infinite_enabled:
                    self._log_to_ui("♾️ Infinite stat points enabled", "info")
                else:
                    self._log_to_ui("♾️ Infinite stat points disabled", "info")
                self._update_points_display()
            else:
                self._log_to_ui(result['message'], "error")
        except Exception as e:
            self.logger.error(f"Failed to toggle infinite stat points: {e}")
            self._log_to_ui(f"Error toggling infinite stat points: {e}", "error")
    
    def _get_current_character(self):
        """Callback to get the current character for comprehensive display."""
        try:
            return self.character_creation_service.current_character
        except Exception as e:
            self.logger.error(f"Error getting current character: {e}")
            return None
    
    def _reload_templates(self) -> None:
        """Reload character templates via admin controls."""
        try:
            result = self.character_creation_service.reload_templates()
            if result['success']:
                self._log_to_ui("🔄 Character templates reloaded", "info")
                # Update template dropdown
                templates = list(self.character_creation_service.get_available_templates().keys())
                if self.char_creation_ui and hasattr(self.char_creation_ui, 'template_combo'):
                    self.char_creation_ui.template_combo['values'] = templates
            else:
                self._log_to_ui(result['message'], "error")
        except Exception as e:
            self.logger.error(f"Failed to reload templates: {e}")
            self._log_to_ui(f"Error reloading templates: {e}", "error")
    
    def _create_admin_panel_window(self) -> None:
        """Create the admin panel window."""
        root_window = self.ui.get_root()
        if not root_window:
            messagebox.showerror("UI Error", "Main window not available")
            return
        
        admin_window = tk.Toplevel(root_window)
        admin_window.title("🔧 Admin/Cheat Panel")
        admin_window.geometry("600x700")
        admin_window.transient(root_window)
        admin_window.configure(bg="#2c3e50")
        
        # Center the window
        admin_window.geometry("+%d+%d" % (
            root_window.winfo_rootx() + 100,
            root_window.winfo_rooty() + 50
        ))
        
        # Title
        title_label = tk.Label(
            admin_window, 
            text="🔧 ADMIN / CHEAT PANEL 🔧", 
            font=("Arial", 16, "bold"),
            fg="#e74c3c",
            bg="#2c3e50"
        )
        title_label.pack(pady=10)
        
        warning_label = tk.Label(
            admin_window,
            text="⚠️ WARNING: These are cheat functions for testing purposes ⚠️",
            font=("Arial", 10),
            fg="#f39c12",
            bg="#2c3e50"
        )
        warning_label.pack(pady=5)
        
        # Create notebook for different admin sections
        notebook = ttk.Notebook(admin_window)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Stats tab
        stats_frame = tk.Frame(notebook, bg="#34495e")
        notebook.add(stats_frame, text="📊 Stats Cheats")
        self._create_stats_cheat_tab(stats_frame, admin_window)
        
        # Character tab
        char_frame = tk.Frame(notebook, bg="#34495e")
        notebook.add(char_frame, text="👤 Character Cheats")
        self._create_character_cheat_tab(char_frame, admin_window)
        
        # System tab
        system_frame = tk.Frame(notebook, bg="#34495e")
        notebook.add(system_frame, text="⚙️ System Controls")
        self._create_system_control_tab(system_frame, admin_window)
        
        # Close button
        close_frame = tk.Frame(admin_window, bg="#2c3e50")
        close_frame.pack(fill=tk.X, padx=10, pady=10)
        
        close_btn = tk.Button(
            close_frame,
            text="Close Admin Panel",
            command=admin_window.destroy,
            bg="#95a5a6",
            fg="white",
            font=("Arial", 12),
            padx=20,
            pady=5
        )
        close_btn.pack()
    
    def _create_stats_cheat_tab(self, parent: tk.Frame, admin_window: tk.Toplevel) -> None:
        """Create the stats cheat tab."""
        # Infinite stat points section
        infinite_frame = tk.LabelFrame(
            parent,
            text="♾️ Infinite Stat Points",
            font=("Arial", 12, "bold"),
            fg="#ecf0f1",
            bg="#34495e"
        )
        infinite_frame.pack(fill=tk.X, padx=10, pady=10)
        
        def toggle_infinite_stats():
            result = self.character_creation_service.toggle_infinite_stat_points()
            if result['success']:
                messagebox.showinfo("Stat Points Cheat", result['message'])
                self._log_to_ui(result['message'], "info")
                # Update UI displays
                self._update_points_display()
            else:
                messagebox.showerror("Error", result['message'])
                self._log_to_ui(result['message'], "error")
        
        tk.Button(
            infinite_frame,
            text="🔄 Toggle Infinite Stat Points",
            command=toggle_infinite_stats,
            bg="#3498db",
            fg="white",
            font=("Arial", 11),
            padx=10,
            pady=5
        ).pack(pady=10)
        
        # Add stat points section
        add_points_frame = tk.LabelFrame(
            parent,
            text="➕ Add Stat Points",
            font=("Arial", 12, "bold"),
            fg="#ecf0f1",
            bg="#34495e"
        )
        add_points_frame.pack(fill=tk.X, padx=10, pady=10)
        
        points_input_frame = tk.Frame(add_points_frame, bg="#34495e")
        points_input_frame.pack(pady=10)
        
        tk.Label(points_input_frame, text="Points to add:", bg="#34495e", fg="white").pack(side=tk.LEFT, padx=5)
        points_var = tk.StringVar(value="10")
        points_entry = tk.Entry(points_input_frame, textvariable=points_var, width=10)
        points_entry.pack(side=tk.LEFT, padx=5)
        
        def add_stat_points():
            try:
                amount = int(points_var.get())
                result = self.character_creation_service.add_stat_points(amount)
                if result['success']:
                    messagebox.showinfo("Stat Points Added", result['message'])
                    self._log_to_ui(result['message'], "info")
                    # Update UI displays
                    self._update_points_display()
                else:
                    messagebox.showerror("Error", result['message'])
                    self._log_to_ui(result['message'], "error")
            except ValueError:
                messagebox.showerror("Invalid Input", "Please enter a valid number")
        
        tk.Button(
            points_input_frame,
            text="Add Points",
            command=add_stat_points,
            bg="#27ae60",
            fg="white",
            padx=10
        ).pack(side=tk.LEFT, padx=5)
    
    def _create_character_cheat_tab(self, parent: tk.Frame, admin_window: tk.Toplevel) -> None:
        """Create the character cheat tab."""
        # Level modification section
        level_frame = tk.LabelFrame(
            parent,
            text="📈 Character Level",
            font=("Arial", 12, "bold"),
            fg="#ecf0f1",
            bg="#34495e"
        )
        level_frame.pack(fill=tk.X, padx=10, pady=10)
        
        level_input_frame = tk.Frame(level_frame, bg="#34495e")
        level_input_frame.pack(pady=10)
        
        tk.Label(level_input_frame, text="Level:", bg="#34495e", fg="white").pack(side=tk.LEFT, padx=5)
        level_var = tk.StringVar(value="1")
        level_combo = ttk.Combobox(
            level_input_frame,
            textvariable=level_var,
            values=[str(i) for i in range(1, 101)],  # Levels 1-100
            state="readonly",
            width=8
        )
        level_combo.pack(side=tk.LEFT, padx=5)
        
        def set_level():
            try:
                level = int(level_var.get())
                result = self.character_creation_service.set_character_level(level)
                if result['success']:
                    messagebox.showinfo("Level Changed", result['message'])
                    self._log_to_ui(result['message'], "info")
                    # Update UI displays
                    self._update_character_display()
                else:
                    messagebox.showerror("Error", result['message'])
                    self._log_to_ui(result['message'], "error")
            except ValueError:
                messagebox.showerror("Invalid Input", "Please select a valid level (1-100)")
        
        tk.Button(
            level_input_frame,
            text="Set Level",
            command=set_level,
            bg="#3498db",
            fg="white",
            padx=10
        ).pack(side=tk.LEFT, padx=5)
        
        # Grade modification section
        grade_frame = tk.LabelFrame(
            parent,
            text="🏆 Character Grade",
            font=("Arial", 12, "bold"),
            fg="#ecf0f1",
            bg="#34495e"
        )
        grade_frame.pack(fill=tk.X, padx=10, pady=10)
        
        grade_input_frame = tk.Frame(grade_frame, bg="#34495e")
        grade_input_frame.pack(pady=10)
        
        tk.Label(grade_input_frame, text="Grade:", bg="#34495e", fg="white").pack(side=tk.LEFT, padx=5)
        grade_var = tk.StringVar(value="0")
        grade_combo = ttk.Combobox(
            grade_input_frame,
            textvariable=grade_var,
            values=["0 (ONE)", "1 (TWO)", "2 (THREE)", "3 (FOUR)", "4 (FIVE)", "5 (SIX)", "6 (SEVEN)"],
            state="readonly",
            width=12
        )
        grade_combo.pack(side=tk.LEFT, padx=5)
        
        def set_grade():
            try:
                grade_text = grade_var.get()
                grade = int(grade_text.split()[0])  # Extract number from "0 (ONE)" format
                result = self.character_creation_service.set_character_grade(grade)
                if result['success']:
                    messagebox.showinfo("Grade Changed", result['message'])
                    self._log_to_ui(result['message'], "info")
                    # Update UI displays
                    self._update_character_display()
                    # Update template info with current character's template
                    if hasattr(self, 'current_character') and self.current_character:
                        template_data = self.character_creation_service.get_current_template()
                        if template_data:
                            self._update_template_info(template_data)
                    self._update_stat_labels()
                    self._update_points_display()
                else:
                    messagebox.showerror("Error", result['message'])
                    self._log_to_ui(result['message'], "error")
            except (ValueError, IndexError):
                messagebox.showerror("Invalid Input", "Please select a valid grade")
        
        tk.Button(
            grade_input_frame,
            text="Set Grade",
            command=set_grade,
            bg="#9b59b6",
            fg="white",
            padx=10
        ).pack(side=tk.LEFT, padx=5)
        
        # Rarity modification section
        rarity_frame = tk.LabelFrame(
            parent,
            text="💎 Character Rarity",
            font=("Arial", 12, "bold"),
            fg="#ecf0f1",
            bg="#34495e"
        )
        rarity_frame.pack(fill=tk.X, padx=10, pady=10)
        
        rarity_input_frame = tk.Frame(rarity_frame, bg="#34495e")
        rarity_input_frame.pack(pady=10)
        
        tk.Label(rarity_input_frame, text="Rarity:", bg="#34495e", fg="white").pack(side=tk.LEFT, padx=5)
        rarity_var = tk.StringVar(value="COMMON")
        rarity_combo = ttk.Combobox(
            rarity_input_frame,
            textvariable=rarity_var,
            values=["COMMON", "UNCOMMON", "RARE", "EPIC", "LEGENDARY", "MYTHIC", "DIVINE"],
            state="readonly",
            width=12
        )
        rarity_combo.pack(side=tk.LEFT, padx=5)
        
        def set_rarity():
            rarity = rarity_var.get()
            result = self.character_creation_service.set_character_rarity(rarity)
            if result['success']:
                messagebox.showinfo("Rarity Changed", result['message'])
                self._log_to_ui(result['message'], "info")
                # Update UI displays
                self._update_character_display()
                # Update template info with current character's template
                if hasattr(self, 'current_character') and self.current_character:
                    template_data = self.character_creation_service.get_current_template()
                    if template_data:
                        self._update_template_info(template_data)
                self._update_stat_labels()
                self._update_points_display()
            else:
                messagebox.showerror("Error", result['message'])
                self._log_to_ui(result['message'], "error")
        
        tk.Button(
            rarity_input_frame,
            text="Set Rarity",
            command=set_rarity,
            bg="#e67e22",
            fg="white",
            padx=10
        ).pack(side=tk.LEFT, padx=5)
    
    def _create_system_control_tab(self, parent: tk.Frame, admin_window: tk.Toplevel) -> None:
        """Create the system control tab."""
        # Configuration reload section
        config_frame = tk.LabelFrame(
            parent,
            text="🔄 Configuration Controls",
            font=("Arial", 12, "bold"),
            fg="#ecf0f1",
            bg="#34495e"
        )
        config_frame.pack(fill=tk.X, padx=10, pady=10)
        
        def reload_templates():
            result = self.character_creation_service.reload_templates()
            if result['success']:
                messagebox.showinfo("Templates Reloaded", result['message'])
                self._log_to_ui(result['message'], "info")
                # Update template dropdown if needed
                self._refresh_template_list()
            else:
                messagebox.showerror("Error", result['message'])
                self._log_to_ui(result['message'], "error")
        
        tk.Button(
            config_frame,
            text="🔄 Reload Character Templates",
            command=reload_templates,
            bg="#3498db",
            fg="white",
            font=("Arial", 11),
            padx=10,
            pady=5
        ).pack(pady=5)
        
        def reload_config():
            try:
                # Reload configuration
                self.config = ConfigManager()
                self.character_creation_service.config = ConfigManager()
                messagebox.showinfo("Config Reloaded", "Configuration files reloaded successfully!")
                self._log_to_ui("Configuration files reloaded", "info")
            except Exception as e:
                messagebox.showerror("Reload Error", f"Failed to reload config: {e}")
                self._log_to_ui(f"Failed to reload config: {e}", "error")
        
        tk.Button(
            config_frame,
            text="⚙️ Reload Configuration",
            command=reload_config,
            bg="#f39c12",
            fg="white",
            font=("Arial", 11),
            padx=10,
            pady=5
        ).pack(pady=5)
        
        # Demo restart section
        restart_frame = tk.LabelFrame(
            parent,
            text="🔄 Demo Controls",
            font=("Arial", 12, "bold"),
            fg="#ecf0f1",
            bg="#34495e"
        )
        restart_frame.pack(fill=tk.X, padx=10, pady=10)
        
        def restart_demo():
            if messagebox.askyesno(
                "Restart Demo",
                "Are you sure you want to restart the demo?\n\nThis will close the current session and restart the application."
            ):
                try:
                    admin_window.destroy()  # Close admin panel first
                    # Restart the demo
                    import sys
                    import os
                    python = sys.executable
                    os.execl(python, python, *sys.argv)
                except Exception as e:
                    messagebox.showerror("Restart Error", f"Failed to restart demo: {e}")
                    self._log_to_ui(f"Failed to restart demo: {e}", "error")
        
        tk.Button(
            restart_frame,
            text="🔄 Restart Demo",
            command=restart_demo,
            bg="#e74c3c",
            fg="white",
            font=("Arial", 11),
            padx=10,
            pady=5
        ).pack(pady=5)
        
        # Admin status display
        status_frame = tk.LabelFrame(
            parent,
            text="ℹ️ Admin Status",
            font=("Arial", 12, "bold"),
            fg="#ecf0f1",
            bg="#34495e"
        )
        status_frame.pack(fill=tk.X, padx=10, pady=10)
        
        def refresh_status():
            status = self.character_creation_service.get_admin_status()
            if status['success']:
                status_text = f"Admin Mode: {'ON' if status['admin_mode'] else 'OFF'}\n"
                status_text += f"Infinite Stat Points: {'ON' if status['infinite_stat_points'] else 'OFF'}\n"
                status_text += f"Available Stat Points: {status['current_stat_points']}"
                
                status_display.config(state=tk.NORMAL)
                status_display.delete(1.0, tk.END)
                status_display.insert(tk.END, status_text)
                status_display.config(state=tk.DISABLED)
        
        status_display = tk.Text(status_frame, height=4, bg="#2c3e50", fg="#ecf0f1", font=("Consolas", 10))
        status_display.pack(fill=tk.X, padx=10, pady=10)
        
        refresh_btn = tk.Button(
            status_frame,
            text="🔄 Refresh Status",
            command=refresh_status,
            bg="#95a5a6",
            fg="white",
            padx=10
        )
        refresh_btn.pack(pady=5)
        
        # Initial status load
        refresh_status()
    
    def _refresh_template_list(self) -> None:
        """Refresh the template dropdown list."""
        try:
            if self.char_creation_ui and hasattr(self.char_creation_ui, 'template_combo'):
                templates = list(self.character_creation_service.get_available_templates().keys())
                if self.char_creation_ui.template_combo:
                    self.char_creation_ui.template_combo['values'] = templates
                    self.logger.info("Template dropdown refreshed")
        except Exception as e:
            self.logger.error(f"Failed to refresh template list: {e}")
    
    # Display update methods
    def _update_template_info(self, template_data: Dict[str, Any]) -> None:
        """Update template information display using dedicated UI service."""
        try:
            # Get formatted template info from business service
            info_result = self.character_creation_service.get_template_display_info(template_data)
            
            if info_result['success'] and self.char_creation_ui:
                # Update UI using dedicated UI service
                self.char_creation_ui.update_template_info(info_result['display_text'])
                
                # Also update the detailed template information in the new tab
                self.char_creation_ui.update_template_details(template_data)
            else:
                self.logger.error(f"Failed to get template display info: {info_result.get('error')}")
            
        except Exception as e:
            self.logger.error(f"Failed to update template info: {e}")
    
    def _update_character_display(self) -> None:
        """Update character stats display using dedicated UI service."""
        try:
            # Get formatted character display from business service
            display_result = self.character_creation_service.get_character_display_text()
            
            if display_result['success'] and self.char_creation_ui:
                # Update UI using dedicated UI service
                self.char_creation_ui.update_character_display(display_result['display_text'])
            elif self.char_creation_ui:
                # Clear display if no character or error
                self.char_creation_ui.update_character_display("")
                
        except Exception as e:
            self.logger.error(f"Failed to update character display: {e}")
    
    def _update_stat_labels(self) -> None:
        """Update the stat labels in the UI with current character stat values."""
        try:
            if self.char_creation_ui and hasattr(self.char_creation_ui, 'update_stat_labels'):
                # Get formatted stat data from service
                stat_data = self.character_creation_service.get_character_stat_data()
                
                # Update UI with stat data
                self.char_creation_ui.update_stat_labels(stat_data)
                
                self.logger.debug(f"Updated stat labels with data: {stat_data}")
            else:
                self.logger.debug("No UI available for stat label update")
                    
        except Exception as e:
            self.logger.error(f"Failed to update stat labels: {e}")
    
    def _update_points_display(self) -> None:
        """Update available points display using dedicated UI service."""
        try:
            # Get points info from business service
            points_result = self.character_creation_service.get_points_display_info()
            
            if points_result['success'] and self.char_creation_ui:
                # Extract available points number from the service result
                available_points = points_result.get('available_points', 0)
                allocated_points = points_result.get('allocated_points', 0)
                
                # Update UI using dedicated UI service
                self.char_creation_ui.update_points_display(available_points, allocated_points)
            elif self.char_creation_ui:
                # Fallback display
                self.char_creation_ui.update_points_display(0, 0)
                    
        except Exception as e:
            self.logger.error(f"Failed to update points display: {e}")
    
    def _reset_creation_ui(self) -> None:
        """Reset the character creation UI using dedicated services."""
        try:
            # Clear UI selections
            self.selected_template_var.set("")
            self.character_name_var.set("")
            
            # Clear displays using dedicated UI service
            if self.char_creation_ui:
                self.char_creation_ui.clear_displays()
            
            # Reset business logic state using service
            reset_result = self.character_creation_service.reset_creation_state()
            if not reset_result['success']:
                self.logger.error(f"Failed to reset service state: {reset_result.get('error')}")
            
            # Update displays using dedicated services
            self._update_points_display()
            self._update_stat_labels()
            
        except Exception as e:
            self.logger.error(f"Failed to reset creation UI: {e}")
    
    def run(self) -> None:
        """Run the demo application."""
        try:
            self.setup_ui()
            
            # Log startup
            self._log_to_ui("🎮 Character Creation Demo Started!", "info")
            self._log_to_ui("📋 Select a character template to begin", "info")
            
            # Start the UI main loop
            self.ui.start_main_loop()
            
        except Exception as e:
            self.logger.error(f"Demo runtime error: {e}")
            messagebox.showerror("Demo Error", f"An error occurred: {e}")


def main():
    """Main entry point for the new demo."""
    try:
        demo = NewGameDemo()
        demo.run()
    except Exception as e:
        from game_sys.logging import get_logger
        logger = get_logger(__name__)
        logger.error(f"Failed to start demo: {e}")
        messagebox.showerror("Startup Error", f"Failed to start demo: {e}")


if __name__ == "__main__":
    main()
