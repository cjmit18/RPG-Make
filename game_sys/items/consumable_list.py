from game_sys.items.item_base import Item
from dataclasses import dataclass
@dataclass
class Consumable(Item):
    effect: str    # "health" or "mana"
    amount: int
    duration: int  # in turns (0 = instant)

    def apply(self, owner) -> None:
        if self.effect == "health":
            owner.health += self.amount
        elif self.effect == "mana":
            owner.mana += self.amount
        else:
            raise ValueError(f"Unknown consumable effect '{self.effect}'")
