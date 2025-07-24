#!/usr/bin/env python3
"""
Simple Game Demo
===============

A basic demo for the game engine with integrated logging and tabbed interface.
"""

import tkinter as tk
from tkinter import ttk
from typing import Dict, Any, Optional, List, Union
import time
import random
import math
import os
import sys
import json

# Import interface definitions for type safety
try:
    from interfaces.game_interfaces import (
        CombatControllerInterface, CharacterControllerInterface,
        InventoryControllerInterface, ComboControllerInterface,
        DemoEventHandlerInterface, DisplayManagerInterface,
        GameStateManagerInterface, UIServiceProtocol,
        ActionResult, CharacterData, CombatResult
    )
except ImportError:
    # Fallback for development - create stub interfaces
    class CombatControllerInterface: pass
    class CharacterControllerInterface: pass
    class InventoryControllerInterface: pass
    class ComboControllerInterface: pass
    class DemoEventHandlerInterface: pass
    class DisplayManagerInterface: pass
    class GameStateManagerInterface: pass
    class UIServiceProtocol: pass
    ActionResult = Dict[str, Any]
    CharacterData = Dict[str, Any]
    CombatResult = Dict[str, Any]


# Import logging system
from logs.logs import get_logger, setup_logging

# Import hooks system
from game_sys.hooks.hooks_setup import emit, on, ON_COMBO_TRIGGERED, ON_COMBO_FINISHED

# Import observer pattern for Task #5 implementation
try:
    from interfaces import GameEventType, UIObserver, GameEventPublisher
    OBSERVER_PATTERN_AVAILABLE = True
except ImportError:
    # Fallback if observer pattern not available
    GameEventType = None
    UIObserver = None
    GameEventPublisher = None
    OBSERVER_PATTERN_AVAILABLE = False

# Set up logging
setup_logging()
logger = get_logger("simple_demo")

# Import game system
from game_sys.core.grades import Grade
from game_sys.core.rarity import Rarity
from game_sys.character.character_factory import create_character
from game_sys.character.character_service import (
    create_character_with_random_stats
)
from game_sys.combat.combat_service import CombatService
from game_sys.config.property_loader import PropertyLoader
from game_sys.managers.equipment_manager import equipment_manager

try:

    from game_sys.magic.enchanting_system import EnchantingSystem
    ITEMS_AVAILABLE = True
    SPELLS_AVAILABLE = True
    ENCHANTING_AVAILABLE = True
except ImportError:
    ITEMS_AVAILABLE = True
    SPELLS_AVAILABLE = True
    ENCHANTING_AVAILABLE = True


# ============================================================================
# CONTROLLER WRAPPER CLASSES - Task #2 Implementation
# ============================================================================

class CombatController(CombatControllerInterface):
    """Controller for combat-related operations with consistent UI integration."""
    
    def __init__(self, combat_service: Optional[Any] = None, ui_service: Optional[UIServiceProtocol] = None) -> None:
        """Initialize combat controller with service and UI integration."""
        super().__init__(ui_service)
        self.service = combat_service
    
    def set_ui_callback(self, callback: callable) -> None:
        """Set callback for UI updates (fallback if no UI service)."""
        self._ui_callback = callback
    
    def _log_message(self, message: str, tag: str = "info") -> None:
        """Helper to log messages via UI service or callback."""
        if self.ui_service and hasattr(self.ui_service, 'log_message'):
            self.ui_service.log_message(message, tag)
        elif hasattr(self, '_ui_callback') and self._ui_callback:
            self._ui_callback(message, tag)
    
    def perform_attack(self, attacker: Any, target: Any, weapon: Optional[Any] = None) -> ActionResult:
        """Perform attack with UI integration."""
        if not self.service:
            return {'success': False, 'message': 'No combat service available', 'damage': 0, 'defeated': False, 'loot': []}
        
        result = self.service.perform_attack(attacker, target, weapon)
        
        if result['success']:
            weapon_info = f" with {weapon.name}" if weapon else ""
            damage_msg = (f"{attacker.name} attacks {target.name}{weapon_info} "
                         f"for {result['damage']:.0f} damage!")
            self._log_message(damage_msg, "combat")
            
            # Display resistance/weakness messages
            if result.get('resistance_messages'):
                for message in result['resistance_messages']:
                    self._log_message(message, "combat")
        else:
            self._log_message(f"Attack failed: {result['message']}", "combat")
        
        return result
    
    def apply_healing(self, caster: Any, target: Any, amount: int) -> ActionResult:
        """Apply healing with UI integration."""
        if not self.service:
            return {'success': False, 'message': 'No combat service available', 'healing': 0}
        
        result = self.service.apply_healing(caster, target, amount)
        
        if result['success']:
            self._log_message(f"{target.name} is healed for {result['healing']:.0f} health!", "heal")
        else:
            self._log_message(f"Healing failed: {result['message']}", "combat")
        
        return result
    
    def cast_spell_at_target(self, caster: Any, target: Any, spell_name: str, **kwargs) -> ActionResult:
        """Cast spell with UI integration."""
        if not self.service:
            return {'success': False, 'message': 'No combat service available', 'damage': 0, 'defeated': False, 'loot': []}
        
        # Fix parameter order - service expects (caster, spell_id, target)
        result = self.service.cast_spell_at_target(caster, spell_name, target, **kwargs)
        
        if result['success']:
            self._log_message(f"{caster.name} casts {spell_name} at {target.name}!", "combat")
            if result.get('damage', 0) > 0:
                self._log_message(f"Deals {result['damage']:.0f} damage!", "combat")
        else:
            self._log_message(f"Spell failed: {result['message']}", "combat")
        
        return result


class CharacterController(CharacterControllerInterface):
    """Controller for character-related operations with consistent UI integration."""
    
    def __init__(self, ui_service: Optional[UIServiceProtocol] = None) -> None:
        """Initialize character controller with UI integration."""
        super().__init__(ui_service)
    
    def set_ui_callback(self, callback: callable) -> None:
        """Set callback for UI updates (fallback if no UI service)."""
        self._ui_callback = callback
    
    def _log_message(self, message: str, tag: str = "info") -> None:
        """Helper to log messages via UI service or callback."""
        if self.ui_service and hasattr(self.ui_service, 'log_message'):
            self.ui_service.log_message(message, tag)
        elif hasattr(self, '_ui_callback') and self._ui_callback:
            self._ui_callback(message, tag)
    
    def level_up_character(self, character: Any) -> bool:
        """Level up character with UI integration."""
        if not character:
            self._log_message("No character available for level up!", "combat")
            return False
        
        old_level = character.level
        
        # Use leveling manager if available
        if hasattr(character, 'leveling_manager'):
            if hasattr(character.leveling_manager, 'gain_experience'):
                character.leveling_manager.gain_experience(
                    character, 
                    character.leveling_manager._xp_for_next_level(character.level)
                )
            else:
                character.level += 1
            
            # Check if level actually increased
            if character.level > old_level:
                points_gained = character.level - old_level
                if hasattr(character.leveling_manager, 'get_stat_points_per_level'):
                    points_per_level = character.leveling_manager.get_stat_points_per_level(character.level)
                else:
                    points_per_level = 3
                total_points = points_gained * points_per_level
                
                if hasattr(character.leveling_manager, 'add_stat_points'):
                    character.leveling_manager.add_stat_points(character, total_points)
                
                msg = f"Level up! Now level {character.level} (+{total_points} stat points)!"
                self._log_message(msg, "info")
                return True
        else:
            # Fallback for characters without leveling manager
            character.level += 1
            msg = f"Level up! Now level {character.level}!"
            self._log_message(msg, "info")
            return True
        
        return False
    
    def allocate_stat_point(self, character: Any, stat_name: str) -> bool:
        """Allocate stat point with UI integration."""
        if not character or not hasattr(character, 'leveling_manager'):
            self._log_message("Cannot allocate stat points - no leveling manager!", "combat")
            return False
        
        success = character.leveling_manager.allocate_stat_points(character, {stat_name: 1})
        
        if success:
            self._log_message(f"Allocated 1 point to {stat_name}!", "info")
        else:
            self._log_message(f"Failed to allocate point to {stat_name}!", "combat")
        
        return success


class InventoryController(InventoryControllerInterface):
    """Controller for inventory-related operations with consistent UI integration."""
    
    def __init__(self, ui_service: Optional[UIServiceProtocol] = None) -> None:
        """Initialize inventory controller with UI integration."""
        super().__init__(ui_service)
    
    def set_ui_callback(self, callback: callable) -> None:
        """Set callback for UI updates (fallback if no UI service)."""
        self._ui_callback = callback
    
    def _log_message(self, message: str, tag: str = "info") -> None:
        """Helper to log messages via UI service or callback."""
        if self.ui_service and hasattr(self.ui_service, 'log_message'):
            self.ui_service.log_message(message, tag)
        elif hasattr(self, '_ui_callback') and self._ui_callback:
            self._ui_callback(message, tag)
    
    def use_item(self, character: Any, item: Any) -> bool:
        """Use item with UI integration."""
        if not character or not item:
            self._log_message("Cannot use item - missing character or item!", "combat")
            return False
        
        # Use inventory system's usage manager
        if hasattr(character, 'inventory') and hasattr(character.inventory, 'usage_manager'):
            result = character.inventory.usage_manager.use_item(character, item)
            
            if result.get('success', False):
                self._log_message(f"Used {item.name}! {result.get('message', '')}", "info")
                return True
            else:
                self._log_message(f"Failed to use {item.name}: {result.get('message', 'Unknown error')}", "combat")
                return False
        else:
            self._log_message("No inventory system available!", "combat")
            return False
    
    def equip_item(self, character: Any, item: Any) -> bool:
        """Equip item with UI integration."""
        if not character or not item:
            self._log_message("Cannot equip item - missing character or item!", "combat")
            return False
        
        # Use smart equipping if available
        if hasattr(character, 'equip_item_smart'):
            success = character.equip_item_smart(item)
        elif hasattr(character, 'equip_item'):
            success = character.equip_item(item)
        else:
            self._log_message("No equipment system available!", "combat")
            return False
        
        if success:
            self._log_message(f"Equipped {item.name}!", "info")
        else:
            self._log_message(f"Failed to equip {item.name}!", "combat")
        
        return success


class ComboController(ComboControllerInterface):
    """Controller for combo-related operations with consistent UI integration."""
    
    def __init__(self, combo_manager: Optional[Any] = None, ui_service: Optional[UIServiceProtocol] = None) -> None:
        """Initialize combo controller with service and UI integration."""
        super().__init__(ui_service)
        self.combo_manager = combo_manager
    
    def set_ui_callback(self, callback: callable) -> None:
        """Set callback for UI updates (fallback if no UI service)."""
        self._ui_callback = callback
    
    def _log_message(self, message: str, tag: str = "info") -> None:
        """Helper to log messages via UI service or callback."""
        if self.ui_service and hasattr(self.ui_service, 'log_message'):
            self.ui_service.log_message(message, tag)
        elif hasattr(self, '_ui_callback') and self._ui_callback:
            self._ui_callback(message, tag)
    
    def record_spell_cast(self, caster: Any, spell_name: str) -> Optional[Dict[str, Any]]:
        """Record spell cast for combo tracking with UI integration."""
        if not self.combo_manager:
            return None
        
        result = self.combo_manager.record_cast(caster, spell_name)
        
        if result and result.get('combo_triggered'):
            combo_name = result.get('combo_name', 'Unknown Combo')
            self._log_message(f"Combo Activated: {combo_name}!", "info")
        
        return result
    
    def check_combo_sequences(self, character, sequence):
        """Check if sequence matches any combos with UI integration."""
        if not self.combo_manager:
            return None
        
        # This would be implemented based on your combo system
        # For now, return None as placeholder
        return None


# ============================================================================
# MAIN DEMO CLASS
# ============================================================================

