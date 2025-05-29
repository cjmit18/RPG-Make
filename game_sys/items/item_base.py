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
