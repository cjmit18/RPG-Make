# game_sys/effects/damage.py

import random
from typing import Dict, Any, Optional

from game_sys.core.damage_types import DamageType
from game_sys.character.actor import Actor
from game_sys.effects.base import Effect
from logs.logs import get_logger

log = get_logger(__name__)


class DamageEffect(Effect):
    """
    Deals one or more damage types, with optional stat scaling, crits, variance,
    and delegates all resistance/weakness/defend logic to Actor.take_damage.
    """

    def __init__(
        self,
        damage_map: Optional[Dict[DamageType, int]] = None,
        stat_name: Optional[str] = None,
        multiplier: float = 1.0,
        crit_chance: float = 0.1,
        variance: float = 0.0,
    ) -> None:
        # Base damage per type (e.g. {DamageType.FIRE: 50})
        self._base_damage_map = damage_map.copy() if damage_map else {}
        self.stat_name = stat_name
        self.multiplier = multiplier
        self.crit_chance = crit_chance
        self.variance = variance

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "DamageEffect":
        dm: Dict[DamageType, int] = {}
        # support either {"damage": {type:amount}} or legacy {"damage_type", "value"}
        if "damage" in data:
            for k, v in data["damage"].items():
                try:
                    dt = DamageType[k.upper()]
                    dm[dt] = int(v)
                except Exception:
                    continue
        elif "damage_type" in data and "value" in data:
            try:
                dt = DamageType[data["damage_type"].upper()]
                dm[dt] = int(data["value"])
            except Exception:
                pass

        return cls(
            damage_map=dm,
            stat_name=data.get("stat_name"),
            multiplier=float(data.get("multiplier", 1.0)),
            crit_chance=float(data.get("crit_chance", 0.1)),
            variance=float(data.get("variance", 0.0)),
        )

    def apply(
        self,
        caster: Actor,
        target: Actor,
        combat_engine: Optional[Any] = None
    ) -> str:
        """
        Inflict the configured damage on target, in this order:
          1) Level‐scale base damage
          2) Add caster.stat_name * multiplier
          3) Apply variance
          4) Apply crit doubling
          5) Call Actor.take_damage(raw_amount, damage_type) to handle
             resistance/weakness/defend/DamageReduction
          6) Build summary based on actual HP lost and type multipliers
        """
        rng = getattr(combat_engine, "rng", random.Random())

        # 1) Level scaling
        lvl_mul = 1.0 + caster.levels.lvl * 0.02
        working: Dict[DamageType, int] = {}
        for dt, base_amt in self._base_damage_map.items():
            scaled = int(round(base_amt * lvl_mul))
            if scaled > 0:
                working[dt] = scaled

        # 2) Stat scaling
        if self.stat_name:
            stat_val = getattr(caster, self.stat_name, 0)
            bonus = int(round(stat_val * self.multiplier))
            for dt in list(working):
                working[dt] += bonus

        summary_parts: list[str] = []
        crit_hit = False

        # 3–5) For each type, apply variance/crit then delegate to take_damage
        for dt, amt in working.items():
            # variance
            if self.variance > 0:
                factor = rng.uniform(1 - self.variance, 1 + self.variance)
                amt = int(round(amt * factor))

            # crit
            if rng.random() < self.crit_chance:
                amt *= 2
                crit_hit = True

            # snapshot health
            before_hp = target.current_health
            # delegate all resist/weak/defend logic here:
            target.take_damage(amt, damage_type=dt)
            after_hp = target.current_health

            lost = before_hp - after_hp
            if lost <= 0:
                continue

            # check multipliers for tagging
            weak_mul = target.get_weakness_multiplier(dt)
            res_mul  = target.get_resistance_multiplier(dt)

            frag = f"{lost} {dt.name.lower()}"
            mult = weak_mul * res_mul
            if mult > 1.0:
                frag += f" (super effective x{mult:.1f})"
            elif mult < 1.0:
                frag += f" (not very effective x{mult:.1f})"
            summary_parts.append(frag)

        # 6) Build the final string
        if not summary_parts:
            result = f"{caster.name} dealt no damage to {target.name}."
        else:
            result = f"{caster.name} deals {' + '.join(summary_parts)} to {target.name}."
            if crit_hit:
                result += " (CRITICAL HIT!)"
            if target.current_health == 0:
                result += f" {target.name} has been defeated!"

        log.info(result)
        return result
