#!/usr/bin/env python3
"""
Character Creation Service
=========================

Service for character creation business logic, extracted from newdemo.py
as part of the decoupling effort. This service coordinates the character
creation workflow using other specialized services.

This service handles:
- Character preview creation
- Stat allocation coordination
- Template selection
- Character finalization
- Integration with other services
"""


from __future__ import annotations
from typing import Dict, Any, Optional, List, Protocol, Union
from dataclasses import dataclass, asdict
from enum import Enum
import logging
from abc import ABC, abstractmethod

from game_sys.character.character_factory import create_character
from game_sys.character.character_service import create_character_with_random_stats
from game_sys.character.template_service import TemplateService
from game_sys.character.character_library_service import CharacterLibraryService
from game_sys.admin.admin_service import AdminService
from game_sys.character.stat_allocation_service import StatAllocationService
from game_sys.character.leveling_manager import LevelingManager
from game_sys.config.config_manager import ConfigManager
from game_sys.logging import get_logger


# ===== DATA CLASSES =====

@dataclass(frozen=True)
class CharacterCreationConfig:
    """Configuration for character creation service."""
    default_stat_points: int = 3
    max_stat_points: int = 999
    auto_save_to_library: bool = True
    enable_build_recommendations: bool = True


@dataclass
class CreationState:
    """Immutable state object for character creation."""
    current_character: Optional[Any] = None
    selected_template_id: Optional[str] = None
    available_stat_points: int = 3
    infinite_stat_points: bool = False
    
    def with_character(self, character: Any) -> CreationState:
        """Return new state with updated character."""
        return CreationState(
            current_character=character,
            selected_template_id=self.selected_template_id,
            available_stat_points=self.available_stat_points,
            infinite_stat_points=self.infinite_stat_points
        )
    
    def with_template(self, template_id: str) -> CreationState:
        """Return new state with updated template."""
        return CreationState(
            current_character=self.current_character,
            selected_template_id=template_id,
            available_stat_points=self.available_stat_points,
            infinite_stat_points=self.infinite_stat_points
        )
    
    def with_stat_points(self, points: int) -> CreationState:
        """Return new state with updated stat points."""
        return CreationState(
            current_character=self.current_character,
            selected_template_id=self.selected_template_id,
            available_stat_points=points,
            infinite_stat_points=self.infinite_stat_points
        )
    
    def with_infinite_points(self, infinite: bool) -> CreationState:
        """Return new state with updated infinite points setting."""
        return CreationState(
            current_character=self.current_character,
            selected_template_id=self.selected_template_id,
            available_stat_points=self.available_stat_points if not infinite else 999,
            infinite_stat_points=infinite
        )


@dataclass(frozen=True)
class ServiceResult:
    """Standard result object for service operations."""
    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    message: Optional[str] = None
    
    @classmethod
    def success_result(cls, data: Dict[str, Any] = None, message: str = None) -> ServiceResult:
        """Create a successful result."""
        return cls(success=True, data=data or {}, message=message)
    
    @classmethod
    def error_result(cls, error: str, message: str = None) -> ServiceResult:
        """Create an error result."""
        return cls(success=False, error=error, message=message or error)


# ===== PROTOCOLS AND INTERFACES =====

class CharacterCreationObserver(Protocol):
    """Protocol for observing character creation events."""
    
    def on_character_created(self, character: Any) -> None:
        """Called when a character is created."""
        ...
    
    def on_stats_allocated(self, character: Any, stat_name: str, amount: int) -> None:
        """Called when stats are allocated."""
        ...
    
    def on_character_finalized(self, character: Any) -> None:
        """Called when character creation is finalized."""
        ...
    
    def on_character_saved(self, character: Any, save_name: str) -> None:
        """Called when a character is saved to library."""
        ...
    
    def on_character_loaded(self, character: Any, save_name: str) -> None:
        """Called when a character is loaded from library."""
        ...
    
    def on_template_selected(self, template_id: str) -> None:
        """Called when a template is selected."""
        ...
    
    def on_character_reset(self) -> None:
        """Called when character stats are reset."""
        ...


class CharacterValidator(ABC):
    """Abstract base class for character validation."""
    
    @abstractmethod
    def validate_character(self, character: Any) -> ServiceResult:
        """Validate a character object."""
        pass
    
    @abstractmethod
    def validate_stat_allocation(self, character: Any, stat_name: str, amount: int) -> ServiceResult:
        """Validate stat allocation request."""
        pass


class DisplayFormatter(ABC):
    """Abstract base class for display formatting."""
    
    @abstractmethod
    def format_character_display(self, character: Any) -> str:
        """Format character for display."""
        pass
    
    @abstractmethod
    def format_template_display(self, template_data: Dict[str, Any]) -> str:
        """Format template information for display."""
        pass


# ===== CONCRETE IMPLEMENTATIONS =====

