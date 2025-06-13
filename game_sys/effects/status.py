# game_sys/effects/status.py

"""
StatusEffect module.

Defines a temporary buff/debuff effect that modifies an actor's stats
for a fixed duration (in turns), with ticking and expiration.
"""

from __future__ import annotations
from typing import Dict, Any, TYPE_CHECKING
from game_sys.effects.base import Effect
from game_sys.core.hooks import hook_dispatcher

if TYPE_CHECKING:
    from game_sys.character.actor import Actor
    from game_sys.combat.combat_engine import CombatEngine


class StatusEffect(Effect):
    """
    A temporary buff/debuff that modifies stats for a set number of turns.
    """

    def __init__(self, name: str, stat_mods: Dict[str, int], duration: int) -> None:
        self.name = name
        self.stat_mods = stat_mods
        self.duration = duration

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> StatusEffect:
        """
        Deserialize a StatusEffect from a data dictionary.

        Expected data keys:
          - type: one of "status", "ApplyStatus", or any casing variant
          - name: str
          - stat_mods: Dict[str, int]
          - duration: int

        Args:
            data: The serialized effect dict.

        Returns:
            A new StatusEffect instance.
        """
        et = data.get("type", "")
        if et.lower() not in ("status", "applystatus"):
            raise ValueError(f"Invalid type for StatusEffect: {data.get('type')}")
        name = data.get("name")
        stat_mods = data.get("stat_mods", {})
        duration = int(data.get("duration", 0))
        return cls(name=name, stat_mods=stat_mods, duration=duration)

    def apply(
        self,
        caster: Actor,
        target: Actor,
        combat_engine: CombatEngine | None = None
    ) -> str:
        """
        Attach this status to the target actor and fire the apply hook.

        Returns:
            A descriptive message of the application.
        """
        target.add_status(self)
        hook_dispatcher.fire("effect.apply", target=target, effect=self)
        return f"{target.name} gains status '{self.name}' for {self.duration} turns."

    def tick(self) -> None:
        """
        Advance this effect by one turn (reduce duration) and fire tick hook.
        """
        self.duration -= 1
        hook_dispatcher.fire("effect.tick", effect=self)

    def is_expired(self) -> bool:
        """
        Check whether this effect has run its course.

        Returns:
            True if duration ≤ 0, False otherwise.
        """
        return self.duration <= 0
