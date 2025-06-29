# game_sys/effects/stat_bonus.py
"""
Module: game_sys.effects.stat_bonus

Concrete stat‐bonus effect: adds a flat bonus to a named stat.
"""
from typing import Any
from game_sys.effects.base import Effect

class StatBonusEffect(Effect):
    def __init__(self, stat: str = "", amount: float = 0.0):
        super().__init__(id=f"stat_bonus_{stat}_{amount}")
        self.stat = stat
        self.amount = amount

    def modify_stat(self, base_stat: float, actor: Any) -> float:
        return base_stat + self.amount
