# game_sys/effects/status.py

from typing import Dict, Any
from game_sys.character.actor import Actor
from game_sys.combat.combat import CombatCapabilities
from game_sys.effects.base import Effect


class StatusEffect(Effect):
    """
    Represents a temporary buff (or debuff) that modifies one or more stats
    for a given number of turns.

    JSON:
      {
        "type": "ApplyStatus",
        "status": "<StatusName>",
        "stat_mods": { "attack": +5, ... },
        "duration": <int>
      }
    """

    def __init__(self, name: str, stat_mods: Dict[str, int], duration: int):
        self.name = name
        self.stat_mods = stat_mods
        self.duration = duration

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "StatusEffect":
        name = data.get("status", "")
        stat_mods = data.get("stat_mods", {}) or {}
        duration = int(data.get("duration", 0))
        return cls(name=name, stat_mods=stat_mods, duration=duration)

    def apply(self, caster: Actor, target: Actor, combat_engine: CombatCapabilities) -> str:
        """
        Apply this status to 'target'. Uses Actor.add_status(...) if available,
        or appends to target.status_effects otherwise.
        """
        try:
            target.add_status(self.name, self.stat_mods, self.duration)
        except AttributeError:
            if not hasattr(target, "status_effects"):
                target.status_effects = []
            target.status_effects.append(self)
        return f"{target.name} gains status '{self.name}' for {self.duration} turns."
