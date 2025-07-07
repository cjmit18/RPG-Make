# game_sys/magic/enchanting_system.py

from typing import Any, Dict, List, Optional
import json
import os
from pathlib import Path

from game_sys.items.enchantment import Enchantment
from game_sys.items.item_loader import load_item
from game_sys.logging import character_logger
from game_sys.config.config_manager import ConfigManager


class EnchantingSystem:
    """
    System for managing enchantments for a character.
    Allows learning, applying, and managing enchantments.
    """

    def __init__(self, actor):
        self.actor = actor
        # Only initialize known_enchantments if actor is not None
        if actor is not None and not hasattr(actor, 'known_enchantments'):
            actor.known_enchantments = []
        self.config_manager = ConfigManager()
        self._load_enchantments()

    def _load_enchantments(self):
        """Load available enchantments from enchantments.json."""
        self.available_enchantments = {}
        
        # Try to load from new enchantments.json file
        try:
            enchantments_path = (Path(__file__).parent /
                                 "data" / "enchantments.json")
            if enchantments_path.exists():
                with open(enchantments_path, 'r') as f:
                    enchantments_data = json.load(f)
                    
                # Extract enchantments from enchantments.json
                enchantments = enchantments_data.get('enchantments', {})
                for enchant_id, enchant_data in enchantments.items():
                    self.available_enchantments[enchant_id] = enchant_data
            else:
                # Fallback: try items.json for backward compatibility
                items_path = (Path(__file__).parent.parent /
                              "items" / "data" / "items.json")
                if items_path.exists():
                    with open(items_path, 'r') as f:
                        items_data = json.load(f)
                        
                    # Extract enchantments from items.json
                    items = items_data.get('items', {})
                    for item_id, item_data in items.items():
                        if item_data.get('type') == 'enchantment':
                            self.available_enchantments[item_id] = item_data
                else:
                    # Final fallback: hardcode enchantments
                    self.available_enchantments = {
                        'fire_enchant': {'name': 'Flame Enchantment'},
                        'ice_enchant': {'name': 'Frost Enchantment'},
                        'lightning_enchant': {'name': 'Lightning Enchantment'},
                        'poison_enchant': {'name': 'Poison Enchantment'},
                        'strength_enchant': {'name': 'Strength Enchantment'},
                        'speed_enchant': {'name': 'Speed Enchantment'},
                    }
        except Exception:
            # Fallback: Use config or hardcoded list
            enchantments = self.config_manager.get_section('enchantments', {})
            if enchantments:
                for enchant_id, enchant_data in enchantments.items():
                    self.available_enchantments[enchant_id] = enchant_data
            else:
                # Last resort: hardcode
                self.available_enchantments = {
                    'fire_enchant': {'name': 'Flame Enchantment'},
                    'ice_enchant': {'name': 'Frost Enchantment'},
                    'lightning_enchant': {'name': 'Lightning Enchantment'},
                    'poison_enchant': {'name': 'Poison Enchantment'},
                    'strength_enchant': {'name': 'Strength Enchantment'},
                    'speed_enchant': {'name': 'Speed Enchantment'},
                }

    def learn_enchantment(self, enchant_id: str) -> bool:
        """
        Learn a new enchantment if requirements are met.
        
        Args:
            enchant_id: The ID of the enchantment to learn
            
        Returns:
            bool: True if learned, False otherwise
        """
        # Check if already learned
        if enchant_id in self.actor.known_enchantments:
            character_logger.info(f"{self.actor.name} already knows enchantment: {enchant_id}")
            return False
            
        # Check requirements (disabled for demo purposes)
        # TODO: Re-enable proper requirements checking when leveling system is stable
        # if (hasattr(self.actor, 'leveling_manager') and 
        #         hasattr(self.actor.leveling_manager, 'check_enchantment_requirements')):
        #     mgr = self.actor.leveling_manager
        #     check_method = mgr.check_enchantment_requirements
        #     if not check_method(self.actor, enchant_id):
        #         character_logger.info(
        #             f"{self.actor.name} doesn't meet requirements for "
        #             f"enchantment: {enchant_id}")
        #         return False
        
        # Learn the enchantment
        self.actor.known_enchantments.append(enchant_id)
        character_logger.info(
            f"{self.actor.name} learned enchantment: {enchant_id}")
        return True
    
    def get_known_enchantments(self) -> List[str]:
        """Get list of known enchantment IDs."""
        return self.actor.known_enchantments
    
    def get_available_enchantments(self) -> List[str]:
        """Get list of all enchantments that can be learned (including already known)."""
        return list(self.available_enchantments.keys())
    
    def get_unlearned_enchantments(self) -> List[str]:
        """Get list of enchantments that can be learned but haven't been yet."""
        return [e_id for e_id in self.available_enchantments 
                if e_id not in self.actor.known_enchantments]
    
    def apply_enchantment(self, enchant_id: str, item) -> bool:
        """
        Apply a known enchantment to an item.
        
        Args:
            enchant_id: The ID of the enchantment to apply
            item: The item to enchant
            
        Returns:
            bool: True if applied successfully, False otherwise
        """
        if enchant_id not in self.actor.known_enchantments:
            character_logger.info(f"{self.actor.name} doesn't know enchantment: {enchant_id}")
            return False
            
        # Load the enchantment
        enchantment = load_item(enchant_id)
        if not enchantment or not isinstance(enchantment, Enchantment):
            character_logger.error(f"Failed to load enchantment: {enchant_id}")
            return False
            
        # Apply enchantment to item
        enchantment.apply(self.actor, item)
        character_logger.info(f"{self.actor.name} applied {enchant_id} to {item.name}")
        return True
    
    def can_enchant_item(self, item) -> bool:
        """Check if an item can be enchanted."""
        # Can only enchant weapons and armor for now
        item_type = getattr(item, 'type', None)
        return item_type in ['weapon', 'armor', 'offhand']
    
    def get_enchantable_items(self) -> List:
        """Get list of items in inventory that can be enchanted."""
        if not hasattr(self.actor, 'inventory'):
            return []
            
        items = self.actor.inventory.list_items()
        return [item for item in items if self.can_enchant_item(item)]
    
    def get_enchantment_info(self, enchant_id: str) -> Dict:
        """Get information about an enchantment."""
        return self.available_enchantments.get(enchant_id, {})


# Create a global instance for convenience
enchanting_system = EnchantingSystem(None)
