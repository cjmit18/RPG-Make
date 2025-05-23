import random
import gen
import uuid
import items_list
class Boot(items_list.Item):  # Inherit from Item
    """Base class for boots"""
    def __init__(self, name: str = "", description: str = "", price: int = 0, effect: str = "", lvl: int = 0, speed_power: int = 0, stamina_power: int = 0) -> None:
        self.lvl: int = 1 if lvl == 0 else lvl
        self.name: str = "Boots" if name == "" else name
        self.id: uuid = uuid.uuid4()
        # Randomly assign attack and defense power based on roll
        roll: int = gen.generate_random_number(1, 3)
        def compare_to(self, other) -> str:
            if self.speed_power:
                diff = self.speed_power - other.speed_power
                return f"{self.name} is {'more' if diff > 0 else 'less'} powerful than {other.name} by {abs(diff)} speed power."
            if self.stamina_power:
                diff = self.stamina_power - other.stamina_power
                return f"{self.name} is {'more' if diff > 0 else 'less'} powerful than {other.name} by {abs(diff)} stamina power."
        if lvl == 1:
            self.description: str = "A basic boots" if description == "" else description
            self.price: int = 10 if price == 0 else price
            self.speed_power: int = gen.generate_random_number(0, 5) * self.lvl if speed_power == 0 else speed_power
            self.stamina_power: int = gen.generate_random_number(0, 5) * self.lvl if stamina_power == 0 else stamina_power
            # Randomly assign speed and stamina power based on roll
        elif lvl > 1 and lvl <= 10:
            self.description: str = f"A Grade {self.lvl} boots" if description == "" else description
            self.price: int = 20 if price == 0 else price
            # Randomly assign speed and	stamina power based on roll
            if roll == 1:
                    self.speed_power: int = gen.generate_random_number(1, 5) * self.lvl
                    self.stamina_power: int = gen.generate_random_number(1, 5) * self.lvl
            elif roll == 2:
                    self.speed_power = gen.generate_random_number(1, 10) * self.lvl
                    self.stamina_power: int = gen.generate_random_number(1, 5) * self.lvl
            elif roll == 3:
                    self.speed_power: int = gen.generate_random_number(1, 15) * self.lvl
                    self.stamina_power: int = gen.generate_random_number(1, 15) * self.lvl
        elif lvl >= 10:
                if roll == 1:
                    self.speed_power: int = gen.generate_random_number(1, 10) * self.lvl
                    self.stamina_power: int = gen.generate_random_number(1, 20) * self.lvl
                elif roll == 2:
                    self.speed_power: int = gen.generate_random_number(1, 20) * self.lvl
                    self.stamina_power: int = gen.generate_random_number(1, 10) * self.lvl
                elif roll == 3:
                    self.speed_power: int = gen.generate_random_number(1, 20) * self.lvl
                    self.stamina_power: int = gen.generate_random_number(1, 20) * self.lvl