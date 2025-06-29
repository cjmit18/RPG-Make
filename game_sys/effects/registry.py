# game_sys/effects/registry.py
"""
Module: game_sys.effects.registry

Central registry mapping effect type IDs to their corresponding Effect classes.
No internal circular imports — only pulls in base effects and extensions.
"""
from typing import Type, Dict
from game_sys.config.feature_flags import FeatureFlags
from game_sys.effects.base import Effect, NullEffect
from game_sys.effects.damage_mod import FlatDamageMod, PercentDamageMod, ElementalDamageMod
from game_sys.effects.stat_bonus import StatBonusEffect
from game_sys.effects.extensions import HealEffect, BuffEffect, DebuffEffect, StatusEffect

flags = FeatureFlags()

class EffectRegistry:
    """
    Maps string effect IDs to Effect classes. Instantiate via get().
    """
    _registry: Dict[str, Type[Effect]] = {}

    @classmethod
    def register(cls, effect_id: str, effect_cls: Type[Effect]):
        """Register an Effect subclass under a given ID."""
        cls._registry[effect_id] = effect_cls

    @classmethod
    def get(cls, effect_id: str) -> Effect:
        """
        Retrieve a fresh Effect instance for the given ID.
        Returns NullEffect if effects are disabled or ID is unknown.
        """
        if not flags.is_enabled('effects'):
            return NullEffect()

        effect_cls = cls._registry.get(effect_id)
        if effect_cls is None:
            return NullEffect()

        try:
            return effect_cls()
        except Exception:
            return NullEffect()

# Register built-in damage mods
EffectRegistry.register('flat',      FlatDamageMod)
EffectRegistry.register('percent',   PercentDamageMod)
EffectRegistry.register('elemental', ElementalDamageMod)
# Register stat bonus
EffectRegistry.register('stat_bonus', StatBonusEffect)
# Register extensions
EffectRegistry.register('heal',   HealEffect)
EffectRegistry.register('buff',   BuffEffect)
EffectRegistry.register('debuff', DebuffEffect)
EffectRegistry.register('status', StatusEffect)
