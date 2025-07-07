# game_sys/effects/registry.py

from typing import Dict, Type
from game_sys.effects.base import Effect, NullEffect
from game_sys.logging import effects_logger, log_exception

from game_sys.effects.extensions import (
    HealEffect,
    BuffEffect,
    DebuffEffect,
    StatusEffect,
    StatBonusEffect,
    InstantManaEffect,
    ResourceDrainEffect,
    EquipmentStatEffect,
    RegenerationEffect
)
from game_sys.effects.damage_mod import (
    FlatDamageMod,
    PercentDamageMod,
    ElementalDamageMod
)
from game_sys.effects.status_effects import (
    BurnEffect,
    PoisonEffect,
    StunEffect,
    FearEffect,
    SlowEffect,
    FreezeEffect,
    HasteEffect,
    SilenceEffect,
    WeakenEffect,
    BerserkEffect,
    ProtectionEffect,
    InvisibilityEffect,
    ParalyzeEffect,
    SleepEffect
)

_effect_map: Dict[str, Type[Effect]] = {
    # flat/percent/elemental use create_from_id
    'flat':        FlatDamageMod,
    'percent':     PercentDamageMod,
    'elemental':   ElementalDamageMod,

    # JSON-defined effects
    'heal':        HealEffect,
    'buff':        BuffEffect,
    'debuff':      DebuffEffect,
    'status':      StatusEffect,
    'instant_mana': InstantManaEffect,

    # passive-system effects
    'stat_bonus':     StatBonusEffect,
    'resource_drain': ResourceDrainEffect,
    'equipment_stat': EquipmentStatEffect,
    'regeneration':   RegenerationEffect,
    
    # Status flag effects
    'burn':        BurnEffect,
    'poison':      PoisonEffect,
    'stun':        StunEffect,
    'fear':        FearEffect,
    'slow':        SlowEffect,
    'freeze':      FreezeEffect,
    'haste':       HasteEffect,
    'silence':     SilenceEffect,
    'weaken':      WeakenEffect,
    'berserk':     BerserkEffect,
    'protection':  ProtectionEffect,
    'invisibility': InvisibilityEffect,
    'paralyze':    ParalyzeEffect,
    'sleep':       SleepEffect,
}


class EffectRegistry:
    """
    Central lookup for effect type → concrete class.
    """
    _registry = _effect_map

    @classmethod
    @log_exception
    def get(cls, etype: str) -> Effect:
        eff_cls = cls._registry.get(etype)
        if eff_cls:
            try:
                effects_logger.debug(f"Creating effect of type: {etype}")
                return eff_cls()  # fallback no-arg instantiation
            except TypeError:
                effects_logger.warning(
                    f"Failed to create effect of type {etype}, "
                    f"falling back to NullEffect"
                )
                return NullEffect()
        effects_logger.warning(
            f"Unknown effect type: {etype}, returning NullEffect"
        )
        return NullEffect()
