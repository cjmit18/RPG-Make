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

# Import logging system
from logs.logs import get_logger, setup_logging

# Set up logging
setup_logging()
logger = get_logger("simple_demo")

# Import game system
from game_sys.character.character_factory import create_character
from game_sys.character.character_service import create_character_with_random_stats
from game_sys.combat.combat_service import CombatService
from game_sys.config.property_loader import PropertyLoader
from game_sys.config.config_manager import ConfigManager
from game_sys.core.damage_type_utils import get_damage_type_by_name, get_damage_type_properties
try:
    from game_sys.items.factory import ItemFactory
    from game_sys.items.item_loader import load_item
    from game_sys.magic.enchanting_system import EnchantingSystem
    ITEMS_AVAILABLE = True
    SPELLS_AVAILABLE = True
    ENCHANTING_AVAILABLE = True
except ImportError:
    ITEMS_AVAILABLE = False
    SPELLS_AVAILABLE = False
    ENCHANTING_AVAILABLE = False

# Default game configuration and toggles
GAME_CONFIG = {
    # Core system toggles
    'COMBAT_ENABLED': True,
    'MAGIC_ENABLED': True,
    'CRAFTING_ENABLED': True,
    'ENCHANTING_ENABLED': True,
    'DUAL_WIELD_ENABLED': True,
    'TWO_HANDED_ENABLED': True,
    'BLOCKING_ENABLED': True,
    'CRITICAL_HITS_ENABLED': True,
    'STATUS_EFFECTS_ENABLED': True,
    'LEARNING_SYSTEM_ENABLED': True,

    # Item quality/rarity system - now loaded from config
    'ITEM_RARITIES': PropertyLoader.get_item_rarities(),

    # Item grades - now loaded from config
    'ITEM_GRADES': PropertyLoader.get_item_grades(),

    # Damage types - now loaded from config
    'DAMAGE_TYPES': PropertyLoader.get_damage_types(),

    # Stat caps and defaults
    'STAT_DEFAULTS': {
        'base_stats': {
            'strength': 10, 'dexterity': 10, 'vitality': 10,
            'intelligence': 10, 'wisdom': 10, 'constitution': 10, 'luck': 10
        },
        'stat_caps': {
            'strength': 999, 'dexterity': 999, 'vitality': 999,
            'intelligence': 999, 'wisdom': 999, 'constitution': 999, 'luck': 999
        },
        'points_per_level': 5,
        'max_level': 100,
    },

    # Combat settings
    'COMBAT_SETTINGS': {
        'critical_chance_base': 0.05,  # 5% base crit chance
        'critical_multiplier': 2.0,    # 2x damage on crit
        'block_reduction': 0.5,        # 50% damage reduction when blocking
        'dodge_chance_base': 0.05,     # 5% base dodge chance
        'accuracy_base': 0.95,         # 95% base hit chance
    },

    # Magic settings
    'MAGIC_SETTINGS': {
        'mana_regen_rate': 1.0,        # Mana per second
        'spell_cooldown_enabled': True,
        'spell_components_required': False,
        'mana_burn_enabled': True,
    },

    # Quality of life settings
    'QOL_SETTINGS': {
        'auto_pickup_enabled': True,
        'auto_sort_inventory': False,
        'show_damage_numbers': True,
        'show_experience_gain': True,
        'fast_animations': False,
        'skip_intro': True,
    },

    # Debug settings
    'DEBUG_SETTINGS': {
        'god_mode': False,
        'infinite_mana': False,
        'infinite_stamina': False,
        'show_debug_info': False,
        'log_all_events': True,
    }
}

