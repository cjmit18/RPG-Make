# game_sys/effects/base.py

"""
Effect base module.
Defines the abstract Effect class and a factory for instantiating
concrete Effect subclasses from data dictionaries.
"""

from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Any, Dict, TYPE_CHECKING

if TYPE_CHECKING:
    from game_sys.character.actor import Actor
    from game_sys.combat.combat_engine import CombatEngine


class Effect(ABC):
    """
    Base class for all effect types (status, damage, healing, etc.).
    Subclasses must implement `apply` and a matching `from_dict`.
    """

    @abstractmethod
    def apply(
        self,
        caster: Actor,
        target: Actor,
        combat_engine: CombatEngine | None = None
    ) -> str:
        """
        Apply this effect during combat or other contexts.
        Returns a descriptive message or result.
        """
        ...

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> Effect:
        """
        Factory method to create an Effect subclass based on the 'type' key.

        Args:
            data: Dictionary containing at least a 'type' field.

        Returns:
            An instance of a concrete Effect subclass.
        """
        et = data.get("type")
        if not et:
            raise ValueError("Effect data missing 'type' field")

        mrt = et.lower()
        # Map various type strings to the correct effect class
        if mrt in ("status", "applystatus"):
            from game_sys.effects.status import StatusEffect
            return StatusEffect.from_dict(data)
        if mrt == "damage":
            from game_sys.effects.damage import DamageEffect
            return DamageEffect.from_dict(data)
        if mrt.lower() == "damagereduction":
            from game_sys.effects.damage_reduction import DamageReductionEffect
            return DamageReductionEffect.from_dict(data)
        if mrt in ("temporarystatbuff",):
            from game_sys.effects.statbuff import TemporaryStatBuff
            return TemporaryStatBuff.from_dict(data)
        if mrt in ("modifyweapondamage",):
            from game_sys.effects.modify_weapon import ModifyWeaponDamageEffect
            return ModifyWeaponDamageEffect.from_dict(data)
        if mrt in ("heal",):
            from game_sys.effects.heal import HealEffect
            return HealEffect.from_dict(data)
        if mrt in ("instantheal",):
            from game_sys.effects.instant import InstantHeal
            return InstantHeal.from_dict(data)
        if mrt in ("instantmana",):
            from game_sys.effects.instant import InstantMana
            return InstantMana.from_dict(data)
        if mrt in ("unlock",):
            from game_sys.effects.unlock import UnlockEffect
            return UnlockEffect.from_dict(data)
        if mrt in ("lifestealpassive",):
            from game_sys.effects.passives.lifesteal import LifeStealPassive
            return LifeStealPassive.from_dict(data)

        raise ValueError(f"Unknown Effect type: {et}")
