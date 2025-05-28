"""This modue defines the Mage class, which is a subclass of Base."""
from .base import Base, StartingItem
from items.potion_list import Mana_Potion, Health_Potion
from items.weapon_list import Staff
from items.armor_list import Robe
class Mage(Base):
    
    def __init__(self, character, **kwargs):
        stats = {}
        items = [
            StartingItem(
                        factory=Staff,
                        args=(),
                        kwargs={"name": "Starting Staff", 
                                "description": "A magical staff that enhances spellcasting abilities.",
                                "attack_power": 2},
                        quantity=1, 
                        auto_equip=True),
            StartingItem(
                        factory=Robe,
                        args=(),
                        kwargs={"name": "Starting Robe", 
                                "description": "A robe that provides basic magical protection.",
                                "defense_power": 2},
                        quantity=1,
                        auto_equip=True
                        ),
            StartingItem(Mana_Potion, quantity=3, auto_equip=False),
            StartingItem(Health_Potion, quantity=2, auto_equip=False),
        ]
        super().__init__(character, stats=stats, starting_items=items, name="Mage")
    def base_stats(self, lvl: int) -> dict[str,int]:
        # Start with the default curve…
        stats = super().base_stats(lvl)
        # …then add class‐specific bonuses per level:
        stats["mana"] += lvl * 5    # Mages get +5 extra Mana per level
        stats["attack"] += lvl * 3   # +3 extra ATTk per level
        return stats