class DefaultCharacterValidator(CharacterValidator):
    """Default implementation of character validator."""
    
    def __init__(self, logger: logging.Logger):
        self.logger = logger
    
    def validate_character(self, character: Any) -> ServiceResult:
        """Validate a character object."""
        if not character:
            return ServiceResult.error_result("Character is None")
        
        if not hasattr(character, 'name') or not character.name:
            return ServiceResult.error_result("Character must have a name")
        
        required_stats = ['strength', 'dexterity', 'intelligence', 'constitution']
        for stat in required_stats:
            # Check if stat exists using multiple methods (same as stat allocation validation)
            stat_exists = False
            try:
                if hasattr(character, 'get_stat'):
                    # Try to get the stat using get_stat method
                    character.get_stat(stat)
                    stat_exists = True
                elif hasattr(character, 'base_stats') and stat in character.base_stats:
                    # Check if stat exists in base_stats dictionary
                    stat_exists = True
                elif hasattr(character, stat):
                    # Fallback to direct attribute check
                    stat_exists = True
            except (AttributeError, KeyError, ValueError):
                pass
            
            if not stat_exists:
                return ServiceResult.error_result(f"Character missing required stat: {stat}")
        
        return ServiceResult.success_result(message="Character validation passed")
    
    def validate_stat_allocation(self, character: Any, stat_name: str, amount: int) -> ServiceResult:
        """Validate stat allocation request."""
        if not character:
            return ServiceResult.error_result("No character selected")
        
        if amount <= 0:
            return ServiceResult.error_result("Stat allocation amount must be positive")
        
        # Check if stat exists - try multiple methods
        stat_exists = False
        try:
            if hasattr(character, 'get_stat'):
                # Try to get the stat using get_stat method
                character.get_stat(stat_name)
                stat_exists = True
            elif hasattr(character, 'base_stats') and stat_name in character.base_stats:
                # Check if stat exists in base_stats dictionary
                stat_exists = True
            elif hasattr(character, stat_name):
                # Fallback to direct attribute check
                stat_exists = True
        except (AttributeError, KeyError, ValueError):
            pass
        
        if not stat_exists:
            return ServiceResult.error_result(f"Invalid stat name: {stat_name}")
        
        return ServiceResult.success_result(message="Stat allocation validation passed")


class DefaultDisplayFormatter(DisplayFormatter):
    """Default implementation of display formatter."""
    
    def __init__(self, logger: logging.Logger):
        self.logger = logger
        self._stat_emojis = {
            'strength': '💪', 'dexterity': '🏃', 'vitality': '❤️',
            'intelligence': '🧠', 'wisdom': '🔮', 'constitution': '🛡️',
            'luck': '🍀', 'agility': '⚡', 'charisma': '✨'
        }
    
    def format_character_display(self, character: Any) -> str:
        """Format character for display."""
        if not character:
            return "No character selected"
        
        lines = []
        
        # Header
        lines.append(f"Character: {character.name}")
        lines.append("─" * 50)
        
        # Basic info
        lines.append(f"Level: {getattr(character, 'level', 1)}")
        lines.append(f"Grade: {getattr(character, 'grade_name', 'UNKNOWN')}")
        lines.append(f"Rarity: {getattr(character, 'rarity', 'COMMON')}")
        lines.append("")
        
        # Primary stats
        lines.append("📊 Primary Stats:")
        primary_stats = ['strength', 'dexterity', 'vitality', 'intelligence',
                        'wisdom', 'constitution', 'luck', 'agility', 'charisma']
        
        for stat in primary_stats:
            value = self._safe_get_stat(character, stat, 0)
            emoji = self._stat_emojis.get(stat, '📊')
            lines.append(f"   {emoji} {stat.capitalize():<12}: {value:.2f}")
        lines.append("")
        
        # Combat stats
        lines.append("⚡ Combat Stats:")
        
        # Health (show as fully maxed for template display)
        max_health = self._safe_get_stat(character, 'max_health', 0)
        lines.append(f"   Health: {max_health:.2f}/{max_health:.2f}")
        
        # Mana (show as fully maxed for template display)  
        max_mana = self._safe_get_stat(character, 'max_mana', 0)
        lines.append(f"   Mana: {max_mana:.2f}/{max_mana:.2f}")
        
        # Other combat stats
        attack = self._safe_get_stat(character, 'attack', 0)
        defense = self._safe_get_stat(character, 'defense', 0)
        lines.append(f"   Attack: {attack:.2f}")
        lines.append(f"   Defense: {defense:.2f}")
        
        return "\n".join(lines)
    
    def format_template_display(self, template_data: Dict[str, Any]) -> str:
        """Format template information for display."""
        lines = []
        
        # Header
        template_name = template_data.get('display_name', template_data.get('name', 'Unknown'))
        lines.append(f"{template_name}")
        lines.append("─" * (len(template_name) + 4))
        
        # Basic info
        template_type = template_data.get('type', 'Unknown')
        job_id = template_data.get('job_id', 'None')
        lines.append(f"Class Type: {template_type}")
        lines.append(f"Job Role: {job_id}")
        lines.append("")
        
        # Description
        if 'description' in template_data:
            lines.append("📖 Description:")
            lines.append(f"   {template_data['description']}")
            lines.append("")
        
        # Base stats
        if 'base_stats' in template_data:
            stats = template_data['base_stats']
            lines.append("📊 Base Statistics:")
            
            for stat_name, value in stats.items():
                emoji = self._stat_emojis.get(stat_name, '📊')
                lines.append(f"   {emoji} {stat_name.capitalize():<12}: {value}")
            lines.append("")
        
        # Starting equipment
        if 'starting_items' in template_data and template_data['starting_items']:
            lines.append("🎒 Starting Equipment:")
            for item in template_data['starting_items']:
                lines.append(f"   • {item}")
            lines.append("")
        
        return "\n".join(lines)
    
    def _safe_get_stat(self, character: Any, stat_name: str, default_value: float = 0.0) -> float:
        """Safely get a character stat."""
        try:
            if hasattr(character, 'get_stat'):
                return float(character.get_stat(stat_name))
            return float(getattr(character, stat_name, default_value))
        except (AttributeError, ValueError, TypeError):
            return default_value


