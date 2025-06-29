# game_sys/items/armor.py
"""
Module: game_sys.items.armor

Concrete Armor subclass with defensive stats.
"""
from typing import Any
from game_sys.items.equipment import Equipment

class Armor(Equipment):
    """
    Armor item.
    JSON attrs:
      - defense: float
      - effect_ids: optional List[str] of damage‐taken modifiers
    """
    def __init__(self, item_id: str, name: str, description: str,
                 defense: float, effect_ids: list[str] = None, **attrs):
        super().__init__(item_id, name, description,
                         slot="body",
                         stats={"defense": defense},
                         effect_ids=effect_ids or [],
                         **attrs)

    def apply(self, user: Any, target: Any = None) -> None:
        super().apply(user, target)
