#!/usr/bin/env python3
"""
Module Cleanup Script
Removes non-character system modules and updates references
"""
import os
import shutil
import glob
from pathlib import Path

def main():
    """Remove all non-character system modules"""
    
    # Base directory
    base_dir = Path(__file__).parent.parent
    systems_dir = base_dir / "rpg_engine" / "systems"
    
    print("🧹 Starting module cleanup...")
    print(f"Working directory: {base_dir}")
    
    # Modules to remove (keep character system only)
    modules_to_remove = [
        "combat",
        "quest", 
        "world",
        "ui"
    ]
    
    # Remove module directories
    for module in modules_to_remove:
        module_path = systems_dir / module
        if module_path.exists():
            print(f"🗑️  Removing {module} system...")
            shutil.rmtree(module_path)
            print(f"✅ Removed {module_path}")
    
    # Clean integration service (keep only mock methods)
    integration_file = systems_dir / "integration" / "system_integration_service.py"
    if integration_file.exists():
        print("🔧 Cleaning integration service...")
        create_minimal_integration_service(integration_file)
        print("✅ Integration service cleaned")
    
    # Update systems __init__.py to only export character system
    systems_init = systems_dir / "__init__.py"
    if systems_init.exists():
        print("📝 Updating systems __init__.py...")
        update_systems_init(systems_init)
        print("✅ Systems __init__.py updated")
    
    # Remove imports from engine
    engine_file = base_dir / "rpg_engine" / "core" / "engine.py"
    if engine_file.exists():
        print("🔧 Cleaning engine imports...")
        clean_engine_imports(engine_file)
        print("✅ Engine imports cleaned")
    
    print("🎉 Module cleanup complete!")
    print("\n📋 Summary:")
    print("✅ Removed: combat, quest, world, ui systems")
    print("✅ Cleaned: integration service")
    print("✅ Updated: systems exports")
    print("✅ Cleaned: engine imports")
    print("\n🔍 Retained: character system (complete)")

def create_minimal_integration_service(file_path):
    """Create minimal integration service with only mock methods"""
    content = '''"""
System Integration Service - Minimal Mock Implementation

Provides mock implementations for testing character system
without dependencies on other systems.
"""
import asyncio
import logging
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field

from ...core.service_container import ServiceContainer, AsyncInitializable
from ...core.event_bus import EventBus, GameEvent


@dataclass(frozen=True)
class CharacterSystemEvent(GameEvent):
    """Event for character system operations"""
    character_id: str = ""
    character_name: str = ""
    operation: str = ""
    result: Dict[str, Any] = field(default_factory=dict)


class SystemIntegrationService(AsyncInitializable):
    """
    Mock integration service for character system testing
    
    Provides minimal mock implementations to support character system
    development without requiring other systems to be present.
    """
    
    def __init__(self, service_container: ServiceContainer):
        self.service_container = service_container
        self.event_bus: Optional[EventBus] = None
        self.logger = logging.getLogger(__name__)
    
    async def initialize_async(self) -> None:
        """Initialize integration service"""
        self.event_bus = await self.service_container.get_service(EventBus)
        self.logger.info("SystemIntegrationService initialized (mock mode)")
    
    async def get_character_data_async(self, character_id: str) -> Optional[Dict[str, Any]]:
        """Get mock character data for testing"""
        return await self._get_mock_character_data(character_id)
    
    async def get_available_character_templates_async(self) -> List[Dict[str, Any]]:
        """Get mock character templates"""
        return [
            {
                "template_id": "warrior_basic",
                "name": "Basic Warrior",
                "description": "A sturdy melee fighter",
                "base_stats": {
                    "strength": 15,
                    "dexterity": 12,
                    "constitution": 14,
                    "intelligence": 10,
                    "wisdom": 11,
                    "charisma": 9
                },
                "starting_equipment": ["iron_sword", "leather_armor"],
                "abilities": ["power_attack", "shield_bash"]
            },
            {
                "template_id": "mage_basic", 
                "name": "Basic Mage",
                "description": "A wielder of arcane magic",
                "base_stats": {
                    "strength": 8,
                    "dexterity": 10,
                    "constitution": 10,
                    "intelligence": 16,
                    "wisdom": 13,
                    "charisma": 12
                },
                "starting_equipment": ["wooden_staff", "robes"],
                "abilities": ["magic_missile", "shield"]
            }
        ]
    
    async def get_system_statistics_async(self) -> Dict[str, Any]:
        """Get mock system statistics"""
        return {
            "systems_active": 1,  # Only character system
            "total_events_processed": 0,
            "uptime_seconds": 0,
            "character_system": {
                "active": True,
                "characters_loaded": 0,
                "last_activity": "never"
            }
        }
    
    async def _get_mock_character_data(self, character_id: str) -> Dict[str, Any]:
        """Generate mock character data"""
        return {
            "character_id": character_id,
            "name": f"Mock Character {character_id[:8]}",
            "level": 1,
            "experience": 0,
            "health": 100,
            "mana": 50,
            "location": "starting_town",
            "status": "active",
            "last_seen": "2025-01-01T00:00:00Z"
        }
    
    async def shutdown_async(self) -> None:
        """Cleanup integration service"""
        self.logger.info("SystemIntegrationService shutdown")
'''
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)

def update_systems_init(file_path):
    """Update systems __init__.py to only export character system"""
    content = '''"""
RPG Engine Systems - Character System Only

This module currently only exports the character system.
Other systems have been temporarily removed for focused development.
"""

from .character.character_system import CharacterSystem
from .character.stat_system import StatSystem
from .character.progression_system import ProgressionSystem  
from .character.inventory_system import InventorySystem

from .integration.system_integration_service import SystemIntegrationService

__all__ = [
    'CharacterSystem',
    'StatSystem', 
    'ProgressionSystem',
    'InventorySystem',
    'SystemIntegrationService'
]
'''
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)

def clean_engine_imports(file_path):
    """Remove imports of deleted systems from engine.py"""
    # Read current content
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Remove imports for deleted systems
    imports_to_remove = [
        "from ..systems.combat.combat_system import CombatSystem",
        "from ..systems.quest.quest_system import QuestSystem",
        "from ..systems.world.world_system import WorldSystem",
        "from ..systems.ui.input_system import InputSystem",
        "CombatSystem",
        "QuestSystem", 
        "WorldSystem",
        "InputSystem"
    ]
    
    for import_line in imports_to_remove:
        content = content.replace(import_line, "")
    
    # Clean up empty lines and registration code
    lines = content.split('\n')
    cleaned_lines = []
    
    for line in lines:
        # Skip lines that register deleted systems
        if any(system in line for system in ["CombatSystem", "QuestSystem", "WorldSystem", "InputSystem"]):
            continue
        cleaned_lines.append(line)
    
    # Write cleaned content
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(cleaned_lines))

if __name__ == "__main__":
    main()
