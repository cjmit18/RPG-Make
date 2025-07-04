# game_sys/effects/base.py
"""
Module: game_sys.effects.base

Defines the abstract Effect class and a NullEffect no-op fallback.
"""
from abc import ABC, abstractmethod
from typing import Any, Dict
from game_sys.config.feature_flags import FeatureFlags
from game_sys.logging import effects_logger, log_exception

flags = FeatureFlags()


class Effect(ABC):
    """
    Base class for all effect types.
    """

    def __init__(self, id: str = ''):
        self.id = id
        effects_logger.debug(f"Created effect with ID: {id}")
        
    @abstractmethod
    def apply(self, caster: Any, target: Any,
                 combat_engine: Any = None) -> str:
        """
        Perform the effect. Returns a descriptive string.
        """
        ...

    def modify_damage(self, base_damage: float, attacker: Any, 
                        defender: Any) -> float:
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
    @log_exception
    def from_dict(cls, data: Dict[str, Any]) -> "Effect":
        """
        Factory: if effects are disabled, always return a NullEffect.
        Otherwise, dispatch on data['type'] to real effects.
        """
        if not flags.is_enabled("effects"):
            effects_logger.debug(
                "Effects disabled by feature flag, returning NullEffect"
            )
            return NullEffect()

        et = data.get("type")
        if not et:
            effects_logger.error("Effect data missing 'type' field")
            raise ValueError("Effect data missing 'type' field")

        # Dispatch logic omitted for brevity
        raise ValueError(f"Unknown Effect type: {et}")


class NullEffect(Effect):
    """
    No-op effect used when the 'effects' feature flag is off.
    """

    def apply(self, caster, target, combat_engine=None) -> str:
        effects_logger.debug(f"NullEffect applied from {caster} to {target}")
        return ""

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "NullEffect":
        effects_logger.debug("Creating NullEffect from dict")
        return cls()
