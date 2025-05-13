import Item_functions
import character_creation
class Inventory:
    def __init__(self, character_name: str = ""):
        self.character_name = character_name
        self.items: dict[str, dict] = {}
        self.slots = ["weapon", "armor", "consumable"]
        self.equipped_items = {
            "weapon": None,
            "armor": None,
            "consumable": None
        }
    def __str__(self):
           if not self.items:
               return f"Inventory of {self.character_name} is empty."
           else:
               return f"Inventory of {self.character_name}:\n" + "\n".join([f"{item.name}: {quantity}" for item, quantity in self.items.items()])
    def __repr__(self):
        if not self.items:
            return f"Inventory: ({self.character_name}, empty)"
        else:
            return f"Inventory: ({self.character_name}, {self.items})"
    def add_item(self, item_name, quantity):
        if item_name in self.items:
            self.items[item_name] += quantity
        else:
            self.items[item_name] = quantity
    def remove_item(self, item_name, quantity):
        if item_name in self.items:
            if self.items[item_name] > quantity:
                self.items[item_name] -= quantity
            elif self.items[item_name] == quantity:
                del self.items[item_name]
            else:
                raise ValueError("Not enough items to remove.")
        else:
            raise ValueError("Item not found in inventory.")
    def check_item(self, item_name):
        if item_name in self.items:
            return self.items[item_name]
        else:
            return 0
    def use_item(self, item_name):
        if item_name in self.items:
            if self.items[item_name] > 0:
                self.remove_item(item_name, 1)
                print(f"Used 1 {item_name}.")
            else:
               raise ValueError("No items left to use.")
        else:
            raise ValueError("Item not found in inventory.")
    def drop(self, item_name):
        if item_name in self.items:
            del self.items[item_name]
            print(f"Dropped {item_name}.")
        else:
            raise ValueError("Item not found in inventory.")
    def drop_all(self):
        self.items.clear()
        print("Dropped all items.")
    def equip_item(self, item, slot):
        if isinstance(item, Item_functions.Items):
            if item.__class__.__name__ != slot.capitalize():
                raise ValueError(f"Item type mismatch: {item.__class__.__name__} cannot be equipped in {slot} slot.")
            elif slot in self.slots:
                if self.check_item(item) > 0:
                    self.equipped_items[slot] = item
                    self.remove_item(item, 1)
                    print(f"Equipped {item.name} as {item.__class__.__name__}.")
                else:
                    raise ValueError("Item not found in inventory.")
    def unequip_item(self, slot):
       if slot in self.slots:
           if self.equipped_items[slot] is not None:
               item = self.equipped_items[slot]
               self.add_item(item, 1)
               self.equipped_items[slot] = None
               print(f"Unequipped {item.name} from {slot} slot.")
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
