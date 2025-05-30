"""Inventory class for managing character inventory in a game.
This class allows adding, removing, equipping, unequipping, using items,
 and loading templates from JSON."""
import uuid
import logging
import json
from pathlib import Path
from typing import TYPE_CHECKING
from game_sys.items.item_base import Item
from game_sys.items.factory import create_item
from game_sys.items.consumable_list import Consumable
if TYPE_CHECKING:
    from game_sys.core.character.character_creation import Character

log = logging.getLogger(__name__)

# Path to JSON inventory templates
_TEMPLATES_PATH = Path(__file__).parent / 'data' / 'inventories.json'

def get_equip_slot(item) -> str | None:
    return getattr(item, 'slot', None)

def is_equippable(item) -> bool:
    return get_equip_slot(item) is not None

class Inventory:
    def __init__(self, owner: 'Character') -> None:
        self.owner = owner
        self._items: dict[uuid.UUID, dict[str, object]] = {}
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
        # Store equipped instances so equipment() can show them even if removed from items
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
        """
        Return the raw equipped‐item IDs by slot. 
        Used internally for loading templates.
        """
        return self._equipped_items
    @property
    def items(self) -> dict:
        return self._items

    @property
    def item_count(self) -> int:
        return sum(entry['quantity'] for entry in self._items.values())

    def add_item(self, item, quantity: int = 1, auto_equip: bool = False) -> None:
        if isinstance(item, str):
            item = create_item(item)
        if item.id in self._items:
            self._items[item.id]['quantity'] += quantity
        else:
            self._items[item.id] = {'item': item, 'quantity': quantity}
        if auto_equip and is_equippable(item):
            try:
                slot = get_equip_slot(item)
                old_id = self._equipped_items.get(slot)
                if old_id:
                    old_item = self._items.get(old_id, {}).get("item")
                    if old_item:
                        old_item.remove(self.owner)
                self._equipped_items[slot] = item.id
                self._equipped_item_objs[slot] = item
                item.apply(self.owner)
            except Exception as e:
                log.warning(f"Auto‑equip failed for {item}: {e}")

    def remove_item(self, item, quantity: int = 1) -> None:
        entry = self._items.get(item.id)
        if not entry:
            raise KeyError(f"Item {item} not in inventory")
        entry['quantity'] -= quantity
        if entry['quantity'] <= 0:
            del self._items[item.id]

    def equip_item(self, item) -> None:
        if isinstance(item, str):
            found = self._find_item(item)
            if not found:
                raise KeyError(f"Item '{item}' not found in inventory")
            item = found
        slot = get_equip_slot(item)
        if slot is None:
            raise ValueError(f"Item {item} not equippable")
        old_id = self._equipped_items.get(slot)
        if old_id:
            old_obj = self._equipped_item_objs.get(slot) or self._find_item(old_id)
            if old_obj:
                old_obj.remove(self.owner)
        self._equipped_items[slot] = item.id
        self._equipped_item_objs[slot] = item
        item.apply(self.owner)
        self.remove_item(item, 1)

    def unequip_item(self, identifier) -> None:
        if isinstance(identifier, str) and identifier in self._equipped_items:
            slot = identifier
            item_id = self._equipped_items.get(slot)
            if item_id is None:
                raise ValueError(f"No item equipped in slot '{slot}'")
            entry = self._items.get(item_id)
            if entry:
                item_obj = entry['item']
            else:
                item_obj = create_item(item_id)
            item_obj.remove(self.owner)
            self._equipped_items[slot] = None
            self._equipped_item_objs.pop(slot, None)
            self.add_item(item_obj, quantity=1)
            return
        if isinstance(identifier, Item):
            item = identifier
        else:
            found = self._find_item(identifier)
            if not found:
                raise KeyError(f"Item '{identifier}' not found in inventory")
            item = found
        slot = get_equip_slot(item)
        if slot is None:
            raise ValueError(f"Item {item} not equippable")
        if self._equipped_items.get(slot) != item.id:
            raise ValueError(f"Item {item} not currently equipped in {slot}")
        item.remove(self.owner)
        self._equipped_items[slot] = None
        self._equipped_item_objs.pop(slot, None)
        self.add_item(item, quantity=1)

    def use_item(self, item_ref) -> bool:
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
        for entry in self._items.values():
            if entry['item'].id == item_id or entry['item'].name == item_id:
                return entry['item']
        return None

    def load_template(self, template_name: str) -> None:
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
