from .base import Base, StartingItem
from items.weapon_list import Dagger
from items.boots_list import Boot
from items.armor_list import Armor

class Rogue(Base):
    """This module defines the Rogue class, which is a subclass of Base."""
    def __init__(self, character, **kwargs):
        stats = {
            "attack": 4,
            "defense": 3,
            "speed": 6,
            "health": 8,
            "mana": 2,
            "stamina": 5
        }
        items = [
            StartingItem(
                        factory=Dagger, 
                        args=(),
                        kwargs={"name": "Starting Dagger", 
                                "description": "A sharp dagger, perfect for a rogue.",
                                "attack_power": 4},
                        quantity=1,
                        auto_equip=True
                        ),
            StartingItem(
                        factory=Boot,
                        args=(),
                        kwargs={"name": "Starting Boots", 
                                "description": "Light boots that enhance speed.",
                                "speed_power": 2},
                        quantity=1,
                        auto_equip=True
                          ),
            StartingItem(
                        factory=Armor,
                        args=(),
                        kwargs={"name": "Starting Armor", 
                                "description": "Light armor that provides basic protection.",
                                "defense_power": 3},
                        quantity=1,
                        auto_equip=True
                        ),
        ]
        super().__init__(character, stats, items, name="Rogue")