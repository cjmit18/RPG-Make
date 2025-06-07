# game_sys/effects/base.py

from abc import ABC, abstractmethod
from typing import Any, Dict, TYPE_CHECKING

if TYPE_CHECKING:
    from game_sys.character.actor import Actor
    from game_sys.combat.combat import CombatCapabilities


class Effect(ABC):
    @abstractmethod
    def apply(self, caster: "Actor", target: "Actor", combat_engine: "CombatCapabilities") -> str:
        """
        Every Effect subclass must implement this. Returns a log string describing what happened.
        """
        pass

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Effect":
        """
        Dispatch to the correct subclass based on data["type"].
        """
        effect_type = data.get("type")

        if effect_type == "Damage":
            from game_sys.effects.damage import DamageEffect
            return DamageEffect.from_dict(data)

        if effect_type == "ApplyStatus":
            from game_sys.effects.status import StatusEffect
            return StatusEffect.from_dict(data)

        if effect_type == "TemporaryStatBuff":
            from game_sys.effects.statbuff import TemporaryStatBuff
            return TemporaryStatBuff.from_dict(data)

        if effect_type == "ModifyWeaponDamage":
            from game_sys.effects.modify_weapon import ModifyWeaponDamageEffect
            return ModifyWeaponDamageEffect.from_dict(data)

        if effect_type == "DamageReduction":
            from game_sys.effects.damage_reduction import DamageReductionEffect
            return DamageReductionEffect.from_dict(data)

        if effect_type == "Unlock":
            from game_sys.effects.unlock import UnlockEffect
            return UnlockEffect.from_dict(data)

        if effect_type == "InstantHeal":
            from game_sys.effects.instant import InstantHeal
            return InstantHeal.from_dict(data)

        if effect_type == "InstantMana":
            from game_sys.effects.instant import InstantMana
            return InstantMana.from_dict(data)

        if effect_type == "Heal":
            from game_sys.effects.heal import HealEffect
            return HealEffect.from_dict(data)

        raise ValueError(f"Unknown Effect type: {effect_type}")
