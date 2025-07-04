# game_sys/effects/factory.py

import re
from typing import Any, Dict
from game_sys.effects.registry import EffectRegistry
from game_sys.effects.base import NullEffect
from game_sys.effects.schemas import validate_effect_definition
from game_sys.logging import effects_logger, log_exception


class EffectFactory:
    """
    Builds Effect instances from either:
      - Full JSON definitions (dicts with 'type' + 'params')
      - Simple ID strings like "flat_2" or "elemental_FIRE_1.2"
    """

    @staticmethod
    @log_exception
    def create(defn: Dict[str, Any]) -> Any:
        """
        Instantiate an effect from a JSON-style dict:
            { "type": str, "params": {...} }
        """
        effects_logger.debug(f"Creating effect from definition: {defn}")
        validate_effect_definition(defn)
        etype = defn["type"]
        params = defn["params"]
        cls = EffectRegistry._registry.get(etype)
        if cls:
            try:
                effect = cls(**params)
                effects_logger.info(
                    f"Created {etype} effect with params: {params}"
                )
                return effect
            except Exception as e:
                effects_logger.warning(
                    f"Failed to create {etype} effect: {e}, "
                    f"falling back to parameterless"
                )
                # fallback to parameterless or NullEffect
                return EffectRegistry.get(etype)
        effects_logger.warning(f"No class registered for effect type: {etype}")
        return EffectRegistry.get(etype)

    @staticmethod
    @log_exception
    def create_from_id(eid: str) -> Any:
        """
        Instantiate a flat/percent/elemental mod from its ID string,
        or delegate to the registry for other IDs.
        """
        effects_logger.debug(f"Creating effect from ID: {eid}")
        parts = eid.split("_")
        etype = parts[0]
        if etype == "flat":
            amt = float(parts[1]) if len(parts) > 1 else 0.0
            cls = EffectRegistry._registry.get("flat")
            effects_logger.debug(f"Creating flat damage mod with amount={amt}")
            return cls(amount=amt) if cls else NullEffect()
        if etype == "percent":
            mul = float(parts[1]) if len(parts) > 1 else 1.0
            cls = EffectRegistry._registry.get("percent")
            effects_logger.debug(f"Creating percent damage mod with multiplier={mul}")
            return cls(multiplier=mul) if cls else NullEffect()
        if etype == "elemental" and len(parts) >= 3:
            elem = parts[1]
            mul = float(parts[2])
            cls = EffectRegistry._registry.get("elemental")
            effects_logger.debug(
                f"Creating elemental damage mod with element={elem}, multiplier={mul}"
            )
            return cls(element=elem, multiplier=mul) if cls else NullEffect()
        # fallback: heal, buff, debuff, status, etc.
        effects_logger.debug(f"Delegating effect creation to registry for ID: {eid}")
        return EffectRegistry.get(eid)
