# game_sys/items/enchantment.py

from typing import Any, List, Dict
from game_sys.items.base import Item
from game_sys.effects.factory import EffectFactory
from game_sys.core.damage_types import DamageType

class Enchantment(Item):
    """
    Enchantment that injects effects + damage_type into a piece of equipment.
    """

    def __init__(
        self,
        item_id: str,
        name: str,
        description: str,
        effects: List[Dict],
        damage_type: str = "PHYSICAL",
        **attrs
    ):
        super().__init__(item_id, name, description, **attrs)
        # Build the live Effect instances from JSON definitions
        self._effects     = [EffectFactory.create(defn) for defn in effects]
        try:
            self.damage_type = DamageType[damage_type.upper()]
        except KeyError:
            self.damage_type = DamageType.PHYSICAL

    def apply(self, user: Any, target: Any = None) -> None:
        """
        Slot this enchantment into `target` equipment:
          - Adds its effect IDs to target.effect_ids
          - Sets target.damage_type
          - Records the enchantment’s own ID in target.enchantments
        """
        if target and hasattr(target, "effect_ids"):
            for eff in self._effects:
                target.effect_ids.append(eff.id)
            target.damage_type = self.damage_type

        if target and hasattr(target, "enchantments"):
            target.enchantments.append(self.id)
