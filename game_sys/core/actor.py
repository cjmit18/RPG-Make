# game_sys/core/actor.py

"""
Actor class for managing game characters, their jobs, stats, inventory, and status effects.
"""

from typing import Type, Optional, Callable
from game_sys.inventory.inventory import Inventory
from game_sys.jobs.factory import create_job
from game_sys.jobs.base import Job
from game_sys.core.experience_functions import Levels
from game_sys.core.stats import Stats
from game_sys.items.item_base import Equipable
from game_sys.combat.status import StatusEffect
from logs.logs import get_logger

log = get_logger(__name__)

class Actor:
    """
    Base class for all game actors (characters, NPCs, etc.).
    Manages job assignment, stats, inventory, status effects, and combat-related methods.
    """

    def __init__(
        self,
        name: str,
        level: int = 1,
        experience: int = 0,
        job_class: Type[Job] = Job,
    ):
        self.name: str = name
        self.levels: Levels = Levels(self, level, experience)

        # Initialize base stats to zeros; job will override in _initialize_job()
        self.stats: Stats = Stats({stat: 0 for stat in Job.base_stats.keys()})

        # Inventory (manages items, equipment, consumables)
        self.inventory: Inventory = Inventory(self)

        # Assign initial job
        self.job: Job = job_class(self.levels.lvl)

        # Who last dealt lethal damage (used in loot logic)
        self.last_damager: Optional["Actor"] = None

        # Active temporary stat modifiers (list of StatusEffect)
        self.status_effects: list[StatusEffect] = []

        # Call initializer to apply job stats/items
        self._initialize_job()

    def _initialize_job(self) -> None:
        """
        Apply job effects: set stats, add & auto-equip starting items, refill resources.
        """
        self.update_stats()

        # Add and auto-equip any starting items from the job
        for item in self.job.starting_items:
            self.inventory.add_item(
                item,
                quantity=1,
                auto_equip=isinstance(item, Equipable),
            )

        # Refill current health/mana/stamina to their max
        caps = self.stats.effective()
        self.current_health = caps.get("health", 0)
        self.current_mana = caps.get("mana", 0)
        self.current_stamina = caps.get("stamina", 0)

    def update_stats(self) -> None:
        """
        Rebuild base stats from the assigned job, clearing any existing modifiers.
        """
        mods = self.job.stats_mods.copy()
        self.stats = Stats(mods)
        self.stats.clear_modifiers()  # Removes any legacy stat adjustments

    def assign_job(self, new_job_class: Callable[[int], Job], level: Optional[int] = None) -> None:
        """
        Change this Actor’s job, removing the old one first.
        """
        if self.job:
            self.remove_job()

        job_level = level if level is not None else self.levels.lvl
        self.job = new_job_class(job_level)
        self._initialize_job()

    def assign_job_by_id(self, job_id: str) -> Job:
        """
        Assign a job by its string ID. Raises ValueError if ID not found.
        """
        sample = create_job(job_id, self.levels.lvl)
        if sample is None:
            raise ValueError(f"Job with ID '{job_id}' not found.")
        self.assign_job(lambda lvl: create_job(job_id, lvl))
        return self.job

    def remove_job(self) -> None:
        """
        Remove current job and revert to a default Job, removing starting items.
        """
        old_job = self.job
        if not old_job:
            return

        # Remove starting items from inventory, if they exist
        for item in old_job.starting_items:
            try:
                self.inventory.remove_item(item, quantity=1)
            except KeyError:
                pass

        # Revert to the base Job
        self.job = Job(self.levels.lvl)
        self._initialize_job()

    def take_damage(self, amount: int) -> None:
        """
        Reduce current health by amount (clamped at zero). If health = 0, log defeat.
        """
        self.current_health = max(0, self.current_health - amount)
        if self.current_health == 0:
            print(f"{self.name} has been defeated!")
            log.info(f"{self.name} has been defeated!")

    def drain_mana(self, amount: int) -> None:
        """
        Reduce current mana by amount (clamped at zero).
        """
        self.current_mana = max(0, self.current_mana - amount)
        log.info(f"{self.name} drains {amount} mana ({self.current_mana}/{self.max_mana}).")

    def drain_stamina(self, amount: int) -> None:
        """
        Reduce current stamina by amount (clamped at zero).
        """
        self.current_stamina = max(0, self.current_stamina - amount)
        log.info(f"{self.name} drains {amount} stamina ({self.current_stamina}/{self.max_stamina}).")

    # ----------------------------
    # STAT PROPERTIES (with buffs)
    # ----------------------------

    @property
    def attack(self) -> int:
        """
        Total attack = base from stats + sum of active 'attack' buffs.
        """
        base = self.stats.effective().get("attack", 0)
        bonus = sum(eff.stat_mods.get("attack", 0) for eff in self.status_effects)
        return base + bonus

    @property
    def defense(self) -> int:
        """
        Total defense = base from stats + sum of active 'defense' buffs.
        """
        base = self.stats.effective().get("defense", 0)
        bonus = sum(eff.stat_mods.get("defense", 0) for eff in self.status_effects)
        return base + bonus

    @property
    def speed(self) -> int:
        """
        Total speed = base from stats + sum of active 'speed' buffs.
        """
        base = self.stats.effective().get("speed", 0)
        bonus = sum(eff.stat_mods.get("speed", 0) for eff in self.status_effects)
        return base + bonus

    @property
    def health(self) -> int:
        """Current health of the actor."""
        return getattr(self, "current_health", 0)

    @health.setter
    def health(self, value: int) -> None:
        """Set health, clamped between 0 and max_health."""
        max_h = self.max_health
        self.current_health = max(0, min(value, max_h))

    @property
    def max_health(self) -> int:
        """Maximum health from stats."""
        return self.stats.effective().get("health", 0)

    @property
    def mana(self) -> int:
        """Current mana of the actor."""
        return getattr(self, "current_mana", 0)

    @mana.setter
    def mana(self, value: int) -> None:
        """Set mana, clamped between 0 and max_mana."""
        max_m = self.max_mana
        self.current_mana = max(0, min(value, max_m))

    @property
    def max_mana(self) -> int:
        """Maximum mana from stats."""
        return self.stats.effective().get("mana", 0)

    @property
    def stamina(self) -> int:
        """Current stamina of the actor."""
        return getattr(self, "current_stamina", 0)

    @stamina.setter
    def stamina(self, value: int) -> None:
        """Set stamina, clamped between 0 and max_stamina."""
        max_s = self.max_stamina
        self.current_stamina = max(0, min(value, max_s))

    @property
    def max_stamina(self) -> int:
        """Maximum stamina from stats."""
        return self.stats.effective().get("stamina", 0)
