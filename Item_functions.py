import inventory_functions
import experience_functions
import character_creation
import uuid
class Items():
    def __init__(self, name: str = "", description: str = "", price: int = 1, quantity:int = 1, id: uuid.UUID = None):
        self.id = uuid.uuid4()
        self.name = name
        self.description = description
        self.price = price
        self.quantity = quantity
    def __str__(self):
        return f"Item: {self.name}\nDescription: {self.description}\nPrice: {self.price}, Quantity: {self.quantity}"
    def __repr__(self):
        return f"({self.name}, {self.description}, {self.price}, {self.quantity})"
class Weapon(Items):
    def __init__(self, name: str = "", description: str = "", price: int = 5, quantity: int = 1, attack_power: int = 10):
        if not isinstance(name, str):
            raise TypeError("Name must be a string.")
        super().__init__(name, description, price, quantity)
        self.attack_power = attack_power
    def __str__(self):
        return f"Weapon: {self.name}\nDescription: {self.description}\nPrice: {self.price}, Quantity: {self.quantity}\nAttack Power: {self.attack_power}"
    def __repr__(self):
        return self.name
class Armor(Items):
    def __init__(self, name:str = "", description:str = "", price:int = 5, quantity:int = 1, defense_power:int = 5):    
        super().__init__(name, description, price, quantity)
        self.defense_power = defense_power
    def __str__(self):
        return f"Armor: {self.name}\nDescription: {self.description}\nPrice: {self.price}, Quantity: {self.quantity}\nDefense Power: {self.defense_power}"
    def __repr__(self):
        return f"{self.name}"
class Consumable(Items):
    def __init__(self, name:str="", description:str="", effect:str = "" , price:int=5, quantity:int=1,duration:int=1, amount:int=0):
        super().__init__(name, description, price, quantity)
        self.effect = effect
        self.amount = amount
        self.duration = duration
    def __str__(self):
        return f"Consumable: {self.name}\nDescription: {self.description}\nPrice: {self.price}, Quantity: {self.quantity}\nEffect: {self.effect}"
    def __repr__(self):
        return f"{self.name}"
if __name__ == "__main__":
    pass