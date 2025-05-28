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
        self.stats = Stats(base=
                           {
                            "health": 100, 
                            "mana": 50,
                            "stamina": 30,
                            "attack": 10,
                            "defense": 10,
                            "speed": 10,
                            }
                           )
        # Inventory component
        self.inventory = Inventory(self)
        # Class/job component applies base stats & starting gear
        self.job = job_class(self)
        # Finalize effective stats & current pools
        self.update_stats()
        # Shared RNG for any systems
        self._rng = rng or random.Random()
 # - Initialize current resource pools at max -
        maxs = self.stats.effective()
        self.current_health = maxs.get("health", 0)
        self.current_mana = maxs.get("mana", 0)
        self.current_stamina = maxs.get("stamina", 0)
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
            # 1) apply the job’s base‐stats for this level
            for stat, val in self.job.base_stats(self.levels.lvl).items():
                self.stats.set_base(stat, val)

            # 2) clear any existing item/buff modifiers
            self.stats.clear_modifiers()

            # 3) apply equipped‐item modifiers
            for item in self.inventory.equipped_items.values():
                if item:
                    for s, mod in item.stat_mod().items():
                        self.stats.add_modifier(s, mod)
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
    def change_job(self, new_job_class: type) -> None:
        """
        Change this actor’s job to `new_job_class`, reapply stats and reset resources.
        new_job_class must be a subclass of jobs.Base taking this Actor as its only arg.
        """
        # 1) swap in the new job
        self.job = new_job_class(self)

        # 2) rebuild all stats from the new job + any equipped items
        self.update_stats()

        # 3) refill current health/mana/stamina to the new maximums
        eff = self.stats.effective()
        self.current_health = eff.get("health", 0)
        self.current_mana   = eff.get("mana",   0)
        self.current_stamina= eff.get("stamina",0)
    # — Resource pools & caps —
    @property
    def max_health(self) -> int:
        return self.stats.effective().get("health", 0)

    @property
    def health(self) -> int:
        return getattr(self, "current_health", 0)

    @health.setter
    def health(self, value: int) -> None:
        self.current_health = max(0, min(value, self.max_health))

    @property
    def max_mana(self) -> int:
        return self.stats.effective().get("mana", 0)

    @property
    def mana(self) -> int:
        return getattr(self, "current_mana", 0)

    @mana.setter
    def mana(self, value: int) -> None:
        self.current_mana = max(0, min(value, self.max_mana))

    @property
    def max_stamina(self) -> int:
        return self.stats.effective().get("stamina", 0)

    @property
    def stamina(self) -> int:
        return getattr(self, "current_stamina", 0)

    @stamina.setter
    def stamina(self, value: int) -> None:
        self.current_stamina = max(0, min(value, self.max_stamina))

    # — Combat stats —
    @property
    def attack(self) -> int:
        return self.stats.effective().get("attack", 0)

    @attack.setter
    def attack(self, value: int) -> None:
        self.stats.set_base("attack", value)

    @property
    def defense(self) -> int:
        return self.stats.effective().get("defense", 0)

    @defense.setter
    def defense(self, value: int) -> None:
        self.stats.set_base("defense", value)

    @property
    def speed(self) -> int:
        return self.stats.effective().get("speed", 0)

    @speed.setter
    def speed(self, value: int) -> None:
        self.stats.set_base("speed", value)


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
