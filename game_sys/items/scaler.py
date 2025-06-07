# game_sys/items/scaler.py

from typing import Tuple, Dict
from game_sys.items.rarity import Rarity

# Example multipliers (tweak to taste)
_RARITY_STATS_MULTIPLIER: Dict[Rarity, float] = {
    Rarity.COMMON:    1.00,
    Rarity.UNCOMMON:  1.05,
    Rarity.RARE:      1.10,
    Rarity.EPIC:      1.20,
    Rarity.LEGENDARY: 1.35,
    Rarity.MYTHIC:    1.50,
    Rarity.EXOTIC:    1.60,
    Rarity.DIVINE:    2.50,
}

_GRADE_STATS_MULTIPLIER: Dict[int, float] = {
    0: 1.00,
    1: 1.10,
    2: 1.25,
    3: 1.50,
    4: 1.75,
    5: 2.00,
    6: 2.50,
    7: 3.00,
}

def scale_stat(
    base_range: Tuple[int, int],
    item_level: int,
    grade: int,
    rarity: Rarity,
) -> int:
    import random
    raw = random.randint(base_range[0], base_range[1])
    level_mult = 1.0 + (item_level * 0.02)
    grade_mult = _GRADE_STATS_MULTIPLIER.get(grade, 1.0)
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
