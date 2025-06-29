# game_sys/items/consumable.py
"""
Module: game_sys.items.consumable

A one‐use item that applies a list of effect IDs to a target.
"""
from typing import Any, List
from game_sys.items.base import Item
from game_sys.effects.factory import EffectFactory


class Consumable(Item):
    """
    Consumable item that applies effects on use.
    JSON attrs:
      - effects: List[Dict] of effect definitions (type + params)
    """
    def __init__(self, item_id: str, name: str, description: str, effects: List[dict], **attrs):
        super().__init__(item_id, name, description, **attrs)
        # Pre‐parse effect definitions into Effect instances
        self._effect_defs = effects
        self._effects = [EffectFactory.create(defn) for defn in effects]

    def apply(self, user: Any, target: Any = None) -> None:
        """
        Apply each configured effect, passing user as caster and target as recipient.
        """
        for eff in self._effects:
            eff.apply(user, target or user)
