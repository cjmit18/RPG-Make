# game_sys/items/item_loader.py
"""
Module: game_sys.items.item_loader

Public API to load items by ID.
"""
from game_sys.items.factory import ItemFactory


def load_item(item_id: str):
    """
    Return an Item instance for the given ID.
    """
    return ItemFactory.create(item_id)
