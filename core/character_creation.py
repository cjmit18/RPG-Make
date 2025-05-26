"""Character Creation Module
This module contains the Character class and its subclasses (NPC, Enemy, Player) for a game."""

import logging
from core.inventory_functions import Inventory
from jobs.base import Base
from core.stats import Stats
import core.experience_functions as experience_functions
import gen

log = logging.getLogger(__name__)

class Character:
    """
    Base class for all characters in the game.
    Attributes:
        name (str): Character name.
        attack, defense, speed (int): Combat stats.
        health, mana, stamina (int): Current resource pools.
        lvl (int): Character level.
        experience (int): Experience points.
        inventory (Inventory): Item storage.
        job (Base): Character's class/job.
    """
    def __init__(self, name: str = "Template", level: int = 1, experience: int = 0) -> None:
        # Identity and progression
        self._name = name
        self.lvls  = experience_functions.Levels(self, level, experience)

        # Unified stats: 'health', 'mana', 'stamina' represent maximum pools
        self.stats = Stats(base={
            "attack":   5  + level * 2,
            "defense":  3  + level * 1,
            "speed":    4  + level * 1,
            "health":  20  + level * 5,
            "mana":    10  + level * 3,
            "stamina": 10  + level * 2,
        })

        # Inventory storage
        self.inventory = Inventory(self)

        # Initialize current pools before class/job modifiers
        maxs = self.stats.effective()
        self.current_health  = maxs["health"]
        self.current_mana    = maxs["mana"]
        self.current_stamina = maxs["stamina"]

        # Assign class/job (Base may apply class-based stat overrides)
        self.change_class(Base)
    def update_stats(self) -> None:
        # 1) clear previous modifiers
        self.stats.clear_modifiers()

        # 2) apply class/job modifiers
        for stat_name, value in self.job.stats.items():
            self.stats.add_modifier(stat_name, value)
    # 3) apply equipped items' modifiers
        for item in self.inventory.equipped_items.values():
            if not item:
                continue
            for stat_name, mod in item.stat_mod().items():
                self.stats.add_modifier(stat_name, mod)
        # 4) clamp current pools within [0, new_max]
        maxs = self.stats.effective()
        self.current_health  = max(0, min(self.current_health,  maxs["health"]))
        self.current_mana    = max(0, min(self.current_mana,    maxs["mana"]))
        self.current_stamina = max(0, min(self.current_stamina, maxs["stamina"]))

    def __str__(self) -> str:
        eff = self.stats.effective()
        lines = [
            f"{self.__class__.__name__}: {self._name}",
            str(self.lvls),
            f"Class: {self.job.__class__.__name__}",
            "-" * 20,
            f"Attack:  {eff['attack']}",
            f"Defense: {eff['defense']}",
            f"Speed:   {eff['speed']}",
            f"Health:  {self.current_health}/{eff['health']}",
            f"Mana:    {self.current_mana}/{eff['mana']}",
            f"Stamina: {self.current_stamina}/{eff['stamina']}",
            "-" * 20,
            str(self.inventory)
            ]
        return "\n".join(lines)
    def __repr__(self) -> str:
        return self.__str__()

    def __eq__(self, other) -> bool:
        if not isinstance(other, Character):
            return NotImplemented
        return self.name == other.name and self.lvl == other.lvl

    def use_item(self, item):
        """Use an item from the inventory."""
        return self.inventory.use_item(item)

    def change_class(self, job_cls: type[Base]) -> None:
        """ Change the character's class/job."""
        # assign new class/job and reapply modifiers
        self.job = job_cls(self)
        self.update_stats()
        self.restore_all()  # reset resource pools

    def get_stat_breakdown(self, stat_name: str) -> str:
        """
        Returns a formatted string showing the breakdown of a specific stat."""
        base  = self.stats.base.get(stat_name, 0)
        total = self.stats.effective().get(stat_name, 0)
        bonus = total - base
        return f"{stat_name.capitalize()}: {total} (Base: {base} + Bonus: {bonus})"

    def to_dict(self) -> dict:
        return {
            "name":       self.name,
            "level":      self.lvls.lvl,
            "experience": self.lvls.experience,
            "class":      self.job.__class__.__name__,
            "inventory":  [item.to_dict() for item in self.inventory.items],
            "equipped":   {slot: item.to_dict() for slot, item in self.inventory.equipped_items.items() if item}
        }

    @classmethod
    def from_dict(cls, data: dict, item_loader) -> "Character":
        """
        Create a Character instance from a dictionary representation.
        """
        from jobs import Knight, Mage, Rogue, Healer, Base
        CLASS_MAP = {"Knight": Knight, "Mage": Mage, "Rogue": Rogue, "Healer": Healer, "Base": Base}
        char = cls(name=data["name"], level=data["level"], experience=data.get("experience", 0))
        job_class = CLASS_MAP.get(data.get("class", "Base"), Base)
        char.change_class(job_class)
        for item_data in data.get("inventory", []):
            item = item_loader(item_data)
            char.inventory.add_item(item)
        for slot, item_data in data.get("equipped", {}).items():
            item = item_loader(item_data)
            char.inventory.equip_item(item)
        return char

    def take_damage(self, amount: int) -> None:
        """Reduce health by the specified amount, ensuring it doesn't go below zero."""
        self.health = self.current_health - amount

    def drain_mana(self, amount: int) -> None:
        """Reduce mana by the specified amount, ensuring it doesn't go below zero."""
        self.mana = self.current_mana - amount

    def drain_stamina(self, amount: int) -> None:
        """Reduce stamina by the specified amount, ensuring it doesn't go below zero."""
        self.stamina = self.current_stamina - amount

    def heal(self, amount: int) -> None:
        """Increase health by the specified amount, ensuring it doesn't exceed max health."""
        self.health = self.current_health + amount
    def restore_mana(self, amount: int) -> None:
        """Increase mana by the specified amount, ensuring it doesn't exceed max mana."""
        self.mana = self.current_mana + amount
    def restore_stamina(self, amount: int) -> None:
        """Increase stamina by the specified amount, ensuring it doesn't exceed max stamina."""
        self.stamina = self.current_stamina + amount
    def restore_all(self) -> None:
        """Restore all resource pools to their maximum values."""
        maxs = self.stats.effective()
        for attr in ("health", "mana", "stamina"):
            setattr(self, f"current_{attr}", maxs[attr])
    # ---- Properties ----

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, name) -> None:
        if not isinstance(name, str):
            raise TypeError("Name must be a string.")
        self._name = name

    @property
    def lvl(self) -> int:
        return self.lvls.lvl

    @lvl.setter
    def lvl(self, lvl: int) -> None:
        if lvl < self.lvls.lvl:
            raise ValueError("Level cannot be decreased.")
        if lvl > self.lvls.max_level:
            lvl = self.lvls.max_level
        self.lvls.lvl = lvl
        self.update_stats()

    # Stat properties
    @property
    def attack(self) -> int:
        return self.stats.effective()["attack"]
    @attack.setter
    def attack(self, value: int) -> None:
        self.stats.set_base("attack", value)

    @property
    def defense(self) -> int:
        return self.stats.effective()["defense"]
    @defense.setter
    def defense(self, value: int) -> None:
        self.stats.set_base("defense", value)

    @property
    def speed(self) -> int:
        return self.stats.effective()["speed"]
    @speed.setter
    def speed(self, value: int) -> None:
        self.stats.set_base("speed", value)

    @property
    def max_health(self) -> int:
        return self.stats.effective()["health"]

    @property
    def health(self) -> int:
        return self.current_health
    @health.setter
    def health(self, value: int) -> None:
        self.current_health = max(0, min(value, self.max_health))

    @property
    def max_mana(self) -> int:
        return self.stats.effective()["mana"]

    @property
    def mana(self) -> int:
        return self.current_mana
    @mana.setter
    def mana(self, value: int) -> None:
        self.current_mana = max(0, min(value, self.max_mana))

    @property
    def max_stamina(self) -> int:
        return self.stats.effective()["stamina"]

    @property
    def stamina(self) -> int:
        return self.current_stamina
    @stamina.setter
    def stamina(self, value: int) -> None:
        self.current_stamina = max(0, min(value, self.max_stamina))


class NPC(Character):
    def __init__(self, name: str = "NPC", level: int = 1) -> None:
        super().__init__(name, level)

class Enemy(Character):
    def __init__(self, name: str = "Enemy", level: int = 1, experience: int = 0) -> None:
        super().__init__(name, level, experience)
        self.lvls.experience = self.lvls.lvl * 100 if experience == 0 else experience

class Player(Character):
    def __init__(self, name: str = "Hero", level: int = 1, experience: int = 0) -> None:
        super().__init__(name, level, experience)
        # Safe to reference current_* here now
