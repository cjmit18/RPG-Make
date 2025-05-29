from dataclasses import dataclass
from .item_base import Item

@dataclass
class Consumable(Item):
    effect: str    # e.g. "health" or "mana"
    amount: int    # how much to restore
    duration: int  # in turns (0 = instant)
