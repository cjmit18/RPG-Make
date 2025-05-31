import uuid
from dataclasses import dataclass
from typing import Dict

@dataclass
class Item:
    """
    Base class for all items (equippable, consumable, etc.).
    """
    name: str
    description: str
    price: int
    level: int


class Equipable(Item):
    """
    An equipable item occupies one slot (e.g. "weapon", "armor", "ring")
    and grants stat bonuses. Each instance carries a unique ID.
    """
    slot: str                 # e.g. "weapon", "armor", "ring"
    bonuses: Dict[str, int]   # e.g. {"attack": 5, "defense": 2}

    def __init__(
        self,
        name: str,
        description: str,
        price: int,
        level: int,
        slot: str,
        bonuses: Dict[str, int],
        id: str = None,
    ):
        # Initialize the base Item fields
        super().__init__(name, description, price, level)

        # Store slot & bonuses on this instance
        self.slot = slot
        self.bonuses = bonuses

        # Auto-generate a UUID if no `id` was supplied
        self.id = id or str(uuid.uuid4())

    def apply(self, owner) -> None:
        """
        Apply this equipment’s bonuses to the character’s stats.
        Uses the item.id as the modifier key.
        """
        for stat, amount in self.bonuses.items():
            owner.stats.add_modifier(self.id, stat, amount)

    def remove(self, owner) -> None:
        """
        Remove this equipment’s bonuses from the character’s stats.
        """
        owner.stats.remove_modifier(self.id)
