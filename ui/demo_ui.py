#!/usr/bin/env python3
"""
Demo UI Management
=================

UI management service for the game demo following service layer architecture.
Handles all Tkinter-related code, widget creation, layout, and UI updates.
"""

import tkinter as tk
from tkinter import ttk
import time
import os
from typing import Dict, Any, Optional, Callable

from game_sys.config.config_manager import ConfigManager
from game_sys.logging import get_logger


class DemoUI:
    """Service class for demo UI management and display."""
    
    def __init__(self, root: Optional[tk.Tk] = None, title: str = "Simple Game Demo", geometry: str = "900x700"):
        """
        Initialize UI service with dependencies.
        
        Args:
            root: Existing Tkinter root window, or None to create a new one
            title: Window title (used only if creating new window)
            geometry: Window size string (e.g., "900x700") (used only if creating new window)
        """
        self.config = ConfigManager()
        self.logger = get_logger(__name__)
        
        # UI state
        self.root = root
        self.main_frame: Optional[tk.Frame] = None
        self.tab_control: Optional[ttk.Notebook] = None
        self.log: Optional[tk.Text] = None
        
        # Tab references
        self.tabs: Dict[str, ttk.Frame] = {}
        
        # UI widgets for external access
        self.widgets: Dict[str, Any] = {}
        
        # Event callbacks
        self.callbacks: Dict[str, Callable] = {}
        
        # Initialize main window if not provided
        if self.root is None:
            self._create_main_window(title, geometry)
        
        self.logger.info("DemoUI service initialized")
    
    def set_log_callback(self, callback: Callable[[str], None]) -> None:
        """Set external log callback function."""
        self.callbacks['log'] = callback
        self.logger.info("External log callback registered")
    
    def set_external_widgets(self, widget_refs: Dict[str, Any]) -> None:
        """Set references to external widgets for integration."""
        self.widgets.update(widget_refs)
        self.logger.info(f"Updated UI service with {len(widget_refs)} external widget references")
    
    def _create_main_window(self, title: str, geometry: str) -> None:
        """Create the main Tkinter window."""
        try:
            self.root = tk.Tk()
            self.root.title(title)
            self.root.geometry(geometry)
            
            self.logger.info(f"Created main window: {title} ({geometry})")
            
        except Exception as e:
            self.logger.error(f"Failed to create main window: {e}")
            raise RuntimeError(f"UI initialization failed: {e}")
    
    def setup_ui(self) -> Dict[str, Any]:
        """
        Set up the complete user interface.
        
        Returns:
            Dictionary with success status and created components
        """
        try:
            self.logger.info("Setting up tabbed UI")
            
            # Create main frame
            self._create_main_frame()
            
            # Create tab control and tabs
            self._create_tab_control()
            self._create_tabs()
            
            # Create log area
            self._create_log_area()
            
            # Bind events
            self._bind_events()
            
            return {
                'success': True,
                'message': 'UI setup completed successfully',
                'root': self.root,
                'tabs': self.tabs,
                'widgets': self.widgets
            }
            
        except Exception as e:
            self.logger.error(f"UI setup failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'message': 'UI setup failed'
            }
    
    def _create_main_frame(self) -> None:
        """Create the main frame container."""
        self.main_frame = tk.Frame(self.root, bg="black")
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
    def _create_tab_control(self) -> None:
        """Create the tab control notebook."""
        self.tab_control = ttk.Notebook(self.main_frame)
        
    def _create_tabs(self) -> None:
        """Create all UI tabs."""
        tab_configs = [
            ("stats", "Character Stats"),
            ("combat", "Combat"),
            ("inventory", "Inventory"),
            ("leveling", "Leveling"),
            ("enchanting", "Enchanting"),
            ("progression", "Progression"),
            ("combo", "Combos"),
            ("settings", "Settings")
        ]
        
        for tab_id, tab_text in tab_configs:
            tab_frame = ttk.Frame(self.tab_control)
            self.tabs[tab_id] = tab_frame
            self.tab_control.add(tab_frame, text=tab_text)
        
        # Pack the tab control
        self.tab_control.pack(expand=1, fill=tk.BOTH, padx=10, pady=10)
        
    def _create_log_area(self) -> None:
        """Create the log display area."""
        self.log_frame = tk.Frame(self.root, bg="black")
        self.log_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=10)
        
        self.log = tk.Text(self.log_frame, bg="black", fg="white", height=8)
        self.log.pack(fill=tk.X)
        
        # Configure text tags for different message types
        self.log.tag_configure("info", foreground="cyan")
        self.log.tag_configure("combat", foreground="red")
        self.log.tag_configure("heal", foreground="green")
        self.log.tag_configure("magic", foreground="purple")
        
        self.widgets['log'] = self.log
        
    def _bind_events(self) -> None:
        """Bind UI events."""
        if self.tab_control:
            self.tab_control.bind('<<NotebookTabChanged>>', self._on_tab_changed)
    
    def _on_tab_changed(self, event) -> None:
        """Handle tab change events."""
        if 'tab_changed' in self.callbacks:
            self.callbacks['tab_changed'](event)
    
    def setup_stats_tab(self, update_callback: Optional[Callable] = None) -> Dict[str, Any]:
        """
        Set up the enhanced character stats tab with detailed equipment and performance metrics.
        
        Args:
            update_callback: Callback function for updating character info
            
        Returns:
            Dictionary with created widgets for external access
        """
        try:
            tab = self.tabs['stats']
            
            # Create main container with better organization
            main_container = tk.Frame(tab, bg="black")
            main_container.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

            # === TOP SECTION: Character Overview ===
            top_frame = tk.Frame(main_container, bg="black")
            top_frame.pack(fill=tk.X, pady=(0, 10))

            # Left: Character portrait and basic info
            left_frame = tk.Frame(top_frame, bg="black")
            left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))

            # Enhanced Character portrait area
            portrait_frame = tk.Frame(left_frame, bg="dark gray", width=180, height=180)
            portrait_frame.pack(pady=5)
            portrait_frame.pack_propagate(False)

            # Character portrait with border
            portrait_inner = tk.Frame(portrait_frame, bg="gray", width=170, height=170)
            portrait_inner.pack(expand=True, pady=5, padx=5)
            
            portrait_label = tk.Label(
                portrait_inner,
                text="🎭\nCharacter\nPortrait",
                bg="gray",
                fg="white",
                font=("Arial", 10, "bold"),
                justify=tk.CENTER
            )
            portrait_label.pack(expand=True)

            # Enhanced Character basic info
            basic_info_frame = tk.Frame(left_frame, bg="black")
            basic_info_frame.pack(fill=tk.BOTH, expand=True, pady=5)

            basic_info_title = tk.Label(
                basic_info_frame,
                text="📊 Character Overview",
                font=("Arial", 11, "bold"),
                fg="cyan",
                bg="black"
            )
            basic_info_title.pack()

            basic_info = tk.Text(
                basic_info_frame,
                width=28,
                height=14,
                bg="#2c3e50",
                fg="white",
                font=("Consolas", 9),
                state="disabled",
                wrap=tk.WORD,
                relief=tk.GROOVE,
                bd=2
            )
            basic_info.pack(fill=tk.BOTH, expand=True, pady=5)

            # === RIGHT: Status Effects Display ===
            right_frame = tk.Frame(top_frame, bg="black")
            right_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=(10, 0))

            status_title = tk.Label(
                right_frame,
                text="✨ Active Effects",
                font=("Arial", 11, "bold"),
                fg="gold",
                bg="black"
            )
            status_title.pack()
            
            status_effects_display = tk.Text(
                right_frame,
                width=25,
                height=14,
                bg="#34495e",
                fg="lightyellow",
                font=("Consolas", 9),
                state="disabled",
                wrap=tk.WORD,
                relief=tk.GROOVE,
                bd=2
            )
            status_effects_display.pack(fill=tk.BOTH, expand=True, pady=5)

            # === MIDDLE SECTION: Detailed Stats and Equipment ===
            middle_frame = tk.Frame(main_container, bg="black")
            middle_frame.pack(fill=tk.BOTH, expand=True, pady=5)

            # Left: Detailed Statistics
            stats_frame = tk.Frame(middle_frame, bg="black")
            stats_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))

            stats_title = tk.Label(
                stats_frame,
                text="📈 Detailed Statistics",
                font=("Arial", 11, "bold"),
                fg="lightgreen",
                bg="black"
            )
            stats_title.pack()

            detailed_stats = tk.Text(
                stats_frame,
                width=45,
                height=18,
                bg="#1e1e1e",
                fg="lightgray",
                font=("Consolas", 9),
                state="disabled",
                wrap=tk.WORD,
                relief=tk.GROOVE,
                bd=2
            )
            detailed_stats.pack(fill=tk.BOTH, expand=True, pady=5)

            # Right: Equipment Manager
            equipment_frame = tk.Frame(middle_frame, bg="black")
            equipment_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=(5, 0))

            equipment_title = tk.Label(
                equipment_frame,
                text="⚔️ Equipment Manager",
                font=("Arial", 11, "bold"),
                fg="orange",
                bg="black"
            )
            equipment_title.pack()

            # Equipment slots visual display
            equipment_slots_frame = tk.Frame(equipment_frame, bg="#2c3e50", relief=tk.GROOVE, bd=2)
            equipment_slots_frame.pack(fill=tk.X, pady=5, padx=5)
            
            # Create equipment slots
            equipment_widgets = self._create_equipment_slots_display(equipment_slots_frame)

            # Equipment actions
            eq_actions_frame = tk.Frame(equipment_frame, bg="black")
            eq_actions_frame.pack(fill=tk.X, pady=5)

            eq_buttons = [
                ("🔍 Inspect Gear", "inspect_equipment", "#3498db"),
                ("⚔️ Quick Equip", "quick_equip_best", "#e74c3c"),
                ("🛡️ Optimize Defense", "optimize_defense", "#2ecc71"),
                ("🎒 Manage Inventory", "view_inventory", "#9b59b6")
            ]

            for text, callback_key, color in eq_buttons:
                btn = tk.Button(
                    eq_actions_frame,
                    text=text,
                    command=lambda k=callback_key: self._handle_button_click(k),
                    bg=color,
                    fg="white",
                    font=("Arial", 9, "bold"),
                    relief=tk.RAISED,
                    bd=1,
                    width=18
                )
                btn.pack(pady=2, fill=tk.X)

            # === BOTTOM SECTION: Enhanced Action Buttons ===
            bottom_frame = tk.Frame(main_container, bg="black")
            bottom_frame.pack(fill=tk.X, pady=(10, 0))

            # Enhanced button grid with better organization
            button_grid_frame = tk.Frame(bottom_frame, bg="black")
            button_grid_frame.pack()

            # Character Management Buttons
            char_buttons = [
                ("📊 View Stats", "detailed_character_view", "#3498db"),
                ("⬆️ Level Up", "level_up", "#2ecc71"),
                ("🎒 Inventory", "view_inventory", "#9b59b6"),
            ]

            # Resource Management Buttons  
            resource_buttons = [
                ("❤️ Restore HP", "restore_health", "#e74c3c"),
                ("💧 Restore MP", "restore_mana", "#3498db"),
                ("⚡ Restore SP", "restore_stamina", "#f39c12"),
            ]

            # System Buttons
            system_buttons = [
                ("💾 Save Game", "save_game", "#34495e"),
                ("📁 Load Game", "load_game", "#2ecc71"),
                ("🔄 Reload", "reload_game", "#95a5a6"),
            ]

            # Create button sections
            self._create_button_section(button_grid_frame, "Character", char_buttons, 0)
            self._create_button_section(button_grid_frame, "Resources", resource_buttons, 1)
            self._create_button_section(button_grid_frame, "System", system_buttons, 2)
            
            # Store widgets for external access
            stats_widgets = {
                'basic_info': basic_info,
                'status_effects_display': status_effects_display,
                'detailed_stats': detailed_stats,
                'equipment_slots_frame': equipment_slots_frame
            }
            stats_widgets.update(equipment_widgets)
            self.widgets.update(stats_widgets)
            
            self.logger.info("Enhanced stats tab setup completed")
            return {
                'success': True,
                'widgets': stats_widgets,
                'message': 'Enhanced stats tab created successfully'
            }
            
        except Exception as e:
            self.logger.error(f"Stats tab setup failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'message': 'Stats tab setup failed'
            }
    
    def _create_equipment_slots_display(self, parent_frame: tk.Frame) -> Dict[str, Any]:
        """Create interactive equipment slots display with enhanced functionality."""
        # Clear existing widgets
        for widget in parent_frame.winfo_children():
            widget.destroy()

        # Create equipment slot layout
        slots_data = [
            ("⛑️", "Helmet", "equipped_helmet"),
            ("🎭", "Cloak", "equipped_cloak"),
            ("👕", "Armor", "equipped_body"),
            ("⚔️", "Weapon", "weapon"),
            ("🛡️", "Offhand", "offhand"),
            ("👢", "Boots", "equipped_feet"),
            ("💍", "Ring", "equipped_ring"),
        ]

        equipment_widgets = {}

        # Create grid layout for equipment slots
        for i, (icon, name, attr) in enumerate(slots_data):
            row = i // 2
            col = i % 2
            
            slot_frame = tk.Frame(parent_frame, bg="#34495e", relief=tk.RAISED, bd=1)
            slot_frame.grid(row=row, column=col, padx=2, pady=2, sticky="ew")
            
            # Configure column weights
            parent_frame.grid_columnconfigure(col, weight=1)
            
            # Add interactive features
            slot_frame.configure(cursor="hand2")
            self._add_equipment_slot_interactions(slot_frame, attr, name)
            
            icon_label = tk.Label(slot_frame, text=icon, font=("Arial", 14), bg="#34495e", fg="white")
            icon_label.grid(row=0, column=0, padx=2)
            
            text_frame = tk.Frame(slot_frame, bg="#34495e")
            text_frame.grid(row=0, column=1, padx=2, sticky="w")
            
            name_label = tk.Label(text_frame, text=name, font=("Arial", 8, "bold"), bg="#34495e", fg="lightgray")
            name_label.pack(anchor="w")
            
            # This will be updated with actual equipment
            item_label = tk.Label(text_frame, text="(Empty)", font=("Arial", 8), bg="#34495e", fg="gray")
            item_label.pack(anchor="w")
            
            # Store references for updating
            equipment_widgets[f"slot_{attr}_label"] = item_label
            equipment_widgets[f"slot_{attr}_frame"] = slot_frame
            
        return equipment_widgets

    def _add_equipment_slot_interactions(self, widget: tk.Widget, slot_type: str, display_name: str) -> None:
        """Add interactive features to equipment slots."""
        def on_enter(event):
            widget.configure(bg="#4a6741")  # Hover effect
            
        def on_leave(event):
            widget.configure(bg="#34495e")  # Normal color
            
        def on_click(event):
            self._show_equipment_slot_popup(slot_type, display_name)
            
        def on_right_click(event):
            self._show_equipment_context_menu(event, slot_type, display_name)
        
        # Bind events to frame and all children
        for element in [widget] + list(widget.winfo_children()):
            if hasattr(element, 'winfo_children'):
                for child in element.winfo_children():
                    child.bind("<Enter>", on_enter)
                    child.bind("<Leave>", on_leave)
                    child.bind("<Button-1>", on_click)
                    child.bind("<Button-3>", on_right_click)
            element.bind("<Enter>", on_enter)
            element.bind("<Leave>", on_leave)
            element.bind("<Button-1>", on_click)
            element.bind("<Button-3>", on_right_click)

    def _show_equipment_slot_popup(self, slot_type: str, display_name: str) -> None:
        """Show detailed equipment slot information popup."""
        if not self.root:
            return
            
        # Create popup window
        popup = tk.Toplevel(self.root)
        popup.title(f"{display_name} Slot")
        popup.geometry("400x500")
        popup.configure(bg="#2c3e50")
        popup.resizable(False, False)
        
        # Make it modal
        popup.transient(self.root)
        popup.grab_set()
        
        # Center the popup
        popup.update_idletasks()
        x = (popup.winfo_screenwidth() - popup.winfo_width()) // 2
        y = (popup.winfo_screenheight() - popup.winfo_height()) // 2
        popup.geometry(f"+{x}+{y}")
        
        # Header
        header = tk.Frame(popup, bg="#34495e", height=60)
        header.pack(fill=tk.X, padx=10, pady=10)
        header.pack_propagate(False)
        
        title_text = f"📦 {display_name} Slot"
        title_label = tk.Label(header, text=title_text, font=("Arial", 12, "bold"), 
                              fg="white", bg="#34495e")
        title_label.pack(expand=True)
        
        # Main content frame
        main_frame = tk.Frame(popup, bg="#2c3e50")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        
        # Equipment details placeholder
        info_frame = tk.Frame(main_frame, bg="#34495e", relief=tk.GROOVE, bd=2)
        info_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        empty_label = tk.Label(info_frame, text=f"📦 {display_name} Slot Information", 
                              font=("Arial", 14, "bold"), fg="orange", bg="#34495e")
        empty_label.pack(pady=20)
        
        # Action buttons
        button_frame = tk.Frame(popup, bg="#2c3e50")
        button_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        equip_btn = tk.Button(button_frame, text="🎒 Browse Inventory", 
                             command=lambda: self._browse_for_equipment(popup, slot_type),
                             bg="#3498db", fg="white", font=("Arial", 10, "bold"))
        equip_btn.pack(side=tk.LEFT, padx=5)
        
        close_btn = tk.Button(button_frame, text="✖️ Close", 
                             command=popup.destroy,
                             bg="#95a5a6", fg="white", font=("Arial", 10, "bold"))
        close_btn.pack(side=tk.RIGHT)

    def _show_equipment_context_menu(self, event, slot_type: str, display_name: str) -> None:
        """Show right-click context menu for equipment slots."""
        if not self.root:
            return
            
        menu = tk.Menu(self.root, tearoff=0, bg="#34495e", fg="white", 
                      activebackground="#4a6741", activeforeground="white")
        
        menu.add_command(label=f"🎒 Browse for {display_name}", 
                        command=lambda: self._browse_for_equipment_type(slot_type))
        menu.add_separator()
        menu.add_command(label="📦 View All Equipment", 
                        command=lambda: self._handle_button_click("inspect_equipment"))
        menu.add_command(label="🎒 Open Inventory", 
                        command=lambda: self._handle_button_click("view_inventory"))
        menu.add_separator()
        menu.add_command(label=f"❌ Unequip {display_name}", 
                        command=lambda: self._handle_button_click(f"unequip_{slot_type}"))
        
        try:
            menu.tk_popup(event.x_root, event.y_root)
        finally:
            menu.grab_release()

    def _browse_for_equipment(self, popup: tk.Toplevel, slot_type: str) -> None:
        """Browse inventory for equipment to equip."""
        popup.destroy()
        self._browse_for_equipment_type(slot_type)

    def _browse_for_equipment_type(self, slot_type: str) -> None:
        """Open inventory browser filtered for specific equipment type."""
        # Switch to inventory tab and trigger browse callback
        if hasattr(self, 'tab_control'):
            self.tab_control.select(2)  # Inventory tab is usually index 2
        self._handle_button_click("view_inventory")

    def _create_button_section(self, parent: tk.Widget, title: str, buttons: list, column: int) -> None:
        """Create a section of buttons with title."""
        section_frame = tk.Frame(parent, bg="black")
        section_frame.grid(row=0, column=column, padx=10, pady=5, sticky="n")
        
        # Section title
        title_label = tk.Label(
            section_frame,
            text=title,
            font=("Arial", 10, "bold"),
            fg="white",
            bg="black"
        )
        title_label.pack(pady=(0, 5))
        
        # Buttons
        for text, callback_key, color in buttons:
            btn = tk.Button(
                section_frame,
                text=text,
                command=lambda k=callback_key: self._handle_button_click(k),
                bg=color,
                fg="white",
                font=("Arial", 9),
                relief=tk.RAISED,
                bd=2,
                width=14,
                height=1
            )
            btn.pack(pady=1)

    def _create_stats_buttons(self, parent: tk.Widget) -> None:
        """Create action buttons for the stats tab."""
        button_frame = tk.Frame(parent, bg="#222")
        button_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=10)
        
        # Button style configuration
        button_style = {
            'bg': '#444',
            'fg': 'white',
            'activebackground': '#666',
            'activeforeground': 'cyan',
            'font': ("Segoe UI", 11, "bold"),
            'relief': tk.RAISED,
            'bd': 2,
            'width': 14,
            'height': 2
        }
        
        # Button configurations
        button_configs = [
            ("View Inventory", "view_inventory", "#5bc0de"),
            ("Level Up", "level_up", "#5cb85c"),
            ("Equip Gear", "equip_gear", "#f0ad4e"),
            ("Restore Health", "restore_health", "#d9534f"),
            ("Restore Mana", "restore_mana", "#5bc0de"),
            ("Restore Stamina", "restore_stamina", "#f7e359"),
            ("Restore All", "restore_all_resources", "#337ab7"),
            ("Save Game", "save_game", "#0275d8"),
            ("Load Game", "load_game", "#5cb85c"),
        ]
        
        # Create buttons in grid layout
        max_cols = 3
        for idx, (text, callback_key, color) in enumerate(button_configs):
            row = idx // max_cols
            col = idx % max_cols
            
            btn = tk.Button(button_frame, text=text, 
                          command=lambda k=callback_key: self._handle_button_click(k),
                          **button_style)
            btn.configure(bg=color)
            btn.grid(row=row, column=col, padx=5, pady=5, sticky="ew")
        
        # Make columns expand equally
        for col in range(max_cols):
            button_frame.grid_columnconfigure(col, weight=1)
        
        # Add visual separator
        sep = tk.Frame(parent, height=2, bd=1, relief=tk.SUNKEN, bg="#444")
        sep.pack(fill=tk.X, padx=10, pady=(0, 10), side=tk.BOTTOM)
    
    def setup_combat_tab(self) -> Dict[str, Any]:
        """
        Set up the combat tab with battle visualization and controls.
        
        Returns:
            Dictionary with created widgets for external access
        """
        try:
            tab = self.tabs['combat']
            
            # Main combat frame
            combat_main = tk.Frame(tab, bg="black")
            combat_main.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            
            # Canvas for battle visualization
            canvas = tk.Canvas(combat_main, bg="black", width=600, height=400,
                             highlightthickness=2, highlightbackground="#444")
            canvas.grid(row=0, column=0, columnspan=2, sticky="nsew", padx=10, pady=10)
            
            # Enemy info panel (right)
            info_frame = tk.Frame(combat_main, bg="black")
            info_frame.grid(row=0, column=2, sticky="nsew", padx=(10, 0), pady=10)
            
            # Combo indicator
            combo_indicator = self._create_combo_indicator(info_frame)
            
            # Enemy info display
            enemy_info = tk.Text(info_frame, width=28, height=10, bg="#f8f8f8", fg="#222",
                               font=("Segoe UI", 10), state="disabled", relief=tk.RIDGE, bd=2)
            enemy_info.pack(fill=tk.BOTH, expand=True)
            
            # Combat controls
            self._create_combat_controls(combat_main)
            
            # Configure grid weights
            combat_main.grid_rowconfigure(0, weight=1)
            combat_main.grid_columnconfigure(0, weight=3)
            combat_main.grid_columnconfigure(1, weight=0)
            combat_main.grid_columnconfigure(2, weight=1)
            
            # Store widgets
            combat_widgets = {
                'canvas': canvas,
                'enemy_info': enemy_info,
                'combo_indicator': combo_indicator
            }
            self.widgets.update(combat_widgets)
            
            self.logger.info("Combat tab setup completed")
            return {
                'success': True,
                'widgets': combat_widgets,
                'message': 'Combat tab created successfully'
            }
            
        except Exception as e:
            self.logger.error(f"Combat tab setup failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'message': 'Combat tab setup failed'
            }
    
    def _create_combo_indicator(self, parent: tk.Widget) -> Dict[str, tk.Widget]:
        """Create combo indicator widgets."""
        combo_indicator = tk.Frame(parent, bg="#1a1a1a", relief=tk.RIDGE, bd=2)
        combo_indicator.pack(fill=tk.X, pady=(0, 5))
        
        combo_label = tk.Label(combo_indicator, text="COMBO", font=("Arial", 10, "bold"),
                              fg="gold", bg="#1a1a1a")
        combo_label.pack(pady=2)
        
        combat_combo_sequence = tk.Label(combo_indicator, text="Ready", font=("Arial", 9),
                                       fg="green", bg="#1a1a1a")
        combat_combo_sequence.pack(pady=2)
        
        combat_combo_progress = tk.Canvas(combo_indicator, height=20, bg="#333",
                                        highlightthickness=0)
        combat_combo_progress.pack(fill=tk.X, padx=5, pady=2)
        
        # Store combo widgets
        combo_widgets = {
            'frame': combo_indicator,
            'sequence': combat_combo_sequence,
            'progress': combat_combo_progress
        }
        self.widgets['combat_combo_sequence'] = combat_combo_sequence
        self.widgets['combat_combo_progress'] = combat_combo_progress
        
        return combo_widgets
    
    def _create_combat_controls(self, parent: tk.Widget) -> None:
        """Create combat control buttons."""
        control_frame = tk.Frame(parent, bg="#222")
        control_frame.grid(row=1, column=0, columnspan=3, sticky="ew", padx=10, pady=(0, 10))
        
        # Combat button configurations
        combat_buttons = [
            ("Attack", "attack", "#d9534f"),
            ("Heal", "heal", "#5cb85c"),
            ("Spawn Enemy", "spawn_enemy", "#f0ad4e"),
            ("Cast Fireball", "cast_fireball", "#ff7043"),
            ("Cast Ice Shard", "cast_ice_shard", "#42a5f5"),
            ("Test Dual Wield", "test_dual_wield", "#9c27b0"),
            ("Tick Status", "tick_status_effects", "#bdb76b")
        ]
        
        for idx, (text, callback_key, color) in enumerate(combat_buttons):
            btn = tk.Button(control_frame, text=text,
                          command=lambda k=callback_key: self._handle_button_click(k),
                          bg=color, fg="white", font=("Arial", 10, "bold"),
                          relief=tk.RAISED, bd=2)
            btn.grid(row=0, column=idx, padx=5, pady=5, sticky="ew")
            control_frame.grid_columnconfigure(idx, weight=1)
    
    def _handle_button_click(self, callback_key: str) -> None:
        """Handle button click events by calling registered callbacks."""
        if callback_key in self.callbacks:
            try:
                self.callbacks[callback_key]()
            except Exception as e:
                self.logger.error(f"Callback {callback_key} failed: {e}")
                self.log_message(f"Action failed: {e}", "error")
        else:
            self.logger.warning(f"No callback registered for: {callback_key}")
            self.log_message(f"Action not implemented: {callback_key}", "info")
    
    def register_callback(self, callback_key: str, callback_func: Callable) -> Dict[str, Any]:
        """
        Register a callback function for UI events.
        
        Args:
            callback_key: Unique identifier for the callback
            callback_func: Function to call when event occurs
            
        Returns:
            Registration result
        """
        try:
            self.callbacks[callback_key] = callback_func
            self.logger.debug(f"Registered callback: {callback_key}")
            return {
                'success': True,
                'message': f'Callback {callback_key} registered successfully'
            }
        except Exception as e:
            self.logger.error(f"Failed to register callback {callback_key}: {e}")
            return {
                'success': False,
                'error': str(e),
                'message': f'Callback registration failed'
            }
    
    def log_message(self, message: str, tag: str = "info") -> Dict[str, Any]:
        """
        Add a message to the log display.
        
        Args:
            message: The message to log
            tag: The formatting tag for the message
            
        Returns:
            Dictionary with success status and message
        """
        # Use external log callback if available
        if 'log' in self.callbacks:
            try:
                self.callbacks['log'](message)
                return {
                    'success': True,
                    'message': 'Message logged via external callback'
                }
            except Exception as e:
                self.logger.error(f"External log callback failed: {e}")
                # Fall through to internal logging
        
        # Fallback to internal logging if log widget exists
        if not self.log:
            return {
                'success': False,
                'error': 'No log widget available',
                'message': 'Logging failed - no widget'
            }
            
        try:
            timestamp = time.strftime("%H:%M:%S")
            self.log.insert(tk.END, f"[{timestamp}] ", "info")
            self.log.insert(tk.END, f"{message}\n", tag)
            self.log.see(tk.END)
            
            # Also log to logger
            self.logger.info(message)
            
            return {
                'success': True,
                'message': 'Message logged successfully'
            }
            
        except Exception as e:
            self.logger.error(f"Failed to log message: {e}")
            return {
                'success': False,
                'error': str(e),
                'message': 'Failed to log message'
            }
    
    def update_character_display(self, character_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update character information displays.
        
        Args:
            character_data: Dictionary containing character information
            
        Returns:
            Update operation result
        """
        try:
            if 'basic_info' not in self.widgets or 'detailed_stats' not in self.widgets:
                return {
                    'success': False,
                    'error': 'Missing character display widgets',
                    'message': 'Character display widgets not found'
                }
            
            # Get player from character data
            if 'player' not in character_data or not character_data['player']:
                return {
                    'success': False,
                    'error': 'No player data provided',
                    'message': 'No player character data'
                }
            
            player = character_data['player']
            
            # Update basic info
            basic_info = self.widgets['basic_info']
            basic_info.config(state="normal")
            basic_info.delete(1.0, tk.END)
            
            # Build basic character info text
            basic_text = f"Name: {getattr(player, 'name', 'Unknown')}\n"
            basic_text += f"Level: {getattr(player, 'level', 1)}\n"
            
            # Add grade and rarity if available
            if hasattr(player, 'grade'):
                grade_val = player.grade
                try:
                    from game_sys.config.config_manager import ConfigManager
                    cfg = ConfigManager()
                    grade_list = cfg.get('defaults.grades', ["ONE", "TWO", "THREE", "FOUR", "FIVE", "SIX", "SEVEN"])
                    if isinstance(grade_val, int) and 0 <= grade_val < len(grade_list):
                        grade_display = grade_list[grade_val]
                    else:
                        grade_display = str(grade_val)
                except Exception:
                    grade_display = str(grade_val)
                basic_text += f"Grade: {grade_display}\n"
            if hasattr(player, 'rarity'):
                basic_text += f"Rarity: {player.rarity}\n"
                
            health_val = f"{getattr(player, 'current_health', 0):.2f}/"
            health_val += f"{getattr(player, 'max_health', 1):.2f}"
            basic_text += f"Health: {health_val}\n"
            
            basic_info.insert(tk.END, basic_text)
            basic_info.config(state="disabled")
            
            # Update detailed stats
            detailed_stats = self.widgets['detailed_stats']
            detailed_stats.config(state="normal")
            detailed_stats.delete(1.0, tk.END)
            
            # Build detailed character info (abbreviated version for UI service)
            detailed_text = f"== {getattr(player, 'name', 'Unknown')} ==\n"
            detailed_text += f"Level: {getattr(player, 'level', 1)}\n"
            
            # Add grade and rarity to detailed view
            if hasattr(player, 'grade'):
                grade_val = player.grade
                try:
                    from game_sys.config.config_manager import ConfigManager
                    cfg = ConfigManager()
                    grade_list = cfg.get('defaults.grades', [])
                    if isinstance(grade_val, int) and 0 <= grade_val < len(grade_list):
                        grade_display = grade_list[grade_val]
                    else:
                        grade_display = str(grade_val)
                except Exception:
                    grade_display = str(grade_val)
                detailed_text += f"Grade: {grade_display}\n"
            if hasattr(player, 'rarity'):
                detailed_text += f"Rarity: {player.rarity}\n"
                
            detailed_text += f"Health: {health_val}\n"

            # Show all stats in organized categories
            detailed_text += "\n=== CORE ATTRIBUTES ===\n"
            
            # Primary stats that should always be shown
            primary_stats = [
                'strength', 'dexterity', 'intelligence', 'wisdom', 'constitution',
                'vitality', 'agility', 'luck', 'focus'
            ]
            
            for stat in primary_stats:
                try:
                    if hasattr(player, "get_stat"):
                        current_val = float(player.get_stat(stat))
                    elif hasattr(player, 'base_stats') and stat in player.base_stats:
                        current_val = float(player.base_stats[stat])
                    else:
                        continue  # Skip if stat not available
                    
                    display_name = stat.replace("_", " ").title()
                    detailed_text += f"  {display_name}: {current_val:.2f}\n"
                except Exception:
                    continue
            
            # Combat stats
            detailed_text += "\n=== COMBAT STATS ===\n"
            combat_stats = [
                'accuracy', 'critical_chance', 'speed',
                'defense', 'magic_defense', 'dodge_chance', 'parry_chance', 'block_chance'
            ]
            
            for stat in combat_stats:
                try:
                    if hasattr(player, "get_stat"):
                        current_val = float(player.get_stat(stat))
                    elif hasattr(player, stat):
                        current_val = float(getattr(player, stat))
                    elif hasattr(player, 'base_stats') and stat in player.base_stats:
                        current_val = float(player.base_stats[stat])
                    else:
                        continue
                    
                    display_name = stat.replace("_", " ").title()
                    if 'chance' in stat.lower():
                        detailed_text += f"  {display_name}: {current_val:.1%}\n"
                    else:
                        detailed_text += f"  {display_name}: {current_val:.2f}\n"
                except Exception:
                    continue
            
            # Derived stats
            detailed_text += "\n=== DERIVED STATS ===\n"
            derived_stats = [
                'max_health', 'max_mana', 'max_stamina', 'health_regen', 'mana_regen', 'stamina_regen',
                'magic_power', 'initiative', 'speed', 'carrying_capacity'
            ]
            
            for stat in derived_stats:
                try:
                    if hasattr(player, "get_stat"):
                        current_val = float(player.get_stat(stat))
                    elif hasattr(player, stat):
                        current_val = float(getattr(player, stat))
                    elif hasattr(player, 'base_stats') and stat in player.base_stats:
                        current_val = float(player.base_stats[stat])
                    else:
                        continue
                    
                    display_name = stat.replace("_", " ").title()
                    detailed_text += f"  {display_name}: {current_val:.2f}\n"
                except Exception:
                    continue
            
            # Show any additional stats from base_stats that weren't covered
            if hasattr(player, 'base_stats') and isinstance(player.base_stats, dict):
                covered_stats = set(primary_stats + combat_stats + derived_stats + 
                                  ['grade', 'rarity', 'skip_default_job', 'max_targets', 'level'])
                additional_stats = []
                
                for raw_key, raw_val in sorted(player.base_stats.items()):
                    key = str(raw_key).strip().lower()
                    if key not in covered_stats and not key.startswith("_"):
                        additional_stats.append((raw_key, raw_val))
                
                if additional_stats:
                    detailed_text += "\n=== ADDITIONAL STATS ===\n"
                    for stat_name, base_val in additional_stats:
                        display_name = stat_name.replace("_", " ").title()
                        try:
                            if hasattr(player, "get_stat"):
                                effective_val = float(player.get_stat(stat_name.lower()))
                            else:
                                effective_val = float(base_val)
                        except Exception:
                            effective_val = base_val
                        detailed_text += f"  {display_name}: {effective_val:.2f}\n"
            
            # Add equipment info
            detailed_text += "\n=== EQUIPMENT ===\n"
            weapon = getattr(player, 'weapon', None)
            if weapon:
                detailed_text += f"  Weapon: {weapon.name}\n"
            else:
                detailed_text += "  Weapon: (None)\n"

            offhand = getattr(player, 'offhand', None)
            if offhand:
                detailed_text += f"  Offhand: {offhand.name}\n"
            else:
                detailed_text += "  Offhand: (None)\n"
            
            detailed_stats.insert(tk.END, detailed_text)
            detailed_stats.config(state="disabled")
            
            # Update status effects if widget exists
            if 'status_effects_display' in self.widgets:
                status_display = self.widgets['status_effects_display']
                status_display.config(state="normal")
                status_display.delete(1.0, tk.END)
                # Add status effects info here if available
                status_display.insert(tk.END, "No active effects")
                status_display.config(state="disabled")
            
            self.logger.debug("Character display updated via UI service")
            
            return {
                'success': True,
                'message': 'Character display updated successfully'
            }
            
        except Exception as e:
            self.logger.error(f"Failed to update character display: {e}")
            return {
                'success': False,
                'error': str(e),
                'message': 'Character display update failed'
            }
    
    def update_enemy_display(self, enemy_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update enemy information display.
        
        Args:
            enemy_data: Dictionary containing enemy information
            
        Returns:
            Update operation result
        """
        try:
            if 'enemy_info' not in self.widgets:
                return {
                    'success': False,
                    'error': 'No enemy_info widget available',
                    'message': 'Enemy info widget not found'
                }
                
            enemy_info = self.widgets['enemy_info']
            enemy_info.config(state="normal")
            enemy_info.delete(1.0, tk.END)
            
            # Build enemy info text from enemy data
            if 'enemy' in enemy_data and enemy_data['enemy']:
                enemy = enemy_data['enemy']
                
                # Build enemy info text
                info = f"Enemy: {getattr(enemy, 'name', 'Unknown')}\n"
                
                # Add level, grade, and rarity if available
                if hasattr(enemy, 'level'):
                    info += f"Level: {enemy.level}\n"
                if hasattr(enemy, 'grade'):
                    grade_val = enemy.grade
                    try:
                        from game_sys.config.config_manager import ConfigManager
                        cfg = ConfigManager()
                        grade_list = cfg.get('defaults.grades', ["ONE", "TWO", "THREE", "FOUR", "FIVE", "SIX", "SEVEN"])
                        if isinstance(grade_val, int) and 0 <= grade_val < len(grade_list):
                            grade_display = grade_list[grade_val]
                        else:
                            grade_display = str(grade_val)
                    except Exception:
                        grade_display = str(grade_val)
                    info += f"Grade: {grade_display}\n"
                if hasattr(enemy, 'rarity'):
                    info += f"Rarity: {enemy.rarity}\n"
                    
                health_val = f"{getattr(enemy, 'current_health', 0):.2f}/"
                health_val += f"{getattr(enemy, 'max_health', 1):.2f}"
                info += f"Health: {health_val}\n"

                # Add BASE STATS section (from base_stats dictionary)
                if hasattr(enemy, 'base_stats'):
                    info += "\n=== BASE STATS ===\n"
                    
                    # List of core stats to display
                    rpg_stats = [
                        'strength', 'dexterity', 'vitality', 'intelligence',
                        'wisdom', 'constitution', 'luck', 
                    ]
                    
                    # Display each base stat
                    for stat in rpg_stats:
                        if stat in enemy.base_stats:
                            info += f"  {stat.title()}: {enemy.base_stats[stat]:.2f}\n"
                
                # Add COMBAT STATS section if get_stat method is available
                if hasattr(enemy, 'get_stat'):
                    info += "\n=== COMBAT STATS ===\n"
                    combat_stats = ['attack', 'defense', 'speed', 'magic_power', 'critical_chance', 'dodge_chance', 'parry_chance', 'block_chance']
                    
                    for stat in combat_stats:
                        try:
                            value = enemy.get_stat(stat)
                            if 'chance' in stat:
                                info += f"  {stat.replace('_', ' ').title()}: {value:.1%}\n"
                            else:
                                info += f"  {stat.replace('_', ' ').title()}: {value:.2f}\n"
                        except:
                            info += f"  {stat.replace('_', ' ').title()}: N/A\n"

                # Add resistances and weaknesses
                if hasattr(enemy, 'resistances') and enemy.resistances:
                    info += "\nResistances:\n"
                    for damage_type, value in enemy.resistances.items():
                        info += f"  {damage_type.name}: {int(value * 100)}%\n"

                if hasattr(enemy, 'weaknesses') and enemy.weaknesses:
                    info += "\nWeaknesses:\n"
                    for damage_type, value in enemy.weaknesses.items():
                        info += f"  {damage_type.name}: +{int(value * 100)}%\n"
                
                enemy_info.insert(tk.END, info)
            else:
                enemy_info.insert(tk.END, "No enemy present")
            
            enemy_info.config(state="disabled")
            
            self.logger.debug("Enemy display updated via UI service")
            
            return {
                'success': True,
                'message': 'Enemy display updated successfully'
            }
            
        except Exception as e:
            self.logger.error(f"Failed to update enemy display: {e}")
            return {
                'success': False,
                'error': str(e),
                'message': 'Enemy display update failed'
            }
    
    def get_widget(self, widget_name: str) -> Optional[Any]:
        """
        Get a widget by name for external access.
        
        Args:
            widget_name: Name of the widget to retrieve
            
        Returns:
            Widget instance or None if not found
        """
        return self.widgets.get(widget_name)
    
    def get_root(self) -> Optional[tk.Tk]:
        """Get the root Tkinter window."""
        return self.root
    
    def start_main_loop(self) -> None:
        """Start the Tkinter main event loop."""
        if self.root:
            self.logger.info("Starting UI main loop")
            self.root.mainloop()
        else:
            raise RuntimeError("Root window not initialized")
    
    def setup_inventory_tab(self) -> Dict[str, Any]:
        """
        Set up the inventory management tab.
        
        Returns:
            Dictionary with created widgets for external access
        """
        try:
            tab = self.tabs['inventory']
            
            # Main inventory frame
            main_inv_frame = tk.Frame(tab, bg="black")
            main_inv_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

            # Left side: Current inventory
            left_inv_frame = tk.Frame(main_inv_frame, bg="black")
            left_inv_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)

            # Inventory title
            inv_title = tk.Label(
                left_inv_frame,
                text="Current Inventory",
                bg="black",
                fg="white",
                font=("Arial", 14, "bold")
            )
            inv_title.pack(pady=5)

            # Inventory list
            inventory_listbox = tk.Listbox(
                left_inv_frame,
                bg="light gray",
                fg="black",
                height=15,
                width=40
            )
            inventory_listbox.pack(fill=tk.BOTH, expand=True, pady=5)

            # Inventory item details
            item_details = tk.Text(
                left_inv_frame,
                bg="light gray",
                fg="black",
                height=5,
                width=40,
                state="disabled"
            )
            item_details.pack(fill=tk.X, pady=5)

            # Middle: Inventory actions
            middle_inv_frame = tk.Frame(main_inv_frame, bg="black")
            middle_inv_frame.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=20)

            # Right side: Equipment and item creation
            right_inv_frame = tk.Frame(main_inv_frame, bg="black")
            right_inv_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5)

            # Equipment title
            eq_title = tk.Label(
                right_inv_frame,
                text="Equipped Items",
                bg="black",
                fg="white",
                font=("Arial", 14, "bold")
            )
            eq_title.pack(pady=5)

            # Equipment display
            equipment_display = tk.Text(
                right_inv_frame,
                bg="light gray",
                fg="black",
                height=10,
                width=30,
                state="disabled"
            )
            equipment_display.pack(fill=tk.X, pady=5)

            # Available items title
            avail_title = tk.Label(
                right_inv_frame,
                text="Available Items to Create",
                bg="black",
                fg="white",
                font=("Arial", 12, "bold")
            )
            avail_title.pack(pady=(20, 5))

            # Available items list
            available_items_listbox = tk.Listbox(
                right_inv_frame,
                bg="light gray",
                fg="black",
                height=10,
                width=30
            )
            available_items_listbox.pack(fill=tk.X, pady=5)

            # Create inventory action buttons
            self._create_inventory_buttons(middle_inv_frame)

            # Store widgets for external access
            inventory_widgets = {
                'inventory_listbox': inventory_listbox,
                'item_details': item_details,
                'equipment_display': equipment_display,
                'available_items_listbox': available_items_listbox
            }
            self.widgets.update(inventory_widgets)

            self.logger.info("Inventory tab setup completed")
            return {
                'success': True,
                'widgets': inventory_widgets,
                'message': 'Inventory tab created successfully'
            }

        except Exception as e:
            self.logger.error(f"Inventory tab setup failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'message': 'Inventory tab setup failed'
            }

    def _create_inventory_buttons(self, parent: tk.Widget) -> None:
        """Create inventory action buttons."""
        inventory_buttons = [
            ("Use Item", "use_item"),
            ("Equip Item", "equip_item"),
            ("Drop Item", "drop_item"),
            ("", None),  # Spacer
            ("Create Item", "create_item"),
            ("Add Random Item", "add_random_item"),
            ("", None),  # Spacer
            ("Unequip Weapon", "unequip_weapon"),
            ("Unequip Armor", "unequip_armor"),
            ("Unequip Offhand", "unequip_offhand"),
            ("Unequip Ring", "unequip_ring"),
        ]

        for text, callback_key in inventory_buttons:
            if text == "":  # Spacer
                spacer = tk.Label(parent, text="", bg="black", height=1)
                spacer.pack(pady=5)
            else:
                btn = tk.Button(
                    parent,
                    text=text,
                    command=lambda k=callback_key: self._handle_button_click(k),
                    width=15
                )
                btn.pack(pady=5)

    def setup_leveling_tab(self) -> Dict[str, Any]:
        """
        Set up the leveling tab with stat allocation interface.
        
        Returns:
            Dictionary with created widgets for external access
        """
        try:
            tab = self.tabs['leveling']
            
            # Main leveling frame
            main_leveling_frame = tk.Frame(tab, bg="black")
            main_leveling_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

            # Left side: Stat allocation
            left_leveling_frame = tk.Frame(main_leveling_frame, bg="black")
            left_leveling_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)

            # Title
            leveling_title = tk.Label(
                left_leveling_frame,
                text="Character Advancement",
                bg="black",
                fg="white",
                font=("Arial", 16, "bold")
            )
            leveling_title.pack(pady=5)

            # Available points display
            available_points_label = tk.Label(
                left_leveling_frame,
                text="Available Stat Points: 0",
                bg="black",
                fg="cyan",
                font=("Arial", 12, "bold")
            )
            available_points_label.pack(pady=5)

            # Stats display area
            stats_display = tk.Text(
                left_leveling_frame,
                bg="light gray",
                fg="black",
                height=20,
                width=50,
                state="disabled"
            )
            stats_display.pack(fill=tk.BOTH, expand=True, pady=5)

            # Right side: Action buttons
            right_leveling_frame = tk.Frame(main_leveling_frame, bg="black")
            right_leveling_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=10)

            # Create leveling action buttons
            self._create_leveling_buttons(right_leveling_frame)

            # Store widgets for external access
            leveling_widgets = {
                'available_points_label': available_points_label,
                'stats_display': stats_display
            }
            self.widgets.update(leveling_widgets)

            self.logger.info("Leveling tab setup completed")
            return {
                'success': True,
                'widgets': leveling_widgets,
                'message': 'Leveling tab created successfully'
            }

        except Exception as e:
            self.logger.error(f"Leveling tab setup failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'message': 'Leveling tab setup failed'
            }

    def _create_leveling_buttons(self, parent: tk.Widget) -> None:
        """Create leveling action buttons."""
        leveling_buttons = [
            ("Allocate Point", "allocate_stat_point"),
            ("Reset Stats", "reset_all_stats"),
            ("", None),  # Spacer
            ("Level Up", "level_up"),
            ("", None),  # Spacer
            ("View Build", "view_character_build"),
            ("Save Build", "save_character_build"),
        ]

        for text, callback_key in leveling_buttons:
            if text == "":  # Spacer
                spacer = tk.Label(parent, text="", bg="black", height=1)
                spacer.pack(pady=5)
            else:
                btn = tk.Button(
                    parent,
                    text=text,
                    command=lambda k=callback_key: self._handle_button_click(k),
                    width=15
                )
                btn.pack(pady=5)

    def setup_enchanting_tab(self) -> Dict[str, Any]:
        """
        Set up the enchanting and spell management tab.
        
        Returns:
            Dictionary with created widgets for external access
        """
        try:
            tab = self.tabs['enchanting']
            
            # Main enchanting frame
            main_frame = tk.Frame(tab, bg="black")
            main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

            # Title
            tk.Label(
                main_frame,
                text="Enchanting & Spell Management",
                bg="black",
                fg="white",
                font=("Arial", 16, "bold")
            ).pack(pady=(0, 10))

            # Create three columns
            columns_frame = tk.Frame(main_frame, bg="black")
            columns_frame.pack(fill=tk.BOTH, expand=True)

            # Left: Available enchantments
            left_frame = tk.Frame(columns_frame, bg="dark gray")
            left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))

            tk.Label(
                left_frame,
                text="Available Enchantments:",
                bg="dark gray",
                fg="white",
                font=("Arial", 10, "bold")
            ).pack(anchor="w", pady=(0, 5))

            available_enchants_listbox = tk.Listbox(
                left_frame,
                bg="black",
                fg="white",
                height=8
            )
            available_enchants_listbox.pack(fill=tk.BOTH, expand=True, pady=5)

            # Middle: Learned enchantments
            middle_frame = tk.Frame(columns_frame, bg="dark gray")
            middle_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)

            tk.Label(
                middle_frame,
                text="Known Enchantments:",
                bg="dark gray",
                fg="white",
                font=("Arial", 10, "bold")
            ).pack(anchor="w", pady=(0, 5))

            learned_enchants_listbox = tk.Listbox(
                middle_frame,
                bg="black",
                fg="white",
                height=8
            )
            learned_enchants_listbox.pack(fill=tk.BOTH, expand=True, pady=5)

            # Right: Enchantable items
            right_frame = tk.Frame(columns_frame, bg="dark gray")
            right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))

            tk.Label(
                right_frame,
                text="Enchantable Items:",
                bg="dark gray",
                fg="white",
                font=("Arial", 10, "bold")
            ).pack(anchor="w", pady=(0, 5))

            enchantable_items_listbox = tk.Listbox(
                right_frame,
                bg="black",
                fg="white",
                height=8
            )
            enchantable_items_listbox.pack(fill=tk.BOTH, expand=True, pady=5)

            # Bottom: Control buttons
            button_frame = tk.Frame(main_frame, bg="black")
            button_frame.pack(fill=tk.X, pady=10)

            # Create enchanting action buttons
            self._create_enchanting_buttons(button_frame)

            # Store widgets for external access
            enchanting_widgets = {
                'available_enchants_listbox': available_enchants_listbox,
                'learned_enchants_listbox': learned_enchants_listbox,
                'enchantable_items_listbox': enchantable_items_listbox
            }
            self.widgets.update(enchanting_widgets)

            self.logger.info("Enchanting tab setup completed")
            return {
                'success': True,
                'widgets': enchanting_widgets,
                'message': 'Enchanting tab created successfully'
            }

        except Exception as e:
            self.logger.error(f"Enchanting tab setup failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'message': 'Enchanting tab setup failed'
            }

    def _create_enchanting_buttons(self, parent: tk.Widget) -> None:
        """Create enchanting action buttons."""
        enchanting_buttons = [
            ("Learn Enchantment", "learn_enchantment"),
            ("Apply Enchantment", "apply_enchantment"),
            ("Remove Enchantment", "remove_enchantment"),
            ("", None),  # Spacer
            ("Create Spell", "create_spell"),
            ("Cast Spell", "cast_spell"),
        ]

        for text, callback_key in enchanting_buttons:
            if text == "":  # Spacer
                spacer = tk.Label(parent, text="", bg="black", height=1)
                spacer.pack(side=tk.LEFT, padx=10)
            else:
                btn = tk.Button(
                    parent,
                    text=text,
                    command=lambda k=callback_key: self._handle_button_click(k),
                    width=15
                )
                btn.pack(side=tk.LEFT, padx=5)

    def setup_progression_tab(self) -> Dict[str, Any]:
        """
        Set up the progression tracking tab.
        
        Returns:
            Dictionary with created widgets for external access
        """
        try:
            tab = self.tabs['progression']
            
            # Main progression frame
            main_frame = tk.Frame(tab, bg="black")
            main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

            # Title
            tk.Label(
                main_frame,
                text="Character Progression",
                bg="black",
                fg="white",
                font=("Arial", 16, "bold")
            ).pack(pady=(0, 10))

            # Create two columns
            columns_frame = tk.Frame(main_frame, bg="black")
            columns_frame.pack(fill=tk.BOTH, expand=True)

            # Left: Progression details
            left_frame = tk.Frame(columns_frame, bg="black")
            left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))

            # Progression display
            progression_display = tk.Text(
                left_frame,
                bg="light gray",
                fg="black",
                height=20,
                width=50,
                state="disabled"
            )
            progression_display.pack(fill=tk.BOTH, expand=True)

            # Right: Action buttons
            right_frame = tk.Frame(columns_frame, bg="black")
            right_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=(10, 0))

            # Create progression action buttons
            self._create_progression_buttons(right_frame)

            # Store widgets for external access
            progression_widgets = {
                'progression_display': progression_display
            }
            self.widgets.update(progression_widgets)

            self.logger.info("Progression tab setup completed")
            return {
                'success': True,
                'widgets': progression_widgets,
                'message': 'Progression tab created successfully'
            }

        except Exception as e:
            self.logger.error(f"Progression tab setup failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'message': 'Progression tab setup failed'
            }

    def _create_progression_buttons(self, parent: tk.Widget) -> None:
        """Create progression action buttons."""
        progression_buttons = [
            ("View Stats History", "view_stats_history"),
            ("Export Character", "export_character"),
            ("Import Character", "import_character"),
            ("", None),  # Spacer
            ("Reset Progress", "reset_progress"),
        ]

        for text, callback_key in progression_buttons:
            if text == "":  # Spacer
                spacer = tk.Label(parent, text="", bg="black", height=1)
                spacer.pack(pady=5)
            else:
                btn = tk.Button(
                    parent,
                    text=text,
                    command=lambda k=callback_key: self._handle_button_click(k),
                    width=15
                )
                btn.pack(pady=5)

    def setup_combo_tab(self) -> Dict[str, Any]:
        """
        Set up the combo system tab.
        
        Returns:
            Dictionary with created widgets for external access
        """
        try:
            tab = self.tabs['combo']
            
            # Title
            title = tk.Label(tab, text="Combo System", font=("Arial", 16, "bold"), fg="cyan", bg="black")
            title.pack(pady=(10, 5))

            # Current combo status
            combo_status_frame = tk.Frame(tab, bg="black")
            combo_status_frame.pack(fill=tk.X, padx=20, pady=10)

            tk.Label(combo_status_frame, text="Combo Status:", font=("Arial", 12, "bold"),
                    fg="white", bg="black").pack(side=tk.LEFT)

            combo_status_label = tk.Label(combo_status_frame, text="Ready for combo...",
                                        font=("Arial", 12), fg="white", bg="black")
            combo_status_label.pack(side=tk.LEFT, padx=(10, 0))

            # Combo sequence display
            sequence_frame = tk.Frame(tab, bg="dark gray", relief=tk.RIDGE, bd=2)
            sequence_frame.pack(fill=tk.X, padx=20, pady=5)

            tk.Label(sequence_frame, text="Combo Sequence:", font=("Arial", 10, "bold"),
                    fg="white", bg="dark gray").pack(pady=5)

            combo_sequence_label = tk.Label(sequence_frame, text="None", font=("Arial", 10),
                                          fg="green", bg="dark gray")
            combo_sequence_label.pack(pady=5)

            # Progress bar for combo timing
            combo_progress = ttk.Progressbar(
                sequence_frame,
                mode='determinate',
                style='Combo.Horizontal.TProgressbar'
            )
            combo_progress.pack(fill=tk.X, padx=10, pady=5)
            combo_progress['maximum'] = 100

            # Available combos display
            available_frame = tk.Frame(tab, bg="black")
            available_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

            tk.Label(available_frame, text="Available Combos:", font=("Arial", 12, "bold"),
                    fg="cyan", bg="black").pack()

            combo_list = tk.Text(available_frame, bg="light gray", fg="black",
                                height=10, width=60, state="disabled")
            combo_list.pack(fill=tk.BOTH, expand=True, pady=5)

            # Action buttons
            button_frame = tk.Frame(tab, bg="black")
            button_frame.pack(fill=tk.X, padx=20, pady=10)

            # Create combo action buttons
            self._create_combo_buttons(button_frame)

            # Store widgets for external access
            combo_widgets = {
                'combo_status_label': combo_status_label,
                'combo_sequence_label': combo_sequence_label,
                'combo_progress': combo_progress,
                'combo_list': combo_list
            }
            self.widgets.update(combo_widgets)

            self.logger.info("Combo tab setup completed")
            return {
                'success': True,
                'widgets': combo_widgets,
                'message': 'Combo tab created successfully'
            }

        except Exception as e:
            self.logger.error(f"Combo tab setup failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'message': 'Combo tab setup failed'
            }

    def _create_combo_buttons(self, parent: tk.Widget) -> None:
        """Create combo action buttons."""
        combo_buttons = [
            ("Practice Combo", "practice_combo"),
            ("Reset Combo", "reset_combo"),
            ("View Guide", "view_combo_guide"),
        ]

        for text, callback_key in combo_buttons:
            btn = tk.Button(
                parent,
                text=text,
                command=lambda k=callback_key: self._handle_button_click(k),
                width=15
            )
            btn.pack(side=tk.LEFT, padx=5)

    def setup_settings_tab(self) -> Dict[str, Any]:
        """
        Set up the settings/configuration tab.
        
        Returns:
            Dictionary with created widgets for external access
        """
        try:
            tab = self.tabs['settings']
            
            # Title
            title = tk.Label(tab, text="Game Settings", font=("Arial", 16, "bold"), fg="white", bg="black")
            title.pack(pady=(10, 20))

            # Settings content
            settings_frame = tk.Frame(tab, bg="black")
            settings_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

            # Settings display
            settings_display = tk.Text(
                settings_frame,
                bg="light gray",
                fg="black",
                height=15,
                width=60,
                state="disabled"
            )
            settings_display.pack(fill=tk.BOTH, expand=True)

            # Action buttons
            button_frame = tk.Frame(settings_frame, bg="black")
            button_frame.pack(fill=tk.X, pady=10)

            # Create settings action buttons
            self._create_settings_buttons(button_frame)

            # Store widgets for external access
            settings_widgets = {
                'settings_display': settings_display
            }
            self.widgets.update(settings_widgets)

            self.logger.info("Settings tab setup completed")
            return {
                'success': True,
                'widgets': settings_widgets,
                'message': 'Settings tab created successfully'
            }

        except Exception as e:
            self.logger.error(f"Settings tab setup failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'message': 'Settings tab setup failed'
            }

    def _create_settings_buttons(self, parent: tk.Widget) -> None:
        """Create settings action buttons."""
        settings_buttons = [
            ("Load Config", "load_config"),
            ("Save Config", "save_config"),
            ("Reset to Defaults", "reset_config"),
        ]

        for text, callback_key in settings_buttons:
            btn = tk.Button(
                parent,
                text=text,
                command=lambda k=callback_key: self._handle_button_click(k),
                width=15
            )
            btn.pack(side=tk.LEFT, padx=5)

    def update_inventory_display(self, character_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update inventory display with current inventory data.
        
        Args:
            character_data: Dictionary containing character information
            
        Returns:
            Update operation result
        """
        try:
            if 'inventory_listbox' not in self.widgets:
                return {
                    'success': False,
                    'error': 'Missing inventory display widget',
                    'message': 'Inventory display widget not found'
                }
                
            inventory_listbox = self.widgets['inventory_listbox']
            inventory_listbox.delete(0, tk.END)
            
            # Get player from character data
            if 'player' not in character_data or not character_data['player']:
                inventory_listbox.insert(tk.END, "No character data available")
                return {
                    'success': False,
                    'error': 'No player data provided',
                    'message': 'No player character data'
                }
            
            player = character_data['player']
            
            # Display inventory items
            if hasattr(player, 'inventory') and player.inventory:
                items = player.inventory.list_items() if hasattr(player.inventory, 'list_items') else []
                if items:
                    for item in items:
                        item_name = getattr(item, 'name', 'Unknown Item')
                        item_type = getattr(item, 'item_type', 'unknown')
                        inventory_listbox.insert(tk.END, f"{item_name} ({item_type})")
                else:
                    inventory_listbox.insert(tk.END, "Inventory is empty")
            else:
                inventory_listbox.insert(tk.END, "Inventory is empty")
            
            self.logger.debug("Inventory display updated via UI service")
            return {
                'success': True,
                'message': 'Inventory display updated successfully'
            }
            
        except Exception as e:
            self.logger.error(f"Failed to update inventory display: {e}")
            return {
                'success': False,
                'error': str(e),
                'message': 'Inventory display update failed'
            }

    def update_equipment_display(self, character_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update equipment display with current equipped items.
        
        Args:
            character_data: Dictionary containing character information
            
        Returns:
            Update operation result
        """
        try:
            if 'equipment_display' not in self.widgets:
                return {
                    'success': False,
                    'error': 'Missing equipment display widget',
                    'message': 'Equipment display widget not found'
                }
                
            equipment_display = self.widgets['equipment_display']
            equipment_display.config(state="normal")
            equipment_display.delete(1.0, tk.END)
            
            # Get player from character data
            if 'player' not in character_data or not character_data['player']:
                equipment_display.insert(tk.END, "No character data available")
                equipment_display.config(state="disabled")
                return {
                    'success': False,
                    'error': 'No player data provided',
                    'message': 'No player character data'
                }
            
            player = character_data['player']
            
            # Build equipment info text
            equipment_text = "=== EQUIPPED ITEMS ===\n\n"
            
            # Check each equipment slot
            equipment_slots = [
                ('weapon', 'Weapon'),
                ('offhand', 'Offhand'),
                ('equipped_body', 'Body Armor'),
                ('equipped_helmet', 'Helmet'),
                ('equipped_feet', 'Boots'),
                ('equipped_ring', 'Ring')
            ]
            
            for slot_attr, slot_name in equipment_slots:
                item = getattr(player, slot_attr, None)
                if item:
                    equipment_text += f"{slot_name}: {item.name}\n"
                    if hasattr(item, 'base_damage') and item.base_damage > 0:
                        equipment_text += f"  Damage: {item.base_damage}\n"
                    if hasattr(item, 'defense') and item.defense > 0:
                        equipment_text += f"  Defense: {item.defense}\n"
                else:
                    equipment_text += f"{slot_name}: (Empty)\n"
                equipment_text += "\n"
            
            equipment_display.insert(tk.END, equipment_text)
            equipment_display.config(state="disabled")
            
            self.logger.debug("Equipment display updated via UI service")
            return {
                'success': True,
                'message': 'Equipment display updated successfully'
            }
            
        except Exception as e:
            self.logger.error(f"Failed to update equipment display: {e}")
            return {
                'success': False,
                'error': str(e),
                'message': 'Equipment display update failed'
            }

    def update_leveling_display(self, character_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update leveling display with current character stats and available points.
        
        Args:
            character_data: Dictionary containing character information
            
        Returns:
            Update operation result
        """
        try:
            if 'stats_display' not in self.widgets or 'available_points_label' not in self.widgets:
                return {
                    'success': False,
                    'error': 'Missing leveling display widgets',
                    'message': 'Leveling display widgets not found'
                }
                
            stats_display = self.widgets['stats_display']
            available_points_label = self.widgets['available_points_label']
            
            # Get player from character data
            if 'player' not in character_data or not character_data['player']:
                stats_display.config(state="normal")
                stats_display.delete(1.0, tk.END)
                stats_display.insert(tk.END, "No character data available")
                stats_display.config(state="disabled")
                available_points_label.config(text="Available Stat Points: 0")
                return {
                    'success': False,
                    'error': 'No player data provided',
                    'message': 'No player character data'
                }
            
            player = character_data['player']
            
            # Update available points label
            available_points = 0
            if hasattr(player, 'leveling_manager'):
                try:
                    available_points = player.leveling_manager.calculate_stat_points_available(player)
                except Exception:
                    available_points = 0
            
            available_points_label.config(text=f"Available Stat Points: {available_points}")
            
            # Update stats display
            stats_display.config(state="normal")
            stats_display.delete(1.0, tk.END)
            
            # Build comprehensive stats text
            stats_text = f"=== CHARACTER STATS - {getattr(player, 'name', 'Unknown')} ===\n"
            stats_text += f"Level: {getattr(player, 'level', 1)}\n"
            stats_text += f"Available Points: {available_points}\n\n"
            
            # Show all stats in organized categories (same as character display)
            stats_text += "=== CORE ATTRIBUTES ===\n"
            
            # Primary stats that should always be shown
            primary_stats = [
                'strength', 'dexterity', 'intelligence', 'wisdom', 'constitution',
                'vitality', 'agility',  'luck', 'focus'
            ]
            
            for stat in primary_stats:
                try:
                    if hasattr(player, 'get_stat'):
                        effective_val = player.get_stat(stat)
                        base_val = player.base_stats.get(stat, 0) if hasattr(player, 'base_stats') else 0
                        if effective_val != base_val:
                            stats_text += f"  {stat.replace('_', ' ').title()}: {effective_val:.1f}\n"
                        else:
                            stats_text += f"  {stat.replace('_', ' ').title()}: {effective_val:.1f}\n"
                    else:
                        base_val = player.base_stats.get(stat, 0) if hasattr(player, 'base_stats') else 0
                        stats_text += f"  {stat.replace('_', ' ').title()}: {base_val}\n"
                except Exception:
                    stats_text += f"  {stat.replace('_', ' ').title()}: N/A\n"
            
            # Combat stats
            stats_text += "\n=== COMBAT STATS ===\n"
            combat_stats = [
                'accuracy', 'critical_chance', 'speed',
                'defense', 'magic_resistance', 'dodge_chance', 'parry_chance', 'block_chance'
            ]
            
            for stat in combat_stats:
                try:
                    if hasattr(player, 'get_stat'):
                        effective_val = player.get_stat(stat)
                        base_val = player.base_stats.get(stat, 0) if hasattr(player, 'base_stats') else 0
                        if effective_val != base_val:
                            stats_text += f"  {stat.replace('_', ' ').title()}: {effective_val:.1f}\n"
                        else:
                            stats_text += f"  {stat.replace('_', ' ').title()}: {effective_val:.1f}\n"
                    else:
                        base_val = player.base_stats.get(stat, 0) if hasattr(player, 'base_stats') else 0
                        stats_text += f"  {stat.replace('_', ' ').title()}: {base_val}\n"
                except Exception:
                    stats_text += f"  {stat.replace('_', ' ').title()}: N/A\n"
            
            # Derived stats
            stats_text += "\n=== DERIVED STATS ===\n"
            derived_stats = [
                'max_health', 'max_mana', 'max_stamina', 'health_regen', 'mana_regen', 'stamina_regen',
                'magic_power', 'initiative', 'speed', 'carrying_capacity'
            ]
            
            for stat in derived_stats:
                try:
                    if hasattr(player, 'get_stat'):
                        effective_val = player.get_stat(stat)
                        base_val = player.base_stats.get(stat, 0) if hasattr(player, 'base_stats') else 0
                        if effective_val != base_val:
                            stats_text += f"  {stat.replace('_', ' ').title()}: {effective_val:.1f}\n"
                        else:
                            stats_text += f"  {stat.replace('_', ' ').title()}: {effective_val:.1f}\n"
                    else:
                        base_val = player.base_stats.get(stat, 0) if hasattr(player, 'base_stats') else 0
                        stats_text += f"  {stat.replace('_', ' ').title()}: {base_val}\n"
                except Exception:
                    stats_text += f"  {stat.replace('_', ' ').title()}: N/A\n"
            
            stats_display.insert(tk.END, stats_text)
            stats_display.config(state="disabled")
            
            self.logger.debug("Leveling display updated via UI service")
            return {
                'success': True,
                'message': 'Leveling display updated successfully'
            }
            
        except Exception as e:
            self.logger.error(f"Failed to update leveling display: {e}")
            return {
                'success': False,
                'error': str(e),
                'message': 'Leveling display update failed'
            }

    def update_progression_display(self, character_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update progression display with character advancement information.
        
        Args:
            character_data: Dictionary containing character information
            
        Returns:
            Update operation result
        """
        try:
            if 'progression_display' not in self.widgets:
                return {
                    'success': False,
                    'error': 'Missing progression display widget',
                    'message': 'Progression display widget not found'
                }
                
            progression_display = self.widgets['progression_display']
            progression_display.config(state="normal")
            progression_display.delete(1.0, tk.END)
            
            # Get player from character data
            if 'player' not in character_data or not character_data['player']:
                progression_display.insert(tk.END, "No character data available")
                progression_display.config(state="disabled")
                return {
                    'success': False,
                    'error': 'No player data provided',
                    'message': 'No player character data'
                }
            
            player = character_data['player']
            
            # Build progression info text
            progression_text = f"=== CHARACTER PROGRESSION - {getattr(player, 'name', 'Unknown')} ===\n\n"
            
            # Level information
            progression_text += f"Current Level: {getattr(player, 'level', 1)}\n"
            if hasattr(player, 'experience'):
                progression_text += f"Experience: {player.experience}\n"
            if hasattr(player, 'next_level_xp'):
                progression_text += f"Next Level XP: {player.next_level_xp}\n"
                
            progression_text += "\n=== GROWTH SUMMARY ===\n"
            
            # Show total stat points allocated
            if hasattr(player, 'base_stats') and isinstance(player.base_stats, dict):
                total_allocated = sum(v for v in player.base_stats.values() if isinstance(v, (int, float)))
                progression_text += f"Total Stat Points Allocated: {total_allocated:.1f}\n"
                
            # Show equipment count
            equipment_count = 0
            equipment_slots = ['weapon', 'offhand', 'equipped_body', 'equipped_helmet', 'equipped_feet', 'equipped_ring']
            for slot in equipment_slots:
                if getattr(player, slot, None):
                    equipment_count += 1
            progression_text += f"Equipment Slots Filled: {equipment_count}/6\n"
            
            progression_text += "\n=== PROGRESSION GOALS ===\n"
            progression_text += "• Reach next level\n"
            progression_text += "• Allocate available stat points\n"
            progression_text += "• Acquire better equipment\n"
            progression_text += "• Learn new enchantments\n"
            
            progression_display.insert(tk.END, progression_text)
            progression_display.config(state="disabled")
            
            self.logger.debug("Progression display updated via UI service")
            return {
                'success': True,
                'message': 'Progression display updated successfully'
            }
            
        except Exception as e:
            self.logger.error(f"Failed to update progression display: {e}")
            return {
                'success': False,
                'error': str(e),
                'message': 'Progression display update failed'
            }

    def setup_all_tabs(self) -> Dict[str, Any]:
        """
        Set up all UI tabs using the service methods.
        
        Returns:
            Dictionary with setup results
        """
        results = []
        
        try:
            # Set up all tabs
            tab_methods = [
                ('stats', self.setup_stats_tab),
                ('combat', self.setup_combat_tab),
                ('inventory', self.setup_inventory_tab),
                ('leveling', self.setup_leveling_tab),
                ('enchanting', self.setup_enchanting_tab),
                ('progression', self.setup_progression_tab),
                ('combo', self.setup_combo_tab),
                ('settings', self.setup_settings_tab)
            ]
            
            for tab_name, tab_method in tab_methods:
                try:
                    result = tab_method()
                    results.append((tab_name, result))
                    if not result.get('success', False):
                        self.logger.warning(f"Failed to set up {tab_name} tab: {result.get('error', 'Unknown error')}")
                except Exception as e:
                    self.logger.error(f"Exception setting up {tab_name} tab: {e}")
                    results.append((tab_name, {'success': False, 'error': str(e)}))
            
            # Count successful setups
            successful_tabs = sum(1 for _, result in results if result.get('success', False))
            total_tabs = len(tab_methods)
            
            self.logger.info(f"Tab setup completed: {successful_tabs}/{total_tabs} tabs successful")
            
            return {
                'success': successful_tabs > 0,
                'message': f'Tab setup completed: {successful_tabs}/{total_tabs} tabs successful',
                'results': results,
                'successful_count': successful_tabs,
                'total_count': total_tabs
            }
            
        except Exception as e:
            self.logger.error(f"Tab setup failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'message': 'Tab setup failed',
                'results': results
            }

    def update_equipment_slots(self, player) -> Dict[str, Any]:
        """
        Update equipment slot displays with current equipment.
        
        Args:
            player: Player character object with equipment
            
        Returns:
            Update operation result
        """
        try:
            if not player:
                return {
                    'success': False,
                    'error': 'No player provided',
                    'message': 'No player character available'
                }
            
            # Update equipment slot displays
            equipment_slots = [
                ('slot_equipped_helmet_label', 'equipped_helmet', 'Helmet'),
                ('slot_equipped_cloak_label', 'equipped_cloak', 'Cloak'),
                ('slot_equipped_body_label', 'equipped_body', 'Armor'),
                ('slot_weapon_label', 'weapon', 'Weapon'),
                ('slot_offhand_label', 'offhand', 'Offhand'),
                ('slot_equipped_feet_label', 'equipped_feet', 'Boots'),
                ('slot_equipped_ring_label', 'equipped_ring', 'Ring'),
            ]
            
            updated_slots = 0
            for slot_label_attr, item_attr, display_name in equipment_slots:
                if slot_label_attr in self.widgets:
                    slot_label = self.widgets[slot_label_attr]
                    equipped_item = getattr(player, item_attr, None)
                    
                    if equipped_item:
                        item_name = getattr(equipped_item, 'name', 'Unknown Item')
                        # Truncate long names
                        if len(item_name) > 12:
                            item_name = item_name[:9] + "..."
                        slot_label.config(text=item_name, fg="lightgreen")
                    else:
                        slot_label.config(text="(Empty)", fg="gray")
                    
                    updated_slots += 1
            
            self.logger.debug(f"Updated {updated_slots} equipment slots")
            return {
                'success': True,
                'message': f'Updated {updated_slots} equipment slots',
                'updated_count': updated_slots
            }
            
        except Exception as e:
            self.logger.error(f"Failed to update equipment slots: {e}")
            return {
                'success': False,
                'error': str(e),
                'message': 'Failed to update equipment slots'
            }

    def destroy(self) -> None:
        """Clean up and destroy the UI."""
        if self.root:
            self.logger.info("Destroying UI")
            self.root.destroy()
            self.root = None
