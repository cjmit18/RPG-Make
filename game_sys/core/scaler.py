# game_sys/items/scaler.py

from typing import Tuple, Dict, Union
import random
from game_sys.core.rarity import Rarity

# Example multipliers (tweak to taste)
_RARITY_STATS_MULTIPLIER: Dict[Rarity, float] = {
    Rarity.COMMON:    1.00,
    Rarity.UNCOMMON:  1.50,
    Rarity.RARE:      2.00,
    Rarity.EPIC:      2.50,
    Rarity.LEGENDARY: 3.00,
    Rarity.MYTHIC:    3.50,
    Rarity.DIVINE:    5.00,
}

_GRADE_STATS_MULTIPLIER: Dict[int, float] = {
    1: 1.00,
    2: 1.25,
    3: 1.50,
    4: 1.75,
    5: 2.00,
    6: 2.50,
    7: 5.00,
}

def scale_stat(
    base_range: Union[int, Tuple[int, int]],
    level: int,
    grade: int,
    rarity: Rarity
) -> int:
    """
    Pick a “raw” value from base_range, then bump it
    by level, grade, and rarity multipliers.

    base_range may be either:
      - an int (for a fixed value), or
      - a (min, max) tuple/list for a random roll.
    """
    # ——— make sure base_range is two numbers ———
    if isinstance(base_range, int):
        min_base, max_base = base_range, base_range
    else:
        # try to unpack; will error if wrong shape
        try:
            min_base, max_base = base_range
        except Exception as e:
            raise ValueError(f"Invalid base_range {base_range!r}") from e

    # roll between min_base and max_base
    raw = random.randint(min_base, max_base)

    # level boost: for example +2% per level
    level_mult = 1.0 + (level * 0.10)
    # grade boost from your grade table
    grade_mult = _GRADE_STATS_MULTIPLIER.get(grade, 1.0)
    # rarity boost from your rarity table
    rarity_mult = _RARITY_STATS_MULTIPLIER.get(rarity, 1.0)

    return int(round(raw * level_mult * grade_mult * rarity_mult))
def scale_damage_map(
    base_damage_map: Dict[str, int],
    item_level: int,
    grade: int,
    rarity: Rarity,
) -> Dict[str, int]:
    scaled = {}
    for dtype_str, amt in base_damage_map.items():
        level_mult = 1.0 + (item_level * 0.02)
        grade_mult = _GRADE_STATS_MULTIPLIER.get(grade, 1.0)
        rarity_mult = _RARITY_STATS_MULTIPLIER.get(rarity, 1.0)
        final_amt = int(round(amt * level_mult * grade_mult * rarity_mult))
        scaled[dtype_str] = final_amt 
    return scaled
