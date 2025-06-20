# game_sys/managers/scaling_manager.py

from typing import Tuple, Dict, Union, List
import random
from game_sys.core.rarity import Rarity
from game_sys.config.config import (
    RARITY_STATS_MULTIPLIER as _RARITY_STATS_MULTIPLIER,
    GRADE_STATS_MULTIPLIER as _GRADE_STATS_MULTIPLIER,
)


def scale_stat(
    base_range: Union[int, Tuple[int, int]],
    level: int,
    grade: int,
    rarity: Rarity
) -> int:
    """
    Pick a “raw” value from base_range, then bump it
    by level, grade, and rarity multipliers.
    """
    if isinstance(base_range, int):
        min_base, max_base = base_range, base_range
    else:
        try:
            min_base, max_base = base_range
        except Exception as e:
            raise ValueError(f"Invalid base_range {base_range!r}") from e

    raw = random.randint(min_base, max_base)
    level_mult = 1.0 + (level * 0.10)  # 10% per level
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
        level_mult = 1.0 + (item_level * 0.05)
        grade_mult = _GRADE_STATS_MULTIPLIER.get(grade, 1.0)
        rarity_mult = _RARITY_STATS_MULTIPLIER.get(rarity, 1.0)
        final_amt = int(round(amt * level_mult * grade_mult * rarity_mult))
        scaled[dtype_str] = final_amt
    return scaled


def get_rarity_weight(r: Rarity) -> float:
    """Weight function: lower rarity => higher chance."""
    return 1.0 / r.value


def roll_rarity(capped_rarities: List[Rarity], rng: random.Random) -> Rarity:
    weights = [get_rarity_weight(r) for r in capped_rarities]
    return rng.choices(capped_rarities, weights=weights, k=1)[0]


def roll_item_rarity(
    rarity_cap: Rarity,
    rng: random.Random
) -> Rarity:
    """Roll an item rarity up to the given cap using rarity weights."""
    capped_rarities = [r for r in Rarity if r.value <= rarity_cap.value]
    return roll_rarity(capped_rarities, rng)


def roll_weighted_value(cap: int, rng: random.Random) -> int:
    values = list(range(1, cap + 1))
    weights = [1.0 / v for v in values]
    return rng.choices(values, weights=weights, k=1)[0]
