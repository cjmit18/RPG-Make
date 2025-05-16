import Item_functions
import character_creation
import uuid
class Inventory:
    def __init__(self,character):
        self.character_name = character.name
        self.character = character
        self.items: dict[uuid.UUID, list[Item_functions.Items]] = {}
        self.slots = ["weapon", "armor", "consumable"]
        self.equipped_items = {
            "weapon": None,
            "armor": None,
            "consumable": None,
        }
    def __str__(self):
            if not self.items:
               return f"Inventory of {self.character_name} is empty."
            else:
                return f"{self.character_name}'s Inventory: \n{[item for item in self.items.values()]}"
    def __repr__(self):
        if not self.items:
            return f"Inventory: ({self.character_name}, empty)"
        else:
            return f"Inventory: ({self.character_name}, {self.items})"
    def add_item(self, item, quantity=1):
        if not isinstance(item, Item_functions.Items):
            raise TypeError("Item must be of type Items.")
        elif not isinstance(quantity, int):
            raise TypeError("Quantity must be an integer.")
        elif quantity <= 0:
            raise ValueError("Quantity must be greater than 0.")
        elif item.id in self.items:
            self.items[item.id].extend([item] * quantity)
        else:
            self.items[item.id] = [item] * quantity
    def remove_item(self, item, quantity):
        if not isinstance(item, Item_functions.Items):
            raise TypeError("Item must be of type Items.")
        elif not isinstance(quantity, int):
            raise TypeError("Quantity must be an integer.")
        elif quantity <= 0:
            raise ValueError("Quantity must be greater than 0.")
        elif item.id not in self.items:
            raise ValueError("Item not found in inventory.")
        elif item.id in self.items and len(self.items[item.id]) < quantity:
            raise ValueError("Not enough items to remove.")
        elif item.id in self.items and len(self.items[item.id]) >= quantity:
            for _ in range(quantity):
                self.items[item.id].remove(item)
            if len(self.items[item.id]) == 0:
                del self.items[item.id]
    
    def check_item(self, item):
        if not isinstance(item, Item_functions.Items):
            raise TypeError("Item must be of type Items.")
        if item.id in self.items:
            return self.items[item.id]
        else:
            return f"Item not found in inventory."
        
    def use_item(self, item):
            if item.id in self.items:
                if isinstance(item, Item_functions.Consumable):
                    if item.effect == "health":
                        self.character.health += item.amount
                    elif item.effect == "mana":
                        self.character.mana += item.amount
                    elif item.effect == "stamina":
                        self.character.stamina += item.amount
                    elif item.effect == "speed":
                        self.character.speed += item.amount
                    self.remove_item(item, 1)
                    if item.quantity == 0:
                        del self.items[item.id]
                    
                    return(f"Used {item.name}. Effect: Increase {item.effect} by {item.amount}.")
                else:
                    raise ValueError("Item is not consumable.")
    def drop(self, item):
        if not isinstance(item, Item_functions.Items):
            raise TypeError("Item must be of type Items.")
        elif item.id not in self.items:
            raise ValueError("Item not found in inventory.")
        else:
            self.remove_item(item, 1)
            print(f"Dropped {item.name}.")
    def drop_all(self):
        self.items.clear()
        print("Dropped all items.")
    def equip_item(self, item, slot):
        if isinstance(item, Item_functions.Items):
            if item.__class__.__name__ != slot.capitalize():
                raise ValueError(f"Item type mismatch: {item.__class__.___} cannot be equipped in {slot} slot.")
            if slot == "weapon" and isinstance(item, Item_functions.Weapon):
                if len(self.check_item(item)) > 0:
                    self.equipped_items[slot] = item
                    self.remove_item(item, 1)
                    print(f"Equipped {item.name} as {item.__class__.__name__}.")
            elif slot == "armor" and isinstance(item, Item_functions.Armor):
                if len(self.check_item(item)) > 0:
                    self.equipped_items[slot] = item
                    self.remove_item(item, 1)
                    print(f"Equipped {item.name} as {item.__class__.__name__}.")
            elif slot == "consumable" and isinstance(item, Item_functions.Consumable):
                if len(self.check_item(item)) > 0:
                    self.equipped_items[slot] = item
                    self.remove_item(item, 1)
                    print(f"Equipped {item.name} as {item.__class__.__name__}.")
    def unequip_item(self, slot):
       if slot in self.slots:
           if self.equipped_items[slot] is not None:
               item = self.equipped_items[slot]
               self.add_item(item, 1)
               self.equipped_items[slot] = None
               print(f"Unequipped {item.name} from {slot.capitalize()} slot.")
           else:
               raise ValueError("No item equipped in this slot.")
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
                raise ValueError("Equipped items must contain 'weapon', 'armor', and 'consumable' keys.")
            if not isinstance(value, Item_functions.Items) and value is not None:
                raise TypeError("Equipped items must be of type Items.")
        self._equipped_items = equipped_items
