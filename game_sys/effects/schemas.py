# game_sys/effects/schemas.py

from typing import Dict, Any, Type

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
    }
}


def validate_effect_definition(defn: Dict[str, Any]) -> bool:
    """
    Validate a raw effect-definition dict (must have 'type' and 'params').
    Raises ValueError on missing or type-mismatched params.
    """
    if 'type' not in defn or 'params' not in defn:
        raise ValueError("Effect definition must have 'type' and 'params'")
    etype = defn['type']
    if etype not in EFFECT_PARAMS:
        raise ValueError(f"Unknown effect type: {etype}")

    params = defn['params']
    expected = EFFECT_PARAMS[etype]

    for key, typ in expected.items():
        if key not in params:
            raise ValueError(f"Missing param '{key}' for effect '{etype}'")
        val = params[key]
        # allow ints where floats are expected
        if typ is float:
            if not isinstance(val, (int, float)):
                raise ValueError(
                    f"Invalid param '{key}' for effect '{etype}': "
                    f"expected a number, got {type(val).__name__}"
                )
        else:
            if not isinstance(val, typ):
                raise ValueError(
                    f"Invalid param '{key}' for effect '{etype}': "
                    f"expected {typ.__name__}, got {type(val).__name__}"
                )
    return True
    # If we reach here, all params are valid