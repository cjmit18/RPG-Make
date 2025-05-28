from .base import Base, StartingItem
from items.weapon_list import Dagger
from items.boots_list import Boot
from items.armor_list import Armor

class Rogue(Base):
    """This module defines the Rogue class, which is a subclass of Base."""
    def __init__(self, character, **kwargs):
        stats = {}
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
        
    def base_stats(self, lvl: int) -> dict[str,int]:
        # Start with the default curve…
        stats = super().base_stats(lvl)
        # …then add class‐specific bonuses per level:
        stats["speed"] += lvl * 5    # Knights get +2 extra Speed HP per level
        stats["stamina"] += lvl * 3   # +3 extra STM per level
        return stats