"""
Character System Package
=======================

Character creation, management, and progression systems.

Core Components:
- Character creation service with template system
- Character stats and attributes management
- Character progression and leveling
- Character data validation and persistence

Services:
- CharacterCreationService: Main character creation interface
- Character templates and presets
- Stat allocation and management
- Character validation systems
"""

try:
    from .character_creation_service import CharacterCreationService
except ImportError:
    CharacterCreationService = None
    Character = None
    CharacterTemplate = None

__all__ = [
    "CharacterCreationService",
    "Character", 
    "CharacterTemplate"
]