# game_sys/items/base.py
"""
Module: game_sys.items.base

Defines the abstract Item interface and a NullItem fallback.
"""
from abc import ABC, abstractmethod
from typing import Any


class Item(ABC):
    """
    Base class for all in‐game items.
    """

    def __init__(self, item_id: str, name: str, description: str, **attrs):
        self.id = item_id
        self.name = name
        self.description = description
        # any extra attributes (e.g. stats) get attached
        for k, v in attrs.items():
            setattr(self, k, v)

    @abstractmethod
    def apply(self, user: Any, target: Any = None) -> None:
        """
        Execute the item's effect.
        - For consumables, target might be the user.
        - For equipment, this might equip the item.
        """
        ...


class NullItem(Item):
    """
    No-op item used when an item_id isn’t registered.
    """
    def __init__(self):
        super().__init__(
            item_id="null",
            name="Null Item",
            description="No effect"
        )

    def apply(self, user: Any, target: Any = None) -> None:
        pass
