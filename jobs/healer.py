from .base import Base, StartingItem
from items.potion_list import Mana_Potion, Health_Potion
from items.weapon_list import Staff
from items.armor_list import Robe

class Healer(Base):
    """This module defines the Healer class, which is a subclass of Base."""
    def __init__(self, character, **kwargs):
        stats = {
            "attack": 2,
            "defense": 3,
            "speed": 4,
            "health": 8,
            "mana": 10,
            "stamina": 5
        }
        items = [
            StartingItem(
                        factory=Staff,
                        args=(),
                        kwargs={"name": "Starting Staff", 
                                "description": "A magical staff that enhances healing abilities.",
                                "attack_power": 2},
                        quantity=1,
                        auto_equip=True),
            StartingItem(Mana_Potion, quantity=3, auto_equip=False),
            StartingItem(Health_Potion, quantity=2, auto_equip=False),
            ]
        super().__init__(character, stats=stats, starting_items=items, name="Healer")