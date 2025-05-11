class Inventory:
    def __init__(self, character_name: str = ""):
        self.character_name = character_name
        self.items = {}
    def __str__(self):
        return f"Inventory of {self.character_name}:\n" + "\n".join([f"{item}: {quantity}" for item, quantity in self.items.items()] ) if self.items else "Inventory is empty."
    def add_item(self, item_name, quantity):
        if item_name in self.items:
            self.items[item_name] += quantity
        else:
            self.items[item_name] = quantity
    def remove_item(self, item_name, quantity):
        if item_name in self.items and self.items[item_name] >= quantity:
            self.items[item_name] -= quantity
            if self.items[item_name] == 0:
                del self.items[item_name]
        else:
            print("Item not available or insufficient quantity.")
    def check_item(self, item_name):
        return self.items.get(item_name, 0)
    def get_items(self):
        return self.items
    def set_items(self, items):
        self.items = items
    def use_item(self, item_name):
        if item_name in self.items:
            self.remove_item(item_name, 1)
            print(f"Used {item_name}.")
        else:
            print("Item not available.")
    def drop(self, item_name):
        if item_name in self.items:
            self.remove_item(item_name, 1)
            print(f"Dropped 1 {item_name}.")
        else:
            print("Item not available.")
    def drop_all(self):
        self.items.clear()
        print("Dropped all items.")
@property
def items(self):
    return self._items
@items.setter
def items(self, items):
    if not isinstance(items, dict):
        raise TypeError("Items must be a dictionary.")
    self._items = items
    