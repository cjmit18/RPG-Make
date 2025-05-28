# core/actor.py

from core.stats import Stats
from core.inventory_functions import Inventory
import random
import core.experience_functions as experience_functions
from core.combat_functions import Combat
from jobs import Base

class Actor:
    def __init__(
        self,
        name: str,
        level: int = 1,
        experience: int = 0,
        job_class: type = Base,
        rng: random.Random | None = None,
    ) -> None:
        self._name = name
        # Progression component
        self.levels = experience_functions.Levels(self, level, experience)
        # Stats component (base gets populated by job)
        self.stats = Stats(base={})
        # Inventory component
        self.inventory = Inventory(self)
        # Class/job component applies base stats & starting gear
        self.job = job_class(self)
        # Finalize effective stats & current pools
        self.update_stats()
        # Shared RNG for any systems
        self._rng = rng or random.Random()

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, value: str) -> None:
        if not isinstance(value, str):
            raise TypeError("Name must be a string.")
        self._name = value

    def update_stats(self) -> None:
        """Rebuild effective stats from base, job, and equipped items."""
        self.stats.clear_modifiers()
        # 1) Class modifiers are applied in job.__init__
        # 2) Apply equipped item modifiers
        for item in self.inventory.equipped_items.values():
            if item:
                for stat, mod in item.stat_mod().items():
                    self.stats.add_modifier(stat, mod)
        # 3) (Optional) clamp current health/mana/stamina here if needed

    def engage(self, opponent: "Actor", action_fn=None) -> str:
        """
        Kick off a full combat loop between self and opponent.
        Returns the winner string.
        """
        return Combat(self, opponent, rng=self._rng, action_fn=action_fn).start_combat_loop()

    def calculate_damage(self, opponent: "Actor") -> str:
        """
        One‐off damage calculation between this actor and opponent.
        """
        return Combat(self, opponent, rng=self._rng).calculate_damage(self, opponent)

    def to_dict(self) -> dict:
        return {
            "name":       self.name,
            "level":      self.levels.lvl,
            "experience": self.levels.experience,
            "class":      self.job.__class__.__name__,
            "stats":      self.stats.to_dict(),
            "inventory":  self.inventory.to_dict(),
        }

    @classmethod
    def from_dict(cls, data: dict, item_loader) -> "Actor":
        actor = cls(
            name=data["name"],
            level=data["level"],
            experience=data.get("experience", 0),
            job_class=globals().get(data.get("class", "Base"), Base),
        )
        actor.stats.load_dict(data["stats"])
        actor.inventory.load_dict(data["inventory"], item_loader)
        return actor
