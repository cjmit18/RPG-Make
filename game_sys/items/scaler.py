# game_sys/items/scaler.py

from typing import Tuple, Dict
from enum import Enum

# Import your DamageType enum if needed (for type hints), but not strictly required here
from game_sys.core.damage_types import DamageType
from game_sys.items.rarity import Rarity

# Multipliers per rarity (example values; tweak as needed)
_RARITY_STATS_MULTIPLIER: Dict[Rarity, float] = {
    Rarity.COMMON:    1.00,  # no bonus
    Rarity.UNCOMMON:  1.05,  # +5%
    Rarity.RARE:      1.10,  # +10%
    Rarity.EPIC:      1.20,  # +20%
    Rarity.LEGENDARY: 1.35,  # +35%
}

# Multipliers per numeric grade (0..3; example values; tweak as needed)
_GRADE_STATS_MULTIPLIER: Dict[int, float] = {
    0: 1.00,  # grade 0 = no bonus
    1: 1.10,  # +10%
    2: 1.25,  # +25%
    3: 1.50,  # +50%
}


def scale_stat(
    base_range: Tuple[int, int],
    item_level: int,
    grade: int,
    rarity: Rarity,
) -> int:
    """
    Given a base_range (min, max), randomly roll an integer then apply multipliers:
      - item_level: each level gives +2% (i.e. multiplier = 1 + item_level * 0.02)
      - grade: look up in _GRADE_STATS_MULTIPLIER
      - rarity: look up in _RARITY_STATS_MULTIPLIER

    Returns a single scaled integer.
    """
    import random

    # 1) Roll within base_range
    raw = random.randint(base_range[0], base_range[1])

    # 2) Compute multipliers
    level_mult = 1.0 + (item_level * 0.02)  # 2% per level
    grade_mult = _GRADE_STATS_MULTIPLIER.get(grade, 1.0)
    rarity_mult = _RARITY_STATS_MULTIPLIER.get(rarity, 1.0)

    # 3) Apply
    final = raw * level_mult * grade_mult * rarity_mult
    return int(round(final))


def scale_damage_map(
    base_damage_map: Dict[str, int],
    item_level: int,
    grade: int,
    rarity: Rarity,
) -> Dict[str, int]:
    """
    Given a base_damage_map from JSON (e.g. {"PHYSICAL":5, "FIRE":3}),
    apply the same level/grade/rarity multipliers to each flat amount.

    Returns a new dict with the same keys (strings) and scaled integer values.
    """
    scaled_map: Dict[str, int] = {}
    for dtype_str, amt in base_damage_map.items():
        level_mult = 1.0 + (item_level * 0.02)
        grade_mult = _GRADE_STATS_MULTIPLIER.get(grade, 1.0)
        rarity_mult = _RARITY_STATS_MULTIPLIER.get(rarity, 1.0)

        final_amt = int(round(amt * level_mult * grade_mult * rarity_mult))
        scaled_map[dtype_str] = final_amt

    return scaled_map
