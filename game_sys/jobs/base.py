"""Base Job Class
This module defines the base class for all jobs in the game system."""
from typing import Dict, List
from game_sys.items.factory import create_item
from game_sys.items.item_base import Equipable, Item
from game_sys.items.consumable_list import Consumable

class Job:
    """
    Base class for all Jobs.
    Holds base stat modifiers (scaled by level) and starting equipment.
    """
    name: str = "Base"
    base_stats: Dict[str, int] = {
        "health": 10,
        "mana": 5,
        "stamina": 5,
        "attack": 5,
        "defense": 5,
        "speed": 5,
    }
    starting_item_ids: List[str] = []

    def __init__(self, level: int = 1):
        self.level = level
        # Scale each base stat by level
        self.stats_mods = {stat: val * self.level for stat, val in self.base_stats.items()}
        # Instantiate starting items from their IDs
        self.starting_items = [create_item(item_id) for item_id in self.starting_item_ids]

    def description(self) -> str:
        """Default description for the Base job."""
        return "A generic adventurer with no specialization."
