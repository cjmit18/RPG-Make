# game_sys/inventory/inventory.py

"""
Inventory class for managing character inventory in a game.
This class allows adding, removing, equipping, unequipping, using items,
and loading templates from JSON.
"""

import uuid
import json
from logs.logs import get_logger
from pathlib import Path
from typing import TYPE_CHECKING

from game_sys.items.item_base import Item
from game_sys.items.factory import create_item
from game_sys.items.consumable_list import Consumable

if TYPE_CHECKING:
    from game_sys.character.character_creation import Character

log = get_logger(__name__)

# Path to JSON inventory templates
_TEMPLATES_PATH = Path(__file__).parent / 'data' / 'inventories.json'


def get_equip_slot(item) -> str | None:
    """Get the equipment slot for an item, if it has one.
    Returns the slot name as a string, or None if not equippable."""
    return getattr(item, 'slot', None)


def is_equippable(item) -> bool:
    """Check if an item is equippable by checking if it has a slot attribute."""
    return get_equip_slot(item) is not None


class Inventory:
    """Inventory class for managing items and equipment for a character.
    Supports adding, removing, equipping, unequipping items, and using consumables."""

    def __init__(self, owner: 'Character') -> None:
        self.owner = owner
        # _items maps item_id (uuid) → {"item": Item instance, "quantity": int}
        self._items: dict[uuid.UUID, dict[str, object]] = {}
        # Equipped slots map slot_name → item_id or None
        self._equipped_items: dict[str, uuid.UUID | None] = {
            "weapon": None,
            "shield": None,
            "offhand": None,
            "armor": None,
            "amulet": None,
            "ring": None,
            "boots": None,
            "consumable": None
        }
        # Keep item instances for equipped slots so we can remove modifiers even if
        # they’re no longer in _items
        self._equipped_item_objs: dict[str, Item] = {}

    def __str__(self) -> str:
        lines = [f"{self.owner.name}'s Inventory:"]
        if not self._items:
            lines.append("  (empty)")
        else:
            for entry in self._items.values():
                item = entry['item']
                lines.append(f"  {item.name} (x{entry['quantity']})")
        lines.append("\nEquipped:")
        for slot, item in self.equipment.items():
            name = item.name if item else "(none)"
            lines.append(f"  {slot}: {name}")
        return "\n".join(lines)

    @property
    def equipment(self) -> dict[str, Item | None]:
        """Return a mapping of slot → equipped Item instance (or None)."""
        result: dict[str, Item | None] = {}
        for slot, item_id in self._equipped_items.items():
            if item_id is None:
                result[slot] = None
            else:
                inst = self._find_item(item_id)
                result[slot] = inst or self._equipped_item_objs.get(slot)
        return result

    @property
    def equipped_items(self) -> dict[str, uuid.UUID | None]:
        """Return the raw equipped‐item IDs by slot. Used internally for loading templates."""
        return self._equipped_items

    @property
    def items(self) -> dict:
        """Expose the raw _items dict for external inspection or iteration."""
        return self._items

    @property
    def item_count(self) -> int:
        """Total count of all items (sum of quantities)."""
        return sum(entry['quantity'] for entry in self._items.values())

    def add_item(self, item, quantity: int = 1, auto_equip: bool = False) -> None:
        """
        Add an item to the inventory. If auto_equip=True, equip it immediately.
        item can be a string (item_id) or an Item instance.
        Raises KeyError if item creation fails.
        """
        # 1) If given a string, create the Item instance
        if isinstance(item, str):
            item = create_item(item)

        # 2) Increment quantity or add new slot
        if item.id in self._items:
            self._items[item.id]['quantity'] += quantity
        else:
            self._items[item.id] = {'item': item, 'quantity': quantity}

        # 3) If auto_equip, move exactly one copy from inventory into the equipped slot
        if auto_equip and is_equippable(item):
            try:
                slot = get_equip_slot(item)
                # If someone is already in that slot, unequip it first
                old_id = self._equipped_items.get(slot)
                if old_id:
                    old_item = self._equipped_item_objs.get(slot)
                    if not old_item:
                        old_item = self._find_item(old_id)
                    if old_item:
                        old_item.remove(self.owner)
                # Equip the new item
                self._equipped_items[slot] = item.id
                self._equipped_item_objs[slot] = item
                item.apply(self.owner)

                # Remove exactly one from inventory to reflect that it's now "worn"
                self.remove_item(item, 1)

            except Exception as e:
                log.warning(f"Auto-equip failed for {item}: {e}")

    def remove_item(self, item, quantity: int = 1) -> None:
        """
        Remove an item from the inventory by its ID or Item instance.
        If quantity > available, remove the slot entirely.
        Raises KeyError if item not present.
        """
        entry = None
        if isinstance(item, str):
            # item is an item_id
            entry = self._items.get(item)
        else:
            # item is an Item instance
            entry = self._items.get(item.id)

        if not entry:
            raise KeyError(f"Item {item} not in inventory")
        entry['quantity'] -= quantity
        if entry['quantity'] <= 0:
            del self._items[entry['item'].id]

    def equip_item(self, item) -> None:
        """
        Equip an item by its ID or Item instance.
        If the item is already equipped, it will be replaced.
        Raises ValueError/KeyError if invalid.
        """
        if isinstance(item, str):
            found = self._find_item(item)
            if not found:
                raise KeyError(f"Item '{item}' not found in inventory")
            item = found

        slot = get_equip_slot(item)
        if slot is None:
            raise ValueError(f"Item {item} not equippable")

        # If there is something already equipped in that slot, unequip it
        old_id = self._equipped_items.get(slot)
        if old_id:
            old_obj = self._equipped_item_objs.get(slot) or self._find_item(old_id)
            if old_obj:
                old_obj.remove(self.owner)

        # Equip this item
        self._equipped_items[slot] = item.id
        self._equipped_item_objs[slot] = item
        item.apply(self.owner)

        # Remove one copy from inventory (since it's now worn)
        self.remove_item(item, 1)
    def unequip_item(self, identifier) -> None:
        """
        Unequip an item by slot name, item ID, or Item instance, or by item name substring.
        Returns it to inventory (adds quantity=1).
        Raises ValueError/KeyError if not currently equipped.
        """
        # 1) If identifier is a slot name (e.g. "weapon"), handle directly
        if isinstance(identifier, str) and identifier in self._equipped_items:
            slot = identifier
            item_id = self._equipped_items.get(slot)
            if item_id is None:
                raise ValueError(f"No item equipped in slot '{slot}'")
            # Find the Item instance (check equipped objects first)
            item_obj = self._equipped_item_objs.get(slot)
            if item_obj is None:
                item_obj = self._find_item(item_id)
            if item_obj is None:
                # Fallback: create a new instance to apply/remove modifiers
                item_obj = create_item(item_id)

            # Remove its effects, clear the slot, and add back 1 to inventory
            item_obj.remove(self.owner)
            self._equipped_items[slot] = None
            self._equipped_item_objs.pop(slot, None)
            self.add_item(item_obj, quantity=1)
            return

        # 2) If identifier is an Item instance, find its slot
        if isinstance(identifier, Item):
            # Determine its slot
            slot = get_equip_slot(identifier)
            if slot is None or self._equipped_items.get(slot) != identifier.id:
                raise ValueError(f"Item {identifier.name} not currently equipped")
            # Unequip by delegating to slot‐based logic
            return self.unequip_item(slot)

        # 3) If identifier is a string that looks like an item ID,
        #    attempt to find which slot is holding it
        if isinstance(identifier, str):
            # Check if identifier matches any equipped slot’s item ID
            for slot, equipped_id in self._equipped_items.items():
                if equipped_id == identifier:
                    # Found the slot that holds this ID
                    return self.unequip_item(slot)

            # 4) Try matching by item name (case-insensitive substring)
            for slot, item_obj in self._equipped_item_objs.items():
                if item_obj and identifier.lower() in item_obj.name.lower():
                    return self.unequip_item(slot)

        # If we reach here, no equipped item matched
        raise KeyError(f"Item '{identifier}' not found in inventory or equipped slots")
    def use_item(self, item_ref) -> bool:
        """
        Use a consumable item by its ID or Item instance.
        Raises TypeError if item is not consumable or ValueError if not found.
        """
        if isinstance(item_ref, Item):
            item_id = getattr(item_ref, "id", None)
            if item_id is None:
                raise ValueError(f"Item {item_ref} has no ID; cannot use")
        else:
            item_id = item_ref

        item = self._find_item(item_id)
        if not item:
            raise ValueError(f"No item '{item_id}' in inventory")
        if not isinstance(item, Consumable):
            raise TypeError(f"{item.name} is not consumable")

        item.apply(self.owner)
        self.remove_item(item, 1)
        return True

    def _find_item(self, item_id: str):
        """Find an item by its ID or name in the inventory.
        Returns the Item instance if found, otherwise None."""
        for entry in self._items.values():
            if entry['item'].id == item_id or entry['item'].name == item_id:
                return entry['item']
        return None

    def load_template(self, template_name: str) -> None:
        """
        Load an inventory template from a JSON file.
        Clears current inventory and equips items as specified in the template.
        """
        with open(_TEMPLATES_PATH, 'r') as f:
            templates = json.load(f)
        entries = templates.get(template_name)
        if entries is None:
            raise KeyError(f"No inventory template '{template_name}' in {_TEMPLATES_PATH}")

        self._items.clear()
        self._equipped_items = {slot: None for slot in self._equipped_items}
        self._equipped_item_objs.clear()

        for entry in entries:
            item = create_item(entry['item_id'])
            qty = entry.get('quantity', 1)
            auto_eq = entry.get('auto_equip', False)
            self.add_item(item, quantity=qty, auto_equip=auto_eq)
