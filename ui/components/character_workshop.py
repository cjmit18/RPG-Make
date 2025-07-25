"""
Character Workshop Component
===========================

A reusable character creation and management component.
Can be used in any application that needs character creation functionality.
"""

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from typing import Dict, Any, Optional, Callable, List, Protocol
from dataclasses import dataclass

from game_sys.logging import get_logger
from game_sys.character.character_creation_service import CharacterCreationService, CharacterCreationObserver


class CharacterWorkshopObserver:
    """Observer that automatically refreshes the workshop UI when events occur."""
    
    def __init__(self, workshop: 'CharacterWorkshop'):
        self.workshop = workshop
        self.logger = get_logger(f"{__name__}.WorkshopObserver")
        self._refreshing = False  # Flag to prevent recursive refreshes
    
    def _safe_refresh(self, refresh_func: Callable, event_name: str) -> None:
        """Safely execute a refresh function, preventing recursion."""
        if self._refreshing:
            self.logger.debug(f"Skipping {event_name} refresh - already refreshing")
            return
        
        try:
            self._refreshing = True
            refresh_func()
        except Exception as e:
            self.logger.error(f"Error during {event_name} refresh: {e}")
        finally:
            self._refreshing = False
    
    def on_character_created(self, character: Any) -> None:
        """Called when a character is created."""
        self.logger.debug("Character created event - refreshing workshop")
        self._safe_refresh(self.workshop._refresh_all_displays, "character_created")
    
    def on_stats_allocated(self, character: Any, stat_name: str, amount: int) -> None:
        """Called when stats are allocated."""
        self.logger.debug(f"Stats allocated event ({stat_name}: +{amount}) - refreshing displays")
        self._safe_refresh(self.workshop._refresh_stat_displays, "stats_allocated")
    
    def on_character_finalized(self, character: Any) -> None:
        """Called when character creation is finalized."""
        self.logger.debug("Character finalized event - refreshing workshop")
        self._safe_refresh(self.workshop._refresh_all_displays, "character_finalized")
    
    def on_character_saved(self, character: Any, save_name: str) -> None:
        """Called when a character is saved to library."""
        self.logger.debug(f"Character saved event ({save_name}) - refreshing workshop")
        self._safe_refresh(self.workshop._refresh_all_displays, "character_saved")
    
    def on_character_loaded(self, character: Any, save_name: str) -> None:
        """Called when a character is loaded from library."""
        self.logger.debug(f"Character loaded event ({save_name}) - refreshing workshop")
        def load_refresh():
            self.workshop._refresh_all_displays()
            # Also update template selection
            if hasattr(character, 'template_id') and character.template_id:
                self.workshop.template_var.set(character.template_id)
        self._safe_refresh(load_refresh, "character_loaded")
    
    def on_template_selected(self, template_id: str) -> None:
        """Called when a template is selected."""
        self.logger.debug(f"Template selected event ({template_id}) - refreshing template info")
        self._safe_refresh(self.workshop._refresh_template_display, "template_selected")
    
    def on_character_reset(self) -> None:
        """Called when character stats are reset."""
        self.logger.debug("Character reset event - refreshing workshop")
        self._safe_refresh(self.workshop._refresh_all_displays, "character_reset")


class CharacterWorkshopCallbacks(Protocol):
    """Protocol defining callbacks for character workshop events."""
    
    def on_character_created(self, character: Any) -> None:
        """Called when a character is successfully created."""
        ...
    
    def on_character_updated(self, character: Any) -> None:
        """Called when a character is updated."""
        ...
    
    def on_status_update(self, message: str, msg_type: str = "info") -> None:
        """Called to update status display."""
        ...


@dataclass
class WorkshopConfig:
    """Configuration for the character workshop."""
    show_preview: bool = True
    show_library_buttons: bool = True
    show_admin_buttons: bool = False
    auto_preview: bool = True
    compact_mode: bool = False


