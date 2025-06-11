# game_sys/jobs/base.py

from typing import List, Dict, Any, Optional


class Job:
    """
    Base Job class. Every concrete job must subclass this and set:
      - base_stats: Dict[str, int]   (e.g. {"health": 50, "attack": 10, ...})
      - starting_items: List[Any]
        (list of item objects to give/equip on assign)
      - starting_skills: List[Any]
        (optional list of skill IDs to grant at start)
      - name: str                     (human-readable job name)
    """
    # Default template stats (override per subclass or via base_stats arg)
    base_stats: Dict[str, int] = {
        "health": 0,
        "attack": 0,
        "defense": 0,
        "speed": 0,
        "mana": 0,
        "stamina": 0,
        "intellect": 0,
    }
    starting_items: List[Any] = []
    starting_skills: List[Any] = []
    stats_mods: Dict[str, int] = {}

    def __init__(
        self,
        level: int,
        base_stats: Optional[Dict[str, int]] = None,
        starting_items: Optional[List[Any]] = None,
        job_id: Optional[str] = None,
    ) -> None:
        """
        Initialize a Job instance.

        Args:
            level: Character level for reference or scaling.
            base_stats: Optional override dict of stat_name → base value.
            starting_items: Optional list of item objects to equip on assign.
            job_id: Internal ID for the job template.
        """
        self.level = level
        # Use passed-in stats_mods if provided,
        # else default to class base_stats
        if base_stats is not None:
            self.stats_mods = base_stats
        else:
            self.stats_mods = dict(self.base_stats)
        # Set instance starting_items and record job_id
        self.starting_items = starting_items or []
        self.job_id = job_id or self.__class__.__name__.lower()

    @property
    def name(self) -> str:
        """
        Return the job's internal ID if set; otherwise class name in lowercase.
        """
        return getattr(self, "job_id", self.__class__.__name__.lower())
