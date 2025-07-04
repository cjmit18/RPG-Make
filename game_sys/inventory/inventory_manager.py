# game_sys/inventory/inventory_manager.py
"""
Module: game_sys.inventory.inventory_manager

Manages an actor's inventory: adding, removing, stacking items.
"""
from game_sys.config.config_manager import ConfigManager
from game_sys.hooks.hooks_setup import emit, ON_ITEM_USED
from game_sys.logging import inventory_logger, log_exception

class InventoryManager:
    def __init__(self, actor: any):
        cfg = ConfigManager()
        self.actor = actor
        self.max_size = cfg.get('constants.inventory.max_size', 20)
        self.items: list[any] = []
        inventory_logger.info(
            f"Initialized inventory for {actor.name} with max size {self.max_size}"
        )

    @log_exception
    def add_item(self, item: any) -> bool:
        """Add an item if space permits; return True if added."""
        item_name = getattr(item, 'name', str(item))
        if len(self.items) >= self.max_size:
            inventory_logger.warning(
                f"Cannot add {item_name} to {self.actor.name}'s inventory: full"
            )
            return False
        self.items.append(item)
        inventory_logger.info(
            f"Added {item_name} to {self.actor.name}'s inventory"
        )
        return True

    @log_exception
    def remove_item(self, item: any) -> bool:
        """Remove an item; return True if removed."""
        item_name = getattr(item, 'name', str(item))
        if item in self.items:
            self.items.remove(item)
            inventory_logger.info(
                f"Removed {item_name} from {self.actor.name}'s inventory"
            )
            return True
        inventory_logger.warning(
            f"Cannot remove {item_name}: not in {self.actor.name}'s inventory"
        )
        return False

    def find(self, item_id: str) -> any:
        """Return the first item matching the given ID, or None."""
        for itm in self.items:
            if getattr(itm, 'id', None) == item_id:
                inventory_logger.debug(
                    f"Found item {item_id} in {self.actor.name}'s inventory"
                )
                return itm
        inventory_logger.debug(
            f"Item {item_id} not found in {self.actor.name}'s inventory"
        )
        return None

    def list_items(self) -> list[any]:
        """List all current inventory items."""
        inventory_logger.debug(
            f"Listing {len(self.items)} items in {self.actor.name}'s inventory"
        )
        return list(self.items)
