"""
Game Systems Package
===================

Core game engine systems including character management, combat,
configuration, logging, and game mechanics.

Modules:
- character: Character creation and management systems
- combat: Combat mechanics and services
- config: Configuration management
- logging: Centralized logging system
- equipment: Equipment and item systems
- admin: Administrative tools and services
"""

from .config.config_manager import ConfigManager
from .logging import get_logger

# Core service imports
try:
    from .character.character_creation_service import CharacterCreationService
    from .combat.combat_service import CombatService
except ImportError as e:
    # Graceful handling if services aren't available yet
    CharacterCreationService = None
    CombatService = None

__all__ = [
    "ConfigManager",
    "get_logger",
    "CharacterCreationService", 
    "CombatService"
]