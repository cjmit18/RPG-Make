# game_sys/items/equipment.py

from typing import Any, Dict, List
from game_sys.items.base import Item

class Equipment(Item):
    """
    Base class for equippable gear.
    Tracks both raw effect_ids and which enchantment items have been slotted.
    """

    def __init__(
        self,
        item_id: str,
        name: str,
        description: str,
        slot: str,
        stats: Dict[str, float],
        effect_ids: List[str],
        **attrs
    ):
        super().__init__(item_id, name, description, **attrs)
        self.slot           = slot
        self.stats          = stats
        self.effect_ids     = effect_ids
        self.enchantments   = []  # List[str] of applied enchantment item IDs

    def apply(self, user: Any, target: Any = None) -> None:
        """
        Equip this item on the user.
        The engine should merge `stats` into actor, and register effect_ids.
        """
        setattr(user, f"equipped_{self.slot}", self)
