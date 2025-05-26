"""Inventory class for managing character inventory in a game.
This class allows adding, removing, equipping, unequipping, and using items."""
import uuid
import logging
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    # only for type‐hints, no runtime import
    from core.character_creation import Character
    from items.items_list import Item
log = logging.getLogger(__name__)
def get_equip_slot(item) -> str | None:
    """Returns the slot name for the given item, or None if not equippable."""
    return getattr(item, 'slot', None) 
def is_equippable(item) -> bool:
    """Return True if item can be equipped to a slot."""
    return bool(item.slot)
class Inventory:
    """Inventory class for managing character inventory in a game.
    This class allows adding, removing, equipping, unequipping, and using items."""
    def __init__(self, character) -> None:
        self.name: str = character.name
        self.character: Character = character
        self._items: dict[uuid.UUID, dict[str, object]] = {}  # <- use _items, not items
        self._equipped_items: dict[str, object] = {slot: None for slot in (
            "weapon","shield","offhand","armor","amulet","ring","boots","consumable"
        )}
    @property
    def slots(self) -> list:
         return ["weapon", "armor", "consumable","shield","amulet", "ring" ,"boots", "offhand"]
    def __str__(self) -> str:
        if not self.items:
            return f"Inventory of {self.name} is empty."
        items_str: str = "\n".join(f"{item['item'].name} x{item['quantity']}" for item in self.items.values())
        return f"{self.name}'s Inventory:\n{items_str}\n"
    def add_item(self, item, quantity=1) -> None:
        """Add an item to the inventory."""
        if item.id in self.items:
            self.items[item.id]["quantity"] += quantity
        else:
            self.items[item.id] = {"item": item, "quantity": quantity}
    def add(self, item, quantity: int = 1, auto_equip: bool = False) -> None:
        """Add an item to the inventory with optional auto-equip."""
        self.add_item(item, quantity)
        if auto_equip and is_equippable(item):
            try:
                self.equip_item(item)
            except ValueError as e:
                log.warning(f"Failed to auto-equip {item.name}: {e}")
    def remove_item(self, item, quantity=1) -> None:
        """Remove an item from the inventory."""
        if item.id not in self.items:
            raise ValueError("Item not found in inventory.")
        if self.items[item.id]["quantity"] < quantity:
            raise ValueError("Not enough quantity to remove.")
        self.items[item.id]["quantity"] -= quantity
        if self.items[item.id]["quantity"] == 0:
            del self.items[item.id]
    def check_item(self, item) -> str:
        """Check if an item is in the inventory."""
        if not isinstance(item.id, uuid.UUID):
            raise TypeError("Item ID must be of type UUID.")
        if item.id in self.items:
            log.info(f"Item {item.name} found in inventory: {self.items[item.id]}")
        else:
            log.info(f"Item {item.name} not found in inventory.")
    def check_by_name(self, name) -> None:
        """Check if an item is in the inventory by name."""
        if not isinstance(name, str):
            raise TypeError("Name must be a string.")
        found_items = [item for item in self.items.values() if item["item"].name == name]
        if found_items:
            log.info(f"Found {len(found_items)} items with name '{name}': {found_items}")
            return found_items
        else:
            log.info(f"No items found with name '{name}'.")
    def check_inventory(self) -> None:
        """Check the inventory."""
        if not self.items:
            log.info(f"Inventory of {self.name} is empty.")
        else:
            items_str: str = "\n".join(
                f"{item['item'].name} x{item['quantity']}" for item in self.items.values()
            )
            log.info(f"{self.name}'s Inventory:\n{items_str}\n") 
    def use_item(self, item) -> str:
            from items.items_list import Consumable
            """Use an item from the inventory."""
            if item.id not in self.items:
                raise ValueError("Item not found in inventory.")
            if not isinstance(item, Consumable):
                raise TypeError("Item not of type Consumable.")
            self.remove_item(item, 1)
            item.use(self.character)
            self.character.update_stats()
            log.info(f"Used {item.name}.")
    def use_by_name(self, name) -> None:
        """Use an item from the inventory by name."""
        if not isinstance(name, str):
            raise TypeError("Name must be a string.")
        found_items = [item for item in self.items.values() if item["item"].name == name]
        if found_items:
            for item in found_items:
                self.use_item(item["item"])
        else:
            raise ValueError("Item not found in inventory.")
    def use_consumable(self, item) -> None:
        """Use a consumable item from the inventory."""
        from items.items_list import Consumable
        if not isinstance(item, Consumable):
            raise TypeError("Item not of type Consumable.")
        elif item.id not in self.items:
            raise ValueError("Item not found in inventory.")
        elif item.id in self.items and self.items[item.id]["quantity"] == 0:
            raise ValueError("Item is out of stock.")
        if self.equipped_items["consumable"] is not None:
            self.use_item(self.equipped_items["consumable"])
    def drop(self, item) -> None:
        """Drop an item from the inventory."""
        if not isinstance(item, Item):
            raise TypeError("Item mitems.Item.")
        elif item.id not in self.items:
            raise ValueError("Item not found in inventory.")
        else:
            self.remove_item(item, 1)
            log.info(f"Dropped {item.name}.")
    def drop_by_name(self, name) -> None:
        """Drop an item from the inventory by name."""
        if not isinstance(name, str):
            raise TypeError("Name must be a string.")
        found_items = [item for item in self.items.values() if item["item"].name == name]
        if found_items:
            for item in found_items:
                self.drop(item["item"])
        else:
            raise ValueError("Item not found in inventory.")
    def drop_all(self) -> None:
        """Drop all items from the inventory."""
        # Check if the inventory is empty
        if not self.items:
            raise ValueError("Inventory is empty.")
        for item in list(self.items.values()):
            self.remove_item(item["item"], item["quantity"])
            if self.character.__class__.__name__ == "Player" or self.character.__class__.__name__ == "Character":
                log.info(f"{self.name} Dropped {item['item'].name}.")
    def equip_item(self, item) -> None:
        """Equip an item from the inventory."""
        matched_slot = get_equip_slot(item)
        # Check if the item is equippable
        if not matched_slot:
            log.warning(f"{item.name} is not equippable.")
            return

        # Shield/offhand conflict check
        if matched_slot == "offhand" and self.equipped_items["shield"]:
            raise ValueError("Cannot equip offhand item while shield is equipped.")
        if matched_slot == "shield" and self.equipped_items["offhand"]:
            raise ValueError("Cannot equip shield while offhand item is equipped.")
        # Check if the item is already equipped
        if self.equipped_items[matched_slot]:
            self.unequip_item(matched_slot)
        self.equipped_items[matched_slot] = item
        self.remove_item(item, 1)
        self.character.update_stats()
        log.info(f"Equipped {item.name} to {matched_slot.capitalize()} slot.")
    def equip_by_name(self, name) -> None:
        """Equip an item from the inventory by name."""
        if not isinstance(name, str):
            raise TypeError("Name must be a string.")
        found_items = [item for item in self.items.values() if item["item"].name == name]
        if found_items:
            for item in found_items:
                self.equip_item(item["item"])
        else:
            raise ValueError("Item not found in inventory.")    
    def unequip_item(self, slot) -> None:
        if slot not in self.slots:
            raise ValueError(f"Invalid slot: {slot}")
        item = self.equipped_items[slot]
        if item:
            self.add_item(item, 1)
            self.equipped_items[slot] = None
            self.character.update_stats()
            log.info(f"Unequipped {item.name} from {slot.capitalize()} slot.")
    def unequip_all(self) -> None:
        """Unequip all items from the inventory."""
        for slot in self.slots:
            if self.equipped_items[slot]:
                self.unequip_item(slot)
    def view_equipped(self) -> None:
        """View equipped items."""
        equipped_str = "\n".join(
            f"{slot.capitalize()}: {item.name if item else 'None'}" for slot, item in self.equipped_items.items()
        )
        log.info(f"Equipped Items:\n{equipped_str}\n")
    def is_equippable(item) -> bool:
        return get_equip_slot(item) is not None
    def is_equipped(self, item) -> bool:
        return item in self.equipped_items.values()
    @property
    def items(self) -> dict:
        return self._items

    @property
    def equipped_items(self) -> dict:
        return self._equipped_items

    @property
    def item_count(self) -> int:
        return sum(item["quantity"] for item in self.items.values())