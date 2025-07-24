"""
Enhanced Character Creation UI Service for RPG Game
Provides a modern, user-friendly interface with dashboard on the right side
"""

import tkinter as tk
from tkinter import ttk
from typing import Dict, Callable, Any, Optional
from game_sys.logging import get_logger
from game_sys.character.leveling_manager import LevelingManager

logger = get_logger(__name__)


class CharacterCreationUI:
    """Service class for managing character creation interface."""
    
    def __init__(self, parent: tk.Widget, callbacks: Dict[str, Callable]):
        """
        Initialize the Character Creation UI service.
        
        Args:
            parent: Parent widget to contain this UI
            callbacks: Dictionary of callback functions for UI events
        """
        self.parent = parent
        self.callbacks = callbacks
        self.main_frame = None
        self.left_frame = None
        self.right_frame = None
        self.scrollable_frame = None
        
        # UI Components
        self.template_combo = None
        self.name_entry = None
        self.character_display = None
        self.template_info = None
        self.status_label = None
        self.visual_display = None
        self.template_details_display = None
        self.info_notebook = None
        
    def _trigger_callback(self, callback_name: str, *args):
        """Safely trigger a callback if it exists and return the result."""
        if callback_name in self.callbacks:
            try:
                return self.callbacks[callback_name](*args)
            except Exception as e:
                logger.error(f"Error in callback {callback_name}: {e}")
                return None
        return None
    
    def create_interface(self, template_options: list, template_var: tk.StringVar, name_var: tk.StringVar) -> Dict[str, Any]:
        """
        Create the complete character creation interface with dashboard on the right.
        
        Args:
            template_options: List of available templates
            template_var: StringVar for template selection
            name_var: StringVar for character name
            
        Returns:
            Dictionary with status and component references
        """
        try:
            # Create main horizontal layout frame
            self.main_frame = tk.Frame(self.parent, bg="#2c3e50")
            self.main_frame.pack(fill=tk.BOTH, expand=True)
            
            # LEFT SIDE: Character Creation Controls (60% width)
            self.left_frame = tk.Frame(self.main_frame, bg="#2c3e50")
            self.left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(10, 5))
            
            # RIGHT SIDE: Character Dashboard (35% width - narrower to give more space to left)
            self.right_frame = tk.Frame(self.main_frame, bg="#34495e")
            self.right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=False, padx=(5, 10))
            self.right_frame.configure(width=420)  # Reduced width for dashboard
            
            # Create left side content
            self._create_character_creation_section(template_options, template_var, name_var)
            
            # Create right side dashboard
            self._create_character_dashboard()
            
            return {
                'status': 'success',
                'main_frame': self.main_frame,
                'message': 'Character creation interface created successfully'
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e),
                'message': 'Failed to create character creation interface'
            }
    
    def _create_character_creation_section(self, template_options: list, template_var: tk.StringVar, name_var: tk.StringVar) -> None:
        """Create the character creation section on the left side."""
        # Create scrollable canvas for the left side
        canvas = tk.Canvas(self.left_frame, bg="#2c3e50", highlightthickness=0)
        scrollbar = tk.Scrollbar(self.left_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg="#2c3e50")
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Pack canvas and scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Bind mousewheel to canvas
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind_all("<MouseWheel>", _on_mousewheel)

        # Store scrollable frame reference
        self.scrollable_frame = scrollable_frame

        # Main creation frame
        main_frame = tk.LabelFrame(
            scrollable_frame,
            text="🎭 Character Creation",
            font=("Arial", 14, "bold"),
            fg="gold",
            bg="#2c3e50",
            bd=2,
            relief=tk.GROOVE
        )
        main_frame.pack(fill=tk.X, padx=12, pady=12)

        # Template selection section
        template_frame = tk.Frame(main_frame, bg="#2c3e50")
        template_frame.pack(fill=tk.X, padx=15, pady=12)

        tk.Label(
            template_frame,
            text="💡 Select Template:",
            font=("Arial", 12, "bold"),
            fg="#3498db",
            bg="#2c3e50"
        ).pack(anchor=tk.W, pady=(0, 8))

        # Template combo and status in horizontal layout
        combo_row = tk.Frame(template_frame, bg="#2c3e50")
        combo_row.pack(fill=tk.X, pady=(0, 15))

        self.template_combo = ttk.Combobox(
            combo_row,
            textvariable=template_var,
            values=template_options,
            state="readonly",
            font=("Arial", 11),
            width=25
        )
        self.template_combo.pack(side=tk.LEFT, padx=(0, 15))
        self.template_combo.bind('<<ComboboxSelected>>', 
                                lambda e: self._trigger_callback('template_selected', e))

        self.status_label = tk.Label(
            combo_row,
            text="🔄 Select template to begin",
            font=("Arial", 10),
            fg="#f39c12",
            bg="#2c3e50",
            wraplength=300
        )
        self.status_label.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # Character Name Section (moved up)
        name_frame = tk.Frame(template_frame, bg="#2c3e50")
        name_frame.pack(fill=tk.X, pady=(0, 15))

        tk.Label(
            name_frame,
            text="🏷️ Character Name:",
            font=("Arial", 12, "bold"),
            fg="white",
            bg="#2c3e50"
        ).pack(anchor=tk.W, pady=(0, 5))

        self.name_entry = tk.Entry(
            name_frame,
            textvariable=name_var,
            font=("Arial", 11),
            bg="#34495e",
            fg="white",
            insertbackground="white",
            relief=tk.SUNKEN,
            bd=2
        )
        self.name_entry.pack(fill=tk.X)

        # Combined Character Information Section (template info + character stats)
        info_frame = tk.Frame(main_frame, bg="#2c3e50")
        info_frame.pack(fill=tk.X, padx=15, pady=(0, 15))

        tk.Label(
            info_frame,
            text="📋 Character Statistics",
            font=("Arial", 12, "bold"),
            fg="#3498db",
            bg="#2c3e50"
        ).pack(anchor=tk.W, pady=(0, 10))

        # Create a combined text display for comprehensive character information
        self.combined_display = tk.Text(
            info_frame,
            height=25,  # Increased height for comprehensive display
            font=("Consolas", 9),
            bg="#34495e",
            fg="#bdc3c7",
            state=tk.DISABLED,
            wrap=tk.WORD,
            relief=tk.SUNKEN,
            bd=2
        )
        self.combined_display.pack(fill=tk.BOTH, expand=True, pady=(0, 15))

        # Keep the old template_info and character_display for backward compatibility
        # but hide them - they'll be replaced by combined_display
        self.template_info = tk.Text(info_frame, height=0)
        self.template_info.pack_forget()
        
        self.character_display = tk.Text(info_frame, height=0)
        self.character_display.pack_forget()

        # Stat allocation section (moved to info_frame for better layout)
        stat_frame = tk.Frame(info_frame, bg="#2c3e50")
        stat_frame.pack(fill=tk.X, pady=(0, 15))

        # Available points display
        self.points_label = tk.Label(
            stat_frame,
            text="📊 Available Stat Points: 0",
            font=("Arial", 11, "bold"),
            fg="#f39c12",
            bg="#2c3e50"
        )
        self.points_label.pack(anchor=tk.W, pady=(0, 10))

        # Stat allocation controls
        stats_grid = tk.Frame(stat_frame, bg="#2c3e50")
        stats_grid.pack(fill=tk.X)

        # Create stat allocation buttons in a 2-column grid
        stats = [
            ("Strength", "strength"),
            ("Intelligence", "intelligence"),
            ("Dexterity", "dexterity"),
            ("Constitution", "constitution"),
            ("Wisdom", "wisdom"),
            ("Luck", "luck"),
            ("Agility", "agility"),
            ("Vitality", "vitality"),
            ("Charisma", "charisma"),
        ]

        self.stat_buttons = {}
        for i, (display_name, stat_name) in enumerate(stats):
            row = i // 2
            col = i % 2
            
            stat_row = tk.Frame(stats_grid, bg="#2c3e50")
            stat_row.grid(row=row, column=col, padx=10, pady=2, sticky="ew")
            
            # Configure grid weights
            stats_grid.grid_columnconfigure(0, weight=1)
            stats_grid.grid_columnconfigure(1, weight=1)
            
            # Stat label
            stat_label = tk.Label(
                stat_row,
                text=f"{display_name}:",
                font=("Arial", 10),
                fg="white",
                bg="#2c3e50",
                width=12,
                anchor="w"
            )
            stat_label.pack(side=tk.LEFT)
            
            # Current value display - starts at 0, will be updated when character is created
            value_label = tk.Label(
                stat_row,
                text="0",  # Initialize with 0, will be updated by update_stat_labels()
                font=("Arial", 10, "bold"),
                fg="#3498db",
                bg="#2c3e50",
                width=3
            )
            value_label.pack(side=tk.LEFT, padx=(5, 10))
            
            # Add point button
            add_btn = tk.Button(
                stat_row,
                text="+",
                font=("Arial", 9, "bold"),
                bg="#27ae60",
                fg="white",
                command=lambda s=stat_name: self._trigger_callback('stat_allocated', s),
                width=2,
                height=1
            )
            add_btn.pack(side=tk.LEFT, padx=2)
            
            # Store references
            self.stat_buttons[stat_name] = {
                'value_label': value_label,
                'add_button': add_btn
            }

        # Action buttons
        button_frame = tk.Frame(main_frame, bg="#2c3e50")
        button_frame.pack(fill=tk.X, padx=15, pady=15)

        buttons = [
            ("🎲 Generate Character", 'preview_character', "#3498db"),
            ("💾 Save Character", 'save_character', "#27ae60"),
            ("📂 Load Character", 'load_character', "#8e44ad"),
            ("🔄 Reset All", 'reset_stats', "#e74c3c")
        ]

        for i, (text, callback, color) in enumerate(buttons):
            btn = tk.Button(
                button_frame,
                text=text,
                font=("Arial", 11, "bold"),
                bg=color,
                fg="white",
                command=lambda c=callback: self._trigger_callback(c),
                relief=tk.RAISED,
                bd=2,
                height=2
            )
            btn.pack(fill=tk.X, pady=5)

    def _create_character_dashboard(self) -> None:
        """Create the character dashboard on the right side."""
        # Dashboard title
        dashboard_title = tk.Label(
            self.right_frame,
            text="🎯 CHARACTER DASHBOARD",
            font=("Arial", 16, "bold"),
            fg="orange",
            bg="#34495e"
        )
        dashboard_title.pack(pady=(15, 20))

        # Create notebook for tabbed content
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('TNotebook', background='#34495e')
        style.configure('TNotebook.Tab', background='#2c3e50', foreground='white', padding=[15, 8])
        style.map('TNotebook.Tab', background=[('selected', '#3498db')])

        self.info_notebook = ttk.Notebook(self.right_frame)
        self.info_notebook.pack(fill=tk.BOTH, expand=True, padx=15, pady=(0, 15))

        # Tab 1: Character Preview
        self._create_preview_tab()
        
        # Tab 2: Template Details
        self._create_template_tab()
        
        # Tab 3: Help & Tips
        self._create_help_tab()

        # Tab 4: Admin Panel (initially hidden)
        self._create_admin_tab()
        
        # Store reference to admin tab for show/hide
        self.admin_tab_index = 3

    def _create_preview_tab(self) -> None:
        """Create the character preview tab."""
        preview_frame = tk.Frame(self.info_notebook, bg="#34495e")
        self.info_notebook.add(preview_frame, text="🎨 PREVIEW")

        # Visual preview section
        preview_section = tk.Frame(preview_frame, bg="#34495e")
        preview_section.pack(fill=tk.X, padx=15, pady=15)

        tk.Label(
            preview_section,
            text="🎭 Character Visual",
            font=("Arial", 13, "bold"),
            fg="white",
            bg="#34495e"
        ).pack(pady=(0, 10))

        self.visual_display = tk.Label(
            preview_section,
            text="⚔️\n👤\n🛡️\n\n• Select template\n• Generate character\n• Allocate stats\n• Create & save!",
            font=("Arial", 11),
            fg="#bdc3c7",
            bg="#2c3e50",
            justify=tk.CENTER,
            relief=tk.SUNKEN,
            bd=3,
            height=8,
            pady=15
        )
        self.visual_display.pack(fill=tk.X, pady=(0, 15))

        # Quick action buttons
        tk.Label(
            preview_section,
            text="⚡ Quick Actions",
            font=("Arial", 13, "bold"),
            fg="white",
            bg="#34495e"
        ).pack(pady=(0, 10))

        quick_buttons = [
            ("🎲 Generate New", 'preview_character', "#3498db"),
            ("💾 Save Character", 'save_character', "#27ae60"),
            ("📂 Load Character", 'load_character', "#8e44ad"),
        ]

        for text, callback, color in quick_buttons:
            tk.Button(
                preview_section,
                text=text,
                font=("Arial", 10, "bold"),
                bg=color,
                fg="white",
                command=lambda c=callback: self._trigger_callback(c),
                relief=tk.RAISED,
                bd=2,
                height=2
            ).pack(fill=tk.X, pady=3)

    def _create_template_tab(self) -> None:
        """Create the template details tab."""
        template_frame = tk.Frame(self.info_notebook, bg="#34495e")
        self.info_notebook.add(template_frame, text="📋 TEMPLATE")

        tk.Label(
            template_frame,
            text="📋 Template Details",
            font=("Arial", 13, "bold"),
            fg="white",
            bg="#34495e"
        ).pack(pady=(15, 10))

        self.template_details_display = tk.Text(
            template_frame,
            font=("Consolas", 9),
            bg="#2c3e50",
            fg="#bdc3c7",
            height=16,
            wrap=tk.WORD,
            relief=tk.SUNKEN,
            bd=3,
            state=tk.DISABLED
        )
        self.template_details_display.pack(fill=tk.BOTH, expand=True, padx=15, pady=(0, 15))

        # Add admin controls section at the bottom
        admin_section = tk.Frame(template_frame, bg="#34495e")
        admin_section.pack(fill=tk.X, padx=15, pady=(0, 15))

        # Admin enable button
        self.admin_button = tk.Button(
            admin_section,
            text="🔧 Enable Admin Mode",
            font=("Arial", 10, "bold"),
            bg="#e74c3c",
            fg="white",
            command=lambda: self._trigger_callback('toggle_admin_mode'),
            relief=tk.RAISED,
            bd=2,
            height=1
        )
        self.admin_button.pack(fill=tk.X, pady=(5, 0))

    def _create_help_tab(self) -> None:
        """Create the help and tips tab."""
        help_frame = tk.Frame(self.info_notebook, bg="#34495e")
        self.info_notebook.add(help_frame, text="💡 GUIDE")

        tk.Label(
            help_frame,
            text="💡 Character Creation Guide",
            font=("Arial", 13, "bold"),
            fg="white",
            bg="#34495e"
        ).pack(pady=(15, 10))

        help_text = tk.Text(
            help_frame,
            font=("Arial", 10),
            bg="#2c3e50",
            fg="#bdc3c7",
            height=20,
            wrap=tk.WORD,
            relief=tk.SUNKEN,
            bd=3,
            state=tk.DISABLED
        )
        help_text.pack(fill=tk.BOTH, expand=True, padx=15, pady=(0, 15))

        # Add helpful content
        help_content = """🎯 CHARACTER CREATION GUIDE:

🔸 TEMPLATE SELECTION
   • Choose a template that matches your playstyle
   • Each template has unique stat distributions
   • Templates determine starting abilities and skills

🔸 STAT ALLOCATION  
   • Focus on 2-3 core stats for effectiveness
   • Balance offensive and defensive capabilities
   • Consider synergies between stats

🔸 CHARACTER GRADES & RARITY
   • Higher grades = superior base statistics
   • Rarity affects skill potency and equipment access
   • Legendary characters have unique abilities

🔸 SAVING & MANAGEMENT
   • Save promising characters to your library
   • Use descriptive names for organization
   • Characters can be loaded and modified later

🔸 ADMIN FEATURES
   • Toggle admin mode for unlimited options
   • Access advanced character modification
   • Test builds without restrictions

🔸 COMBAT TIPS
   • Consider equipment requirements
   • Plan skill combinations
   • Test different builds for versatility"""

        help_text.config(state=tk.NORMAL)
        help_text.insert(tk.END, help_content)
        help_text.config(state=tk.DISABLED)

    def _create_admin_tab(self) -> None:
        """Create the admin controls tab (initially hidden)."""
        admin_frame = tk.Frame(self.info_notebook, bg="#34495e")
        self.admin_tab = admin_frame  # Store reference
        
        # Don't add to notebook initially - will be added when admin mode is enabled
        
        tk.Label(
            admin_frame,
            text="🔧 Admin Controls",
            font=("Arial", 13, "bold"),
            fg="orange",
            bg="#34495e"
        ).pack(pady=(15, 10))

        # Admin controls scroll area
        admin_scroll_frame = tk.Frame(admin_frame, bg="#34495e")
        admin_scroll_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=(0, 15))

        # Character modification section
        char_mod_frame = tk.LabelFrame(
            admin_scroll_frame,
            text="🎭 Character Modification",
            font=("Arial", 11, "bold"),
            fg="#ecf0f1",
            bg="#34495e",
            bd=2
        )
        char_mod_frame.pack(fill=tk.X, pady=(0, 10))

        # Grade controls
        grade_frame = tk.Frame(char_mod_frame, bg="#34495e")
        grade_frame.pack(fill=tk.X, padx=10, pady=5)

        tk.Label(grade_frame, text="Grade:", bg="#34495e", fg="white", font=("Arial", 10)).pack(side=tk.LEFT, padx=(0, 5))
        
        grades = ["ONE", "TWO", "THREE", "FOUR", "FIVE", "SIX", "SEVEN"]
        self.grade_var = tk.StringVar(value="THREE")
        grade_combo = ttk.Combobox(
            grade_frame,
            textvariable=self.grade_var,
            values=grades,
            state="readonly",
            width=10,
            font=("Arial", 9)
        )
        grade_combo.pack(side=tk.LEFT, padx=(0, 5))
        
        tk.Button(
            grade_frame,
            text="Set Grade",
            command=lambda: self._trigger_callback('set_character_grade', self.grade_var.get()),
            bg="#9b59b6",
            fg="white",
            font=("Arial", 9),
            padx=8,
            pady=2
        ).pack(side=tk.LEFT, padx=5)

        # Rarity controls
        rarity_frame = tk.Frame(char_mod_frame, bg="#34495e")
        rarity_frame.pack(fill=tk.X, padx=10, pady=5)

        tk.Label(rarity_frame, text="Rarity:", bg="#34495e", fg="white", font=("Arial", 10)).pack(side=tk.LEFT, padx=(0, 5))
        
        rarities = ["COMMON", "UNCOMMON", "RARE", "EPIC", "LEGENDARY", "MYTHIC", "DIVINE"]
        self.rarity_var = tk.StringVar(value="COMMON")
        rarity_combo = ttk.Combobox(
            rarity_frame,
            textvariable=self.rarity_var,
            values=rarities,
            state="readonly",
            width=12,
            font=("Arial", 9)
        )
        rarity_combo.pack(side=tk.LEFT, padx=(0, 5))
        
        tk.Button(
            rarity_frame,
            text="Set Rarity",
            command=lambda: self._trigger_callback('set_character_rarity', self.rarity_var.get()),
            bg="#e67e22",
            fg="white",
            font=("Arial", 9),
            padx=8,
            pady=2
        ).pack(side=tk.LEFT, padx=5)

        # Stat modification section
        stat_mod_frame = tk.LabelFrame(
            admin_scroll_frame,
            text="📊 Stat Modification",
            font=("Arial", 11, "bold"),
            fg="#ecf0f1",
            bg="#34495e",
            bd=2
        )
        stat_mod_frame.pack(fill=tk.X, pady=(0, 10))

        # Add stat points button
        tk.Button(
            stat_mod_frame,
            text="➕ Add 10 Stat Points",
            command=lambda: self._trigger_callback('add_stat_points', 10),
            bg="#27ae60",
            fg="white",
            font=("Arial", 10, "bold"),
            padx=10,
            pady=5
        ).pack(fill=tk.X, padx=10, pady=5)

        # Infinite stat points toggle
        tk.Button(
            stat_mod_frame,
            text="♾️ Toggle Infinite Stat Points",
            command=lambda: self._trigger_callback('toggle_infinite_stat_points'),
            bg="#f39c12",
            fg="white",
            font=("Arial", 10, "bold"),
            padx=10,
            pady=5
        ).pack(fill=tk.X, padx=10, pady=5)

        # System controls section
        system_frame = tk.LabelFrame(
            admin_scroll_frame,
            text="⚙️ System Controls",
            font=("Arial", 11, "bold"),
            fg="#ecf0f1",
            bg="#34495e",
            bd=2
        )
        system_frame.pack(fill=tk.X, pady=(0, 10))

        tk.Button(
            system_frame,
            text="🔄 Reload Templates",
            command=lambda: self._trigger_callback('reload_templates'),
            bg="#3498db",
            fg="white",
            font=("Arial", 10),
            padx=10,
            pady=5
        ).pack(fill=tk.X, padx=10, pady=3)

        tk.Button(
            system_frame,
            text="🎯 Show Full Admin Panel",
            command=lambda: self._trigger_callback('show_admin_panel'),
            bg="#8e44ad",
            fg="white",
            font=("Arial", 10),
            padx=10,
            pady=5
        ).pack(fill=tk.X, padx=10, pady=3)

    def update_status(self, message: str, color: str = "#f39c12") -> None:
        """Update the status label."""
        if self.status_label:
            self.status_label.config(text=message, fg=color)
    
    def update_template_info(self, template_data: str) -> None:
        """Update template information display."""
        # For backward compatibility, but now we use combined display
        self._update_combined_display(template_data=template_data)
    
    def update_character_display(self, character_data: str) -> None:
        """Update character statistics display."""
        # For backward compatibility, but now we use combined display
        self._update_combined_display(character_data=character_data)
    
    def update_combined_display(self, template_data: str = None, character_data: str = None) -> None:
        """Update the combined template info and character stats display."""
        if hasattr(self, 'combined_display') and self.combined_display:
            self.combined_display.config(state=tk.NORMAL)
            self.combined_display.delete(1.0, tk.END)
            
            # Build combined content
            content = ""
            
            if template_data:
                content += "📋 TEMPLATE INFORMATION\n"
                content += "=" * 60 + "\n"
                content += template_data + "\n\n"
            
            if character_data:
                content += "📊 CHARACTER STATISTICS\n"
                content += "=" * 60 + "\n"
                content += character_data + "\n"
            
            if not template_data and not character_data:
                content = "🔄 Select a template and generate a character to view details..."
            
            self.combined_display.insert(tk.END, content)
            self.combined_display.config(state=tk.DISABLED)
    
    def _update_combined_display(self, template_data: str = None, character_data: str = None) -> None:
        """Internal method to update combined display with comprehensive character information."""
        if hasattr(self, 'combined_display') and self.combined_display:
            self.combined_display.config(state=tk.NORMAL)
            self.combined_display.delete(1.0, tk.END)
            
            try:
                content = ""
                
                # If character_data is provided, try to get comprehensive character info
                if character_data and "CHARACTER:" in character_data:
                    # This means we have a character to analyze comprehensively
                    try:
                        # Try to get the current character from the callback system
                        if 'get_current_character' in self.callbacks:
                            current_character = self._trigger_callback('get_current_character')
                            if current_character:
                                from game_sys.character.character_info_service import CharacterInfoService
                                char_info_service = CharacterInfoService()
                                comprehensive_display = char_info_service.format_character_display(current_character)
                                content = comprehensive_display
                            else:
                                content = character_data  # Fallback to provided character data
                        else:
                            content = character_data  # Fallback to provided character data
                    except Exception as e:
                        logger.warning(f"Error getting comprehensive character info: {e}")
                        content = character_data  # Fallback to provided character data
                
                elif template_data and character_data:
                    # Both template and character data provided
                    content += "📋 TEMPLATE INFORMATION\n"
                    content += "=" * 80 + "\n"
                    content += template_data + "\n\n"
                    
                    content += "⚔️ CHARACTER INFORMATION\n"
                    content += "=" * 80 + "\n"
                    content += character_data + "\n"
                
                elif template_data:
                    # Only template data
                    content += "📋 TEMPLATE INFORMATION\n"
                    content += "=" * 80 + "\n"
                    content += template_data + "\n"
                
                elif character_data:
                    # Only character data
                    content += "⚔️ CHARACTER INFORMATION\n"
                    content += "=" * 80 + "\n"
                    content += character_data + "\n"
                
                else:
                    content = "🔄 Select a template and generate a character to view comprehensive details..."
                
                self.combined_display.insert(tk.END, content)
                
            except Exception as e:
                error_content = f"❌ Error updating display: {e}\n\nPlease try regenerating your character."
                self.combined_display.insert(tk.END, error_content)
            
            finally:
                self.combined_display.config(state=tk.DISABLED)
    
    def update_visual_display(self, visual_data: str) -> None:
        """Update visual character display."""
        if self.visual_display:
            self.visual_display.config(text=visual_data)
    
    def update_template_details(self, details: str) -> None:
        """Update detailed template information in dashboard."""
        if self.template_details_display:
            self.template_details_display.config(state=tk.NORMAL)
            self.template_details_display.delete(1.0, tk.END)
            
            # Format the template details nicely
            if isinstance(details, dict):
                formatted_text = self._format_template_dict(details)
            else:
                formatted_text = str(details)
            
            self.template_details_display.insert(tk.END, formatted_text)
            self.template_details_display.config(state=tk.DISABLED)
    
    def _format_template_dict(self, template_dict: dict) -> str:
        """Format template dictionary for display with enhanced details."""
        lines = []
        
        # Template name and header
        if 'name' in template_dict:
            template_name = template_dict.get('display_name', template_dict['name'])
            lines.append(f"📋 TEMPLATE: {template_name.upper()}")
            lines.append("=" * 60)
        
        # Basic information section
        lines.append("🎭 BASIC INFORMATION")
        lines.append("─" * 30)
        
        template_type = template_dict.get('type', 'Unknown')
        job_id = template_dict.get('job_id', 'None')
        lines.append(f"🎪 Class Type: {template_type}")
        lines.append(f"💼 Job Role: {job_id}")
        
        if 'description' in template_dict:
            lines.append(f"� Description:")
            lines.append(f"   {template_dict['description']}")
            lines.append("")
        
        # Base stats with enhanced formatting
        if 'base_stats' in template_dict:
            lines.append("📊 Base Statistics:")
            stats = template_dict['base_stats']
            
            # Group stats by category for better display
            primary_stats = ['strength', 'dexterity', 'vitality', 'intelligence', 'wisdom', 'constitution']
            secondary_stats = ['luck', 'agility', 'charisma']
            
            # Display primary stats
            lines.append("   🔸 Primary Attributes:")
            for stat_name in primary_stats:
                if stat_name in stats:
                    stat_value = stats[stat_name]
                    emoji = self._get_stat_emoji(stat_name)
                    lines.append(f"     {emoji} {stat_name.capitalize():<12}: {round(stat_value)}")
            
            # Display secondary stats if available
            secondary_found = [stat for stat in secondary_stats if stat in stats]
            if secondary_found:
                lines.append("   🔸 Secondary Attributes:")
                for stat_name in secondary_found:
                    stat_value = stats[stat_name]
                    emoji = self._get_stat_emoji(stat_name)
                    lines.append(f"     {emoji} {stat_name.capitalize():<12}: {round(stat_value)}")
            
            lines.append("")
        
        # Starting equipment with better organization
        if 'starting_items' in template_dict:
            items = template_dict['starting_items']
            if items:
                lines.append("🎒 Starting Equipment:")
                
                # Categorize items if possible
                weapons = [item for item in items if any(weapon_type in item.lower() 
                          for weapon_type in ['sword', 'bow', 'staff', 'dagger', 'axe', 'mace', 'spear'])]
                armor = [item for item in items if any(armor_type in item.lower() 
                        for armor_type in ['helm', 'armor', 'shield', 'boots', 'gloves', 'robe'])]
                consumables = [item for item in items if any(consumable_type in item.lower() 
                              for consumable_type in ['potion', 'scroll', 'food', 'drink'])]
                other_items = [item for item in items if item not in weapons + armor + consumables]
                
                if weapons:
                    lines.append("   ⚔️  Weapons:")
                    for item in weapons:
                        lines.append(f"     • {item}")
                
                if armor:
                    lines.append("   🛡️  Armor & Protection:")
                    for item in armor:
                        lines.append(f"     • {item}")
                
                if consumables:
                    lines.append("   🧪 Consumables:")
                    for item in consumables:
                        lines.append(f"     • {item}")
                
                if other_items:
                    lines.append("   � Other Items:")
                    for item in other_items:
                        lines.append(f"     • {item}")
                
                lines.append("")
        
        # Special abilities with enhanced formatting
        if 'abilities' in template_dict:
            abilities = template_dict['abilities']
            if abilities:
                lines.append("⚡ Special Abilities & Skills:")
                for ability in abilities:
                    lines.append(f"   🔹 {ability}")
                lines.append("")
        
        # Advanced template information
        base_stats = template_dict.get('base_stats', {})
        
        # Combat role analysis
        if base_stats:
            lines.append("🎯 COMBAT ROLE ANALYSIS")
            lines.append("─" * 30)
            combat_roles = self._analyze_combat_roles(base_stats)
            for role in combat_roles:
                lines.append(f"   🔹 {role}")
            lines.append("")
        
        # Build recommendations based on stats
        if base_stats:
            lines.append("📈 BUILD RECOMMENDATIONS")
            lines.append("─" * 30)
            recommendations = self._generate_build_recommendations(base_stats)
            for category, rec_list in recommendations.items():
                if rec_list:
                    lines.append(f"   {category}:")
                    for rec in rec_list:
                        lines.append(f"     • {rec}")
            lines.append("")
        
        # Enhanced gameplay tips
        gameplay_tips = self._get_enhanced_template_tips(template_dict)
        if gameplay_tips:
            lines.append("💡 GAMEPLAY STRATEGY")
            lines.append("─" * 30)
            for category, tips in gameplay_tips.items():
                if tips:
                    lines.append(f"   🔸 {category}:")
                    for tip in tips:
                        lines.append(f"     • {tip}")
            lines.append("")
        
        # Grade and rarity information
        if 'grade_range' in template_dict:
            lines.append("� TEMPLATE GRADES")
            lines.append("─" * 30)
            lines.append(f"   Grade Range: {template_dict['grade_range']}")
            lines.append("")
        
        if 'rarity_weights' in template_dict:
            lines.append("💎 RARITY DISTRIBUTION")
            lines.append("─" * 30)
            weights = template_dict['rarity_weights']
            for rarity, weight in weights.items():
                lines.append(f"   • {rarity}: {weight}% chance")
            lines.append("")
        
        # Final recommendations summary
        lines.append("🌟 QUICK SUMMARY")
        lines.append("─" * 30)
        
        job_id = template_dict.get('job_id', 'Unknown')
        template_name = template_dict.get('display_name', template_dict.get('name', 'Unknown'))
        
        lines.append(f"   Perfect for players who enjoy {job_id.lower()} gameplay!")
        
        if base_stats:
            primary_stat = max(base_stats.items(), key=lambda x: x[1])[0]
            lines.append(f"   Focus on {primary_stat.capitalize()} for optimal performance")
        
        lines.append(f"   {template_name} offers a balanced mix of combat and utility")
        
        return "\n".join(lines)
    
    def _generate_build_recommendations(self, stats: dict) -> dict:
        """Generate categorized build recommendations."""
        recommendations = {
            "Primary Focus": [],
            "Secondary Stats": [],
            "Playstyle Tips": []
        }
        
        if not stats:
            return recommendations
        
        # Sort stats to identify priorities
        sorted_stats = sorted(stats.items(), key=lambda x: x[1], reverse=True)
        
        # Primary focus based on highest stat
        if sorted_stats:
            primary_stat, primary_value = sorted_stats[0]
            
            if primary_stat == 'strength':
                recommendations["Primary Focus"].append("Melee combat specialist - prioritize weapon mastery")
                recommendations["Secondary Stats"].append("Constitution for survivability, Dexterity for accuracy")
                recommendations["Playstyle Tips"].append("Get close to enemies and deal heavy physical damage")
                
            elif primary_stat == 'intelligence':
                recommendations["Primary Focus"].append("Magical damage dealer - focus on spell power")
                recommendations["Secondary Stats"].append("Wisdom for mana pool, Constitution for survivability")
                recommendations["Playstyle Tips"].append("Use spells from range, exploit elemental weaknesses")
                
            elif primary_stat == 'dexterity':
                recommendations["Primary Focus"].append("Precision striker - emphasize critical hits")
                recommendations["Secondary Stats"].append("Agility for evasion, Strength for damage")
                recommendations["Playstyle Tips"].append("Hit-and-run tactics, exploit positioning advantages")
                
            elif primary_stat == 'wisdom':
                recommendations["Primary Focus"].append("Support/healer - focus on utility magic")
                recommendations["Secondary Stats"].append("Intelligence for versatility, Constitution for durability")
                recommendations["Playstyle Tips"].append("Support team with healing and buffs")
                
            elif primary_stat == 'constitution':
                recommendations["Primary Focus"].append("Tank/defender - maximize damage absorption")
                recommendations["Secondary Stats"].append("Strength for counter-attacks, Wisdom for resistance")
                recommendations["Playstyle Tips"].append("Draw enemy attention, protect weaker allies")
        
        # Add general recommendations based on stat balance
        total_stats = sum(stats.values())
        if total_stats > 50:  # High stat total
            recommendations["Playstyle Tips"].append("Versatile build - can adapt to various situations")
        
        return recommendations
    
    def update_stat_labels(self, stats: dict = None) -> None:
        """Update stat label display."""
        if not hasattr(self, 'stat_buttons') or not self.stat_buttons:
            return
            
        if stats:
            logger.debug(f"STAT UPDATE: Received stats data: {stats}")
            for stat_name, stat_data in stats.items():
                if stat_name in self.stat_buttons:
                    # Update the value display
                    current_value = stat_data.get('current_value', 0)
                    value_label = self.stat_buttons[stat_name]['value_label']
                    
                    logger.debug(f"STAT UPDATE: Setting {stat_name} label to {current_value}")
                    old_text = value_label.cget('text')
                    logger.debug(f"STAT UPDATE: {stat_name} old text: '{old_text}', new text: '{current_value}'")
                    
                    # Destroy and recreate the label to force visual update
                    parent = value_label.master
                    pack_info = value_label.pack_info()
                    value_label.destroy()
                    
                    # Create new label with updated text
                    new_label = tk.Label(
                        parent,
                        text=str(current_value),
                        font=("Arial", 10, "bold"),
                        fg="#3498db",
                        bg="#2c3e50",
                        width=3
                    )
                    new_label.pack(**pack_info)
                    
                    # Update our reference
                    self.stat_buttons[stat_name]['value_label'] = new_label
                    
                    new_text = new_label.cget('text')
                    logger.debug(f"STAT UPDATE: {stat_name} final text: '{new_text}'")
                    
                    # Update button state based on availability
                    can_allocate = stat_data.get('can_allocate', False)
                    btn_state = tk.NORMAL if can_allocate else tk.DISABLED
                    btn_color = "#27ae60" if can_allocate else "#95a5a6"
                    add_button = self.stat_buttons[stat_name]['add_button']
                    add_button.config(state=btn_state, bg=btn_color)
            
            # Force complete UI refresh using multiple methods
            self._force_ui_refresh()
                
        else:
            # Reset all stat displays
            for stat_name in self.stat_buttons:
                value_label = self.stat_buttons[stat_name]['value_label']
                add_button = self.stat_buttons[stat_name]['add_button']
                
                # Destroy and recreate for reset too
                parent = value_label.master
                pack_info = value_label.pack_info()
                value_label.destroy()
                
                new_label = tk.Label(
                    parent,
                    text="0",
                    font=("Arial", 10, "bold"),
                    fg="#3498db",
                    bg="#2c3e50",
                    width=3
                )
                new_label.pack(**pack_info)
                self.stat_buttons[stat_name]['value_label'] = new_label
                
                add_button.config(state=tk.DISABLED, bg="#95a5a6")
            
            # Force complete UI refresh
            self._force_ui_refresh()
    
    def _force_ui_refresh(self):
        """Force complete UI refresh using multiple approaches."""
        try:
            if hasattr(self, 'parent') and self.parent:
                self.parent.update_idletasks()
                self.parent.update()
                # Schedule another update for safety
                self.parent.after(1, lambda: self.parent.update_idletasks())
            if hasattr(self, 'main_frame') and self.main_frame:
                self.main_frame.update_idletasks()
                self.main_frame.update()
        except Exception as e:
            self.logger.error(f"UI refresh error: {e}")
    
    def update_points_display(self, available_points: int = 0, allocated_points: int = 0) -> None:
        """Update points display."""
        if hasattr(self, 'points_label') and self.points_label:
            self.points_label.config(text=f"📊 Available Stat Points: {available_points}")
            
            # Color based on availability
            if available_points > 0:
                self.points_label.config(fg="#27ae60")  # Green when points available
            else:
                self.points_label.config(fg="#f39c12")  # Orange when no points
    
    def clear_displays(self) -> None:
        """Clear all display areas."""
        # Clear combined display
        if hasattr(self, 'combined_display') and self.combined_display:
            self.combined_display.config(state=tk.NORMAL)
            self.combined_display.delete(1.0, tk.END)
            self.combined_display.insert(tk.END, "🔄 Select a template and generate a character to view details...")
            self.combined_display.config(state=tk.DISABLED)
        
        # Clear other displays
        self.update_visual_display("⚔️\n👤\n🛡️\n\n• Select template\n• Generate character\n• Create & save!")
        self.update_template_details("Select a template to view details...")
        self.update_stat_labels({})
        self.update_points_display(0, 0)
    
    def get_template_selection(self) -> str:
        """Get currently selected template."""
        return self.template_combo.get() if self.template_combo else ""
    
    def get_character_name(self) -> str:
        """Get current character name."""
        return self.name_entry.get() if self.name_entry else ""
    
    def set_template_selection(self, template: str) -> None:
        """Set template selection."""
        if self.template_combo and template in self.template_combo['values']:
            self.template_combo.set(template)
    
    def update_admin_mode(self, admin_enabled: bool) -> None:
        """Update admin mode UI state."""
        if hasattr(self, 'admin_button') and self.admin_button:
            if admin_enabled:
                self.admin_button.config(
                    text="🔧 Admin Mode ON",
                    bg="#27ae60"
                )
                # Add admin tab if not already added
                if hasattr(self, 'admin_tab') and hasattr(self, 'info_notebook'):
                    try:
                        # Check if admin tab is already in notebook
                        tabs = [self.info_notebook.tab(i, "text") for i in range(self.info_notebook.index("end"))]
                        if "🔧 ADMIN" not in tabs:
                            self.info_notebook.add(self.admin_tab, text="🔧 ADMIN")
                    except:
                        pass
            else:
                self.admin_button.config(
                    text="🔧 Enable Admin Mode",
                    bg="#e74c3c"
                )
                # Remove admin tab if present
                if hasattr(self, 'admin_tab') and hasattr(self, 'info_notebook'):
                    try:
                        # Find and remove admin tab
                        for i in range(self.info_notebook.index("end")):
                            if self.info_notebook.tab(i, "text") == "🔧 ADMIN":
                                self.info_notebook.forget(i)
                                break
                    except:
                        pass
    
    def _get_stat_emoji(self, stat_name: str) -> str:
        """Get emoji for stat visualization."""
        emoji_map = {
            'strength': '💪',
            'dexterity': '🎯',
            'vitality': '❤️',
            'intelligence': '🧠',
            'wisdom': '🔮',
            'constitution': '🛡️',
            'luck': '🍀',
            'agility': '⚡',
            'charisma': '✨'
        }
        return emoji_map.get(stat_name.lower(), '📊')
    
    def _analyze_combat_roles(self, stats: dict) -> list:
        """Analyze potential combat roles based on stats."""
        roles = []
        
        if not stats:
            return ["⚖️ Balanced combatant - adaptable to various roles"]
        
        # Calculate role scores
        tank_score = stats.get('constitution', 0) + stats.get('vitality', 0)
        damage_score = stats.get('strength', 0) + stats.get('dexterity', 0)
        magic_score = stats.get('intelligence', 0) + stats.get('wisdom', 0)
        support_score = stats.get('wisdom', 0) + stats.get('charisma', 0)
        
        # Determine primary roles
        scores = {
            'Tank/Defender': tank_score,
            'Physical Damage Dealer': damage_score,
            'Magical Damage Dealer': magic_score,
            'Support/Healer': support_score
        }
        
        # Sort by score and add top roles
        sorted_roles = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        
        for role, score in sorted_roles[:2]:  # Top 2 roles
            if score > 0:
                effectiveness = "Excellent" if score >= 20 else "Good" if score >= 15 else "Moderate"
                roles.append(f"{effectiveness} {role} (Score: {score})")
        
        if not roles:
            roles.append("⚖️ Versatile combatant - balanced across all roles")
        
        return roles
    
    def _get_enhanced_template_tips(self, template_data: dict) -> dict:
        """Get categorized gameplay tips for the template."""
        tips = {
            "Character Development": [],
            "Combat Strategy": [],
            "Equipment Focus": [],
            "Skill Progression": []
        }
        
        job_id = template_data.get('job_id', '').lower()
        base_stats = template_data.get('base_stats', {})
        starting_items = template_data.get('starting_items', [])
        
        # Job-specific development tips
        if 'warrior' in job_id or 'fighter' in job_id:
            tips["Character Development"].extend([
                "Prioritize Strength and Constitution for maximum effectiveness",
                "Consider Dexterity for weapon versatility and accuracy"
            ])
            tips["Combat Strategy"].extend([
                "Excel in melee combat - get close to enemies",
                "Use heavy armor to mitigate incoming damage",
                "Focus on weapon mastery and combat techniques"
            ])
            tips["Equipment Focus"].append("Heavy armor, shields, and melee weapons")
        
        elif 'mage' in job_id or 'wizard' in job_id:
            tips["Character Development"].extend([
                "Intelligence is your primary stat - max it first",
                "Wisdom helps with mana pool and spell resistance",
                "Don't neglect Constitution for survivability"
            ])
            tips["Combat Strategy"].extend([
                "Maintain distance from enemies - you're fragile",
                "Learn spell combinations for maximum effect",
                "Use elemental weaknesses to your advantage"
            ])
            tips["Equipment Focus"].append("Robes, staves, and magical accessories")
        
        elif 'rogue' in job_id or 'thief' in job_id:
            tips["Character Development"].extend([
                "Dexterity enables critical strikes and stealth",
                "Agility improves mobility and evasion",
                "Some Strength helps with weapon damage"
            ])
            tips["Combat Strategy"].extend([
                "Strike from stealth for bonus damage",
                "Use hit-and-run tactics to avoid retaliation",
                "Target enemy weak points and vulnerabilities"
            ])
            tips["Equipment Focus"].append("Light armor for mobility, dual weapons")
        
        elif 'cleric' in job_id or 'priest' in job_id:
            tips["Character Development"].extend([
                "Wisdom enhances healing power and divine magic",
                "Constitution provides durability for front-line support",
                "Intelligence helps with spell versatility"
            ])
            tips["Combat Strategy"].extend([
                "Balance healing allies with offensive spells",
                "Position yourself to support the team effectively",
                "Use divine magic against undead and evil enemies"
            ])
            tips["Equipment Focus"].append("Medium armor, holy symbols, healing items")
        
        # Stat-based tips
        if base_stats:
            highest_stat = max(base_stats.items(), key=lambda x: x[1])[0]
            
            if highest_stat == 'strength':
                tips["Skill Progression"].append("Focus on weapon skills and physical combat abilities")
            elif highest_stat == 'intelligence':
                tips["Skill Progression"].append("Prioritize spell learning and magical research")
            elif highest_stat == 'dexterity':
                tips["Skill Progression"].append("Develop archery, stealth, and precision skills")
            elif highest_stat == 'wisdom':
                tips["Skill Progression"].append("Learn healing, divination, and support magic")
            elif highest_stat == 'constitution':
                tips["Skill Progression"].append("Focus on defensive abilities and endurance skills")
        
        # Equipment-based tips
        if any('staff' in item.lower() for item in starting_items):
            tips["Combat Strategy"].append("Staves enhance magical abilities and can be used for melee")
        
        if any('bow' in item.lower() for item in starting_items):
            tips["Combat Strategy"].append("Maintain range advantage and use terrain wisely")
        
        if any('sword' in item.lower() for item in starting_items):
            tips["Combat Strategy"].append("Versatile weapon - good for offense and defense")
        
        # Remove empty categories
        return {category: tips_list for category, tips_list in tips.items() if tips_list}
    
    def destroy(self) -> None:
        """Clean up UI components."""
        if self.main_frame:
            self.main_frame.destroy()
