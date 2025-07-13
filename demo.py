#!/usr/bin/env python3
"""
Simple Game Demo
===============

A basic demo for the game engine with integrated logging and tabbed interface.
"""

import tkinter as tk
from tkinter import ttk
import time
import random
import math
import os
import sys
import json


# Import logging system
from logs.logs import get_logger, setup_logging

# Import hooks system
from game_sys.hooks.hooks_setup import emit, on, ON_COMBO_TRIGGERED, ON_COMBO_FINISHED

# Set up logging
setup_logging()
logger = get_logger("simple_demo")

# Import game system


from game_sys.character.character_factory import create_character
from game_sys.character.character_service import (
    create_character_with_random_stats
)
from game_sys.combat.combat_service import CombatService
from game_sys.config.property_loader import PropertyLoader

try:

    from game_sys.magic.enchanting_system import EnchantingSystem
    ITEMS_AVAILABLE = True
    SPELLS_AVAILABLE = True
    ENCHANTING_AVAILABLE = True
except ImportError:
    ITEMS_AVAILABLE = True
    SPELLS_AVAILABLE = True
    ENCHANTING_AVAILABLE = True

class SimpleGameDemo:
    def check_and_apply_combo_bonus(self):
        """Check if the current combo sequence matches any defined combo and apply its bonus."""
        if not hasattr(self, 'combo_sequence') or not self.combo_sequence:
            return
        if not hasattr(self, 'combos_data') or not isinstance(self.combos_data, list):
            return
        for combo in self.combos_data:
            if isinstance(combo, dict):
                sequence = combo.get('sequence', [])
                effects = combo.get('effects', None)
                name = combo.get('name', 'Unnamed Combo')
                # Check for exact match (can be improved for partials, order, etc.)
                if self.combo_sequence == sequence:
                    # Apply effects (for demo, just log and show in combo tab)
                    self.log_message(f"Combo Bonus Activated: {name}! Effects: {effects}", "info")
                    # Optionally, apply effects to player/enemy here
                    # Reset combo sequence after activation
                    self.combo_sequence = []
                    self.combo_timer = 0
                    self.update_combo_tab()
                    break
    def save_game(self):
        """Save the current game state asynchronously (demo version)."""
        import asyncio
        from game_sys.config.save_load import save_actors_async
        try:
            # For demo, just save player and enemy if they exist
            actors = [a for a in [getattr(self, 'player', None), getattr(self, 'enemy', None)] if a]
            asyncio.run(save_actors_async(actors, "demo_save.json"))
            self.log_message("Game saved to demo_save.json", "info")
        except Exception as e:
            self.log_message(f"Save failed: {e}", "combat")

    def load_game(self):
        """Load the game state asynchronously (demo version)."""
        import asyncio
        from game_sys.config.save_load import load_actors_async
        try:
            actors = asyncio.run(load_actors_async("demo_save.json"))
            # For demo, assign first to player, second to enemy
            if actors:
                self.player = actors[0]
                if len(actors) > 1:
                    self.enemy = actors[1]
                self.log_message("Game loaded from demo_save.json", "info")
                self.update_char_info()
                self.update_enemy_info()
            else:
                self.log_message("No actors found in save file.", "combat")
        except Exception as e:
            self.log_message(f"Load failed: {e}", "combat")
    """A simple game demo with logging and tabbed UI."""

    def __init__(self):
        """Initialize the demo."""
        logger.info("Initializing Simple Game Demo")
        
        # --- Startup validation and logging ---
        from game_sys.config.config_manager import ConfigManager
        cfg = ConfigManager()
        config_files = [
            os.path.abspath(cfg.default_path),
            os.path.abspath(cfg.user_path),
            os.path.abspath(cfg.game_settings_path)
        ]
        logger.info("STARTUP: Validating config files...")
        for path in config_files:
            if os.path.exists(path):
                logger.info(f"Config file found: {path}")
            else:
                logger.warning(f"Config file missing: {path}")

        # Validate config keys and log important values
        try:
            # Check a few critical config values
            strength_mult = cfg.get('constants.combat.strength_multiplier', None)
            stamina_costs = cfg.get('constants.combat.stamina_costs', None)
            max_level = cfg.get('constants.leveling.max_level', None)
            logger.info(f"CONFIG: strength_multiplier = {strength_mult}")
            logger.info(f"CONFIG: stamina_costs = {stamina_costs}")
            logger.info(f"CONFIG: max_level = {max_level}")
            # Check for required keys
            required_keys = [
                'constants.combat.strength_multiplier',
                'constants.combat.stamina_costs',
                'constants.derived_stats.health',
                'constants.derived_stats.stamina',
                'constants.derived_stats.mana',
                'constants.leveling.max_level',
                'defaults.grades',
                'defaults.rarities'
            ]
            for key in required_keys:
                val = cfg.get(key, None)
                if val is None:
                    logger.error(f"CONFIG ERROR: Missing required config key: {key}")
                else:
                    logger.info(f"CONFIG OK: {key} = {val}")
        except Exception as e:
            logger.error(f"CONFIG VALIDATION ERROR: {e}")

        # Log working directory and Python version
        logger.info(f"Working directory: {os.getcwd()}")
        logger.info(f"Python version: {sys.version}")

        # Create main window
        self.root = tk.Tk()
        self.root.title("Simple Game Demo")
        self.root.geometry("900x700")

        # Set up UI
        self.setup_ui()

        # Set up combo hooks
        self.setup_combo_hooks()

        # Set up game state
        self.setup_game_state()

        logger.info("Demo initialized")

    def setup_ui(self):
        """Set up the user interface with tabs."""
        logger.info("Setting up tabbed UI")

        # Create main frame
        self.main_frame = tk.Frame(self.root, bg="black")
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # Create tab control
        self.tab_control = ttk.Notebook(self.main_frame)

        # Create tabs
        self.stats_tab = ttk.Frame(self.tab_control)
        self.combat_tab = ttk.Frame(self.tab_control)
        self.inventory_tab = ttk.Frame(self.tab_control)
        self.leveling_tab = ttk.Frame(self.tab_control)  # Leveling tab
        self.enchanting_tab = ttk.Frame(self.tab_control)  # Enchanting tab

        # Add tabs to notebook
        self.tab_control.add(self.stats_tab, text="Character Stats")
        self.tab_control.add(self.combat_tab, text="Combat")
        self.tab_control.add(self.inventory_tab, text="Inventory")
        self.tab_control.add(self.leveling_tab, text="Leveling")
        self.tab_control.add(self.enchanting_tab, text="Enchanting")

        # Add progression tab
        self.progression_tab = ttk.Frame(self.tab_control)
        self.tab_control.add(self.progression_tab, text="Progression")

        # Combo Tab
        self.combo_tab = ttk.Frame(self.tab_control)
        self.tab_control.add(self.combo_tab, text="Combos")

        # Settings tab
        self.settings_tab = ttk.Frame(self.tab_control)
        self.tab_control.add(self.settings_tab, text="Settings")

        # Pack the tab control
        self.tab_control.pack(expand=1, fill=tk.BOTH, padx=10, pady=10)

        # Bind tab change event to update displays
        self.tab_control.bind('<<NotebookTabChanged>>', self.on_tab_changed)

        # Set up the Stats tab
        self.setup_stats_tab()

        # Set up the Combat tab
        self.setup_combat_tab()

        # Set up the Inventory tab
        self.setup_inventory_tab()

        # Set up the Leveling tab
        self.setup_leveling_tab()  # Set up leveling tab

        # Set up the Enchanting tab
        self.setup_enchanting_tab()  # Set up enchanting tab

        # Set up the Progression tab
        self.setup_progression_tab()  # Set up progression tab

        # Set up the Combo tab
        self.setup_combo_tab()

        # Set up the Settings tab
        self.setup_settings_tab()

        # Create log area
        self.log_frame = tk.Frame(self.root, bg="black")
        self.log_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=10)

        self.log = tk.Text(self.log_frame, bg="black", fg="white", height=8)
        self.log.pack(fill=tk.X)

        # Configure text tags
        self.log.tag_configure("info", foreground="cyan")
        self.log.tag_configure("combat", foreground="red")
        self.log.tag_configure("heal", foreground="green")

    def setup_combo_hooks(self):
        """Set up combo system hooks for real-time updates."""
        # Initialize combo tracking variables
        self.combo_sequence = []
        self.combo_timer = 0.0
        self.combo_window = 3.0  # 3 second window for combos
        
        # Hook for combo triggers
        def on_combo_triggered(actor, combo):
            self.log_message(f"{actor.name} triggered combo: {combo}!", "combat")
            # Update combo display
            self.combo_sequence = []
            self.combo_timer = 0.0
            # Flash combo notification
            if hasattr(self, 'combo_tab') and hasattr(self, 'combo_status_label'):
                self.combo_status_label.config(text=f"COMBO TRIGGERED: {combo.upper()}", fg="yellow")
                self.root.after(2000, lambda: self.combo_status_label.config(text="Ready for combo...", fg="white"))
        
        on(ON_COMBO_TRIGGERED, on_combo_triggered)
        
        # Hook for combo finish (if available)
        try:
            def on_combo_finished(actor, combo):
                self.log_message(f"{actor.name} completed combo: {combo}", "info")
                if hasattr(self, 'combo_tab'):
                    self.update_combo_tab()
            on(ON_COMBO_FINISHED, on_combo_finished)
        except NameError:
            # ON_COMBO_FINISHED might not be defined
            pass

    def setup_combo_tab(self):
        """Set up the combo tab UI elements."""
        import json
        import os
        combo_tab = self.combo_tab
        # Do not set bg for ttk.Frame (combo_tab)

        # Title
        title = tk.Label(combo_tab, text="Combo System", font=("Arial", 16, "bold"), fg="cyan", bg="black")
        title.pack(pady=(10, 5))

        # Current combo sequence
        self.combo_sequence_label = tk.Label(combo_tab, text="Current Combo: -", font=("Arial", 12), fg="white", bg="black")
        self.combo_sequence_label.pack(pady=(5, 10))

        # Combo progress bar
        self.combo_progress_var = tk.DoubleVar()
        self.combo_progress = tk.Scale(combo_tab, variable=self.combo_progress_var, from_=0, to=100, orient=tk.HORIZONTAL, length=300, showvalue=0, fg="green", troughcolor="#222", sliderrelief=tk.FLAT)
        self.combo_progress.pack(pady=(0, 10))

        # Combo status bar
        status_frame = tk.Frame(combo_tab, bg="black")
        status_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        self.combo_status_label = tk.Label(status_frame, text="Status: Ready", font=("Arial", 10), fg="green", bg="black")
        self.combo_status_label.pack(side=tk.LEFT)
        
        self.combo_timer_label = tk.Label(status_frame, text="Timer: 0.0s", font=("Arial", 10), fg="yellow", bg="black")
        self.combo_timer_label.pack(side=tk.RIGHT)

        # Available combos section
        combos_frame = tk.Frame(combo_tab, bg="black")
        combos_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        combos_title = tk.Label(combos_frame, text="Available Combos", font=("Arial", 14, "bold"), fg="yellow", bg="black")
        combos_title.pack(anchor="w")

        self.combos_listbox = tk.Listbox(combos_frame, bg="#222", fg="white", font=("Arial", 11), height=8)
        self.combos_listbox.pack(fill=tk.BOTH, expand=True, pady=(5, 0))

        # Combo details
        self.combo_details = tk.Text(combos_frame, bg="#111", fg="white", font=("Arial", 10), height=6, state="disabled")
        self.combo_details.pack(fill=tk.X, pady=(5, 0))

        # Load combos from config
        combos_path = os.path.join("game_sys", "magic", "data", "combos.json")
        self.combos_data = []
        if os.path.exists(combos_path):
            try:
                with open(combos_path, "r") as f:
                    data = json.load(f)
                    # Convert from the actual JSON structure to list format expected by demo
                    combos_dict = data.get("combos", {})
                    for combo_id, combo_info in combos_dict.items():
                        combo_with_name = combo_info.copy()
                        if "name" not in combo_with_name:
                            combo_with_name["name"] = combo_id.replace("_", " ").title()
                        self.combos_data.append(combo_with_name)
            except Exception as e:
                self.log_message(f"Failed to load combos.json: {e}", "info")

        # Populate combos listbox
        for combo in self.combos_data:
            if isinstance(combo, dict):
                name = combo.get("name", "Unnamed Combo")
            else:
                name = str(combo)
            self.combos_listbox.insert(tk.END, name)

        self.combos_listbox.bind("<<ListboxSelect>>", self.on_combo_select)

        # Initial update
        self.update_combo_tab()

    def update_combo_tab(self):
        """Update the combo tab display with current sequence and progress."""
        # Update current combo sequence
        seq = self.combo_sequence if hasattr(self, "combo_sequence") else []
        seq_str = " > ".join(seq) if seq else "-"
        self.combo_sequence_label.config(text=f"Current Combo: {seq_str}")

        # Update progress bar
        pct = 0
        timer_val = 0.0
        if hasattr(self, "combo_timer") and hasattr(self, "combo_window") and self.combo_window > 0:
            timer_val = self.combo_timer
            pct = max(0, min(100, int(100 * self.combo_timer / self.combo_window)))
        self.combo_progress_var.set(pct)
        
        # Update status bar
        if hasattr(self, 'combo_status_label'):
            if seq:
                status = "Building Combo" if pct > 0 else "Combo Ready"
                color = "orange" if pct > 0 else "green"
            else:
                status = "Ready"
                color = "green"
            self.combo_status_label.config(text=f"Status: {status}", fg=color)
        
        if hasattr(self, 'combo_timer_label'):
            self.combo_timer_label.config(text=f"Timer: {timer_val:.1f}s")
            
        # Update combat tab combo visuals
        self.update_combat_combo_display(seq, pct, timer_val)

        # If a combo is selected, show details
        selection = self.combos_listbox.curselection()
        if selection and isinstance(self.combos_data, list) and selection[0] < len(self.combos_data):
            idx = selection[0]
            combo = self.combos_data[idx]
            if isinstance(combo, dict):
                details = (
                    f"Name: {combo.get('name', '-') }\n"
                    f"Sequence: {', '.join(combo.get('sequence', []))}\n"
                    f"Timing Window: {combo.get('window', '-')}\n"
                    f"Cost: {combo.get('cost', '-')}\n"
                    f"Effects: {combo.get('effects', '-')}\n"
                    f"Requirements: {combo.get('requirements', '-')}\n"
                )
            else:
                details = str(combo)
            self.combo_details.config(state="normal")
            self.combo_details.delete(1.0, tk.END)
            self.combo_details.insert(tk.END, details)
            self.combo_details.config(state="disabled")
        else:
            self.combo_details.config(state="normal")
            self.combo_details.delete(1.0, tk.END)
            self.combo_details.insert(tk.END, "Select a combo to view details.")
            self.combo_details.config(state="disabled")

    def on_combo_select(self, event):
        """Handle selection of a combo in the listbox."""
        self.update_combo_tab()

    # Call update_combo_tab() whenever combo state changes (e.g., after spell cast)

    def update_combat_combo_display(self, seq, pct, timer_val):
        """Update combo visuals in the combat tab."""
        if not hasattr(self, 'combat_combo_sequence'):
            return
            
        # Update sequence display
        seq_text = " > ".join(seq[-3:]) if seq else "Ready"  # Show last 3 spells
        if len(seq) > 3:
            seq_text = "..." + seq_text
        self.combat_combo_sequence.config(text=seq_text)
        
        # Update color based on sequence length
        if len(seq) >= 2:
            self.combat_combo_sequence.config(fg="orange")
        elif len(seq) == 1:
            self.combat_combo_sequence.config(fg="yellow")
        else:
            self.combat_combo_sequence.config(fg="green")
            
        # Update progress bar
        if hasattr(self, 'combat_combo_progress'):
            self.combat_combo_progress.delete("all")
            width = self.combat_combo_progress.winfo_width()
            if width > 1:  # Only draw if widget is rendered
                # Background
                self.combat_combo_progress.create_rectangle(0, 0, width, 20, 
                                                          fill="#333", outline="")
                # Progress
                if pct > 0:
                    progress_width = int(width * pct / 100)
                    color = "#ff4444" if pct > 80 else "#ffaa00" if pct > 50 else "#44ff44"
                    self.combat_combo_progress.create_rectangle(0, 0, progress_width, 20, 
                                                              fill=color, outline="")

    def track_spell_cast(self, spell_id):
        """Track a spell cast for combo building."""
        import time
        
        # Add to sequence
        if not hasattr(self, 'combo_sequence'):
            self.combo_sequence = []
        self.combo_sequence.append(spell_id)
        
        # Reset timer
        self.combo_timer = self.combo_window
        
        # Trim sequence to reasonable length
        if len(self.combo_sequence) > 5:
            self.combo_sequence.pop(0)
            
        # Show visual feedback for spell cast
        self.log_message(f"Cast spell: {spell_id}", "magic")
            
        # Update displays
        self.update_combo_tab()
        
        # Start timer countdown
        self.start_combo_timer()
        
    def start_combo_timer(self):
        """Start/continue the combo timer countdown."""
        if hasattr(self, 'combo_timer') and self.combo_timer > 0:
            self.combo_timer -= 0.1
            self.root.after(100, self.start_combo_timer)  # Update every 100ms
            if self.combo_timer <= 0:
                # Timer expired, clear sequence
                self.combo_sequence = []
                self.update_combo_tab()

    def setup_stats_tab(self):
        """Set up the character stats tab."""
        # Left side: Character portrait and basic info
        left_frame = tk.Frame(self.stats_tab, bg="black")
        left_frame.pack(
            side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10
        )

        # Character portrait area
        portrait_frame = tk.Frame(
            left_frame, bg="dark gray", width=200, height=200
        )
        portrait_frame.pack(pady=10)
        portrait_frame.pack_propagate(False)

        portrait_label = tk.Label(
            portrait_frame,
            text="Character Portrait",
            bg="dark gray",
            fg="white"
        )
        portrait_label.pack(expand=True)

        # Character details
        self.basic_info = tk.Text(
            left_frame,
            width=25,
            height=8,
            bg="light gray",
            state="disabled"
        )
        self.basic_info.pack(fill=tk.X, pady=10)

        # Status effects display
        status_frame = tk.Frame(left_frame, bg="black")
        status_frame.pack(fill=tk.X, pady=5)
        
        status_title = tk.Label(status_frame, text="Active Effects", font=("Arial", 12, "bold"), fg="cyan", bg="black")
        status_title.pack()
        
        self.status_effects_display = tk.Text(
            status_frame,
            width=25,
            height=4,
            bg="dark gray",
            fg="white",
            state="disabled"
        )
        self.status_effects_display.pack(fill=tk.X, pady=5)

        # Right side: Detailed stats
        right_frame = tk.Frame(self.stats_tab, bg="black")
        right_frame.pack(
            side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10
        )

        # Detailed character info
        self.detailed_stats = tk.Text(
            right_frame,
            width=30,
            height=20,
            bg="light gray",
            state="disabled"
        )
        self.detailed_stats.pack(fill=tk.BOTH, expand=True)

        # Bottom: Character actions
        button_frame = tk.Frame(self.stats_tab, bg="#222")
        button_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=10)

        # Improved button style
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

        stat_buttons = [
            ("View Inventory", self.view_inventory, "#5bc0de"),
            ("Level Up", self.level_up, "#5cb85c"),
            ("Equip Gear", self.equip_gear, "#f0ad4e"),
            ("Restore Health", self.restore_health, "#d9534f"),
            ("Restore Mana", self.restore_mana, "#5bc0de"),
            ("Restore Stamina", self.restore_stamina, "#f7e359"),
            ("Restore All", self.restore_all_resources, "#337ab7"),
            ("Save Game", self.save_game, "#0275d8"),
            ("Load Game", self.load_game, "#5cb85c"),
        ]


        # Use a grid layout for better button visibility and wrapping
        max_cols = 3
        for idx, (text, command, color) in enumerate(stat_buttons):
            row = idx // max_cols
            col = idx % max_cols
            btn = tk.Button(button_frame, text=text, command=command, **button_style)
            btn.configure(bg=color)
            btn.grid(row=row, column=col, padx=6, pady=6, sticky="nsew")

        # Make columns expand equally
        for col in range(max_cols):
            button_frame.grid_columnconfigure(col, weight=1)

        # Add a visual separator
        sep = tk.Frame(self.stats_tab, height=2, bd=1, relief=tk.SUNKEN, bg="#444")
        sep.pack(fill=tk.X, padx=10, pady=(0, 10), side=tk.BOTTOM)

    def setup_combat_tab(self):
        """Set up the combat tab with improved layout and visuals."""
        # Main combat frame
        combat_main = tk.Frame(self.combat_tab, bg="black")
        combat_main.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Canvas for battle visualization
        self.canvas = tk.Canvas(
            combat_main,
            bg="black",
            width=600,
            height=400,
            highlightthickness=2,
            highlightbackground="#444"
        )
        self.canvas.grid(row=0, column=0, columnspan=2, sticky="nsew", padx=10, pady=10)

        # Enemy info panel (right)
        info_frame = tk.Frame(combat_main, bg="black")
        info_frame.grid(row=0, column=2, sticky="nsew", padx=(10, 0), pady=10)
        
        # Combo indicator (top part of info panel)
        combo_indicator = tk.Frame(info_frame, bg="#1a1a1a", relief=tk.RIDGE, bd=2)
        combo_indicator.pack(fill=tk.X, pady=(0, 5))
        
        combo_label = tk.Label(combo_indicator, text="COMBO", font=("Arial", 10, "bold"), 
                              fg="gold", bg="#1a1a1a")
        combo_label.pack(pady=2)
        
        self.combat_combo_sequence = tk.Label(combo_indicator, text="Ready", font=("Arial", 9), 
                                            fg="green", bg="#1a1a1a")
        self.combat_combo_sequence.pack(pady=2)
        
        self.combat_combo_progress = tk.Canvas(combo_indicator, height=20, bg="#333", 
                                             highlightthickness=0)
        self.combat_combo_progress.pack(fill=tk.X, padx=5, pady=2)
        
        # Enemy info panel
        self.enemy_info = tk.Text(
            info_frame,
            width=28,
            height=10,
            bg="#f8f8f8",
            fg="#222",
            font=("Segoe UI", 10),
            state="disabled",
            relief=tk.RIDGE,
            bd=2
        )
        self.enemy_info.pack(fill=tk.BOTH, expand=True)

        # Combat controls (bottom)
        control_frame = tk.Frame(combat_main, bg="#222")
        control_frame.grid(row=1, column=0, columnspan=3, sticky="ew", padx=10, pady=(0, 10))

        # Create styled combat buttons
        combat_buttons = [
            ("Attack", self.attack, "#d9534f"),
            ("Heal", self.heal, "#5cb85c"),
            ("Spawn Enemy", self.spawn_enemy, "#f0ad4e"),
            ("Cast Fireball", self.cast_fireball, "#ff7043"),
            ("Cast Ice Shard", self.cast_ice_shard, "#42a5f5"),
            ("Test Dual Wield", self.test_dual_wield, "#9c27b0"),
            ("Tick Status", self.tick_status_effects, "#bdb76b")
        ]
        for idx, (text, command, color) in enumerate(combat_buttons):
            btn = tk.Button(control_frame, text=text, command=command,
                            bg=color, fg="white", font=("Segoe UI", 11, "bold"),
                            activebackground="#444", activeforeground="cyan",
                            relief=tk.RAISED, bd=2, width=16, height=2)
            btn.grid(row=0, column=idx, padx=8, pady=8, sticky="nsew")

        # Make columns expand equally
        for idx in range(len(combat_buttons)):
            control_frame.grid_columnconfigure(idx, weight=1)

        # Configure grid weights for resizing
        combat_main.grid_rowconfigure(0, weight=1)
        combat_main.grid_columnconfigure(0, weight=3)
        combat_main.grid_columnconfigure(1, weight=0)
        combat_main.grid_columnconfigure(2, weight=1)

    def log_message(self, message, tag="info"):
        """Add a message to the log.

        Args:
            message: The message to log
            tag: The text tag for formatting
        """
        timestamp = time.strftime("%H:%M:%S")
        self.log.insert(tk.END, f"[{timestamp}] ", "info")
        self.log.insert(tk.END, f"{message}\n", tag)
        self.log.see(tk.END)

        # Also log to logger
        logger.info(message)

    def setup_game_state(self):
        """Set up the initial game state."""
        logger.info("Setting up game state")

        # Initialize AI system first
        ai_controller = None
        try:
            from game_sys.ai.ai_demo_integration import AIDemoController
            # Create a temporary combat service for AI controller
            temp_combat_service = CombatService()
            ai_controller = AIDemoController(temp_combat_service)
            self.ai_enabled = True
            logger.info("AI system initialized successfully")
        except ImportError as e:
            logger.warning(f"AI system not available: {e}")
            self.ai_enabled = False

        # Initialize combat service with AI controller
        self.combat_service = CombatService(ai_controller)
        
        # Update AI controller reference if we have one
        if ai_controller:
            ai_controller.combat_service = self.combat_service
            self.ai_controller = ai_controller
        else:
            self.ai_controller = None

        # Create player character
        from game_sys.character.leveling_manager import LevelingManager
        # Create player character with specific grade and rarity
        # Grade 5 = SIX (0-indexed), and LEGENDARY rarity should give stat boosts
        self.player = create_character(
            template_id="hero",
            level=1, grade=0, rarity="COMMON"
        )
        logger.info(f"Created player: {self.player.name}")
        self.log_message(f"Welcome, {self.player.name}!")

            # Initialize enchanting system for player
        if ENCHANTING_AVAILABLE:
                setattr(
                    self.player, 'enchanting_system', EnchantingSystem(self.player)
                )
                self.log_message("Enchanting system initialized!")

        self.update_char_info()
        # Show correct available stat points from config
        available_points = self.player.leveling_manager.calculate_stat_points_available(
                self.player
        )
        self.log_message(
                f"You have {available_points} stat points to allocate in the Leveling tab!",
                "info"
            )

        # Create enemy with random stats
        self.enemy = create_character(
            "dragon", level= 50, grade=0, rarity="COMMON"
        )
        if self.enemy:
            # Enable AI for the enemy
            if self.ai_enabled and self.ai_controller:
                ai_success = self.ai_controller.enable_ai_for_enemy(self.enemy)
                if ai_success:
                    self.log_message("AI enabled for enemy", "info")
                else:
                    self.log_message("Failed to enable AI for enemy", "combat")

            # Display enemy info with grade and rarity
            enemy_info = (
                f"A {self.enemy.name} appears! "
                f"(Level {getattr(self.enemy, 'level', 100)}, "
                f"Grade {getattr(self.enemy, 'grade', 7)+1}, "
                f"Rarity {getattr(self.enemy, 'rarity', 'DIVINE')})"
            )
            if self.ai_enabled:
                enemy_info += " [AI CONTROLLED]"
            self.log_message(enemy_info, "combat")
            self.update_enemy_info()
        else:
            logger.error("Failed to create enemy")

        # Draw game state
        self.draw_game_state()

        # Update inventory displays if available
        if hasattr(self, 'inventory_listbox'):
            self.update_inventory_display()
            self.update_equipment_display()
            
        # Update leveling display
        if hasattr(self, 'update_leveling_display'):
            self.update_leveling_display()

    def update_char_info(self):
        """Update the character info displays."""
        if not hasattr(self, 'player') or not self.player:
            return

        # Enable text widgets for updating
        self.basic_info.config(state="normal")
        self.detailed_stats.config(state="normal")
        if hasattr(self, 'status_effects_display'):
            self.status_effects_display.config(state="normal")

        # Clear current text
        self.basic_info.delete(1.0, tk.END)
        self.detailed_stats.delete(1.0, tk.END)
        if hasattr(self, 'status_effects_display'):
            self.status_effects_display.delete(1.0, tk.END)

        # Build basic character info text
        basic_info = f"Name: {self.player.name}\n"
        basic_info += f"Level: {self.player.level}\n"
        
        # Add grade and rarity if available, display grade name if possible
        grade_display = None
        if hasattr(self.player, 'grade'):
            grade_val = self.player.grade
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
            basic_info += f"Grade: {grade_display}\n"
        if hasattr(self.player, 'rarity'):
            basic_info += f"Rarity: {self.player.rarity}\n"
            
        health_val = f"{self.player.current_health:.2f}/"
        health_val += f"{self.player.max_health:.2f}"
        basic_info += f"Health: {health_val}\n"

        # Insert basic text
        self.basic_info.insert(tk.END, basic_info)

        # Build detailed character info
        detailed_info = f"== {self.player.name} ==\n"
        detailed_info += f"Level: {self.player.level}\n"
        
        # Add grade and rarity to detailed view as well
        if hasattr(self.player, 'grade'):
            grade_val = self.player.grade
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
            detailed_info += f"Grade: {grade_display}\n"
        if hasattr(self.player, 'rarity'):
            detailed_info += f"Rarity: {self.player.rarity}\n"
            
        detailed_info += f"Health: {health_val}\n"

        # Show all available base stats
        detailed_info += "\n=== BASE STATS ===\n"
        if hasattr(self.player, 'base_stats') and isinstance(self.player.base_stats, dict):
            from game_sys.config.config_manager import ConfigManager
            cfg = ConfigManager()
            stats_defaults = cfg.get('constants.stats_defaults', {})
            # Filter out non-stat meta keys and tidy formatting
            meta_keys = {"grade", "rarity", "skip_default_job", "max_targets", "level", "defense", "accuracy", "initiative", "magic_power", "parry_chance"}
            core_stats = []
            for raw_key, raw_val in sorted(self.player.base_stats.items()):
                key = str(raw_key).strip()
                if key in meta_keys or key.startswith("_") or key.lower() == "level":
                    continue
                core_stats.append((key, raw_val))

            # Build output, showing effective values when they differ
            for stat_name, base_val in core_stats:
                stat_key = stat_name.lower()
                display_name = stat_key.replace("_", " ").title()
                try:
                    if hasattr(self.player, "get_stat"):
                        effective_val = float(self.player.get_stat(stat_key))
                    else:
                        effective_val = float(base_val)
                except Exception:
                    effective_val = base_val

                # Special-case magic power: if base is tiny (<=1) but effective bigger, prefer effective
                if stat_key == "magic_power" and effective_val > base_val:
                    shown_val = effective_val
                else:
                    shown_val = base_val

                # If effective differs noticeably, show both
                detailed_info += f"  {display_name}: {effective_val:.2f}\n"

        # Show all derived/combat stats, grouped by category
        if hasattr(self.player, 'get_stat'):
            # --- Offensive Stats ---
            detailed_info += "\n=== OFFENSIVE STATS ===\n"
            offensive_stats = [
                ('Attack', 'attack'),
                ('Magic Power', 'magic_power'),
                ('Physical Damage', 'physical_damage'),
                ('Critical Chance', 'critical_chance'),
                ('Parry Chance', 'parry_chance'),
                ('Initiative', 'initiative'),
                ('Speed', 'speed'),
            ]
            for display_name, stat_name in offensive_stats:
                try:
                    value = self.player.get_stat(stat_name)
                    if 'chance' in stat_name:
                        detailed_info += f"  {display_name}: {float(value):.1%}\n"
                    else:
                        detailed_info += f"  {display_name}: {float(value):.2f}\n"
                except Exception:
                    detailed_info += f"  {display_name}: N/A\n"

            # --- Defensive Stats ---
            detailed_info += "\n=== DEFENSIVE STATS ===\n"
            # Revert to simple defense display (no formula breakdown)
            try:
                defense_val = self.player.get_stat('defense')
                detailed_info += f"  Defense: {defense_val:.2f}\n"
            except Exception:
                detailed_info += "  Defense: N/A\n"
            defensive_stats = [
                ('Block Chance', 'block_chance'),
                ('Dodge Chance', 'dodge_chance'),
                ('Magic Resistance', 'magic_resistance'),
                ('Damage Reduction', 'damage_reduction'),
            ]
            for display_name, stat_name in defensive_stats:
                try:
                    value = self.player.get_stat(stat_name)
                    if 'chance' in stat_name:
                        detailed_info += f"  {display_name}: {float(value):.1%}\n"
                    else:
                        detailed_info += f"  {display_name}: {float(value):.2f}\n"
                except Exception:
                    detailed_info += f"  {display_name}: N/A\n"

            # --- Regeneration Stats ---
            detailed_info += "\n=== REGENERATION ===\n"
            regen_stats = ['health_regeneration', 'mana_regeneration', 'stamina_regeneration']
            for stat_name in regen_stats:
                try:
                    value = self.player.get_stat(stat_name)
                except Exception:
                    value = None
                display_name = stat_name.replace('_', ' ').title()
                try:
                    if value is None:
                        detailed_info += f"  {display_name}: N/A\n"
                    else:
                        detailed_info += f"  {display_name}: {float(value):.3f}/sec\n"
                except (ValueError, TypeError):
                    detailed_info += f"  {display_name}: {value}\n"
        # Resource Stats (Derived)
        detailed_info += "\n=== RESOURCE STATS ===\n"
        resource_stats = [
            ('health', 'max_health', 'current_health'),
            ('mana', 'max_mana', 'current_mana'),
            ('stamina', 'max_stamina', 'current_stamina')
        ]
        for base_stat, max_attr, current_attr in resource_stats:
            if hasattr(self.player, 'get_stat'):
                max_val = self.player.get_stat(base_stat)
                current_val = getattr(self.player, current_attr, max_val)
                display_name = base_stat.replace('_', ' ').title()
                detailed_info += f"  {display_name}: {current_val:.0f}/{max_val:.0f}\n"

        # Defensive Stats (Derived)
        detailed_info += "\n=== DEFENSIVE STATS ===\n"
        defensive_stats = ['dodge_chance', 'block_chance', 'magic_resistance', 'damage_reduction']
        for stat_name in defensive_stats:
            if hasattr(self.player, 'get_stat'):
                value = self.player.get_stat(stat_name)
                display_name = stat_name.replace('_', ' ').title()
                if 'chance' in stat_name:
                    detailed_info += f"  {display_name}: {value:.1%}\n"
                else:
                    detailed_info += f"  {display_name}: {value:.2f}\n"

        # Regeneration Stats (Derived)
        detailed_info += "\n=== REGENERATION ===\n"
        regen_stats = ['health_regeneration', 'mana_regeneration', 'stamina_regeneration']
        for stat_name in regen_stats:
            if hasattr(self.player, 'get_stat'):
                value = self.player.get_stat(stat_name)
                display_name = stat_name.replace('_', ' ').title()
                detailed_info += f"  {display_name}: {value:.3f}/sec\n"

        # Special Stats
        detailed_info += "\n=== SPECIAL STATS ===\n"
        special_stats = ['critical_chance', 'luck_factor', 'physical_damage']
        for stat_name in special_stats:
            if hasattr(self.player, 'get_stat'):
                value = self.player.get_stat(stat_name)
                display_name = stat_name.replace('_', ' ').title()
                if 'chance' in stat_name:
                    detailed_info += f"  {display_name}: {value:.1%}\n"
                else:
                    detailed_info += f"  {display_name}: {value:.2f}\n"

        # Add equipment if available
        detailed_info += "\n=== EQUIPMENT ===\n"
        weapon = getattr(self.player, 'weapon', None)
        if weapon:
            detailed_info += f"  Weapon: {weapon.name}\n"
        else:
            detailed_info += "  Weapon: (None)\n"

        offhand = getattr(self.player, 'offhand', None)
        if offhand:
            detailed_info += f"  Offhand: {offhand.name}\n"
        else:
            detailed_info += "  Offhand: (None)\n"

        body_armor = getattr(self.player, 'equipped_body', None)
        if body_armor:
            detailed_info += f"  Body: {body_armor.name}\n"
        else:
            detailed_info += "  Body: (None)\n"

        # Add inventory if available
        detailed_info += "\nInventory:\n"
        if hasattr(self.player, 'inventory'):
            items = self.player.inventory.list_items()
            if items:
                detailed_info += f"Items ({len(items)}):\n"
                for item in items[:5]:  # Show first 5 items
                    detailed_info += f"  - {item.name}\n"
                if len(items) > 5:
                    detailed_info += f"  ... and {len(items) - 5} more\n"
            else:
                detailed_info += "Empty inventory\n"
        else:
            detailed_info += "(No inventory system)"

        # Insert detailed text
        self.detailed_stats.insert(tk.END, detailed_info)

        # Disable text widgets to make them read-only
        self.basic_info.config(state="disabled")
        self.detailed_stats.config(state="disabled")

    def update_enemy_info(self):
        """Update the enemy info display."""
        # Enable text widget for updating
        self.enemy_info.config(state="normal")

        if not hasattr(self, 'enemy') or not self.enemy:
            self.enemy_info.delete(1.0, tk.END)
            self.enemy_info.insert(tk.END, "No enemy present")
            self.enemy_info.config(state="disabled")
            return

        # Clear current text
        self.enemy_info.delete(1.0, tk.END)

        # Build enemy info text
        info = f"Enemy: {self.enemy.name}\n"
        
        # Add level, grade, and rarity if available
        if hasattr(self.enemy, 'level'):
            info += f"Level: {self.enemy.level}\n"
        if hasattr(self.enemy, 'grade'):
            grade_val = self.enemy.grade
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
        if hasattr(self.enemy, 'rarity'):
            info += f"Rarity: {self.enemy.rarity}\n"
            
        health_val = f"{self.enemy.current_health:.2f}/"
        health_val += f"{self.enemy.max_health:.2f}"
        info += f"Health: {health_val}\n"

        # Add BASE STATS section (from base_stats dictionary)
        if hasattr(self.enemy, 'base_stats'):
            info += "\n=== BASE STATS ===\n"
            
            # List of core stats to display
            rpg_stats = [
                'strength', 'dexterity', 'vitality', 'intelligence',
                'wisdom', 'constitution', 'luck', 
            ]
            
            # Display each base stat
            for stat in rpg_stats:
                if stat in self.enemy.base_stats:
                    value = self.enemy.base_stats[stat]
                    display_name = stat.replace('_', ' ').title()
                    info += f"  {display_name}: {value:.2f}\n"
        
        # Add COMBAT STATS section if get_stat method is available
        if hasattr(self.enemy, 'get_stat'):
            info += "\n=== COMBAT STATS ===\n"
            combat_stats = ['attack', 'defense', 'speed', 'magic_power', 'critical_chance', 'dodge_chance']
            
            for stat in combat_stats:
                try:
                    value = self.enemy.get_stat(stat)
                    display_name = stat.replace('_', ' ').title()
                    info += f"  {display_name}: {value:.1f}\n"
                except:
                    pass

        # Add resistances and weaknesses
        if hasattr(self.enemy, 'resistances') and self.enemy.resistances:
            info += "\nResistances:\n"
            for damage_type, value in self.enemy.resistances.items():
                info += f"  {damage_type.name}: {int(value * 100)}%\n"

        if hasattr(self.enemy, 'weaknesses') and self.enemy.weaknesses:
            info += "\nWeaknesses:\n"
            for damage_type, value in self.enemy.weaknesses.items():
                info += f"  {damage_type.name}: +{int(value * 100)}%\n"

        # Insert text
        self.enemy_info.insert(tk.END, info)

        # Disable text widget to make it read-only
        self.enemy_info.config(state="disabled")

    def view_inventory(self):
        """View player inventory."""
        if not hasattr(self, 'player') or not self.player:
            self.log_message("No player character available!")
            return

        if hasattr(self.player, 'inventory'):
            self.log_message("Opening inventory...")
            # Switch to inventory tab and update displays
            self.tab_control.select(self.inventory_tab)
            self.update_inventory_display()
            self.update_equipment_display()
        else:
            self.log_message("No inventory system available!")

    def level_up(self):
        """Level up the character."""
        if not hasattr(self, 'player') or not self.player:
            self.log_message("No player character available!")
            return

        old_level = self.player.level

        # Use leveling manager if available
        if hasattr(self.player, 'leveling_manager'):
            # Level up through the leveling manager - use gain_experience instead of level_up
            if hasattr(self.player.leveling_manager, 'gain_experience'):
                self.player.leveling_manager.gain_experience(self.player, self.player.leveling_manager._xp_for_next_level(self.player.level))
            else:
                self.player.level += 1

            # Check if level actually increased
            if self.player.level > old_level:
                # Award stat points for the level up (config-driven)
                points_gained = self.player.level - old_level
                if hasattr(self.player.leveling_manager, 'get_stat_points_per_level'):
                    points_per_level = self.player.leveling_manager.get_stat_points_per_level(self.player.level)
                else:
                    points_per_level = 3
                total_points = points_gained * points_per_level
                if hasattr(self.player.leveling_manager, 'add_stat_points'):
                    self.player.leveling_manager.add_stat_points(
                        self.player,
                        total_points
                    )
                msg = f"Level up! Now level {self.player.level} (+{total_points} stat points)!"
                self.log_message(msg, "info")
            else:
                self.player.level += 1
                if hasattr(self.player.leveling_manager, 'get_stat_points_per_level'):
                    points_per_level = self.player.leveling_manager.get_stat_points_per_level(self.player)
                else:
                    points_per_level = 4
                if hasattr(self.player.leveling_manager, 'add_stat_points'):
                    self.player.leveling_manager.add_stat_points(self.player, points_per_level)
                msg = f"Level up! Now level {self.player.level} (+{points_per_level} stat points)!"
                self.log_message(msg, "info")
        else:
            # Fallback: manual level up
            self.player.level += 1

            # Increase base stats manually
            if hasattr(self.player, 'base_stats'):
                stat_increases = {
                    'attack': 2,
                    'defense': 2,
                    'speed': 1,
                    'health': 15,
                    'mana': 8,
                    'stamina': 5,
                    'magic_power': 2,
                    'intelligence': 2,
                    'strength': 2,
                    'dexterity': 1,
                    'vitality': 2,
                    'wisdom': 1,
                    'constitution': 2,
                    'luck': 1
                }
                for stat, increase in stat_increases.items():
                    if stat in self.player.base_stats:
                        self.player.base_stats[stat] += increase

            msg = f"Level up! You are now level {self.player.level}!"
            self.log_message(msg, "info")

        # Force stat recalculation
        if hasattr(self.player, 'update_stats'):
            self.player.update_stats()

        # Full restore on level up
        if hasattr(self.player, 'max_health'):
            self.player.current_health = self.player.max_health
        if hasattr(self.player, 'max_mana'):
            self.player.current_mana = self.player.max_mana
        if hasattr(self.player, 'max_stamina'):
            self.player.current_stamina = self.player.max_stamina

        # Update displays - ensure level is reflected in all UI components
        self.update_char_info()
        if hasattr(self, 'update_leveling_display'):
            self.update_leveling_display()
        if hasattr(self, 'update_progression_display'):
            self.update_progression_display()  # Make sure progression tab is updated too

    def equip_gear(self):
        """Equip gear on the character."""
        if not hasattr(self, 'player') or not self.player:
            self.log_message("No player character available!")
            return

        # Switch to inventory tab where equipment can be managed
        self.log_message("Opening inventory for equipment management...")
        self.tab_control.select(self.inventory_tab)
        self.update_inventory_display()
        self.update_equipment_display()

    def cast_fireball(self):
        """Cast fireball spell at the enemy."""
        if not SPELLS_AVAILABLE:
            self.log_message("Spell system not available!", "combat")
            return

        if not hasattr(self, 'player') or not self.player:
            self.log_message("No player character available!")
            return

        if not hasattr(self, 'enemy') or not self.enemy:
            self.log_message("No enemy to target!", "combat")
            return

        # Track combo sequence
        self.track_spell_cast("fireball")
        
        # Use combat service to cast the spell
        result = self.combat_service.cast_spell_at_target(
            self.player, "fireball", self.enemy
        )
        
        if result['success']:
            # Log the spell cast
            spell_msg = (f"{self.player.name} casts Fireball for "
                        f"{result['damage']:.0f} FIRE damage!")
            self.log_message(spell_msg, "combat")
            
            # Display resistance/weakness messages from combat engine
            if result.get('resistance_messages'):
                for message in result['resistance_messages']:
                    self.log_message(message, "combat")
            
            # Log effects if any were applied
            if result.get('effects_applied'):
                for effect in result['effects_applied']:
                    self.log_message(f"Applied {effect} effect!", "combat")
            
            # Create visual effect
            self.create_particles(450, 200, "orange", 25)
            
            # Handle enemy defeat and loot
            if result['defeated']:
                self.log_message(f"{self.enemy.name} is defeated by fire magic!", "combat")
                
                # Display loot if any was generated
                if result['loot']:
                    loot_names = [item.name for item in result['loot']]
                    loot_msg = f"Loot obtained: {', '.join(loot_names)}"
                    self.log_message(loot_msg, "info")
                
                self.enemy = None
        else:
            self.log_message(result['message'], "combat")

        # Update displays
        self.update_char_info()
        self.update_enemy_info()
        self.draw_game_state()

    def cast_ice_shard(self):
        """Cast ice shard spell at the enemy."""
        if not SPELLS_AVAILABLE:
            self.log_message("Spell system not available!", "combat")
            return

        if not hasattr(self, 'player') or not self.player:
            self.log_message("No player character available!")
            return

        if not hasattr(self, 'enemy') or not self.enemy:
            self.log_message("No enemy to target!", "combat")
            return

        # Track combo sequence
        self.track_spell_cast("ice_shard")
        
        # Use combat service to cast ice shard
        result = self.combat_service.cast_spell_at_target(self.player, "ice_shard", self.enemy)
        
        if result['success']:
            # Log spell cast
            self.log_message(result['message'], "combat")
            
            # Display resistance/weakness messages from combat engine
            if result.get('resistance_messages'):
                for message in result['resistance_messages']:
                    self.log_message(message, "combat")
            
            # Display effects applied
            if result.get('effects_applied'):
                for effect_msg in result['effects_applied']:
                    self.log_message(effect_msg, "combat")
            
            # Create visual effect
            self.create_particles(450, 200, "cyan", 20)
            
            # Handle enemy defeat and loot
            if result['defeated']:
                enemy_name = self.enemy.name
                self.log_message(f"{enemy_name} is frozen solid and defeated!", "combat")
                
                # Display loot if any
                if result['loot']:
                    loot_names = [getattr(item, 'name', str(item)) for item in result['loot']]
                    self.log_message(f"Loot found: {', '.join(loot_names)}", "loot")
                
                self.enemy = None
        else:
            self.log_message(result['message'], "combat")

        # Update displays
        self.update_char_info()
        self.update_enemy_info()
        self.draw_game_state()

    def draw_game_state(self):
        """Draw the current game state on the canvas."""
        # Clear canvas
        self.canvas.delete("all")

        # Draw player if exists
        if hasattr(self, 'player') and self.player:
            player_x, player_y = 150, 200

            # Draw player circle
            self.canvas.create_oval(
                player_x - 30, player_y - 30,
                player_x + 30, player_y + 30,
                fill="green", outline="white"
            )

            # Draw player name
            self.canvas.create_text(
                player_x, player_y - 50,
                text=self.player.name,
                fill="white", font=("Arial", 14)
            )

            # Draw health bar
            health_pct = self.player.current_health / self.player.max_health
            bar_width = 100
            bar_y = player_y + 40
            bar_height = 10

            # Health background
            self.canvas.create_rectangle(
                player_x - bar_width/2, bar_y,
                player_x + bar_width/2, bar_y + bar_height,
                fill="gray", outline="white"
            )
            # Health
            self.canvas.create_rectangle(
                player_x - bar_width/2, bar_y,
                player_x - bar_width/2 + bar_width * health_pct, bar_y + bar_height,
                fill="red", outline=""
            )
            # Health label
            self.canvas.create_text(
                player_x, bar_y + bar_height/2,
                text=f"HP: {int(self.player.current_health)}/{int(self.player.max_health)}",
                fill="white", font=("Arial", 9)
            )

            # Draw mana bar below health
            mana_pct = 0
            if hasattr(self.player, 'current_mana') and hasattr(self.player, 'max_mana') and self.player.max_mana > 0:
                mana_pct = self.player.current_mana / self.player.max_mana
            mana_y = bar_y + bar_height + 4
            self.canvas.create_rectangle(
                player_x - bar_width/2, mana_y,
                player_x + bar_width/2, mana_y + bar_height,
                fill="#224488", outline="white"
            )
            self.canvas.create_rectangle(
                player_x - bar_width/2, mana_y,
                player_x - bar_width/2 + bar_width * mana_pct, mana_y + bar_height,
                fill="#3399ff", outline=""
            )
            self.canvas.create_text(
                player_x, mana_y + bar_height/2,
                text=f"MP: {int(getattr(self.player, 'current_mana', 0))}/{int(getattr(self.player, 'max_mana', 0))}",
                fill="white", font=("Arial", 9)
            )

            # Draw stamina bar below mana
            stamina_pct = 0
            if hasattr(self.player, 'current_stamina') and hasattr(self.player, 'max_stamina') and self.player.max_stamina > 0:
                stamina_pct = self.player.current_stamina / self.player.max_stamina
            stamina_y = mana_y + bar_height + 4
            self.canvas.create_rectangle(
                player_x - bar_width/2, stamina_y,
                player_x + bar_width/2, stamina_y + bar_height,
                fill="#555522", outline="white"
            )
            self.canvas.create_rectangle(
                player_x - bar_width/2, stamina_y,
                player_x - bar_width/2 + bar_width * stamina_pct, stamina_y + bar_height,
                fill="#f7e359", outline=""
            )
            self.canvas.create_text(
                player_x, stamina_y + bar_height/2,
                text=f"SP: {int(getattr(self.player, 'current_stamina', 0))}/{int(getattr(self.player, 'max_stamina', 0))}",
                fill="black", font=("Arial", 9)
            )

        # Draw enemy if exists
        if hasattr(self, 'enemy') and self.enemy:
            enemy_x, enemy_y = 450, 200

            # Draw enemy circle
            self.canvas.create_oval(
                enemy_x - 30, enemy_y - 30,
                enemy_x + 30, enemy_y + 30,
                fill="red", outline="white"
            )

            # Draw enemy name
            self.canvas.create_text(
                enemy_x, enemy_y - 50,
                text=self.enemy.name,
                fill="white", font=("Arial", 14)
            )

            # Draw health bar
            health_pct = self.enemy.current_health / self.enemy.max_health if self.enemy.max_health > 0 else 0
            bar_width = 100
            bar_y = enemy_y + 40
            bar_height = 10

            # Health background
            self.canvas.create_rectangle(
                enemy_x - bar_width/2, bar_y,
                enemy_x + bar_width/2, bar_y + bar_height,
                fill="gray", outline="white"
            )
            # Health
            self.canvas.create_rectangle(
                enemy_x - bar_width/2, bar_y,
                enemy_x - bar_width/2 + bar_width * health_pct, bar_y + bar_height,
                fill="red", outline=""
            )
            # Health label
            self.canvas.create_text(
                enemy_x, bar_y + bar_height/2,
                text=f"HP: {int(getattr(self.enemy, 'current_health', 0))}/{int(getattr(self.enemy, 'max_health', 0))}",
                fill="white", font=("Arial", 9)
            )

            # Draw mana bar below health
            mana_pct = 0
            if hasattr(self.enemy, 'current_mana') and hasattr(self.enemy, 'max_mana') and self.enemy.max_mana > 0:
                mana_pct = self.enemy.current_mana / self.enemy.max_mana
            mana_y = bar_y + bar_height + 4
            self.canvas.create_rectangle(
                enemy_x - bar_width/2, mana_y,
                enemy_x + bar_width/2, mana_y + bar_height,
                fill="#224488", outline="white"
            )
            self.canvas.create_rectangle(
                enemy_x - bar_width/2, mana_y,
                enemy_x - bar_width/2 + bar_width * mana_pct, mana_y + bar_height,
                fill="#3399ff", outline=""
            )
            self.canvas.create_text(
                enemy_x, mana_y + bar_height/2,
                text=f"MP: {int(getattr(self.enemy, 'current_mana', 0))}/{int(getattr(self.enemy, 'max_mana', 0))}",
                fill="white", font=("Arial", 9)
            )

            # Draw stamina bar below mana
            stamina_pct = 0
            if hasattr(self.enemy, 'current_stamina') and hasattr(self.enemy, 'max_stamina') and self.enemy.max_stamina > 0:
                stamina_pct = self.enemy.current_stamina / self.enemy.max_stamina
            stamina_y = mana_y + bar_height + 4
            self.canvas.create_rectangle(
                enemy_x - bar_width/2, stamina_y,
                enemy_x + bar_width/2, stamina_y + bar_height,
                fill="#555522", outline="white"
            )
            self.canvas.create_rectangle(
                enemy_x - bar_width/2, stamina_y,
                enemy_x - bar_width/2 + bar_width * stamina_pct, stamina_y + bar_height,
                fill="#f7e359", outline=""
            )
            self.canvas.create_text(
                enemy_x, stamina_y + bar_height/2,
                text=f"SP: {int(getattr(self.enemy, 'current_stamina', 0))}/{int(getattr(self.enemy, 'max_stamina', 0))}",
                fill="black", font=("Arial", 9)
            )

        # Draw dividing line
        self.canvas.create_line(
            300, 100, 300, 300,
            fill="white", dash=(4, 4)
        )

        # Switch to combat tab to show the updated state
        self.tab_control.select(self.combat_tab)

    def create_particles(self, x, y, color, count=10):
        """Create particle effects.

        Args:
            x: X position
            y: Y position
            color: Particle color
            count: Number of particles
        """
        particles = []

        # Create particles
        for _ in range(count):
            angle = random.uniform(0, math.pi * 2)
            speed = random.uniform(1, 3)
            size = random.uniform(2, 5)

            particle = {
                'id': self.canvas.create_oval(
                    x - size, y - size,
                    x + size, y + size,
                    fill=color, outline=""
                ),
                'vx': math.cos(angle) * speed,
                'vy': math.sin(angle) * speed,
                'frames': 20
            }

            particles.append(particle)

        # Animate particles
        def update_particles():
            if not particles:
                return

            for p in particles[:]:
                # Update position
                self.canvas.move(p['id'], p['vx'], p['vy'])

                # Update lifetime
                p['frames'] -= 1
                if p['frames'] <= 0:
                    self.canvas.delete(p['id'])
                    particles.remove(p)

            # Continue animation if particles remain
            if particles:
                self.root.after(50, update_particles)

        # Start animation
        update_particles()

    def attack(self):
        """Attack the enemy."""
        if not hasattr(self, 'player') or not self.player:
            logger.warning("No player to attack with")
            return
        if not hasattr(self, 'enemy') or not self.enemy:
            logger.warning("No enemy to attack")
            self.log_message("No enemy to attack!", "combat")
            return

        # Use combat service to perform the attack
        result = self.combat_service.perform_attack(
            self.player, self.enemy, self.player.weapon
        )

        if result['success']:
            # Log the attack result
            weapon_info = ""
            if hasattr(self.player, 'weapon') and self.player.weapon:
                weapon_info = f" with {self.player.weapon.name}"
            damage_msg = (f"{self.player.name} attacks {self.enemy.name}{weapon_info} "
                         f"for {result['damage']:.0f} damage!")
            self.log_message(damage_msg, "combat")

            # Display resistance/weakness messages from combat engine
            if result.get('resistance_messages'):
                for message in result['resistance_messages']:
                    self.log_message(message, "combat")

            # Create visual effect
            self.create_particles(450, 200, "red", 15)

            # Handle enemy defeat and loot
            if result['defeated']:
                self.log_message(f"{self.enemy.name} is defeated!", "combat")
                if result['loot']:
                    loot_names = [item.name for item in result['loot']]
                    loot_msg = f"Loot obtained: {', '.join(loot_names)}"
                    self.log_message(loot_msg, "info")
                self.enemy = None
            else:
                # If enemy is still alive and AI is enabled, let AI take its turn
                if self.ai_enabled and self.ai_controller and self.enemy:
                    try:
                        self.ai_controller.process_ai_turn(self.enemy, self.player, 0.0)
                    except Exception as e:
                        logger.warning(f"AI turn failed: {e}")
        else:
            # Attack failed
            self.log_message(f"Attack failed: {result['message']}", "combat")

        # Update displays
        self.update_enemy_info()
        self.draw_game_state()

    def heal(self):
        """Heal the player."""
        if not hasattr(self, 'player') or not self.player:
            logger.warning("No player to heal")
            return

        # Use combat service for healing
        heal_amount = random.randint(5, 15)
        result = self.combat_service.apply_healing(
            self.player, self.player, heal_amount
        )
        
        if result['success']:
            self.log_message(f"You are healed for {result['healing']:.0f} health!", "heal")
        else:
            self.log_message(f"Healing failed: {result['message']}", "combat")

        # Create visual effect
        self.create_particles(150, 200, "green", 15)

        # Update displays
        self.update_char_info()
        self.draw_game_state()

    def spawn_enemy(self):
        """Spawn a new enemy."""
        enemy_types = ["goblin", "orc", "dragon"]
        enemy_type = random.choice(enemy_types)

        logger.info(f"Spawning {enemy_type}")

        # Create enemy with random stats
        self.enemy = create_character_with_random_stats(enemy_type)

        # Enable AI for the spawned enemy if AI is available
        if self.enemy and getattr(self, 'ai_enabled', False) and getattr(self, 'ai_controller', None):
            ai_success = self.ai_controller.enable_ai_for_enemy(self.enemy)
            if ai_success:
                self.log_message(f"AI enabled for {self.enemy.name}", "info")
            else:
                self.log_message(f"Failed to enable AI for {self.enemy.name}", "combat")

        if self.enemy:
            logger.info(f"Created enemy: {self.enemy.name}")
            
            # Display enemy info with grade and rarity
            enemy_info = (f"A {self.enemy.name} appears! "
                         f"(Level {self.enemy.level}, "
                         f"Grade {self.enemy.grade}, "
                         f"Rarity {self.enemy.rarity})")
            self.log_message(enemy_info, "combat")

            # Create visual effect
            self.create_particles(450, 200, "blue", 15)

            # Display resistances/weaknesses if the enemy has any
            if hasattr(self.enemy, 'resistances') and self.enemy.resistances:
                resistance_info = []
                for damage_type, value in self.enemy.resistances.items():
                    resistance_info.append(f"{damage_type.name} ({int(value*100)}%)")
                
                if resistance_info:
                    msg = f"{self.enemy.name} resists: {', '.join(resistance_info)}"
                    self.log_message(msg, "combat")
                    
            if hasattr(self.enemy, 'weaknesses') and self.enemy.weaknesses:
                weakness_info = []
                for damage_type, value in self.enemy.weaknesses.items():
                    weakness_info.append(f"{damage_type.name} ({int(value*100)}%)")
                
                if weakness_info:
                    msg = f"{self.enemy.name} is weak to: {', '.join(weakness_info)}"
                    self.log_message(msg, "combat")

            # Update displays
            self.update_enemy_info()
            self.draw_game_state()
        else:
            logger.error(f"Failed to create {enemy_type}")
            self.log_message(f"Failed to spawn {enemy_type}!", "combat")

    def test_dual_wield(self):
        """Test dual wielding functionality."""
        if not hasattr(self, 'player') or not self.player:
            self.log_message("No player available for dual wield test!", "combat")
            return

        try:
            from game_sys.items.factory import ItemFactory
            
            self.log_message("=== Dual Wield Test ===", "info")
            
            # Check current equipment
            current_weapon = getattr(self.player, 'weapon', None)
            current_offhand = getattr(self.player, 'offhand', None)
            
            self.log_message(f"Current weapon: {current_weapon.name if current_weapon else 'None'}", "info")
            self.log_message(f"Current offhand: {current_offhand.name if current_offhand else 'None'}", "info")
            
            # Try to equip dual-wieldable weapons
            try:
                # Create two daggers for dual wielding
                main_dagger = ItemFactory.create('iron_dagger')
                offhand_dagger = ItemFactory.create('iron_dagger')
                
                # Check if items were created successfully
                if not main_dagger or not offhand_dagger:
                    self.log_message("Failed to create dual-wield weapons", "combat")
                    return
                
                # Check dual_wield property
                main_dual_wield = getattr(main_dagger, 'dual_wield', False)
                offhand_dual_wield = getattr(offhand_dagger, 'dual_wield', False)
                
                self.log_message(f"Main dagger dual_wield: {main_dual_wield}", "info")
                self.log_message(f"Offhand dagger dual_wield: {offhand_dual_wield}", "info")
                
                if not main_dual_wield or not offhand_dual_wield:
                    self.log_message("Warning: Daggers may not be configured for dual wielding", "combat")
                
                # Try to equip main hand weapon
                success = self.player.equip_weapon(main_dagger)
                if success:
                    self.log_message(f"✓ Equipped {main_dagger.name} in main hand", "info")
                else:
                    self.log_message(f"✗ Failed to equip {main_dagger.name} in main hand", "combat")
                    return
                
                # Try to equip offhand weapon
                success = self.player.equip_offhand(offhand_dagger)
                if success:
                    self.log_message(f"✓ Equipped {offhand_dagger.name} in offhand", "info")
                    self.log_message("✓ Dual wielding setup complete!", "info")
                    
                    # Show dual wield stats
                    main_attack = getattr(main_dagger, 'attack', 0)
                    offhand_attack = getattr(offhand_dagger, 'attack', 0)
                    total_attack = main_attack + offhand_attack
                    
                    self.log_message(f"Main hand attack: {main_attack}", "info")
                    self.log_message(f"Offhand attack: {offhand_attack}", "info") 
                    self.log_message(f"Combined attack power: {total_attack}", "info")
                    
                    # Test combat with dual wielding
                    if hasattr(self, 'enemy') and self.enemy:
                        self.log_message("Testing dual wield attack...", "info")
                        self.attack()
                    else:
                        self.log_message("Spawn an enemy to test dual wield combat!", "info")
                        
                else:
                    self.log_message(f"✗ Failed to equip {offhand_dagger.name} in offhand", "combat")
                    
            except Exception as e:
                self.log_message(f"Error creating dual wield weapons: {e}", "combat")
                
        except Exception as e:
            self.log_message(f"Dual wield test failed: {e}", "combat")
            logger.error(f"Dual wield test error: {e}")
        
        # Update displays
        self.update_char_info()
        self.draw_game_state()

    def quit(self):
        """Quit the demo."""
        logger.info("Exiting demo")
        self.root.destroy()

    def reload_game(self):
        """Reload the game state without restarting the application."""
        logger.info("Reloading game state...")
        # Remove current player/enemy and re-initialize game state
        self.player = None
        self.enemy = None
        self.setup_game_state()
        self.log_message("Game state reloaded!", "info")

    def run(self):
        """Run the demo."""
        logger.info("Starting demo")

        # Add reload and quit buttons to main window
        button_frame = tk.Frame(self.root)
        button_frame.pack(side=tk.BOTTOM, pady=5)

        reload_btn = tk.Button(button_frame, text="Reload Game", command=self.reload_game)
        reload_btn.pack(side=tk.LEFT, padx=10)

        quit_btn = tk.Button(button_frame, text="Quit Game", command=self.quit)
        quit_btn.pack(side=tk.LEFT, padx=10)

        self.root.mainloop()
        logger.info("Demo ended")

    def on_tab_changed(self, event):
        """Handle tab change events to update displays."""
        selected_tab = event.widget.tab('current')['text']

        if selected_tab == "Character Stats":
            self.update_char_info()
        elif selected_tab == "Inventory":
            if hasattr(self, 'update_inventory_display'):
                self.update_inventory_display()
            if hasattr(self, 'update_equipment_display'):
                self.update_equipment_display()
        elif selected_tab == "Combat":
            self.update_enemy_info()
            self.draw_game_state()
        elif selected_tab == "Leveling":
            self.update_leveling_display()  # Update leveling tab display
        elif selected_tab == "Enchanting":
            self.refresh_enchanting_lists()  # Update enchanting tab display
        elif selected_tab == "Progression":
            self.update_progression_display()  # Update progression tab display
        elif selected_tab == "Settings":
            pass  # Currently nothing dynamic to refresh for settings

            self.update_progression_display()  # Update progression tab display

    def setup_inventory_tab(self):
        """Set up the inventory management tab."""
        # Main inventory frame
        main_inv_frame = tk.Frame(self.inventory_tab, bg="black")
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
        self.inventory_listbox = tk.Listbox(
            left_inv_frame,
            bg="light gray",
            fg="black",
            height=15,
            width=40
        )
        self.inventory_listbox.pack(fill=tk.BOTH, expand=True, pady=5)

        # Inventory item details
        self.item_details = tk.Text(
            left_inv_frame,
            bg="light gray",
            fg="black",
            height=5,
            width=40,
            state="disabled"
        )
        self.item_details.pack(fill=tk.X, pady=5)

        # Bind listbox selection
        self.inventory_listbox.bind('<<ListboxSelect>>', self.on_inventory_select)

        # Middle: Inventory actions
        middle_inv_frame = tk.Frame(main_inv_frame, bg="black")
        middle_inv_frame.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=20)

        inventory_buttons = [
            ("Use Item", self.use_selected_item),
            ("Equip Item", self.equip_selected_item),
            ("Drop Item", self.drop_selected_item),
            ("", None),  # Spacer
            ("Create Item", self.create_item_dialog),
            ("Add Random Item", self.add_random_item),
            ("", None),  # Spacer
            ("Unequip Weapon", lambda: self.unequip_item("weapon")),
            ("Unequip Armor", lambda: self.unequip_item("body")),
            ("Unequip Offhand", lambda: self.unequip_item("offhand")),
        ]

        for text, command in inventory_buttons:
            if text == "":  # Spacer
                spacer = tk.Label(middle_inv_frame, text="", bg="black", height=1)
                spacer.pack(pady=5)
            else:
                btn = tk.Button(
                    middle_inv_frame,
                    text=text,
                    command=command,
                    width=15
                )
                btn.pack(pady=5)

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
        self.equipment_display = tk.Text(
            right_inv_frame,
            bg="light gray",
            fg="black",
            height=10,
            width=30,
            state="disabled"
        )
        self.equipment_display.pack(fill=tk.X, pady=5)

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
        self.available_items_listbox = tk.Listbox(
            right_inv_frame,
            bg="light gray",
            fg="black",
            height=10,
            width=30
        )
        self.available_items_listbox.pack(fill=tk.X, pady=5)

        # Populate available items
        self.populate_available_items()

    def populate_available_items(self):
        """Populate the list of items that can be created."""
        if not ITEMS_AVAILABLE:
            self.available_items_listbox.insert(tk.END, "Items system not available")
            return

        # Get all available items from the JSON data
        available_items = [
            # Consumables
            "potion_health",
            "potion_mana",

            # Weapons
            "iron_sword",
            "wooden_stick",
            "orc_axe",
            "dragon_claw",
            "vampiric_blade",

            # Two-handed weapons
            "apprentice_staff",
            "arcane_staff",

            # Offhand weapons & shields
            "iron_dagger",
            "wooden_shield",
            "spell_focus",
            "arcane_focus",

            # Armor
            "leather_armor",
            "basic_clothes",
            "mage_robes",
            "archmage_robes",
            "dragon_scale_armor",
            "thornmail_armor",
            "boots_of_speed",
            "cloak_of_fortune",

            # Accessories
            "ring_of_power",

            # Enchantments
            "fire_enchant",
            "ice_enchant",
            "lightning_enchant",
            "poison_enchant",
            "strength_enchant",
            "speed_enchant"
        ]

        for item_id in available_items:
            self.available_items_listbox.insert(tk.END, item_id)

    def on_inventory_select(self, event):
        """Handle inventory item selection."""
        selection = self.inventory_listbox.curselection()

        # Enable text widget for updating
        self.item_details.config(state="normal")

        if not selection:
            self.item_details.delete(1.0, tk.END)
            self.item_details.config(state="disabled")
            return

        if not hasattr(self, 'player') or not self.player:
            self.item_details.delete(1.0, tk.END)
            self.item_details.insert(tk.END, "No player available")
            self.item_details.config(state="disabled")
            return

        if not hasattr(self.player, 'inventory'):
            self.item_details.delete(1.0, tk.END)
            self.item_details.insert(tk.END, "No inventory system available")
            self.item_details.config(state="disabled")
            return

        # Get selected item info
        try:
            items = self.player.inventory.list_items()
            if selection[0] < len(items):
                item = items[selection[0]]

                # Display item details
                self.item_details.delete(1.0, tk.END)
                details = f"Name: {item.name}\n"
                desc = getattr(item, 'description', 'N/A')
                details += f"Description: {desc}\n"
                details += f"Type: {type(item).__name__}\n"

                # Add item stats
                if hasattr(item, 'base_damage'):
                    details += f"Base Damage: {item.base_damage}\n"
                if hasattr(item, 'defense'):
                    details += f"Defense: {item.defense}\n"
                if hasattr(item, 'block_chance'):
                    details += f"Block Chance: {item.block_chance:.1%}\n"
                if hasattr(item, 'damage_type'):
                    details += f"Damage Type: {item.damage_type}\n"
                if hasattr(item, 'stats'):
                    details += "Stat Bonuses:\n"
                    for stat, value in item.stats.items():
                        # Format the value depending on its type
                        if isinstance(value, float) and 'chance' in stat:
                            formatted_value = f"{value:.1%}"  # Display as percentage
                        elif isinstance(value, float):
                            formatted_value = f"{value:.2f}"  # Display with 2 decimal places
                        else:
                            formatted_value = str(value)

                        details += f"  +{formatted_value} {stat.replace('_', ' ').title()}\n"

                # Show enchantments if the item has any
                if hasattr(item, 'enchantments') and item.enchantments:
                    details += "\nEnchantments:\n"
                    for enchant in item.enchantments:
                        details += f"  • {enchant.replace('_', ' ').title()}\n"

                # Add other properties
                if hasattr(item, 'slot'):
                    details += f"Slot: {item.slot}\n"
                if hasattr(item, 'level'):
                    details += f"Level: {item.level}\n"
                if hasattr(item, 'price'):
                    details += f"Price: {item.price}\n"
                if hasattr(item, 'dual_wield'):
                    if item.dual_wield:
                        details += "Can be dual wielded\n"
                if hasattr(item, 'effect_ids') and item.effect_ids:
                    details += f"Effects: {', '.join(item.effect_ids)}\n"

                self.item_details.insert(tk.END, details)
        except Exception as e:
            self.item_details.delete(1.0, tk.END)
            self.item_details.insert(tk.END, f"Error: {e}")

        # Disable text widget to make it read-only
        self.item_details.config(state="disabled")

    def create_item_dialog(self):
        """Open dialog to create an item."""
        if not ITEMS_AVAILABLE:
            self.log_message("Items system not available!", "combat")
            return

        selection = self.available_items_listbox.curselection()
        if not selection:
            msg = f"Please select an item to create from the available items list"

            self.log_message(msg, "info")
            return

        item_id = self.available_items_listbox.get(selection[0])
        self.create_and_add_item(item_id)

    def create_and_add_item(self, item_id):
        from game_sys.items.factory import ItemFactory
        """Create an item with a unique UUID and add it to the player's inventory (stackable)."""
        if not ITEMS_AVAILABLE:
            self.log_message("Items system not available!", "combat")
            return

        if not hasattr(self, 'player') or not self.player:
            self.log_message("No player character available!", "combat")
            return

        if not hasattr(self.player, 'inventory'):
            self.log_message("No inventory system available!", "combat")
            return

        try:
            # Create item instance
            item = ItemFactory.create(item_id)
            if not item:
                self.log_message(f"Failed to create item: {item_id}", "combat")
                return

            # Assign a unique UUID to the item
            import uuid
            item.uuid = str(uuid.uuid4())

            # Add item to player's inventory
            self.player.inventory.add_item(item)

            display_name = getattr(item, 'display_name', None) or getattr(item, 'name', None) or getattr(item, 'id', str(item))
            msg = f"Created and added {display_name} (UUID: {item.uuid}) to inventory!"
            self.log_message(msg, "info")

            # Update inventory display
            self.update_inventory_display()
        except Exception as e:
            self.log_message(f"Error creating item: {e}", "combat")

    def add_random_item(self):
        """Add a random item with a unique UUID to the player's inventory."""
        import random
        available_items = [
            "potion_health", "potion_mana", "iron_sword", "wooden_stick", "orc_axe", "dragon_claw",
            "vampiric_blade", "apprentice_staff", "arcane_staff", "iron_dagger", "wooden_shield",
            "spell_focus", "arcane_focus", "leather_armor", "basic_clothes", "mage_robes",
            "archmage_robes", "dragon_scale_armor", "thornmail_armor", "boots_of_speed",
            "cloak_of_fortune", "ring_of_power", "fire_enchant", "ice_enchant", "lightning_enchant",
            "poison_enchant", "strength_enchant", "speed_enchant"
        ]
        item_id = random.choice(available_items)
        self.create_and_add_item(item_id)
        item_count = len(available_items)
        random_index = random.randint(0, item_count - 1)
        item_id = available_items[random_index]
        self.create_and_add_item(item_id)

    def use_selected_item(self):
        """Use the selected inventory item."""
        selection = self.inventory_listbox.curselection()
        if not selection:
            self.log_message("Please select an item to use", "info")
            return

        if not hasattr(self, 'player') or not self.player:
            self.log_message("No player character available!", "combat")
            return

        if not hasattr(self.player, 'inventory'):
            self.log_message("No inventory system available!", "combat")
            return

        try:
            items = self.player.inventory.list_items()
            if selection[0] < len(items):
                item = items[selection[0]]
                display_name = getattr(item, 'display_name', None) or getattr(item, 'name', None) or getattr(item, 'id', str(item))

                # Check if item is consumable or has active abilities
                is_consumable = (
                    (hasattr(item, 'consumable') and item.consumable) or
                    (hasattr(item, 'item_type') and item.item_type == 'consumable') or
                    'potion' in display_name.lower()
                )

                has_active_ability = (
                    hasattr(item, 'use_action') or
                    hasattr(item, 'active_ability') or
                    hasattr(item, 'skill_id') or
                    hasattr(item, 'enchant_id')
                )

                if is_consumable or has_active_ability:
                    # Use the item
                    if hasattr(item, 'use_action'):
                        # Item has a use action method
                        item.use_action(self.player)
                        msg = f"Used {display_name} (UUID: {getattr(item, 'uuid', 'N/A')})!"
                    elif is_consumable:
                        # Basic consumable (e.g., health potion)
                        if 'health' in display_name.lower():
                            heal_amount = getattr(item, 'heal_amount', 25)
                            old_health = self.player.current_health
                            new_health = min(
                                self.player.current_health + heal_amount,
                                self.player.max_health
                            )
                            self.player.current_health = new_health
                            actual_heal = new_health - old_health
                            heal_val = f"+{actual_heal:.1f}HP"
                            heal_msg = f"Used {display_name} (UUID: {getattr(item, 'uuid', 'N/A')})! {heal_val}"
                            msg = heal_msg
                        else:
                            msg = f"Used {display_name} (UUID: {getattr(item, 'uuid', 'N/A')})! (simulated effect)"
                    else:
                        msg = f"Activated {display_name} (UUID: {getattr(item, 'uuid', 'N/A')})!"

                    self.log_message(msg, "heal")

                    # Remove consumable items from inventory
                    if is_consumable:
                        self.player.inventory.remove_item(item)

                    self.update_inventory_display()
                    self.update_char_info()
                else:
                    msg = f"Cannot use {display_name} (UUID: {getattr(item, 'uuid', 'N/A')}) - not consumable or usable"
                    self.log_message(msg, "info")
        except Exception as e:
            self.log_message(f"Error using item: {e}", "combat")

    def equip_selected_item(self):
        """Equip the selected item by UUID with proper slot validation and inventory manager integration."""
        
        if not ITEMS_AVAILABLE:
            self.log_message("Items system not available!", "combat")
            return
        from game_sys.logging import inventory_logger

        selection = self.inventory_listbox.curselection()
        if not selection:
            self.log_message("Please select an item to equip", "info")
            return
            
        if not hasattr(self, 'player') or not self.player:
            self.log_message("No player character available!", "combat")
            return
            
        if not hasattr(self.player, 'inventory'):
            self.log_message("No inventory system available!", "combat")
            return

        try:
            # Use inventory manager's list_items method
            items = self.player.inventory.list_items()
            if selection[0] >= len(items):
                self.log_message("Selected item is no longer available", "combat")
                return
                
            item = items[selection[0]]
            display_name = getattr(item, 'display_name', None) or getattr(item, 'name', None) or getattr(item, 'id', str(item))
            item_uuid = getattr(item, 'uuid', None)
            slot = getattr(item, 'slot', None)
            
            if not slot:
                self.log_message(f"Cannot equip {display_name} - no equipment slot defined", "combat")
                return
                
            # Check if slot is available based on equipment type
            slot_available = False
            conflict_message = None
            
            if slot == 'weapon':
                current_weapon = getattr(self.player, 'weapon', None)
                current_offhand = getattr(self.player, 'offhand', None)
                
                # Check if weapon slot is available
                if current_weapon is None:
                    slot_available = True
                else:
                    # Weapon slot occupied - check if it's a dual-wield scenario
                    if (hasattr(item, 'dual_wield') and item.dual_wield and 
                        hasattr(current_weapon, 'dual_wield') and current_weapon.dual_wield and
                        current_offhand is None):
                        # Both weapons are dual-wieldable and offhand is free
                        # Move current weapon to offhand and equip new weapon in main hand
                        slot_available = True
                        self.log_message(f"Moving {current_weapon.name} to offhand to make room for {display_name}", "info")
                    else:
                        slot_available = False
                        weapon_name = getattr(current_weapon, 'name', str(current_weapon))
                        if hasattr(item, 'dual_wield') and item.dual_wield:
                            if not (hasattr(current_weapon, 'dual_wield') and current_weapon.dual_wield):
                                conflict_message = f"Cannot dual-wield: {weapon_name} is not dual-wieldable"
                            elif current_offhand is not None:
                                offhand_name = getattr(current_offhand, 'name', str(current_offhand))
                                conflict_message = f"Cannot dual-wield: offhand occupied by {offhand_name}"
                            else:
                                conflict_message = f"Weapon slot occupied by {weapon_name}"
                        else:
                            conflict_message = f"Weapon slot occupied by {weapon_name}"
                    
            elif slot == 'offhand':
                current_offhand = getattr(self.player, 'offhand', None)
                current_weapon = getattr(self.player, 'weapon', None)
                
                # Special dual-wield logic
                if hasattr(item, 'dual_wield') and item.dual_wield:
                    # Dual-wield items can go in offhand if main hand is empty or also dual-wield
                    if current_weapon is None or (hasattr(current_weapon, 'dual_wield') and current_weapon.dual_wield):
                        slot_available = current_offhand is None
                        if not slot_available:
                            offhand_name = getattr(current_offhand, 'name', str(current_offhand))
                            conflict_message = f"Offhand slot occupied by {offhand_name}"
                    else:
                        weapon_name = getattr(current_weapon, 'name', str(current_weapon))
                        slot_available = False
                        conflict_message = f"Cannot dual-wield: main weapon {weapon_name} is not dual-wieldable"
                else:
                    # Regular offhand item (shield, focus, etc.)
                    slot_available = current_offhand is None
                    if not slot_available:
                        offhand_name = getattr(current_offhand, 'name', str(current_offhand))
                        conflict_message = f"Offhand slot occupied by {offhand_name}"
                        
            elif slot in ['body', 'helmet', 'legs', 'feet', 'gloves', 'boots', 'cloak']:
                slot_attr = f'equipped_{slot}'
                current_item = getattr(self.player, slot_attr, None)
                slot_available = current_item is None
                if not slot_available:
                    item_name = getattr(current_item, 'name', str(current_item))
                    conflict_message = f"{slot.title()} slot occupied by {item_name}"
            else:
                slot_available = False
                conflict_message = f"Unknown equipment slot: {slot}"
                
            if not slot_available:
                self.log_message(f"Cannot equip {display_name}: {conflict_message}", "combat")
                self.log_message("Use unequip buttons first to free up slots", "info")
                return
                
            # Attempt to equip using UUID-based method if available
            equipped_successfully = False
            weapon_moved_to_offhand = False
            
            # Check if we need to move current weapon to offhand for dual-wield
            if (slot == 'weapon' and slot_available and 
                hasattr(item, 'dual_wield') and item.dual_wield and
                getattr(self.player, 'weapon', None) is not None and
                getattr(self.player, 'offhand', None) is None):
                
                current_weapon = self.player.weapon
                if hasattr(current_weapon, 'dual_wield') and current_weapon.dual_wield:
                    # Move current weapon to offhand first
                    if hasattr(self.player, 'equip_offhand'):
                        try:
                            # Unequip current weapon without adding to inventory
                            self.player.weapon = None
                            # Equip it to offhand
                            self.player.equip_offhand(current_weapon)
                            weapon_moved_to_offhand = True
                            self.log_message(f"Moved {current_weapon.name} to offhand for dual-wielding", "info")
                        except Exception as e:
                            self.log_message(f"Failed to move weapon to offhand: {e}", "combat")
                            # Restore weapon if move failed
                            self.player.weapon = current_weapon
                            slot_available = False
            
            if slot_available and hasattr(self.player, 'equip_item_by_uuid') and item_uuid:
                # Preferred: Use UUID-based equipment
                success = self.player.equip_item_by_uuid(item_uuid)
                if success:
                    if weapon_moved_to_offhand:
                        self.log_message(f"Equipped {display_name} (UUID: {item_uuid}) - moved previous weapon to offhand for dual-wielding", "info")
                    else:
                        self.log_message(f"Equipped {display_name} (UUID: {item_uuid})", "info")
                    equipped_successfully = True
                    
                    # Remove item from inventory after successful equipment
                    removal_success = self.player.inventory.remove_item(item)
                    if not removal_success:
                        inventory_logger.warning(f"Failed to remove {display_name} from inventory after equipping")
                else:
                    self.log_message(f"Failed to equip {display_name} by UUID", "combat")
                    
            elif hasattr(self.player, 'equip_item') and item_uuid:
                # Alternative: Generic equip_item method with UUID
                success = self.player.equip_item(item_uuid)
                if success:
                    self.log_message(f"Equipped {display_name} (UUID: {item_uuid})", "info")
                    equipped_successfully = True
                    
                    # Remove item from inventory after successful equipment
                    removal_success = self.player.inventory.remove_item(item)
                    if not removal_success:
                        inventory_logger.warning(f"Failed to remove {display_name} from inventory after equipping")
                else:
                    self.log_message(f"Failed to equip {display_name} by UUID", "combat")
                    
            else:
                # Fallback: Direct slot-based equipment (legacy support)
                try:
                    if slot == 'weapon' and hasattr(self.player, 'equip_weapon'):
                        self.player.equip_weapon(item)
                        equipped_successfully = True
                    elif slot == 'offhand' and hasattr(self.player, 'equip_offhand'):
                        self.player.equip_offhand(item)
                        equipped_successfully = True
                    elif slot in ['body', 'helmet', 'legs', 'feet', 'gloves', 'boots', 'cloak'] and hasattr(self.player, 'equip_armor'):
                        self.player.equip_armor(item)
                        equipped_successfully = True
                    else:
                        self.log_message(f"No equipment method available for slot: {slot}", "combat")
                        
                    if equipped_successfully:
                        uuid_text = f" (UUID: {item_uuid})" if item_uuid else ""
                        if weapon_moved_to_offhand:
                            self.log_message(f"Equipped {display_name}{uuid_text} using fallback method (moved previous weapon to offhand for dual-wielding)", "info")
                        else:
                            self.log_message(f"Equipped {display_name}{uuid_text} using fallback method", "info")
                        
                        # Remove item from inventory after successful equipment
                        removal_success = self.player.inventory.remove_item(item)
                        if not removal_success:
                            inventory_logger.warning(f"Failed to remove {display_name} from inventory after equipping")
                        
                except Exception as e:
                    self.log_message(f"Fallback equipment failed: {e}", "combat")
                    
            # Update displays if equipment was successful
            if equipped_successfully:
                # Force stat recalculation to apply equipment bonuses
                if hasattr(self.player, 'update_stats'):
                    self.player.update_stats()
                    
                # Update all relevant displays
                self.update_inventory_display()
                self.update_equipment_display()
                self.update_char_info()
                
                # Show equipment stats if available
                if hasattr(item, 'stats') and item.stats:
                    stat_bonuses = []
                    for stat, value in item.stats.items():
                        if isinstance(value, float) and 'chance' in stat:
                            stat_bonuses.append(f"+{value:.1%} {stat.replace('_', ' ').title()}")
                        else:
                            stat_bonuses.append(f"+{value} {stat.replace('_', ' ').title()}")
                            
                    if stat_bonuses:
                        self.log_message(f"Equipment bonuses: {', '.join(stat_bonuses)}", "info")
            else:
                self.log_message(f"Failed to equip {display_name}", "combat")
                
        except Exception as e:
            self.log_message(f"Error equipping item: {e}", "combat")
            # Log additional debug info
            logger.error(f"Equipment error details: {e}")
            import traceback
            logger.error(traceback.format_exc())

    def drop_selected_item(self):
        """Drop (remove) the selected inventory item."""
        selection = self.inventory_listbox.curselection()
        if not selection:
            self.log_message("Please select an item to drop", "info")
            return

        if not hasattr(self, 'player') or not self.player:
            self.log_message("No player character available!", "combat")
            return

        if not hasattr(self.player, 'inventory'):
            self.log_message("No inventory system available!", "combat")
            return

        try:
            items = self.player.inventory.list_items()
            if selection[0] < len(items):
                item = items[selection[0]]
                display_name = getattr(item, 'display_name', None) or getattr(item, 'name', None) or getattr(item, 'id', str(item))
                success = self.player.inventory.remove_item(item)
                if success:
                    self.log_message(f"Dropped {display_name} (UUID: {getattr(item, 'uuid', 'N/A')})", "info")
                else:
                    self.log_message(f"Could not drop {display_name} (UUID: {getattr(item, 'uuid', 'N/A')})", "combat")
                self.update_inventory_display()
        except Exception as e:
            self.log_message(f"Error dropping item: {e}", "combat")

    def update_inventory_display(self):
        """Update the inventory display. Use display name, not item id."""
        if not hasattr(self, 'inventory_listbox'):
            return

        # Clear current display
        self.inventory_listbox.delete(0, tk.END)

        if not hasattr(self, 'player') or not self.player:
            self.inventory_listbox.insert(tk.END, "No player available")
            return

        if not hasattr(self.player, 'inventory'):
            self.inventory_listbox.insert(tk.END, "No inventory system")
            return

        try:
            # Get inventory items
            items = self.player.inventory.list_items()

            # Get list of currently equipped items to filter out
            equipped_items = set()

            # Check for equipped weapon
            if hasattr(self.player, 'weapon') and self.player.weapon:
                equipped_items.add(self.player.weapon)

            # Check for equipped offhand
            if hasattr(self.player, 'offhand') and self.player.offhand:
                equipped_items.add(self.player.offhand)

            # Check for equipped armor pieces
            armor_slots = ['body', 'helmet', 'legs', 'feet', 'gloves', 'boots', 'cloak']
            for slot in armor_slots:
                slot_attr = f'equipped_{slot}'
                if hasattr(self.player, slot_attr):
                    equipped_item = getattr(self.player, slot_attr)
                    if equipped_item:
                        equipped_items.add(equipped_item)

            # Filter out equipped items from inventory display
            unequipped_items = [item for item in items if item not in equipped_items]

            if not unequipped_items:
                self.inventory_listbox.insert(tk.END, "(Empty)")
                self.inventory_listbox.insert(tk.END, "")
                self.inventory_listbox.insert(tk.END, "Note: Starting equipment")
                self.inventory_listbox.insert(tk.END, "is automatically equipped")
                self.inventory_listbox.insert(tk.END, "and shown in equipment")
            else:
                for item in unequipped_items:
                    # Prefer display_name, fallback to name, then id
                    display_text = getattr(item, 'display_name', None) or getattr(item, 'name', None) or getattr(item, 'id', str(item))
                    self.inventory_listbox.insert(tk.END, display_text)
        except Exception as e:
            self.inventory_listbox.insert(tk.END, f"Error: {e}")

    def update_equipment_display(self):
        """Update the equipment display."""
        if not hasattr(self, 'equipment_display'):
            return

        # Enable text widget for updating
        self.equipment_display.config(state="normal")

        # Clear current display
        self.equipment_display.delete(1.0, tk.END)

        if not hasattr(self, 'player') or not self.player:
            self.equipment_display.insert(tk.END, "No player available")
            self.equipment_display.config(state="disabled")
            return

        if not hasattr(self.player, 'inventory'):
            self.equipment_display.insert(tk.END, "No inventory system")
            self.equipment_display.config(state="disabled")
            return

        try:
            # Show equipped items
            equipment_text = "== Equipped Items ==\n"

            # Check for weapon
            weapon = getattr(self.player, 'weapon', None)
            if weapon:
                equipment_text += f"Weapon: {weapon.name}\n"
            else:
                equipment_text += "Weapon: (None)\n"

            # Check for body armor
            body = getattr(self.player, 'equipped_body', None)
            if body:
                equipment_text += f"Body: {body.name}\n"
            else:
                equipment_text += "Body: (None)\n"

            # Check for helmet
            helmet = getattr(self.player, 'equipped_helmet', None)
            if helmet:
                equipment_text += f"Helmet: {helmet.name}\n"
            else:
                equipment_text += "Helmet: (None)\n"

            # Check for shield/offhand
            offhand = getattr(self.player, 'offhand', None)
            if not offhand:
                offhand = getattr(self.player, 'equipped_offhand', None)
            if offhand:
                equipment_text += f"Offhand: {offhand.name}\n"
            else:
                equipment_text += "Offhand: (None)\n"

            self.equipment_display.insert(tk.END, equipment_text)
        except Exception as e:
            self.equipment_display.insert(tk.END, f"Error: {e}")

        # Disable text widget to make it read-only
        self.equipment_display.config(state="disabled")

    def unequip_item(self, slot):
        """Unequip an item from the specified slot using UUID if possible."""
        if not hasattr(self, 'player') or not self.player:
            self.log_message("No player character available!", "combat")
            return
        try:
            # Use UUID-based unequip if available
            if hasattr(self.player, 'unequip_item_by_slot'):
                unequipped = self.player.unequip_item_by_slot(slot)
                if unequipped:
                    display_name = getattr(unequipped, 'display_name', None) or getattr(unequipped, 'name', None) or getattr(unequipped, 'id', str(unequipped))
                    msg = f"Unequipped {slot}: {display_name} (UUID: {getattr(unequipped, 'uuid', 'N/A')}) returned to inventory."
                    self.log_message(msg, "info")
                else:
                    self.log_message(f"No item equipped in {slot} slot.", "info")
            else:
                # Fallback to legacy slot-based unequip
                if slot == "weapon":
                    if hasattr(self.player, 'weapon') and self.player.weapon:
                        unequipped_weapon = self.player.unequip_weapon()
                        if unequipped_weapon:
                            msg = f"Unequipped weapon: {unequipped_weapon.name} (returned to inventory)"
                            self.log_message(msg, "info")
                        else:
                            self.log_message("Failed to unequip weapon", "combat")
                    else:
                        self.log_message("No weapon equipped", "info")
                elif slot == "offhand":
                    if hasattr(self.player, 'offhand') and self.player.offhand:
                        unequipped_offhand = self.player.unequip_offhand()
                        if unequipped_offhand:
                            msg = f"Unequipped offhand: {unequipped_offhand.name} (returned to inventory)"
                            self.log_message(msg, "info")
                        else:
                            self.log_message("Failed to unequip offhand", "combat")
                    else:
                        self.log_message("No offhand item equipped", "info")
                elif slot == "body":
                    if hasattr(self.player, 'unequip_armor'):
                        unequipped_item = self.player.unequip_armor("body")
                        if unequipped_item:
                            msg = f"Unequipped body armor: {unequipped_item.name} (returned to inventory)"
                            self.log_message(msg, "info")
                        else:
                            self.log_message("No body armor equipped", "info")
                    else:
                        self.log_message("Armor unequipping not implemented", "combat")
                else:
                    self.log_message(f"Unknown equipment slot: {slot}", "combat")
            # Update displays
            self.update_inventory_display()
            self.update_equipment_display()
            self.update_char_info()
        except Exception as e:
            self.log_message(f"Error unequipping {slot}: {e}", "combat")

    def restore_health(self):
        """Restore player's health to maximum."""
        if not hasattr(self, 'player') or not self.player:
            self.log_message("No player character available!")
            return

        if hasattr(self.player, 'max_health'):
            self.player.current_health = self.player.max_health
            self.log_message("Health fully restored!", "info")
            self.update_char_info()
        else:
            self.log_message("Player has no health system!", "error")

    def restore_mana(self):
        """Restore player's mana to maximum."""
        if not hasattr(self, 'player') or not self.player:
            self.log_message("No player character available!")
            return

        if hasattr(self.player, 'max_mana'):
            self.player.current_mana = self.player.max_mana
            self.log_message("Mana fully restored!", "info")
            self.update_char_info()
        else:
            self.log_message("Player has no mana system!", "error")

    def restore_stamina(self):
        """Restore player's stamina to maximum."""
        if not hasattr(self, 'player') or not self.player:
            self.log_message("No player character available!")
            return

        if hasattr(self.player, 'max_stamina'):
            self.player.current_stamina = self.player.max_stamina
            self.log_message("Stamina fully restored!", "info")
            self.update_char_info()
        else:
            self.log_message("Player has no stamina system!", "error")

    def restore_all_resources(self):
        """Restore all player resources to maximum."""
        if not hasattr(self, 'player') or not self.player:
            self.log_message("No player character available!")
            return

        restored = []

        if hasattr(self.player, 'restore_all'):
            # Use engine's restore_all method if available
            self.player.restore_all()
            restored.append("all resources")
        else:
            # Manual restoration
            if hasattr(self.player, 'max_health'):
                self.player.current_health = self.player.max_health
                restored.append("health")

            if hasattr(self.player, 'max_mana'):
                self.player.current_mana = self.player.max_mana
                restored.append("mana")

            if hasattr(self.player, 'max_stamina'):
                self.player.current_stamina = self.player.max_stamina
                restored.append("stamina")

        if restored:
            msg = f"Restored {', '.join(restored)}!"
            self.log_message(msg, "info")
            self.update_char_info()
        else:
            self.log_message("No resources to restore!", "error")

    def tick_status_effects(self):
        """Manually tick status effects for demonstration."""
        if not hasattr(self, 'enemy') or not self.enemy:
            self.log_message("No enemy to tick status effects on!")
            return

        # Import the status manager to tick effects
        try:
            from game_sys.effects.status_manager import status_manager

            # Register the enemy if not already registered
            if self.enemy not in status_manager.actors:
                status_manager.register_actor(self.enemy)

            # Also register the player if they have status effects
            if hasattr(self, 'player') and self.player:
                if self.player not in status_manager.actors:
                    status_manager.register_actor(self.player)

            # Tick status effects for 1 second
            dt = 1.0
            old_health = self.enemy.current_health
            status_manager.tick(dt)
            new_health = self.enemy.current_health

            damage_dealt = old_health - new_health
            if damage_dealt > 0:
                self.log_message(f"Status effects dealt {damage_dealt:.1f} damage!", "combat")

                # Check if enemy died from status effects
                if self.enemy.current_health <= 0:
                    self.log_message("Enemy defeated by status effects!", "combat")
                    self.enemy = None

                # Update displays after potential enemy death
                self.update_enemy_info()
                self.draw_game_state()
            else:
                self.log_message("Status effects ticked (no damage)", "info")

        except ImportError as e:
            self.log_message(f"Could not import status manager: {e}", "error")
        except Exception as e:
            self.log_message(f"Error ticking status effects: {e}", "error")

    def setup_leveling_tab(self):
        """Set up the leveling and stat allocation tab."""
        # Main container
        main_frame = tk.Frame(self.leveling_tab, bg="black")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Left side: Available stat points and current stats
        left_frame = tk.Frame(main_frame, bg="dark gray")
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))

        # Available points display
        points_frame = tk.Frame(left_frame, bg="dark gray")
        points_frame.pack(fill=tk.X, pady=(0, 10))

        # Create stat frame for allocatable stats
        stat_frame = tk.Frame(left_frame, bg="dark gray")

        tk.Label(
            points_frame,
            text="Available Stat Points:",
            bg="dark gray",
            fg="white",
            font=("Arial", 12, "bold")
        ).pack(anchor="w")

        self.available_points_label = tk.Label(
            points_frame,
            text="0",
            bg="dark gray",
            fg="yellow",
            font=("Arial", 14, "bold")
        )
        self.available_points_label.pack(anchor="w")
        
        stat_frame.pack(fill=tk.BOTH, expand=True)

        tk.Label(
            stat_frame,
            text="Allocatable Stats:",
            bg="dark gray",
            fg="white",
            font=("Arial", 12, "bold")
        ).pack(anchor="w", pady=(0, 5))

        self.allocatable_stats_text = tk.Text(
            stat_frame,
            bg="black",
            fg="white",
            font=("Courier", 10),
            height=15,
            state="disabled"
        )
        self.allocatable_stats_text.pack(fill=tk.BOTH, expand=True)

        # Right side: Stat allocation controls
        right_frame = tk.Frame(main_frame, bg="dark gray", relief="ridge", bd=2)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))

        # Add a scrollable frame for many stats
        canvas = tk.Canvas(right_frame, bg="dark gray", highlightthickness=0)
        scrollbar = tk.Scrollbar(right_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg="dark gray")

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # Pack scrollbar and canvas
        scrollbar.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)

        tk.Label(
            scrollable_frame,
            text="Allocate Stat Points:",
            bg="dark gray",
            fg="white",
            font=("Arial", 12, "bold")
        ).pack(anchor="w", pady=(10, 10), padx=5)

        # Stat allocation buttons - include all character stats
        self.stat_buttons = {}
        
        # Get allocatable stats from leveling manager if available
        if hasattr(self, 'player') and self.player and hasattr(self.player, 'leveling_manager'):
            # Use leveling manager's allocatable stats
            allocatable_stats = self.player.leveling_manager.get_allocatable_stats()
        else:
            # Fallback to traditional RPG stats only
            allocatable_stats = [
                'strength', 'dexterity', 'vitality', 'intelligence', 'wisdom', 'constitution', 'luck', 'agility'
            ]

        for stat in allocatable_stats:
            stat_frame = tk.Frame(scrollable_frame, bg="dark gray", relief="ridge", bd=1)
            stat_frame.pack(fill=tk.X, pady=2, padx=2)

            # Stat name and current value
            info_frame = tk.Frame(stat_frame, bg="dark gray")
            info_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)

            tk.Label(
                info_frame,
                text=f"{stat.title()}:",
                bg="dark gray",
                fg="white",
                width=15,
                anchor="w",
                font=("Arial", 9)
            ).pack(side=tk.LEFT, padx=(5, 0))

            # Current value label
            value_label = tk.Label(
                info_frame,
                text="0.0",
                bg="dark gray",
                fg="cyan",
                width=6,
                anchor="e",
                font=("Arial", 9, "bold")
            )
            value_label.pack(side=tk.LEFT, padx=(0, 5))
            self.stat_buttons[f"{stat}_value"] = value_label

            # Allocation button
            btn = tk.Button(
                stat_frame,
                text=f"+ {stat.title()}",
                bg="green",
                fg="white",
                width=15,
                font=("Arial", 8, "bold"),
                relief="raised",
                bd=2,
                command=lambda s=stat: self.allocate_stat_point(s)
            )
            btn.pack(side=tk.RIGHT, padx=5, pady=2)
            self.stat_buttons[stat] = btn

        # Bottom controls (outside the scrollable area)
        control_frame = tk.Frame(right_frame, bg="dark gray", relief="ridge", bd=2)
        control_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=(10, 0), padx=5)

        # Reset points button
        reset_btn = tk.Button(
            control_frame,
            text="Reset All Points",
            bg="red",
            fg="white",
            font=("Arial", 10, "bold"),
            relief="raised",
            bd=3,
            command=self.reset_stat_points
        )
        reset_btn.pack(fill=tk.X, pady=3, padx=3)

        # Gain XP button for testing
        xp_btn = tk.Button(
            control_frame,
            text="Gain XP (Test)",
            bg="blue",
            fg="white",
            font=("Arial", 10, "bold"),
            relief="raised",
            bd=3,
            command=self.gain_test_xp
        )
        xp_btn.pack(fill=tk.X, pady=3, padx=3)

        # Add skill/spell/enchantment learning section
        learn_frame = tk.Frame(self.leveling_tab, bg="black")
        learn_frame.pack(fill=tk.X, padx=10, pady=10)

        tk.Label(
            learn_frame,
            text="Learn Skills/Spells/Enchantments:",
            bg="black",
            fg="yellow",
            font=("Arial", 12, "bold")
        ).pack(anchor="w")

        self.learn_skill_btn = tk.Button(
            learn_frame,
            text="Learn Skill",
            bg="purple",
            fg="white",
            command=self.learn_skill_dialog
        )
        self.learn_skill_btn.pack(side=tk.LEFT, padx=5)

        self.learn_spell_btn = tk.Button(
            learn_frame,
            text="Learn Spell",
            bg="blue",
            fg="white",
            command=self.learn_spell_dialog
        )
        self.learn_spell_btn.pack(side=tk.LEFT, padx=5)

        self.learn_enchant_btn = tk.Button(
            learn_frame,
            text="Learn Enchantment",
            bg="orange",
            fg="white",
            command=self.learn_enchant_dialog
        )
        self.learn_enchant_btn.pack(side=tk.LEFT, padx=5)

    def learn_skill_dialog(self):
        """Dialog to learn a skill if requirements are met."""
        try:
            # Define skills with level requirements
            skill_requirements = {
                "power_attack": {"level": 2, "strength": 15},
                "defensive_stance": {"level": 3, "constitution": 12},
                "quick_strike": {"level": 4, "dexterity": 18},
                "berserker_rage": {"level": 5, "strength": 20, "constitution": 15}
            }

            if not hasattr(self.player, 'known_skills'):
                self.player.known_skills = []

            # Find skills not yet learned and check level requirements
            available_for_learning = []
            for skill, requirements in skill_requirements.items():
                if skill not in self.player.known_skills:
                    # Check level requirement
                    if self.player.level >= requirements["level"]:
                        # Check stat requirements
                        can_learn = True
                        for stat, required_value in requirements.items():
                            if stat != "level":
                                current_value = getattr(self.player, stat, 0)
                                if current_value < required_value:
                                    can_learn = False
                                    break
                        if can_learn:
                            available_for_learning.append(skill)

            if not available_for_learning:
                self.log_message("No skills available to learn at your current level/stats!", "info")
                return

            # Learn the first available skill
            skill_id = available_for_learning[0]
            self.player.known_skills.append(skill_id)
            requirements_text = ", ".join([f"{k}: {v}" for k, v in skill_requirements[skill_id].items()])
            self.log_message(f"Learned skill: {skill_id}! (Required: {requirements_text})", "info")

            # Update progression display
            self.update_progression_display()

        except Exception as e:
            self.log_message(f"Error learning skill: {e}", "error")

    def learn_spell_dialog(self):
        """Dialog to learn a spell if requirements are met."""
        try:
            # Define spells with level requirements
            spell_requirements = {
                "magic_missile": {"level": 1, "intelligence": 10},
                "heal": {"level": 2, "wisdom": 12},
                "fireball": {"level": 3, "intelligence": 15},
                "ice_shard": {"level": 4, "intelligence": 18},
                "lightning_bolt": {"level": 5, "intelligence": 20, "wisdom": 15}
            }

            if not hasattr(self.player, 'known_spells'):
                self.player.known_spells = []

            # Find spells not yet learned and check level requirements
            available_for_learning = []
            for spell, requirements in spell_requirements.items():
                if spell not in self.player.known_spells:
                    # Check level requirement
                    if self.player.level >= requirements["level"]:
                        # Check stat requirements
                        can_learn = True
                        for stat, required_value in requirements.items():
                            if stat != "level":
                                current_value = getattr(self.player, stat, 0)
                                if current_value < required_value:
                                    can_learn = False
                                    break
                        if can_learn:
                            available_for_learning.append(spell)

            if not available_for_learning:
                self.log_message("No spells available to learn at your current level/stats!", "info")
                return

            # Learn the first available spell
            spell_id = available_for_learning[0]
            self.player.known_spells.append(spell_id)
            requirements_text = ", ".join([f"{k}: {v}" for k, v in spell_requirements[spell_id].items()])
            self.log_message(f"Learned spell: {spell_id}! (Required: {requirements_text})", "info")

            # Update progression display
            self.update_progression_display()

        except Exception as e:
            self.log_message(f"Error learning spell: {e}", "error")

    def learn_enchant_dialog(self):
        """Dialog to learn an enchantment if requirements are met."""
        try:
            # Simple enchantment learning for demo purposes
            available_enchants = ["fire_enchant", "ice_enchant", "lightning_enchant", "strength_enchant", "speed_enchant"]

            if not hasattr(self.player, 'known_enchantments'):
                self.player.known_enchantments = []

            # Find enchantments not yet learned
            unlearned_enchants = [enchant for enchant in available_enchants if enchant not in self.player.known_enchantments]

            if not unlearned_enchants:
                self.log_message("No new enchantments available to learn!", "info")
                return

            # For demo, learn the first available enchantment
            enchant_id = unlearned_enchants[0]
            self.player.known_enchantments.append(enchant_id)
            self.log_message(f"Learned enchantment: {enchant_id}!", "info")

        except Exception as e:
            self.log_message(f"Error learning enchantment: {e}", "error")

    def setup_enchanting_tab(self):
        """Set up the enchanting and spell management tab."""
        # Initialize selection tracking variables
        self.selected_enchantment_index = None
        self.selected_item_index = None
        self.selected_enchantment_text = None
        self.selected_item_text = None

        # Main enchanting frame
        main_frame = tk.Frame(self.enchanting_tab, bg="black")
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

        self.available_enchants_listbox = tk.Listbox(
            left_frame,
            bg="black",
            fg="white",
            height=8
        )
        self.available_enchants_listbox.pack(fill=tk.BOTH, expand=True, pady=5)

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

        self.learned_enchants_listbox = tk.Listbox(
            middle_frame,
            bg="black",
            fg="white",
            height=8,
            selectmode=tk.SINGLE
        )
        self.learned_enchants_listbox.pack(fill=tk.BOTH, expand=True, pady=5)

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

        self.enchantable_items_listbox = tk.Listbox(
            right_frame,
            bg="black",
            fg="white",
            height=8,
            selectmode=tk.SINGLE
        )
        self.enchantable_items_listbox.pack(fill=tk.BOTH, expand=True, pady=5)

        # Add select buttons below each listbox
        enchant_btn_frame = tk.Frame(middle_frame, bg="dark gray")
        enchant_btn_frame.pack(fill=tk.X, pady=5)

        tk.Button(
            enchant_btn_frame,
            text="Select This Enchantment",
            bg="blue",
            fg="white",
            command=self.select_enchantment
        ).pack()

        item_btn_frame = tk.Frame(right_frame, bg="dark gray")
        item_btn_frame.pack(fill=tk.X, pady=5)

        tk.Button(
            item_btn_frame,
            text="Select This Item",
            bg="green",
            fg="white",
            command=self.select_item
        ).pack()

        # Bottom controls
        controls_frame = tk.Frame(main_frame, bg="black")
        controls_frame.pack(fill=tk.X, pady=(10, 0))

        # Instructions label
        instructions_label = tk.Label(
            controls_frame,
            text="1. Highlight & Select enchantment  2. Highlight & Select item  3. Apply",
            bg="black",
            fg="cyan",
            font=("Arial", 10, "bold")
        )
        instructions_label.pack(pady=(0, 5))

        # Button frame
        button_frame = tk.Frame(controls_frame, bg="black")
        button_frame.pack()

        tk.Button(
            button_frame,
            text="Learn Selected Enchantment",
            bg="purple",
            fg="white",
            command=self.learn_selected_enchantment
        ).pack(side=tk.LEFT, padx=5)

        tk.Button(
            button_frame,
            text="Apply Enchantment to Item",
            bg="blue",
            fg="white",
            command=self.apply_selected_enchantment
        ).pack(side=tk.LEFT, padx=5)

        tk.Button(
            button_frame,
            text="Refresh All Lists",
            bg="green",
            fg="white",
            command=self.refresh_enchanting_lists
        ).pack(side=tk.LEFT, padx=5)

        # Additional control buttons
        additional_btn_frame = tk.Frame(controls_frame, bg="black")
        additional_btn_frame.pack(pady=(10, 0))

        tk.Button(
            additional_btn_frame,
            text="Clear Enchantment Selection",
            bg="red",
            fg="white",
            command=self.clear_enchantment_selection
        ).pack(side=tk.LEFT, padx=5)

        tk.Button(
            additional_btn_frame,
            text="Clear Item Selection",
            bg="red",
            fg="white",
            command=self.clear_item_selection
        ).pack(side=tk.LEFT, padx=5)

        tk.Button(
            additional_btn_frame,
            text="Clear Both Selections",
            bg="darkred",
            fg="white",
            command=self.clear_both_selections
        ).pack(side=tk.LEFT, padx=5)

        # Selection info label
        self.enchanting_selection_label = tk.Label(
            controls_frame,
            text="Select enchantment and item, then apply",
            bg="black",
            fg="yellow",
            font=("Arial", 10)
        )
        self.enchanting_selection_label.pack(pady=(5, 0))
        self.enchanting_selection_label = tk.Label(
            controls_frame,
            text="Select enchantment and item, then apply",
            bg="black",
            fg="yellow",
            font=("Arial", 10)
        )
        self.enchanting_selection_label.pack(pady=(5, 0))

    def setup_progression_tab(self):
        """Set up the progression overview tab."""
        # Main progression frame
        main_frame = tk.Frame(self.progression_tab, bg="black")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Title
        tk.Label(
            main_frame,
            text="Character Progression Overview",
            bg="black",
            fg="white",
            font=("Arial", 16, "bold")
        ).pack(pady=(0, 10))

        # Top section: Level and XP info
        level_frame = tk.Frame(main_frame, bg="dark gray")
        level_frame.pack(fill=tk.X, pady=(0, 10))

        self.level_label = tk.Label(
            level_frame,
            text="Level: 1",
            bg="dark gray",
            fg="yellow",
            font=("Arial", 14, "bold")
        )
        self.level_label.pack(side=tk.LEFT, padx=10, pady=5)

        self.stat_points_label = tk.Label(
            level_frame,
            text="Available Stat Points: 0",
            bg="dark gray",
            fg="cyan",
            font=("Arial", 12)
        )
        self.stat_points_label.pack(side=tk.LEFT, padx=10, pady=5)

        # Middle section: Three columns for skills, spells, items
        columns_frame = tk.Frame(main_frame, bg="black")
        columns_frame.pack(fill=tk.BOTH, expand=True)

        # Skills column
        skills_frame = tk.Frame(columns_frame, bg="dark gray")
        skills_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))

        tk.Label(
            skills_frame,
            text="Available Skills:",
            bg="dark gray",
            fg="white",
            font=("Arial", 12, "bold")
        ).pack(anchor="w", pady=(0, 5))

        self.available_skills_listbox = tk.Listbox(
            skills_frame,
            bg="black",
            fg="white",
            height=8
        )
        self.available_skills_listbox.pack(fill=tk.BOTH, expand=True, pady=5)

        tk.Label(
            skills_frame,
            text="Learned Skills:",
            bg="dark gray",
            fg="white",
            font=("Arial", 12, "bold")
        ).pack(anchor="w", pady=(10, 5))

        self.learned_skills_listbox = tk.Listbox(
            skills_frame,
            bg="black",
            fg="green",
            height=8
        )
        self.learned_skills_listbox.pack(fill=tk.BOTH, expand=True, pady=5)

        # Spells column
        spells_frame = tk.Frame(columns_frame, bg="dark gray")
        spells_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)

        tk.Label(
            spells_frame,
            text="Available Spells:",
            bg="dark gray",
            fg="white",
            font=("Arial", 12, "bold")
        ).pack(anchor="w", pady=(0, 5))

        self.available_spells_listbox = tk.Listbox(
            spells_frame,
            bg="black",
            fg="white",
            height=8
        )
        self.available_spells_listbox.pack(fill=tk.BOTH, expand=True, pady=5)

        tk.Label(
            spells_frame,
            text="Learned Spells:",
            bg="dark gray",
            fg="white",
            font=("Arial", 12, "bold")
        ).pack(anchor="w", pady=(10, 5))

        self.learned_spells_listbox = tk.Listbox(
            spells_frame,
            bg="black",
            fg="blue",
            height=8
        )
        self.learned_spells_listbox.pack(fill=tk.BOTH, expand=True, pady=5)

        # Items column
        items_frame = tk.Frame(columns_frame, bg="dark gray")
        items_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))

        tk.Label(
            items_frame,
            text="Unlocked Items:",
            bg="dark gray",
            fg="white",
            font=("Arial", 12, "bold")
        ).pack(anchor="w", pady=(0, 5))

        self.unlocked_items_listbox = tk.Listbox(
            items_frame,
            bg="black",
            fg="white",
            height=16
        )
        self.unlocked_items_listbox.pack(fill=tk.BOTH, expand=True, pady=5)

        # Bottom section: Progression info text
        info_frame = tk.Frame(main_frame, bg="dark gray")
        info_frame.pack(fill=tk.X, pady=(10, 0))

        tk.Label(
            info_frame,
            text="Progression Information:",
            bg="dark gray",
            fg="white",
            font=("Arial", 12, "bold")
        ).pack(anchor="w", pady=(0, 5))

        self.progression_info = tk.Text(
            info_frame,
            bg="black",
            fg="white",
            font=("Courier", 10),
            height=6,
            state="disabled"
        )
        self.progression_info.pack(fill=tk.X, pady=5)

    def learn_selected_enchantment(self):
        """Learn the selected enchantment from the available list."""
        if not hasattr(self, 'available_enchants_listbox'):
            return

        selection = self.available_enchants_listbox.curselection()
        if not selection:
            self.log_message("Please select an enchantment to learn", "info")
            return

        enchant_id = self.available_enchants_listbox.get(selection[0])

        try:
            if hasattr(self.player, 'enchanting_system'):
                success = self.player.enchanting_system.learn_enchantment(enchant_id)
                if success:
                    self.log_message(f"Successfully learned enchantment: {enchant_id}!", "info")
                    self.refresh_enchanting_lists()  # Update the lists
                else:
                    self.log_message(f"Failed to learn enchantment: {enchant_id}", "combat")
            else:
                # Fallback: Manual learning
                if not hasattr(self.player, 'known_enchantments'):
                    self.player.known_enchantments = []

                if enchant_id not in self.player.known_enchantments:
                    self.player.known_enchantments.append(enchant_id)
                    self.log_message(f"Learned enchantment: {enchant_id}!", "info")
                    self.refresh_enchanting_lists()
                else:
                    self.log_message(f"Already know enchantment: {enchant_id}", "info")

        except Exception as e:
            self.log_message(f"Error learning enchantment: {e}", "combat")

    def apply_selected_enchantment(self):
        """Apply the selected enchantment to the selected item."""
        if not hasattr(self, 'player') or not self.player:
            self.log_message("No player character available!", "combat")
            return

        # Check stored selections instead of current listbox selections
        if not self.selected_enchantment_text or self.selected_enchantment_index is None:
            self.log_message("Please select an enchantment to apply", "info")
            return

        if not self.selected_item_text or self.selected_item_index is None:
            self.log_message("Please select an item to enchant", "info")
            return

        try:
            # Get the enchantment ID from stored selection
            enchant_id = self.selected_enchantment_text

            # Get the item from inventory using stored selection
            if hasattr(self.player, 'inventory'):
                items = self.player.inventory.list_items()
                # Filter for enchantable items (weapons and armor)
                enchantable_items = [item for item in items
                                   if hasattr(item, 'type') and
                                   item.type in ['weapon', 'armor', 'offhand_weapon', 'shield', 'two_handed_weapon']]

                if self.selected_item_index < len(enchantable_items):
                    item = enchantable_items[self.selected_item_index]

                    # Apply enchantment - use simple fallback since enchanting system has issues
                    # The enchanting system incorrectly tries to load enchantments as items
                    if not hasattr(item, 'enchantments'):
                        item.enchantments = []
                    if enchant_id not in item.enchantments:
                        # Add enchantment to the item's enchantment list
                        item.enchantments.append(enchant_id)

                        # Update item name to show enchantment
                        if not f"[{enchant_id}]" in item.name:
                            item.name = f"{item.name} [{enchant_id}]"

                        # Apply stat boosts based on enchantment type
                        if not hasattr(item, 'stats'):
                            item.stats = {}

                        # Apply different effects based on enchantment type
                        if 'fire' in enchant_id:
                            # Fire enchants add fire damage and strength
                            item.stats['fire_damage'] = item.stats.get('fire_damage', 0) + 5
                            item.stats['strength'] = item.stats.get('strength', 0) + 2
                            from game_sys.core.damage_types import DamageType
                            from game_sys.core.damage_type_utils import get_damage_type_by_name
                            item.damage_type = get_damage_type_by_name("FIRE")
                            self.log_message(f"Added fire damage (+5) and strength (+2) to {item.name}!", "info")

                        elif 'ice' in enchant_id:
                            # Ice enchants add ice damage and slow effect
                            item.stats['ice_damage'] = item.stats.get('ice_damage', 0) + 3
                            item.stats['slow_chance'] = item.stats.get('slow_chance', 0) + 0.2
                            from game_sys.core.damage_types import DamageType
                            from game_sys.core.damage_type_utils import get_damage_type_by_name
                            item.damage_type = get_damage_type_by_name("ICE")
                            msg = f"Added ice damage (+3) and slow chance (+20%) to {item.name}!"

                            self.log_message(msg, "info")

                        elif 'lightning' in enchant_id:
                            # Lightning enchants add lightning damage and attack speed
                            item.stats['lightning_damage'] = item.stats.get('lightning_damage', 0) + 4
                            item.stats['attack_speed'] = item.stats.get('attack_speed', 0) + 0.15
                            from game_sys.core.damage_types import DamageType
                            from game_sys.core.damage_type_utils import get_damage_type_by_name
                            item.damage_type = get_damage_type_by_name("LIGHTNING")
                            msg = f"Added lightning damage (+4) and attack speed (+15%) to {item.name}!"

                            self.log_message(msg, "info")

                        elif 'poison' in enchant_id:
                            # Poison enchants add poison damage and DOT effect
                            item.stats['poison_damage'] = item.stats.get('poison_damage', 0) + 3
                            item.stats['dot_chance'] = item.stats.get('dot_chance', 0) + 0.25
                            from game_sys.core.damage_types import DamageType
                            from game_sys.core.damage_type_utils import get_damage_type_by_name
                            item.damage_type = get_damage_type_by_name("POISON")
                            msg = f"Added poison damage (+3) and DOT chance (+25%) to {item.name}!"

                            self.log_message(msg, "info")

                        elif 'strength' in enchant_id:
                            # Strength enchants add physical damage and strength
                            item.stats['damage'] = item.stats.get('damage', 0) + 3
                            item.stats['strength'] = item.stats.get('strength', 0) + 5
                            from game_sys.core.damage_types import DamageType
                            from game_sys.core.damage_type_utils import get_damage_type_by_name
                            item.damage_type = get_damage_type_by_name("PHYSICAL")
                            msg = f"Added physical damage (+3) and strength (+5) to {item.name}!"

                            self.log_message(msg, "info")

                        else:
                            # Generic enhancement for unknown enchant types
                            item.stats['damage'] = item.stats.get('damage', 0) + 2
                            item.stats['defense'] = item.stats.get('defense', 0) + 2
                            # Default to physical damage type for generic enchants
                            from game_sys.core.damage_types import DamageType
                            from game_sys.core.damage_type_utils import get_damage_type_by_name
                            item.damage_type = get_damage_type_by_name("PHYSICAL")
                            self.log_message(f"Enhanced {item.name} with +2 damage and +2 defense!", "info")

                        self.log_message(f"Applied {enchant_id} to {item.name}!", "info")
                    else:
                        self.log_message(f"{item.name} already has {enchant_id}", "info")

                    # Clear selections after successful application
                    self.selected_enchantment_index = None
                    self.selected_enchantment_text = None
                    self.selected_item_index = None
                    self.selected_item_text = None

                    # Refresh displays
                    self.refresh_enchanting_lists()
                    self.update_inventory_display()
                    self.update_enchanting_feedback()
                else:
                    self.log_message("Selected item is no longer available", "info")
            else:
                self.log_message("No inventory system available", "info")

        except Exception as e:
            self.log_message(f"Error applying enchantment: {e}", "combat")

    def refresh_enchanting_lists(self):
        """Refresh the enchanting tab lists."""
        if not hasattr(self, 'player') or not self.player:
            return

        try:
            # Refresh available enchantments list
            if hasattr(self, 'available_enchants_listbox'):
                self.available_enchants_listbox.delete(0, tk.END)
                if hasattr(self.player, 'enchanting_system'):
                    available_enchants = self.player.enchanting_system.get_available_enchantments()
                    for enchant in available_enchants:
                        self.available_enchants_listbox.insert(tk.END, enchant)
                else:
                    # Fallback: Use hardcoded list of enchantments
                    enchants = ['fire_enchant', 'ice_enchant', 'lightning_enchant',
                               'poison_enchant', 'strength_enchant', 'speed_enchant']
                    for enchant in enchants:
                        self.available_enchants_listbox.insert(tk.END, enchant)

            # Refresh learned enchantments list
            if hasattr(self, 'learned_enchants_listbox'):
                self.learned_enchants_listbox.delete(0, tk.END)
                if hasattr(self.player, 'enchanting_system'):
                    learned_enchants = self.player.enchanting_system.get_known_enchantments()
                    for enchant in learned_enchants:
                        self.learned_enchants_listbox.insert(tk.END, enchant)
                elif hasattr(self.player, 'known_enchantments'):
                    for enchant in self.player.known_enchantments:
                        self.learned_enchants_listbox.insert(tk.END, enchant)

            # Refresh enchantable items list
            if hasattr(self, 'enchantable_items_listbox'):
                self.enchantable_items_listbox.delete(0, tk.END)
                if hasattr(self.player, 'inventory'):
                    items = self.player.inventory.list_items()
                    enchantable_items = []

                    for item in items:
                        # Check multiple ways an item might be enchantable
                        is_enchantable = False
                        item_type = "unknown"

                        # Check type attribute
                        if hasattr(item, 'type'):
                            item_type = item.type
                            if item.type in ['weapon', 'armor', 'offhand_weapon', 'shield', 'two_handed_weapon']:
                                is_enchantable = True

                        # Check item_type attribute
                        elif hasattr(item, 'item_type'):
                            item_type = item.item_type
                            if item.item_type in ['weapon', 'armor', 'offhand_weapon', 'shield', 'two_handed_weapon']:
                                is_enchantable = True

                        # Check class name as fallback
                        elif any(weapon_type in str(type(item)).lower()
                               for weapon_type in ['weapon', 'armor', 'shield']):
                            is_enchantable = True
                            item_type = "equipment"

                        # Check for specific attributes that indicate equipment
                        elif (hasattr(item, 'base_damage') or hasattr(item, 'defense') or
                              hasattr(item, 'slot') or hasattr(item, 'block_chance')):
                            is_enchantable = True
                            if hasattr(item, 'base_damage'):
                                item_type = "weapon"
                            elif hasattr(item, 'defense'):
                                item_type = "armor"
                            else:
                                item_type = "equipment"

                        if is_enchantable:
                            enchantable_items.append((item, item_type))

                    if enchantable_items:
                        for item, item_type in enchantable_items:
                            display_name = f"{item.name} ({item_type})"
                            self.enchantable_items_listbox.insert(tk.END, display_name)
                    else:
                        self.enchantable_items_listbox.insert(tk.END, "(No enchantable items)")
                        # Add debug info
                        if items:
                            self.enchantable_items_listbox.insert(tk.END, f"Found {len(items)} total items:")
                            for item in items[:3]:  # Show first 3 items for debugging
                                item_info = f"  {item.name}"
                                if hasattr(item, 'type'):
                                    item_info += f" (type: {item.type})"
                                elif hasattr(item, 'item_type'):
                                    item_info += f" (item_type: {item.item_type})"
                                else:
                                    item_info += f" (class: {type(item).__name__})"
                                self.enchantable_items_listbox.insert(tk.END, item_info)
                else:
                    self.enchantable_items_listbox.insert(tk.END, "(No inventory system)")

            # Refresh displays - no need to restore selections since we use buttons
            self.update_enchanting_feedback()

        except Exception as e:
            self.log_message(f"Error refreshing enchanting lists: {e}", "combat")

    def select_enchantment(self):
        """Select the currently highlighted enchantment."""
        try:
            selection = self.learned_enchants_listbox.curselection()
            if not selection:
                self.log_message("Please highlight an enchantment first", "info")
                return

            self.selected_enchantment_index = selection[0]
            self.selected_enchantment_text = self.learned_enchants_listbox.get(selection[0])

            self.log_message(f"Selected enchantment: {self.selected_enchantment_text}", "info")
            self.update_enchanting_feedback()
        except Exception as e:
            self.log_message(f"Error selecting enchantment: {e}", "combat")

    def select_item(self):
        """Select the currently highlighted item."""
        try:
            selection = self.enchantable_items_listbox.curselection()
            if not selection:
                self.log_message("Please highlight an item first", "info")
                return

            self.selected_item_index = selection[0]
            self.selected_item_text = self.enchantable_items_listbox.get(selection[0])

            self.log_message(f"Selected item: {self.selected_item_text}", "info")
            self.update_enchanting_feedback()
        except Exception as e:
            self.log_message(f"Error selecting item: {e}", "combat")

    def update_enchanting_feedback(self):
        """Update the feedback label based on current selections."""
        try:
            if hasattr(self, 'enchanting_selection_label'):
                if self.selected_enchantment_text and self.selected_item_text:
                    self.enchanting_selection_label.config(
                        text=f"Ready: {self.selected_enchantment_text} -> {self.selected_item_text}",
                        fg="green")
                elif self.selected_enchantment_text:
                    self.enchanting_selection_label.config(
                        text=f"Selected enchantment: {self.selected_enchantment_text} (select item)",
                        fg="yellow")
                elif self.selected_item_text:
                    self.enchanting_selection_label.config(
                        text=f"Selected item: {self.selected_item_text} (select enchantment)",
                        fg="yellow")
                else:
                    self.enchanting_selection_label.config(
                        text="Select enchantment and item, then apply",
                        fg="yellow")
        except Exception:
            pass

    def update_progression_display(self):
        """Update all progression displays with current data."""
        if not hasattr(self, 'player') or not self.player:
            return

        try:
            # Update level and XP info
            if hasattr(self, 'level_label'):
                level_text = f"Level: {getattr(self.player, 'level', 1)}"
                if hasattr(self.player, 'leveling_manager'):
                    current_xp = getattr(self.player.leveling_manager, 'current_experience', 0)
                    # Use a simple XP calculation for next level
                    needed_xp = self.player.level * 100
                    level_text += f" (XP: {current_xp}/{needed_xp})"
                self.level_label.config(text=level_text)

            # Update stat points
            if hasattr(self, 'stat_points_label') and hasattr(self.player, 'leveling_manager'):
                available_points = self.player.leveling_manager.calculate_stat_points_available(self.player)
                self.stat_points_label.config(text=f"Available Stat Points: {available_points}")

            # Update skills lists
            if hasattr(self, 'available_skills_listbox'):
                self.available_skills_listbox.delete(0, tk.END)
                if hasattr(self.player, 'leveling_manager'):
                    available_skills = self.player.leveling_manager.get_available_skills_for_level(self.player)
                    for skill in available_skills:
                        self.available_skills_listbox.insert(tk.END, skill)

            if hasattr(self, 'learned_skills_listbox'):
                self.learned_skills_listbox.delete(0, tk.END)
                if hasattr(self.player, 'leveling_manager'):
                    # Add learned skills if available
                    learned = self.player.leveling_manager.get_learned_skills(self.player)
                    for skill in learned:
                        self.learned_skills_listbox.insert(tk.END, skill)

            # Update spells lists
            if hasattr(self, 'available_spells_listbox'):
                self.available_spells_listbox.delete(0, tk.END)
                if hasattr(self.player, 'leveling_manager'):
                    available_spells = self.player.leveling_manager.get_available_spells_for_level(self.player)
                    for spell in available_spells:
                        self.available_spells_listbox.insert(tk.END, spell)

            if hasattr(self, 'learned_spells_listbox'):
                self.learned_spells_listbox.delete(0, tk.END)
                if hasattr(self.player, 'leveling_manager'):
                    # Add learned spells if available
                    learned = self.player.leveling_manager.get_learned_spells(self.player)
                    for spell in learned:
                        self.learned_spells_listbox.insert(tk.END, spell)

            # Update items list - show items that can be crafted/found at current level
            if hasattr(self, 'unlocked_items_listbox'):
                self.unlocked_items_listbox.delete(0, tk.END)

                # Define items by level requirement
                items_by_level = {
                    1: ["wooden_stick", "basic_clothes", "potion_health"],
                    2: ["leather_armor", "potion_mana", "wooden_shield"],
                    3: ["iron_sword", "iron_dagger", "apprentice_staff"],
                    4: ["mage_robes", "spell_focus", "boots_of_speed"],
                    5: ["arcane_staff", "archmage_robes", "vampiric_blade"],
                    10: ["ring_of_power", "cloak_of_fortune", "thornmail_armor"],
                    15: ["orc_axe", "arcane_focus"],
                    25: ["dragon_claw", "dragon_scale_armor"]
                }

                # Show all items available up to current level
                for level in sorted(items_by_level.keys()):
                    if self.player.level >= level:
                        for item_id in items_by_level[level]:
                            self.unlocked_items_listbox.insert(tk.END, f"Lv{level}: {item_id}")
                    else:
                        # Show next level items as locked
                        for item_id in items_by_level[level]:
                            self.unlocked_items_listbox.insert(tk.END, f"[LOCKED] Lv{level}: {item_id}")
                        break  # Only show next level, not all future levels

            # Update progression info
            if hasattr(self, 'progression_info'):
                self.progression_info.config(state="normal")
                self.progression_info.delete(1.0, tk.END)

                info_text = f"Character: {self.player.name}\n"
                info_text += f"Level: {self.player.level}\n"

                # Show what's available at next level
                current_level = self.player.level
                info_text += f"\nNext Level ({current_level + 1}) Unlocks:\n"

                # Skills
                skill_requirements = {
                    "power_attack": {"level": 2, "strength": 15},
                    "defensive_stance": {"level": 3, "constitution": 12},
                    "quick_strike": {"level": 4, "dexterity": 18},
                    "berserker_rage": {"level": 5, "strength": 20, "constitution": 15}
                }

                skills_next = [skill for skill, req in skill_requirements.items()
                              if req["level"] == current_level + 1]
                if skills_next:
                    info_text += f"  Skills: {', '.join(skills_next)}\n"

                # Spells
                spell_requirements = {
                    "magic_missile": {"level": 1, "intelligence": 10},
                    "heal": {"level": 2, "wisdom": 12},
                    "fireball": {"level": 3, "intelligence": 15},
                    "ice_shard": {"level": 4, "intelligence": 18},
                    "lightning_bolt": {"level": 5, "intelligence": 20, "wisdom": 15}
                }

                spells_next = [spell for spell, req in spell_requirements.items()
                              if req["level"] == current_level + 1]
                if spells_next:
                    info_text += f"  Spells: {', '.join(spells_next)}\n"

                # Items
                items_by_level = {
                    2: ["leather_armor", "potion_mana", "wooden_shield"],
                    3: ["iron_sword", "iron_dagger", "apprentice_staff"],
                    4: ["mage_robes", "spell_focus", "boots_of_speed"],
                    5: ["arcane_staff", "archmage_robes", "vampiric_blade"],
                    10: ["ring_of_power", "cloak_of_fortune", "thornmail_armor"],
                    15: ["orc_axe", "arcane_focus"],
                    25: ["dragon_claw", "dragon_scale_armor"]
                }

                if current_level + 1 in items_by_level:
                    items_next = items_by_level[current_level + 1]
                    info_text += f"  Items: {', '.join(items_next[:3])}\n"
                    if len(items_next) > 3:
                        info_text += f"     ... and {len(items_next) - 3} more\n"

                self.progression_info.insert(tk.END, info_text)
                self.progression_info.config(state="disabled")

        except Exception as e:
            self.log_message(f"Error updating progression display: {e}", "combat")

    def reset_stat_points(self):
        """Reset all allocated stat points for the player."""
        if not hasattr(self, 'player') or not self.player:
            self.log_message("No player character available!", "combat")
            return

        try:
            # Use leveling manager if available
            if hasattr(self.player, 'leveling_manager'):
                self.player.leveling_manager.reset_stat_points(self.player)
                available = self.player.leveling_manager.calculate_stat_points_available(self.player)
                self.log_message(f"Stat points reset successfully! You have {available} points to allocate.", "info")
            else:
                # Manual reset fallback - calculate points to return
                if hasattr(self.player, 'base_stats'):
                    # Get the original base stats (before allocation)
                    defaults = {
                        'attack': 10.0,
                        'constitution': 10.0, 
                        'defense': 6.0,
                        'dexterity': 11.0,
                        'fire_damage': 5.0,
                        'health': 100.0,
                        'intelligence': 10.0,
                        'luck': 10.0,
                        'magic_power': 5.0,
                        'mana': 50.0,
                        'max_targets': 1.0,
                        'speed': 5.0,
                        'stamina': 50.0,
                        'strength': 13.0,
                        'vitality': 10.0,
                        'wisdom': 10.0
                    }
                    
                    # Calculate points to return
                    points_to_return = 0
                    for stat, current_value in self.player.base_stats.items():
                        default_value = defaults.get(stat, 10.0)
                        if current_value > default_value:
                            points_to_return += int(current_value - default_value)
                    
                    # Reset to default values
                    for stat, value in defaults.items():
                        if stat in self.player.base_stats:
                            self.player.base_stats[stat] = value

                    # No legacy available_stat_points; stat points are config-driven

                    # Update derived stats
                    if hasattr(self.player, 'update_stats'):
                        self.player.update_stats()

                    self.log_message(f"Stat points reset! Returned {points_to_return} points for allocation.", "info")
                else:
                    self.log_message("No stats system available", "combat")

            # Update displays
            self.update_char_info()
            self.update_leveling_display()

        except Exception as e:
            self.log_message(f"Error resetting stat points: {e}", "combat")

    def gain_test_xp(self):
        """Give the player some test experience points."""
        if not hasattr(self, 'player') or not self.player:
            self.log_message("No player character available!", "combat")
            return

        try:
            xp_amount = 100  # Test XP amount

            # Use leveling manager if available
            if hasattr(self.player, 'leveling_manager'):
                old_level = self.player.level
                leveled_up = self.player.leveling_manager.gain_experience(
                    self.player,
                    xp_amount
                )

                if leveled_up:
                    level_diff = self.player.level - old_level
                    msg = f"Gained {xp_amount} XP and leveled up {level_diff} time(s)! Level {self.player.level}"
                    self.log_message(msg, "info")
                    
                    # Calculate new available stat points
                    available = self.player.leveling_manager.calculate_stat_points_available(self.player)
                    self.log_message(f"You now have {available} stat points to allocate!", "info")
                else:
                    msg = f"Gained {xp_amount} XP (no level up)"
                    self.log_message(msg, "info")
            else:
                # Manual XP gain fallback
                if not hasattr(self.player, 'experience'):
                    self.player.experience = 0
                if not hasattr(self.player, 'level'):
                    self.player.level = 1

                old_level = self.player.level
                self.player.experience += xp_amount
                
                # Simple level up check
                xp_needed = self.player.level * 100
                if self.player.experience >= xp_needed:
                    self.player.level += 1
                    self.player.experience -= xp_needed
                    
                    # Stat points are handled by leveling_manager
                    msg = f"Gained {xp_amount} XP and leveled up! Level {self.player.level}"
                    self.log_message(msg, "info")
                else:
                    msg = f"Gained {xp_amount} XP!"
                    self.log_message(msg, "info")

            # Update displays
            self.update_char_info()
            self.update_leveling_display()

        except Exception as e:
            self.log_message(f"Error gaining XP: {e}", "combat")

    def allocate_stat_point(self, stat_name):
        """Allocate a stat point to the specified stat."""
        if not hasattr(self, 'player') or not self.player:
            self.log_message("No player character available!", "combat")
            return

        try:
            # Use leveling manager if available
            if hasattr(self.player, 'leveling_manager'):
                success = self.player.leveling_manager.allocate_stat_point(
                    self.player,
                    stat_name
                )

                if success:
                    # Only log stat allocation if player is not an enemy (debug silence for enemies)
                    is_enemy = hasattr(self.player, 'type') and getattr(self.player, 'type', None) == 'enemy'
                    if not is_enemy:
                        msg = f"Allocated 1 point to {stat_name}!"
                        self.log_message(msg, "info")
                    # Update derived stats
                    if hasattr(self.player, 'update_stats'):
                        self.player.update_stats()
                else:
                    available = self.player.leveling_manager.calculate_stat_points_available(self.player)
                    msg = f"Cannot allocate point to {stat_name} (available: {available})"
                    self.log_message(msg, "combat")
            else:
                # Stat points are handled by leveling_manager; no legacy fallback
                pass

            # Update displays
            self.update_char_info()
            self.update_leveling_display()

        except Exception as e:
            self.log_message(f"Error allocating stat point: {e}", "combat")

    def update_leveling_display(self):
        """Update the leveling tab display."""
        if not hasattr(self, 'player') or not self.player:
            return

        try:
            # Update available stat points display
            if hasattr(self, 'available_points_label'):
                if hasattr(self.player, 'leveling_manager'):
                    available_points = self.player.leveling_manager.calculate_stat_points_available(self.player)
                    self.available_points_label.config(text=str(available_points))
                else:
                    self.available_points_label.config(text="0")

            # Update allocatable stats display
            if hasattr(self, 'allocatable_stats_text'):
                self.allocatable_stats_text.config(state="normal")
                self.allocatable_stats_text.delete(1.0, tk.END)

                # --- Character Info Section ---
                char_info = f"== {self.player.name} ==\n"
                char_info += f"Level: {self.player.level}\n"
                if hasattr(self.player, 'grade_name'):
                    char_info += f"Grade: {self.player.grade_name}\n"
                elif hasattr(self.player, 'grade'):
                    char_info += f"Grade: {self.player.grade}\n"
                if hasattr(self.player, 'rarity'):
                    char_info += f"Rarity: {self.player.rarity}\n"
                health_val = f"{getattr(self.player, 'current_health', 0):.2f}/"
                health_val += f"{getattr(self.player, 'max_health', 0):.2f}"
                char_info += f"Health: {health_val}\n"

                # --- Base Stats Section ---
                rpg_stats = ['strength', 'dexterity', 'vitality', 'intelligence', 'wisdom', 'constitution', 'luck', 'agility']
                if not hasattr(self.player, 'base_stats') or not isinstance(self.player.base_stats, dict):
                    self.player.base_stats = {stat: 10 for stat in rpg_stats}
                else:
                    for stat in rpg_stats:
                        if stat not in self.player.base_stats:
                            self.player.base_stats[stat] = 10
                char_info += "\n=== BASE STATS ===\n"
                for stat_name in rpg_stats:
                    value = self.player.base_stats[stat_name]
                    display_name = stat_name.replace('_', ' ').title()
                    char_info += f"  {display_name}: {value:.2f}\n"

                # --- Combat Stats (Derived) ---
                char_info += "\n=== COMBAT STATS ===\n"
                combat_stats = ['attack', 'defense', 'speed', 'magic_power']
                for stat_name in combat_stats:
                    if hasattr(self.player, 'get_stat'):
                        value = self.player.get_stat(stat_name)
                        display_name = stat_name.replace('_', ' ').title()
                        char_info += f"  {display_name}: {value:.1f}\n"

                # --- Resource Stats (Derived) ---
                char_info += "\n=== RESOURCE STATS ===\n"
                resource_stats = [
                    ('health', 'max_health', 'current_health'),
                    ('mana', 'max_mana', 'current_mana'),
                    ('stamina', 'max_stamina', 'current_stamina')
                ]
                for base_stat, max_attr, current_attr in resource_stats:
                    if hasattr(self.player, 'get_stat'):
                        max_val = self.player.get_stat(base_stat)
                        current_val = getattr(self.player, current_attr, max_val)
                        display_name = base_stat.replace('_', ' ').title()
                        char_info += f"  {display_name}: {current_val:.0f}/{max_val:.0f}\n"

                # --- Defensive Stats (Derived) ---
                char_info += "\n=== DEFENSIVE STATS ===\n"
                defensive_stats = ['dodge_chance', 'block_chance', 'magic_resistance', 'damage_reduction']
                for stat_name in defensive_stats:
                    if hasattr(self.player, 'get_stat'):
                        value = self.player.get_stat(stat_name)
                        display_name = stat_name.replace('_', ' ').title()
                        if 'chance' in stat_name:
                            char_info += f"  {display_name}: {value:.1%}\n"
                        else:
                            char_info += f"  {display_name}: {value:.2f}\n"

                # --- Regeneration Stats (Derived) ---
                char_info += "\n=== REGENERATION ===\n"
                regen_stats = ['health_regeneration', 'mana_regeneration', 'stamina_regeneration']
                for stat_name in regen_stats:
                    if hasattr(self.player, 'get_stat'):
                        value = self.player.get_stat(stat_name)
                        display_name = stat_name.replace('_', ' ').title()
                        char_info += f"  {display_name}: {value:.3f}/sec\n"

                # --- Special Stats ---
                char_info += "\n=== SPECIAL STATS ===\n"
                special_stats = ['critical_chance', 'luck_factor', 'physical_damage']
                for stat_name in special_stats:
                    if hasattr(self.player, 'get_stat'):
                        value = self.player.get_stat(stat_name)
                        display_name = stat_name.replace('_', ' ').title()
                        if 'chance' in stat_name:
                            char_info += f"  {display_name}: {value:.1%}\n"
                        else:
                            char_info += f"  {display_name}: {value:.2f}\n"

                # --- Equipment Section ---
                char_info += "\n=== EQUIPMENT ===\n"
                weapon = getattr(self.player, 'weapon', None)
                if weapon:
                    char_info += f"  Weapon: {weapon.name}\n"
                else:
                    char_info += "  Weapon: (None)\n"
                offhand = getattr(self.player, 'offhand', None)
                if offhand:
                    char_info += f"  Offhand: {offhand.name}\n"
                else:
                    char_info += "  Offhand: (None)\n"
                body_armor = getattr(self.player, 'equipped_body', None)
                if body_armor:
                    char_info += f"  Body: {body_armor.name}\n"
                else:
                    char_info += "  Body: (None)\n"

                # --- Inventory Section ---
                char_info += "\nInventory:\n"
                if hasattr(self.player, 'inventory'):
                    try:
                        items = self.player.inventory.list_items()
                    except Exception:
                        items = []
                    if items:
                        char_info += f"Items ({len(items)}):\n"
                        for item in items[:5]:
                            item_name = getattr(item, 'name', str(item))
                            char_info += f"  - {item_name}\n"
                        if len(items) > 5:
                            char_info += f"  ... and {len(items) - 5} more\n"
                    else:
                        char_info += "Empty inventory\n"
                else:
                    char_info += "(No inventory system)"

                self.allocatable_stats_text.insert(tk.END, char_info)
                self.allocatable_stats_text.config(state="disabled")

            # Update stat buttons values and enable/disable based on available points
            if hasattr(self, 'stat_buttons') and hasattr(self.player, 'base_stats'):
                # Get available points for button state
                if hasattr(self.player, 'leveling_manager'):
                    available_points = self.player.leveling_manager.calculate_stat_points_available(self.player)
                else:
                    available_points = 0
                # Update values for ALL stats that have buttons
                for stat, base_value in self.player.base_stats.items():
                    value_label_key = f"{stat}_value"
                    if value_label_key in self.stat_buttons:
                        # Show effective value if different from base value
                        if hasattr(self.player, 'get_stat'):
                            effective_value = self.player.get_stat(stat)
                            if abs(base_value - effective_value) > 0.01:
                                # Show both base → effective
                                self.stat_buttons[value_label_key].config(text=f"{base_value:.1f}→{effective_value:.1f}")
                            else:
                                self.stat_buttons[value_label_key].config(text=f"{base_value:.1f}")
                        else:
                            self.stat_buttons[value_label_key].config(text=f"{base_value:.1f}")
                        # Enable/disable allocation buttons based on available points
                        if stat in self.stat_buttons:
                            btn = self.stat_buttons[stat]
                            if available_points > 0:
                                btn.config(state="normal", bg="green")
                            else:
                                btn.config(state="disabled", bg="gray")
        except Exception as e:
            self.log_message(f"Error updating leveling display: {e}", "combat")

    def clear_enchantment_selection(self):
        """Clear the enchantment selection."""
        self.selected_enchantment_index = None
        self.selected_enchantment_text = None
        self.log_message("Enchantment selection cleared", "info")
        self.update_enchanting_feedback()

    def clear_item_selection(self):
        """Clear the item selection."""
        self.selected_item_index = None
        self.selected_item_text = None
        self.log_message("Item selection cleared", "info")
        self.update_enchanting_feedback()

    def clear_both_selections(self):
        """Clear both enchantment and item selections."""
        self.selected_enchantment_index = None
        self.selected_enchantment_text = None
        self.selected_item_index = None
        self.selected_item_text = None
        self.log_message("Both selections cleared", "info")
        self.update_enchanting_feedback()


    def setup_settings_tab(self):
        """Set up the Settings tab with Save, Load, and Reload buttons."""
        settings_frame = tk.Frame(self.settings_tab, bg="black")
        settings_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        button_style = {
            "bg": "#444",
            "fg": "white",
            "activebackground": "#666",
            "activeforeground": "cyan",
            "font": ("Segoe UI", 12, "bold"),
            "relief": tk.RAISED,
            "bd": 2,
            "width": 18,
            "height": 2
        }

        tk.Button(settings_frame, text="Save Game", command=self.save_game, **button_style).pack(pady=10)
        tk.Button(settings_frame, text="Load Game", command=self.load_game, **button_style).pack(pady=10)
        tk.Button(settings_frame, text="Reload Game", command=self.reload_game, **button_style).pack(pady=10)


def main():
    """Main entry point for the demo."""
    try:
        # Set up basic console logging for error tracking during development
        import logging
        logging.basicConfig(level=logging.ERROR)
        console_logger = logging.getLogger("console")
        console_logger.setLevel(logging.ERROR)

        # Create handler to output to console
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.ERROR)
        console_logger.addHandler(console_handler)

        logger.info("Starting demo application...")

        # Create and run the demo
        demo = SimpleGameDemo()
        demo.run()

    except Exception as e:
        # Log to both logger and console for debugging
        if 'logger' in globals():
            logger.exception(f"Error in demo: {e}")

        # Also print to console for immediate visibility
        import traceback
        print(f"ERROR: {e}")
        traceback.print_exc()
        raise

if __name__ == "__main__":
    main()