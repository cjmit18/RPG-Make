# game_sys/items/factory.py
import random
from typing import Dict, Any, List, Optional, Union

from .item_base import Item, EquipableItem, ConsumableItem
from .loader import load_templates
from game_sys.items.rarity import Rarity
from game_sys.core.scaler import scale_stat, scale_damage_map
from game_sys.core.damage_types import DamageType

# Grade-based multiplier modifiers
_GRADE_MODIFIERS: Dict[int, float] = {
    1: 1.0,
    2: 1.1,
    3: 1.25,
    4: 1.5,
    5: 2.0,
    6: 2.5,
    7: 3.0,
}

# Load all item templates at module-import time
_TEMPLATES: Dict[str, Dict[str, Any]] = {}
for entry in load_templates():
    if isinstance(entry, dict) and 'id' in entry:
        _TEMPLATES[entry['id']] = entry


def _roll_field(spec: Union[int, float, str, bool, Dict[str, Any], List[Any]],
                rng: random.Random) -> Any:
    if isinstance(spec, (int, float, str, bool)):
        return spec
    if isinstance(spec, dict):
        lo = spec.get('min')
        hi = spec.get('max', lo)
        if lo is None:
            raise ValueError(f"Invalid spec without 'min': {spec!r}")
        lo, hi = int(lo), int(hi)
        return rng.randint(lo, hi) if hi >= lo else lo
    if isinstance(spec, list) and spec:
        return _roll_field(rng.choice(spec), rng)
    return spec


def _instantiate(template: Dict[str, Any], rng: random.Random) -> Item:
    item_type = template.get('type')
    item_id = template.get('id', '<unknown>')
    name = template.get('name', '')
    description = template.get('description', '')
    level = int(template.get('level', 1))
    grade = int(template.get('grade', 1))
    # parse rarity string into enum
    rar_val = template.get('rarity', 'common')
    if isinstance(rar_val, Rarity):
        rarity = rar_val
    else:
        if isinstance(rar_val, str) and rar_val.upper() in Rarity.__members__:
            rarity = Rarity[rar_val.upper()]
        else:
            rarity = Rarity.COMMON

    base_price = int(template.get('price', 0))
    price = int(round(base_price * _GRADE_MODIFIERS.get(grade, 1.0)))

    if item_type == 'equipable':
        slot = template.get('slot', '')
        # Scale flat bonuses
        scaled_ranges: Dict[str, Dict[str, int]] = {}
        for stat, spec in template.get('base_bonus_ranges', {}).items():
            lo = int(spec.get('min', 0))
            hi = int(spec.get('max', lo))
            rolled = scale_stat((lo, hi), level, grade=grade, rarity=rarity)
            scaled_ranges[stat] = {'min': rolled, 'max': rolled}
        # Scale damage
        raw_dmg: Dict[DamageType, int] = {}
        for dt_str, spec in template.get('raw_damage_map', {}).items():
            dmg = _roll_field(spec, rng)
            if dt_str.upper() in DamageType.__members__:
                raw_dmg[DamageType[dt_str.upper()]] = int(dmg)
        scaled_dmg = scale_damage_map(raw_dmg, level, grade=grade,
                                      rarity=rarity)
        # Percent buffs
        percent_bonuses = {
            stat: float(pct) for stat, pct in
            template.get('percent_bonuses', {}).items()
            }
        passive_effects = template.get('passive_Effects', []) or []

        item = EquipableItem(
            id=item_id, name=name, description=description, price=price,
            level=level, slot=slot, grade=grade, rarity=rarity,
            base_bonus_ranges=scaled_ranges,
            raw_damage_map={
                dt.name: {'min': amt, 'max': amt}
                for dt, amt in scaled_dmg.items()
            },
            is_enchantable=bool(template.get('is_enchantable', False)),
            percent_bonuses=percent_bonuses,
            passive_Effects=passive_effects,
        )
        item.rescale(level)
        return item

    elif item_type == 'consumable':
        # Scale effects
        effects_data = []
        for eff in template.get('effects', []):
            eff_copy = dict(eff)
            amt_spec = eff_copy.get('amount')
            if isinstance(amt_spec, dict):
                lo = int(amt_spec.get('min', 0))
                hi = int(amt_spec.get('max', lo))
                eff_copy['amount'] = scale_stat(
                    (lo, hi), level, grade=grade, rarity=rarity
                )
            else:
                eff_copy['amount'] = _roll_field(amt_spec, rng)
            effects_data.append(eff_copy)
        item = ConsumableItem(
            id=item_id,
            name=name,
            description=description,
            price=price,
            level=level,
            effects_data=effects_data,
            grade=grade,
            rarity=rarity
        )
        # assign for display
        item.grade = grade
        item.rarity = rarity
        return item

    else:
        raise KeyError(f"Unknown item type '{item_type}' for id '{item_id}'")


def create_item(
    item_id: str,
    seed: Optional[int] = None,
    grade: Optional[int] = None,
    rarity: Optional[Union[Rarity, str]] = None,
    level: Optional[int] = None,
    rng: Optional[random.Random] = None
) -> Item:
    if rng is None:
        rng = random.Random(seed) if seed is not None else random.Random()
    templ = _TEMPLATES.get(item_id)
    if templ is None:
        raise KeyError(f"No item template for id={item_id!r}")
    import copy
    templ_copy = copy.deepcopy(templ)
    if grade is not None:
        templ_copy['grade'] = grade
    if rarity is not None:
        # allow passing either enum or string
        if isinstance(rarity, Rarity):
            templ_copy['rarity'] = rarity.name.lower()
        else:
            templ_copy['rarity'] = str(rarity).lower()
    if level is not None:
        templ_copy['level'] = level
    return _instantiate(templ_copy, rng)


def list_all_ids() -> List[str]:
    return list(_TEMPLATES.keys())
