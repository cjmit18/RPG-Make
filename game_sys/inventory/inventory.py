# game_sys/inventory/inventory.py

import uuid
import json
from logs.logs import get_logger
from pathlib import Path
from typing import TYPE_CHECKING, Optional, Union, Dict, Any, List

from game_sys.items.item_base import Item
from game_sys.items.factory import create_item
from game_sys.items.consumable_list import Consumable

if TYPE_CHECKING:
    from game_sys.character.character_creation import Character

log = get_logger(__name__)

# Path to JSON inventory templates
_TEMPLATES_PATH = Path(__file__).parent / "data" / "inventories.json"


def get_equip_slot(item: Item) -> Optional[str]:
    """
    Return the item’s primary equipment slot (e.g. "weapon", "shield", "armor", etc.).
    We do NOT force offhand here; offhand‐eligible items are handled in equip_item().
    """
    return getattr(item, "slot", None)


def is_equippable(item: Item) -> bool:
    """Check if an item is equippable (has a 'slot' attribute)."""
    return get_equip_slot(item) is not None


class Inventory:
    """
    Inventory class for managing a character's items:

      - self._items: maps item_id (UUID or str) → {"item": Item, "quantity": int}
      - self._equipped_items: slot_name → item_id (UUID or str) or None
      - self._equipped_item_objs: slot_name → Item instance or None
    """

    def __init__(self, owner: "Character") -> None:
        self.owner = owner
        self._items: Dict[uuid.UUID | str, Dict[str, Any]] = {}
        self._equipped_items: Dict[str, uuid.UUID | str | None] = {
            "weapon": None,
            "offhand": None,
            "shield": None,
            "armor": None,
            "amulet": None,
            "ring": None,
            "boots": None,
            "consumable": None,
        }
        self._equipped_item_objs: Dict[str, Optional[Item]] = {
            slot: None for slot in self._equipped_items
        }

    def __str__(self) -> str:
        """
        Show (1) all items in stash, then (2) all equipped slots
        in a fixed order: weapon → offhand → shield → armor → amulet → ring → boots → consumable.
        """
        lines: List[str] = []

        # 1) List all items in inventory._items
        if not self._items:
            lines.append("  (empty)")
        else:
            for item_id, entry in self._items.items():
                item_obj = entry["item"]
                qty = entry["quantity"]
                lines.append(f"  {item_obj.name} (x{qty})")

        # 2) Now list “Equipped:” header + slots in the fixed order
        lines.append("")  # blank line before “Equipped:”
        lines.append("Equipped:")
        order = [
            "weapon",
            "offhand",
            "shield",
            "armor",
            "amulet",
            "ring",
            "boots",
            "consumable",
        ]
        for slot in order:
            equipped_obj = self._equipped_item_objs.get(slot)
            if equipped_obj:
                lines.append(f"  {slot}: {equipped_obj.name}")
            else:
                lines.append(f"  {slot}: (none)")

        return "\n".join(lines)

    @property
    def equipment(self) -> Dict[str, Optional[Item]]:
        """
        Return a dict mapping slot → equipped Item instance (or None).
        """
        result: Dict[str, Optional[Item]] = {}
        for slot, item_id in self._equipped_items.items():
            if item_id is None:
                result[slot] = None
            else:
                inst = self._find_item(item_id)
                result[slot] = inst or self._equipped_item_objs.get(slot)
        return result

    @property
    def equipped_items(self) -> Dict[str, uuid.UUID | str | None]:
        """
        Return raw equipped‐item IDs by slot (useful for saving/loading).
        """
        return self._equipped_items

    @property
    def items(self) -> Dict[uuid.UUID | str, Dict[str, Any]]:
        """
        Expose the raw _items dict for inspection.
        """
        return self._items

    @property
    def item_count(self) -> int:
        """
        Total count of all items (sum of quantities).
        """
        return sum(entry["quantity"] for entry in self._items.values())

    def add_item(self, item: Union[str, Item], quantity: int = 1, auto_equip: bool = False) -> None:
        """
        Add an item to the inventory. If auto_equip=True and the item is equippable, equip immediately.
        'item' can be a string (item_id) or an Item instance.
        Raises KeyError if creation fails.
        """
        # 1) If given a string, create the Item instance
        if isinstance(item, str):
            item = create_item(item)

        # 2) Increment quantity or add new slot
        iid = item.id
        if iid in self._items:
            self._items[iid]["quantity"] += quantity
        else:
            self._items[iid] = {"item": item, "quantity": quantity}

        log.info("Added %d× %s (ID=%s) to %s's inventory.", quantity, item.name, item.id, self.owner.name)

        # 3) If auto_equip, equip now (without removing from inventory)
        if auto_equip and is_equippable(item):
            try:
                self.equip_item(item.id)
            except Exception as e:
                log.warning("Auto-equip failed for %s (ID=%s): %s", item.name, item.id, e)

    def remove_item(self, item: Union[str, Item], quantity: int = 1) -> None:
        """
        Remove up to `quantity` copies of the specified item from inventory.
        `item` can be an Item instance or an item_id string.
        Raises KeyError if not enough copies exist.
        """
        entry = None
        if isinstance(item, Item):
            entry = self._items.get(item.id)
        else:
            entry = self._items.get(item)

        if not entry or entry["quantity"] < quantity:
            raise KeyError(f"Not enough copies of '{item}' to remove")
        entry["quantity"] -= quantity
        if entry["quantity"] <= 0:
            del self._items[entry["item"].id]

        log.info("Removed %d× %s from %s's inventory.", quantity, item if isinstance(item, str) else item.id, self.owner.name)

    def _find_item(self, item_id: uuid.UUID | str) -> Optional[Item]:
        """
        Find an item by its item_id. Return Item instance or None.
        """
        entry = self._items.get(item_id)
        return entry["item"] if entry else None

    def equip_item(self, item_ref: Union[str, Item], slot: Optional[str] = None) -> None:
        """
        Equip a consumable or equipable by its object or ID:
          1) If slot is given, force that slot (e.g. "offhand" or "weapon").
          2) Otherwise, try primary = get_equip_slot(item). If primary is free, use it.
             If primary is occupied and item.offhand==True and offhand is free, use "offhand".
             Else: ValueError.
        Then:
          - Remove one copy from self._items
          - Place item.ID in self._equipped_items[slot_to_use]
          - Call owner.stats.add_modifier(...) for each bonus in item.bonuses,
            using a unique modifier key = f"{item.id}_{slot_to_use}"
        """
        # 1) Resolve item_ref → actual Item instance
        if isinstance(item_ref, Item):
            item_obj = item_ref
        else:
            inv_entry = self._items.get(item_ref)
            if not inv_entry:
                raise KeyError(f"No such item '{item_ref}' in inventory")
            item_obj = inv_entry["item"]

        # 2) Determine primary slot
        primary = get_equip_slot(item_obj)
        if primary is None:
            raise ValueError(f"Item '{item_obj.name}' (ID={item_obj.id}) not equippable")

        # 3) Decide final slot_to_use
        if slot:
            slot_to_use = slot
        else:
            if self._equipped_items.get(primary) is None:
                slot_to_use = primary
            else:
                # primary is occupied; check offhand fallback
                if getattr(item_obj, "offhand", False) and self._equipped_items.get("offhand") is None:
                    # If item is offhand-eligible and offhand is free, use it
                    slot_to_use = "offhand"
                else:
                    self.unequip_item(primary)  # Unequip primary slot
                    slot_to_use = primary  # Now we can use primary

        # 4) Remove one copy from inventory._items
        inv_entry = self._items.get(item_obj.id)
        if not inv_entry or inv_entry["quantity"] < 1:
            raise KeyError(f"No copies of '{item_obj.name}' to equip")
        inv_entry["quantity"] -= 1
        if inv_entry["quantity"] == 0:
            del self._items[item_obj.id]

        # 5) Place the item into the chosen slot
        self._equipped_items[slot_to_use] = item_obj.id
        self._equipped_item_objs[slot_to_use] = item_obj

        # 6) Add its bonuses to owner.stats, using a unique modifier key
        mod_key = f"{item_obj.id}_{slot_to_use}"
        for stat_name, amount in getattr(item_obj, "bonuses", {}).items():
            self.owner.stats.add_modifier(mod_key, stat_name, int(amount))

        log.info("%s equipped '%s' into slot '%s'.", self.owner.name, item_obj.name, slot_to_use)

    def unequip_item(self, slot_or_identifier: str) -> None:
        """
        Unequip an item either by passing a slot name (e.g. "weapon", "offhand")
        or by passing the item-ID or a substring of the item’s name.

        Steps:
          1) Figure out which slot to unequip using slot_or_identifier.
          2) Remove stats modifiers via owner.stats.remove_modifier(f"{item_id}_{slot}").
          3) Delete from _equipped_items/_equipped_item_objs and restore one copy to _items.
        """
        # 1A) If exact slot name given, use it
        if slot_or_identifier in self._equipped_items:
            slot = slot_or_identifier
        else:
            # 1B) Otherwise, try to match against equipped Item IDs or name substrings
            needle = slot_or_identifier.lower()
            found_slot = None
            for s, obj in self._equipped_item_objs.items():
                if obj is None:
                    continue
                # Match if ID matches exactly
                if obj.id == slot_or_identifier:
                    found_slot = s
                    break
                # Or if substring of the name matches
                if needle in obj.name.lower():
                    found_slot = s
                    break
            if found_slot is None:
                raise KeyError(f"No equipped item matching '{slot_or_identifier}'")
            slot = found_slot

        # 2) Get the Item instance & its ID
        equipped_id = self._equipped_items.get(slot)
        equipped_obj = self._equipped_item_objs.get(slot)
        if equipped_id is None or equipped_obj is None:
            raise KeyError(f"No item equipped in slot '{slot}'")

        # 3) Remove stat modifiers for that item (using the unique modifier key)
        mod_key = f"{equipped_id}_{slot}"
        try:
            self.owner.stats.remove_modifier(mod_key)
        except Exception:
            pass  # ignore if not present

        # 4) Remove from equipped dicts
        del self._equipped_items[slot]
        del self._equipped_item_objs[slot]

        # 5) Return one copy to inventory._items
        entry = self._items.get(equipped_id)
        if entry:
            entry["quantity"] += 1
        else:
            self._items[equipped_id] = {"item": equipped_obj, "quantity": 1}

        log.info("%s unequipped '%s' from slot '%s'.", self.owner.name, equipped_obj.name, slot)

    def use_item(self, item_ref: Union[str, Item]) -> bool:
        """
        Use a consumable item by its ID or Item instance.
        Raises TypeError if item is not consumable or ValueError if not found.
        """
        if isinstance(item_ref, Item):
            item_id = getattr(item_ref, "id", None)
            if item_id is None:
                raise ValueError(f"Item {item_ref} has no ID; cannot use")
        else:
            item_id = uuid.UUID(item_ref) if self._is_uuid(item_ref) else None
        if not item_id:
            raise ValueError(f"Invalid item reference '{item_ref}'")

        item = self._find_item(item_id)
        if not item:
            raise ValueError(f"No item '{item_ref}' in inventory")
        if not isinstance(item, Consumable):
            raise TypeError(f"{item.name} is not consumable")

        item.apply(self.owner)
        self.remove_item(item, 1)
        log.info(f"{self.owner.name} used {item.name}.")
        return True

    def load_template(self, template_name: str) -> None:
        """
        Load an inventory template from a JSON file under 'data/inventories.json'.
        Clears current inventory and equips items as specified in the template.
        """
        with open(_TEMPLATES_PATH, "r") as f:
            templates = json.load(f)
        entries = templates.get(template_name)
        if entries is None:
            raise KeyError(f"No inventory template '{template_name}' in {_TEMPLATES_PATH}")

        # Clear current inventory & equipment
        self._items.clear()
        self._equipped_items = {slot: None for slot in self._equipped_items}
        self._equipped_item_objs = {slot: None for slot in self._equipped_items}

        for entry in entries:
            itm = create_item(entry["item_id"])
            qty = entry.get("quantity", 1)
            auto_eq = entry.get("auto_equip", False)
            self.add_item(itm, quantity=qty, auto_equip=auto_eq)

        log.info("Loaded inventory template '%s' for %s.", template_name, self.owner.name)

    @staticmethod
    def _is_uuid(value: str) -> bool:
        """Return True if a string is a valid UUID."""
        try:
            uuid.UUID(value)
            return True
        except Exception:
            return False
