"""
Game Controller Interfaces

This module defines the interfaces and protocols for the game controller architecture.
It provides type-safe contracts for all controller classes and their interactions.
"""

from typing import Protocol, Dict, Any, Optional, List, Union
from abc import ABC, abstractmethod


class UIServiceProtocol(Protocol):
    """Protocol defining the interface for UI service classes."""
    
    def log_message(self, message: str, tag: str = "info") -> None:
        """Log a message to the UI display."""
        ...
    
    def update_character_display(self, character_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update character display with provided data."""
        ...
    
    def update_enemy_display(self, enemy_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update enemy display with provided data."""
        ...


class GameServiceProtocol(Protocol):
    """Protocol defining the interface for game service classes."""
    
    def attack(self, attacker: Any, target: Any, weapon: Optional[Any] = None) -> Dict[str, Any]:
        """Execute an attack action."""
        ...
    
    def heal(self, caster: Any, target: Any, amount: int) -> Dict[str, Any]:
        """Execute a healing action."""
        ...
    
    def cast_spell_at_target(self, caster: Any, spell_id: str, target: Any) -> Dict[str, Any]:
        """Cast a spell at a target."""
        ...


class GameControllerInterface(ABC):
    """Abstract base class defining the interface for game controllers."""
    
    def __init__(self, ui_service: Optional[UIServiceProtocol] = None) -> None:
        """Initialize controller with optional UI service."""
        self.ui_service = ui_service
        self.ui_callback: Optional[callable] = None
    
    def set_ui_callback(self, callback: callable) -> None:
        """Set UI callback for logging."""
        self.ui_callback = callback
    
    @abstractmethod
    def _log_message(self, message: str, tag: str = "info") -> None:
        """Log message using UI service or callback."""
        ...


class CombatControllerInterface(GameControllerInterface):
    """Interface for combat controller operations."""
    
    @abstractmethod
    def perform_attack(self, attacker: Any, target: Any, weapon: Optional[Any] = None) -> Dict[str, Any]:
        """Perform an attack action with UI integration."""
        ...
    
    @abstractmethod
    def apply_healing(self, caster: Any, target: Any, amount: int) -> Dict[str, Any]:
        """Apply healing with UI integration."""
        ...
    
    @abstractmethod
    def cast_spell_at_target(self, caster: Any, target: Any, spell_name: str, **kwargs) -> Dict[str, Any]:
        """Cast spell with UI integration."""
        ...


class CharacterControllerInterface(GameControllerInterface):
    """Interface for character controller operations."""
    
    @abstractmethod
    def level_up_character(self, character: Any) -> Dict[str, Any]:
        """Level up character with UI integration."""
        ...
    
    @abstractmethod
    def allocate_stat_point(self, character: Any, stat_name: str) -> bool:
        """Allocate stat point with validation and UI feedback."""
        ...


class InventoryControllerInterface(GameControllerInterface):
    """Interface for inventory controller operations."""
    
    @abstractmethod
    def use_item(self, character: Any, item: Any) -> bool:
        """Use item with validation and UI feedback."""
        ...
    
    @abstractmethod
    def equip_item(self, character: Any, item: Any) -> bool:
        """Equip item with validation and UI feedback."""
        ...


class ComboControllerInterface(GameControllerInterface):
    """Interface for combo controller operations."""
    
    @abstractmethod
    def record_spell_cast(self, caster: Any, spell_name: str) -> None:
        """Record spell cast for combo tracking."""
        ...
    
    @abstractmethod
    def check_combo_sequences(self, character: Any, sequence: List[str]) -> Optional[Dict[str, Any]]:
        """Check for combo sequences and apply effects."""
        ...


class DemoEventHandlerInterface(ABC):
    """Interface defining event handler methods for the demo."""
    
    @abstractmethod
    def on_attack_button_clicked(self) -> None:
        """Handle attack button click."""
        ...
    
    @abstractmethod
    def on_heal_button_clicked(self) -> None:
        """Handle heal button click."""
        ...
    
    @abstractmethod
    def on_fireball_button_clicked(self) -> None:
        """Handle fireball button click."""
        ...
    
    @abstractmethod
    def on_ice_shard_button_clicked(self) -> None:
        """Handle ice shard button click."""
        ...
    
    @abstractmethod
    def on_level_up_button_clicked(self) -> None:
        """Handle level up button click."""
        ...
    
    @abstractmethod
    def on_spawn_enemy_button_clicked(self) -> None:
        """Handle spawn enemy button click."""
        ...
    
    @abstractmethod
    def on_use_item_button_clicked(self) -> None:
        """Handle use item button click."""
        ...
    
    @abstractmethod
    def on_allocate_stat_button_clicked(self, stat_name: str) -> None:
        """Handle stat allocation button click."""
        ...


class DisplayManagerInterface(ABC):
    """Interface for display management operations."""
    
    @abstractmethod
    def update_all_displays(self) -> None:
        """Update all relevant displays."""
        ...
    
    @abstractmethod
    def update_character_related_displays(self) -> None:
        """Update displays related to character changes."""
        ...
    
    @abstractmethod
    def update_combat_related_displays(self) -> None:
        """Update displays related to combat changes."""
        ...
    
    @abstractmethod
    def update_inventory_related_displays(self) -> None:
        """Update displays related to inventory changes."""
        ...


class GameStateManagerInterface(ABC):
    """Interface for game state management."""
    
    @abstractmethod
    def setup_game_state(self) -> None:
        """Initialize the game state."""
        ...
    
    @abstractmethod
    def save_game(self) -> None:
        """Save the current game state."""
        ...
    
    @abstractmethod
    def load_game(self) -> None:
        """Load a saved game state."""
        ...
    
    @abstractmethod
    def reload_game(self) -> None:
        """Reload the game state."""
        ...


# Type aliases for better readability
ActionResult = Dict[str, Any]
CharacterData = Dict[str, Any]
ItemData = Dict[str, Any]
SpellResult = Dict[str, Any]
UICallback = callable
LoggingCallback = callable

# Result type definitions
class CombatResult:
    """Standardized combat result structure."""
    def __init__(self, success: bool, message: str = "", damage: float = 0.0, 
                 defeated: bool = False, loot: Optional[List[Any]] = None):
        self.success = success
        self.message = message
        self.damage = damage
        self.defeated = defeated
        self.loot = loot or []

class ValidationResult:
    """Standardized validation result structure."""
    def __init__(self, valid: bool, message: str = "", data: Optional[Any] = None):
        self.valid = valid
        self.message = message
        self.data = data
