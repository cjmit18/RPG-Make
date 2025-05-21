import random
import gen
import uuid
import items_list
class Boot(items_list.Item):  # Inherit from Item
    """Base class for boots"""
    def __init__(self, name: str = "", description: str = "", price: int = 0, effect: str = "boots", lvl: int = 0, speed_power: int = 0, stamina_power: int = 0) -> None:
        self.lvl: int = 1 if lvl == 0 else lvl
        self.name: str = "Boots" if name == "" else name
        self.id = uuid.uuid4()
        # Randomly assign attack and defense power based on roll
        roll: int = gen.generate_random_number(1, 3)
        if lvl == 1:
            self.description: str = "A basic boots" if description == "" else description
            self.price: int = 10 if price == 0 else price
            # Randomly assign health and mana power based on roll
            if roll == 1:
                self.speed_power: int = gen.generate_random_number(2, 10) * self.lvl
                self.stamina_power: int = 0
            elif roll == 2:
                self.speed_power: int = 0
                self.stamina_power: int = gen.generate_random_number(2, 10) * self.lvl
            elif roll == 3:
                self.speed_power: int = gen.generate_random_number(1, 10) * self.lvl
                self.stamina_power: int = gen.generate_random_number(1, 10) * self.lvl
            else:
                # Default values if roll is not in range
                self.health_power: int = 5
                self.mana_power: int = 5
        elif lvl > 1 and lvl <= 10:
            self.description: str = f"A Grade {self.lvl} boots" if description == "" else description
            self.price: int = 20 if price == 0 else price
            self.effect: str = random.choice(["speed", "stamina"])
            # Randomly assign speed and	stamina power based on roll
            if roll == 1:
                if self.effect == "speed":
                    self.speed_power: int = gen.generate_random_number(1, 5) * self.lvl
                    self.stamina_power: int = 0
                elif self.effect == "stamina":
                    self.speed_power = 0
                    self.stamina_power: int = gen.generate_random_number(1, 5) * self.lvl
                elif self.effect == "both":
                    self.speed_power: int = gen.generate_random_number(0, 5) * self.lvl
                    self.stamina_power: int = gen.generate_random_number(0, 5) * self.lvl
            elif roll == 2:
                if self.effect == "speed":
                    self.speed_power: int = gen.generate_random_number(1, 10) * self.lvl
                    self.stamina_power: int = 0
                elif self.effect == "stamina":
                    self.speed_power = 0
                    self.stamina_power: int = gen.generate_random_number(1, 10) * self.lvl
                elif self.effect == "both":
                    self.speed_power: int = gen.generate_random_number(1, 10) * self.lvl
                    self.stamina_power: int = gen.generate_random_number(1, 10) * self.lvl
            elif roll == 3:
                if self.effect == "speed":
                    self.speed_power: int = gen.generate_random_number(1, 15) * self.lvl
                    self.stamina_power: int = 0
                elif self.effect == "stamina":
                    self.speed_power = 0
                    self.stamina_power: int = gen.generate_random_number(1, 15) * self.lvl
                elif self.effect == "both":
                    self.speed_power: int = gen.generate_random_number(0, 15) * self.lvl
                    self.stamina_power: int = gen.generate_random_number(0, 15) * self.lvl