class CharacterWorkshop:
    """
    Reusable character workshop component.
    Provides character creation, editing, and management functionality.
    """
    
    def __init__(self, 
                 parent: tk.Widget, 
                 character_service: CharacterCreationService,
                 callbacks: Optional[CharacterWorkshopCallbacks] = None,
                 config: Optional[WorkshopConfig] = None):
        """Initialize the character workshop."""
        self.parent = parent
        self.character_service = character_service
        self.callbacks = callbacks
        self.config = config or WorkshopConfig()
        self.logger = get_logger(f"{__name__}.CharacterWorkshop")
        
        # UI components
        self.main_frame: Optional[tk.Frame] = None
        self.left_panel: Optional[tk.LabelFrame] = None
        self.right_panel: Optional[tk.LabelFrame] = None
        
        # Template selection
        self.template_frame: Optional[tk.Frame] = None
        self.template_var = tk.StringVar()
        self.template_combo: Optional[ttk.Combobox] = None
        
        # Character naming
        self.name_frame: Optional[tk.Frame] = None
        self.name_var = tk.StringVar()
        self.name_entry: Optional[tk.Entry] = None
        
        # Stat allocation
        self.stats_frame: Optional[tk.LabelFrame] = None
        self.stat_vars: Dict[str, tk.StringVar] = {}
        self.stat_buttons: Dict[str, tk.Button] = {}
        
        # Action buttons
        self.actions_frame: Optional[tk.Frame] = None
        
        # Character preview
        self.preview_text: Optional[tk.Text] = None
        
        # Auto-refresh observer
        self.workshop_observer: Optional[CharacterWorkshopObserver] = None
        
        # Initialize the interface
        self._create_interface()
        
        # Set up auto-refresh observer
        self._setup_auto_refresh()
    
    def _create_interface(self) -> None:
        """Create the workshop interface."""
        try:
            # Main container
            self.main_frame = tk.Frame(self.parent)
            self.main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
            
            if self.config.compact_mode:
                self._create_compact_layout()
            else:
                self._create_standard_layout()
            
            self._setup_template_selection()
            self._setup_character_naming()
            self._setup_stat_allocation()
            self._setup_action_buttons()
            
            if self.config.show_preview:
                self._setup_character_preview()
            
            self._load_initial_data()
            
            self.logger.info("Character workshop interface created")
            
        except Exception as e:
            self.logger.error(f"Failed to create workshop interface: {e}")
            raise
    
    def _create_standard_layout(self) -> None:
        """Create standard two-panel layout."""
        # Left panel for controls
        self.left_panel = tk.LabelFrame(self.main_frame, text="Character Creation")
        self.left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        # Right panel for preview (if enabled)
        if self.config.show_preview:
            self.right_panel = tk.LabelFrame(self.main_frame, text="Character Preview")
            self.right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))
    
    def _create_compact_layout(self) -> None:
        """Create compact single-panel layout."""
        self.left_panel = tk.Frame(self.main_frame)
        self.left_panel.pack(fill=tk.BOTH, expand=True)
    
    def _setup_template_selection(self) -> None:
        """Set up template selection interface."""
        self.template_frame = tk.LabelFrame(self.left_panel, text="Character Template")
        self.template_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Template selection
        tk.Label(self.template_frame, text="Template:").pack(anchor=tk.W, padx=5, pady=2)
        
        self.template_combo = ttk.Combobox(
            self.template_frame,
            textvariable=self.template_var,
            state="readonly",
            width=30
        )
        self.template_combo.pack(fill=tk.X, padx=5, pady=2)
        self.template_combo.bind("<<ComboboxSelected>>", self._on_template_selected)
    
    def _setup_character_naming(self) -> None:
        """Set up character naming interface."""
        self.name_frame = tk.Frame(self.template_frame)
        self.name_frame.pack(fill=tk.X, padx=5, pady=5)
        
        tk.Label(self.name_frame, text="Character Name:").pack(side=tk.LEFT)
        
        self.name_entry = tk.Entry(
            self.name_frame,
            textvariable=self.name_var,
            width=20
        )
        self.name_entry.pack(side=tk.RIGHT)
    
    def _setup_stat_allocation(self) -> None:
        """Set up stat allocation interface."""
        self.stats_frame = tk.LabelFrame(self.left_panel, text="Stat Allocation")
        self.stats_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Points display
        self.points_frame = tk.Frame(self.stats_frame)
        self.points_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.points_label = tk.Label(self.points_frame, text="Available Points: 0")
        self.points_label.pack(side=tk.LEFT)
        
        # Reset button
        tk.Button(
            self.points_frame,
            text="Reset Stats",
            command=self._reset_stats
        ).pack(side=tk.RIGHT)
        
        # Stat controls will be added dynamically
        self.stat_controls_frame = tk.Frame(self.stats_frame)
        self.stat_controls_frame.pack(fill=tk.X, padx=5, pady=5)
    
    def _setup_action_buttons(self) -> None:
        """Set up action buttons."""
        self.actions_frame = tk.Frame(self.left_panel)
        self.actions_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Main action buttons
        button_frame1 = tk.Frame(self.actions_frame)
        button_frame1.pack(fill=tk.X, pady=2)
        
        tk.Button(
            button_frame1,
            text="🎲 New Character",
            command=self._create_new_character,
            bg="#3498db",
            fg="white",
            font=("Arial", 10, "bold")
        ).pack(side=tk.LEFT, padx=2, fill=tk.X, expand=True)
        
        tk.Button(
            button_frame1,
            text="✅ Finalize",
            command=self._finalize_character,
            bg="#27ae60",
            fg="white",
            font=("Arial", 10, "bold")
        ).pack(side=tk.LEFT, padx=2, fill=tk.X, expand=True)
        
        # Library buttons (if enabled)
        if self.config.show_library_buttons:
            button_frame2 = tk.Frame(self.actions_frame)
            button_frame2.pack(fill=tk.X, pady=2)
            
            tk.Button(
                button_frame2,
                text="💾 Save",
                command=self._save_character
            ).pack(side=tk.LEFT, padx=2, fill=tk.X, expand=True)
            
            tk.Button(
                button_frame2,
                text="📂 Load",
                command=self._load_character
            ).pack(side=tk.LEFT, padx=2, fill=tk.X, expand=True)
            
            tk.Button(
                button_frame2,
                text="📋 Copy",
                command=self._copy_character
            ).pack(side=tk.LEFT, padx=2, fill=tk.X, expand=True)
        
        # Admin buttons (if enabled)
        if self.config.show_admin_buttons:
            button_frame3 = tk.Frame(self.actions_frame)
            button_frame3.pack(fill=tk.X, pady=2)
            
            tk.Button(
                button_frame3,
                text="⚙️ Admin Panel",
                command=self._open_admin_panel,
                bg="#e74c3c",
                fg="white",
                font=("Arial", 10, "bold")
            ).pack(side=tk.LEFT, padx=2, fill=tk.X, expand=True)
            
            tk.Button(
                button_frame3,
                text="🔧 Debug Info",
                command=self._show_debug_info,
                bg="#f39c12",
                fg="white"
            ).pack(side=tk.LEFT, padx=2, fill=tk.X, expand=True)
    
    def _setup_character_preview(self) -> None:
        """Set up character preview panel."""
        if not self.right_panel:
            return
        
        preview_frame = tk.Frame(self.right_panel)
        preview_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Preview text area
        self.preview_text = tk.Text(
            preview_frame,
            wrap=tk.WORD,
            state=tk.DISABLED,
            font=('Consolas', 10),
            height=30
        )
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(preview_frame, orient=tk.VERTICAL, command=self.preview_text.yview)
        self.preview_text.configure(yscrollcommand=scrollbar.set)
        
        self.preview_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Initialize with placeholder text
        self._update_preview("Select a template to begin character creation")
    
    def _load_initial_data(self) -> None:
        """Load initial data (templates, etc.)."""
        try:
            # Load available templates
            templates = list(self.character_service.get_available_templates().keys())
            self.template_combo['values'] = templates
            
            if templates:
                self.template_var.set(templates[0])
                self._on_template_selected()
            
        except Exception as e:
            self.logger.error(f"Failed to load initial data: {e}")
    
    def _create_stat_controls(self) -> None:
        """Create stat allocation controls dynamically."""
        # Clear existing controls
        for widget in self.stat_controls_frame.winfo_children():
            widget.destroy()
        
        self.stat_vars.clear()
        self.stat_buttons.clear()
        
        if not self.character_service.current_character:
            return
        
        # Get character stats - use the correct stat names from the config
        character = self.character_service.current_character
        stat_names = ['strength', 'intelligence', 'dexterity', 'constitution', 
                     'wisdom', 'luck', 'vitality', 'charisma']
        
        for i, stat_name in enumerate(stat_names):
            row = i // 2
            col = i % 2
            
            # Create frame for this stat
            stat_frame = tk.Frame(self.stat_controls_frame)
            stat_frame.grid(row=row, column=col, sticky=tk.W+tk.E, padx=5, pady=2)
            
            # Get stat value safely
            try:
                if hasattr(character, 'get_stat'):
                    stat_value = character.get_stat(stat_name)
                else:
                    stat_value = getattr(character, stat_name, 0)
            except (AttributeError, ValueError, TypeError):
                stat_value = 0
            
            self.stat_vars[stat_name] = tk.StringVar(value=str(int(stat_value)))
            
            tk.Label(stat_frame, text=f"{stat_name.capitalize()}:", width=12, anchor=tk.W).pack(side=tk.LEFT)
            tk.Label(stat_frame, textvariable=self.stat_vars[stat_name], width=3).pack(side=tk.LEFT)
            
            # Add point button
            add_btn = tk.Button(
                stat_frame,
                text="+",
                command=lambda s=stat_name: self._allocate_stat_point(s),
                width=2
            )
            add_btn.pack(side=tk.RIGHT)
            self.stat_buttons[stat_name] = add_btn
        
        # Configure grid weights
        for i in range(2):
            self.stat_controls_frame.columnconfigure(i, weight=1)
    
    def _update_points_display(self) -> None:
        """Update the available points display."""
        try:
            # Get points info using the correct method  
            points_info = self.character_service.get_points_display_info()
            available = points_info.get('available_points', 0)
            allocated = points_info.get('allocated_points', 0)
            infinite = points_info.get('infinite_mode', False)
            
            if infinite:
                self.points_label.config(text="Available Points: ∞")
            else:
                self.points_label.config(text=f"Available Points: {available} | Allocated: {allocated}")
            
        except Exception as e:
            self.logger.error(f"Failed to update points display: {e}")
            self.points_label.config(text="Points: Error loading")
    
    def _update_stat_displays(self) -> None:
        """Update stat value displays."""
        if not self.character_service.current_character:
            return
        
        character = self.character_service.current_character
        
        for stat_name, var in self.stat_vars.items():
            try:
                # Use get_stat method if available, fall back to getattr
                if hasattr(character, 'get_stat'):
                    stat_value = character.get_stat(stat_name)
                else:
                    stat_value = getattr(character, stat_name, 0)
                var.set(f"{stat_value:.2f}")
            except (AttributeError, ValueError, TypeError):
                var.set("0.00")
    
    def _update_preview(self, content: str) -> None:
        """Update the character preview display."""
        if not self.preview_text:
            return
        
        try:
            self.preview_text.config(state=tk.NORMAL)
            self.preview_text.delete(1.0, tk.END)
            self.preview_text.insert(tk.END, content)
            self.preview_text.config(state=tk.DISABLED)
        except Exception as e:
            self.logger.error(f"Preview update error: {e}")
    
    def _generate_character_preview(self) -> str:
        """Generate character preview text."""
        if not self.character_service.current_character:
            return "No character created yet"
        
        try:
            character = self.character_service.current_character
            
            def safe_get_stat(stat_name: str, default=0):
                """Safely get a character stat."""
                try:
                    if hasattr(character, 'get_stat'):
                        value = character.get_stat(stat_name)
                        return f"{value:.2f}" if isinstance(value, (int, float)) else value
                    value = getattr(character, stat_name, default)
                    return f"{value:.2f}" if isinstance(value, (int, float)) else value
                except (AttributeError, ValueError, TypeError):
                    return f"{default:.2f}" if isinstance(default, (int, float)) else default
            
            def safe_get_attr(attr_name: str, default="Unknown"):
                """Safely get a character attribute."""
                try:
                    return getattr(character, attr_name, default)
                except (AttributeError, TypeError):
                    return default
            
            # Generate character info
            info_lines = [
                f"Character: {character.name}",
                f"Level: {safe_get_attr('level', 1)}",
                f"Template: {safe_get_attr('template_id', 'Unknown') or 'Unknown'}",
                f"Grade: {safe_get_attr('grade_name', 'Unknown')}",
                f"Rarity: {safe_get_attr('rarity', 'Unknown')}",
                "",
                "=== BASE STATS ===",
                f"Strength: {safe_get_stat('strength')}",
                f"Intelligence: {safe_get_stat('intelligence')}",
                f"Dexterity: {safe_get_stat('dexterity')}",
                f"Constitution: {safe_get_stat('constitution')}",
                f"Wisdom: {safe_get_stat('wisdom')}",
                f"Luck: {safe_get_stat('luck')}",
                f"Vitality: {safe_get_stat('vitality')}",
                f"Charisma: {safe_get_stat('charisma')}",
                "",
                "=== DERIVED STATS ===",
                f"Health Points: {safe_get_attr('max_health', 0):.2f}/{safe_get_attr('max_health', 0):.2f}",
                f"Mana Points: {safe_get_attr('max_mana', 0):.2f}/{safe_get_attr('max_mana', 0):.2f}",
                "",
                "=== COMBAT STATS ===",
                f"Attack: {safe_get_stat('attack')}",
                f"Defense: {safe_get_stat('defense')}",
                f"Magic Power: {safe_get_stat('magic_power')}",
            ]
            
            return "\n".join(info_lines)
            
        except Exception as e:
            self.logger.error(f"Character preview generation error: {e}")
            return f"Error generating preview: {e}"
    
    # Event handlers
    def _on_template_selected(self, event=None) -> None:
        """Handle template selection."""
        template_id = self.template_var.get()
        if not template_id:
            return
        
        try:
            result = self.character_service.select_template(template_id)
            if result.get('success', False):
                # Show template details
                template_data = result.get('template')
                if template_data:
                    self._show_template_details(template_data)
                
                # Always create a new character when template changes to update stats
                self._create_new_character()
                self._trigger_status_update(f"Template '{template_id}' selected")
            else:
                self._trigger_status_update("Failed to select template", "error")
        except Exception as e:
            self.logger.error(f"Template selection error: {e}")
            self._trigger_status_update(f"Template selection error: {e}", "error")
    
    def _show_template_details(self, template_data: Dict[str, Any]) -> None:
        """Show template details in preview area."""
        if not self.preview_text:
            return
        
        try:
            # Generate template info with ranges for random generation
            info_lines = [
                f"=== TEMPLATE: {template_data.get('display_name', 'Unknown')} ===",
                f"Type: {template_data.get('team', 'Unknown')}",
                "",
                "=== POSSIBLE RANGES ===",
                "(Values show ranges for randomly generated characters)",
                "",
            ]
            
            # Show grade range
            grade = template_data.get('grade', 1)
            if isinstance(grade, dict):
                max_grade = grade.get('max', 'FIVE')
                info_lines.append(f"Grade: 1 - {max_grade}")
            else:
                info_lines.append(f"Grade: 1 - {grade}")
            
            # Show rarity range  
            rarity = template_data.get('rarity', 'COMMON')
            if isinstance(rarity, dict):
                max_rarity = rarity.get('max', 'DIVINE')
                info_lines.append(f"Rarity: COMMON - {max_rarity}")
            else:
                # Get rarity index to show range
                rarity_levels = ["COMMON", "UNCOMMON", "RARE", "EPIC", "LEGENDARY", "MYTHIC", "DIVINE"]
                try:
                    max_index = rarity_levels.index(rarity.upper())
                    max_rarity = rarity_levels[max_index]
                    info_lines.append(f"Rarity: COMMON - {max_rarity}")
                except ValueError:
                    info_lines.append(f"Rarity: Up to {rarity}")
            
            # Show level range
            level = template_data.get('level', 1)
            if isinstance(level, dict):
                start_level = level.get('start', 1)
                info_lines.append(f"Level: 1 - {start_level}")
            else:
                info_lines.append(f"Level: 1 - {level}")
            
            info_lines.extend([
                "",
                "=== BASE STATS (Fixed) ===",
            ])
            
            # Add base stats (these remain fixed)
            base_stats = template_data.get('base_stats', {})
            for stat_name, stat_value in base_stats.items():
                info_lines.append(f"{stat_name.capitalize()}: {stat_value}")
            
            # Add other template info
            if template_data.get('starting_items'):
                info_lines.extend([
                    "",
                    "=== STARTING ITEMS ===",
                    f"Items: {len(template_data['starting_items'])} items"
                ])
            
            if template_data.get('starting_skills'):
                info_lines.extend([
                    "",
                    "=== STARTING SKILLS ===",
                    f"Skills: {len(template_data['starting_skills'])} skills"
                ])
            
            # Add gold range
            gold = template_data.get('gold', {})
            if isinstance(gold, dict):
                min_gold = gold.get('min', 0)
                max_gold = gold.get('max', 0)
                info_lines.extend([
                    "",
                    "=== STARTING GOLD ===",
                    f"Gold: {min_gold} - {max_gold}"
                ])
            
            info_lines.extend([
                "",
                "Click 'New Character' to create a character from this template",
                "Each creation will have random grade, rarity, and level within these ranges!"
            ])
            
            template_info = "\n".join(info_lines)
            self._update_preview(template_info)
            
        except Exception as e:
            self.logger.error(f"Template details error: {e}")
            self._update_preview(f"Error showing template details: {e}")
    
    def _create_new_character(self) -> None:
        """Create a new character preview."""
        template_id = self.template_var.get()
        if not template_id:
            self._trigger_status_update("Please select a template first", "warning")
            return
        
        try:
            # Try to use the service method first
            result = self.character_service.create_character_preview(template_id)
            if result.get('success', False):
                self._create_stat_controls()
                self._update_points_display()
                if self.config.show_preview:
                    self._update_preview(self._generate_character_preview())
                
                self._trigger_status_update("Character preview created")
                if self.callbacks:
                    self.callbacks.on_character_updated(self.character_service.current_character)
            else:
                # If the service method fails, try direct character creation
                self._trigger_status_update("Service method failed, trying direct creation...", "warning")
                
                # Direct character creation as fallback
                from game_sys.character.character_service import create_character_with_random_stats
                character = create_character_with_random_stats(template_id)
                
                if character:
                    # Manually set the current character
                    self.character_service._state = self.character_service._state.with_character(character)
                    
                    self._create_stat_controls()
                    self._update_points_display()
                    if self.config.show_preview:
                        self._update_preview(self._generate_character_preview())
                    
                    self._trigger_status_update(f"Character created: {character.name}")
                    if self.callbacks:
                        self.callbacks.on_character_updated(character)
                else:
                    self._trigger_status_update("Failed to create character", "error")
        except Exception as e:
            self.logger.error(f"Character creation error: {e}")
            self._trigger_status_update(f"Character creation error: {e}", "error")
    
    def _allocate_stat_point(self, stat_name: str) -> None:
        """Allocate a stat point."""
        try:
            result = self.character_service.allocate_stat_point(stat_name)
            if result['success']:
                self._update_stat_displays()
                self._update_points_display()
                if self.config.show_preview:
                    self._update_preview(self._generate_character_preview())
                
                self._trigger_status_update(f"Point allocated to {stat_name}")
                if self.callbacks:
                    self.callbacks.on_character_updated(self.character_service.current_character)
            else:
                self._trigger_status_update(result['message'], "warning")
        except Exception as e:
            self.logger.error(f"Stat allocation error: {e}")
            self._trigger_status_update(f"Stat allocation error: {e}", "error")
    
    def _reset_stats(self) -> None:
        """Reset character stats."""
        try:
            result = self.character_service.reset_stat_allocation()
            if result['success']:
                self._update_stat_displays()
                self._update_points_display()
                if self.config.show_preview:
                    self._update_preview(self._generate_character_preview())
                
                self._trigger_status_update("Character stats reset")
                if self.callbacks:
                    self.callbacks.on_character_updated(self.character_service.current_character)
            else:
                self._trigger_status_update(result['message'], "error")
        except Exception as e:
            self.logger.error(f"Reset stats error: {e}")
            self._trigger_status_update(f"Reset stats error: {e}", "error")
    
    def _finalize_character(self) -> None:
        """Finalize character creation."""
        try:
            custom_name = self.name_var.get().strip()
            result = self.character_service.finalize_character(custom_name)
            
            if result.success:
                character = result.data.get('character') if result.data else self.character_service.current_character
                messagebox.showinfo(
                    "Character Created!",
                    f"Successfully created {character.name}!"
                )
                self._trigger_status_update("Character finalized!")
                if self.callbacks:
                    self.callbacks.on_character_created(character)
            else:
                messagebox.showerror("Error", result.message or result.error)
                self._trigger_status_update(result.message or result.error, "error")
        except Exception as e:
            self.logger.error(f"Character finalization error: {e}")
            self._trigger_status_update(f"Finalization error: {e}", "error")
    
    def _save_character(self) -> None:
        """Save character to library."""
        try:
            if not self.character_service.current_character:
                messagebox.showwarning("No Character", "No character to save!")
                return
            
            # Get save name from user
            save_name = simpledialog.askstring(
                "Save Character",
                f"Enter a name for saving '{self.character_service.current_character.name}':",
                initialvalue=self.character_service.current_character.name
            )
            
            if save_name and save_name.strip():
                result = self.character_service.save_current_character(save_name.strip())
                if result['success']:
                    messagebox.showinfo("Character Saved!", result['message'])
                    self._trigger_status_update("Character saved to library")
                else:
                    messagebox.showerror("Save Failed", result['message'])
                    self._trigger_status_update(result['message'], "error")
        except Exception as e:
            self.logger.error(f"Save character error: {e}")
            self._trigger_status_update(f"Save error: {e}", "error")
    
    def _load_character(self) -> None:
        """Load character from library."""
        try:
            # Get available characters using the correct method that returns dict
            result = self.character_service.get_saved_character_list()
            if not result.get('success', False) or result.get('count', 0) == 0:
                messagebox.showinfo("Library Empty", "No saved characters found!")
                return
            
            # Create selection dialog with delete option
            characters = result.get('characters', [])
            character_names = [f"{char['save_name']} ({char['character_name']})" for char in characters]
            
            # Enhanced selection dialog with delete functionality
            selected_action = self._show_character_management_dialog(
                "Character Library",
                "Select a character to load or delete:",
                character_names
            )
            
            if selected_action is not None:
                action, index = selected_action
                save_name = character_names[index].split(' (')[0]
                
                if action == "load":
                    load_result = self.character_service.load_saved_character(save_name)
                    if load_result.get('success', False):
                        # Update template selection
                        template_id = load_result.get('template_id', '')
                        if template_id:
                            self.template_var.set(template_id)
                        
                        # Update displays
                        self.refresh()
                        messagebox.showinfo("Character Loaded", load_result.get('message', 'Character loaded successfully'))
                        self._trigger_status_update("Character loaded from library")
                    else:
                        messagebox.showerror("Load Failed", load_result.get('message', 'Failed to load character'))
                        self._trigger_status_update(load_result.get('message', 'Load failed'), "error")
                
                elif action == "delete":
                    # Confirm deletion
                    if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete '{save_name}'?\n\nThis action cannot be undone."):
                        delete_result = self.character_service.delete_saved_character(save_name)
                        if delete_result.get('success', False):
                            messagebox.showinfo("Character Deleted", f"Character '{save_name}' has been deleted.")
                            self._trigger_status_update(f"Character '{save_name}' deleted from library")
                        else:
                            messagebox.showerror("Delete Failed", delete_result.get('message', 'Failed to delete character'))
                            self._trigger_status_update(delete_result.get('message', 'Delete failed'), "error")
                    
        except Exception as e:
            self.logger.error(f"Load character error: {e}")
            self._trigger_status_update(f"Load error: {e}", "error")
    
    def _show_selection_dialog(self, title: str, prompt: str, options: List[str]) -> Optional[int]:
        """Show a simple selection dialog."""
        if not options:
            return None
        
        # Create a simple dialog
        dialog = tk.Toplevel(self.parent)
        dialog.title(title)
        dialog.geometry("400x300")
        dialog.transient(self.parent)
        dialog.grab_set()
        
        result = [None]  # Use list to store result for closure
        
        # Center dialog
        dialog.geometry("+%d+%d" % (
            self.parent.winfo_rootx() + 50,
            self.parent.winfo_rooty() + 50
        ))
        
        # Prompt label
        tk.Label(dialog, text=prompt, font=("Arial", 10)).pack(pady=10)
        
        # Listbox with options
        list_frame = tk.Frame(dialog)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        scrollbar = tk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        listbox = tk.Listbox(list_frame, yscrollcommand=scrollbar.set)
        listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=listbox.yview)
        
        for option in options:
            listbox.insert(tk.END, option)
        
        # Buttons
        button_frame = tk.Frame(dialog)
        button_frame.pack(fill=tk.X, padx=10, pady=10)
        
        def on_select():
            selection = listbox.curselection()
            if selection:
                result[0] = selection[0]
                dialog.destroy()
        
        def on_cancel():
            dialog.destroy()
        
        tk.Button(button_frame, text="Select", command=on_select, bg="#3498db", fg="white").pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Cancel", command=on_cancel, bg="#95a5a6", fg="white").pack(side=tk.RIGHT, padx=5)
        
        # Enable double-click selection
        listbox.bind("<Double-Button-1>", lambda e: on_select())
        
        # Wait for dialog to close
        dialog.wait_window()
        
        return result[0]
    
    def _show_character_management_dialog(self, title: str, prompt: str, options: List[str]) -> Optional[tuple]:
        """Show a character management dialog with load and delete options."""
        if not options:
            return None
        
        # Create dialog
        dialog = tk.Toplevel(self.parent)
        dialog.title(title)
        dialog.geometry("500x350")
        dialog.transient(self.parent)
        dialog.grab_set()
        
        result = [None]  # Use list to store result for closure
        
        # Center dialog
        dialog.geometry("+%d+%d" % (
            self.parent.winfo_rootx() + 50,
            self.parent.winfo_rooty() + 50
        ))
        
        # Prompt label
        tk.Label(dialog, text=prompt, font=("Arial", 10)).pack(pady=10)
        
        # Listbox with options
        list_frame = tk.Frame(dialog)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        scrollbar = tk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        listbox = tk.Listbox(list_frame, yscrollcommand=scrollbar.set)
        listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=listbox.yview)
        
        for option in options:
            listbox.insert(tk.END, option)
        
        # Buttons
        button_frame = tk.Frame(dialog)
        button_frame.pack(fill=tk.X, padx=10, pady=10)
        
        def on_load():
            selection = listbox.curselection()
            if selection:
                result[0] = ("load", selection[0])
                dialog.destroy()
            else:
                messagebox.showwarning("No Selection", "Please select a character first.")
        
        def on_delete():
            selection = listbox.curselection()
            if selection:
                result[0] = ("delete", selection[0])
                dialog.destroy()
            else:
                messagebox.showwarning("No Selection", "Please select a character first.")
        
        def on_cancel():
            dialog.destroy()
        
        # Button layout
        tk.Button(button_frame, text="📂 Load", command=on_load, bg="#3498db", fg="white").pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="🗑️ Delete", command=on_delete, bg="#e74c3c", fg="white").pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Cancel", command=on_cancel, bg="#95a5a6", fg="white").pack(side=tk.RIGHT, padx=5)
        
        # Enable double-click to load
        listbox.bind("<Double-Button-1>", lambda e: on_load())
        
        # Wait for dialog to close
        dialog.wait_window()
        
        return result[0]
    
    def _copy_character(self) -> None:
        """Copy character info to clipboard."""
        try:
            if self.character_service.current_character:
                character_info = self._generate_character_preview()
                
                # Copy to clipboard
                self.parent.clipboard_clear()
                self.parent.clipboard_append(character_info)
                self.parent.update()
                
                self._trigger_status_update("Character info copied to clipboard")
            else:
                self._trigger_status_update("No character to copy", "warning")
        except Exception as e:
            self.logger.error(f"Copy character error: {e}")
            self._trigger_status_update(f"Copy error: {e}", "error")
    
    def _trigger_status_update(self, message: str, msg_type: str = "info") -> None:
        """Trigger status update callback."""
        if self.callbacks:
            self.callbacks.on_status_update(message, msg_type)
    
    # Public methods
    def refresh(self) -> None:
        """Refresh the workshop content."""
        try:
            # Reload templates
            templates = list(self.character_service.get_available_templates().keys())
            self.template_combo['values'] = templates
            
            # Update displays
            self._update_stat_displays()
            self._update_points_display()
            if self.config.show_preview:
                self._update_preview(self._generate_character_preview())
            
        except Exception as e:
            self.logger.error(f"Workshop refresh error: {e}")
    
    def _setup_auto_refresh(self) -> None:
        """Set up automatic refresh observer."""
        try:
            self.workshop_observer = CharacterWorkshopObserver(self)
            self.character_service.add_observer(self.workshop_observer)
            self.logger.info("Auto-refresh observer registered")
        except Exception as e:
            self.logger.error(f"Failed to setup auto-refresh: {e}")
    
    def _refresh_all_displays(self) -> None:
        """Refresh all UI displays."""
        try:
            self._create_stat_controls()
            self._update_points_display()
            if self.config.show_preview:
                self._update_preview(self._generate_character_preview())
            self.logger.debug("All displays refreshed")
        except Exception as e:
            self.logger.error(f"Failed to refresh all displays: {e}")
    
    def _refresh_stat_displays(self) -> None:
        """Refresh stat-related displays only."""
        try:
            self._update_stat_displays()
            self._update_points_display()
            if self.config.show_preview:
                self._update_preview(self._generate_character_preview())
            self.logger.debug("Stat displays refreshed")
        except Exception as e:
            self.logger.error(f"Failed to refresh stat displays: {e}")
    
    def _refresh_template_display(self) -> None:
        """Refresh template-related displays only."""
        try:
            # Update template combo if needed
            templates = list(self.character_service.get_available_templates().keys())
            current_values = list(self.template_combo['values']) if self.template_combo else []
            if current_values != templates:
                self.template_combo['values'] = templates
            
            # Show template details if one is selected - but don't call select_template again!
            template_id = self.template_var.get()
            if template_id and self.config.show_preview:
                # Get template data directly without triggering selection
                template_data = self.character_service._template_service.get_template(template_id)
                if template_data:
                    self._show_template_details(template_data)
            
            self.logger.debug("Template display refreshed")
        except Exception as e:
            self.logger.error(f"Failed to refresh template display: {e}")
    
    def get_current_character(self) -> Any:
        """Get the current character."""
        return self.character_service.current_character
    
    def set_admin_mode(self, enabled: bool) -> None:
        """Enable or disable admin mode features."""
        self.config.show_admin_buttons = enabled
        # Could refresh button layout here if needed
    
    def _open_admin_panel(self) -> None:
        """Open admin panel window."""
        try:
            # Check if we have the admin service
            if not hasattr(self, '_admin_service'):
                # Try to get admin service from callbacks
                if hasattr(self.callbacks, 'get_admin_service'):
                    self._admin_service = self.callbacks.get_admin_service()
                else:
                    messagebox.showerror("Admin Panel", "Admin service not available!")
                    return
            
            # Create admin panel window
            admin_window = tk.Toplevel(self.parent)
            admin_window.title("Admin Panel")
            admin_window.geometry("600x500")
            admin_window.transient(self.parent)
            
            # Center the window
            admin_window.geometry("+%d+%d" % (
                self.parent.winfo_rootx() + 100,
                self.parent.winfo_rooty() + 100
            ))
            
            # Create notebook for admin tabs
            notebook = ttk.Notebook(admin_window)
            notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            
            # Character cheats tab
            char_frame = tk.Frame(notebook)
            notebook.add(char_frame, text="Character Cheats")
            
            tk.Label(char_frame, text="Character Manipulation", font=("Arial", 14, "bold")).pack(pady=10)
            
            # Level controls
            level_frame = tk.Frame(char_frame)
            level_frame.pack(fill=tk.X, padx=20, pady=5)
            tk.Label(level_frame, text="Set Level:").pack(side=tk.LEFT)
            level_var = tk.StringVar(value="1")
            tk.Entry(level_frame, textvariable=level_var, width=10).pack(side=tk.LEFT, padx=5)
            tk.Button(level_frame, text="Apply", 
                     command=lambda: self._admin_set_level(level_var.get())).pack(side=tk.LEFT, padx=5)
            
            # Stat boosts
            tk.Button(char_frame, text="Max All Stats", 
                     command=self._admin_max_stats, width=20).pack(pady=5)
            tk.Button(char_frame, text="Restore Full Health", 
                     command=self._admin_heal_full, width=20).pack(pady=5)
            tk.Button(char_frame, text="Grant All Skills", 
                     command=self._admin_grant_skills, width=20).pack(pady=5)
            
            # Item cheats tab
            item_frame = tk.Frame(notebook)
            notebook.add(item_frame, text="Item Cheats")
            
            tk.Label(item_frame, text="Item Management", font=("Arial", 14, "bold")).pack(pady=10)
            tk.Button(item_frame, text="Give Best Equipment", 
                     command=self._admin_give_best_gear, width=20).pack(pady=5)
            tk.Button(item_frame, text="Clear All Equipment", 
                     command=self._admin_clear_gear, width=20).pack(pady=5)
            
            self._trigger_status_update("Admin panel opened")
            
        except Exception as e:
            self.logger.error(f"Admin panel error: {e}")
            messagebox.showerror("Admin Panel Error", f"Failed to open admin panel: {e}")
    
    def _show_debug_info(self) -> None:
        """Show debug information."""
        try:
            # Get current character using the correct property
            character = self.character_service.current_character
            if not character:
                messagebox.showinfo("Debug Info", "No character loaded")
                return
            
            # Gather debug info
            debug_info = f"""Debug Information
"""
            
            # Create debug window
            debug_window = tk.Toplevel(self.parent)
            debug_window.title("Debug Information")
            debug_window.geometry("500x600")
            
            text_widget = tk.Text(debug_window, wrap=tk.WORD, font=('Consolas', 10))
            scrollbar = tk.Scrollbar(debug_window, command=text_widget.yview)
            text_widget.configure(yscrollcommand=scrollbar.set)
            
            text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            
            text_widget.insert(tk.END, debug_info)
            text_widget.configure(state=tk.DISABLED)
            
            self._trigger_status_update("Debug info displayed")
        
        except Exception as e:
            self.logger.error(f"Debug info error: {e}")
            messagebox.showerror("Debug Error", f"Failed to show debug info: {e}")

    # Admin command methods
    def _admin_set_level(self, level_str: str) -> None:
        """Set character level (admin command)."""
        try:
            level = int(level_str)
            if level < 1 or level > 100:
                messagebox.showerror("Invalid Level", "Level must be between 1 and 100")
                return
            
            # This would need admin service integration
            messagebox.showinfo("Admin Command", f"Set level to {level} (placeholder)")
            self._trigger_status_update(f"Admin: Set level to {level}")
            
        except ValueError:
            messagebox.showerror("Invalid Input", "Level must be a number")

    def _admin_max_stats(self) -> None:
        """Max all character stats (admin command)."""
        messagebox.showinfo("Admin Command", "Max all stats (placeholder)")
        self._trigger_status_update("Admin: Maxed all stats")

    def _admin_heal_full(self) -> None:
        """Restore full health (admin command)."""
        messagebox.showinfo("Admin Command", "Full heal (placeholder)")
        self._trigger_status_update("Admin: Full heal applied")

    def _admin_grant_skills(self) -> None:
        """Grant all skills (admin command)."""
        messagebox.showinfo("Admin Command", "Grant all skills (placeholder)")
        self._trigger_status_update("Admin: All skills granted")

    def _admin_give_best_gear(self) -> None:
        """Give best equipment (admin command)."""
        messagebox.showinfo("Admin Command", "Give best gear (placeholder)")
        self._trigger_status_update("Admin: Best gear equipped")

    def _admin_clear_gear(self) -> None:
        """Clear all equipment (admin command)."""
        messagebox.showinfo("Admin Command", "Clear all gear (placeholder)")
        self._trigger_status_update("Admin: All gear cleared")
