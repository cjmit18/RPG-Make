# game_sys/jobs/base.py

from typing import List, Dict


class Job:
    """
    Base Job class. Every concrete job must subclass this and set:
      - base_stats: Dict[str, int]   (e.g. {"health": 50, "attack": 10, ...})
      - starting_items: List[object]  (list of item objects to give/equip on assign)
      - name: str                     (human-readable job name)
      - stats_mods (optional)         (used by Character.assign_job_by_id)
    """

    # Example default—concrete subclasses should override this:
    base_stats: Dict[str, int] = {
        "health": 0,
        "mana": 0,
        "stamina": 0,
        "attack": 0,
        "defense": 0,
        "speed": 0,
        "intellect": 0,
    }

    starting_items: List[object] = []
    stats_mods: Dict[str, int] = {}

    def __init__(self, level: int) -> None:
        self.level = level
        # Concrete subclasses can scale base_stats/stats_mods by level if needed.

    @property
    def name(self) -> str:
        """
        Return the job's internal name (typically the class name in lowercase).
        Concrete subclasses can override if they want a different display name.
        """
        return self.__class__.__name__.lower()
