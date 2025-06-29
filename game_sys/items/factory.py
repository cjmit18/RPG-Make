# game_sys/items/factory.py
"""
Module: game_sys.items.factory

Creates Item instances from JSON definitions.
"""
import json
from typing import Any, Dict
from pathlib import Path
from game_sys.items.registry import ItemRegistry

# Load all item definitions once
_ITEM_DATA: Dict[str, Dict[str, Any]] = {}
_data_path = Path(__file__).parent / 'data' / 'items.json'
if _data_path.exists():
    _ITEM_DATA = json.loads(_data_path.read_text()).get('items', {})

class ItemFactory:
    """
    Builds Item instances by ID.
    """
    @staticmethod
    def create(item_id: str) -> Any:
        data = _ITEM_DATA.get(item_id)
        if not data:
            return ItemRegistry.get('null')()
        item_type = data.get('type', 'null')
        cls = ItemRegistry.get(item_type)
        # Pass all JSON fields as kwargs
        return cls(item_id=item_id, **data)
