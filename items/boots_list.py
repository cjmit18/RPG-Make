import random
import gen
import uuid
from items.items_list import Item
class Boot(Item):  # Inherit from Item
    """Base class for boots"""
    slot: str = "boots"
    def __init__(self,  
                name: str = "",
                description: str = "",
                price: int = 0,
                lvl: int = 0,
                speed_power: int = 0,
                stamina_power: int = 0
                ) -> None:
        super().__init__(name, description, price, lvl or 1)
        self.lvls.lvl = 1 if lvl == 0 else lvl
        self.name: str = "Boots" if name == "" else name
        self.speed_power: int = speed_power
        self.stamina_power: int = stamina_power
        # Randomly assign attack and defense power based on roll
        roll: int = gen.generate_random_number(1, 3)
        if self.lvls.lvl == 1:
            self.description: str = "A basic boots" if description == "" else description
            self.price: int = 10 if price == 0 else price
            self.speed_power: int = gen.generate_random_number(0, 5) * self.lvls.lvl if speed_power == 0 else speed_power
            self.stamina_power: int = gen.generate_random_number(0, 5) * self.lvls.lvl if stamina_power == 0 else stamina_power
            # Randomly assign speed and stamina power based on roll
        elif self.lvls.lvl > 1 and self.lvls.lvl <= 10:
            self.description: str = f"A Grade {self.lvls.lvl} boots" if description == "" else description
            self.price: int = 20 if price == 0 else price
            # Randomly assign speed and	stamina power based on roll
            if roll == 1:
                self.speed_power: int = gen.generate_random_number(1, 5) * self.lvls.lvl
                self.stamina_power: int = gen.generate_random_number(1, 5) * self.lvls.lvl
            elif roll == 2:
                self.speed_power = gen.generate_random_number(1, 10) * self.lvls.lvl
                self.stamina_power: int = gen.generate_random_number(1, 5) * self.lvls.lvl
            elif roll == 3:
                self.speed_power: int = gen.generate_random_number(1, 15) * self.lvls.lvl
                self.stamina_power: int = gen.generate_random_number(1, 15) * self.lvls.lvl
        elif self.lvls.lvl >= 10:
            if roll == 1:
                self.speed_power: int = gen.generate_random_number(1, 10) * self.lvls.lvl
                self.stamina_power: int = gen.generate_random_number(1, 20) * self.lvls.lvl
            elif roll == 2:
                self.speed_power: int = gen.generate_random_number(1, 20) * self.lvls.lvl
                self.stamina_power: int = gen.generate_random_number(1, 10) * self.lvls.lvl
            elif roll == 3:
                self.speed_power: int = gen.generate_random_number(1, 20) * self.lvls.lvl
                self.stamina_power: int = gen.generate_random_number(1, 20) * self.lvls.lvl
    def compare_to(self, other) -> str:
        """Compare this boots to another boots."""
        if self.speed_power and self.stamina_power:
            diff = self.speed_power - other.speed_power
            return f"{self.name} is {'more' if diff > 0 else 'less'} powerful than {other.name} by {abs(diff)} speed power."
        elif self.stamina_power:
            diff = self.stamina_power - other.stamina_power
            return f"{self.name} is {'more' if diff > 0 else 'less'} powerful than {other.name} by {abs(diff)} stamina power."
        elif self.speed_power:
            diff = self.speed_power - other.speed_power
            return f"{self.name} is {'more' if diff > 0 else 'less'} powerful than {other.name} by {abs(diff)} speed power."
    def stat_mod(self) -> dict[str, int]:
        """Return a dictionary of stat modifiers for the weapon."""
        return {"speed": getattr(self, "speed_power", 0),
                "stamina": getattr(self, "stamina_power", 0)}
