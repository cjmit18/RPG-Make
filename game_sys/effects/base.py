# game_sys/effects/base.py

from __future__ import annotations
from typing import Any, Dict, Optional, Type

from game_sys.core.actor import Actor
from game_sys.combat.status import StatusEffect
from game_sys.effects.damage import DamageEffect
from game_sys.effects.heal import HealEffect
from game_sys.effects.modify_weapon import ModifyWeaponDamageEffect
from game_sys.effects.damage_reduction import DamageReductionEffect
from game_sys.effects.unlock import UnlockEffect


class ApplyStatusEffect:
    """
    When applied, creates and attaches a StatusEffect to the target actor.
    """

    def __init__(
        self,
        status_name: str,
        duration: int,
        stat_mods: Optional[Dict[str, int]] = None,
    ) -> None:
        self.status_name: str = status_name
        self.duration: int = duration
        self.stat_mods: Dict[str, int] = stat_mods or {}

    def apply(self, caster: Actor, target: Actor) -> None:
        """
        Attach a new StatusEffect to `target` with the given name, modifiers, and duration.
        """
        status = StatusEffect(
            name=self.status_name,
            stat_mods=self.stat_mods,
            duration=self.duration,
        )
        target.add_status(status)


class Effect:
    """
    Base class for all Effects. `from_dict(...)` returns an instance
    whose class implements `apply(caster: Actor, target: Actor)`.
    """

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> Effect:
        """
        Deserialize a dictionary into the appropriate Effect subclass.

        Supported "type" values (case-sensitive):
          - "ApplyStatus"
          - "Damage"
          - "ModifyWeaponDamage"
          - "Heal"
          - "DamageReduction"
          - "Unlock"

        Raises:
            ValueError: if required fields are missing or have incorrect types.
        """
        effect_type = data.get("type", "").strip()

        # 1) APPLY STATUS
        if effect_type == "ApplyStatus":
            status_name = data.get("status")
            duration = data.get("duration")
            stat_mods = data.get("stat_mods", {})

            if not isinstance(status_name, str):
                raise ValueError(f"ApplyStatus requires 'status' as str, got {status_name!r}")
            if not isinstance(duration, int):
                raise ValueError(f"ApplyStatus requires 'duration' as int, got {duration!r}")
            if not isinstance(stat_mods, dict):
                raise ValueError(f"ApplyStatus 'stat_mods' must be dict, got {stat_mods!r}")

            return ApplyStatusEffect(
                status_name=status_name,
                duration=duration,
                stat_mods=stat_mods,
            )

        # 2) DAMAGE
        if effect_type == "Damage":
            value = data.get("value")
            multiplier = data.get("multiplier", 1.0)
            requires_status = data.get("requires_status", None)

            if not isinstance(value, int):
                raise ValueError(f"Damage requires 'value' as int, got {value!r}")
            if not isinstance(multiplier, (int, float)):
                raise ValueError(f"Damage requires 'multiplier' as int or float, got {multiplier!r}")
            if requires_status is not None and not isinstance(requires_status, str):
                raise ValueError(f"Damage optional 'requires_status' must be str, got {requires_status!r}")

            return DamageEffect(
                amount=value,
                multiplier=float(multiplier),
                requires_status=requires_status,
            )

        # 3) MODIFY WEAPON DAMAGE
        if effect_type == "ModifyWeaponDamage":
            weapon_type = data.get("weapon_type")
            percent_bonus = data.get("percent_bonus")

            if not isinstance(weapon_type, str):
                raise ValueError(f"ModifyWeaponDamage requires 'weapon_type' as str, got {weapon_type!r}")
            if not isinstance(percent_bonus, (int, float)):
                raise ValueError(f"ModifyWeaponDamage requires 'percent_bonus' as int or float, got {percent_bonus!r}")

            return ModifyWeaponDamageEffect(
                weapon_type=weapon_type,
                percent_bonus=float(percent_bonus),
            )

        # 4) HEAL
        if effect_type == "Heal":
            value = data.get("value")
            if not isinstance(value, int):
                raise ValueError(f"Heal requires 'value' as int, got {value!r}")

            return HealEffect(amount=value)

        # 5) DAMAGE REDUCTION
        if effect_type == "DamageReduction":
            value = data.get("value")
            duration = data.get("duration")
            applicable_to = data.get("applicable_to", None)

            if not isinstance(value, int):
                raise ValueError(f"DamageReduction requires 'value' as int, got {value!r}")
            if not isinstance(duration, int):
                raise ValueError(f"DamageReduction requires 'duration' as int, got {duration!r}")
            if applicable_to is not None and not isinstance(applicable_to, str):
                raise ValueError(f"DamageReduction optional 'applicable_to' must be str, got {applicable_to!r}")

            return DamageReductionEffect(
                percent=value,
                duration=duration,
                target=applicable_to,
            )

        # 6) UNLOCK
        if effect_type == "Unlock":
            target_type = data.get("target_type")
            if not isinstance(target_type, str):
                raise ValueError(f"Unlock requires 'target_type' as str, got {target_type!r}")

            return UnlockEffect(target_type=target_type)

        # 7) FALLBACK: UNRECOGNIZED TYPE
        raise ValueError(f"Unknown Effect type: {effect_type}")
