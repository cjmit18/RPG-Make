"""This module defines the Knight class, which is a subclass of Base."""
from .base import Base, StartingItem
from items.weapon_list import Sword
from items.armor_list import Shield
from items.potion_list import Health_Potion
class Knight(Base):
    def __init__(self, character, **kwargs):
        stats = {}
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
        
    def base_stats(self, lvl: int) -> dict[str,int]:
        # Start with the default curve…
        stats = super().base_stats(lvl)
        # …then add class‐specific bonuses per level:
        stats["defense"] += lvl * 5    # Knights get +2 extra Defense per level
        stats["health"] += lvl * 3   # +3 extra Health per level
        return stats