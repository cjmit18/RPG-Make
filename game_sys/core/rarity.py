from enum import Enum, auto
"""Module: game_sys.core.grades
Defines the grading system for character progression and item quality.
"""
class Rarity(Enum):
    """Enumeration for item rarity."""
    COMMON = auto()
    UNCOMMON = auto()
    RARE = auto()
    EPIC = auto()
    LEGENDARY = auto()
    MYTHIC = auto()
    DIVINE = auto()
