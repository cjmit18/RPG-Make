"""Actor class for managing game characters, their jobs, stats, and inventory.
This class handles character creation, job assignment, stat management, and inventory operations."""

from typing import Type, Optional, Callable
from game_sys.core.inventory.inventory import Inventory
from game_sys.jobs.factory import create_job
from game_sys.jobs.base import Job
from game_sys.core.experience_functions import Levels
from game_sys.core.stats import Stats
from game_sys.items.item_base import Equipable
from logs.logs import get_logger
log = get_logger(__name__)
class Actor:
    def __init__(
        self,
        name: str,
        level: int = 1,
        experience: int = 0,
        job_class: Type[Job] = Job,
    ):
        self.name = name
        self.levels = Levels(self, level, experience)
        self.experience = experience
        # initialize stats with zeroed base values
        self.stats = Stats({stat: 0 for stat in Job.base_stats.keys()})
        self.inventory = Inventory(self)

        # initialize job
        self.job: Job = job_class(self.levels.lvl)
        self._initialize_job()

    def _initialize_job(self) -> None:
        """
        Apply job effects: set stats, add & auto-equip starting items, refill resources.
        """
        self.update_stats()
        # add and equip starting items
        for item in self.job.starting_items:
            self.inventory.add_item(
                item,
                quantity=1,
                auto_equip=isinstance(item, Equipable),
            )
        # refill resources to new maxima
        caps = self.stats.effective()
        self.current_health = caps.get("health", 0)
        self.current_mana = caps.get("mana", 0)
        self.current_stamina = caps.get("stamina", 0)

    def update_stats(self) -> None:
        """Rebuild base stats from job and clear existing modifiers."""
        for stat, val in self.job.stats_mods.items():
            self.stats.set_base(stat, val)
        self.stats.clear_modifiers()

    def assign_job(
        self,
        new_job_class: Callable[[int], Job],
        level: Optional[int] = None,
    ) -> None:
        """Change to a new job, removing the old one first."""
        if self.job:
            self.remove_job()

        job_level = level if level is not None else self.levels.lvl
        self.job = new_job_class(job_level)
        self._initialize_job()

    def assign_job_by_id(self, job_id: str) -> None:
        """Assign a job by its string ID."""
        sample = create_job(job_id, self.levels.lvl)
        if sample is None:
            raise ValueError(f"Job with ID '{job_id}' not found.")
        self.assign_job(lambda lvl: create_job(job_id, lvl))
        return self.job
    def remove_job(self) -> None:
        """Remove current job and revert to base job stats and items."""
        old_job = self.job
        if not old_job:
            return

        # remove starting items
        for item in old_job.starting_items:
            try:
                self.inventory.remove_item(item, quantity=1)
            except ValueError:
                pass

        # revert to base job
        self.job = Job(self.levels.lvl)
        self._initialize_job()

    def take_damage(self, amount: int) -> None:
        # clamp current_health to ≥0
        self.current_health = max(0, self.current_health - amount)

        # on death, print the defeat line
        if self.current_health == 0:
            print(f"{self.name} has been defeated!")
    def drain_mana(self, amount: int) -> None:
        """Reduce current mana by amount, clamping at zero."""
        self.mana -= amount
        log.info(f"{self.name} drains {amount} mana, mana now {self.mana}/{self.max_mana}")
    def drain_stamina(self, amount: int) -> None:
        """Reduce current stamina by amount, clamping at zero."""
        self.stamina -= amount
        log.info(f"{self.name} drains {amount} stamina, stamina now {self.stamina}/{self.max_stamina}")

    @property
    def attack(self) -> int:
        """Effective attack stat from base + modifiers."""
        return self.stats.effective().get("attack", 0)

    @property
    def defense(self) -> int:
        """Effective defense stat from base + modifiers."""
        return self.stats.effective().get("defense", 0)

    @property
    def speed(self) -> int:
        """Effective speed stat from base + modifiers."""
        return self.stats.effective().get("speed", 0)

    @property
    def health(self) -> int:
        """Current health of the actor."""
        return getattr(self, 'current_health', 0)

    @health.setter
    def health(self, value: int) -> None:
        """Setter for health: clamps between 0 and max_health."""
        max_h = self.max_health
        self.current_health = max(0, min(value, max_h))

    @property
    def max_health(self) -> int:
        """Maximum health from stats."""
        return self.stats.effective().get("health", 0)

    @property
    def mana(self) -> int:
        """Current mana of the actor."""
        return getattr(self, 'current_mana', 0)

    @mana.setter
    def mana(self, value: int) -> None:
        """Setter for mana: clamps between 0 and max_mana."""
        max_m = self.max_mana
        self.current_mana = max(0, min(value, max_m))

    @property
    def max_mana(self) -> int:
        """Maximum mana from stats."""
        return self.stats.effective().get("mana", 0)

    @property
    def stamina(self) -> int:
        """Current stamina of the actor."""
        return getattr(self, 'current_stamina', 0)

    @stamina.setter
    def stamina(self, value: int) -> None:
        """Setter for stamina: clamps between 0 and max_stamina."""
        max_s = self.max_stamina
        self.current_stamina = max(0, min(value, max_s))

    @property
    def max_stamina(self) -> int:
        """Maximum stamina from stats."""
        return self.stats.effective().get("stamina", 0)
