# game_sys/enchantments/factory.py

import random
from pathlib import Path
from typing import Optional, Dict, Any
from game_sys.enchantments.base import BasicEnchantment
from game_sys.core.rarity import Rarity
from game_sys.core.damage_types import DamageType
from game_sys.managers.scaling_manager import scale_stat, roll_rarity as rolled

# Load raw enchantment templates at import
_TEMPLATES: Dict[str, Dict[str, Any]] = BasicEnchantment.load_all(Path(__file__).parent)

def create_enchantment(
    enchant_id: str,
    level: Optional[int] = None,
    grade: Optional[int] = None,
    rarity: Optional[Rarity] = None,
    seed: Optional[int] = None,
    rng: Optional[random.Random] = None,
    roll_level: bool = False,
    roll_grade: bool = False,
    roll_rarity: bool = False
) -> BasicEnchantment:
    """
    Create a BasicEnchantment scaled by level, grade, and rarity.
    Uses passed-in values directly unless roll_* flags are set.
    """
    if rng is None:
        rng = random.Random(seed) if seed is not None else random.Random()

    templ = _TEMPLATES.get(enchant_id)
    if templ is None:
        raise KeyError(f"No enchantment template for id='{enchant_id}'")

    # Level
    if roll_level:
        lvl_cap = int(level) if level is not None else int(templ.get("level", 1))
        capped_levels = list(range(1, lvl_cap + 1))
        lvl = rng.choices(capped_levels, weights=[1.0 / x for x in capped_levels], k=1)[0]
    else:
        lvl = int(random.randint(1, level)) if level is not None and level >= templ.get("level", 1) else int(templ.get("level", 1))

    # Grade
    if roll_grade:
        grd_cap = int(grade) if grade is not None else int(templ.get("grade", 1))
        capped_grades = list(range(1, grd_cap + 1))
        grd = rng.choices(capped_grades, weights=[1.0 / x for x in capped_grades], k=1)[0]
    else:
        grd = int(random.randint(1, grade)) if grade is not None and grade >= templ.get("grade", 1) else int(templ.get("grade", 1))

    # Rarity
    if roll_rarity:
        templ_rarity = templ.get("rarity", "COMMON")
        rarity_cap = rarity if isinstance(rarity, Rarity) else (
            Rarity[rarity.upper()] if isinstance(rarity, str) and rarity.upper() in Rarity.__members__
            else Rarity[templ_rarity.upper()] if templ_rarity.upper() in Rarity.__members__
            else Rarity.COMMON
        )
        capped_rarities = [r for r in Rarity if r.value <= rarity_cap.value]
        rar = rolled(capped_rarities, rng)
    else:
        if rarity is not None:
            if isinstance(rarity, Rarity):
                templ_rarity = templ.get("rarity", "COMMON")
                templ_rarity_enum = Rarity[templ_rarity.upper()] if isinstance(templ_rarity, str) and templ_rarity.upper() in Rarity.__members__ else Rarity.COMMON
                rar = rarity if rarity.value >= templ_rarity_enum.value else templ_rarity_enum
            elif isinstance(rarity, str) and rarity.upper() in Rarity.__members__:
                rar = Rarity[rarity.upper()]
            else:
                rar = Rarity.COMMON
        else:
            templ_rarity = templ.get("rarity", "COMMON")
            rar = Rarity[templ_rarity.upper()] if isinstance(templ_rarity, str) and templ_rarity.upper() in Rarity.__members__ else Rarity.COMMON

    # Roll stat bonuses
    stat_bonuses: Dict[str, int] = {}
    for stat, spec in templ.get("stat_bonuses", {}).items():
        base_range = (spec.get("min", 0), spec.get("max", 0))
        stat_bonuses[stat] = max(1, scale_stat(base_range, lvl, grd, rar))

    # Roll damage modifiers
    dmg_mods: Dict[DamageType, int] = {}
    for dt_str, spec in templ.get("damage_modifiers", {}).items():
        try:
            dt = DamageType[dt_str.upper()]
            base_range = (spec.get("min", 0), spec.get("max", 0))
            dmg_mods[dt] = max(0, scale_stat(base_range, lvl, grd, rar))
        except KeyError:
            continue

    return BasicEnchantment(
        enchant_id=enchant_id,
        name=templ.get("name", enchant_id),
        description=templ.get("description", ""),
        level=lvl,
        grade=grd,
        rarity=rar,
        applicable_slots=templ.get("applicable_slots", []),
        stat_bonuses=stat_bonuses,
        damage_modifiers=dmg_mods,
    )
