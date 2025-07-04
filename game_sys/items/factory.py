# game_sys/items/factory.py
"""
Module: game_sys.items.factory

Creates Item instances from JSON definitions.
"""
import json
from typing import Any, Dict
from pathlib import Path
from game_sys.items.registry import ItemRegistry
from game_sys.logging import items_logger

# Load all item definitions once
_ITEM_DATA: Dict[str, Dict[str, Any]] = {}
_data_path = Path(__file__).parent / 'data' / 'items.json'
if _data_path.exists():
    try:
        _ITEM_DATA = json.loads(_data_path.read_text()).get('items', {})
        items_logger.info(f"Loaded {len(_ITEM_DATA)} items from {_data_path}")
    except Exception as e:
        items_logger.error(f"Error loading items from {_data_path}: {e}")
else:
    items_logger.warning(f"Items data file not found at {_data_path}")

class ItemFactory:
    """
    Builds Item instances by ID.
    """
    @staticmethod
    def create(item_id: str) -> Any:
        data = _ITEM_DATA.get(item_id)
        if not data:
            items_logger.warning(f"Item ID '{item_id}' not found in item data")
            null_item = ItemRegistry.get('null')
            return null_item(item_id=item_id, name="Unknown Item", description="Item not found")
        
        item_type = data.get('type', 'null')
        items_logger.debug(f"Creating item '{item_id}' of type '{item_type}'")
        
        # Auto-detect dual wield items based on slot and dual_wield flag
        if (data.get('slot') == 'offhand' or data.get('dual_wield', False)):
            if item_type == 'weapon':
                item_type = 'offhand_weapon'
                items_logger.debug(f"Adjusted item type to 'offhand_weapon' for {item_id}")
            elif item_type == 'armor' and data.get('defense', 0) > 0:
                item_type = 'shield'
                items_logger.debug(f"Adjusted item type to 'shield' for {item_id}")
        
        try:
            cls = ItemRegistry.get(item_type)
            # Pass all JSON fields as kwargs
            item = cls(item_id=item_id, **data)
            items_logger.info(f"Successfully created item '{item_id}'")
            return item
        except KeyError:
            # Fallback to base type if specialized type doesn't exist
            items_logger.warning(
                f"Item type '{item_type}' not found for {item_id}, using base type"
            )
            if 'weapon' in item_type:
                base_type = 'weapon'
            elif 'armor' in item_type or 'shield' in item_type:
                base_type = 'armor'
            else:
                base_type = 'null'
            cls = ItemRegistry.get(base_type)
            return cls(item_id=item_id, **data)
