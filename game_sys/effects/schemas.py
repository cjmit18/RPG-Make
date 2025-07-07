# game_sys/effects/schemas.py

from typing import Dict, Any, Type
from game_sys.logging import effects_logger, log_exception

# Define the base schema for each effect type:
# keys = param name, values = Python type(s) expected
EFFECT_PARAMS: Dict[str, Dict[str, Type]] = {
    'flat':     { 'amount': float },
    'percent':  { 'multiplier': float },
    'elemental':{
        'element':    str,
        'multiplier': float
    },
    'stat_bonus': {
        'stat':   str,
        'amount': float
    },
    'heal': {
        'amount': float
    },
    'buff': {
        'stat':    str,
        'amount':  float,
        'duration':float
    },
    'debuff': {
        'stat':    str,
        'amount':  float,
        'duration':float
    },
    'status': {
        'name':        str,
        'duration':    float,
        'tick_damage': float
    },
    'instant': {
        'resource': str,
        'amount':   float
    },
    'instant_mana': {
        'amount': float
    },
    'resource_drain': {
        'resource': str,
        'rate':     float,
        'duration': float
    },
    # Status effect types that use the status flag system
    'burn': {
        'duration': float,
        'tick_damage': float
    },
    'poison': {
        'duration': float,
        'tick_damage': float
    },
    'stun': {
        'duration': float
    },
    'fear': {
        'duration': float
    },
    'slow': {
        'duration': float,
        'intensity': float
    },
    'freeze': {
        'duration': float
    },
    'haste': {
        'duration': float,
        'intensity': float
    },
    'regeneration': {
        'duration': float,
        'tick_heal': float
    },
    'silence': {
        'duration': float
    },
    'weaken': {
        'duration': float,
        'intensity': float
    },
    'berserk': {
        'duration': float,
        'damage_multiplier': float
    },
    'protection': {
        'duration': float,
        'damage_reduction': float
    },
    'invisibility': {
        'duration': float
    },
    'paralyze': {
        'duration': float
    },
    'sleep': {
        'duration': float
    }
}


@log_exception
def validate_effect_definition(defn: Dict[str, Any]) -> bool:
    """
    Validate a raw effect-definition dict (must have 'type' and 'params').
    Raises ValueError on missing or type-mismatched params.
    """
    effects_logger.debug(f"Validating effect definition: {defn}")
    
    if 'type' not in defn or 'params' not in defn:
        effects_logger.error("Effect definition missing 'type' or 'params'")
        raise ValueError("Effect definition must have 'type' and 'params'")
        
    etype = defn['type']
    if etype not in EFFECT_PARAMS:
        effects_logger.error(f"Unknown effect type: {etype}")
        raise ValueError(f"Unknown effect type: {etype}")

    params = defn['params']
    expected = EFFECT_PARAMS[etype]

    for key, typ in expected.items():
        if key not in params:
            effects_logger.error(f"Missing param '{key}' for effect '{etype}'")
            raise ValueError(f"Missing param '{key}' for effect '{etype}'")
            
        val = params[key]
        # allow ints where floats are expected
        if typ is float:
            if not isinstance(val, (int, float)):
                effects_logger.error(
                    f"Invalid param '{key}' for effect '{etype}': "
                    f"expected a number, got {type(val).__name__}"
                )
                raise ValueError(
                    f"Invalid param '{key}' for effect '{etype}': "
                    f"expected a number, got {type(val).__name__}"
                )
        else:
            if not isinstance(val, typ):
                effects_logger.error(
                    f"Invalid param '{key}' for effect '{etype}': "
                    f"expected {typ.__name__}, got {type(val).__name__}"
                )
                raise ValueError(
                    f"Invalid param '{key}' for effect '{etype}': "
                    f"expected {typ.__name__}, got {type(val).__name__}"
                )
                
    effects_logger.debug(
        f"Effect definition for {etype} validated successfully"
    )
    return True