"""Class Creation Module
This module contains the Base job class and related functionality for character classes."""

from inventory_functions import is_equippable
import character_creation
import items_list
from weapon_list import Axe, Dagger, Staff, Weapon, Off_Hand, Sword, Bow
from boots_list import Boot
from armor_list import Shield, Armor, Robe
from potion_list import Health_Potion, Mana_Potion, Potion
from amulet_list import Amulet
from ring_list import Ring
import gen
import uuid
import random
import logging

log = logging.getLogger(__name__)
class Base:
    def __init__(self,
                 character: character_creation,
                 stats: dict | None = None,
                 starting_items: list | None = None,
                 name: str | None = None) -> None:

        self.name      = name or self.__class__.__name__
        self.character = character
        self.job       = self.__class__.__name__
        self.lvl       = character.lvls.lvl

        # 1) default to a small buff if no stats passed in
        stats = stats or {
            "attack":  3 * self.lvl,
            "defense": 3 * self.lvl,
            "speed":   3 * self.lvl,
            "health":  3 * self.lvl,
            "mana":    3 * self.lvl,
            "stamina": 3 * self.lvl,
        }

        # 2) apply each value as a new BASE stat
        for stat_name, stat_value in stats.items():
            # replaces setattr(self.character._base_stats, …)
            self.character.stats.set_base(stat_name, stat_value)
            log.info(f"{self.character.name}'s base {stat_name} set to {stat_value}")

        # 3) give the character any free starting items
        if starting_items:
            starting_items.append(Health_Potion())
            for item in starting_items:
                qty = 5 if isinstance(item, (Health_Potion, Mana_Potion)) else 1
                self.character.inventory.add_item(item, qty)
                # auto-equip if it’s wearable
                if is_equippable(item) and not isinstance(item, Potion):
                    self.character.inventory.equip_item(item)

        # 4) refresh all stats so modifiers (gear + class) take effect
        self.character.update_stats()
    def __str__(self) -> str:
        eff = self.character.stats.effective()
        parts = [f"Class: {self.job}"]
        for stat in ["attack", "defense", "speed", "health", "mana", "stamina"]:
            base = self.character.stats.base.get(stat, 0)
            total = eff[stat]
            bonus = total - base
            line = f"{stat.capitalize()}: {total}"
            if bonus:
                line += f" (Base: {base} + Bonus: {bonus})"
            parts.append(line)
        return "\n".join(parts)

    def __repr__(self) -> str:
        return f"<{self.job} {self.character.name} (Lvl {self.character.lvl})>"

    @staticmethod
    def generate_random_class(
        cls,
        character: character_creation,
    ) -> "Base":
        """Assigns a random subclass (Knight, Mage, Rogue, Healer) if cls is None."""
        if cls is None:
            cls = random.choice([Knight, Mage, Rogue, Healer])
        return cls(character)
    @classmethod
    def set_stats(cls, character: "character_creation.Character", stats: dict) -> None:
        """Completely overwrite a character’s base stats via the Stats API."""
        for stat_name, stat_value in stats.items():
            character.stats.set_base(stat_name, stat_value)
            log.info(f"{character.name}'s base {stat_name} reset to {stat_value}")
        character.update_stats()

# Example subclasses (customize per game design)
class Knight(Base):
    def __init__(self, character, **kwargs):
        super().__init__(
            character,
            stats={"attack": 5, "defense": 7, "speed": 3, "health": 10, "mana": 2, "stamina": 5},
            starting_items=[Sword(), Shield()],
            name="Knight"
        )

class Mage(Base):
    def __init__(self, character, **kwargs):
        super().__init__(
            character,
            stats={"attack": 2, "defense": 2, "speed": 4, "health": 6, "mana": 12, "stamina": 3},
            starting_items=[Staff(), Mana_Potion()],
            name="Mage"
        )

class Rogue(Base):
    def __init__(self, character, **kwargs):
        super().__init__(
            character,
            stats={"attack": 7, "defense": 3, "speed": 8, "health": 8, "mana": 3, "stamina": 6},
            starting_items=[Dagger(), Boot()],
            name="Rogue"
        )

class Healer(Base):
    def __init__(self, character, **kwargs):
        super().__init__(
            character,
            stats={"attack": 1, "defense": 4, "speed": 3, "health": 8, "mana": 14, "stamina": 4},
            starting_items=[Amulet(), Health_Potion()],
            name="Healer"
        )
