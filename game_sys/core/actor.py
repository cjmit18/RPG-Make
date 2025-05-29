# game_sys/core/actor.py

from typing import Type, Optional
from game_sys.core.inventory_functions import Inventory
from game_sys.jobs.base import Job
from game_sys.core.experience_functions import Levels  # assuming you have a Levels class managing levels/experience
from game_sys.core.stats import Stats  # assuming you have a Stats class managing stats/bonuses

class Actor:
    def __init__(self, name: str, level: int = 1, experience: int = 0, job_class: Type[Job] = Job):
        self.name       = name
        self.levels     = Levels(self, level, experience)  # your existing Levels setup
        self.experience = experience
        # stats: holds base + modifiers
        self.stats      = Stats({s: 0 for s in Job.base_stats.keys()})
        self.inventory  = Inventory(self)

        # initialize job
        # pass in numeric level, not the actor itself
        self.job: Optional[Job] = job_class(self.levels.lvl)

        # build stats and gear
        self.update_stats()
        # auto-equip starting job items
        from game_sys.items.item_base import Equipable
        for item in self.job.starting_items:
            self.inventory.add_item(item, quantity=1, auto_equip=isinstance(item, Equipable))
    #--- Refill Health/Mana/Stamina ---
        maxs = self.stats.effective()
        self.current_health =  maxs.get('health', 0)
        self.current_mana   =  maxs.get('mana', 0)
        self.current_stamina = maxs.get('stamina', 0)

    def update_stats(self) -> None:
        """Rebuild stats from job then clear/apply modifiers."""
        # 1) apply job base_stats (scaled by level)
        for stat, val in self.job.stats_mods.items():
            self.stats.set_base(stat, val)
        # 2) clear any existing modifiers
        self.stats.clear_modifiers()

    def assign_job(self, new_job_class: Type[Job], level: Optional[int] = None) -> None:
        """Change to a new job at runtime, removing the old one first."""
        if self.job:
            self.remove_job()

        job_level       = level if level is not None else self.levels.lvl
        self.job        = new_job_class(job_level)

        # rebuild stats & re-equip
        self.update_stats()
        from game_sys.items.item_base import Equipable
        for item in self.job.starting_items:
            self.inventory.add_item(item, quantity=1, auto_equip=isinstance(item, Equipable))
        
        # 4) refill current health/mana/stamina to max
        maxs = self.stats.effective()
        self.current_health = maxs.get('health', 0)
        self.current_mana   = maxs.get('mana', 0)
        self.current_stamina = maxs.get('stamina', 0)

    def remove_job(self) -> None:
        """Strip stat mods and remove job items."""
        old_job = self.job
        if not old_job:
            return
        
        # 1) Take away starting items
        for item in old_job.starting_items:
            try:
                self.inventory.remove_item(item, quantity=1)
            except ValueError:
                # Item not found, ignore
                pass
        # 2) revert to base job and rebuild stats
        from game_sys.jobs.base import Job as BaseJob
        self.job = BaseJob(self.levels.lvl)
        self.update_stats()
    def take_damage(self, amount: int) -> None:
        """
        Reduce current health by `amount`, clamping at zero.
        If health hits zero, print a defeat message.
        """
        self.current_health = max(self.current_health - amount, 0)
        if self.current_health == 0:
            # This must match the test’s expectation exactly:
            print(f"{self.name} has been defeated!")
    def drain_mana(self, amount: int) -> None:
        """
        Reduce current mana by `amount`, clamping at zero.
        """
        self.current_mana = max(self.current_mana - amount, 0)