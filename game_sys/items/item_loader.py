# game_sys/items/item_loader.py
"""
Module: game_sys.items.item_loader

Public API to load items by ID.
"""
from game_sys.items.factory import ItemFactory
from game_sys.logging import items_logger, log_exception


@log_exception
def load_item(item_id: str):
    """
    Return an Item instance for the given ID.
    """
    items_logger.debug(f"Loading item: {item_id}")
    item = ItemFactory.create(item_id)
    if item:
        items_logger.info(f"Successfully loaded item: {item.name} ({item_id})")
    else:
        items_logger.warning(f"Failed to load item: {item_id}")
    return item
