# /mnt/data/status.py

from typing import Dict

class StatusEffect:
    """
    Represents a temporary buff (or debuff) that modifies one or more stats
    for a given number of turns.
    """
    def __init__(self, name: str, stat_mods: Dict[str, int], duration: int):
        """
        Args:
          name:       e.g. "Strength Brew Buff"
          stat_mods:  {"attack": +5, "defense": +2}
          duration:   how many turns this effect remains active
        """
        self.name = name
        self.stat_mods = stat_mods
        self.duration = duration  # in turns

    def tick(self) -> None:
        """Called once per turn; reduces remaining duration by 1."""
        self.duration -= 1

    def is_expired(self) -> bool:
        """Returns True if this effect’s duration has reached zero."""
        return self.duration <= 0
