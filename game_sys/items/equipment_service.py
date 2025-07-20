# game_sys/items/equipment_service.py
"""
Equipment Service
================

Service layer for equipment operations. This module provides a bridge between
the items system and the equipment manager, following the project's service-oriented
architecture pattern.
"""

from typing import Any, Tuple, Optional
from game_sys.logging import get_logger
from game_sys.managers.equipment_manager import equipment_manager

logger = get_logger(__name__)


class EquipmentService:
    """
    Service layer for equipment operations.
    
    This service acts as a bridge between the items system and the equipment manager,
    providing a clean API for equipment operations while maintaining separation of concerns.
    """
    
    def __init__(self):
        self.equipment_manager = equipment_manager
        logger.info("Equipment Service initialized")
    
    def equip_item(self, actor: Any, item: Any) -> Tuple[bool, str]:
        """
        Equip an item on an actor using smart logic.
        
        Args:
            actor: The character equipping the item
            item: The item to equip
            
        Returns:
            Tuple[bool, str]: (success, message)
        """
        return self.equipment_manager.equip_item_with_smart_logic(actor, item)
    
    def unequip_item(self, actor: Any, slot: str) -> Tuple[bool, str]:
        """
        Unequip an item from a specific slot.
        
        Args:
            actor: The character unequipping the item
            slot: The slot to unequip from
            
        Returns:
            Tuple[bool, str]: (success, message)
        """
        return self.equipment_manager.unequip_item_from_slot(actor, slot)
    
    def can_equip(self, actor: Any, item: Any) -> bool:
        """
        Check if an item can be equipped (simple boolean check).
        
        Args:
            actor: The character who would equip the item
            item: The item to check
            
        Returns:
            bool: True if the item can be equipped
        """
        available, _ = self.check_equipment_availability(actor, item)
        return available
    
    def check_equipment_availability(self, actor: Any, item: Any) -> Tuple[bool, Optional[str]]:
        """
        Check if an item can be equipped.
        
        Args:
            actor: The character who would equip the item
            item: The item to check
            
        Returns:
            Tuple[bool, Optional[str]]: (available, conflict_message)
        """
        slot = getattr(item, 'slot', None)
        if not slot:
            return False, "Item has no equipment slot"
            
        return self.equipment_manager.check_equipment_slot_availability(actor, item, slot)
    
    def get_equipment_status(self, actor: Any) -> str:
        """
        Get a text description of the actor's current equipment status.
        
        Args:
            actor: The character to check
            
        Returns:
            str: Equipment status description
        """
        return self.equipment_manager.get_dual_wield_status_info(actor)
    
    def suggest_equipment_resolution(self, actor: Any, item: Any) -> str:
        """
        Get suggestions for resolving equipment conflicts.
        
        Args:
            actor: The character who wants to equip the item
            item: The item that has conflicts
            
        Returns:
            str: Suggestion message
        """
        slot = getattr(item, 'slot', None)
        if not slot:
            return "Item has no equipment slot"
            
        return self.equipment_manager.suggest_equipment_resolution(actor, item, slot)


# Global service instance
equipment_service = EquipmentService()