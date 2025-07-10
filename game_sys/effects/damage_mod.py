# game_sys/effects/damage_mod.py

from typing import Any
from game_sys.effects.base import Effect
from game_sys.logging import effects_logger

class FlatDamageMod(Effect):
    async def apply_async(self, caster: Any = None, target: Any = None, combat_engine: Any = None) -> str:
        if hasattr(self, 'on_pre_apply_async') and callable(getattr(self, 'on_pre_apply_async')):
            await self.on_pre_apply_async(caster, target)
        result = self.apply(caster, target, combat_engine)
        if hasattr(self, 'on_post_apply_async') and callable(getattr(self, 'on_post_apply_async')):
            await self.on_post_apply_async(caster, target, result)
        return result
    """
    Adds a flat amount to the damage.
    """
    def __init__(self, amount: float = 0.0):
        super().__init__(id=f"flat_{amount}")
        self.amount = amount
        effects_logger.debug(f"Created FlatDamageMod with amount: {amount}")

    def modify_damage(self, damage: float, attacker: Any, defender: Any) -> float:
        new_damage = damage + self.amount
        effects_logger.debug(
            f"FlatDamageMod: {damage} -> {new_damage} (added {self.amount})"
        )
        return new_damage

    def apply(self, caster: Any = None, target: Any = None, 
              combat_engine: Any = None) -> str:
        # No direct "on-apply" behavior; this is used in the damage pipeline.
        effects_logger.debug(
            f"Applied FlatDamageMod to {target.name if target else 'unknown'}"
        )
        return ""


class PercentDamageMod(Effect):
    async def apply_async(self, caster: Any = None, target: Any = None, combat_engine: Any = None) -> str:
        if hasattr(self, 'on_pre_apply_async') and callable(getattr(self, 'on_pre_apply_async')):
            await self.on_pre_apply_async(caster, target)
        result = self.apply(caster, target, combat_engine)
        if hasattr(self, 'on_post_apply_async') and callable(getattr(self, 'on_post_apply_async')):
            await self.on_post_apply_async(caster, target, result)
        return result
    """
    Multiplies damage by a percentage.
    """
    def __init__(self, multiplier: float = 1.0):
        super().__init__(id=f"percent_{multiplier}")
        self.multiplier = multiplier
        effects_logger.debug(f"Created PercentDamageMod with multiplier: {multiplier}")

    def modify_damage(self, damage: float, attacker: Any, defender: Any) -> float:
        new_damage = damage * self.multiplier
        effects_logger.debug(
            f"PercentDamageMod: {damage} -> {new_damage} (multiplier: {self.multiplier})"
        )
        return new_damage

    def apply(self, caster: Any = None, target: Any = None, 
              combat_engine: Any = None) -> str:
        effects_logger.debug(
            f"Applied PercentDamageMod to {target.name if target else 'unknown'}"
        )
        return ""

class ElementalDamageMod(Effect):
    async def apply_async(self, caster: Any = None, target: Any = None, combat_engine: Any = None) -> str:
        if hasattr(self, 'on_pre_apply_async') and callable(getattr(self, 'on_pre_apply_async')):
            await self.on_pre_apply_async(caster, target)
        result = self.apply(caster, target, combat_engine)
        if hasattr(self, 'on_post_apply_async') and callable(getattr(self, 'on_post_apply_async')):
            await self.on_post_apply_async(caster, target, result)
        return result
    """
    Multiplies damage by a factor for a specific element.
    """
    def __init__(self, element: str, multiplier: float = 1.0):
        super().__init__(id=f"elemental_{element}_{multiplier}")
        self.element = element
        self.multiplier = multiplier
        effects_logger.debug(
            f"Created ElementalDamageMod: {element} with multiplier: {multiplier}"
        )

    def modify_damage(self, damage: float, attacker: Any, defender: Any) -> float:
        # Elemental resistances/weaknesses are handled later in ScalingManager
        new_damage = damage * self.multiplier
        effects_logger.debug(
            f"ElementalDamageMod({self.element}): {damage} -> {new_damage}"
        )
        return new_damage

    def apply(self, caster: Any = None, target: Any = None, 
              combat_engine: Any = None) -> str:
        effects_logger.debug(
            f"Applied ElementalDamageMod({self.element}) to "
            f"{target.name if target else 'unknown'}"
        )
        return ""
