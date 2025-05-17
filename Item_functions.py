import inventory_functions
import experience_functions
import character_creation
import uuid, random, logging
logging.basicConfig(level=logging.INFO)
log = logging.getLogger()
class Items():
    def __init__(self, name: str = "", description: str = "", price: int = 0, quantity:int = 0, lvl: int = 0, id: uuid.UUID = None):
        self.id = uuid.uuid4()
        self.name = name
        self.description = description
        self.price = price
        self.quantity = quantity
        self.lvl = experience_functions.Levels(self, lvl).lvl
        self.experience = experience_functions.Levels(self, lvl).experience
    def __str__(self):
        return f"Item: {self.name}\nDescription: {self.description}\nPrice: {self.price}, Quantity: {self.quantity}, Lvl: {self.lvl}"
    def __repr__(self):
        return f"({self.name}, {self.description}, {self.price}, {self.quantity})"
    def generate(item_type = random.choice(["weapon","armor","consumable"]), attack_power=0, defense_power=0, effect="", amount=0, duration=0, lvl=1, price=0, quantity=0):
        if item_type == "weapon":
            if lvl == 1:
                return Weapon(name = "Sword", 
                              description = "A basic sword",
                              attack_power= 10 if attack_power == 0 else attack_power,
                              price = 10 if price == 0 else price,
                              quantity = 1 if quantity == 0 else quantity,
                              lvl = 1 if lvl == 0 else lvl,
                              )
            elif lvl == 2:
                return Weapon(name = "Sword", 
                              description = "A grade 2 sword",
                              attack_power= 20 if attack_power == 0 else attack_power,
                              price = 20 if price == 0 else price,
                              quantity = 1 if quantity == 0 else quantity,
                              lvl = 2 if lvl == 0 else lvl,
                              )
            elif lvl == 3:
                return Weapon(name = "Sword", 
                              description = "A grade 3 sword",
                              attack_power= 30 if attack_power == 0 else attack_power,
                              price = 30 if price == 0 else price,
                              quantity = 1 if quantity == 0 else quantity,
                              lvl = 3 if lvl == 0 else lvl,
                              )
        elif item_type == "armor":
            if lvl == 1:
                return Armor(name="Shield", 
                             description="A basic shield",
                             defense_power= 10 if defense_power == 0 else defense_power,
                             price = 10 if price == 0 else price,
                             )
            elif lvl == 2:
                return Armor(name="Shield",
                             description="A grade 2 shield",
                             defense_power= 20 if defense_power == 0 else defense_power,
                             price = 20 if price == 0 else price,
                             )
            elif lvl == 3:
                return Armor(name="Shield",
                             description="A grade 3 shield",
                             defense_power= 30 if defense_power == 0 else defense_power,
                             price = 30 if price == 0 else price,
                             )
        elif item_type == "consumable":
            if effect == "" and amount == 0:
                effect = random.choice(["health", "mana", "stamina", "speed"])
            if lvl == 1:
                if effect == "health":
                    return Consumable(name="Health Potion", 
                                      description="A basic Health Potion",
                                      effect="health", 
                                      amount=25 if amount == 0 else amount,
                                    duration=60 if duration == 0 else duration, 
                                    price=5 if price == 0 else price,
                                    )
                elif effect == "mana":
                    return Consumable(name="Mana Potion",
                                       description="A basic Mana Potion",
                                       effect="mana",
                                         amount=25 if amount == 0 else amount,
                                           duration=60 if duration == 0 else duration, 
                                             price=10 if price == 0 else price,
                                           )
                elif effect == "stamina":
                    return Consumable(name="Stamina Potion",
                                       description="A basic Stamina Potion",
                                         effect="stamina",
                                           amount=25 if amount == 0 else amount,
                                             duration=60 if duration == 0 else duration,
                                                price=20 if price == 0 else price,
                                               )
                elif effect == "speed":
                    return Consumable(name="Speed Potion", 
                                      description="A basic Speed Potion",
                                      effect="speed",
                                        amount=25 if amount == 0 else amount,
                                          duration=60 if duration == 0 else duration,
                                            price=20 if price == 0 else price,
                                            )
                else:
                    return Consumable(name="Consumable", description="A consumable", effect="None", amount=0, duration=0,)
            elif lvl == 2:
                if effect == "health":
                    return Consumable(name="Health Potion", 
                                      description="A grade 2 Health Potion",
                                      effect="health", 
                                      amount=50 if amount == 0 else amount,
                                    duration=120 if duration == 0 else duration, 
                                    price=25 if price == 0 else price,
                                    )
                elif effect == "mana":
                    return Consumable(name="Mana Potion",
                                       description="A grade 2 Mana Potion",
                                       effect="mana",
                                         amount=50 if amount == 0 else amount,
                                           duration=120 if duration == 0 else duration, 
                                           price=50 if price == 0 else price,
                                           )
                elif effect == "stamina":
                    return Consumable(name="Stamina Potion",
                                       description="A grade 2 Stamina Potion",
                                         effect="stamina",
                                           amount=50 if amount == 0 else amount,
                                             duration=120 if duration == 0 else duration,
                                             price=100 if price == 0 else price,
                                               )
                elif effect == "speed":
                    return Consumable(name="Speed Potion", 
                                      description="A a grade 2 Speed Potion",
                                      effect="speed",
                                        amount=50 if amount == 0 else amount,
                                          duration=120 if duration == 0 else duration,
                                          price=100 if price == 0 else price,
                                            )
            elif lvl == 3:
                if effect == "health":
                    return Consumable(name="Health Potion", 
                                      description="A grade 3 Health Potion",
                                      effect="health", 
                                      amount=100 if amount == 0 else amount,
                                    duration=300 if duration == 0 else duration, 
                                    price=125 if price == 0 else price,
                                    )
                elif effect == "mana":
                    return Consumable(name="Mana Potion",
                                       description="A a grade 3 Mana Potion",
                                       effect="mana",
                                         amount=100 if amount == 0 else amount,
                                           duration=300 if duration == 0 else duration,
                                           price=250 if price == 0 else price, 
                                           )
                elif effect == "stamina":
                    return Consumable(name="Stamina Potion",
                                       description="A a grade 3 Stamina Potion",
                                         effect="stamina",
                                           amount=100 if amount == 0 else amount,
                                             duration=300 if duration == 0 else duration,
                                                price=300 if price == 0 else price,
                                               )
                elif effect == "speed":
                    return Consumable(name="Speed Potion", 
                                      description="A a grade 3 Speed Potion",
                                      effect="speed",
                                        amount=100 if amount == 0 else amount,
                                          duration=300 if duration == 0 else duration,
                                            price=300 if price == 0 else price,
                                            )
                else:
                    return Consumable(name="Consumable", description="A consumable", effect="None", amount=1, duration=0,price=0)
        else:
            raise ValueError("Invalid item type.")
