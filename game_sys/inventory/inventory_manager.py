# game_sys/inventory/inventory_manager.py
"""
Module: game_sys.inventory.inventory_manager

Manages an actor's inventory: adding, removing, stacking items.
"""
from game_sys.config.config_manager import ConfigManager
from game_sys.hooks.hooks_setup import emit, ON_ITEM_USED

class InventoryManager:
    def __init__(self, actor: any):
        cfg = ConfigManager()
        self.actor = actor
        self.max_size = cfg.get('constants.inventory.max_size', 20)
        self.items: list[any] = []

    def add_item(self, item: any) -> bool:
        """Add an item if space permits; return True if added."""
        if len(self.items) >= self.max_size:
            return False
        self.items.append(item)
        return True

    def remove_item(self, item: any) -> bool:
        """Remove an item; return True if removed."""
        if item in self.items:
            self.items.remove(item)
            return True
        return False

    def find(self, item_id: str) -> any:
        """Return the first item matching the given ID, or None."""
        for itm in self.items:
            if getattr(itm, 'id', None) == item_id:
                return itm
        return None

    def list_items(self) -> list[any]:
        """List all current inventory items."""
        return list(self.items)
