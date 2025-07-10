# game_sys/inventory/inventory_manager.py
"""
Module: game_sys.inventory.inventory_manager

Manages an actor's inventory: adding, removing, stacking items.
"""
from typing import Any, List, Optional
from game_sys.config.config_manager import ConfigManager
from game_sys.logging import inventory_logger, log_exception


class InventoryManager:
    def __init__(self, actor: Any):
        cfg = ConfigManager()
        self.actor = actor
        self.max_size = cfg.get('constants.inventory.max_size', 20)
        self.items: List[Any] = []
        inventory_logger.info(
            f"Initialized {actor.name} inventory (max size: {self.max_size})"
        )

    # --- ASYNC HOOKS: can be monkey-patched or subclassed --- #
    async def on_pre_add_item(self, item: Any):
        """Async hook before adding item. Override for effects, UI, etc."""
        from game_sys.hooks.hooks_setup import emit_async, ON_PRE_ADD_ITEM
        await emit_async(ON_PRE_ADD_ITEM, actor=self.actor, item=item)

    async def on_post_add_item(self, item: Any, success: bool):
        """Async hook after adding item. Override for effects, UI, etc."""
        from game_sys.hooks.hooks_setup import emit_async, ON_POST_ADD_ITEM
        await emit_async(ON_POST_ADD_ITEM, actor=self.actor, item=item, success=success)

    async def on_pre_remove_item(self, item: Any):
        """Async hook before removing item. Override for effects, UI, etc."""
        from game_sys.hooks.hooks_setup import emit_async, ON_PRE_REMOVE_ITEM
        await emit_async(ON_PRE_REMOVE_ITEM, actor=self.actor, item=item)

    async def on_post_remove_item(self, item: Any, success: bool):
        """Async hook after removing item. Override for effects, UI, etc."""
        from game_sys.hooks.hooks_setup import emit_async, ON_POST_REMOVE_ITEM
        await emit_async(ON_POST_REMOVE_ITEM, actor=self.actor, item=item, success=success)

    async def add_item_async(self, item: Any) -> bool:
        """Async version of add_item with awaitable hooks/effects."""
        await self.on_pre_add_item(item)
        result = self.add_item(item)
        await self.on_post_add_item(item, result)
        return result

    async def remove_item_async(self, item: Any) -> bool:
        """Async version of remove_item with awaitable hooks/effects."""
        await self.on_pre_remove_item(item)
        result = self.remove_item(item)
        await self.on_post_remove_item(item, result)
        return result

    @log_exception
    def get_item_quantity(self, item: Any) -> int:
        """Get the quantity of a specific item type in the inventory."""
        count = 0
        item_id = getattr(item, 'id', None)
        if item_id is None:
            inventory_logger.warning(
                f"Cannot get quantity for item without id: {item}"
            )
            return 0
            
        for inv_item in self.items:
            if getattr(inv_item, 'id', None) == item_id:
                count += 1
        return count

    @log_exception
    def clear(self):
        """Remove all items from inventory."""
        count = len(self.items)
        self.items = []
        inventory_logger.info(
            f"Cleared {count} items from {self.actor.name}'s inventory"
        )

    @log_exception
    def add_item(self,
                item: Any,
                quantity: int = 1,
                auto_equip: bool = True) -> bool:
        """
        Add items if space permits. Each item instance must have a unique UUID.
        If auto_equip and quantity=1, attempts to equip equipable items ONLY if slot is empty.
        """
        item_name = getattr(item, 'name', str(item))
        # Check space available
        space_needed = quantity
        if isinstance(self.max_size, (int, float)):
            if len(self.items) + space_needed > self.max_size:
                available = self.max_size - len(self.items)
                inventory_logger.warning(
                    f"Cannot add {quantity}x {item_name}: "
                    f"need {space_needed} slots, {available} available"
                )
                return False
        # Add the items (each with a unique UUID)
        for _ in range(quantity):
            if not hasattr(item, 'uuid'):
                import uuid as _uuid
                item.uuid = str(_uuid.uuid4())
            self.items.append(item)
        inventory_logger.info(
            f"Added {quantity}x {item_name} to {self.actor.name}'s inventory"
        )
        # Auto-equip logic if enabled and quantity is 1
        if auto_equip and quantity == 1 and hasattr(item, 'slot'):
            slot = item.slot
            slot_empty = False
            if slot == 'weapon':
                slot_empty = getattr(self.actor, 'weapon', None) is None
            elif slot == 'offhand':
                slot_empty = getattr(self.actor, 'offhand', None) is None
            elif slot in ['body', 'helmet', 'legs', 'feet']:
                slot_empty = getattr(self.actor, f'equipped_{slot}', None) is None
            if slot_empty:
                if slot == 'weapon' and hasattr(self.actor, 'equip_weapon'):
                    self.actor.equip_weapon(item)
                elif slot == 'offhand' and hasattr(self.actor, 'equip_offhand'):
                    self.actor.equip_offhand(item)
                elif slot in ['body', 'helmet', 'legs', 'feet'] and hasattr(self.actor, 'equip_armor'):
                    self.actor.equip_armor(item)
        return True

    @log_exception
    def remove_item(self, item: Any) -> bool:
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

    def find(self, item_id: str) -> Optional[Any]:
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

    def list_items(self) -> List[Any]:
        """List all current inventory items."""
        inventory_logger.debug(
            f"Listing {len(self.items)} items in {self.actor.name}'s inventory"
        )
        return list(self.items)