class Weapon(Items):
    def __init__(self, name: str = "", description: str = "", price: int = 5, attack_power: int = 10, lvl: int = 1, quantity:int = 1):
        if not isinstance(name, str):
            raise TypeError("Name must be a string.")
        super().__init__(name, description, price, quantity, lvl)
        self.attack_power = attack_power
        self.quantity = quantity
    def __str__(self):
        return f"Weapon: {self.name}\nDescription: {self.description}\nPrice: {self.price}, Quantity: {self.quantity}\nAttack Power: {self.attack_power}"
    def __repr__(self):
        return self.name
class Armor(Items):
    def __init__(self, name:str = "", description:str = "", price:int = 5, quantity:int = 1, defense_power:int = 5, lvl:int = 1):    
        super().__init__(name, description, price, quantity, lvl)
        self.defense_power = defense_power
    def __str__(self):
        return f"Armor: {self.name}\nDescription: {self.description}\nPrice: {self.price}, Quantity: {self.quantity}\nDefense Power: {self.defense_power}"
    def __repr__(self):
        return f"{self.name}"
class Consumable(Items):
    def __init__(self, price=0,name:str="", description:str="", effect:str = "" ,duration:int=1, amount:int=0,quantity:int=1, lvl:int=1):
        super().__init__(name, description, price, quantity, lvl)
        self.price = price
        self.effect = effect
        self.duration = duration
        self.amount = amount
        self.quantity = quantity
    def __str__(self):
        if self.duration > 1:
            return f"Consumable: {self.name}\nDescription: {self.description}\nPrice: {self.price}, Quantity: {self.quantity}\nEffect: Increases {self.effect} by {self.amount} for {self.duration} turns."
        elif self.duration <= 1:
            return f"Consumable: {self.name}\nDescription: {self.description}\nPrice: {self.price}, Quantity: {self.quantity}\nEffect: Increases {self.effect} by {self.amount}."
    def __repr__(self):
        return f"{self.name}"
if __name__ == "__main__":
    pass#Figure out how to fix quantity