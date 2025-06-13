# game_sys/inventory/inventory.py

"""
Inventory module: manages an actor's collection of items, equipment, and consumables.
Enhanced to support dual-wielding and proper offhand unequip logic.
"""

from __future__ import annotations
from typing import Any, Dict, List, Optional, Union
from logs.logs import get_logger
from game_sys.items.item_base import Item, EquipableItem, ConsumableItem
from game_sys.items.factory import create_item, _TEMPLATES
from game_sys.core.hooks import hook_dispatcher
from game_sys.core.equipment_slot import EquipmentSlot

log = get_logger(__name__)


class Inventory:
    """
    Represents a character's inventory, handling item storage, equip/unequip, usage,
    and item lookup/equip by ID. Supports dual-wield for weapons and
    ensures offhand items are unequipped when equipping two-handed weapons.
    """

    def __init__(self, owner: Any) -> None:
        self.owner = owner
        self._items: Dict[str, Dict[str, Any]] = {}
        self.equipped_items: Dict[str, EquipableItem] = {}

    def add_item(
        self,
        item: Union[str, Item],
        quantity: int = 1,
        auto_equip: bool = False
    ) -> None:
        if isinstance(item, str):
            item_obj = create_item(item)
        else:
            item_obj = item

        entry = self._items.get(item_obj.id)
        if entry:
            entry['quantity'] += quantity
        else:
            self._items[item_obj.id] = {'item': item_obj, 'quantity': quantity}

        log.info(
            "Added %dx %s (ID=%s) to %s's inventory.",
            quantity, item_obj.name, item_obj.id, self.owner.name
        )
        hook_dispatcher.fire(
            "inventory.item_added", inventory=self, item=item_obj, quantity=quantity
        )

        if auto_equip and isinstance(item_obj, EquipableItem):
            self.equip_item(item_obj)

    def remove_item(self, item: Union[str, Item], quantity: int = 1) -> None:
        item_id = item.id if isinstance(item, Item) else item
        entry = self._items.get(item_id)
        if not entry or entry['quantity'] < quantity:
            raise KeyError(f"Not enough copies of '{item_id}' to remove")
        entry['quantity'] -= quantity
        if entry['quantity'] <= 0:
            del self._items[item_id]

        log.info(
            "Removed %dx %s from %s's inventory.",
            quantity, item_id, self.owner.name
        )
        hook_dispatcher.fire(
            "inventory.item_removed", inventory=self, item_id=item_id, quantity=quantity
        )

    def view_item_by_id(self, item_id: str) -> Optional[Item]:
        entry = self._items.get(item_id)
        return entry['item'] if entry else None

    def equip_item(self, item_ref: Union[str, EquipableItem]) -> None:
        # Resolve item_obj
        if isinstance(item_ref, str):
            entry = self._items.get(item_ref)
            if not entry:
                log.warning("No item '%s' to equip.", item_ref)
                return
            item_obj = entry['item']
        else:
            item_obj = item_ref
            if item_obj.id not in self._items:
                log.warning("Item '%s' not in inventory.", item_obj.id)
                return

        if not isinstance(item_obj, EquipableItem):
            log.warning("Item '%s' is not equipable.", item_obj.id)
            return

        # Determine offhand capability (fallback to template if attribute missing)
        try:
            can_offhand = item_obj.offhand
        except AttributeError:
            can_offhand = _TEMPLATES.get(item_obj.id, {}).get('offhand', False)

        # Choose slot key based on item.slot
        base_slot = item_obj.slot.lower()
        # Determine equip slot
        if base_slot == EquipmentSlot.WEAPON.name.lower():
            if can_offhand:
                # One-handed: primary if free, else offhand if free, else primary
                if 'weapon' not in self.equipped_items:
                    equip_slot = 'weapon'
                elif 'offhand' not in self.equipped_items:
                    equip_slot = 'offhand'
                else:
                    equip_slot = 'weapon'
            else:
                # Two-handed: clear offhand then equip primary
                if 'offhand' in self.equipped_items:
                    self.unequip_item('offhand')
                equip_slot = 'weapon'
        else:
            # Non-weapon slots equip directly
            equip_slot = base_slot

        # Perform equip
        prev = self.equipped_items.get(equip_slot)
        if prev is item_obj:
            return
        if prev is not None:
            self.unequip_item(equip_slot)

        self.equipped_items[equip_slot] = item_obj
        log.info(
            "%s equipped '%s' into slot '%s'.",
            self.owner.name, item_obj.name, equip_slot
        )
        hook_dispatcher.fire(
            "inventory.equip", inventory=self, slot=equip_slot, item=item_obj
        )

    def unequip_item(self, slot: str) -> None:
        item = self.equipped_items.pop(slot, None)
        if not item:
            return
        log.info(
            "%s unequipped '%s' from slot '%s'.",
            self.owner.name, item.name, slot
        )
        hook_dispatcher.fire(
            "inventory.unequip", inventory=self, slot=slot, item=item
        )

    def use_item(self, item_ref: Union[str, Item]) -> bool:
        if isinstance(item_ref, str):
            entry = self._items.get(item_ref)
            item_obj = entry['item'] if entry else None
        else:
            item_obj = item_ref
            entry = self._items.get(item_obj.id)

        if not entry or entry['quantity'] < 1:
            raise ValueError(f"No item '{item_ref}' in inventory")
        if not isinstance(item_obj, ConsumableItem):
            raise TypeError(f"Item '{item_obj.id}' is not consumable")

        result = item_obj.apply(self.owner, None)
        self.remove_item(item_obj.id, 1)
        log.info(
            "%s used %s.", self.owner.name, item_obj.name
        )
        hook_dispatcher.fire(
            "inventory.item_used", inventory=self, item=item_obj
        )
        return True

    def list_items(self) -> List[Item]:
        return [entry['item'] for entry in self._items.values()]

    def __str__(self) -> str:
        lines: List[str] = [f"Inventory of {self.owner.name}"]
        if not self._items:
            lines.append("    - (empty)")
        else:
            for item_id, entry in self._items.items():
                lines.append(f"    - {entry['item'].name} (ID={item_id}, Qty={entry['quantity']})")
        if self.equipped_items:
            lines.append("Equipped items:")
            for slot, itm in self.equipped_items.items():
                lines.append(f"    - {slot}: {itm.name} (ID={itm.id})")
        else:
            lines.append("Equipped items: (none)")
        return "\n".join(lines)
