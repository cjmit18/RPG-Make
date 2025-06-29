# game_sys/items/item_loader.py
"""
Module: game_sys.items.item_loader

Loads item definitions and constructs item instances.
Stubbed for now to return a minimal Item object with an `apply` method.
"""

import json
from pathlib import Path
from typing import Any


class Item:
    """
    Minimal Item class.
    Attributes are set from the JSON file, if it exists.
    """
    def __init__(self, id: str, **attrs):
        self.id = id
        for k, v in attrs.items():
            setattr(self, k, v)

    def apply(self, actor: Any):
        """
        Apply this item's effect to the given actor.
        Stub: does nothing by default; override in real items.
        """
        pass


def load_item(item_id: str) -> Item:
    """
    Attempt to load <item_id>.json from the same folder;
    if missing or invalid, return a bare Item(id).
    """
    path = Path(__file__).parent / f"{item_id}.json"
    if path.exists():
        try:
            data = json.loads(path.read_text())
            # Expect JSON to contain attributes for the Item ctor
            return Item(item_id, **data)
        except Exception:
            # Malformed JSON: fall through to bare Item
            pass
    return Item(item_id)