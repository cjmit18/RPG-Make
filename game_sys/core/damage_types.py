# game_sys/core/damage_types.py
"""
Module: game_sys.core.damage_types

Defines the DamageType enum for use in damage calculations, resistances,
weaknesses, and effect matching throughout the engine.
"""
from enum import Enum, auto

class DamageType(Enum):
    NONE = auto()
    PHYSICAL = auto()
    FIRE = auto()
    ICE = auto()
    LIGHTNING = auto()
    POISON = auto()
    ARCANE = auto()
    HOLY = auto()
    DARK = auto()
    MAGIC = auto()

    def __str__(self):
        return self.name