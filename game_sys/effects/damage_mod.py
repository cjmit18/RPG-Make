# game_sys/effects/damage_mod.py

from typing import Any
from game_sys.effects.base import Effect

class FlatDamageMod(Effect):
    """
    Adds a flat amount to the damage.
    """
    def __init__(self, amount: float = 0.0):
        super().__init__(id=f"flat_{amount}")
        self.amount = amount

    def modify_damage(self, damage: float, attacker: Any, defender: Any) -> float:
        return damage + self.amount

    def apply(self, caster: Any = None, target: Any = None, combat_engine: Any = None) -> str:
        # No direct “on-apply” behavior; this is used in the damage pipeline.
        return ""

class PercentDamageMod(Effect):
    """
    Multiplies damage by a percentage.
    """
    def __init__(self, multiplier: float = 1.0):
        super().__init__(id=f"percent_{multiplier}")
        self.multiplier = multiplier

    def modify_damage(self, damage: float, attacker: Any, defender: Any) -> float:
        return damage * self.multiplier

    def apply(self, caster: Any = None, target: Any = None, combat_engine: Any = None) -> str:
        return ""

class ElementalDamageMod(Effect):
    """
    Multiplies damage by a factor for a specific element.
    """
    def __init__(self, element: str, multiplier: float = 1.0):
        super().__init__(id=f"elemental_{element}_{multiplier}")
        self.element = element
        self.multiplier = multiplier

    def modify_damage(self, damage: float, attacker: Any, defender: Any) -> float:
        # Elemental resistances/weaknesses are handled later in ScalingManager
        return damage * self.multiplier

    def apply(self, caster: Any = None, target: Any = None, combat_engine: Any = None) -> str:
        return ""
