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
from game_sys.combat.engine import CombatEngine
try:
    from game_sys.items.factory import ItemFactory
    from game_sys.items.item_loader import load_item
    from game_sys.magic.spell_loader import load_spell
    ITEMS_AVAILABLE = True
    SPELLS_AVAILABLE = True
except ImportError:
    ITEMS_AVAILABLE = False
    SPELLS_AVAILABLE = False

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
    
    # Item quality/rarity system
    'ITEM_RARITIES': {
        'common': {'color': 'white', 'multiplier': 1.0, 'prefix': ''},
        'uncommon': {'color': 'green', 'multiplier': 1.2, 'prefix': 'Fine '},
        'rare': {'color': 'blue', 'multiplier': 1.5, 'prefix': 'Rare '},
        'epic': {'color': 'purple', 'multiplier': 2.0, 'prefix': 'Epic '},
        'legendary': {'color': 'orange', 'multiplier': 3.0, 'prefix': 'Legendary '},
        'artifact': {'color': 'red', 'multiplier': 5.0, 'prefix': 'Artifact '},
    },
    
    # Item grades
    'ITEM_GRADES': {
        'poor': {'color': 'gray', 'multiplier': 0.8, 'suffix': ' (Poor)'},
        'normal': {'color': 'white', 'multiplier': 1.0, 'suffix': ''},
        'superior': {'color': 'yellow', 'multiplier': 1.3, 'suffix': ' (Superior)'},
        'masterwork': {'color': 'cyan', 'multiplier': 1.6, 'suffix': ' (Masterwork)'},
        'perfect': {'color': 'gold', 'multiplier': 2.0, 'suffix': ' (Perfect)'},
    },
    
    # Damage types
    'DAMAGE_TYPES': {
        'physical': {'name': 'Physical', 'color': 'white'},
        'fire': {'name': 'Fire', 'color': 'red'},
        'ice': {'name': 'Ice', 'color': 'cyan'},
        'lightning': {'name': 'Lightning', 'color': 'yellow'},
        'poison': {'name': 'Poison', 'color': 'green'},
        'holy': {'name': 'Holy', 'color': 'gold'},
        'shadow': {'name': 'Shadow', 'color': 'purple'},
        'arcane': {'name': 'Arcane', 'color': 'magenta'},
    },
    
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
        
        # Create player character
        self.player = create_character(template_id="hero")
        if self.player:
            logger.info(f"Created player: {self.player.name}")
            self.log_message(f"Welcome, {self.player.name}!")
            self.update_char_info()
        else:
            logger.error("Failed to create player")
            self.log_message("Failed to create player!", "combat")
        
        # Create enemy
        self.enemy = create_character("dragon")
        if self.enemy:
            logger.info(f"Created enemy: {self.enemy.name}")
            self.log_message(f"A {self.enemy.name} appears!", "combat")
            self.update_enemy_info()
        else:
            logger.error("Failed to create enemy")
        
        # Draw game state
        self.draw_game_state()
        
        # Update inventory displays if available
        if hasattr(self, 'inventory_listbox'):
            self.update_inventory_display()
            self.update_equipment_display()
    
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
        health_val = f"{self.player.current_health:.2f}/"
        health_val += f"{self.player.max_health:.2f}"
        basic_info += f"Health: {health_val}\n"
        
        # Insert basic text
        self.basic_info.insert(tk.END, basic_info)
        
        # Build detailed character info
        detailed_info = f"== {self.player.name} ==\n"
        detailed_info += f"Level: {self.player.level}\n"
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
        health_val = f"{self.enemy.current_health:.2f}/"
        health_val += f"{self.enemy.max_health:.2f}"
        info += f"Health: {health_val}\n"
        
        # Add attributes if available (safely)
        if hasattr(self.enemy, 'strength'):
            str_val = getattr(self.enemy, 'strength', 'N/A')
            info += f"Strength: {str_val}\n"
        
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
        
        # Check mana
        if self.player.current_mana < 20:  # Fireball costs 20 mana
            self.log_message("Not enough mana to cast Fireball!", "combat")
            return
            
        # Load and cast fireball
        try:
            if not SPELLS_AVAILABLE:
                self.log_message("Spell system not available!", "combat")
                return
                
            fireball = load_spell("fireball")
            if fireball:
                # Apply spell damage directly for demo purposes
                intel = getattr(self.player, 'intelligence', 0)
                damage = fireball.base_power + (intel * 2)
                self.player.current_mana -= fireball.mana_cost
                
                # Apply damage to enemy
                self.enemy.take_damage(damage)
                
                # Apply burn effect if available
                if hasattr(fireball, 'effects') and fireball.effects:
                    for effect in fireball.effects:
                        try:
                            # Handle StatusEffect objects (preferred)
                            if hasattr(effect, 'apply'):
                                # Apply the effect using the engine's built-in method
                                effect.apply(self.player, self.enemy)
                                
                                # Get effect name for logging
                                effect_name = getattr(effect, 'name', 'unknown effect')
                                
                                # Special handling for burn effects
                                if effect_name == 'burn':
                                    duration = getattr(effect, 'duration', 5)
                                    tick_dmg = getattr(effect, 'tick_damage', 1)
                                    
                                    # Try to register with status manager for proper ticking
                                    try:
                                        from game_sys.effects.status_manager import status_manager
                                        if self.enemy not in status_manager.actors:
                                            status_manager.register_actor(self.enemy)
                                        msg = f"Enemy burns for {duration}s ({tick_dmg} dmg/tick)!"
                                    except (ImportError, AttributeError):
                                        msg = f"Enemy burns for {duration}s!"
                                    
                                    self.log_message(msg, "combat")
                                else:
                                    self.log_message(f"Applied {effect_name} to enemy!", "combat")
                                    
                            elif isinstance(effect, dict) and effect.get('type') == 'status':
                                # Handle dict-based effects (fallback/legacy support)
                                params = effect.get('params', {})
                                if params.get('name') == 'burn':
                                    duration = params.get('duration', 5)
                                    tick_dmg = params.get('tick_damage', 1)
                                    msg = f"Enemy burns for {duration}s!"
                                    self.log_message(msg, "combat")
                                else:
                                    effect_name = params.get('name', 'unknown')
                                    self.log_message(f"Applied {effect_name} to enemy!", "combat")
                            else:
                                # Unknown effect type - just log something generic
                                self.log_message("Applied magical effect to enemy!", "combat")
                                
                        except Exception as effect_error:
                            # Log effect application errors but continue
                            self.log_message(f"Effect application error: {effect_error}", "combat")
                            print(f"DEBUG: Effect error details: {effect_error}")  # For debugging
                
                # Log spell cast
                player_name = self.player.name
                cast_msg = f"{player_name} casts Fireball ({damage} fire dmg)!"
                self.log_message(cast_msg, "combat")
                
                # Create visual effect
                self.create_particles(450, 200, "orange", 25)
                
                # Check if enemy defeated
                if self.enemy.current_health <= 0:
                    defeat_msg = f"{self.enemy.name} is defeated by magic!"
                    self.log_message(defeat_msg, "combat")
                    self.enemy = None
            else:
                self.log_message("Failed to load Fireball spell!", "combat")
                
        except Exception as e:
            self.log_message(f"Error casting Fireball: {e}", "combat")
        
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
        
        # Check mana
        if self.player.current_mana < 15:  # Ice shard costs 15 mana
            self.log_message("Not enough mana to cast Ice Shard!", "combat")
            return
            
        # Load and cast ice shard
        try:
            from game_sys.magic.spell_loader import load_spell
            ice_shard = load_spell("ice_shard")
            if ice_shard:
                # Apply spell damage directly for demo purposes
                intel = getattr(self.player, 'intelligence', 0)
                damage = ice_shard.base_power + (intel * 1.5)
                self.player.current_mana -= ice_shard.mana_cost
                
                # Apply damage to enemy
                self.enemy.take_damage(damage)
                
                # Apply spell effects (like slow/debuff)
                if hasattr(ice_shard, 'effects') and ice_shard.effects:
                    for effect in ice_shard.effects:
                        try:
                            # Handle effect objects (preferred)
                            if hasattr(effect, 'apply'):
                                effect.apply(self.player, self.enemy)
                                
                                # Get effect information for better messaging
                                if hasattr(effect, 'id') and 'debuff_speed' in effect.id:
                                    # Parse the debuff effect ID (e.g., "debuff_speed_-0.2_3")
                                    parts = effect.id.split('_')
                                    if len(parts) >= 4:
                                        stat = parts[1]  # "speed"
                                        amount = abs(float(parts[2]))  # 0.2
                                        duration = parts[3]  # "3"
                                        msg = f"Enemy {stat} reduced by {amount} for {duration}s!"
                                        self.log_message(msg, "combat")
                                    else:
                                        self.log_message("Applied speed debuff!", "combat")
                                elif hasattr(effect, '__class__') and 'Debuff' in effect.__class__.__name__:
                                    # Generic debuff effect
                                    effect_type = effect.__class__.__name__.replace('Effect', '').lower()
                                    self.log_message(f"Applied {effect_type}!", "combat")
                                else:
                                    # Try to get a meaningful effect name
                                    effect_name = 'magical effect'
                                    if hasattr(effect, 'name'):
                                        effect_name = effect.name
                                    elif hasattr(effect, 'id'):
                                        effect_name = effect.id.replace('_', ' ')
                                    elif hasattr(effect, '__class__'):
                                        effect_name = effect.__class__.__name__.replace('Effect', '').lower()
                                    
                                    self.log_message(f"Applied {effect_name}!", "combat")
                                    
                            elif isinstance(effect, dict):
                                # Handle dict-based effects (fallback)
                                effect_type = effect.get('type', 'unknown')
                                params = effect.get('params', {})
                                if effect_type == 'debuff':
                                    stat = params.get('stat', 'unknown')
                                    amount = params.get('amount', 0)
                                    duration = params.get('duration', 0)
                                    msg = f"Enemy {stat} reduced by {abs(amount)} for {duration}s!"
                                    self.log_message(msg, "combat")
                                else:
                                    self.log_message("Applied magical effect!", "combat")
                        except Exception as effect_error:
                            self.log_message(f"Effect error: {effect_error}", "combat")
                
                # Log spell cast
                player_name = self.player.name
                cast_msg = f"{player_name} casts Ice Shard ({damage} ice dmg)!"
                self.log_message(cast_msg, "combat")
                
                # Create visual effect
                self.create_particles(450, 200, "cyan", 20)
                
                # Check if enemy defeated
                if self.enemy.current_health <= 0:
                    enemy_name = self.enemy.name
                    msg = f"{enemy_name} is frozen solid!"
                    self.log_message(msg, "combat")
                    self.enemy = None
            else:
                self.log_message("Failed to load Ice Shard spell!", "combat")
                
        except Exception as e:
            self.log_message(f"Error casting Ice Shard: {e}", "combat")
        
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

        # Calculate damage using weapon and stats
        base_damage = 0
        
        # Get weapon damage
        if hasattr(self.player, 'weapon') and self.player.weapon:
            base_damage = getattr(self.player.weapon, 'base_damage', 5)
        else:
            base_damage = 3  # Unarmed damage
            
        # Add attack stat bonus
        attack_bonus = 0
        if hasattr(self.player, 'base_stats'):
            attack_bonus = self.player.base_stats.get('attack', 0)
            
        # Calculate total damage with some randomness
        min_damage = max(1, int(base_damage + attack_bonus * 0.5))
        max_damage = int(base_damage + attack_bonus * 1.5)
        damage = random.randint(min_damage, max_damage)

        # Apply damage to enemy
        self.enemy.take_damage(damage)
        
        # Log attack
        logger.info(f"{self.player.name} attacks for {damage} damage")
        
        # Format combat message
        player_name = self.player.name
        enemy_name = self.enemy.name
        weapon_info = ""
        if hasattr(self.player, 'weapon') and self.player.weapon:
            weapon_info = f" with {self.player.weapon.name}"
        msg = f"{player_name} attacks {enemy_name}{weapon_info} for {damage} damage!"
        self.log_message(msg, "combat")
        
        # Create visual effect
        self.create_particles(450, 200, "red", 15)
        
        # Check if enemy defeated
        if self.enemy.current_health <= 0:
            logger.info(f"{self.enemy.name} defeated")
            self.log_message(f"{self.enemy.name} is defeated!", "combat")
            self.enemy = None
        
        # Update displays
        self.update_enemy_info()
        self.draw_game_state()
    
    def heal(self):
        """Heal the player."""
        if not hasattr(self, 'player') or not self.player:
            logger.warning("No player to heal")
            return
        
        # Calculate healing
        heal_amount = random.randint(5, 15)
        
        # Apply healing
        self.player.current_health = min(
            self.player.current_health + heal_amount,
            self.player.max_health
        )
        
        # Log healing
        logger.info(f"Healed player for {heal_amount}")
        self.log_message(f"You are healed for {heal_amount} health!", "heal")
        
        # Create visual effect
        self.create_particles(150, 200, "green", 15)
        
        # Update displays
        self.update_char_info()
        self.draw_game_state()
    
    def spawn_enemy(self):
        """Spawn a new enemy."""
        enemy_types = ["goblin", "Orc","Dragon"]
        enemy_type = random.choice(enemy_types)
        
        logger.info(f"Spawning {enemy_type}")
        
        # Create enemy
        self.enemy = create_character(enemy_type)
        
        if self.enemy:
            logger.info(f"Created enemy: {self.enemy.name}")
            self.log_message(f"A {self.enemy.name} appears!", "combat")
            
            # Create visual effect
            self.create_particles(450, 200, "blue", 15)
            
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
            
        # Add some common items that should be available
        available_items = [
            "potion_health",
            "iron_sword", 
            "leather_armor",
            "wooden_shield",
            "iron_dagger",
            "wooden_stick",
            "basic_clothes",
            "apprentice_staff",
            "mage_robes"
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
                        details += f"  +{value} {stat.replace('_', ' ').title()}\n"
                        
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
            self.log_message("Please select an item to create from the available items list", "info")
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
                    # Manual equipping based on slot
                    if (item.slot == "weapon" and
                            hasattr(self.player, 'equip_weapon')):
                        self.player.equip_weapon(item)
                        self.player.inventory.remove_item(item)
                        msg = f"Equipped weapon: {item.name}"
                        self.log_message(msg, "info")
                    elif (item.slot == "offhand" and
                          hasattr(self.player, 'equip_offhand')):
                        self.player.equip_offhand(item)
                        self.player.inventory.remove_item(item)
                        msg = f"Equipped offhand: {item.name}"
                        self.log_message(msg, "info")
                    elif item.slot in ["body", "helmet", "legs", "feet"]:
                        # Handle armor pieces by setting them directly
                        slot_attr = f"equipped_{item.slot}"
                        setattr(self.player, slot_attr, item)
                        
                        # Apply armor stats if available
                        if hasattr(item, 'stats'):
                            for stat_name, bonus in item.stats.items():
                                current_val = self.player.base_stats.get(
                                    stat_name, 0.0)
                                new_val = current_val + bonus
                                self.player.base_stats[stat_name] = new_val
                        
                        self.player.inventory.remove_item(item)
                        self.player.update_stats()
                        msg = f"Equipped {item.slot}: {item.name}"
                        self.log_message(msg, "info")
                    else:
                        msg = f"Cannot equip {item.name} - unknown slot"
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
            if not items:
                self.inventory_listbox.insert(tk.END, "(Empty)")
                self.inventory_listbox.insert(tk.END, "")
                self.inventory_listbox.insert(tk.END, "Note: Starting equipment")
                self.inventory_listbox.insert(tk.END, "is automatically equipped")
                self.inventory_listbox.insert(tk.END, "and shown in equipment")
            else:
                for item in items:
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
                        # Add weapon back to inventory
                        if hasattr(self.player, 'inventory'):
                            success = self.player.inventory.add_item(unequipped_weapon)
                            if success:
                                msg = f"Unequipped weapon: {unequipped_weapon.name} (returned to inventory)"
                                self.log_message(msg, "info")
                            else:
                                msg = f"Unequipped weapon: {unequipped_weapon.name} (inventory full!)"
                                self.log_message(msg, "info")
                        else:
                            self.log_message(f"Unequipped weapon: {unequipped_weapon.name}", "info")
                    else:
                        self.log_message("Failed to unequip weapon", "combat")
                else:
                    self.log_message("No weapon equipped", "info")
                    
            elif slot == "offhand":
                if hasattr(self.player, 'offhand') and self.player.offhand:
                    # Use the player's unequip_offhand method which returns the item
                    unequipped_offhand = self.player.unequip_offhand()
                    
                    if unequipped_offhand:
                        # Add offhand back to inventory
                        if hasattr(self.player, 'inventory'):
                            success = self.player.inventory.add_item(unequipped_offhand)
                            if success:
                                msg = f"Unequipped offhand: {unequipped_offhand.name} (returned to inventory)"
                            else:
                                msg = f"Unequipped offhand: {unequipped_offhand.name} (inventory full!)"
                        else:
                            msg = f"Unequipped offhand: {unequipped_offhand.name}"
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
                        # Add armor back to inventory
                        if hasattr(self.player, 'inventory'):
                            success = self.player.inventory.add_item(unequipped_item)
                            if success:
                                msg = f"Unequipped body armor: {unequipped_item.name} (added to inventory)"
                            else:
                                msg = f"Unequipped body armor: {unequipped_item.name} (inventory full!)"
                        else:
                            msg = f"Unequipped body armor: {unequipped_item.name}"
                        self.log_message(msg, "info")
                    else:
                        self.log_message("No body armor equipped", "info")
                else:
                    # Fallback to manual unequipping
                    body_attr = getattr(self.player, 'equipped_body', None)
                    if body_attr:
                        item_name = body_attr.name
                        # Remove the armor item and its stats
                        if hasattr(body_attr, 'stats'):
                            for stat_name, bonus in body_attr.stats.items():
                                current_val = self.player.base_stats.get(
                                    stat_name, 0.0)
                                new_val = max(0.0, current_val - bonus)
                                self.player.base_stats[stat_name] = new_val
                        setattr(self.player, 'equipped_body', None)
                        self.player.update_stats()
                        
                        # Add armor back to inventory
                        if hasattr(self.player, 'inventory'):
                            success = self.player.inventory.add_item(body_attr)
                            if success:
                                msg = f"Unequipped body armor: {item_name} (added to inventory)"
                            else:
                                msg = f"Unequipped body armor: {item_name} (inventory full!)"
                        else:
                            msg = f"Unequipped body armor: {item_name}"
                        self.log_message(msg, "info")
                    else:
                        self.log_message("No body armor equipped", "info")
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
        right_frame = tk.Frame(main_frame, bg="dark gray")
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))
        
        tk.Label(
            right_frame,
            text="Allocate Stat Points:",
            bg="dark gray",
            fg="white",
            font=("Arial", 12, "bold")
        ).pack(anchor="w", pady=(0, 10))
        
        # Stat allocation buttons
        self.stat_buttons = {}
        allocatable_stats = [
            'strength', 'dexterity', 'vitality', 
            'intelligence', 'wisdom', 'constitution', 'luck'
        ]
        
        for stat in allocatable_stats:
            stat_frame = tk.Frame(right_frame, bg="dark gray")
            stat_frame.pack(fill=tk.X, pady=2)
            
            # Stat name and current value
            info_frame = tk.Frame(stat_frame, bg="dark gray")
            info_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
            
            tk.Label(
                info_frame,
                text=f"{stat.title()}:",
                bg="dark gray",
                fg="white",
                width=12,
                anchor="w"
            ).pack(side=tk.LEFT)
            
            # Current value label
            value_label = tk.Label(
                info_frame,
                text="0",
                bg="dark gray",
                fg="cyan",
                width=5,
                anchor="w"
            )
            value_label.pack(side=tk.LEFT)
            self.stat_buttons[f"{stat}_value"] = value_label
            
            # Allocation button
            btn = tk.Button(
                stat_frame,
                text=f"+ {stat.title()}",
                bg="green",
                fg="white",
                width=12,
                command=lambda s=stat: self.allocate_stat_point(s)
            )
            btn.pack(side=tk.RIGHT)
            self.stat_buttons[stat] = btn
        
        # Bottom controls
        control_frame = tk.Frame(right_frame, bg="dark gray")
        control_frame.pack(fill=tk.X, pady=(20, 0))
        
        # Reset points button
        tk.Button(
            control_frame,
            text="Reset All Points",
            bg="red",
            fg="white",
            command=self.reset_stat_points
        ).pack(fill=tk.X, pady=2)
        
        # Gain XP button for testing
        tk.Button(
            control_frame,
            text="Gain XP (Test)",
            bg="blue",
            fg="white",
            command=self.gain_test_xp
        ).pack(fill=tk.X, pady=2)
        
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
            from game_sys.skills.learning_system import LearningSystem
            from game_sys.character.leveling_manager import leveling_manager
            if not hasattr(self.player, 'learning'):
                self.player.learning = LearningSystem(self.player)
            available = self.player.learning.get_available_skills()
            if not available:
                self.log_message("No skills available to learn!", "info")
                return
            skill_id = available[0]  # For demo, just pick the first
            if self.player.learning.learn_if_allowed(skill_id):
                self.log_message(f"Learned skill: {skill_id}", "info")
            else:
                reqs = leveling_manager.get_skill_level_requirement(skill_id)
                self.log_message(f"Cannot learn {skill_id}: requirements not met (level {reqs})", "error")
        except Exception as e:
            self.log_message(f"Error learning skill: {e}", "error")

    def learn_spell_dialog(self):
        """Dialog to learn a spell if requirements are met."""
        try:
            if not hasattr(self.player, 'leveling_manager'):
                self.log_message("No leveling manager available!", "combat")
                return
                
            # Get available spells for the player's level
            available = self.player.leveling_manager.get_available_spells_for_level(self.player)
            if not available:
                self.log_message("No spells available to learn!", "info")
                return
                
            spell_id = available[0]  # For demo, just pick the first
            # Check if requirements are met
            level_req = self.player.leveling_manager.get_spell_level_requirement(spell_id)
            stat_reqs = self.player.leveling_manager.get_spell_stat_requirements(spell_id)
            
            # Check level requirement
            if level_req and self.player.level < level_req:
                self.log_message(f"Cannot learn {spell_id}: requires level {level_req}", "combat")
                return
                
            # Check stat requirements
            missing_stats = []
            for stat, required in stat_reqs.items():
                current_val = self.player.get_stat(stat)
                if current_val < required:
                    missing_stats.append(f"{stat}: {current_val}/{required}")
            
            if missing_stats:
                msg = f"Cannot learn {spell_id}: missing stats: {', '.join(missing_stats)}"
                self.log_message(msg, "combat")
                return
                
            # Learn the spell (simulate)
            self.log_message(f"Learned spell: {spell_id}!", "heal")
            self.update_progression_display()
            
        except Exception as e:
            self.log_message(f"Error learning spell: {e}", "combat")
    
    def learn_enchant_dialog(self):
        """Dialog to learn an enchantment if requirements are met."""
        try:
            if not hasattr(self.player, 'leveling_manager'):
                self.log_message("No leveling manager available!", "combat")
                return
                
            # Get available enchantments for the player's level
            available = self.player.leveling_manager.get_available_enchantments_for_level(self.player)
            if not available:
                self.log_message("No enchantments available to learn!", "info")
                return
                
            enchant_id = available[0]  # For demo, just pick the first
            # Check if requirements are met
            level_req = self.player.leveling_manager.get_enchantment_level_requirement(enchant_id)
            stat_reqs = self.player.leveling_manager.get_enchantment_stat_requirements(enchant_id)
            
            # Check level requirement
            if level_req and self.player.level < level_req:
                self.log_message(f"Cannot learn {enchant_id}: requires level {level_req}", "combat")
                return
                
            # Check stat requirements
            missing_stats = []
            for stat, required in stat_reqs.items():
                current_val = self.player.get_stat(stat)
                if current_val < required:
                    missing_stats.append(f"{stat}: {current_val}/{required}")
            
            if missing_stats:
                msg = f"Cannot learn {enchant_id}: missing stats: {', '.join(missing_stats)}"
                self.log_message(msg, "combat")
                return
                
            # Learn the enchantment (simulate)
            self.log_message(f"Learned enchantment: {enchant_id}!", "heal")
            self.update_progression_display()
            
        except Exception as e:
            self.log_message(f"Error learning enchantment: {e}", "combat")
    
    def setup_enchanting_tab(self):
        """Set up the enchanting and spell management tab."""
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
        
        # Left side: Available enchantments
        left_frame = tk.Frame(main_frame, bg="dark gray")
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        tk.Label(
            left_frame,
            text="Available Enchantments:",
            bg="dark gray",
            fg="white",
            font=("Arial", 12, "bold")
        ).pack(anchor="w", pady=(0, 5))
        
        self.available_enchants_listbox = tk.Listbox(
            left_frame,
            bg="black",
            fg="white",
            height=10
        )
        self.available_enchants_listbox.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Right side: Learned enchantments and spells
        right_frame = tk.Frame(main_frame, bg="dark gray")
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))
        
        tk.Label(
            right_frame,
            text="Learned Spells & Enchantments:",
            bg="dark gray",
            fg="white",
            font=("Arial", 12, "bold")
        ).pack(anchor="w", pady=(0, 5))
        
        self.learned_enchants_listbox = tk.Listbox(
            right_frame,
            bg="black",
            fg="white",
            height=10
        )
        self.learned_enchants_listbox.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Bottom controls
        controls_frame = tk.Frame(main_frame, bg="black")
        controls_frame.pack(fill=tk.X, pady=(10, 0))
        
        tk.Button(
            controls_frame,
            text="Learn Selected Enchantment",
            bg="purple",
            fg="white",
            command=self.learn_selected_enchantment
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            controls_frame,
            text="Apply Enchantment to Item",
            bg="blue",
            fg="white",
            command=self.apply_enchantment_to_item
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            controls_frame,
            text="Refresh Lists",
            bg="green",
            fg="white",
            command=self.refresh_enchanting_lists
        ).pack(side=tk.LEFT, padx=5)
    
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
        
        # Call the existing learn enchantment dialog logic
        try:
            self.log_message(f"Learning enchantment: {enchant_id}", "info")
            # This would integrate with the actual enchantment learning system
        except Exception as e:
            self.log_message(f"Error learning enchantment: {e}", "combat")
    
    def apply_enchantment_to_item(self):
        """Apply an enchantment to an item."""
        self.log_message("Enchantment application not yet implemented", "info")
    
    def allocate_stat_point(self, stat_name):
        """Allocate a stat point to the specified stat."""
        if not hasattr(self, 'player') or not self.player:
            self.log_message("No player character available!", "combat")
            return
            
        # Check if player has leveling manager
        if not hasattr(self.player, 'leveling_manager'):
            self.log_message("No leveling manager available!", "combat")
            return            # Check if player has available stat points
            available_points = 0
            if hasattr(self.player.leveling_manager, 'calculate_stat_points_available'):
                available_points = self.player.leveling_manager.calculate_stat_points_available(self.player)
            else:
                available_points = getattr(self.player.leveling_manager, 'available_stat_points', 0)
                
            if available_points <= 0:
                self.log_message("No stat points available to allocate!", "info")
                return
            
        try:
            # Allocate the stat point
            if hasattr(self.player.leveling_manager, 'allocate_stat_point'):
                success = self.player.leveling_manager.allocate_stat_point(self.player, stat_name)
                if success:
                    self.log_message(f"Allocated 1 point to {stat_name.title()}!", "info")
                    self.update_leveling_display()
                    self.update_char_info()
                else:
                    self.log_message(f"Failed to allocate point to {stat_name}", "combat")
            else:
                # Manual allocation fallback
                if hasattr(self.player, 'base_stats'):
                    current_val = self.player.base_stats.get(stat_name, 0)
                    self.player.base_stats[stat_name] = current_val + 1
                    
                    # Track stat point usage through spent_stat_points
                    if not hasattr(self.player, 'spent_stat_points'):
                        self.player.spent_stat_points = 0
                    self.player.spent_stat_points += 1
                    
                    self.player.update_stats()
                    self.log_message(f"Allocated 1 point to {stat_name.title()}!", "info")
                    self.update_leveling_display()
                    self.update_char_info()
                else:
                    self.log_message("No stats system available!", "combat")
        except Exception as e:
            self.log_message(f"Error allocating stat point: {e}", "combat")
    
    def reset_stat_points(self):
        """Reset all allocated stat points."""
        if not hasattr(self, 'player') or not self.player:
            self.log_message("No player character available!", "combat")
            return
            
        if not hasattr(self.player, 'leveling_manager'):
            self.log_message("No leveling manager available!", "combat")
            return
            
        try:
            if hasattr(self.player.leveling_manager, 'reset_stat_points'):
                self.player.leveling_manager.reset_stat_points(self.player)
                self.log_message("All stat points have been reset!", "info")
            else:
                # Manual reset fallback
                # Count currently allocated points
                allocated_points = 0
                if hasattr(self.player, 'base_stats'):
                    base_values = {
                        'strength': 10, 'dexterity': 10, 'vitality': 10,
                        'intelligence': 10, 'wisdom': 10, 'constitution': 10, 'luck': 10
                    }
                    for stat, current in self.player.base_stats.items():
                        if stat in base_values:
                            allocated_points += max(0, current - base_values[stat])
                            self.player.base_stats[stat] = base_values[stat]
                    
                    # Manually reset the spent_stat_points attribute
                    if hasattr(self.player, 'spent_stat_points'):
                        self.player.spent_stat_points = 0
                    
                    self.player.update_stats()
                    self.log_message(f"Reset {allocated_points} stat points!", "info")
                else:
                    self.log_message("No stats system available!", "combat")
                    
            self.update_leveling_display()
            self.update_char_info()
        except Exception as e:
            self.log_message(f"Error resetting stat points: {e}", "combat")
    
    def gain_test_xp(self):
        """Gain some XP for testing purposes."""
        if not hasattr(self, 'player') or not self.player:
            self.log_message("No player character available!", "combat")
            return
            
        if not hasattr(self.player, 'leveling_manager'):
            self.log_message("No leveling manager available!", "combat")
            return
            
        try:
            xp_gain = 50  # Test XP amount
            
            if hasattr(self.player.leveling_manager, 'gain_experience'):
                old_level = self.player.level
                self.player.leveling_manager.gain_experience(
                    actor=self.player, 
                    amount=xp_gain
                )
                new_level = self.player.level
                
                self.log_message(f"Gained {xp_gain} XP!", "heal")
                
                if new_level > old_level:
                    self.log_message(f"Level up! Now level {new_level}!", "heal")
                    
            else:
                # Manual XP gain fallback
                current_xp = getattr(self.player.leveling_manager, 'current_experience', 0)
                self.player.leveling_manager.current_experience = current_xp + xp_gain
                
                # Simple level check
                needed_xp = self.player.level * 100
                if self.player.leveling_manager.current_experience >= needed_xp:
                    self.player.level += 1
                    self.player.leveling_manager.current_experience -= needed_xp
                    
                    # Award stat points
                    if hasattr(self.player.leveling_manager, 'add_stat_points'):
                        self.player.leveling_manager.add_stat_points(self.player, 5)
                        self.log_message(f"Level up! Now level {self.player.level}! Gained 5 stat points!", "heal")
                    else:
                        self.log_message(f"Level up! Now level {self.player.level}!", "heal")
                else:
                    self.log_message(f"Gained {xp_gain} XP!", "heal")
                    
            self.update_leveling_display()
            self.update_char_info()
        except Exception as e:
            self.log_message(f"Error gaining XP: {e}", "combat")
    
    def update_leveling_display(self):
        """Update the leveling tab display with current data."""
        if not hasattr(self, 'player') or not self.player:
            return
            
        try:
            # Update available points label
            if hasattr(self, 'available_points_label'):
                available_points = 0
                if hasattr(self.player, 'leveling_manager'):
                    if hasattr(self.player.leveling_manager, 'calculate_stat_points_available'):
                        available_points = self.player.leveling_manager.calculate_stat_points_available(self.player)
                    else:
                        available_points = getattr(self.player.leveling_manager, 'available_stat_points', 0)
                self.available_points_label.config(text=str(available_points))
            
            # Update allocatable stats display
            if hasattr(self, 'allocatable_stats_text'):
                self.allocatable_stats_text.config(state="normal")
                self.allocatable_stats_text.delete(1.0, tk.END)
                
                stats_text = "Current Allocatable Stats:\n\n"
                
                if hasattr(self.player, 'base_stats'):
                    for stat, value in self.player.base_stats.items():
                        if stat in ['strength', 'dexterity', 'vitality', 'intelligence', 'wisdom', 'constitution', 'luck']:
                            # Format stat values with 2 decimal places
                            if isinstance(value, (int, float)):
                                stats_text += f"{stat.title():>12}: {value:.2f}\n"
                            else:
                                stats_text += f"{stat.title():>12}: {value}\n"
                else:
                    stats_text += "No stats system available"
                
                # Add derived stats if available
                if hasattr(self.player, 'current_health'):
                    stats_text += f"\nDerived Stats:\n"
                    stats_text += f"{'Health':>12}: {self.player.current_health:.2f}/{self.player.max_health:.2f}\n"
                    
                if hasattr(self.player, 'current_mana'):
                    stats_text += f"{'Mana':>12}: {self.player.current_mana:.2f}/{self.player.max_mana:.2f}\n"
                    
                if hasattr(self.player, 'current_stamina'):
                    stats_text += f"{'Stamina':>12}: {self.player.current_stamina:.2f}/{self.player.max_stamina:.2f}\n"
                
                self.allocatable_stats_text.insert(tk.END, stats_text)
                self.allocatable_stats_text.config(state="disabled")
            
            # Update stat value labels
            if hasattr(self, 'stat_buttons') and hasattr(self.player, 'base_stats'):
                for stat in ['strength', 'dexterity', 'vitality', 'intelligence', 'wisdom', 'constitution', 'luck']:
                    value_label_key = f"{stat}_value"
                    if value_label_key in self.stat_buttons:
                        current_value = self.player.base_stats.get(stat, 0)
                        self.stat_buttons[value_label_key].config(text=str(current_value))
                        
        except Exception as e:
            self.log_message(f"Error updating leveling display: {e}", "combat")
    
    def refresh_enchanting_lists(self):
        """Refresh the enchanting tab lists."""
        if not hasattr(self, 'player') or not self.player:
            return
            
        try:
            # This would refresh enchanting interface if it exists
            if hasattr(self, 'available_enchants_listbox'):
                self.available_enchants_listbox.delete(0, tk.END)
                if hasattr(self.player, 'leveling_manager'):
                    available_enchants = self.player.leveling_manager.get_available_enchantments_for_level(self.player)
                    for enchant in available_enchants:
                        self.available_enchants_listbox.insert(tk.END, enchant)
            
            if hasattr(self, 'learned_enchants_listbox'):
                self.learned_enchants_listbox.delete(0, tk.END)
                if hasattr(self.player, 'enchantments'):
                    for enchant in self.player.enchantments:
                        self.learned_enchants_listbox.insert(tk.END, enchant)
            
            self.log_message("Enchanting interface refreshed", "info")
        except Exception as e:
            self.log_message(f"Error refreshing enchanting lists: {e}", "combat")
    
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
                if hasattr(self.player, 'learning'):
                    # Add learned skills if available
                    learned = getattr(self.player.learning, 'learned_skills', [])
                    for skill in learned:
                        self.learned_skills_listbox.insert(tk.END, skill)
            
            # Update spells lists
            if hasattr(self, 'available_spells_listbox'):
                self.available_spells_listbox.delete(0, tk.END)
                if hasattr(self.player, 'leveling_manager'):
                    available_spells = self.player.leveling_manager.get_available_spells_for_level(self.player)
                    for spell in available_spells:
                        self.available_spells_listbox.insert(tk.END, spell)
            
            # Update items list
            if hasattr(self, 'unlocked_items_listbox'):
                self.unlocked_items_listbox.delete(0, tk.END)
                if hasattr(self.player, 'leveling_manager'):
                    available_items = self.player.leveling_manager.get_available_items_for_level(self.player)
                    for item in available_items:
                        self.unlocked_items_listbox.insert(tk.END, item)
            
            # Update progression info
            if hasattr(self, 'progression_info'):
                self.progression_info.config(state="normal")
                self.progression_info.delete(1.0, tk.END)
                
                info_text = f"Character: {self.player.name}\n"
                info_text += f"Level: {self.player.level}\n"
                
                if hasattr(self.player, 'leveling_manager'):
                    # Get next level unlocks
                    next_unlocks = self.player.leveling_manager.get_next_level_unlocks(self.player)
                    info_text += f"\nNext Level Unlocks:\n"
                    for category, items in next_unlocks.items():
                        if items:
                            info_text += f"  {category.title()}: {', '.join(items[:3])}\n"
                            if len(items) > 3:
                                info_text += f"     ... and {len(items) - 3} more\n"
                
                self.progression_info.insert(tk.END, info_text)
                self.progression_info.config(state="disabled")
                
        except Exception as e:
            self.log_message(f"Error updating progression display: {e}", "combat")
    

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
