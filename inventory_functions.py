
"""Inventory class for managing character inventory in a game.
This class allows adding, removing, equipping, unequipping, and using items."""
import character_creation
import items_list
import weapon_list as weapons
import armor_list as armors
import potion_list as potions
import uuid
import logging
logging.basicConfig(level=logging.INFO)
log = logging.getLogger()
class Inventory:
    """Inventory class for managing character inventory in a game.
    This class allows adding, removing, equipping, unequipping, and using items."""
    def __init__(self,character) -> None:
        self.name: str = character.name  
        self.character: character_creation.Character = character
        self.items: dict[uuid.UUID, dict["item": items_list.Item, "quantity": int]] = {}
        self.slots: list = ["weapon", "armor", "consumable","shield","amulet", "ring" ,"boots"]
        self.equipped_items: dict = {
            "weapon": None,
            "armor": None,
            "shield": None,
            "consumable": None,
            "amulet": None,
            "ring": None,
            "boots": None,
        }
    def __str__(self) -> str:
        if not self.items:
            return f"Inventory of {self.name} is empty."
        else:
            items_str: str = "\n".join(
                f"{item['item'].name} x{item['quantity']}" for item in self.items.values()
            )
            return f"{self.name}'s Inventory:\n{items_str}\n"
    def __repr__(self) -> str:
        if not self.items:
            return f"Inventory: ({self.name}, empty)"
        else:
            return f"Inventory: ({self.name}, {self.items})"
    def add_item(self, item, quantity=1) -> None:
        """Add an item to the inventory."""
        if not isinstance(item.id, uuid.UUID):
            raise TypeError("Item ID must be of type UUID.")
        elif not isinstance(quantity, int):
            raise TypeError("Quantity must be an integer.")
        elif quantity <= 0:
            raise ValueError("Quantity must be greater than 0.")
        elif item.id in self.items:
            self.items[item.id]["quantity"] += quantity
        else:
            self.items[item.id] = {"item": item, "quantity": quantity}
    def remove_item(self, item, quantity=1) -> None:
        """Remove an item from the inventory."""
        if not isinstance(item.id, uuid.UUID):
            raise TypeError("Item ID must be of type UUID.")
        elif not isinstance(quantity, int):
            raise TypeError("Quantity must be an integer.")
        elif quantity <= 0:
            raise ValueError("Quantity must be greater than 0.")
        elif item.id not in self.items:
            raise ValueError("Item not found in inventory.")
        elif self.items[item.id]["quantity"] < quantity:
            raise ValueError("Not enough quantity to remove.")
        else:
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
            """Use an item from the inventory."""
            if not isinstance(item.id, uuid.UUID):
                raise TypeError("Item ID must be of type UUID.")
            if isinstance(item, potions.Potion):
                if item.effect == "health":
                            self.character._health += item.amount
                elif item.effect == "mana":
                            self.character._mana += item.amount
                elif item.effect == "stamina":
                            self.character._stamina += item.amount
                elif item.effect == "speed":
                            self.character._speed += item.amount
                log.info( f"Used {item.name}. Effect: Increase {item.effect} by {item.amount}.")
                self.remove_item(item, 1)
                
            else:
                raise ValueError("Item not found in inventory")
                
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
        if not isinstance(item, items_list.Consumable):
            raise TypeError("Item not of type Consumable.")
        elif item.id not in self.items:
            raise ValueError("Item not found in inventory.")
        elif item.id in self.items and self.items[item.id]["quantity"] == 0:
            raise ValueError("Item is out of stock.")
        if self.equipped_items["consumable"] is not None:
            self.use_item(self.equipped_items["consumable"])
    def drop(self, item) -> None:
        """Drop an item from the inventory."""
        if not isinstance(item, items_list.Item):
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
        if not self.items:
            raise ValueError("Inventory is empty.")
        for item in list(self.items.values()):
            self.remove_item(item["item"], item["quantity"])
            if self.character.__class__.__name__ == "Player" or self.character.__class__.__name__ == "Character":
                log.info(f"{self.name} Dropped {item['item'].name}.")
    def equip_item(self, item) -> None:
        """Equip an item from the inventory."""
        if not isinstance(item.id, uuid.UUID):
            raise TypeError("Item ID must be of type UUID.")
        elif item.id not in self.items:
            raise ValueError("Item not found in inventory.")
        elif item.id in self.items and self.items[item.id]["quantity"] == 0:
            raise ValueError("Item is out of stock.")
        if isinstance(item, weapons.Weapon):
            if self.items[item.id]["quantity"]> 0:
                self.equipped_items["weapon"] = item
                self.remove_item(item, 1)
                log.info(f"Equipped {item.name} as {"Weapon"}.")
        elif isinstance(item, armors.Armor) and not isinstance(item, armors.Shield):
            if self.items[item.id]["quantity"]> 0:
                self.equipped_items["armor"] = item
                self.remove_item(item, 1)
                log.info(f"Equipped {item.name} as {"Armor"}.")
        elif isinstance(item, armors.Shield):
            if self.items[item.id]["quantity"]> 0:
                self.equipped_items["shield"] = item
                self.remove_item(item, 1)
                log.info(f"Equipped {item.name} as {"Shield"}.")
        elif isinstance(item, items_list.Amulet):
            if self.items[item.id]["quantity"]> 0:
                self.equipped_items["amulet"] = item
                self.remove_item(item, 1)
                log.info(f"Equipped {item.name} as {"Amulet"}.")
        elif isinstance(item, items_list.Ring):
            if self.items[item.id]["quantity"]> 0:
                self.equipped_items["ring"] = item
                self.remove_item(item, 1)
                log.info(f"Equipped {item.name} as {"Ring"}.")
        elif isinstance(item, items_list.Boots):
            if self.items[item.id]["quantity"]> 0:
                self.equipped_items["boots"] = item
                self.remove_item(item, 1)
                log.info(f"Equipped {item.name} as {"Boots"}.")
        elif isinstance(item, items_list.Consumable):
            if self.items[item.id]["quantity"]> 0:
                self.equipped_items["consumable"] = item
                self.remove_item(item, 1)
                log.info(f"Equipped {item.name} as {"Consumable"}.")
        else:
            raise ValueError("Item not of type Weapon, Armor, Consumable, Shield, Amulet or Ring.")
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
        """Unequip an item from the inventory."""
        if not isinstance(slot, str):
            raise TypeError("Slot must be a string.")
        if slot not in self.slots:
            raise ValueError("Invalid slot. Choose from 'weapon', 'armor', or 'consumable'.")
        if slot in self.slots:
           if self.equipped_items[slot] is not None:
               item = self.equipped_items[slot]
               self.add_item(item, 1)
               self.equipped_items[slot] = None
               log.info(f"Unequipped {item.name} from {slot.capitalize()} slot.")
           else:
               raise ValueError("No item equipped in this slot.")
    def unequip_all(self) -> None:
        """Unequip all items from the inventory."""
        if not self.equipped_items:
            raise ValueError("No items equipped.")
        for slot in self.slots:
            if self.equipped_items[slot] is not None:
                item = self.equipped_items[slot]
                self.add_item(item, 1)
                self.equipped_items[slot] = None
                log.info(f"Unequipped {item.name} from {slot.capitalize()} slot.")
    def view_equipped(self) -> None:
        """View equipped items."""
        if not self.equipped_items:
            log.info(f"No items equipped.")
        else:
            equipped_str = "\n".join(
                f"{slot.capitalize()}: {item.name if item else 'None'}" for slot, item in self.equipped_items.items()
            )
            log.info(f"Equipped items:\n{equipped_str}\n")
    def find_by_name(self, name) -> None:
        """Find an item in the inventory by name."""
        if not isinstance(name, str):
            raise TypeError("Name must be a string.")
        found_items = [item for item in self.items.values() if item["item"].name == name]
        if found_items:
            log.info(f"Found {len(found_items)} items with name '{name}': {found_items}")
        else:
            log.info(f"No items found with name '{name}'.")
    def find_by_type(self, item_type) -> None:
        """Find an item in the inventory by type."""
        if not isinstance(item_type, str):
            raise TypeError("Item type must be a string.")
        found_items = [item for item in self.items.values() if item["item"].__class__.__name__.lower() == item_type.lower()]
        if found_items:
            log.info(f"Found {len(found_items)} items of type '{item_type}': {found_items}")
        else:
            log.info(f"No items found of type '{item_type}'.")
    def find_by_effect(self, effect) -> None:
        """Find an item in the inventory by effect."""
        if not isinstance(effect, str):
            raise TypeError("Effect must be a string.")
        found_items = [item for item in self.items.values() if isinstance(item["item"], items_list.Consumable) and item["item"].effect == effect]
        if found_items:
            log.info(f"Found {len(found_items)} items with effect '{effect}': {found_items}")
        else:
            log.info(f"No items found with effect '{effect}'.")
    def find_by_price(self, price) -> None:
        """Find an item in the inventory by price."""
        if not isinstance(price, (int, float)):
            raise TypeError("Price must be a number.")
        found_items = [item for item in self.items.values() if item["item"].price == price]
        if found_items:
            log.info(f"Found {len(found_items)} items with price '{price}': {found_items}")
        else:
            log.info(f"No items found with price '{price}'.")
    def find_by_level(self, level) -> None:
        """Find an item in the inventory by level."""
        if not isinstance(level, int):
            raise TypeError("Level must be an integer.")
        found_items = [item for item in self.items.values() if item["item"].lvl == level]
        if found_items:
            log.info(f"Found {len(found_items)} items with level '{level}': {found_items}")
        else:
            log.info(f"No items found with level '{level}'.")
    def sort_by_name(self) -> None:
        """Sort items in the inventory by name."""
        sorted_items = sorted(self.items.values(), key=lambda x: x["item"].name)
        log.info(f"Sorted items by name: {sorted_items}")
    def sort_by_price(self) -> None:
        """Sort items in the inventory by price."""
        sorted_items = sorted(self.items.values(), key=lambda x: x["item"].price)
        log.info(f"Sorted items by price: {sorted_items}")
    def sort_by_level(self) -> None:
        """Sort items in the inventory by level."""
        sorted_items = sorted(self.items.values(), key=lambda x: x["item"].lvl)
        log.info(f"Sorted items by level: {sorted_items}")
    def sort_by_effect(self) -> None:
        """Sort items in the inventory by effect."""
        sorted_items = sorted(self.items.values(), key=lambda x: x["item"].effect)
        log.info(f"Sorted items by effect: {sorted_items}")
    def sort_by_type(self) -> None:
        """Sort items in the inventory by type."""
        sorted_items = sorted(self.items.values(), key=lambda x: x["item"].__class__.__name__)
        log.info(f"Sorted items by type: {sorted_items}")
    def sort_by_quantity(self) -> None:
        """Sort items in the inventory by quantity."""
        sorted_items = sorted(self.items.values(), key=lambda x: x["quantity"], reverse=True)
        log.info(f"Sorted items by quantity: {sorted_items}")
    @property
    def items(self):
        return self._items
    @items.setter
    def items(self, items):
        if not isinstance(items, dict):
            raise TypeError("Items must be a dictionary.")
        for key, value in items.values():
            if not isinstance(key, uuid.UUID):
                raise TypeError("Item ID must be of type UUID.")
            if not isinstance(value, dict):
                raise TypeError("Item value must be a dictionary.")
            if "item" not in value or "quantity" not in value:
                raise ValueError("Item dictionary must contain 'item' and 'quantity' keys.")
            if not isinstance(value["item"], items_list.Item):
                raise TypeError("Item must be of type Item.")
            if not isinstance(value["quantity"], int):
                raise TypeError("Quantity must be an integer.")
            if value["quantity"] < 0:
                raise ValueError("Quantity must be greater than or equal to 0.")
        self._items = items
               
    @property
    def equipped_items(self):
        return self._equipped_items
    @equipped_items.setter
    def equipped_items(self, value):
        if not isinstance(value, dict):
            raise TypeError("Equipped items must be a dictionary.")
        for key, item in value.items():
            if key not in self.slots:
                raise ValueError(f"Invalid slot: {key}. Must be one of {self.slots}.")
            if item is not None and not isinstance(item, items_list.Item):
                raise TypeError(f"Equipped item must be of type Item or None.")
        self._equipped_items = value
        
    @property
    def item_count(self) -> int:
        """Get the total number of items in the inventory."""
        return sum(item["quantity"] for item in self.items.values())