class SimpleGameDemo:
    """A simple game demo with logging and tabbed UI."""

    def __init__(self):
        """Initialize the demo."""
        logger.info("Initializing Simple Game Demo")

        # Create main window
        self.root = tk.Tk()
        self.root.title("Simple Game Demo")
        self.root.geometry("900x700")

        # Set up UI
        self.setup_ui()

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
        self.tab_control.add(self.leveling_tab, text="Leveling")  # Add leveling tab
        self.tab_control.add(self.enchanting_tab, text="Enchanting")  # Add enchanting tab

        # Add progression tab
        self.progression_tab = ttk.Frame(self.tab_control)
        self.tab_control.add(self.progression_tab, text="Progression")

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

        # Create log area
        self.log_frame = tk.Frame(self.root, bg="black")
        self.log_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=10)

        self.log = tk.Text(self.log_frame, bg="black", fg="white", height=8)
        self.log.pack(fill=tk.X)

        # Configure text tags
        self.log.tag_configure("info", foreground="cyan")
        self.log.tag_configure("combat", foreground="red")
        self.log.tag_configure("heal", foreground="green")

    def setup_stats_tab(self):
        """Set up the character stats tab."""
        # Left side: Character portrait and basic info
        left_frame = tk.Frame(self.stats_tab, bg="black")
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Character portrait area
        portrait_frame = tk.Frame(left_frame, bg="dark gray", width=200, height=200)
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
            height=10,
            bg="light gray",
            state="disabled"
        )
        self.basic_info.pack(fill=tk.X, pady=10)

        # Right side: Detailed stats
        right_frame = tk.Frame(self.stats_tab, bg="black")
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)

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
        button_frame = tk.Frame(self.stats_tab, bg="black")
        button_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=10)

        stat_buttons = [
            ("View Inventory", self.view_inventory),
            ("Level Up", self.level_up),
            ("Equip Gear", self.equip_gear),
            ("Restore Health", self.restore_health),
            ("Restore Mana", self.restore_mana),
            ("Restore Stamina", self.restore_stamina),
            ("Restore All", self.restore_all_resources),
        ]

        for text, command in stat_buttons:
            btn = tk.Button(button_frame, text=text, command=command)
            btn.pack(side=tk.LEFT, padx=5)

    def setup_combat_tab(self):
        """Set up the combat tab."""
        # Combat canvas for visualization
        self.canvas = tk.Canvas(
            self.combat_tab,
            bg="black",
            width=600,
            height=400
        )
        self.canvas.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Combat controls
        control_frame = tk.Frame(self.combat_tab, bg="gray")
        control_frame.pack(fill=tk.X, padx=10, pady=10)

        # Create combat buttons
        combat_buttons = [
            ("Attack", self.attack),
            ("Heal", self.heal),
            ("Spawn Enemy", self.spawn_enemy),
            ("Cast Fireball", self.cast_fireball),
            ("Cast Ice Shard", self.cast_ice_shard),
            ("Tick Status", self.tick_status_effects)
        ]

        for text, command in combat_buttons:
            btn = tk.Button(control_frame, text=text, command=command)
            btn.pack(side=tk.LEFT, padx=5, pady=5)

        # Enemy info
        self.enemy_info = tk.Text(
            self.combat_tab,
            width=25,
            height=5,
            bg="light gray",
            state="disabled"
        )
        self.enemy_info.pack(side=tk.RIGHT, padx=10, pady=10)

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

        # Initialize combat service
        self.combat_service = CombatService()

        # Initialize AI system
        try:
            from game_sys.ai.ai_demo_integration import AIDemoController
            self.ai_controller = AIDemoController(self.combat_service)
            self.ai_enabled = True
            logger.info("AI system initialized successfully")
        except ImportError as e:
            logger.warning(f"AI system not available: {e}")
            self.ai_controller = None
            self.ai_enabled = False

        # Create player character
        self.player = create_character(template_id="hero")
        if self.player:
            logger.info(f"Created player: {self.player.name}")
            self.log_message(f"Welcome, {self.player.name}!")

            # Initialize leveling system attributes for testing
            if not hasattr(self.player, 'experience'):
                self.player.experience = 0
            if not hasattr(self.player, 'level'):
                self.player.level = 1
            if not hasattr(self.player, 'spent_stat_points'):
                self.player.spent_stat_points = 0
                
            # Give some starting stat points for testing
            # Set level to 2 so they have 5 stat points available
            self.player.level = 2
            if not hasattr(self.player, 'available_stat_points'):
                self.player.available_stat_points = 5  # Start with 5 points for testing

            # Initialize enchanting system for player
            if ENCHANTING_AVAILABLE:
                self.player.enchanting_system = EnchantingSystem(self.player)
                self.log_message("Enchanting system initialized!")

            self.update_char_info()
            self.log_message("You have 5 stat points to allocate in the Leveling tab!", "info")
        else:
            logger.error("Failed to create player")
            self.log_message("Failed to create player!", "combat")

        # Create enemy with random stats
        self.enemy = create_character_with_random_stats("dragon")
        if self.enemy:
            logger.info(f"Created enemy: {self.enemy.name}")
            
            # Enable AI for the enemy
            if self.ai_enabled and self.ai_controller:
                ai_success = self.ai_controller.enable_ai_for_enemy(self.enemy)
                if ai_success:
                    self.log_message("AI enabled for enemy", "info")
                else:
                    self.log_message("Failed to enable AI for enemy", "combat")
            
            # Display enemy info with grade and rarity
            enemy_info = (f"A {self.enemy.name} appears! "
                         f"(Level {self.enemy.level}, "
                         f"Grade {self.enemy.grade}, "
                         f"Rarity {self.enemy.rarity})")
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

        # Clear current text
        self.basic_info.delete(1.0, tk.END)
        self.detailed_stats.delete(1.0, tk.END)

        # Build basic character info text
        basic_info = f"Name: {self.player.name}\n"
        basic_info += f"Level: {self.player.level}\n"
        
        # Add grade and rarity if available
        if hasattr(self.player, 'grade'):
            basic_info += f"Grade: {self.player.grade}\n"
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
            detailed_info += f"Grade: {self.player.grade}\n"
        if hasattr(self.player, 'rarity'):
            detailed_info += f"Rarity: {self.player.rarity}\n"
            
        detailed_info += f"Health: {health_val}\n"

        # Traditional RPG Stats (Base)
        detailed_info += "\n=== BASE STATS ===\n"
        if hasattr(self.player, 'base_stats'):
            rpg_stats = ['strength', 'dexterity', 'vitality', 'intelligence', 'wisdom', 'constitution', 'luck']
            for stat_name in rpg_stats:
                if stat_name in self.player.base_stats:
                    value = self.player.base_stats[stat_name]
                    display_name = stat_name.replace('_', ' ').title()
                    detailed_info += f"  {display_name}: {value:.2f}\n"

        # Combat Stats (Derived)
        detailed_info += "\n=== COMBAT STATS ===\n"
        combat_stats = ['attack', 'defense', 'speed', 'magic_power']
        for stat_name in combat_stats:
            if hasattr(self.player, 'get_stat'):
                value = self.player.get_stat(stat_name)
                display_name = stat_name.replace('_', ' ').title()
                detailed_info += f"  {display_name}: {value:.1f}\n"

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
            info += f"Grade: {self.enemy.grade}\n"
        if hasattr(self.enemy, 'rarity'):
            info += f"Rarity: {self.enemy.rarity}\n"
            
        health_val = f"{self.enemy.current_health:.2f}/"
        health_val += f"{self.enemy.max_health:.2f}"
        info += f"Health: {health_val}\n"

        # Add attributes if available (safely)
        if hasattr(self.enemy, 'strength'):
            str_val = getattr(self.enemy, 'strength', 'N/A')
            info += f"Strength: {str_val}\n"

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
                # Give enough XP to level up
                xp_needed = self.player.level * 100  # Simple XP calculation
                self.player.leveling_manager.gain_experience(
                    actor=self.player,
                    amount=xp_needed
                )
            else:
                # Manual level up
                self.player.level += 1

            # Check if level actually increased
            if self.player.level > old_level:
                # Award stat points for the level up
                points_gained = self.player.level - old_level
                if hasattr(self.player.leveling_manager, 'add_stat_points'):
                    self.player.leveling_manager.add_stat_points(
                        self.player,
                        points_gained * 3  # 3 points per level
                    )

                msg = f"Level up! Now level {self.player.level} (+{points_gained * 3} stat points)!"
                self.log_message(msg, "info")
            else:
                # Force a level up if manager didn't do it
                self.player.level += 1
                if hasattr(self.player.leveling_manager, 'add_stat_points'):
                    self.player.leveling_manager.add_stat_points(self.player, 3)
                msg = f"Level up! Now level {self.player.level} (+3 stat points)!"
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

        # Update displays
        self.update_char_info()
        if hasattr(self, 'update_leveling_display'):
            self.update_leveling_display()

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
            # Spell failed
            self.log_message(f"Fireball failed: {result['message']}", "combat")

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

            # Background
            self.canvas.create_rectangle(
                player_x - bar_width/2, player_y + 40,
                player_x + bar_width/2, player_y + 50,
                fill="gray", outline="white"
            )

            # Health
            self.canvas.create_rectangle(
                player_x - bar_width/2, player_y + 40,
                player_x - bar_width/2 + bar_width * health_pct, player_y + 50,
                fill="red", outline=""
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
            health_pct = self.enemy.current_health / self.enemy.max_health
            bar_width = 100

            # Background
            self.canvas.create_rectangle(
                enemy_x - bar_width/2, enemy_y + 40,
                enemy_x + bar_width/2, enemy_y + 50,
                fill="gray", outline="white"
            )

            # Health
            self.canvas.create_rectangle(
                enemy_x - bar_width/2, enemy_y + 40,
                enemy_x - bar_width/2 + bar_width * health_pct, enemy_y + 50,
                fill="red", outline=""
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
                
                # Display loot if any was generated
                if result['loot']:
                    loot_names = [item.name for item in result['loot']]
                    loot_msg = f"Loot obtained: {', '.join(loot_names)}"
                    self.log_message(loot_msg, "info")
                
                self.enemy = None
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

    def quit(self):
        """Quit the demo."""
        logger.info("Exiting demo")
        self.root.destroy()

    def run(self):
        """Run the demo."""
        logger.info("Starting demo")

        # Add quit button to main window
        quit_btn = tk.Button(self.root, text="Quit Game", command=self.quit)
        quit_btn.pack(side=tk.BOTTOM, pady=5)

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
            "orch_axe",
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
        """Create an item and add it to inventory."""
        if not hasattr(self, 'player') or not self.player:
            self.log_message("No player character available!", "combat")
            return

        if not hasattr(self.player, 'inventory'):
            self.log_message("No inventory system available!", "combat")
            return

        try:
            # Create the item using ItemFactory
            if not ITEMS_AVAILABLE:
                self.log_message("Items system not available!", "combat")
                return

            # Import locally to avoid linting issues
            from game_sys.items.factory import ItemFactory
            item = ItemFactory.create(item_id)
            if item:
                # Try to add to inventory
                if hasattr(self.player.inventory, 'add_item'):
                    success = self.player.inventory.add_item(item)
                    if success:
                        msg = f"Created and added {item.name} to inventory!"
                        self.log_message(msg, "info")
                    else:
                        self.log_message("Inventory full!", "combat")
                else:
                    msg = "No inventory add method available"
                    self.log_message(msg, "combat")
                    return

                self.update_inventory_display()
                self.update_equipment_display()
            else:
                self.log_message(f"Failed to create item: {item_id}", "combat")
        except Exception as e:
            self.log_message(f"Error creating item {item_id}: {e}", "combat")

    def add_random_item(self):
        """Add a random item to inventory."""
        if not ITEMS_AVAILABLE:
            self.log_message("Items system not available!", "combat")
            return

        # Pick a random item from available items
        item_count = self.available_items_listbox.size()
        if item_count == 0:
            return

        random_index = random.randint(0, item_count - 1)
        item_id = self.available_items_listbox.get(random_index)
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

                # Check if item is consumable or has active abilities
                is_consumable = (
                    (hasattr(item, 'consumable') and item.consumable) or
                    (hasattr(item, 'item_type') and
                     item.item_type == 'consumable') or
                    'potion' in item.name.lower()
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
                        msg = f"Used {item.name}!"
                    elif is_consumable:
                        # Basic consumable (e.g., health potion)
                        if 'health' in item.name.lower():
                            heal_amount = getattr(item, 'heal_amount', 25)
                            old_health = self.player.current_health
                            new_health = min(
                                self.player.current_health + heal_amount,
                                self.player.max_health
                            )
                            self.player.current_health = new_health
                            actual_heal = new_health - old_health
                            item_name = item.name
                            heal_val = f"+{actual_heal:.1f}HP"
                            heal_msg = f"Used {item_name}! {heal_val}"
                            msg = heal_msg
                        else:
                            msg = f"Used {item.name}! (simulated effect)"
                    else:
                        msg = f"Activated {item.name}!"

                    self.log_message(msg, "heal")

                    # Remove consumable items from inventory
                    if is_consumable:
                        self.player.inventory.remove_item(item)

                    self.update_inventory_display()
                    self.update_char_info()
                else:
                    msg = f"Cannot use {item.name} - not consumable or usable"
                    self.log_message(msg, "info")
        except Exception as e:
            self.log_message(f"Error using item: {e}", "combat")

    def equip_selected_item(self):
        """Equip the selected inventory item."""
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
            items = self.player.inventory.list_items()
            if selection[0] < len(items):
                item = items[selection[0]]

                # Use the item's apply method which handles equipping
                if hasattr(item, 'apply'):
                    item.apply(self.player)

                    # Remove item from inventory after equipping
                    self.player.inventory.remove_item(item)

                    self.log_message(f"Equipped {item.name}!", "info")
                elif hasattr(item, 'slot'):
                    # Use smart equipping for weapons that handles dual wield
                    if (item.slot in ["weapon", "offhand"] or
                        getattr(item, 'dual_wield', False)):
                        if hasattr(self.player, 'equip_weapon_smart'):
                            success = self.player.equip_weapon_smart(item)
                            if success:
                                # Remove item from inventory after equipping
                                self.player.inventory.remove_item(item)
                                msg = f"Equipped {item.name}!"
                                self.log_message(msg, "info")
                            else:
                                msg = f"Failed to equip {item.name}"
                                self.log_message(msg, "combat")
                        else:
                            # Fallback to regular weapon equipping
                            if hasattr(self.player, 'equip_weapon'):
                                self.player.equip_weapon(item)
                                self.player.inventory.remove_item(item)
                                msg = f"Equipped weapon: {item.name}"
                                self.log_message(msg, "info")
                    elif item.slot in ["body", "helmet", "legs", "feet", "gloves", "boots", "cloak"]:
                        # Use proper armor equipping method
                        if hasattr(self.player, 'equip_armor'):
                            success = self.player.equip_armor(item)
                            if success:
                                msg = f"Equipped {item.slot}: {item.name}"
                                self.log_message(msg, "info")
                            else:
                                msg = f"Failed to equip {item.name}"
                                self.log_message(msg, "combat")
                        else:
                            # Fallback for older actor without equip_armor method
                            slot_attr = f"equipped_{item.slot}"
                            setattr(self.player, slot_attr, item)
                            self.player.inventory.remove_item(item)
                            self.player.update_stats()
                            msg = f"Equipped {item.slot}: {item.name}"
                            self.log_message(msg, "info")
                    else:
                        msg = f"Cannot equip {item.name} - unknown slot: {item.slot}"
                        self.log_message(msg, "combat")
                else:
                    msg = f"Cannot equip {item.name} - not equipment"
                    self.log_message(msg, "combat")

                self.update_inventory_display()
                self.update_equipment_display()
                self.update_char_info()
        except Exception as e:
            self.log_message(f"Error equipping item: {e}", "combat")

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
                success = self.player.inventory.remove_item(item)
                if success:
                    self.log_message(f"Dropped {item.name}", "info")
                else:
                    self.log_message(f"Could not drop {item.name}", "combat")
                self.update_inventory_display()
        except Exception as e:
            self.log_message(f"Error dropping item: {e}", "combat")

    def update_inventory_display(self):
        """Update the inventory display."""
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
                    # Just show item name for now
                    display_text = getattr(item, 'name', str(item))
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
        """Unequip an item from the specified slot."""
        if not hasattr(self, 'player') or not self.player:
            self.log_message("No player character available!", "combat")
            return

        try:
            if slot == "weapon":
                if hasattr(self.player, 'weapon') and self.player.weapon:
                    # Use the player's unequip_weapon method which returns the item
                    unequipped_weapon = self.player.unequip_weapon()

                    if unequipped_weapon:
                        # The unequip_weapon method already adds to inventory
                        msg = f"Unequipped weapon: {unequipped_weapon.name} (returned to inventory)"
                        self.log_message(msg, "info")
                    else:
                        self.log_message("Failed to unequip weapon", "combat")
                else:
                    self.log_message("No weapon equipped", "info")

            elif slot == "offhand":
                if hasattr(self.player, 'offhand') and self.player.offhand:
                    # Use the player's unequip_offhand method which returns the item
                    unequipped_offhand = self.player.unequip_offhand()

                    if unequipped_offhand:
                        # The unequip_offhand method already adds to inventory
                        msg = f"Unequipped offhand: {unequipped_offhand.name} (returned to inventory)"
                        self.log_message(msg, "info")
                    else:
                        self.log_message("Failed to unequip offhand", "combat")
                else:
                    self.log_message("No offhand item equipped", "info")

            elif slot == "body":
                # Use the actor's unequip_armor method
                if hasattr(self.player, 'unequip_armor'):
                    unequipped_item = self.player.unequip_armor("body")
                    if unequipped_item:
                        # The unequip_armor method already adds to inventory
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

        # Current allocatable stats display
        stats_frame = tk.Frame(left_frame, bg="dark gray")
        stats_frame.pack(fill=tk.BOTH, expand=True)

        tk.Label(
            stats_frame,
            text="Allocatable Stats:",
            bg="dark gray",
            fg="white",
            font=("Arial", 12, "bold")
        ).pack(anchor="w", pady=(0, 5))

        self.allocatable_stats_text = tk.Text(
            stats_frame,
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
        
        # Get actual stats from the player character if available
        if hasattr(self, 'player') and self.player:
            # Use actual character stats
            allocatable_stats = list(self.player.base_stats.keys())
        else:
            # Fallback to common stats
            allocatable_stats = [
                'attack', 'defense', 'speed', 'health', 'mana', 'stamina', 'magic_power',
                'strength', 'dexterity', 'vitality', 'intelligence', 'wisdom', 'constitution', 'luck'
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
                available_points = getattr(self.player.leveling_manager, 'available_stat_points', 0)
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
                    15: ["orch_axe", "arcane_focus"],
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
                    15: ["orch_axe", "arcane_focus"],
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

                    # Return the points
                    if not hasattr(self.player, 'available_stat_points'):
                        self.player.available_stat_points = 0
                    self.player.available_stat_points += points_to_return

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
                    
                    # Add stat points manually (3 per level)
                    if not hasattr(self.player, 'available_stat_points'):
                        self.player.available_stat_points = 0
                    self.player.available_stat_points += 3
                    
                    msg = f"Gained {xp_amount} XP and leveled up! Level {self.player.level}"
                    self.log_message(msg, "info")
                    self.log_message(f"You now have {self.player.available_stat_points} stat points!", "info")
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
                # Manual stat allocation fallback
                available_points = getattr(self.player, 'available_stat_points', 0)
                
                if available_points <= 0:
                    self.log_message("No stat points available!", "combat")
                    return
                
                if hasattr(self.player, 'base_stats'):
                    if stat_name in self.player.base_stats:
                        self.player.base_stats[stat_name] += 1.0
                        self.player.available_stat_points -= 1

                        # Update derived stats
                        if hasattr(self.player, 'update_stats'):
                            self.player.update_stats()

                        msg = f"Allocated 1 point to {stat_name}! ({self.player.available_stat_points} remaining)"
                        self.log_message(msg, "info")
                    else:
                        msg = f"Stat {stat_name} not found!"
                        self.log_message(msg, "combat")
                else:
                    msg = "No stats system available"
                    self.log_message(msg, "combat")

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
                elif hasattr(self.player, 'available_stat_points'):
                    # Fallback to manual stat points
                    self.available_points_label.config(text=str(self.player.available_stat_points))
                else:
                    # Initialize stat points if not present
                    if not hasattr(self.player, 'available_stat_points'):
                        self.player.available_stat_points = 0
                    self.available_points_label.config(text="0")

            # Update allocatable stats display
            if hasattr(self, 'allocatable_stats_text'):
                self.allocatable_stats_text.config(state="normal")
                self.allocatable_stats_text.delete(1.0, tk.END)

                if hasattr(self.player, 'base_stats'):
                    stats_text = "=== BASE STATS ===\n"
                    
                    # Show base stats organized by category
                    rpg_stats = ['strength', 'dexterity', 'vitality', 'intelligence', 'wisdom', 'constitution', 'luck']
                    combat_stats = ['attack', 'defense', 'speed', 'magic_power']
                    resource_stats = ['health', 'mana', 'stamina']
                    
                    # RPG Stats
                    stats_text += "\nCore Attributes:\n"
                    for stat in rpg_stats:
                        if stat in self.player.base_stats:
                            base_val = self.player.base_stats[stat]
                            effective_val = self.player.get_stat(stat) if hasattr(self.player, 'get_stat') else base_val
                            if abs(base_val - effective_val) > 0.01:
                                stats_text += f"{stat.title():<15}: {base_val:>6.1f} → {effective_val:>6.1f}\n"
                            else:
                                stats_text += f"{stat.title():<15}: {base_val:>8.1f}\n"
                    
                    # Combat Stats
                    stats_text += "\nCombat Stats:\n"
                    for stat in combat_stats:
                        if stat in self.player.base_stats:
                            base_val = self.player.base_stats[stat]
                            effective_val = self.player.get_stat(stat) if hasattr(self.player, 'get_stat') else base_val
                            if abs(base_val - effective_val) > 0.01:
                                stats_text += f"{stat.title():<15}: {base_val:>6.1f} → {effective_val:>6.1f}\n"
                            else:
                                stats_text += f"{stat.title():<15}: {base_val:>8.1f}\n"
                    
                    # Resource Stats 
                    stats_text += "\nResource Stats:\n"
                    for stat in resource_stats:
                        if stat in self.player.base_stats:
                            base_val = self.player.base_stats[stat]
                            effective_val = self.player.get_stat(stat) if hasattr(self.player, 'get_stat') else base_val
                            if abs(base_val - effective_val) > 0.01:
                                stats_text += f"{stat.title():<15}: {base_val:>6.1f} → {effective_val:>6.1f}\n"
                            else:
                                stats_text += f"{stat.title():<15}: {base_val:>8.1f}\n"
                    
                    # Other base stats not in categories above
                    other_stats = [s for s in sorted(self.player.base_stats.keys()) 
                                 if s not in rpg_stats + combat_stats + resource_stats]
                    if other_stats:
                        stats_text += "\nOther Stats:\n"
                        for stat in other_stats:
                            base_val = self.player.base_stats[stat]
                            effective_val = self.player.get_stat(stat) if hasattr(self.player, 'get_stat') else base_val
                            if abs(base_val - effective_val) > 0.01:
                                stats_text += f"{stat.title():<15}: {base_val:>6.1f} → {effective_val:>6.1f}\n"
                            else:
                                stats_text += f"{stat.title():<15}: {base_val:>8.1f}\n"

                    # Add derived stats that aren't base stats
                    stats_text += "\n=== DERIVED STATS ===\n"
                    derived_stats = ['dodge_chance', 'block_chance', 'magic_resistance', 'damage_reduction',
                                   'health_regeneration', 'mana_regeneration', 'stamina_regeneration',
                                   'critical_chance', 'luck_factor', 'physical_damage']
                    
                    for stat in derived_stats:
                        if hasattr(self.player, 'get_stat'):
                            try:
                                value = self.player.get_stat(stat)
                                if 'chance' in stat or 'factor' in stat:
                                    stats_text += f"{stat.replace('_', ' ').title():<15}: {value:>7.1%}\n"
                                elif 'regeneration' in stat:
                                    stats_text += f"{stat.replace('_', ' ').title():<15}: {value:>7.3f}/s\n"
                                else:
                                    stats_text += f"{stat.replace('_', ' ').title():<15}: {value:>8.2f}\n"
                            except:
                                # Skip stats that can't be calculated
                                pass

                    # Add level and XP info
                    stats_text += f"\n=== PROGRESSION ===\n"
                    stats_text += f"Level: {getattr(self.player, 'level', 1)}\n"
                    stats_text += f"Experience: {getattr(self.player, 'experience', 0)}\n"
                    
                    # Show stat points info
                    if hasattr(self.player, 'leveling_manager'):
                        available = self.player.leveling_manager.calculate_stat_points_available(self.player)
                        spent = getattr(self.player, 'spent_stat_points', 0)
                        stats_text += f"Stat Points Available: {available}\n"
                        stats_text += f"Stat Points Spent: {spent}\n"
                    elif hasattr(self.player, 'available_stat_points'):
                        stats_text += f"Stat Points Available: {self.player.available_stat_points}\n"

                    # Add current resource values
                    stats_text += "\n=== CURRENT RESOURCES ===\n"
                    if hasattr(self.player, 'current_health'):
                        stats_text += f"{'Health':<15}: {self.player.current_health:>8.1f} / {self.player.max_health:>8.1f}\n"
                        if hasattr(self.player, 'current_mana'):
                            stats_text += f"{'Mana':<15}: {self.player.current_mana:>8.1f} / {self.player.max_mana:>8.1f}\n"
                        if hasattr(self.player, 'current_stamina'):
                            stats_text += f"{'Stamina':<15}: {self.player.current_stamina:>8.1f} / {self.player.max_stamina:>8.1f}\n"

                    self.allocatable_stats_text.insert(tk.END, stats_text)
                else:
                    self.allocatable_stats_text.insert(tk.END, "No stats system available")

                self.allocatable_stats_text.config(state="disabled")

            # Update stat buttons values and enable/disable based on available points
            if hasattr(self, 'stat_buttons') and hasattr(self.player, 'base_stats'):
                # Get available points for button state
                if hasattr(self.player, 'leveling_manager'):
                    available_points = self.player.leveling_manager.calculate_stat_points_available(self.player)
                else:
                    available_points = getattr(self.player, 'available_stat_points', 0)
                
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
                                # Just show the value since they're the same
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
