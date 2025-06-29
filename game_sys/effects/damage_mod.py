# game_sys/effects/damage_mod.py
"""
Module: game_sys.effects.damage_mod

Concrete damage‐modifying effects:
- FlatDamageMod: adds a flat bonus to base damage.
- PercentDamageMod: multiplies base damage by a percentage.
- ElementalDamageMod: applies an elemental multiplier to base damage.
"""
from typing import Any
from game_sys.effects.base import Effect

class FlatDamageMod(Effect):
    def __init__(self, amount: float = 0.0):
        super().__init__(id=f"flat_{amount}")
        self.amount = amount

    def modify_damage(self, base_damage: float, attacker: Any, defender: Any) -> float:
        return base_damage + self.amount

class PercentDamageMod(Effect):
    def __init__(self, multiplier: float = 1.0):
        super().__init__(id=f"percent_{multiplier}")
        self.multiplier = multiplier

    def modify_damage(self, base_damage: float, attacker: Any, defender: Any) -> float:
        return base_damage * self.multiplier

class ElementalDamageMod(Effect):
    def __init__(self, element: str = "NONE", multiplier: float = 1.0):
        super().__init__(id=f"elemental_{element}_{multiplier}")
        self.element = element
        self.multiplier = multiplier

    def modify_damage(self, base_damage: float, attacker: Any, defender: Any) -> float:
        # TODO: factor in defender.resistances[self.element] if desired
        return base_damage * self.multiplier
