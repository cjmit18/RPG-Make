# game_sys/effects/damage_reduction.py
from __future__ import annotations
from typing import Optional
from game_sys.core.actor import Actor

class DamageReductionEffect:
    """
    Reduces incoming damage by a fixed percentage for `duration` turns.
    """

    def __init__(
        self,
        percent: int,
        duration: int,
        target: Optional[str] = None
    ) -> None:
        self.percent   = percent
        self.duration  = duration
        self.target    = target  # e.g. "Self" or "Enemy"

    def apply(self, caster: Actor, target: Actor) -> None:
        # If the JSON said "applicable_to": "Self", we attach to caster, else to target
        actual_target = caster if self.target == "Self" else target
        # Wrap in a StatusEffect so that Actor.take_damage sees it:
        from game_sys.effects.status import StatusEffect
        stat_mods = {"DamageReduction": self.percent}
        actual_target.add_status(StatusEffect(name="DamageReduction", stat_mods=stat_mods, duration=self.duration))
