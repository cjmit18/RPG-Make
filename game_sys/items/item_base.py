from dataclasses import dataclass
from typing import Dict

@dataclass
class Item:
    name: str
    description: str
    price: int
    level: int

@dataclass
class Equipable(Item):
    slot: str                  # e.g. "weapon", "armor", "ring"
    bonuses: Dict[str, int]    # e.g. {"attack": 5, "defense": 2}

    def apply(self, owner) -> None:
        """
        Apply this equipment's bonuses to the character's stats.
        Uses the item name as the modifier ID.
        """
        for stat, amount in self.bonuses.items():
            owner.stats.add_modifier(self.name, stat, amount)

    def remove(self, owner) -> None:
        """
        Remove this equipment's bonuses from the character's stats.
        """
        owner.stats.remove_modifier(self.name)