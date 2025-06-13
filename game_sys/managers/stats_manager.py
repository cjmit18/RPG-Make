# game_sys/managers/stats_manager.py
"""
StatsManager: Handles experience accumulation,
level-ups, and stat calculations.
"""
from typing import Any, Dict
from game_sys.core.experience import Levels
from game_sys.core.stats import Stats
from game_sys.core.hooks import hook_dispatcher


class StatsManager:
    """
    Manages an actor's level, experience, and derived statistics.

    Responsibilities:
      - Track and modify experience and levels
      - Recalculate stats on level-up or job changes
      - Emit hooks for other systems to react
    """

    def __init__(self, actor: Any) -> None:
        """
        Initialize the StatsManager with the owning actor.

        Args:
            actor: The Actor instance this manager belongs to.
        """
        self.actor = actor
        # Initialize level/experience tracker
        self.levels: Levels = Levels(
            actor,
            getattr(actor, 'level', 1),
            getattr(actor, 'experience', 0)
        )
        # Compute initial stats
        self.stats: Stats = self.calculate_stats()

    def calculate_stats(self) -> Stats:
        """
        Compute and return a new Stats object based on current level, job,
        and any growth modifiers.
        Returns:
            Stats: The recalculated stats for the actor.
        """
        from game_sys.core.scaler import scale_stat
        from game_sys.core.rarity import Rarity

        stats_data: Dict[str, int] = {}
        # Use job-defined stat_mods (base value per stat) for scaling
        job = getattr(self.actor, 'job', None)
        if job and hasattr(job, 'stats_mods'):
            base_mods = job.stats_mods or {}
        else:
            base_mods = {}

        # Scale each stat using existing scale_stat logic
        level = self.levels.lvl
        grade = getattr(self.actor, 'grade', 1)
        rarity = getattr(self.actor, 'rarity', Rarity.COMMON)
        for stat_name, base_value in base_mods.items():
            # Wrap single value into tuple for deterministic scaling
            stats_data[stat_name] = scale_stat(
                (base_value, base_value),
                level=level,
                grade=grade,
                rarity=rarity,
            )

        # Ensure all stats from BaseJob exist
        try:
            from game_sys.jobs.base import Job as BaseJob
            for key in BaseJob.base_stats.keys():
                stats_data.setdefault(key, 0)
        except ImportError:
            pass

        return Stats(stats_data)

    def add_experience(self, amount: int) -> None:
        """
        Add experience points and handle level-ups.

        Args:
            amount: Experience points to add (must be non-negative).

        Raises:
            ValueError: If amount is negative.
        """
        if amount < 0:
            raise ValueError("Experience amount must be non-negative.")

        old_lvl = self.levels.lvl
        # Increase experience
        self.levels.experience = self.levels.experience + amount
        hook_dispatcher.fire(
            "character.experience_added", actor=self.actor, amount=amount
        )

        # Check for level-up
        new_lvl = self.levels.lvl
        if new_lvl > old_lvl:
            hook_dispatcher.fire(
                "character.level_up", actor=self.actor, new_level=new_lvl
            )
            # Recalculate stats on level-up
            self.stats = self.calculate_stats()
            hook_dispatcher.fire(
                "actor.stats_updated", actor=self.actor, stats=self.stats
            )

    def assign_job(self, job_id: str) -> None:
        """
        Assign a new job to the actor and recalculate stats.

        Args:
            job_id: Identifier of the job to assign.
        """
        # Delegate to actor.job_manager or job factory
        # TODO: Use JobManager instead to set actor.job
        if hasattr(self.actor, 'job_manager'):
            self.actor.job_manager.assign(job_id)
        else:
            # Fallback: directly set on actor
            from game_sys.jobs.factory import create_job
            self.actor.job = create_job(job_id)

        # Recalculate stats after job change
        self.stats = self.calculate_stats()
        hook_dispatcher.fire(
            "actor.stats_updated", actor=self.actor, stats=self.stats
        )
