"""Actor class for managing game characters, their jobs, stats, and inventory.
This class handles character creation, job assignment, stat management, and inventory operations."""

from typing import Type, Optional, Callable
from game_sys.core.inventory_functions import Inventory
from game_sys.jobs.factory import create_job
from game_sys.jobs.base import Job
from game_sys.core.experience_functions import Levels
from game_sys.core.stats import Stats
from game_sys.items.item_base import Equipable

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
        # initialize stats with base zeros
        self.stats = Stats({stat: 0 for stat in Job.base_stats.keys()})
        self.inventory = Inventory(self)

        # initialize job
        self.job: Job = job_class(self.levels.lvl)
        self._initialize_job()

    def _initialize_job(self) -> None:
        """
        Apply job effects: set stats, add & auto-equip starting items, refill resources.
        """
        # rebuild stats
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
        # set base stats
        for stat, val in self.job.stats_mods.items():
            self.stats.set_base(stat, val)
        # clear existing modifiers
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
        self.assign_job(lambda lvl: create_job(job_id, lvl))

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
        """Reduce current health by amount, clamping at zero, and report defeat."""
        self.current_health = max(self.current_health - amount, 0)
        if self.current_health == 0:
            print(f"{self.name} has been defeated!")

    def drain_mana(self, amount: int) -> None:
        """Reduce current mana by amount, clamping at zero."""
        self.current_mana = max(self.current_mana - amount, 0)
