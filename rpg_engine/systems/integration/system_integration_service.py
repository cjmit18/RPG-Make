"""
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
