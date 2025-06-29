# game_sys/effects/factory.py

import re
from typing import Any, Dict
from game_sys.effects.registry import EffectRegistry
from game_sys.effects.base import NullEffect
from game_sys.effects.schemas import validate_effect_definition

class EffectFactory:
    """
    Builds Effect instances from either:
      - Full JSON definitions (dicts with 'type' + 'params')
      - Simple ID strings like "flat_2" or "elemental_FIRE_1.2"
    """

    @staticmethod
    def create(defn: Dict[str, Any]) -> Any:
        """
        Instantiate an effect from a JSON-style dict:
            { "type": str, "params": {...} }
        """
        validate_effect_definition(defn)
        etype = defn["type"]
        params = defn["params"]
        cls = EffectRegistry._registry.get(etype)
        if cls:
            try:
                return cls(**params)
            except Exception:
                # fallback to parameterless or NullEffect
                return EffectRegistry.get(etype)
        return EffectRegistry.get(etype)

    @staticmethod
    def create_from_id(eid: str) -> Any:
        """
        Instantiate a flat/percent/elemental mod from its ID string,
        or delegate to the registry for other IDs.
        """
        parts = eid.split("_")
        etype = parts[0]
        if etype == "flat":
            amt = float(parts[1]) if len(parts) > 1 else 0.0
            cls = EffectRegistry._registry.get("flat")
            return cls(amount=amt) if cls else NullEffect()
        if etype == "percent":
            mul = float(parts[1]) if len(parts) > 1 else 1.0
            cls = EffectRegistry._registry.get("percent")
            return cls(multiplier=mul) if cls else NullEffect()
        if etype == "elemental" and len(parts) >= 3:
            elem = parts[1]
            mul  = float(parts[2])
            cls = EffectRegistry._registry.get("elemental")
            return cls(element=elem, multiplier=mul) if cls else NullEffect()
        # fallback: heal, buff, debuff, status, etc.
        return EffectRegistry.get(eid)
