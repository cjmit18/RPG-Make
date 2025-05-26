"""This module defines the Knight class, which is a subclass of Base."""
from .base import Base, StartingItem
from items.weapon_list import Sword
from items.armor_list import Shield
from items.potion_list import Health_Potion
class Knight(Base):
    def __init__(self, character, **kwargs):
        stats = { "attack": 5,
                  "defense": 7,
                  "speed": 3,
                  "health": 10,
                  "mana": 2,
                  "stamina": 5 
                }
        items = [
                StartingItem(
                        factory=Sword,
                        args=(),
                        kwargs={"name": "Starting Sword", 
                                "description": "A sturdy sword, perfect for a knight.",
                                "attack_power": 5},
                        quantity=1,
                        auto_equip=True
                               ),
                StartingItem(
                        Shield,
                        args=(),
                        kwargs={"name": "Starting Shield", 
                                "description": "A shield that provides excellent defense.",
                                "defense_power": 5},
                        quantity=1, auto_equip=True),
                StartingItem(Health_Potion, quantity=2, auto_equip=False),
                ]
        super().__init__(character, stats=stats, starting_items=items, name="Knight")
        job = "Knight"