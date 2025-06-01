"""Stat Buff Effect Module
This module defines a temporary stat buff effect that modifies a target's stats for a limited duration.
"""
from game_sys.effects.base import Effect
from game_sys.combat.status import StatusEffect

class TemporaryStatBuff(Effect):
    """
    TemporaryStatBuff Effect
    This effect applies a temporary buff to a target's stat for a specified duration.
    It creates a StatusEffect that modifies the target's stats.
    """
    def __init__(self, stat_name: str, amount: int, duration: int):
        self.stat_name = stat_name
        self.amount = amount
        self.duration = duration

    def apply(self, source, target):
        # Create a StatusEffect and append to target
        buff_name = f"{source.name}-{self.stat_name}-{self.amount}-{self.duration}"
        status = StatusEffect(name=buff_name,
                              stat_mods={self.stat_name: self.amount},
                              duration=self.duration)
        target.status_effects.append(status)