class SimpleGameDemo(DemoEventHandlerInterface, DisplayManagerInterface, GameStateManagerInterface):
    """Main demo class implementing multiple interfaces for type safety."""
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

    def __init__(self) -> None:
        """Initialize the demo with type-safe interface compliance."""
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

        # Initialize UI service for selective delegation (using existing window)
        try:
            from ui.demo_ui import DemoUI
            self.ui_service = DemoUI(root=self.root)
            self.ui_service.set_log_callback(self._log_to_console)
            logger.info("UI service initialized with existing window")
        except ImportError as e:
            logger.warning(f"UI service not available: {e}")
            self.ui_service = None

        # Initialize controller classes for Task #2 implementation
        self._initialize_controllers()

        # Set up UI
        self.setup_ui()

        # Set up combo hooks
        self.setup_combo_hooks()

        # Set up game state
        self.setup_game_state()

        logger.info("Demo initialized")

    def _initialize_controllers(self):
        """Initialize controller wrapper classes for game logic separation."""
        logger.info("Initializing controller classes...")
        
        # Initialize combat service (will be set up properly in setup_game_state)
        self.combat_service = None
        
        # Initialize controller classes with UI service integration
        self.combat_controller = CombatController(
            combat_service=None,  # Will be set later
            ui_service=self.ui_service
        )
        self.character_controller = CharacterController(ui_service=self.ui_service)
        self.inventory_controller = InventoryController(ui_service=self.ui_service)
        self.combo_controller = ComboController(
            combo_manager=None,  # Will be set later if available
            ui_service=self.ui_service
        )
        
        # Initialize Observer Pattern for Task #5 implementation
        self._initialize_observer_pattern()
        
        logger.info("Controllers initialized with observer pattern integration")
        # Set up fallback UI callbacks if no UI service
        if not self.ui_service:
            self.combat_controller.set_ui_callback(self.log_message)
            self.character_controller.set_ui_callback(self.log_message)
            self.inventory_controller.set_ui_callback(self.log_message)
            self.combo_controller.set_ui_callback(self.log_message)
        
        logger.info("Controller classes initialized")

    def _initialize_observer_pattern(self):
        """Initialize observer pattern for Task #5 implementation."""
        if not OBSERVER_PATTERN_AVAILABLE:
            logger.warning("Observer pattern not available - skipping initialization")
            self.ui_observer = None
            return
        
        try:
            # Create UI observer and connect it to the demo UI service
            self.ui_observer = UIObserver(self.ui_service)
            
            # The UI observer is now automatically subscribed to relevant events
            # and will handle UI updates when events are published
            
            logger.info("🔍 Observer pattern initialized successfully")
            if hasattr(self, 'log_message'):
                # This will be available after setup_ui, so we'll log it later
                pass
            else:
                # Store message to log after UI setup
                self._pending_observer_message = "🔍 Observer pattern ready for event-driven UI updates"
                
        except Exception as e:
            logger.error(f"Failed to initialize observer pattern: {e}")
            self.ui_observer = None

    def _wire_controllers(self):
        """Wire controller classes with actual service instances."""
        logger.info("Wiring controllers with services...")
        
        # Wire combat controller with combat service
        if self.combat_service:
            self.combat_controller.service = self.combat_service
            logger.info("Combat controller wired with CombatService")
        
        # Wire combo controller with combo manager if available
        try:
            from game_sys.magic.combo import ComboManager
            combo_manager = ComboManager()
            self.combo_controller.combo_manager = combo_manager
            logger.info("Combo controller wired with ComboManager")
        except ImportError as e:
            logger.debug(f"ComboManager not available: {e}")
        
        logger.info("Controllers wired successfully")

    def _log_to_console(self, message: str, tag: str = "info") -> None:
        """Helper method for UI service to log to console."""
        if hasattr(self, 'log'):
            timestamp = time.strftime("%H:%M:%S")
            self.log.insert(tk.END, f"[{timestamp}] ", "info")
            self.log.insert(tk.END, f"{message}\n", tag)
            self.log.see(tk.END)

    def setup_ui(self):
        """Set up the user interface with tabs."""
        logger.info("Setting up tabbed UI")

        # Create main frame
        self.main_frame = tk.Frame(self.root, bg="black")
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # Configure progress bar styles for combo system
        style = ttk.Style()
        
        # Combo tab progress bar style
        style.configure("Combo.Horizontal.TProgressbar",
                       background='#4CAF50',  # Green color
                       troughcolor='#333333',  # Dark trough
                       borderwidth=1,
                       lightcolor='#4CAF50',
                       darkcolor='#2E7D32')
                       
        # Combat tab progress bar style  
        style.configure("Combat.Horizontal.TProgressbar",
                       background='#FF9800',  # Orange color
                       troughcolor='#333333',  # Dark trough
                       borderwidth=1,
                       lightcolor='#FF9800',
                       darkcolor='#E65100')

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

        # Set up all tabs using UI service if available
        if hasattr(self, 'ui_service') and self.ui_service:
            # Create tabs in UI service
            self.ui_service.tabs = {
                'stats': self.stats_tab,
                'combat': self.combat_tab,
                'inventory': self.inventory_tab,
                'leveling': self.leveling_tab,
                'enchanting': self.enchanting_tab,
                'progression': self.progression_tab,
                'combo': self.combo_tab,
                'settings': self.settings_tab
            }
            # Set up all tabs via service
            setup_result = self.ui_service.setup_all_tabs()
            if setup_result.get('success', False):
                self.log_message(f"UI Service: {setup_result['message']}")
            else:
                self.log_message(f"UI Service setup failed: {setup_result.get('error', 'Unknown error')}")
                # Fallback to local setup
                self.setup_all_tabs()
        else:
            # Fallback to local setup method
            self.setup_all_tabs()

        # Create log area
        self.log_frame = tk.Frame(self.root, bg="black")
        self.log_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=10)

        self.log = tk.Text(self.log_frame, bg="black", fg="white", height=8)
        self.log.pack(fill=tk.X)

        # Configure text tags
        self.log.tag_configure("info", foreground="cyan")
        self.log.tag_configure("combat", foreground="red")
        self.log.tag_configure("heal", foreground="green")

        # Pass widget references to UI service for selective delegation
        if hasattr(self, 'ui_service') and self.ui_service:
            widget_refs = {
                'basic_info': getattr(self, 'basic_info', None),
                'detailed_stats': getattr(self, 'detailed_stats', None),
                'enemy_info': getattr(self, 'enemy_info', None),
                'status_effects_display': getattr(self, 'status_effects_display', None),
                'log': self.log
            }
            # Filter out None values
            widget_refs = {k: v for k, v in widget_refs.items() if v is not None}
            self.ui_service.set_external_widgets(widget_refs)
            
            # Get widget references back from UI service
            self._get_ui_service_widgets()
            
            # Register callbacks for all UI actions
            self._register_ui_callbacks()

    def _register_ui_callbacks(self):
        """Register all UI callbacks with the UI service."""
        if not hasattr(self, 'ui_service') or not self.ui_service:
            return
            
        # Combat tab callbacks (matching ui/demo_ui.py combat_buttons)
        self.ui_service.register_callback('attack', self.on_attack_button_clicked)
        self.ui_service.register_callback('heal', self.on_heal_button_clicked)
        self.ui_service.register_callback('spawn_enemy', self.on_spawn_enemy_button_clicked)
        self.ui_service.register_callback('cast_fireball', self.on_fireball_button_clicked)  # Note: cast_fireball, not fireball
        self.ui_service.register_callback('cast_ice_shard', self.on_ice_shard_button_clicked)  # Note: cast_ice_shard, not ice_shard
        self.ui_service.register_callback('test_dual_wield', self.test_dual_wield)
        self.ui_service.register_callback('tick_status_effects', self.tick_status_effects)
        
        # Stats tab callbacks (matching ui/demo_ui.py button_configs)
        self.ui_service.register_callback('view_inventory', self.view_inventory)
        self.ui_service.register_callback('level_up', self.on_level_up_button_clicked)
        self.ui_service.register_callback('equip_gear', self.equip_gear)  # Map to existing equip_gear method
        self.ui_service.register_callback('restore_health', self.restore_health)
        self.ui_service.register_callback('restore_mana', self.restore_mana)
        self.ui_service.register_callback('restore_stamina', self.restore_stamina)
        self.ui_service.register_callback('restore_all_resources', self.restore_all_resources)  # Use existing method
        self.ui_service.register_callback('save_game', self.save_game)
        self.ui_service.register_callback('load_game', self.load_game)
        
        # Additional character callbacks
        self.ui_service.register_callback('detailed_character_view', self._detailed_character_view_placeholder)
        self.ui_service.register_callback('reload_game', self.reload_game)
        
        # Equipment callbacks
        self.ui_service.register_callback('inspect_equipment', self._inspect_equipment_placeholder)
        self.ui_service.register_callback('quick_equip_best', self.equip_gear)  # Map to existing equip_gear
        self.ui_service.register_callback('optimize_defense', self._optimize_defense_placeholder)
        
        # Inventory tab callbacks (matching ui/demo_ui.py inventory_buttons)
        self.ui_service.register_callback('use_item', self.on_use_item_button_clicked)
        self.ui_service.register_callback('equip_item', lambda: self._equip_selected_item())
        self.ui_service.register_callback('drop_item', lambda: self._drop_selected_item())
        self.ui_service.register_callback('create_item', self._create_item_placeholder)
        self.ui_service.register_callback('add_random_item', self._add_random_item_placeholder)
        self.ui_service.register_callback('unequip_weapon', lambda: self.unequip_item('weapon'))
        self.ui_service.register_callback('unequip_armor', lambda: self.unequip_item('body'))
        self.ui_service.register_callback('unequip_offhand', lambda: self.unequip_item('offhand'))
        self.ui_service.register_callback('unequip_ring', lambda: self.unequip_item('ring'))
        
        # Additional unequip callbacks for equipment slots
        self.ui_service.register_callback('unequip_equipped_helmet', lambda: self.unequip_item('helmet'))
        self.ui_service.register_callback('unequip_equipped_cloak', lambda: self.unequip_item('cloak'))
        self.ui_service.register_callback('unequip_equipped_body', lambda: self.unequip_item('body'))
        self.ui_service.register_callback('unequip_equipped_feet', lambda: self.unequip_item('feet'))
        self.ui_service.register_callback('unequip_equipped_ring', lambda: self.unequip_item('ring'))
        
        # Leveling tab callbacks (matching ui/demo_ui.py leveling_buttons)
        self.ui_service.register_callback('allocate_stat_point', self._allocate_stat_point_placeholder)
        self.ui_service.register_callback('reset_all_stats', self._reset_all_stats_placeholder)
        self.ui_service.register_callback('view_character_build', self._detailed_character_view_placeholder)
        self.ui_service.register_callback('save_character_build', self._save_character_build_placeholder)

    def _equip_selected_item(self):
        """Equip currently selected item from inventory."""
        self.log_message("Equip selected item - placeholder implementation", "info")

    def _drop_selected_item(self):
        """Drop currently selected item from inventory."""
        self.log_message("Drop selected item - placeholder implementation", "info")

    def _create_item_placeholder(self):
        """Create item - placeholder implementation."""
        self.log_message("Create item - feature not yet implemented", "info")

    def _add_random_item_placeholder(self):
        """Add random item - placeholder implementation."""
        self.log_message("Add random item - feature not yet implemented", "info")

    def _allocate_stat_point_placeholder(self):
        """Allocate stat point - placeholder implementation."""
        self.log_message("Allocate stat point - feature not yet implemented", "info")

    def _reset_all_stats_placeholder(self):
        """Reset all stats - placeholder implementation."""
        self.log_message("Reset all stats - feature not yet implemented", "info")

    def _save_character_build_placeholder(self):
        """Save character build - placeholder implementation."""
        self.log_message("Save character build - feature not yet implemented", "info")

    def _get_ui_service_widgets(self):
        """Get widget references from the UI service for local use."""
        if not hasattr(self, 'ui_service') or not self.ui_service:
            return
            
        # Get widget references from UI service
        if hasattr(self.ui_service, 'widgets'):
            # Combat tab widgets
            self.canvas = self.ui_service.widgets.get('canvas', None)
            self.enemy_info = self.ui_service.widgets.get('enemy_info', None)
            
            # Combo widgets (for tracking spells and combo updates)
            combo_status_label = self.ui_service.widgets.get('combo_status_label', None)
            combo_sequence_label = self.ui_service.widgets.get('combo_sequence_label', None) 
            combo_progress = self.ui_service.widgets.get('combo_progress', None)
            combo_list = self.ui_service.widgets.get('combo_list', None)
            
            # Combat combo widgets (from combat tab's combo indicator)
            combat_combo_sequence = self.ui_service.widgets.get('combat_combo_sequence', None)
            combat_combo_progress = self.ui_service.widgets.get('combat_combo_progress', None)
            
            # Log successful widget retrieval
            if self.canvas:
                self.log_message("Canvas widget retrieved from UI service", "info")
            if self.enemy_info:
                self.log_message("Enemy info widget retrieved from UI service", "info")
            if combo_sequence_label:
                self.log_message("Combo sequence widgets retrieved from UI service", "info")
            if combat_combo_sequence:
                self.log_message("Combat combo widgets retrieved from UI service", "info")
        else:
            self.log_message("Warning: UI service widgets not available", "info")

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

        # Combo progress bar - use a proper progress bar
        progress_frame = tk.Frame(combo_tab, bg="black")
        progress_frame.pack(pady=(0, 10))
        
        progress_label = tk.Label(progress_frame, text="Combo Timer:", font=("Arial", 10), fg="white", bg="black")
        progress_label.pack()
        
        self.combo_progress = ttk.Progressbar(
            progress_frame, 
            mode='determinate', 
            length=300, 
            style='Combo.Horizontal.TProgressbar'
        )
        self.combo_progress.pack(pady=5)
        self.combo_progress['maximum'] = 100

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
        # Check if combo tab widgets exist (either from UI service or local setup)
        if not (hasattr(self, 'combo_sequence_label') or 
                (hasattr(self, 'ui_service') and self.ui_service and 
                 hasattr(self.ui_service, 'widgets'))):
            # Combo tab not set up yet, skip update
            return
            
        # Update current combo sequence
        seq = self.combo_sequence if hasattr(self, "combo_sequence") else []
        seq_str = " > ".join(seq) if seq else "-"
        
        # Try to update combo sequence label (UI service first, then local)
        if (hasattr(self, 'ui_service') and self.ui_service and 
            hasattr(self.ui_service, 'widgets') and 
            'combo_sequence_label' in self.ui_service.widgets):
            self.ui_service.widgets['combo_sequence_label'].config(text=seq_str)
        elif hasattr(self, 'combo_sequence_label'):
            self.combo_sequence_label.config(text=f"Current Combo: {seq_str}")

        # Update progress bar
        pct = 0
        timer_val = 0.0
        if hasattr(self, "combo_timer") and hasattr(self, "combo_window") and self.combo_window > 0:
            timer_val = self.combo_timer
            pct = max(0, min(100, int(100 * self.combo_timer / self.combo_window)))
        
        # Update the progress bar (UI service first, then local)
        if (hasattr(self, 'ui_service') and self.ui_service and 
            hasattr(self.ui_service, 'widgets') and 
            'combo_progress' in self.ui_service.widgets):
            self.ui_service.widgets['combo_progress']['value'] = pct
        elif hasattr(self, 'combo_progress'):
            self.combo_progress['value'] = pct
        
        # Update status bar (UI service first, then local)
        if seq:
            status = "Building Combo" if pct > 0 else "Combo Ready"
            color = "orange" if pct > 0 else "green"
        else:
            status = "Ready"
            color = "green"
            
        if (hasattr(self, 'ui_service') and self.ui_service and 
            hasattr(self.ui_service, 'widgets') and 
            'combo_status_label' in self.ui_service.widgets):
            self.ui_service.widgets['combo_status_label'].config(text=status, fg=color)
        elif hasattr(self, 'combo_status_label'):
            self.combo_status_label.config(text=f"Status: {status}", fg=color)
        
        # Update timer display if available
        if (hasattr(self, 'ui_service') and self.ui_service and 
            hasattr(self.ui_service, 'widgets') and 
            'combo_timer_label' in self.ui_service.widgets):
            self.ui_service.widgets['combo_timer_label'].config(text=f"Timer: {timer_val:.1f}s")
        elif hasattr(self, 'combo_timer_label'):
            self.combo_timer_label.config(text=f"Timer: {timer_val:.1f}s")
            
        # Update combat tab combo visuals
        self.update_combat_combo_display(seq, pct, timer_val)

        # Update combo details (if available)
        self._update_combo_details()

    def _update_combo_details(self):
        """Update combo details display with proper widget access."""
        # Get combo list/listbox and details widgets
        combo_list_widget = None
        combo_details_widget = None
        
        # Try UI service widgets first
        if (hasattr(self, 'ui_service') and self.ui_service and 
            hasattr(self.ui_service, 'widgets')):
            combo_list_widget = self.ui_service.widgets.get('combo_list')
            # UI service doesn't seem to have combo_details, so we may not need this part
        
        # Fallback to local widgets
        if not combo_list_widget and hasattr(self, 'combos_listbox'):
            combo_list_widget = self.combos_listbox
        if not combo_details_widget and hasattr(self, 'combo_details'):
            combo_details_widget = self.combo_details
            
        # Update combo list/listbox with available combos if we have data
        if combo_list_widget and hasattr(self, 'combos_data') and isinstance(self.combos_data, list):
            # Check if it's a Text widget (UI service) or Listbox (local)
            if hasattr(combo_list_widget, 'delete') and hasattr(combo_list_widget, 'insert'):
                # Text widget - clear and populate
                try:
                    combo_list_widget.config(state="normal")
                    combo_list_widget.delete(1.0, 'end')
                    
                    combo_text = "Available Combos:\n" + "="*30 + "\n\n"
                    for i, combo in enumerate(self.combos_data):
                        if isinstance(combo, dict):
                            name = combo.get('name', f'Combo {i+1}')
                            sequence = combo.get('sequence', [])
                            effects = combo.get('effects', 'Unknown')
                            combo_text += f"{i+1}. {name}\n"
                            combo_text += f"   Sequence: {' > '.join(sequence)}\n"
                            combo_text += f"   Effects: {effects}\n\n"
                        else:
                            combo_text += f"{i+1}. {str(combo)}\n\n"
                    
                    combo_list_widget.insert(1.0, combo_text)
                    combo_list_widget.config(state="disabled")
                except tk.TclError:
                    # Widget access failed, skip
                    pass
                    
        # Update combo details for selected combo (only if we have local widgets)
        if hasattr(self, 'combos_listbox') and hasattr(self, 'combo_details'):
            try:
                selection = self.combos_listbox.curselection()
                if selection and isinstance(self.combos_data, list) and selection[0] < len(self.combos_data):
                    idx = selection[0]
                    combo = self.combos_data[idx]
                    if isinstance(combo, dict):
                        details = (
                            f"Name: {combo.get('name', '-')}\n"
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
            except (AttributeError, IndexError, tk.TclError):
                # Widget access failed or selection invalid, skip
                pass

    def on_combo_select(self, event):
        """Handle selection of a combo in the listbox."""
        self.update_combo_tab()

    # Call update_combo_tab() whenever combo state changes (e.g., after spell cast)

    def update_combat_combo_display(self, seq, pct, timer_val):
        """Update combo visuals in the combat tab."""
        # Check if combat combo widgets exist (either from UI service or local setup)
        combat_combo_sequence = None
        combat_combo_progress = None
        
        # Try to get widgets from UI service first
        if (hasattr(self, 'ui_service') and self.ui_service and 
            hasattr(self.ui_service, 'widgets')):
            combat_combo_sequence = self.ui_service.widgets.get('combat_combo_sequence')
            combat_combo_progress = self.ui_service.widgets.get('combat_combo_progress')
        
        # Fallback to local widgets
        if not combat_combo_sequence and hasattr(self, 'combat_combo_sequence'):
            combat_combo_sequence = self.combat_combo_sequence
        if not combat_combo_progress and hasattr(self, 'combat_combo_progress'):
            combat_combo_progress = self.combat_combo_progress
            
        # Update sequence display if available
        if combat_combo_sequence:
            seq_text = " > ".join(seq[-3:]) if seq else "Ready"  # Show last 3 spells
            if len(seq) > 3:
                seq_text = "..." + seq_text
            combat_combo_sequence.config(text=seq_text)
            
            # Update color based on sequence length
            if len(seq) >= 2:
                combat_combo_sequence.config(fg="orange")
            elif len(seq) == 1:
                combat_combo_sequence.config(fg="yellow")
            else:
                combat_combo_sequence.config(fg="green")
                
        # Update progress bar if available
        if combat_combo_progress:
            # Check if it's a Canvas (from UI service) or Progressbar (local)
            if hasattr(combat_combo_progress, 'create_rectangle'):
                # It's a Canvas - draw progress bar
                combat_combo_progress.delete("progress_bar")  # Clear existing
                width = combat_combo_progress.winfo_width()
                height = combat_combo_progress.winfo_height()
                if width > 1 and height > 1:  # Make sure canvas is properly sized
                    progress_width = int(width * pct / 100)
                    if progress_width > 0:
                        color = "#4CAF50" if pct < 75 else "#FF9800"  # Green to orange
                        combat_combo_progress.create_rectangle(
                            0, 0, progress_width, height,
                            fill=color, tags="progress_bar", outline=""
                        )
            else:
                # It's a Progressbar - set value
                try:
                    combat_combo_progress['value'] = pct
                except tk.TclError:
                    # Widget doesn't support value property, skip
                    pass

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
            # Update displays during countdown
            self.update_combo_tab()
            self.root.after(100, self.start_combo_timer)  # Update every 100ms
        else:
            # Timer expired, clear sequence
            if hasattr(self, 'combo_sequence'):
                self.combo_sequence = []
                self.update_combo_tab()

    def setup_stats_tab(self):
        """Set up the enhanced character stats tab with detailed equipment info."""
        # Create main container with better organization
        main_container = tk.Frame(self.stats_tab, bg="black")
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

        self.basic_info = tk.Text(
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
        self.basic_info.pack(fill=tk.BOTH, expand=True, pady=5)

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
        
        self.status_effects_display = tk.Text(
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
        self.status_effects_display.pack(fill=tk.BOTH, expand=True, pady=5)

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

        self.detailed_stats = tk.Text(
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
        self.detailed_stats.pack(fill=tk.BOTH, expand=True, pady=5)

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
        self.equipment_slots_frame = tk.Frame(equipment_frame, bg="#2c3e50", relief=tk.GROOVE, bd=2)
        self.equipment_slots_frame.pack(fill=tk.X, pady=5, padx=5)
        
        self._create_equipment_slots_display()

        # Equipment actions
        eq_actions_frame = tk.Frame(equipment_frame, bg="black")
        eq_actions_frame.pack(fill=tk.X, pady=5)

        eq_buttons = [
            ("🔍 Inspect Gear", self._inspect_equipment_placeholder, "#3498db"),
            ("⚔️ Quick Equip", self.equip_gear, "#e74c3c"),
            ("🛡️ Optimize Defense", self._optimize_defense_placeholder, "#2ecc71"),
            ("🎒 Manage Inventory", self.view_inventory, "#9b59b6")
        ]

        for text, command, color in eq_buttons:
            btn = tk.Button(
                eq_actions_frame,
                text=text,
                command=command,
                bg=color,
                fg="white",
                font=("Arial", 9, "bold"),
                relief=tk.RAISED,
                bd=1,
                width=18
            )
            btn.pack(pady=2, fill=tk.X)

        # === BOTTOM SECTION: Action Buttons ===
        bottom_frame = tk.Frame(main_container, bg="black")
        bottom_frame.pack(fill=tk.X, pady=(10, 0))

        # Enhanced button grid with better organization
        button_grid_frame = tk.Frame(bottom_frame, bg="black")
        button_grid_frame.pack()

        # Character Management Buttons
        char_buttons = [
            ("📊 View Stats", self.detailed_character_view, "#3498db"),
            ("⬆️ Level Up", self.on_level_up_button_clicked, "#2ecc71"),
            ("🎒 Inventory", self.view_inventory, "#9b59b6"),
        ]

        # Resource Management Buttons  
        resource_buttons = [
            ("❤️ Restore HP", self.restore_health, "#e74c3c"),
            ("💧 Restore MP", self.restore_mana, "#3498db"),
            ("⚡ Restore SP", self.restore_stamina, "#f39c12"),
        ]

        # System Buttons
        system_buttons = [
            ("💾 Save Game", self.save_game, "#34495e"),
            ("📁 Load Game", self.load_game, "#2ecc71"),
            ("🔄 Reload", self.reload_game, "#95a5a6"),
        ]

        # Create button sections
        self._create_button_section(button_grid_frame, "Character", char_buttons, 0)
        self._create_button_section(button_grid_frame, "Resources", resource_buttons, 1)
        self._create_button_section(button_grid_frame, "System", system_buttons, 2)

    def _create_equipment_slots_display(self):
        """Create visual equipment slots display."""
        # Clear existing widgets
        for widget in self.equipment_slots_frame.winfo_children():
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

        # Create grid layout for equipment slots
        for i, (icon, name, attr) in enumerate(slots_data):
            row = i // 2
            col = i % 2
            
            slot_frame = tk.Frame(self.equipment_slots_frame, bg="#34495e", relief=tk.RAISED, bd=1)
            slot_frame.grid(row=row, column=col, padx=2, pady=2, sticky="ew")
            
            # Configure column weights
            self.equipment_slots_frame.grid_columnconfigure(col, weight=1)
            
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
            setattr(self, f"slot_{attr}_label", item_label)











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
        
        # Use a proper progress bar instead of canvas
        self.combat_combo_progress = ttk.Progressbar(
            combo_indicator, 
            mode='determinate', 
            style='Combat.Horizontal.TProgressbar'
        )
        self.combat_combo_progress.pack(fill=tk.X, padx=5, pady=2)
        self.combat_combo_progress['maximum'] = 100
        
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
            ("Attack", self.on_attack_button_clicked, "#d9534f"),
            ("Heal", self.on_heal_button_clicked, "#5cb85c"),
            ("Spawn Enemy", self.on_spawn_enemy_button_clicked, "#f0ad4e"),
            ("Cast Fireball", self.on_fireball_button_clicked, "#ff7043"),
            ("Cast Ice Shard", self.on_ice_shard_button_clicked, "#42a5f5"),
            ("Test Dual Wield", self.test_dual_wield, "#9c27b0"),
            ("Quick Equipment", self.test_equipment_quick, "#ff6600"),
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
        # Try to use UI service first, fallback to direct console log
        if hasattr(self, 'ui_service') and self.ui_service:
            result = self.ui_service.log_message(message, tag)
            if result.get('success', False):
                # Also log to logger
                logger.info(message)
                return
        
        # Fallback to original implementation
        timestamp = time.strftime("%H:%M:%S")
        self.log.insert(tk.END, f"[{timestamp}] ", "info")
        self.log.insert(tk.END, f"{message}\n", tag)
        self.log.see(tk.END)

        # Also log to logger
        logger.info(message)

    def setup_game_state(self):
        """Set up the initial game state."""
        logger.info("Setting up game state")

        # Log pending observer message if available
        if hasattr(self, '_pending_observer_message'):
            self.log_message(self._pending_observer_message, "info")
            delattr(self, '_pending_observer_message')

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

        # Wire up controller classes with actual services
        self._wire_controllers()

        # Create player character
        from game_sys.character.leveling_manager import LevelingManager
        from game_sys.config.config_manager import ConfigManager
        
        # Get grade constants from config
        cfg = ConfigManager()
        grade_list = cfg.get('defaults.grades', ["ONE", "TWO", "THREE", "FOUR", "FIVE", "SIX", "SEVEN"])
        
        # Create player character with specific grade and rarity
        # Using grade index 0 (ONE) for starting character
        self.player = create_character(
            template_id="hero",
            level=1, grade=0, rarity="COMMON"  # grade 0 = ONE from config
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
            "dragon", level=50, grade=0, rarity="COMMON"  # grade 0 = ONE from config
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
            enemy_grade = getattr(self.enemy, 'grade', 0)
            enemy_grade_display = self._get_grade_display(enemy_grade)
            enemy_info = (
                f"A {self.enemy.name} appears! "
                f"(Level {getattr(self.enemy, 'level', 100)}, "
                f"Grade {enemy_grade_display}, "
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
        """Update the character info displays with comprehensive details."""
        if not hasattr(self, 'player') or not self.player:
            return

        # Always use enhanced implementation for better character display
        # The UI service basic implementation is too limited
        self._update_character_display_enhanced()

    def _update_character_display_enhanced(self):
        """Enhanced character display implementation."""
        # Get widgets from UI service or use local widgets
        basic_info_widget = None
        detailed_stats_widget = None
        status_effects_widget = None
        
        # Try UI service widgets first
        if (hasattr(self, 'ui_service') and self.ui_service and 
            hasattr(self.ui_service, 'widgets')):
            basic_info_widget = self.ui_service.widgets.get('basic_info')
            detailed_stats_widget = self.ui_service.widgets.get('detailed_stats') 
            status_effects_widget = self.ui_service.widgets.get('status_effects_display')
        
        # Fallback to local widgets
        if not basic_info_widget and hasattr(self, 'basic_info'):
            basic_info_widget = self.basic_info
        if not detailed_stats_widget and hasattr(self, 'detailed_stats'):
            detailed_stats_widget = self.detailed_stats
        if not status_effects_widget and hasattr(self, 'status_effects_display'):
            status_effects_widget = self.status_effects_display

        # Update basic info if widget available
        if basic_info_widget:
            try:
                basic_info_widget.config(state="normal")
                basic_info_widget.delete(1.0, tk.END)
                basic_info = self._build_basic_character_info()
                basic_info_widget.insert(tk.END, basic_info)
                basic_info_widget.config(state="disabled")
            except tk.TclError:
                # Widget might not support these operations
                pass

        # Update detailed stats if widget available
        if detailed_stats_widget:
            try:
                detailed_stats_widget.config(state="normal")
                detailed_stats_widget.delete(1.0, tk.END)
                detailed_info = self._build_detailed_character_info()
                detailed_stats_widget.insert(tk.END, detailed_info)
                detailed_stats_widget.config(state="disabled")
            except tk.TclError:
                # Widget might not support these operations
                pass

        # Update status effects if widget available
        if status_effects_widget:
            try:
                status_effects_widget.config(state="normal")
                status_effects_widget.delete(1.0, tk.END)
                status_info = self._build_status_effects_info()
                status_effects_widget.insert(tk.END, status_info)
                status_effects_widget.config(state="disabled")
            except tk.TclError:
                # Widget might not support these operations
                pass

        # Update equipment display if available
        if hasattr(self, 'ui_service') and self.ui_service:
            self.ui_service.update_equipment_slots(self.player)

    def _update_performance_metrics(self):
        """Update combat effectiveness and equipment coverage metrics."""
        if not hasattr(self, 'player') or not self.player:
            return
            
        try:
            # Calculate Attack Rating
            attack_rating = self._calculate_attack_rating()
            max_attack = 100  # Reasonable maximum for display
            attack_percent = min(attack_rating / max_attack, 1.0)
            
            # Update attack rating bar
            if hasattr(self, 'attack_rating_bar'):
                self.attack_rating_bar.delete("all")
                bar_width = 100
                fill_width = int(bar_width * attack_percent)
                
                # Background bar
                self.attack_rating_bar.create_rectangle(0, 2, bar_width, 10, fill="gray20", outline="")
                
                # Fill bar with color based on rating
                if attack_percent > 0.7:
                    fill_color = "#27ae60"  # Green for high
                elif attack_percent > 0.4:
                    fill_color = "#f39c12"  # Orange for medium
                else:
                    fill_color = "#e74c3c"  # Red for low
                    
                if fill_width > 0:
                    self.attack_rating_bar.create_rectangle(0, 2, fill_width, 10, fill=fill_color, outline="")
                    
            # Update attack rating label
            if hasattr(self, 'attack_rating_label'):
                self.attack_rating_label.config(text=f"{attack_rating:.0f}")
            
            # Calculate Defense Rating
            defense_rating = self._calculate_defense_rating()
            max_defense = 50  # Reasonable maximum for display
            defense_percent = min(defense_rating / max_defense, 1.0)
            
            # Update defense rating bar
            if hasattr(self, 'defense_rating_bar'):
                self.defense_rating_bar.delete("all")
                fill_width = int(bar_width * defense_percent)
                
                # Background bar
                self.defense_rating_bar.create_rectangle(0, 2, bar_width, 10, fill="gray20", outline="")
                
                # Fill bar with color
                if defense_percent > 0.7:
                    fill_color = "#3498db"  # Blue for high defense
                elif defense_percent > 0.4:
                    fill_color = "#f39c12"  # Orange for medium
                else:
                    fill_color = "#e74c3c"  # Red for low
                    
                if fill_width > 0:
                    self.defense_rating_bar.create_rectangle(0, 2, fill_width, 10, fill=fill_color, outline="")
                    
            # Update defense rating label
            if hasattr(self, 'defense_rating_label'):
                self.defense_rating_label.config(text=f"{defense_rating:.0f}")
                
            # Calculate Equipment Coverage
            coverage_count, total_slots = self._calculate_equipment_coverage()
            coverage_percent = coverage_count / total_slots if total_slots > 0 else 0
            
            # Update equipment coverage bar
            if hasattr(self, 'coverage_progress'):
                self.coverage_progress.delete("all")
                bar_width = 120
                fill_width = int(bar_width * coverage_percent)
                
                # Background
                self.coverage_progress.create_rectangle(1, 2, bar_width-1, 13, fill="gray20", outline="gray")
                
                # Fill based on coverage
                if coverage_percent > 0.8:
                    fill_color = "#27ae60"  # Green for well-equipped
                elif coverage_percent > 0.5:
                    fill_color = "#f39c12"  # Orange for partial
                else:
                    fill_color = "#e74c3c"  # Red for poorly equipped
                    
                if fill_width > 1:
                    self.coverage_progress.create_rectangle(1, 2, fill_width, 13, fill=fill_color, outline="")
                    
            # Update coverage label
            if hasattr(self, 'coverage_label'):
                self.coverage_label.config(text=f"{coverage_count}/{total_slots} slots")
                
        except Exception as e:
            # Silently handle any errors to avoid breaking the UI
            pass

    def _update_build_recommendations(self):
        """Update character build recommendations based on current equipment and stats."""
        if not hasattr(self, 'player') or not self.player:
            return
            
        if not hasattr(self, 'build_recommendations'):
            return
            
        try:
            self.build_recommendations.config(state="normal")
            self.build_recommendations.delete(1.0, tk.END)
            
            recommendations = self._analyze_character_build()
            self.build_recommendations.insert(tk.END, recommendations)
            self.build_recommendations.config(state="disabled")
            
        except Exception:
            pass

    def _calculate_attack_rating(self):
        """Calculate overall attack rating for the character."""
        total_attack = 0
        
        # Primary weapon damage
        weapon = getattr(self.player, 'weapon', None)
        if weapon and hasattr(weapon, 'base_damage'):
            total_attack += weapon.base_damage
            
        # Offhand weapon damage (with dual-wield penalty)
        offhand = getattr(self.player, 'offhand', None)
        if offhand and hasattr(offhand, 'base_damage'):
            total_attack += offhand.base_damage * 0.75  # Dual-wield penalty
            
        # Strength/stat modifiers if available
        if hasattr(self.player, 'get_stat'):
            try:
                strength = self.player.get_stat('strength')
                total_attack += strength * 0.5  # Strength contributes to attack
            except:
                pass
                
        return max(total_attack, 1)  # Minimum of 1 for unarmed

    def _calculate_defense_rating(self):
        """Calculate overall defense rating for the character."""
        total_defense = 0
        
        # Armor defense values
        armor_slots = ['equipped_body', 'equipped_helmet', 'equipped_feet', 'equipped_cloak']
        for slot in armor_slots:
            item = getattr(self.player, slot, None)
            if item and hasattr(item, 'defense'):
                total_defense += item.defense
                
        # Shield defense
        offhand = getattr(self.player, 'offhand', None)
        if offhand and hasattr(offhand, 'defense'):
            total_defense += offhand.defense
            
        # Constitution modifier if available
        if hasattr(self.player, 'get_stat'):
            try:
                constitution = self.player.get_stat('constitution')
                total_defense += constitution * 0.2  # Constitution contributes to defense
            except:
                pass
                
        return total_defense

    def _calculate_equipment_coverage(self):
        """Calculate how many equipment slots are filled."""
        equipment_slots = ['weapon', 'offhand', 'equipped_body', 'equipped_helmet', 
                          'equipped_feet', 'equipped_cloak', 'equipped_ring']
        
        equipped_count = 0
        for slot in equipment_slots:
            if hasattr(self.player, slot) and getattr(self.player, slot, None) is not None:
                equipped_count += 1
                
        return equipped_count, len(equipment_slots)

    def _analyze_character_build(self):
        """Analyze character build and provide recommendations."""
        analysis = "BUILD ANALYSIS\n"
        analysis += "─" * 15 + "\n\n"
        
        # Fighting Style Analysis
        weapon = getattr(self.player, 'weapon', None)
        offhand = getattr(self.player, 'offhand', None)
        
        if weapon and offhand and hasattr(offhand, 'base_damage'):
            analysis += "Style: Dual Wielder\n"
            analysis += "✓ High DPS potential\n"
            analysis += "⚠ Needs accuracy gear\n\n"
        elif weapon and offhand and hasattr(offhand, 'defense'):
            analysis += "Style: Sword & Board\n"
            analysis += "✓ Balanced fighter\n"
            analysis += "✓ Good survivability\n\n"
        elif weapon and getattr(weapon, 'two_handed', False):
            analysis += "Style: Two-Handed\n"
            analysis += "✓ Maximum damage\n"
            analysis += "⚠ No shield defense\n\n"
        else:
            analysis += "Style: Basic Fighter\n"
            analysis += "⚠ Needs better gear\n\n"
            
        # Equipment Recommendations
        coverage_count, total_slots = self._calculate_equipment_coverage()
        
        if coverage_count < total_slots // 2:
            analysis += "PRIORITY: Get more gear!\n"
            analysis += f"Only {coverage_count}/{total_slots} equipped\n\n"
            
        # Missing equipment analysis
        missing_slots = []
        essential_slots = [('weapon', 'Weapon'), ('equipped_body', 'Armor')]
        
        for slot, name in essential_slots:
            if not getattr(self.player, slot, None):
                missing_slots.append(name)
                
        if missing_slots:
            analysis += "MISSING ESSENTIALS:\n"
            for item in missing_slots:
                analysis += f"• {item}\n"
            analysis += "\n"
            
        # Stat recommendations
        attack_rating = self._calculate_attack_rating()
        defense_rating = self._calculate_defense_rating()
        
        if attack_rating < 10:
            analysis += "⚠ Low attack power\n"
        if defense_rating < 5:
            analysis += "⚠ Very vulnerable\n"
            
        # Build strengths
        if attack_rating > 30:
            analysis += "✓ Strong offense\n"
        if defense_rating > 15:
            analysis += "✓ Good defense\n"
            
        return analysis

    def _update_quick_stats_bars(self):
        """Update the quick HP/MP bars in the portrait area."""
        if not hasattr(self, 'player') or not self.player:
            return
            
        try:
            # Update HP bar
            if hasattr(self, 'hp_bar') and hasattr(self, 'hp_label'):
                current_hp = getattr(self.player, 'current_health', 0)
                max_hp = getattr(self.player, 'max_health', 1)
                hp_percent = current_hp / max_hp if max_hp > 0 else 0
                
                self.hp_bar.delete("all")
                bar_width = 100
                fill_width = int(bar_width * hp_percent)
                
                # Background
                self.hp_bar.create_rectangle(0, 0, bar_width, 8, fill="gray20", outline="")
                
                # HP fill - color changes based on health percentage
                if hp_percent > 0.6:
                    hp_color = "#27ae60"  # Green
                elif hp_percent > 0.3:
                    hp_color = "#f39c12"  # Orange
                else:
                    hp_color = "#e74c3c"  # Red
                    
                if fill_width > 0:
                    self.hp_bar.create_rectangle(0, 0, fill_width, 8, fill=hp_color, outline="")
                    
                # Update HP label
                self.hp_label.config(text=f"{current_hp:.0f}/{max_hp:.0f}")
                
            # Update MP bar
            if hasattr(self, 'mp_bar') and hasattr(self, 'mp_label'):
                current_mp = getattr(self.player, 'current_mana', 0)
                max_mp = getattr(self.player, 'max_mana', 1)
                mp_percent = current_mp / max_mp if max_mp > 0 else 0
                
                self.mp_bar.delete("all")
                fill_width = int(bar_width * mp_percent)
                
                # Background
                self.mp_bar.create_rectangle(0, 0, bar_width, 8, fill="gray20", outline="")
                
                # MP fill - always blue
                if fill_width > 0:
                    self.mp_bar.create_rectangle(0, 0, fill_width, 8, fill="#3498db", outline="")
                    
                # Update MP label
                self.mp_label.config(text=f"{current_mp:.0f}/{max_mp:.0f}")
                
        except Exception:
            pass

    def _get_grade_display(self, grade):
        """Convert grade to display format using Grade enum."""
        if grade is None:
            return "Unknown"
        
        # Handle Grade enum values - use enum name instead of Roman numerals
        if isinstance(grade, Grade):
            return grade.name
        
        # Handle integer indices (0-indexed)
        if isinstance(grade, int):
            grade_list = [Grade.ONE, Grade.TWO, Grade.THREE, Grade.FOUR, Grade.FIVE, Grade.SIX, Grade.SEVEN]
            if 0 <= grade < len(grade_list):
                return grade_list[grade].name
            return f"Grade {grade + 1}"  # fallback
        
        # Handle string names
        if isinstance(grade, str):
            try:
                grade_enum = Grade[grade.upper()]
                return grade_enum.name
            except KeyError:
                return grade.upper()  # fallback to original string
        
        return str(grade)

    def _get_rarity_display(self, rarity):
        """Convert rarity to display format using Rarity enum."""
        if rarity is None:
            return "Unknown"
        
        # Handle Rarity enum values
        if isinstance(rarity, Rarity):
            return rarity.name.title()
        
        # Handle string names
        if isinstance(rarity, str):
            try:
                rarity_enum = Rarity[rarity.upper()]
                return rarity_enum.name.title()
            except KeyError:
                return rarity.title()
        
        return str(rarity)

    def _build_basic_character_info(self):
        """Build enhanced basic character information."""
        info = f"╔═ {self.player.name} ═╗\n"
        
        # Core Identity
        info += f"Level: {self.player.level}"
        if hasattr(self.player, 'experience') and hasattr(self.player, 'next_level_xp'):
            info += f" ({self.player.experience}/{self.player.next_level_xp} XP)\n"
        else:
            info += "\n"
            
        # Grade and Rarity with enhanced display
        if hasattr(self.player, 'grade'):
            grade_display = self._get_grade_display(self.player.grade)
            info += f"Grade: {grade_display}\n"
        if hasattr(self.player, 'rarity'):
            info += f"Rarity: {self.player.rarity}\n"

        # Enhanced Resource Display
        info += "\n── VITALS ──\n"
        info += f"HP: {self.player.current_health:.0f}/{self.player.max_health:.0f}\n"
        
        if hasattr(self.player, 'current_mana') and hasattr(self.player, 'max_mana'):
            info += f"MP: {self.player.current_mana:.0f}/{self.player.max_mana:.0f}\n"
        
        if hasattr(self.player, 'current_stamina') and hasattr(self.player, 'max_stamina'):
            info += f"SP: {self.player.current_stamina:.0f}/{self.player.max_stamina:.0f}\n"

        # Combat Summary
        info += "\n── COMBAT ──\n"
        weapon = getattr(self.player, 'weapon', None)
        if weapon:
            base_damage = getattr(weapon, 'base_damage', 0)
            damage_type = getattr(weapon, 'damage_type', 'PHYSICAL')
            info += f"ATK: {base_damage} ({damage_type})\n"
        else:
            info += f"ATK: Unarmed (0)\n"

        # Defense calculation
        total_defense = 0
        body_armor = getattr(self.player, 'equipped_body', None)
        if body_armor:
            defense = getattr(body_armor, 'defense', 0)
            total_defense += defense
            
        info += f"DEF: {total_defense}\n"

        #Magic Power
        magic_power = getattr(self.player, 'get_stat', lambda x: 0)('magic_power')
        if magic_power:
            info += f"MGK PWR: {magic_power:.0f}\n"

        # Equipment Summary
        info += "\n── GEAR ──\n"
        equipped_count = 0
        if weapon:
            equipped_count += 1
        if getattr(self.player, 'offhand', None):
            equipped_count += 1
        if body_armor:
            equipped_count += 1
            
        info += f"Equipped: {equipped_count}/6 slots\n"
        
        return info

    def _build_detailed_character_info(self):
        """Build comprehensive detailed character information."""
        info = f"╔════════════════════════╗\n"
        info += f"║    {self.player.name:^18}  ║\n"
        info += f"╚════════════════════════╝\n\n"

        # Core Statistics with calculations
        info += "╔═══ CORE ATTRIBUTES ═══╗\n"
        if hasattr(self.player, 'base_stats') and isinstance(self.player.base_stats, dict):
            core_stats = self._get_core_stats()
            for stat_name, base_val, effective_val in core_stats:
                display_name = stat_name.replace("_", " ").title()
                if abs(effective_val - base_val) > 0.01:  # Show both if different
                    info += f"  {display_name:.<12}: {effective_val:.0f}\n"
                else:
                    info += f"  {display_name:.<12}: {effective_val:.0f}\n"

        # Enhanced Equipment Section
        info += "\n╔═══ EQUIPMENT DETAILS ═══╗\n"
        info += self._build_equipment_details()

        # Combat Statistics
        info += "\n╔═══ COMBAT ANALYSIS ═══╗\n"
        info += self._build_combat_analysis()

        # Resistance and Weaknesses
        if hasattr(self.player, 'resistances') and self.player.resistances:
            info += "\n╔═══ RESISTANCES ═══╗\n"
            for damage_type, value in self.player.resistances.items():
                info += f"{damage_type}: {value:.1%} reduction\n"

        if hasattr(self.player, 'weaknesses') and self.player.weaknesses:
            info += "\n╔═══ WEAKNESSES ═══╗\n"
            for damage_type, value in self.player.weaknesses.items():
                info += f"{damage_type}: +{value:.1%} damage taken\n"

        # Inventory Summary
        info += "\n╔═══ INVENTORY ═══╗\n"
        if hasattr(self.player, 'inventory'):
            items = self.player.inventory.list_items()
            if items:
                # Categorize items
                weapons = [i for i in items if getattr(i, 'slot', '') in ['weapon', 'two_handed']]
                armor = [i for i in items if getattr(i, 'slot', '') in ['body', 'helmet', 'feet']]
                consumables = [i for i in items if getattr(i, 'slot', '') == 'consumable']
                others = [i for i in items if i not in weapons + armor + consumables]
                
                info += f"Total Items: {len(items)}\n"
                if weapons:
                    info += f" Weapons: {len(weapons)}\n"
                if armor:
                    info += f" Armor: {len(armor)}\n"
                if consumables:
                    info += f"Consumables: {len(consumables)}\n"
                if others:
                    info += f"Other: {len(others)}\n"

                info += "\n  Recent Items:\n"
                for item in items[-3:]:  # Show last 3 items
                    item_type = getattr(item, 'slot', 'misc')
                    icon = self._get_item_icon(item_type)
                    info += f"    {icon} {item.name}\n"
            else:
                info += "Inventory: Empty\n"
        else:
            info += "No inventory system available\n"

        return info

    def _build_equipment_details(self):
        """Build detailed equipment information with stats."""
        info = ""
        
        # Weapon Details
        weapon = getattr(self.player, 'weapon', None)
        if weapon:
            info += f"  ⚔️  Weapon: {weapon.name}\n"
            if hasattr(weapon, 'base_damage'):
                damage_type = getattr(weapon, 'damage_type', 'PHYSICAL')
                info += f"      💥 Damage: {weapon.base_damage} ({damage_type})\n"
            if hasattr(weapon, 'stats') and weapon.stats:
                info += f"      📊 Bonuses: {self._format_item_stats(weapon.stats)}\n"
            if hasattr(weapon, 'enchantments') and weapon.enchantments:
                info += f"      ✨ Enchantments: {len(weapon.enchantments)}\n"
        else:
            info += "  ⚔️  Weapon: (None)\n"

        # Offhand Details
        offhand = getattr(self.player, 'offhand', None)
        if offhand:
            info += f"  🛡️  Offhand: {offhand.name}\n"
            if hasattr(offhand, 'defense'):
                info += f"      🛡️  Defense: {offhand.defense}\n"
            elif hasattr(offhand, 'base_damage'):
                damage_type = getattr(offhand, 'damage_type', 'PHYSICAL')
                info += f"      💥 Damage: {offhand.base_damage} ({damage_type})\n"
            if hasattr(offhand, 'block_chance'):
                info += f"      🚫 Block: {offhand.block_chance:.1%}\n"
            if hasattr(offhand, 'stats') and offhand.stats:
                info += f"      📊 Bonuses: {self._format_item_stats(offhand.stats)}\n"
        else:
            info += "  🛡️  Offhand: (None)\n"

        # Body Armor Details
        body_armor = getattr(self.player, 'equipped_body', None)
        if body_armor:
            info += f"  🛡️  Armor: {body_armor.name}\n"
            if hasattr(body_armor, 'defense'):
                info += f"      🛡️  Defense: {body_armor.defense}\n"
            if hasattr(body_armor, 'stats') and body_armor.stats:
                info += f"      📊 Bonuses: {self._format_item_stats(body_armor.stats)}\n"
        else:
            info += "  🛡️  Armor: (None)\n"

        # Additional Slots
        for slot_name, display_name, icon in [
            ('equipped_helmet', 'Helmet', '⛑️'),
            ('equipped_feet', 'Boots', '👢'),
            ('equipped_cloak', 'Cloak', '🎭'),
            ('equipped_ring', 'Ring', '💍')
        ]:
            item = getattr(self.player, slot_name, None)
            if item:
                info += f"  {icon} {display_name}: {item.name}\n"
                if hasattr(item, 'stats') and item.stats:
                    info += f"      📊 Bonuses: {self._format_item_stats(item.stats)}\n"

        # Dual-Wield Status
        dual_wield_info = self._get_dual_wield_status()
        if dual_wield_info:
            info += f"\n  ⚡ Status: {dual_wield_info}\n"
            
        return info

    def _build_combat_analysis(self):
        """Build detailed combat statistics analysis using scaled stats."""
        info = ""
        
        # Display combat stats directly from the scaler
        if hasattr(self.player, 'get_stat'):
            try:
                # Attack/damage stats
                attack = self.player.get_stat('attack')
                info += f"Attack: {attack:.1f}\n"
            except:
                info += f"Attack: N/A\n"
                
            try:
                # Defense stats
                defense = self.player.get_stat('defense')
                info += f"Defense: {defense:.1f}\n"
            except:
                info += f"Defense: N/A\n"
                
            try:
                # Critical hit chance
                crit_chance = self.player.get_stat('critical_chance')
                info += f"Crit Chance: {crit_chance:.1%}\n"
            except:
                pass
                
            try:
                # Block chance
                block_chance = self.player.get_stat('block_chance')
                info += f"Block Chance: {block_chance:.1%}\n"
            except:
                pass
                
            try:
                # Additional combat stats if available
                accuracy = self.player.get_stat('accuracy')
                info += f"Accuracy: {accuracy:.1f}\n"
            except:
                pass
                
            try:
                dodge_chance = self.player.get_stat('dodge_chance')
                info += f"Dodge: {dodge_chance:.1%}\n"
            except:
                pass
        else:
            info += "Combat stats not available\n"

        return info

    def _build_status_effects_info(self):
        """Build active status effects information."""
        if not hasattr(self.player, 'status_effects') or not self.player.status_effects:
            return "No active effects"
            
        info = "═══ ACTIVE EFFECTS ═══\n"
        for effect_id, effect_data in self.player.status_effects.items():
            effect_name = effect_id.replace('_', ' ').title()
            duration = effect_data.get('duration', 'Permanent')
            if isinstance(duration, (int, float)) and duration > 0:
                info += f"✨ {effect_name} ({duration:.0f}s)\n"
            else:
                info += f"✨ {effect_name}\n"
                
            # Show effect details if available
            if 'stat' in effect_data and 'amount' in effect_data:
                stat_name = effect_data['stat'].replace('_', ' ').title()
                amount = effect_data['amount']
                sign = '+' if amount > 0 else ''
                info += f"{stat_name}: {sign}{amount}\n"
                
        return info

    def _get_core_stats(self):
        """Get comprehensive statistics organized in categories with effective values."""
        stats = []
        if not hasattr(self.player, 'base_stats'):
            return stats
            
        # Primary attributes that should always be shown first
        primary_stats = ['strength', 'dexterity', 'intelligence', 'wisdom', 'constitution',
                        'vitality', 'agility', 'luck', 'focus']
        
        # Combat-related stats
        combat_stats = ['accuracy', 'critical_chance', 'speed',
                       'defense', 'magic_defense', 'dodge_chance', 'parry_chance', 'block_chance']
        
        # Derived/calculated stats  
        derived_stats = ['max_health', 'max_mana', 'max_stamina', 'health_regen', 'mana_regen', 'stamina_regen',
                        'initiative', 'speed', 'carrying_capacity']
        
        # Stats to exclude from display (meta information)
        meta_keys = {"grade", "rarity", "skip_default_job", "max_targets", "level"}
        
        def add_stat_if_available(stat_name, category_prefix=""):
            """Helper to add a stat if it's available."""
            # Check base_stats first
            base_val = None
            if hasattr(self.player, 'base_stats') and stat_name in self.player.base_stats:
                base_val = self.player.base_stats[stat_name]
            # Check direct attributes
            elif hasattr(self.player, stat_name):
                base_val = getattr(self.player, stat_name)
            else:
                return False  # Stat not available
                
            try:
                # For derived stats like max_health, max_mana, etc., prefer direct attributes over get_stat
                # as get_stat may not be properly configured for derived stats
                if stat_name in ['max_health', 'max_mana', 'max_stamina', 'health_regen', 'mana_regen', 'stamina_regen']:
                    if hasattr(self.player, stat_name):
                        effective_val = getattr(self.player, stat_name)
                    elif hasattr(self.player, 'get_stat'):
                        effective_val = self.player.get_stat(stat_name)
                    else:
                        effective_val = base_val
                else:
                    # For other stats, use get_stat method if available
                    if hasattr(self.player, 'get_stat'):
                        effective_val = self.player.get_stat(stat_name)
                    else:
                        effective_val = base_val
                    
                display_name = category_prefix + stat_name
                stats.append((display_name, base_val, effective_val))
                return True
            except Exception:
                # Fallback to base value
                display_name = category_prefix + stat_name
                stats.append((display_name, base_val, base_val))
                return True
        
        # Add primary stats first
        for stat_name in primary_stats:
            add_stat_if_available(stat_name)
                
        # Add combat stats
        for stat_name in combat_stats:
            add_stat_if_available(stat_name)
            
        # Add derived stats  
        for stat_name in derived_stats:
            add_stat_if_available(stat_name)
        
        # Add any additional stats from base_stats that weren't covered
        if hasattr(self.player, 'base_stats') and isinstance(self.player.base_stats, dict):
            covered_stats = set(primary_stats + combat_stats + derived_stats)
            
            for stat_name, base_val in sorted(self.player.base_stats.items()):
                if (stat_name not in covered_stats and 
                    stat_name not in meta_keys and 
                    not stat_name.startswith("_")):
                    add_stat_if_available(stat_name)
                    
        return stats



    def _format_item_stats(self, stats_dict):
        """Format item stats for display."""
        if not stats_dict:
            return "None"
            
        formatted = []
        for stat, value in stats_dict.items():
            stat_name = stat.replace('_', ' ').title()
            sign = '+' if value > 0 else ''
            formatted.append(f"{stat_name} {sign}{value}")
            
        return ', '.join(formatted)

    def _get_item_icon(self, item_type):
        """Get icon for item type."""
        icons = {
            'weapon': '⚔️',
            'two_handed': '🗡️',
            'armor': '🛡️',
            'body': '👕',
            'helmet': '⛑️',
            'feet': '👢',
            'consumable': '🧪',
            'accessory': '💎',
            'material': '🔨',
            'offhand': '🛡️',
        }
        return icons.get(item_type, '📦')

    def _get_dual_wield_status(self):
        """Get dual-wield status information."""
        try:
            return equipment_manager.get_dual_wield_status_info(self.player)
        except:
            weapon = getattr(self.player, 'weapon', None)
            offhand = getattr(self.player, 'offhand', None)
            
            if weapon and offhand:
                if getattr(offhand, 'base_damage', 0) > 0:  # Weapon in offhand
                    return "Dual Wielding"
                else:
                    return "Weapon + Shield"
            elif weapon and getattr(weapon, 'two_handed', False):
                return "Two-Handed Weapon"
            elif weapon:
                return "Single Weapon"
            else:
                return "Unarmed"

    def update_enemy_info(self):
        """Update the enemy info display."""
        
        # Try to use UI service for enemy display if available
        if hasattr(self, 'ui_service') and self.ui_service and hasattr(self, 'enemy') and self.enemy:
            try:
                # Prepare enemy data for UI service
                enemy_data = {
                    'name': self.enemy.name,
                    'level': getattr(self.enemy, 'level', 'Unknown'),
                    'current_health': getattr(self.enemy, 'current_health', 0),
                    'max_health': getattr(self.enemy, 'max_health', 1),
                    'enemy': self.enemy  # Pass the full enemy object
                }
                
                # Try to delegate to UI service
                result = self.ui_service.update_enemy_display(enemy_data)
                if result.get('success', False):
                    logger.info("Enemy display updated via UI service")
                    return
                else:
                    logger.debug(f"UI service enemy update failed: {result.get('message', 'Unknown error')}")
            except Exception as e:
                logger.debug(f"UI service enemy update error: {e}")
        
        # Fallback to original implementation
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
        """Level up the character using character controller."""
        if not hasattr(self, 'player') or not self.player:
            self.log_message("No player character available!")
            return

        # Use character controller for level up
        success = self.character_controller.level_up_character(self.player)

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
        """Legacy method - use on_fireball_button_clicked() instead."""
        return self.on_fireball_button_clicked()

    def cast_ice_shard(self):
        """Legacy method - use on_ice_shard_button_clicked() instead."""
        return self.on_ice_shard_button_clicked()

    def draw_game_state(self):
        """Draw the current game state on the canvas."""
        # Safety check - canvas might not exist during initialization
        if not hasattr(self, 'canvas') or not self.canvas:
            return
            
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

    # ============================================================================
    # EVENT HANDLER METHODS - Task #3 Implementation
    # ============================================================================

    def on_attack_button_clicked(self):
        """Handle attack button click - delegate to combat controller."""
        if not hasattr(self, 'player') or not self.player:
            logger.warning("No player to attack with")
            return
        if not hasattr(self, 'enemy') or not self.enemy:
            logger.warning("No enemy to attack")
            self.log_message("No enemy to attack!", "combat")
            return

        # Delegate to combat controller
        result = self.combat_controller.perform_attack(
            self.player, self.enemy, self.player.weapon
        )

        if result['success']:
            # Visual effects only
            self.create_particles(450, 200, "red", 15)

            # Handle enemy defeat and loot
            if result['defeated']:
                if result['loot']:
                    loot_names = [item.name for item in result['loot']]
                    loot_msg = f"Loot obtained: {', '.join(loot_names)}"
                    self.log_message(loot_msg, "info")
                self.enemy = None
            else:
                # AI turn processing
                if self.ai_enabled and self.ai_controller and self.enemy:
                    try:
                        self.ai_controller.process_ai_turn(self.enemy, self.player, 0.0)
                    except Exception as e:
                        logger.warning(f"AI turn failed: {e}")

        # Update displays
        self._refresh_combat_displays()

    def on_heal_button_clicked(self):
        """Handle heal button click - delegate to combat controller."""
        if not hasattr(self, 'player') or not self.player:
            logger.warning("No player to heal")
            return

        # Delegate to combat controller
        heal_amount = random.randint(self.player.current_health, self.player.max_health)
        self.combat_controller.apply_healing(self.player, self.player, heal_amount)
        
        # Visual effects only
        self.create_particles(150, 200, "green", 15)

        # Update displays
        self._refresh_combat_displays()

    def on_fireball_button_clicked(self):
        """Handle fireball button click - delegate to combat controller."""
        if not SPELLS_AVAILABLE:
            self.log_message("Spell system not available!", "combat")
            return
        if not hasattr(self, 'player') or not self.player:
            self.log_message("No player character available!")
            return
        if not hasattr(self, 'enemy') or not self.enemy:
            self.log_message("No enemy to target!", "combat")
            return

        # Track combo sequence first
        self.track_spell_cast("fireball")
        
        # Delegate to combat controller with proper spell name
        try:
            result = self.combat_controller.cast_spell_at_target(
                self.player, self.enemy, "fireball"
            )
            
            if result['success']:
                # Visual effects only
                self.create_particles(450, 200, "orange", 25)
                
                # Handle enemy defeat and loot
                if result['defeated']:
                    if result['loot']:
                        loot_names = [item.name for item in result['loot']]
                        loot_msg = f"Loot obtained: {', '.join(loot_names)}"
                        self.log_message(loot_msg, "info")
                    self.enemy = None
            else:
                self.log_message("Fireball spell failed!", "combat")
                
        except Exception as e:
            logger.error(f"Error casting fireball: {e}")
            self.log_message(f"Fireball spell error: {e}", "combat")

        # Update displays
        self._refresh_combat_displays()

    def on_ice_shard_button_clicked(self):
        """Handle ice shard button click - delegate to combat controller."""
        if not SPELLS_AVAILABLE:
            self.log_message("Spell system not available!", "combat")
            return
        if not hasattr(self, 'player') or not self.player:
            self.log_message("No player character available!")
            return
        if not hasattr(self, 'enemy') or not self.enemy:
            self.log_message("No enemy to target!", "combat")
            return

        # Track combo sequence first
        self.track_spell_cast("ice_shard")
        
        # Delegate to combat controller with proper spell name
        try:
            result = self.combat_controller.cast_spell_at_target(
                self.player, self.enemy, "ice_shard"
            )
            
            if result['success']:
                # Visual effects only
                self.create_particles(450, 200, "cyan", 20)
                
                # Handle enemy defeat and loot
                if result['defeated']:
                    if result['loot']:
                        loot_names = [getattr(item, 'name', str(item)) for item in result['loot']]
                        self.log_message(f"Loot found: {', '.join(loot_names)}", "loot")
                    self.enemy = None
            else:
                self.log_message("Ice shard spell failed!", "combat")
                
        except Exception as e:
            logger.error(f"Error casting ice shard: {e}")
            self.log_message(f"Ice shard spell error: {e}", "combat")

        # Update displays
        self._refresh_combat_displays()

    def on_level_up_button_clicked(self):
        """Handle level up button click - delegate to character controller."""
        if not hasattr(self, 'player') or not self.player:
            self.log_message("No player character available!")
            return

        # Delegate to character controller
        self.character_controller.level_up_character(self.player)

        # Force stat recalculation and full restore
        if hasattr(self.player, 'update_stats'):
            self.player.update_stats()
        if hasattr(self.player, 'max_health'):
            self.player.current_health = self.player.max_health
        if hasattr(self.player, 'max_mana'):
            self.player.current_mana = self.player.max_mana
        if hasattr(self.player, 'max_stamina'):
            self.player.current_stamina = self.player.max_stamina

        # Update displays
        self._refresh_character_displays()

    def on_spawn_enemy_button_clicked(self):
        """Handle spawn enemy button click."""
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
            
            # Display enemy info
            enemy_info = (f"A {self.enemy.name} appears! "
                         f"(Level {self.enemy.level}, "
                         f"Grade {self.enemy.grade}, "
                         f"Rarity {self.enemy.rarity})")
            self.log_message(enemy_info, "combat")

            # Visual effect
            self.create_particles(450, 200, "purple", 20)
            
            # Update displays
            self._refresh_combat_displays()

    def on_use_item_button_clicked(self):
        """Handle use item button click - delegate to inventory controller."""
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
                
                # Delegate to inventory controller
                success = self.inventory_controller.use_item(self.player, item)
                
                if success:
                    # Update displays after successful use
                    self._refresh_inventory_displays()
                    
        except Exception as e:
            self.log_message(f"Error using item: {e}", "combat")

    def on_allocate_stat_button_clicked(self, stat_name: str):
        """Handle stat allocation button click - delegate to character controller."""
        if not hasattr(self, 'player') or not self.player:
            self.log_message("No player character available!", "combat")
            return

        # Delegate to character controller
        success = self.character_controller.allocate_stat_point(self.player, stat_name)
        
        if success:
            # Update displays
            self._refresh_character_displays()

    # ============================================================================
    # DISPLAY REFRESH HELPERS - Task #3 Implementation
    # ============================================================================

    def _refresh_combat_displays(self):
        """Refresh all combat-related displays."""
        self.update_combat_related_displays()

    def _refresh_character_displays(self):
        """Refresh all character-related displays."""
        self.update_character_related_displays()

    def _refresh_inventory_displays(self):
        """Refresh all inventory-related displays."""
        self.update_inventory_related_displays()

    # ============================================================================
    # UI SETUP CONSOLIDATION - Task #3 Phase 2
    # ============================================================================

    def setup_all_tabs(self):
        """Fallback tab setup method - delegates to UI service if not already handled."""
        # This is a fallback - UI service should have already handled tab setup
        self.log_message("Warning: Using fallback tab setup instead of UI service", "info")
        
        # Only set up the tabs that are not handled by UI service
        try:
            # These are handled locally since they have complex widget references
            self.setup_stats_tab()
            self.setup_combat_tab()
            
            # Log that other tabs should be handled by UI service
            self.log_message("Other tabs should be handled by UI service", "info")
        except Exception as e:
            self.log_message(f"Fallback tab setup failed: {e}", "combat")

    # ============================================================================
    # DISPLAY MANAGER PATTERN - Task #3 Phase 3
    # ============================================================================

    def update_all_displays(self):
        """Master display update method - updates all relevant displays."""
        self.update_char_info()
        self.update_enemy_info()
        self.update_inventory_display()
        self.update_equipment_display()
        self.update_progression_display()
        self.update_leveling_display()
        self.draw_game_state()

    def update_character_related_displays(self):
        """Update displays related to character changes."""
        self.update_char_info()
        self.update_progression_display()
        self.update_leveling_display()

    def update_combat_related_displays(self):
        """Update displays related to combat changes."""
        self.update_char_info()
        self.update_enemy_info()
        self.draw_game_state()

    def update_inventory_related_displays(self):
        """Update displays related to inventory changes."""
        self.update_inventory_display()
        self.update_equipment_display()
        self.update_char_info()

    # ============================================================================
    # LEGACY METHODS - To be replaced with event handlers
    # ============================================================================

    def attack(self):
        """Legacy method - use on_attack_button_clicked() instead."""
        return self.on_attack_button_clicked()

    def heal(self):
        """Legacy method - use on_heal_button_clicked() instead."""
        return self.on_heal_button_clicked()

    def cast_fireball(self):
        """Legacy method - use on_fireball_button_clicked() instead."""
        return self.on_fireball_button_clicked()

    def cast_ice_shard(self):
        """Legacy method - use on_ice_shard_button_clicked() instead."""
        return self.on_ice_shard_button_clicked()

    def level_up(self):
        """Legacy method - use on_level_up_button_clicked() instead."""
        return self.on_level_up_button_clicked()

    def use_selected_item(self):
        """Legacy method - use on_use_item_button_clicked() instead."""
        return self.on_use_item_button_clicked()

    def spawn_enemy(self):
        """Legacy method - use on_spawn_enemy_button_clicked() instead."""
        return self.on_spawn_enemy_button_clicked()

    # ============================================================================
    # END LEGACY METHODS
    # ============================================================================

    def test_dual_wield(self):
        """Test comprehensive dual wielding functionality with enhanced system."""
        if not hasattr(self, 'player') or not self.player:
            self.log_message("No player available for dual wield test!", "combat")
            return

        try:
            from game_sys.items.factory import ItemFactory
            
            self.log_message("=== Enhanced Dual Wield System Test ===", "info")
            
            # Show current equipment status
            current_status = equipment_manager.get_dual_wield_status_info(self.player)
            self.log_message(f"Current Status: {current_status}", "info")
            
            # Test 1: Create and demonstrate dual-wieldable weapons
            self.log_message("\n--- Test 1: Dual-Wieldable Weapons ---", "info")
            main_dagger = ItemFactory.create('iron_dagger')
            offhand_dagger = ItemFactory.create('dagger')
            dragon_tooth_dagger = ItemFactory.create('dragon_tooth_dagger')
            
            if main_dagger:
                self.log_message(f"Created: {main_dagger.name} (dual_wield: {getattr(main_dagger, 'dual_wield', False)})", "info")
                # Add to inventory and try to equip
                self.player.inventory.add_item(main_dagger)
                
            if offhand_dagger:
                self.log_message(f"Created: {offhand_dagger.name} (dual_wield: {getattr(offhand_dagger, 'dual_wield', False)})", "info")
                self.player.inventory.add_item(offhand_dagger)
                
            # Test 2: Two-handed weapons
            self.log_message("\n--- Test 2: Two-Handed Weapons ---", "info")
            fire_staff = ItemFactory.create('fire_staff')
            arcane_staff = ItemFactory.create('arcane_staff')
            
            if fire_staff:
                self.log_message(f"Created: {fire_staff.name} (two_handed: {getattr(fire_staff, 'two_handed', False)})", "info")
                self.player.inventory.add_item(fire_staff)
                
            # Test 3: Shield/Focus items  
            self.log_message("\n--- Test 3: Shields and Focuses ---", "info")
            wooden_shield = ItemFactory.create('wooden_shield')
            spell_focus = ItemFactory.create('spell_focus')
            arcane_focus = ItemFactory.create('arcane_focus')
            
            for item in [wooden_shield, spell_focus, arcane_focus]:
                if item:
                    restriction = getattr(item, 'slot_restriction', 'none')
                    dual_wield = getattr(item, 'dual_wield', False)
                    self.log_message(f"Created: {item.name} (restriction: {restriction}, dual_wield: {dual_wield})", "info")
                    self.player.inventory.add_item(item)
            
            # Update displays to show new inventory
            self.update_inventory_display()
            self.update_equipment_display()
            
            self.log_message("\n=== Dual Wield Test Complete ===", "info")
            self.log_message("Try equipping different combinations in the Inventory tab to see the enhanced logic!", "info")
            self.log_message("- Iron Dagger + Dagger = Dual wielding", "info")
            self.log_message("- Fire Staff = Two-handed (clears both slots)", "info")
            self.log_message("- Wooden Shield = Offhand-only item", "info")
            self.log_message("- Enhanced error messages will guide you!", "info")
                
        except Exception as e:
            self.log_message(f"Dual wield test error: {e}", "combat")
            logger.error(f"Dual wield test error: {e}")
        
        # Update displays
        self.update_char_info()
        self.draw_game_state()

    def test_equipment_quick(self):
        """Quick test to create and equip some basic items."""
        if not hasattr(self, 'player') or not self.player:
            self.log_message("No player available for equipment test!", "combat")
            return

        try:
            from game_sys.items.factory import ItemFactory
            
            self.log_message("=== Quick Equipment Test ===", "info")
            
            # Test simple armor equipping
            leather_armor = ItemFactory.create('leather_armor')
            if leather_armor:
                self.log_message(f"Created {leather_armor.name}, slot: {getattr(leather_armor, 'slot', 'NONE')}", "info")
                self.player.inventory.add_item(leather_armor)
                
            # Test weapon equipping
            iron_sword = ItemFactory.create('iron_sword')
            if iron_sword:
                self.log_message(f"Created {iron_sword.name}, slot: {getattr(iron_sword, 'slot', 'NONE')}", "info")
                self.player.inventory.add_item(iron_sword)
                
            # Update displays
            self.update_inventory_display()
            self.log_message("Items added to inventory. Try equipping them in the Inventory tab!", "info")
                
        except Exception as e:
            self.log_message(f"Quick equipment test error: {e}", "combat")
        
        self.update_char_info()

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
            ("Use Item", self.on_use_item_button_clicked),
            ("Equip Item", self.equip_selected_item),
            ("Drop Item", self.drop_selected_item),
            ("", None),  # Spacer
            ("Create Item", self.create_item_dialog),
            ("Add Random Item", self.add_random_item),
            ("", None),  # Spacer
            ("Unequip Weapon", lambda: self.unequip_item("weapon")),
            ("Unequip Armor", lambda: self.unequip_item("body")),
            ("Unequip Offhand", lambda: self.unequip_item("offhand")),
            ("Unequip Ring", lambda: self.unequip_item("ring")),
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
            self.player.inventory.add_item(item, auto_equip=False)
            display_name = getattr(item, 'display_name', None) or getattr(item, 'name', None) or getattr(item, 'id', str(item))
            msg = f"Created and added {display_name} (UUID: {item.uuid}) to inventory!"
            self.log_message(msg, "info")

            # Update inventory display
            self.update_inventory_related_displays()
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
        """Use the selected inventory item via inventory controller."""
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
                
                # Use inventory controller to handle item usage
                success = self.inventory_controller.use_item(self.player, item)
                
                if success:
                    # Update displays after successful use
                    self.update_inventory_display()
                    self.update_char_info()
                    
        except Exception as e:
            self.log_message(f"Error using item: {e}", "combat")

    def equip_selected_item(self):
        """Equip the selected item using the enhanced equipment manager."""
        
        if not ITEMS_AVAILABLE:
            self.log_message("Items system not available!", "combat")
            return

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
            
            # Use the enhanced equipment manager for all equipment logic
            success, message = equipment_manager.equip_item_with_smart_logic(self.player, item)
            
            if success:
                self.log_message(message, "info")
                
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
                
                # Update all relevant displays
                self.update_inventory_display()
                self.update_equipment_display()
                self.update_char_info()
            else:
                self.log_message(message, "combat")
                
        except Exception as e:
            self.log_message(f"Error equipping item: {e}", "combat")
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
        """Update the inventory display - delegates to UI service only."""
        if hasattr(self, 'ui_service') and self.ui_service:
            return self.ui_service.update_inventory_display({'player': self.player})
        else:
            self.log_message("UI service not available for inventory display", "info")

    def update_equipment_display(self):
        """Update the equipment display - delegates to UI service only."""
        if hasattr(self, 'ui_service') and self.ui_service:
            return self.ui_service.update_equipment_display({'player': self.player})
        else:
            self.log_message("UI service not available for equipment display", "info")

    def _update_equipment_slot_display(self):
        """Update the visual equipment slot displays."""
        try:
            slots_data = [
                ("equipped_helmet", "helmet"),
                ("equipped_cloak", "cloak"), 
                ("equipped_body", "body"),
                ("weapon", "weapon"),
                ("offhand", "offhand"),
                ("equipped_feet", "feet"),
                ("equipped_ring", "ring")
            ]
            
            for attr_name, slot_type in slots_data:
                label_attr = f"slot_{attr_name}_label"
                if hasattr(self, label_attr):
                    label = getattr(self, label_attr)
                    item = getattr(self.player, attr_name, None)
                    
                    if item:
                        # Show item name with truncation if needed
                        item_name = item.name
                        if len(item_name) > 15:
                            item_name = item_name[:12] + "..."
                        label.config(text=item_name, fg="lightgreen")
                    else:
                        label.config(text="(Empty)", fg="gray")
                        
        except Exception as e:
            logger.debug(f"Error updating equipment slot display: {e}")

    def _check_equipment_slot_availability(self, item, slot):
        """
        Enhanced equipment slot checking with comprehensive dual-wield logic.
        
        Returns:
            tuple: (slot_available: bool, conflict_message: str or None)
        """
        current_weapon = getattr(self.player, 'weapon', None)
        current_offhand = getattr(self.player, 'offhand', None)
        item_name = getattr(item, 'name', str(item))
        
        if slot == 'weapon':
            return self._check_weapon_slot_availability(item, item_name, current_weapon, current_offhand)
        elif slot == 'offhand':
            return self._check_offhand_slot_availability(item, item_name, current_weapon, current_offhand)
        elif slot == 'two_handed':
            return self._check_two_handed_slot_availability(item, item_name, current_weapon, current_offhand)
        else:
            # Regular armor/accessory slots
            slot_attr = f'equipped_{slot}' if slot != 'ring' else 'ring'
            current_item = getattr(self.player, slot_attr, None)
            if current_item is None:
                return True, None
            else:
                current_name = getattr(current_item, 'name', str(current_item))
                return False, f"{slot.title()} slot occupied by {current_name}"

    def _check_weapon_slot_availability(self, item, item_name, current_weapon, current_offhand):
        """Check weapon slot availability with dual-wield logic."""
        is_item_dual = getattr(item, 'dual_wield', False)
        is_item_two_handed = getattr(item, 'two_handed', False)
        
        # Two-handed weapons need both slots free
        if is_item_two_handed:
            if current_weapon is None and current_offhand is None:
                return True, None
            else:
                conflicts = []
                if current_weapon: 
                    conflicts.append(f"weapon ({current_weapon.name})")
                if current_offhand: 
                    conflicts.append(f"offhand ({current_offhand.name})")
                return False, f"Two-handed weapon requires both hands free. Currently occupied: {', '.join(conflicts)}"
        
        # No weapon equipped - always available
        if current_weapon is None:
            return True, None
        
        # Weapon slot occupied - analyze dual-wield possibilities
        current_weapon_dual = getattr(current_weapon, 'dual_wield', False)
        current_weapon_two_handed = getattr(current_weapon, 'two_handed', False)
        current_weapon_name = getattr(current_weapon, 'name', str(current_weapon))
        
        # Current weapon is two-handed - cannot dual-wield
        if current_weapon_two_handed:
            return False, f"Cannot equip {item_name}: {current_weapon_name} is two-handed and cannot be dual-wielded"
        
        # Both weapons can dual-wield and offhand is free
        if is_item_dual and current_weapon_dual and current_offhand is None:
            self.log_message(f"Auto-moving {current_weapon_name} to offhand for dual-wielding with {item_name}", "info")
            return True, None
        
        # Generate appropriate conflict messages
        if is_item_dual:
            if not current_weapon_dual:
                return False, f"Cannot dual-wield: {current_weapon_name} is not dual-wieldable"
            elif current_offhand is not None:
                offhand_name = getattr(current_offhand, 'name', str(current_offhand))
                return False, f"Cannot dual-wield: offhand occupied by {offhand_name}. Unequip first."
            else:
                return False, f"Weapon slot occupied by {current_weapon_name}"
        else:
            return False, f"Weapon slot occupied by {current_weapon_name}. Unequip first."

    def _check_offhand_slot_availability(self, item, item_name, current_weapon, current_offhand):
        """Check offhand slot availability with dual-wield logic."""
        is_item_dual = getattr(item, 'dual_wield', False)
        slot_restriction = getattr(item, 'slot_restriction', None)
        
        # Offhand slot occupied
        if current_offhand is not None:
            offhand_name = getattr(current_offhand, 'name', str(current_offhand))
            return False, f"Offhand slot occupied by {offhand_name}. Unequip first."
        
        # Check slot restrictions
        if slot_restriction == 'offhand_only':
            # Item can only go in offhand (shields, focuses, etc.)
            if current_weapon and getattr(current_weapon, 'two_handed', False):
                weapon_name = getattr(current_weapon, 'name', str(current_weapon))
                return False, f"Cannot equip {item_name}: {weapon_name} is two-handed and requires both hands"
            return True, None
        
        # Item can dual-wield
        if is_item_dual:
            if current_weapon is None:
                return True, None
            elif getattr(current_weapon, 'dual_wield', False):
                return True, None
            elif getattr(current_weapon, 'two_handed', False):
                weapon_name = getattr(current_weapon, 'name', str(current_weapon))
                return False, f"Cannot dual-wield: {weapon_name} is two-handed"
            else:
                weapon_name = getattr(current_weapon, 'name', str(current_weapon))
                return False, f"Cannot dual-wield: {weapon_name} is not dual-wieldable"
        
        # Regular offhand item
        return True, None

    def _check_two_handed_slot_availability(self, item, item_name, current_weapon, current_offhand):
        """Check availability for two-handed weapons."""
        conflicts = []
        if current_weapon:
            weapon_name = getattr(current_weapon, 'name', str(current_weapon))
            conflicts.append(f"weapon ({weapon_name})")
        if current_offhand:
            offhand_name = getattr(current_offhand, 'name', str(current_offhand))
            conflicts.append(f"offhand ({offhand_name})")
        
        if conflicts:
            return False, f"Two-handed weapon requires both hands free. Currently occupied: {', '.join(conflicts)}"
        else:
            return True, None

    def _suggest_dual_wield_alternative(self, item, slot):
        """Suggest alternative actions for dual-wield scenarios."""
        current_weapon = getattr(self.player, 'weapon', None)
        current_offhand = getattr(self.player, 'offhand', None)
        is_item_dual = getattr(item, 'dual_wield', False)
        is_item_two_handed = getattr(item, 'two_handed', False)
        
        suggestions = []
        
        if is_item_two_handed:
            if current_weapon:
                suggestions.append("Unequip your main weapon")
            if current_offhand:
                suggestions.append("Unequip your offhand item")
            if suggestions:
                return f"Two-handed weapon needs both hands free. {' and '.join(suggestions)}."
        
        if slot == 'weapon' and is_item_dual and current_weapon:
            current_weapon_dual = getattr(current_weapon, 'dual_wield', False)
            current_weapon_two_handed = getattr(current_weapon, 'two_handed', False)
            
            if current_weapon_two_handed:
                return "Unequip your two-handed weapon first."
            elif current_weapon_dual and current_offhand is not None:
                offhand_name = getattr(current_offhand, 'name', 'offhand item')
                return f"Unequip {offhand_name} first to make room for dual-wielding."
            elif not current_weapon_dual:
                weapon_name = getattr(current_weapon, 'name', 'main weapon')
                return f"Unequip {weapon_name} first (not dual-wieldable)."
        
        elif slot == 'offhand':
            if is_item_dual and current_weapon:
                current_weapon_dual = getattr(current_weapon, 'dual_wield', False)
                current_weapon_two_handed = getattr(current_weapon, 'two_handed', False)
                
                if current_weapon_two_handed:
                    weapon_name = getattr(current_weapon, 'name', 'weapon')
                    return f"Unequip {weapon_name} first (two-handed weapons use both hands)."
                elif not current_weapon_dual:
                    weapon_name = getattr(current_weapon, 'name', 'main weapon')
                    return f"Equip a dual-wieldable weapon first (current: {weapon_name})."
                    
            if current_offhand:
                offhand_name = getattr(current_offhand, 'name', 'offhand item')
                return f"Unequip {offhand_name} first."
        
        return "Try unequipping conflicting items first."

    def _get_dual_wield_status_info(self):
        """Get current dual-wield status for display."""
        current_weapon = getattr(self.player, 'weapon', None)
        current_offhand = getattr(self.player, 'offhand', None)
        
        if not current_weapon and not current_offhand:
            return "Empty hands - ready for any weapon"
        
        weapon_name = getattr(current_weapon, 'name', 'Unknown') if current_weapon else None
        offhand_name = getattr(current_offhand, 'name', 'Unknown') if current_offhand else None
        
        status_parts = []
        
        if current_weapon:
            weapon_two_handed = getattr(current_weapon, 'two_handed', False)
            weapon_dual = getattr(current_weapon, 'dual_wield', False)
            
            if weapon_two_handed:
                status_parts.append(f"Two-handed: {weapon_name}")
            elif weapon_dual:
                status_parts.append(f"Dual-wieldable: {weapon_name}")
            else:
                status_parts.append(f"Single weapon: {weapon_name}")
        
        if current_offhand:
            offhand_dual = getattr(current_offhand, 'dual_wield', False)
            slot_restriction = getattr(current_offhand, 'slot_restriction', None)
            
            if offhand_dual:
                status_parts.append(f"Dual-wielding: {offhand_name}")
            elif slot_restriction == 'offhand_only':
                status_parts.append(f"Shield/Focus: {offhand_name}")
            else:
                status_parts.append(f"Offhand: {offhand_name}")
        
        return " | ".join(status_parts)

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

    def _detailed_character_view_placeholder(self):
        """Placeholder method for detailed character view."""
        self.log_message("Detailed character view - Feature coming soon!", "info")

    def _inspect_equipment_placeholder(self):
        """Show detailed equipment information."""
        if not hasattr(self, 'player') or not self.player:
            self.log_message("No player character available!", "info")
            return
            
        # Switch to inventory tab where equipment can be viewed
        if hasattr(self, 'tab_control') and hasattr(self, 'inventory_tab'):
            self.tab_control.select(self.inventory_tab)
            self.log_message("Switched to Inventory tab to view equipment details", "info")
        else:
            # Show equipment summary in log
            weapon = getattr(self.player, 'weapon', None)
            offhand = getattr(self.player, 'offhand', None)  
            body_armor = getattr(self.player, 'equipped_body', None)
            
            equipment_info = "=== EQUIPMENT INSPECTION ===\n"
            if weapon:
                equipment_info += f"⚔️ Weapon: {weapon.name}\n"
                if hasattr(weapon, 'base_damage'):
                    equipment_info += f"   Damage: {weapon.base_damage}\n"
            else:
                equipment_info += "⚔️ Weapon: (None)\n"
                
            if offhand:
                equipment_info += f"🛡️ Offhand: {offhand.name}\n"
                if hasattr(offhand, 'defense'):
                    equipment_info += f"   Defense: {offhand.defense}\n"
                elif hasattr(offhand, 'base_damage'):
                    equipment_info += f"   Damage: {offhand.base_damage}\n"
            else:
                equipment_info += "🛡️ Offhand: (None)\n"
                
            if body_armor:
                equipment_info += f"🛡️ Armor: {body_armor.name}\n"
                if hasattr(body_armor, 'defense'):
                    equipment_info += f"   Defense: {body_armor.defense}\n"
            else:
                equipment_info += "🛡️ Armor: (None)\n"
                
            self.log_message(equipment_info, "info")

    def _optimize_defense_placeholder(self):
        """Placeholder method for defense optimization.""" 
        self.log_message("Defense optimization - Feature coming soon!", "info")

    def _equip_selected_item(self):
        """Wrapper for equipping selected item."""
        return self.equip_selected_item()

    def _drop_selected_item(self):
        """Wrapper for dropping selected item."""
        return self.drop_selected_item()

    def _create_item_placeholder(self):
        """Placeholder for create item functionality."""
        self.create_item_dialog()

    def _add_random_item_placeholder(self):
        """Placeholder for add random item functionality."""
        self.add_random_item()

    def _allocate_stat_point_placeholder(self):
        """Placeholder for stat point allocation."""
        self.log_message("Stat allocation - Use the leveling tab instead", "info")

    def _reset_all_stats_placeholder(self):
        """Placeholder for resetting stats."""
        self.log_message("Reset stats - Feature coming soon!", "info")

    def _save_character_build_placeholder(self):
        """Placeholder for saving character build."""
        self.log_message("Save character build - Feature coming soon!", "info")

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
            
            # 🎯 OBSERVER PATTERN ENHANCEMENT (Task #5):
            # Use event-driven UI updates instead of manual updates
            if OBSERVER_PATTERN_AVAILABLE and GameEventPublisher:
                # Publish skill learned event - UI observer handles the rest automatically
                GameEventPublisher.publish_skill_learned(skill_id, source=self)
            else:
                # Fallback to manual UI updates for compatibility
                requirements_text = ", ".join([f"{k}: {v}" for k, v in skill_requirements[skill_id].items()])
                self.log_message(f"Learned skill: {skill_id}! (Required: {requirements_text})", "info")
                # Update progression display
                self.update_progression_display()

        except Exception as e:
            # 🎯 OBSERVER PATTERN ENHANCEMENT: Event-driven error handling
            if OBSERVER_PATTERN_AVAILABLE and GameEventPublisher:
                GameEventPublisher.publish_error(f"Error learning skill: {e}", source=self)
            else:
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
            
            # 🎯 OBSERVER PATTERN ENHANCEMENT (Task #5):
            # Use event-driven UI updates instead of manual updates
            if OBSERVER_PATTERN_AVAILABLE and GameEventPublisher:
                # Publish spell learned event - UI observer will automatically:
                # 1. Update progression display
                # 2. Log the learning message with proper formatting  
                # 3. Handle any errors gracefully
                GameEventPublisher.publish_spell_learned(spell_id, source=self)
            else:
                # Fallback to manual UI updates for compatibility
                requirements_text = ", ".join([f"{k}: {v}" for k, v in spell_requirements[spell_id].items()])
                self.log_message(f"Learned spell: {spell_id}! (Required: {requirements_text})", "info")
                # Update progression display
                self.update_progression_display()

        except Exception as e:
            # 🎯 OBSERVER PATTERN ENHANCEMENT: Event-driven error handling
            if OBSERVER_PATTERN_AVAILABLE and GameEventPublisher:
                GameEventPublisher.publish_error(f"Error learning spell: {e}", source=self)
            else:
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
            
            # 🎯 OBSERVER PATTERN ENHANCEMENT (Task #5):
            # Use event-driven UI updates instead of manual updates
            if OBSERVER_PATTERN_AVAILABLE and GameEventPublisher:
                # Publish enchantment learned event
                GameEventPublisher.publish_enchantment_learned(enchant_id, source=self)
            else:
                # Fallback to manual UI updates
                self.log_message(f"Learned enchantment: {enchant_id}!", "info")

        except Exception as e:
            # 🎯 OBSERVER PATTERN ENHANCEMENT: Event-driven error handling
            if OBSERVER_PATTERN_AVAILABLE and GameEventPublisher:
                GameEventPublisher.publish_error(f"Error learning enchantment: {e}", source=self)
            else:
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
                            item.stats['speed'] = item.stats.get('speed', 0) + 0.15
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
        """Update progression display - delegates to UI service only."""
        if hasattr(self, 'ui_service') and self.ui_service:
            return self.ui_service.update_progression_display({'player': self.player})
        else:
            self.log_message("UI service not available for progression display", "info")

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
            old_level = getattr(self.player, 'level', 1)
            old_xp = getattr(self.player, 'experience', 0)

            # Use leveling manager if available
            if hasattr(self.player, 'leveling_manager'):
                leveled_up = self.player.leveling_manager.gain_experience(
                    self.player,
                    xp_amount
                )

                # 🎯 OBSERVER PATTERN ENHANCEMENT (Task #5):
                # Publish XP and level change events
                if OBSERVER_PATTERN_AVAILABLE and GameEventPublisher:
                    # Publish XP change event
                    new_xp = getattr(self.player, 'experience', old_xp)
                    GameEventPublisher.publish_stat_change('experience', old_xp, new_xp, source=self)
                    
                    # If level up occurred, publish level up event
                    if leveled_up:
                        GameEventPublisher.publish_level_up(self.player.level, source=self)
                else:
                    # Fallback to manual logging
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

                self.player.experience += xp_amount
                
                # Simple level up check
                xp_needed = self.player.level * 100
                leveled_up = False
                if self.player.experience >= xp_needed:
                    self.player.level += 1
                    self.player.experience -= xp_needed
                    leveled_up = True

                # 🎯 OBSERVER PATTERN ENHANCEMENT: Publish events for manual XP gain too
                if OBSERVER_PATTERN_AVAILABLE and GameEventPublisher:
                    GameEventPublisher.publish_stat_change('experience', old_xp, self.player.experience, source=self)
                    if leveled_up:
                        GameEventPublisher.publish_level_up(self.player.level, source=self)
                else:
                    # Fallback to manual logging
                    if leveled_up:
                        msg = f"Gained {xp_amount} XP and leveled up! Level {self.player.level}"
                        self.log_message(msg, "info")
                    else:
                        msg = f"Gained {xp_amount} XP!"
                        self.log_message(msg, "info")

            # 🎯 OBSERVER PATTERN: Only manual display updates if observer not available
            if not OBSERVER_PATTERN_AVAILABLE:
                self.update_char_info()
                self.update_leveling_display()

        except Exception as e:
            # 🎯 OBSERVER PATTERN ENHANCEMENT: Event-driven error handling
            if OBSERVER_PATTERN_AVAILABLE and GameEventPublisher:
                GameEventPublisher.publish_error(f"Error gaining XP: {e}", source=self)
            else:
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
        """Update the leveling tab display - delegates to UI service."""
        # Always use UI service first since demo UI controls UI
        if hasattr(self, 'ui_service') and self.ui_service:
            result = self.ui_service.update_leveling_display({'player': self.player})
            if result.get('success', False):
                return

        # Minimal fallback implementation for backwards compatibility
        if not hasattr(self, 'player') or not self.player:
            return

        try:
            # Update available stat points display only
            if hasattr(self, 'available_points_label'):
                if hasattr(self.player, 'leveling_manager'):
                    available_points = self.player.leveling_manager.calculate_stat_points_available(self.player)
                    self.available_points_label.config(text=str(available_points))
                else:
                    self.available_points_label.config(text="0")
                    
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

        # Also use proper console logging for immediate visibility
        import traceback
        console_logger.error(f"ERROR: {e}")
        traceback.print_exc()
        raise

if __name__ == "__main__":
    main()