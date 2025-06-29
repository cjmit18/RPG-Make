# game_sys/effects/base.py
"""
Module: game_sys.effects.base

Defines the abstract Effect class and a NullEffect no-op fallback.
"""
from abc import ABC, abstractmethod
from typing import Any, Dict
from game_sys.config.feature_flags import FeatureFlags

flags = FeatureFlags()

class Effect(ABC):
    """
    Base class for all effect types.
    """

    def __init__(self, id: str = ''):
        self.id = id
    @abstractmethod
    def apply(self, caster: Any, target: Any, combat_engine: Any = None) -> str:
        """
        Perform the effect. Returns a descriptive string.
        """
        ...

    def modify_damage(self, base_damage: float, attacker: Any, defender: Any) -> float:
        """
        Modify damage. Default: no change.
        """
        return base_damage

    def modify_stat(self, base_stat: float, actor: Any) -> float:
        """
        Modify a stat value. Default: no change.
        """
        return base_stat

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Effect":
        """
        Factory: if effects are disabled, always return a NullEffect.
        Otherwise, dispatch on data['type'] to real effects.
        """
        if not flags.is_enabled("effects"):
            return NullEffect()

        et = data.get("type")
        if not et:
            raise ValueError("Effect data missing 'type' field")

        # Dispatch logic omitted for brevity
        raise ValueError(f"Unknown Effect type: {et}")

class NullEffect(Effect):
    """
    No-op effect used when the 'effects' feature flag is off.
    """

    def apply(self, caster, target, combat_engine=None) -> str:
        return ""

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "NullEffect":
        return cls()
