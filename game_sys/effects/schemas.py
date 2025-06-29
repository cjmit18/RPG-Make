# game_sys/effects/schemas.py
"""
Module: game_sys.effects.schemas

Defines JSON schema structures for effect configuration.
"""
from typing import Dict, Any, Type

# Define the base schema structure
EFFECT_PARAMS: Dict[str, Dict[str, Type]] = {
    'flat': {
        'amount': float
    },
    'percent': {
        'multiplier': float
    },
    'elemental': {
        'element': str,
        'multiplier': float
    },
    'stat_bonus': {
        'stat': str,
        'amount': float
    },
    'heal': {
        'amount': float
    },
    'buff': {
        'stat': str,
        'amount': float,
        'duration': float
    },
    'debuff': {
        'stat': str,
        'amount': float,
        'duration': float
    },
    'status': {
        'name': str,
        'duration': float,
        'tick_damage': float
    }
}

def validate_effect_definition(defn: Dict[str, Any]) -> bool:
    """
    Validate a raw effect definition dictionary against the schema.
    Raises ValueError on mismatch.
    """
    if 'type' not in defn or 'params' not in defn:
        raise ValueError("Effect definition must have 'type' and 'params'")
    etype = defn['type']
    if etype not in EFFECT_PARAMS:
        raise ValueError(f"Unknown effect type: {etype}")
    params = defn['params']
    expected = EFFECT_PARAMS[etype]
    for key, typ in expected.items():
        if key not in params or not isinstance(params[key], typ):
            raise ValueError(f"Invalid or missing param '{key}' for effect '{etype}'")
    return True
