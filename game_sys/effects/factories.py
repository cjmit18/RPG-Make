# game_sys/effects/factory.py
"""
Module: game_sys.effects.factory

Parses JSON-like effect definitions and constructs Effect instances.
Validates definitions against `schemas.EFFECT_PARAMS` and dispatches to the registry.
"""
from typing import Dict, Any
from game_sys.effects.schemas import validate_effect_definition
from game_sys.effects.registry import EffectRegistry

class EffectFactory:
    """
    Responsible for creating Effect instances from dict definitions.
    """
    @staticmethod
    def create(defn: Dict[str, Any]):
        """
        Validate the definition and retrieve an Effect instance.

        Args:
            defn: A dict containing 'type' and 'params'.

        Returns:
            An Effect instance, or NullEffect if disabled or unknown.
        """
        # Schema validation
        validate_effect_definition(defn)

        # Retrieve raw type and params
        etype = defn['type']
        params = defn['params']

        # Lookup prototype via registry
        eff = EffectRegistry.get(etype)

        # Dynamically construct instance if constructor accepts params
        try:
            return eff.__class__(**params)
        except TypeError:
            # Fallback: return existing instance if no parameters needed
            return eff
