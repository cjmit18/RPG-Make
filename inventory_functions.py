
import character_creation
import items_list
import uuid, logging
logging.basicConfig(level=logging.INFO)
log = logging.getLogger()
class Inventory:
    def __init__(self,character):
        self.name = character.name  
        self.character: character_creation.Character = character
        self.items: dict[uuid.UUID, dict["item": items_list.Item, "quantity": int]] = {}
        self.slots: list = ["weapon", "armor", "consumable"]
        self.equipped_items: dict = {
            "weapon": None,
            "armor": None,
            "consumable": None,
        }
    def __str__(self) -> str:
        if not self.items:
            return f"Inventory of {self.name} is empty."
        else:
            items_str = "\n".join(
                f"{item['item'].name} x{item['quantity']}" for item in self.items.values()
            )
            return f"{self.name}'s Inventory:\n{items_str}\n"
    def __repr__(self) -> str:
        if not self.items:
            return f"Inventory: ({self.name}, empty)"
        else:
            return f"Inventory: ({self.name}, {self.items})"
    def add_item(self, item, quantity=1) -> None:
        if not isinstance(item, items_list.Item):
            raise TypeError("Item not of type item.")
        elif not isinstance(quantity, int):
            raise TypeError("Quantity must be an integer.")
        elif quantity <= 0:
            raise ValueError("Quantity must be greater than 0.")
        if item.id in self.items:
            self.items[item.id]["quantity"] += quantity
        else:
            self.items[item.id] = {
                "item": item,
                "quantity": quantity}
    def remove_item(self, item, quantity=1) -> None:
        if not isinstance(item, items_list.Item):
            raise TypeError("Item not of item type.")
        elif not isinstance(quantity, int):
            raise TypeError("Quantity must be an integer.")
        elif quantity <= 0:
            raise ValueError("Quantity must be greater than 0.")
        elif item.id not in self.items:
            raise ValueError("Item not found in inventory.")
        elif item.id in self.items and self.items[item.id]["quantity"] < quantity:
            raise ValueError("Not enough items to remove.")
        elif item.id in self.items and self.items[item.id]["quantity"] >= quantity:
            self.items[item.id]["quantity"] -= quantity
            if self.items[item.id]["quantity"] == 0:
                del self.items[item.id]
    def check_item(self, item) -> str:
        if not isinstance(item, items_list.Item):
            raise TypeError("Item not type.Item.")
        elif not isinstance(item.id, uuid.UUID):
            raise TypeError("Item ID must be of type UUID.")
        elif item.id not in self.items:
            raise ValueError("Item not found in inventory.")
        elif item.id in self.items and self.items[item.id]["quantity"] > 0:
            log.info(item)
        elif item.id in self.items and self.items[item.id]["quantity"] == 0:
            log.info(f"{item.name} is in inventory but out of stock.")    
    def check_by_name(self, name) -> None:
        if not isinstance(name, str):
            raise TypeError("Name must be a string.")
        found_items = [item for item in self.items.values() if item["item"].name == name]
        if found_items:
            log.info(f"Found {len(found_items)} items with name '{name}': {found_items}")
        else:
            log.info(f"No items found with name '{name}'.")    
    def use_item(self, item) -> str:
            if not isinstance(item, items_list.Item):
                raise TypeError("Item not of type item.")
            if isinstance(item, items_list.Item):
                if item.id not in self.items:
                    raise ValueError("Item not found in inventory.")
                elif item.id in self.items and self.items[item.id]["quantity"] == 0:
                    raise ValueError("Item is out of stock.")
                elif item.id in self.items and self.items[item.id]["quantity"] > 0:
                    self.items[item.id]["quantity"] -= 1
                    if self.items[item.id]["quantity"] == 0:
                        del self.items[item.id]
                    if isinstance(item, items_list.Potion):
                        if item.effect == "health":
                            self.character.health += item.amount
                        elif item.effect == "mana":
                            self.character.mana += item.amount
                        elif item.effect == "stamina":
                            self.character.stamina += item.amount
                        elif item.effect == "speed":
                            self.character.speed += item.amount
                        log.info( f"Used {item.name}. Effect: Increase {item.effect} by {item.amount}.")
                else:
                    raise ValueError("Item not found in inventory")
                
    def use_by_name(self, name) -> None:
        if not isinstance(name, str):
            raise TypeError("Name must be a string.")
        found_items = [item for item in self.items.values() if item["item"].name == name]
        if found_items:
            for item in found_items:
                self.use_item(item["item"])
        else:
            raise ValueError("Item not found in inventory.")
    def use_consumable(self, item) -> None:
        if not isinstance(item, items_list.Item):
            raise TypeError("Item mitems.Item.")
        if isinstance(item, items_list.Item):
            if item.__class__.__name__ == "Consumable" and isinstance(item, items_list.Consumable):
                if item.id not in self.items:
                    raise ValueError("Item not found in inventory.")
                elif item.id in self.items and self.items[item.id]["quantity"] == 0:
                    raise ValueError("Item is out of stock.")
                elif item.id in self.items and self.items[item.id]["quantity"] > 0:
                    self.items[item.id]["quantity"] -= 1
                    if self.items[item.id]["quantity"] == 0:
                        del self.items[item.id]
                    log.info(f"Used {item.name}. Effect: {item.effect}.")
                else:
                    raise ValueError("Item not found in inventory")
    def drop(self, item) -> None:
        if not isinstance(item, items_list.Item):
            raise TypeError("Item mitems.Item.")
        elif item.id not in self.items:
            raise ValueError("Item not found in inventory.")
        else:
            self.remove_item(item, 1)
            log.info(f"Dropped {item.name}.")
    def drop_by_name(self, name) -> None:
        if not isinstance(name, str):
            raise TypeError("Name must be a string.")
        found_items = [item for item in self.items.values() if item["item"].name == name]
        if found_items:
            for item in found_items:
                self.drop(item["item"])
        else:
            raise ValueError("Item not found in inventory.")
    def drop_all(self) -> None:
        if not self.items:
            raise ValueError("Inventory is empty.")
        for item in list(self.items.values()):
            self.remove_item(item["item"], item["quantity"])
            if self.character.__class__.__name__ == "Player" or self.character.__class__.__name__ == "Character":
                log.info(f"{self.name} Dropped {item['item'].name}.")
    def equip_item(self, item) -> None:
        if not isinstance(item, items_list.Item):
            raise TypeError("Item not of type item.")
        elif not isinstance(item.id, uuid.UUID):
            raise TypeError("Item ID must be of type UUID.")
        elif item.id not in self.items:
            raise ValueError("Item not found in inventory.")
        elif item.id in self.items and self.items[item.id]["quantity"] == 0:
            raise ValueError("Item is out of stock.")
        if isinstance(item, items_list.Weapon) or isinstance(item, items_list.Armor) or isinstance(item, items_list.Consumable):
            if isinstance(item, items_list.Weapon):
                if self.items[item.id]["quantity"]> 0:
                        self.equipped_items["weapon"] = item
                        self.remove_item(item, 1)
                        log.info(f"Equipped {item.name} as {"Weapon"}.")
            if isinstance(item, items_list.Armor):
                if self.items[item.id]["quantity"]> 0:
                    self.equipped_items["armor"] = item
                    self.remove_item(item, 1)
                    log.info(f"Equipped {item.name} as {"Armor"}.")
            if isinstance(item, items_list.Consumable):
                if self.items[item.id]["quantity"]> 0:
                    self.equipped_items["consumable"] = item
                    self.remove_item(item, 1)
                    log.info(f"Equipped {item.name} as {"Consumable"}.")
    def equip_by_name(self, name) -> None:
        if not isinstance(name, str):
            raise TypeError("Name must be a string.")
        found_items = [item for item in self.items.values() if item["item"].name == name]
        if found_items:
            for item in found_items:
                self.equip_item(item["item"])
        else:
            raise ValueError("Item not found in inventory.")    
    def unequip_item(self, slot) -> None:
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
        for slot in self.slots:
            if self.equipped_items[slot] is not None:
                item = self.equipped_items[slot]
                self.add_item(item, 1)
                self.equipped_items[slot] = None
                log.info(f"Unequipped {item.name} from {slot.capitalize()} slot.")
    def find_by_name(self, name) -> None:
        if not isinstance(name, str):
            raise TypeError("Name must be a string.")
        found_items = [item for item in self.items.values() if item["item"].name == name]
        if found_items:
            log.info(f"Found {len(found_items)} items with name '{name}': {found_items}")
        else:
            log.info(f"No items found with name '{name}'.")
    def find_by_type(self, item_type) -> None:
        if not isinstance(item_type, str):
            raise TypeError("Item type must be a string.")
        found_items = [item for item in self.items.values() if item["item"].__class__.__name__.lower() == item_type.lower()]
        if found_items:
            log.info(f"Found {len(found_items)} items of type '{item_type}': {found_items}")
        else:
            log.info(f"No items found of type '{item_type}'.")
    def find_by_effect(self, effect) -> None:
        if not isinstance(effect, str):
            raise TypeError("Effect must be a string.")
        found_items = [item for item in self.items.values() if isinstance(item["item"], items_list.Consumable) and item["item"].effect == effect]
        if found_items:
            log.info(f"Found {len(found_items)} items with effect '{effect}': {found_items}")
        else:
            log.info(f"No items found with effect '{effect}'.")
    def find_by_price(self, price) -> None:
        if not isinstance(price, (int, float)):
            raise TypeError("Price must be a number.")
        found_items = [item for item in self.items.values() if item["item"].price == price]
        if found_items:
            log.info(f"Found {len(found_items)} items with price '{price}': {found_items}")
        else:
            log.info(f"No items found with price '{price}'.")
    def find_by_level(self, level) -> None:
        if not isinstance(level, int):
            raise TypeError("Level must be an integer.")
        found_items = [item for item in self.items.values() if item["item"].lvl == level]
        if found_items:
            log.info(f"Found {len(found_items)} items with level '{level}': {found_items}")
        else:
            log.info(f"No items found with level '{level}'.")
    def sort_by_name(self) -> None:
        sorted_items = sorted(self.items.values(), key=lambda x: x["item"].name)
        log.info(f"Sorted items by name: {sorted_items}")
    def sort_by_price(self) -> None:
        sorted_items = sorted(self.items.values(), key=lambda x: x["item"].price)
        log.info(f"Sorted items by price: {sorted_items}")
    def sort_by_level(self) -> None:
        sorted_items = sorted(self.items.values(), key=lambda x: x["item"].lvl)
        log.info(f"Sorted items by level: {sorted_items}")
    def sort_by_effect(self) -> None:
        sorted_items = sorted(self.items.values(), key=lambda x: x["item"].effect)
        log.info(f"Sorted items by effect: {sorted_items}")
    def sort_by_type(self) -> None:
        sorted_items = sorted(self.items.values(), key=lambda x: x["item"].__class__.__name__)
        log.info(f"Sorted items by type: {sorted_items}")
    def sort_by_quantity(self) -> None:
        sorted_items = sorted(self.items.values(), key=lambda x: x["quantity"], reverse=True)
        log.info(f"Sorted items by quantity: {sorted_items}")
    @property
    def items(self):
        return self._items
    @items.setter
    def items(self, items):
        if not isinstance(items, dict):
            raise TypeError("Items must be a dictionary.")
        for key, value in items.items():
            if not isinstance(key, str):
                raise TypeError("Item name must be a string.")
            if not isinstance(value, int):
                raise TypeError("Item quantity must be an integer.")
        self._items = items
    @property
    def equipped_items(self):
        return self._equipped_items
    @equipped_items.setter
    def equipped_items(self, equipped_items):
        if not isinstance(equipped_items, dict):
            raise TypeError("Equipped items must be a dictionary.")
        for key, value in equipped_items.items():
            if key not in self.slots:
                raise ValueError("Invalid slot. Choose from 'weapon', 'armor', or 'consumable'.")
            if not isinstance(value, items_list.Item) and value is not None:
                raise TypeError("Equipped item must be of type Item or None.")
        self._equipped_items = equipped_items
