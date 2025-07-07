# game_sys/items/material.py
"""
Module: game_sys.items.material

Crafting materials and misc items that don't have special effects.
"""
from typing import Any
from game_sys.items.base import Item


class Material(Item):
    """
    Material item used for crafting or trading.
    Has no special effects when used.
    """
    def __init__(self, item_id: str, name: str, description: str, **attrs):
        super().__init__(item_id, name, description, **attrs)
        
        # Materials typically have a price for trading
        self.price = attrs.get('price', 1)

    def apply(self, user: Any, target: Any = None) -> None:
        """
        Materials have no effect when used.
        """
        pass
