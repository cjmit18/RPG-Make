# game_sys/items/factory.py

import random
from typing import Dict, Any, List, Optional, Union
from .item_base import Item, EquipableItem, ConsumableItem
from .loader import load_templates
from game_sys.core.rarity import Rarity
from game_sys.managers.scaling_manager import scale_stat, scale_damage_map
from game_sys.core.damage_types import DamageType

_TEMPLATES: Dict[str, Dict[str, Any]] = {}
for entry in load_templates():
    if isinstance(entry, dict) and 'id' in entry:
        _TEMPLATES[entry['id']] = entry


def _roll_field(spec: Union[int, float, str, bool, Dict[str, Any], List[Any]], rng: random.Random) -> Any:
    if isinstance(spec, (int, float, str, bool)):
        return spec
    if isinstance(spec, dict):
        lo = spec.get('min')
        hi = spec.get('max', lo)
        if lo is None:
            raise ValueError(f"Invalid spec without 'min': {spec!r}")
        return rng.randint(int(lo), int(hi))
    if isinstance(spec, list) and spec:
        return _roll_field(rng.choice(spec), rng)
    return spec


def _instantiate(template: Dict[str, Any], rng: random.Random) -> Item:
    item_type = template.get('type')
    item_id = template.get('id', '<unknown>')
    name = template.get('name', '')
    description = template.get('description', 'Place holder description.')
    level = int(template.get('level', 1))
    grade = int(template.get('grade', 1))
    pool = template.get("enchantment_pool", [])
    reqs = template.get("enchantment_requirements", {})
    min_lvl = reqs.get("min_item_level", 1)
    min_grade = reqs.get("min_item_grade", 1)
    min_rarity_str = reqs.get("min_item_rarity", 'UNCOMMON').upper()
    min_rarity = Rarity[min_rarity_str] if min_rarity_str in Rarity.__members__ else Rarity.UNCOMMON
    slot_type = reqs.get("slot_type", [])
    rar_val = template.get('rarity', 'COMMON')
    amount = template.get('amount', 1)

    rarity = (
        rar_val if isinstance(rar_val, Rarity)
        else Rarity[rar_val.upper()] if isinstance(rar_val, str) and rar_val.upper() in Rarity.__members__
        else Rarity.COMMON
    )

    base_price = int(template.get('price', 0))
    price = int(round(base_price * grade * rarity.value * level))

    if item_type == 'equipable':
        slot = template.get('slot', '')
        scaled_ranges = {
            stat: {'min': scale_stat((int(spec.get('min', 0)), int(spec.get('max', 0))), level, grade, rarity),
                   'max': scale_stat((int(spec.get('min', 0)), int(spec.get('max', 0))), level, grade, rarity)}
            for stat, spec in template.get('base_bonus_ranges', {}).items()
        }

        grade = int(template.get('grade')) if template.get('grade') is not None else random.randint(template.get('grade_min', 1), template.get('grade_max', 1))
        
        raw_dmg = {
            DamageType[dt_str.upper()]: int(_roll_field(spec, rng))
            for dt_str, spec in template.get('raw_damage_map', {}).items()
            if dt_str.upper() in DamageType.__members__
        }
        scaled_dmg = scale_damage_map(raw_dmg, level, grade, rarity)

        percent_bonuses = {
            stat: float(pct) for stat, pct in template.get('percent_bonuses', {}).items()
        }
        passive_effects = template.get('passive_effects', []) or []

        item = EquipableItem(
            id=item_id,
            name=name,
            description=description,
            price=price,
            level=level,
            slot=slot,
            grade=grade,
            rarity=rarity,
            base_bonus_ranges=scaled_ranges,
            damage_map={
                dt.name: {'min': amt, 'max': amt} for dt, amt in scaled_dmg.items()
            },
            percent_bonuses=percent_bonuses,
            passive_effects=passive_effects,
            enchantments=[]
        )

    elif item_type == 'consumable':
        effects_data = []
        for eff in template.get('effects', []):
            eff_copy = dict(eff)
            amt_spec = eff_copy.get('amount')
            eff_copy['amount'] = (
                scale_stat((int(amt_spec.get('min', 0)), int(amt_spec.get('max', 0))), level, grade, rarity)
                if isinstance(amt_spec, dict)
                else _roll_field(amt_spec, rng)
            )
            effects_data.append(eff_copy)

        item = ConsumableItem(
            id=item_id,
            name=name,
            description=description,
            price=price,
            level=level,
            effects_data=effects_data,
            grade=grade,
            rarity=rarity,
            amount=amount
        )
        item.grade = grade
        item.rarity = rarity

    else:
        raise KeyError(f"Unknown item type '{item_type}' for id '{item_id}'")

    if (
        item_type == 'equipable'
        and pool
        and level >= min_lvl
        and grade >= min_grade
        and slot in slot_type
        and rarity.value >= min_rarity.value
            ):
        from game_sys.enchantments.factory import create_enchantment
        lo = template.get("min_enchantments", 0)
        hi = template.get("max_enchantments", 0)
        count = rng.randint(lo, hi)
        valid = [e for e in pool if isinstance(e, str)]
        chosen = rng.sample(valid, k=min(count, len(valid)))

        item.enchantments = []
        for ench_id in chosen:
            enchant = create_enchantment(ench_id, level=level, grade=grade, rarity=rarity, rng=rng)
            if item.slot.lower() in [s.lower() for s in enchant.applicable_slots]:
                item.enchantments.append(enchant)

    return item

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
        templ_copy['rarity'] = rarity.name.lower() if isinstance(rarity, Rarity) else str(rarity).lower()
    if level is not None:
        templ_copy['level'] = level

    from game_sys.core.hooks import hook_dispatcher
    hook_dispatcher.fire("item.created", item=templ_copy, seed=seed, rng=rng)
    return _instantiate(templ_copy, rng)

def list_all_ids() -> List[str]:
    return list(_TEMPLATES.keys())
