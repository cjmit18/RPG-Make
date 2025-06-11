# File: game_sys/enchantments/factory.py

import random
import copy
from typing import Dict, Any, Optional, List

from .loader import load_templates
from game_sys.enchantments.base import Enchantment
from game_sys.core.scaler import scale_stat, scale_damage_map, _GRADE_STATS_MULTIPLIER as _GRADE_MODIFIERS
from game_sys.core.rarity import Rarity
from game_sys.core.damage_types import DamageType

# Grade modifiers for scaling stats and damage (example values, adjust as needed)
# Load all enchantment templates at import
_TEMPLATES: Dict[str, Any] = load_templates()


def _roll_range(spec: Any, rng: random.Random) -> int:
    """
    Given a spec dict with 'min'/'max', roll an integer between them.
    """
    lo = int(spec.get("min", 0))
    hi = int(spec.get("max", lo))
    return rng.randint(lo, hi) if hi >= lo else lo


def _instantiate(template: Dict[str, Any], rng: random.Random) -> Enchantment:
    """
    Build an Enchantment from a JSON template dict, applying level/grade/rarity scaling.
    """
    ench_id = template.get("id")
    name = template.get("name", "")
    description = template.get("description", "")
    level = int(template.get("level", 1))
    grade = int(template.get("grade", 1))
    rarity = Rarity[template.get("rarity", "COMMON").upper()]

    # 1) Scale stat bonuses
    scaled_stats: Dict[str, int] = {}
    for stat, spec in template.get("stat_bonuses", {}).items():
        rolled = _roll_range(spec, rng)
        scaled = scale_stat(rolled, level, grade=grade, rarity=rarity)
        final = int(scaled * _GRADE_MODIFIERS.get(grade, 1.0))
        scaled_stats[stat] = final

    # 2) Scale damage modifiers
    raw_damage_map: Dict[DamageType, int] = {}
    for dt_str, spec in template.get("damage_modifiers", {}).items():
        rolled = _roll_range(spec, rng)
        raw_damage_map[DamageType[dt_str.upper()]] = rolled

    scaled_damage_map = scale_damage_map(
        raw_damage_map, level, grade=grade, rarity=rarity
    )
    for dt in scaled_damage_map:
        scaled_damage_map[dt] = int(
            scaled_damage_map[dt] * _GRADE_MODIFIERS.get(grade, 1.0)
        )

    # 3) Instantiate Enchantment object
    return Enchantment(
        id=ench_id,
        name=name,
        description=description,
        level=level,
        grade=grade,
        rarity=rarity,
        stat_bonuses=scaled_stats,
        damage_modifiers={dt.name: dmg for dt, dmg in scaled_damage_map.items()},
    )


def create_enchantment(
    enchant_id: str,
    level: Optional[int] = None,
    grade: int = 1,
    rarity: Rarity = Rarity.COMMON,
    seed: Optional[int] = None,
    rng: Optional[random.Random] = None
) -> Enchantment:
    """
    Public factory: returns a scaled, randomized Enchantment instance by ID.
    """
    if rng is None:
        rng = random.Random(seed) if seed is not None else random.Random()

    templ = _TEMPLATES.get(enchant_id)
    if templ is None:
        raise KeyError(f"No enchantment template for id={enchant_id!r}")

    templ_copy = copy.deepcopy(templ)
    if level is not None:
        templ_copy["level"] = level
    templ_copy["grade"] = grade
    templ_copy["rarity"] = rarity.name

    return _instantiate(templ_copy, rng)


def list_all_ids() -> List[str]:
    """Return all defined enchantment IDs."""
    return list(_TEMPLATES.keys())
