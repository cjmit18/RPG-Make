# game_sys/items/accessory.py
"""
Module: game_sys.items.accessory

Accessory items like rings, amulets, and other jewelry.
"""
from typing import Dict, Any, List
from game_sys.items.equipment import Equipment


class Accessory(Equipment):
    """
    Accessory items that can be equipped for stat bonuses and special effects.
    """
    def __init__(self, item_id: str, name: str, description: str, **kwargs):
        # Extract accessory-specific properties
        slot = kwargs.pop('slot', 'accessory')
        stats = kwargs.pop('stats', {})
        effect_ids = kwargs.pop('effect_ids', [])
        
        # Initialize Equipment with extracted properties
        super().__init__(item_id, name, description,
                         slot=slot,
                         stats=stats,
                         effect_ids=effect_ids,
                         **kwargs)
        
    def apply(self, user: Any, target: Any = None) -> None:
        """Apply accessory effects to an actor."""
        super().apply(user, target)
        
    def get_tooltip_data(self) -> Dict[str, Any]:
        """Get data for tooltip display."""
        data = super().get_tooltip_data()
        return data
