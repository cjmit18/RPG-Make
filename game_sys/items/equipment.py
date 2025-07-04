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
        Delegates to actor's equip methods for weapon/offhand slots,
        or sets the slot directly for armor pieces.
        """
        # Delegate to actor's equip methods for weapon/offhand slots
        if self.slot == "weapon":
            if hasattr(user, 'equip_weapon'):
                user.equip_weapon(self)
            else:
                setattr(user, "weapon", self)
        elif self.slot == "offhand":
            if hasattr(user, 'equip_offhand'):
                user.equip_offhand(self)
            else:
                setattr(user, "offhand", self)
        else:
            # For armor and other slots, merge stats directly
            for stat_name, bonus in self.stats.items():
                current_value = user.base_stats.get(stat_name, 0.0)
                user.base_stats[stat_name] = current_value + bonus
            
            # Add effect IDs to actor's skill effect IDs
            user.skill_effect_ids.extend(self.effect_ids)
            
            # Set the equipment slot
            setattr(user, f"equipped_{self.slot}", self)
        
        # Update actor's computed stats
        if hasattr(user, 'update_stats'):
            user.update_stats()