# ===== MAIN SERVICE CLASS =====

class CharacterCreationService:
    """
    Refactored character creation service following clean architecture principles.
    
    This service coordinates character creation workflow while maintaining clear
    separation of concerns and improved maintainability.
    """
    
    def __init__(self, 
                 config: Optional[CharacterCreationConfig] = None,
                 validator: Optional[CharacterValidator] = None,
                 formatter: Optional[DisplayFormatter] = None,
                 observers: Optional[List[CharacterCreationObserver]] = None):
        """
        Initialize character creation service with dependency injection.
        
        Args:
            config: Service configuration
            validator: Character validator implementation
            formatter: Display formatter implementation
            observers: List of observers for service events
        """
        self.logger = get_logger(__name__)
        self.config = config or CharacterCreationConfig()
        
        # Injected dependencies
        self.validator = validator or DefaultCharacterValidator(self.logger)
        self.formatter = formatter or DefaultDisplayFormatter(self.logger)
        self.observers = observers or []
        
        # Core services
        self._config_manager = ConfigManager()
        self._template_service = TemplateService()
        self._library_service = CharacterLibraryService()
        self._admin_service = AdminService()
        self._stat_service = StatAllocationService(self._admin_service)
        self._leveling_manager = LevelingManager()
        
        # Service state
        self._state = CreationState(
            available_stat_points=self.config.default_stat_points
        )
        
        # Set up event handlers
        self._setup_event_handlers()
        
        self.logger.info("CharacterCreationService initialized with dependency injection")
    
    def _setup_event_handlers(self) -> None:
        """Set up event handlers for game events."""
        from game_sys.hooks.hooks_setup import on, ON_LEVEL_UP
        on(ON_LEVEL_UP, self._on_stat_points_updated)
    
    def _on_stat_points_updated(self, actor, new_level=None, **kwargs) -> None:
        """Handle stat points update events."""
        try:
            # Check if this is the current character
            if actor and actor == self._state.current_character:
                # Recalculate available stat points
                new_stat_points = self._leveling_manager.calculate_stat_points_available(actor)
                self._state = self._state.with_stat_points(new_stat_points)
                self.logger.info(f"Updated stat points to {new_stat_points} for character level {actor.level}")
        except Exception as e:
            self.logger.error(f"Error handling stat points update: {e}")

    # ===== PUBLIC API =====
    
    @property
    def current_character(self) -> Optional[Any]:
        """Get the current character."""
        return self._state.current_character
    
    @property
    def selected_template_id(self) -> Optional[str]:
        """Get the selected template ID."""
        return self._state.selected_template_id
    
    @property
    def available_stat_points(self) -> int:
        """Get available stat points."""
        return self._state.available_stat_points
    
    def add_observer(self, observer: CharacterCreationObserver) -> None:
        """Add an observer for service events."""
        if observer not in self.observers:
            self.observers.append(observer)
    
    def remove_observer(self, observer: CharacterCreationObserver) -> None:
        """Remove an observer."""
        if observer in self.observers:
            self.observers.remove(observer)
    
    # Remove duplicate method - use legacy version below
    
    def select_template(self, template_id: str) -> dict:
        """
        Select a character template for creation.
        
        Args:
            template_id: ID of the template to select
            
        Returns:
            Dictionary with selection results
        """
        try:
            result = self._template_service.select_template(template_id)
            if result['success']:
                self._state = self._state.with_template(template_id)
                # Set stat points from template or config
                stat_points = self._get_default_stat_points(template_id)
                self._state = self._state.with_stat_points(stat_points)
                
                # Notify observers
                self._notify_template_selected(template_id)
                
                return {
                    'success': True,
                    'template': result['template_data'],  # Add template key for UI compatibility
                    'template_data': result['template_data'],
                    'message': f"Template '{template_id}' selected successfully"
                }
            else:
                return {
                    'success': False,
                    'error': result.get('error', 'Unknown error'),
                    'message': result.get('message', 'Failed to select template')
                }
        except Exception as e:
            self.logger.error(f"Failed to select template {template_id}: {e}")
            return {
                'success': False,
                'error': str(e),
                'message': 'Failed to select template'
            }
    
    def create_character_preview(self, template_id: str, custom_stats: Optional[Dict[str, int]] = None) -> Dict[str, Any]:
        """
        Create a new character preview with validation.
        
        Args:
            template_id: ID of the template to use
            custom_stats: Optional custom stat allocations
            
        Returns:
            Dictionary with character preview results
        """
        try:
            # Validate template selection
            if not self._template_service.get_template(template_id):
                return {
                    'success': False,
                    'error': f"Template '{template_id}' not found",
                    'message': "Invalid template selected"
                }
            
            # Create character with random stats for variety
            overrides = custom_stats or {}
            character = create_character_with_random_stats(template_id, **overrides)
            
            # Check if character creation succeeded
            if not character:
                return {
                    'success': False,
                    'error': 'Character creation failed',
                    'message': 'Failed to create character from template'
                }
            
            # Validate created character
            validation_result = self.validator.validate_character(character)
            if not validation_result.success:
                return {
                    'success': False,
                    'error': validation_result.error,
                    'message': validation_result.message
                }
            
            # Update state with stat points from template/config
            stat_points = self._get_default_stat_points(template_id)
            self._state = (self._state
                         .with_character(character)
                         .with_template(template_id)
                         .with_stat_points(stat_points))
            
            # Notify observers
            self._notify_character_created(character)
            
            grade_name = getattr(character, 'grade', 'UNKNOWN')
            self.logger.info(f"Created character preview: {character.name} (Grade: {grade_name})")
            
            return {
                'success': True,
                'character': character,
                'stats': self._extract_character_stats(character),
                'message': f"Created {character.name} (Grade: {grade_name}, Rarity: {character.rarity})"
            }
            
        except Exception as e:
            self.logger.error(f"Failed to create character preview: {e}")
            return {
                'success': False,
                'error': str(e),
                'message': "Failed to create character preview"
            }
    
    def allocate_stat_point(self, stat_name: str, amount: int = 1) -> Dict[str, Any]:
        """
        Allocate stat points to a specific stat with validation.
        
        Args:
            stat_name: Name of the stat to increase
            amount: Number of points to allocate
            
        Returns:
            Dict with allocation status
        """
        try:
            if not self._state.current_character:
                return {
                    'success': False,
                    'error': "No character selected",
                    'message': "No character available for stat allocation"
                }
            
            # Validate allocation
            validation_result = self.validator.validate_stat_allocation(
                self._state.current_character, stat_name, amount
            )
            if not validation_result.success:
                return {
                    'success': False,
                    'error': validation_result.error,
                    'message': validation_result.message
                }
            
            # Check available points (unless infinite mode)
            if not self._state.infinite_stat_points and amount > self._state.available_stat_points:
                return {
                    'success': False,
                    'error': "Insufficient stat points",
                    'message': f"Cannot allocate {amount} points (only {self._state.available_stat_points} available)"
                }
            
            # Perform allocation
            result = self._stat_service.allocate_stat_point(
                self._state.current_character,
                stat_name,
                self._state.available_stat_points,
                amount
            )
            
            if result['success']:
                # Update state
                new_points = self._state.available_stat_points - amount if not self._state.infinite_stat_points else self._state.available_stat_points
                self._state = self._state.with_stat_points(max(0, new_points))
                
                # Notify observers
                self._notify_stats_allocated(self._state.current_character, stat_name, amount)
                
                return {
                    'success': True,
                    'points_remaining': self._state.available_stat_points,
                    'message': result.get('message', f"Allocated {amount} points to {stat_name}")
                }
            else:
                return {
                    'success': False,
                    'error': result.get('error', 'Unknown error'),
                    'message': result.get('message', 'Failed to allocate stat point')
                }
                
        except Exception as e:
            self.logger.error(f"Failed to allocate stat point: {e}")
            return {
                'success': False,
                'error': str(e),
                'message': "Failed to allocate stat point"
            }
    
    def reset_stat_allocation(self) -> Dict[str, Any]:
        """Reset stat allocation to template defaults."""
        try:
            if not self._state.current_character or not self._state.selected_template_id:
                return {
                    'success': False,
                    'error': "No character or template selected",
                    'message': "No character or template selected"
                }
            
            template_data = self._template_service.get_template(self._state.selected_template_id)
            if not template_data:
                return {
                    'success': False,
                    'error': f"Template {self._state.selected_template_id} not found",
                    'message': f"Template {self._state.selected_template_id} not found"
                }
            
            result = self._stat_service.reset_stat_allocation(self._state.current_character, template_data)
            
            if result['success']:
                # Recalculate available stat points based on character's current level
                if self._state.current_character:
                    new_stat_points = self._leveling_manager.calculate_stat_points_available(self._state.current_character)
                    self._state = self._state.with_stat_points(new_stat_points)
                    self.logger.info(f"Reset stats - available points updated to {new_stat_points} for level {self._state.current_character.level}")
                else:
                    # Fallback to default if no character
                    self._state = self._state.with_stat_points(self._get_default_stat_points())
                
                # Notify observers
                self._notify_character_reset()
                
                return {
                    'success': True,
                    'message': "Character stats reset to template defaults"
                }
            else:
                return {
                    'success': False,
                    'error': result.get('error', 'Unknown error'),
                    'message': result.get('message', 'Failed to reset stats')
                }
                
        except Exception as e:
            self.logger.error(f"Failed to reset stats: {e}")
            return {
                'success': False,
                'error': str(e),
                'message': "Failed to reset character stats"
            }
    
    def finalize_character(self, custom_name: Optional[str] = None, save_to_library: bool = None) -> ServiceResult:
        """
        Finalize character creation with validation.
        
        Args:
            custom_name: Optional custom name for the character
            save_to_library: Whether to save to library (uses config default if None)
            
        Returns:
            ServiceResult with finalized character
        """
        try:
            if not self._state.current_character:
                return ServiceResult.error_result("No character to finalize")
            
            # Final validation
            validation_result = self.validator.validate_character(self._state.current_character)
            if not validation_result.success:
                return validation_result
            
            # Apply custom name if provided
            if custom_name and custom_name.strip():
                self._state.current_character.name = custom_name.strip()
            
            # Save to library if requested
            should_save = save_to_library if save_to_library is not None else self.config.auto_save_to_library
            save_result = None
            
            if should_save:
                save_result = self._library_service.save_character(
                    self._state.current_character,
                    self._state.current_character.name,
                    self._state.selected_template_id
                )
                if not save_result['success']:
                    self.logger.warning(f"Failed to save character to library: {save_result.get('error')}")
            
            # Notify observers
            self._notify_character_finalized(self._state.current_character)
            
            finalized_character = self._state.current_character
            self.logger.info(f"Finalized character: {finalized_character.name}")
            
            result_data = {
                'character': finalized_character,
                'stats': self._extract_character_stats(finalized_character)
            }
            
            message = f"Character '{finalized_character.name}' created successfully!"
            
            if save_result and save_result['success']:
                result_data['saved_to_library'] = True
                result_data['save_name'] = save_result['save_name']
                message += f" Saved to library as '{save_result['save_name']}'"
            elif should_save:
                result_data['saved_to_library'] = False
                message += " (Warning: Could not save to library)"
            
            return ServiceResult.success_result(data=result_data, message=message)
            
        except Exception as e:
            self.logger.error(f"Failed to finalize character: {e}")
            return ServiceResult.error_result(str(e), "Failed to finalize character creation")
    
    def reset_creation_state(self) -> ServiceResult:
        """Reset the character creation state to initial values."""
        try:
            self._state = CreationState(available_stat_points=self.config.default_stat_points)
            self.logger.info("Character creation state reset")
            return ServiceResult.success_result(message="Character creation state reset successfully")
        except Exception as e:
            self.logger.error(f"Failed to reset creation state: {e}")
            return ServiceResult.error_result(str(e), "Failed to reset creation state")
    
    # ===== DISPLAY METHODS =====
    
    def get_character_display(self) -> ServiceResult:
        """Get formatted character display text."""
        try:
            if not self._state.current_character:
                return ServiceResult.success_result(
                    data={'display_text': "No character selected"},
                    message="No character available for display"
                )
            
            display_text = self.formatter.format_character_display(self._state.current_character)
            
            return ServiceResult.success_result(
                data={
                    'display_text': display_text,
                    'stats': self._extract_character_stats(self._state.current_character)
                },
                message="Character display formatted successfully"
            )
            
        except Exception as e:
            self.logger.error(f"Failed to format character display: {e}")
            return ServiceResult.error_result(str(e), "Failed to format character display")
    
    def get_template_display(self, template_id: Optional[str] = None) -> ServiceResult:
        """Get formatted template display text."""
        try:
            template_id = template_id or self._state.selected_template_id
            if not template_id:
                return ServiceResult.error_result("No template selected")
            
            template_data = self._template_service.get_template(template_id)
            if not template_data:
                return ServiceResult.error_result(f"Template '{template_id}' not found")
            
            display_text = self.formatter.format_template_display(template_data)
            
            return ServiceResult.success_result(
                data={
                    'display_text': display_text,
                    'template_data': template_data
                },
                message="Template display formatted successfully"
            )
            
        except Exception as e:
            self.logger.error(f"Failed to format template display: {e}")
            return ServiceResult.error_result(str(e), "Failed to format template display")
    
    def get_points_display_info(self) -> Dict[str, Any]:
        """Get points display information."""
        try:
            # Calculate allocated points from character's actual spent points
            allocated_points = 0
            if self._state.current_character:
                allocated_points = getattr(self._state.current_character, 'spent_stat_points', 0)
            
            return {
                'success': True,
                'available_points': self._state.available_stat_points,
                'infinite_mode': self._state.infinite_stat_points,
                'allocated_points': allocated_points,
                'message': "Points display info retrieved successfully"
            }
        except Exception as e:
            self.logger.error(f"Failed to get points display info: {e}")
            return {
                'success': False,
                'error': str(e),
                'message': "Failed to get points display info"
            }
    
    # ===== ADMIN FUNCTIONS =====
    
    def toggle_infinite_stat_points(self) -> ServiceResult:
        """Toggle infinite stat points mode."""
        try:
            admin_result = self._admin_service.toggle_infinite_stat_points()
            if admin_result['success']:
                infinite_enabled = admin_result.get('infinite_stat_points', False)
                self._state = self._state.with_infinite_points(infinite_enabled)
                
                message = "♾️ Infinite stat points enabled" if infinite_enabled else "♾️ Infinite stat points disabled"
                return ServiceResult.success_result(
                    data={'infinite_enabled': infinite_enabled},
                    message=message
                )
            else:
                return ServiceResult.error_result(
                    admin_result.get('error', 'Unknown error'),
                    admin_result.get('message', 'Failed to toggle infinite stat points')
                )
        except Exception as e:
            self.logger.error(f"Failed to toggle infinite stat points: {e}")
            return ServiceResult.error_result(str(e), "Failed to toggle infinite stat points")
    
    def set_character_grade(self, grade: int) -> ServiceResult:
        """Set character grade (admin function)."""
        try:
            if not self._state.current_character:
                return ServiceResult.error_result("No character selected")
            
            result = self._admin_service.set_character_grade(self._state.current_character, grade)
            if result['success']:
                return ServiceResult.success_result(
                    message=f"Character grade set to {grade}"
                )
            else:
                return ServiceResult.error_result(
                    result.get('error', 'Unknown error'),
                    result.get('message', 'Failed to set character grade')
                )
        except Exception as e:
            self.logger.error(f"Failed to set character grade: {e}")
            return ServiceResult.error_result(str(e), "Failed to set character grade")
    
    def set_character_rarity(self, rarity: str) -> ServiceResult:
        """Set character rarity (admin function)."""
        try:
            if not self._state.current_character:
                return ServiceResult.error_result("No character selected")
            
            result = self._admin_service.set_character_rarity(self._state.current_character, rarity)
            if result['success']:
                return ServiceResult.success_result(
                    message=f"Character rarity set to {rarity}"
                )
            else:
                return ServiceResult.error_result(
                    result.get('error', 'Unknown error'),
                    result.get('message', 'Failed to set character rarity')
                )
        except Exception as e:
            self.logger.error(f"Failed to set character rarity: {e}")
            return ServiceResult.error_result(str(e), "Failed to set character rarity")
    
    # ===== LEGACY COMPATIBILITY METHODS =====
    
    def get_available_templates(self) -> Dict[str, Dict[str, Any]]:
        """Legacy method for backward compatibility."""
        return self._template_service.get_available_templates()
    
    def get_template_display_info(self, template_data: Dict[str, Any]) -> Dict[str, Any]:
        """Legacy method for backward compatibility."""
        try:
            display_text = self.formatter.format_template_display(template_data)
            return {
                'success': True,
                'display_text': display_text,
                'template_data': template_data,
                'message': 'Template info formatted successfully'
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': 'Failed to format template information'
            }
    
    def get_character_display_text(self) -> Dict[str, Any]:
        """Get formatted character display text as dictionary."""
        try:
            if not self._state.current_character:
                return {
                    'success': True,
                    'display_text': "No character selected",
                    'stats': {},
                    'message': "No character available for display"
                }
            
            display_text = self.formatter.format_character_display(self._state.current_character)
            
            return {
                'success': True,
                'display_text': display_text,
                'stats': self._extract_character_stats(self._state.current_character),
                'message': "Character display formatted successfully"
            }
            
        except Exception as e:
            self.logger.error(f"Failed to format character display: {e}")
            return {
                'success': False,
                'error': str(e),
                'display_text': '',
                'stats': {},
                'message': 'Failed to format character display'
            }
    
    def get_character_stat_data(self) -> Dict[str, Dict[str, Any]]:
        """Get character stats formatted for UI display."""
        try:
            if not self._state.current_character:
                return {}
            
            character = self._state.current_character
            available_points = self._state.available_stat_points
            
            stat_data = {}
            stat_names = ['strength', 'dexterity', 'vitality', 'intelligence', 
                          'wisdom', 'constitution', 'luck', 'agility', 'charisma']
            
            for stat_name in stat_names:
                current_value = self._safe_get_stat(character, stat_name)
                can_allocate = (available_points > 0 or self._state.infinite_stat_points)
                
                stat_data[stat_name] = {
                    'current_value': f"{current_value:.2f}",
                    'can_allocate': can_allocate
                }
            
            return stat_data
        except Exception as e:
            self.logger.error(f"Failed to get character stat data: {e}")
            return {}
    
    # ===== PRIVATE METHODS =====
    
    def _get_default_stat_points(self, template_id: Optional[str] = None) -> int:
        """Get the default available stat points from template or config."""
        # Try to get from template if provided
        if template_id:
            template = self._template_service.get_template(template_id)
            if template and 'stat_points' in template:
                return template['stat_points']
        # Fallback to config
        return self._config_manager.get('character_creation.stat_points', 
                                      self._config_manager.get('stat_points_per_level', 3))
    
    def _extract_character_stats(self, character: Any) -> Dict[str, Any]:
        """Extract comprehensive character statistics."""
        try:
            stats = {}
            
            # Basic info
            stats['name'] = getattr(character, 'name', 'Unknown')
            stats['level'] = getattr(character, 'level', 1)
            stats['grade'] = getattr(character, 'grade', 0)
            stats['grade_name'] = getattr(character, 'grade_name', 'ONE')
            stats['rarity'] = getattr(character, 'rarity', 'COMMON')
            
            # Primary stats
            primary_stats = ['strength', 'dexterity', 'vitality', 'intelligence',
                           'wisdom', 'constitution', 'luck', 'agility', 'charisma']
            for stat in primary_stats:
                stats[stat] = self._safe_get_stat(character, stat)
            
            # Derived stats
            derived_stats = ['health', 'mana', 'attack', 'defense']
            for stat in derived_stats:
                stats[stat] = self._safe_get_stat(character, stat)
            
            return stats
        except Exception as e:
            self.logger.error(f"Failed to extract character stats: {e}")
            return {}
    
    def _safe_get_stat(self, character: Any, stat_name: str, default_value: float = 0.0) -> float:
        """Safely get a character stat."""
        try:
            if hasattr(character, 'get_stat'):
                return float(character.get_stat(stat_name))
            return float(getattr(character, stat_name, default_value))
        except (AttributeError, ValueError, TypeError):
            return default_value
    
    def _notify_character_created(self, character: Any) -> None:
        """Notify observers that a character was created."""
        for observer in self.observers:
            try:
                observer.on_character_created(character)
            except Exception as e:
                self.logger.error(f"Observer notification failed: {e}")
    
    def _notify_stats_allocated(self, character: Any, stat_name: str, amount: int) -> None:
        """Notify observers that stats were allocated."""
        for observer in self.observers:
            try:
                observer.on_stats_allocated(character, stat_name, amount)
            except Exception as e:
                self.logger.error(f"Observer notification failed: {e}")
    
    def _notify_character_finalized(self, character: Any) -> None:
        """Notify observers that character was finalized."""
        for observer in self.observers:
            try:
                observer.on_character_finalized(character)
            except Exception as e:
                self.logger.error(f"Observer notification failed: {e}")
        
        # Also publish centralized event
        try:
            from interfaces.ui_observer import GameEventPublisher
            character_name = getattr(character, 'name', 'Unknown Character')
            GameEventPublisher.publish_character_finalized(character_name, source=self)
        except Exception as e:
            self.logger.error(f"Failed to publish character finalized event: {e}")
    
    def _notify_character_saved(self, character: Any, save_name: str) -> None:
        """Notify observers that character was saved."""
        for observer in self.observers:
            try:
                observer.on_character_saved(character, save_name)
            except Exception as e:
                self.logger.error(f"Observer notification failed: {e}")
        
        # Also publish centralized event
        try:
            from interfaces.ui_observer import GameEventPublisher
            character_name = getattr(character, 'name', 'Unknown Character')
            GameEventPublisher.publish_character_saved(character_name, save_name, source=self)
        except Exception as e:
            self.logger.error(f"Failed to publish character saved event: {e}")
    
    def _notify_character_loaded(self, character: Any, save_name: str) -> None:
        """Notify observers that character was loaded."""
        for observer in self.observers:
            try:
                observer.on_character_loaded(character, save_name)
            except Exception as e:
                self.logger.error(f"Observer notification failed: {e}")
        
        # Also publish centralized event
        try:
            from interfaces.ui_observer import GameEventPublisher
            character_name = getattr(character, 'name', 'Unknown Character')
            GameEventPublisher.publish_character_loaded(character_name, save_name, source=self)
        except Exception as e:
            self.logger.error(f"Failed to publish character loaded event: {e}")
    
    def _notify_template_selected(self, template_id: str) -> None:
        """Notify observers that template was selected."""
        for observer in self.observers:
            try:
                observer.on_template_selected(template_id)
            except Exception as e:
                self.logger.error(f"Observer notification failed: {e}")
        
        # Also publish centralized event
        try:
            from interfaces.ui_observer import GameEventPublisher
            GameEventPublisher.publish_template_selected(template_id, source=self)
        except Exception as e:
            self.logger.error(f"Failed to publish template selected event: {e}")
    
    def _notify_character_reset(self) -> None:
        """Notify observers that character was reset."""
        for observer in self.observers:
            try:
                observer.on_character_reset()
            except Exception as e:
                self.logger.error(f"Observer notification failed: {e}")
        
        # Also publish centralized event
        try:
            from interfaces.ui_observer import GameEventPublisher
            character_name = getattr(self._state.current_character, 'name', None) if hasattr(self, '_state') and self._state.current_character else None
            GameEventPublisher.publish_character_reset(character_name, source=self)
        except Exception as e:
            self.logger.error(f"Failed to publish character reset event: {e}")
    
    # ===== MISSING UI INTEGRATION METHODS =====
    
    def get_saved_character_list(self) -> Dict[str, Any]:
        """Get list of saved characters from the library."""
        try:
            if hasattr(self, '_library_service'):
                result = self._library_service.list_characters()
                return {
                    'success': result.get('success', False),
                    'characters': result.get('characters', []),
                    'count': result.get('count', 0),
                    'message': result.get('message', 'Retrieved character list')
                }
            else:
                # Fallback - return empty list if library service not available
                return {
                    'success': True,
                    'characters': [],
                    'count': 0,
                    'message': 'Character library service not available'
                }
        except Exception as e:
            self.logger.error(f"Failed to get saved character list: {e}")
            return {
                'success': False,
                'characters': [],
                'count': 0,
                'message': f"Error getting character list: {e}"
            }
    
    def save_current_character(self, save_name: str) -> Dict[str, Any]:
        """Save current character to library with custom name."""
        try:
            if not self._state.current_character:
                return {
                    'success': False,
                    'message': 'No character to save'
                }
            
            if hasattr(self, '_library_service'):
                # Get the template_id from the current state
                template_id = getattr(self._state, 'selected_template_id', 'unknown')
                result = self._library_service.save_character(
                    self._state.current_character, 
                    save_name, 
                    template_id
                )
                
                # Notify observers if save was successful
                if result.get('success', False):
                    self._notify_character_saved(self._state.current_character, save_name)
                
                return {
                    'success': result.get('success', False),
                    'save_name': save_name,
                    'message': result.get('message', f'Character saved as {save_name}')
                }
            else:
                return {
                    'success': False,
                    'message': 'Character library service not available'
                }
        except Exception as e:
            self.logger.error(f"Failed to save character: {e}")
            return {
                'success': False,
                'message': f"Error saving character: {e}"
            }
    
    def load_saved_character(self, save_name: str) -> Dict[str, Any]:
        """Load a character from the library and set it as current character."""
        try:
            if hasattr(self, '_library_service'):
                result = self._library_service.load_character(save_name)
                
                if result.get('success', False):
                    loaded_character = result.get('character')
                    template_id = result.get('template_id')
                    
                    if loaded_character and template_id:
                        # Update the service state with the loaded character
                        stat_points = self._get_default_stat_points(template_id)
                        self._state = (self._state
                                     .with_character(loaded_character)
                                     .with_template(template_id)
                                     .with_stat_points(stat_points))
                        
                        # Notify observers
                        self._notify_character_loaded(loaded_character, save_name)
                        
                        return {
                            'success': True,
                            'character': loaded_character,
                            'template_id': template_id,
                            'save_name': save_name,
                            'message': result.get('message', f'Character {save_name} loaded successfully')
                        }
                    else:
                        return {
                            'success': False,
                            'message': 'Loaded character data was incomplete'
                        }
                else:
                    return {
                        'success': False,
                        'error': result.get('error', 'Unknown error'),
                        'message': result.get('message', f'Failed to load character {save_name}')
                    }
            else:
                return {
                    'success': False,
                    'message': 'Character library service not available'
                }
        except Exception as e:
            self.logger.error(f"Failed to load character {save_name}: {e}")
            return {
                'success': False,
                'error': str(e),
                'message': f"Error loading character {save_name}: {e}"
            }
    
    def delete_saved_character(self, save_name: str) -> Dict[str, Any]:
        """Delete a character from the library."""
        try:
            if hasattr(self, '_library_service'):
                result = self._library_service.delete_character(save_name)
                return {
                    'success': result.get('success', False),
                    'message': result.get('message', f'Character {save_name} deleted')
                }
            else:
                return {
                    'success': False,
                    'message': 'Character library service not available'
                }
        except Exception as e:
            self.logger.error(f"Failed to delete character: {e}")
            return {
                'success': False,
                'message': f"Error deleting character: {e}"
            }
    
    def toggle_admin_mode(self) -> Dict[str, Any]:
        """Toggle admin mode for character creation."""
        try:
            if hasattr(self, '_admin_service'):
                # Toggle admin mode
                current_mode = getattr(self._admin_service, 'admin_enabled', False)
                new_mode = not current_mode
                self._admin_service.admin_enabled = new_mode
                
                return {
                    'success': True,
                    'admin_enabled': new_mode,
                    'message': f"Admin mode {'enabled' if new_mode else 'disabled'}"
                }
            else:
                return {
                    'success': False,
                    'message': 'Admin service not available'
                }
        except Exception as e:
            self.logger.error(f"Failed to toggle admin mode: {e}")
            return {
                'success': False,
                'message': f"Error toggling admin mode: {e}"
            }