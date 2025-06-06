# game_sys/effects/damage.py

import random
from typing import Dict, Any, Optional
from game_sys.core.damage_types import DamageType
from game_sys.core.actor import Actor
from game_sys.combat.combat import CombatCapabilities
from game_sys.effects.base import Effect


class DamageEffect(Effect):
    """
    An Effect that deals damage of one or more types. Supports:
      - A flat 'damage_map': { DamageType.FIRE: 10, DamageType.PHYSICAL: 5 }
      - A stat-based 'stat_name' & 'multiplier' (e.g. "intellect" × 2), which merges into PHYSICAL.
      - Crit roll and variance per roll.
    """

    def __init__(
        self,
        damage_map: Optional[Dict[DamageType, int]] = None,
        stat_name: Optional[str] = None,
        multiplier: float = 1.0,
        crit_chance: float = 0.1,
        variance: float = 1.0,
    ) -> None:
        self._base_damage_map: Dict[DamageType, int] = damage_map.copy() if damage_map else {}
        self.stat_name = stat_name
        self.multiplier = multiplier
        self.crit_chance = crit_chance
        self.variance = variance

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "DamageEffect":
        # (Existing parsing logic stays unchanged; omitted for brevity)
        # Builds a damage_map keyed by DamageType, plus optional stat_name, multiplier, crit_chance, variance.

        dm: Dict[DamageType, int] = {}
        if "damage" in data:
            raw_map = data["damage"]
            for dt_str, amt in raw_map.items():
                try:
                    key = DamageType[dt_str.upper()]
                    dm[key] = int(amt)
                except Exception:
                    continue
        elif "damage_type" in data and "value" in data:
            key = DamageType[data["damage_type"].upper()]
            dm[key] = int(data["value"])

        stat = data.get("stat_name")
        mult = float(data.get("multiplier", 1.0))
        crit = float(data.get("crit_chance", 0.1))
        var = float(data.get("variance", 1.0))

        return cls(
            damage_map=dm,
            stat_name=stat,
            multiplier=mult,
            crit_chance=crit,
            variance=var,
        )

    def apply(self, caster: Actor, target: Actor, combat_engine: CombatCapabilities) -> str:
        """
        Deal all damage types in one combined call to take_damage, but still log each component.

        Original behavior (calling take_damage per-type) has been replaced so that:
          - We compute each type’s final damage (after stat, variance, crit, weakness/resistance)
          - Sum them into a single 'total_damage'
          - Call target.take_damage(total_damage) once at the end
          - Return a log string that shows per-type breakdown plus total
        """
        rng = combat_engine.rng if combat_engine and hasattr(combat_engine, "rng") else random.Random()
        working_map = self._base_damage_map.copy()

        # (A) Add stat-derived PHYSICAL damage if stat_name provided
        if self.stat_name:
            stat_val = getattr(caster.stats, self.stat_name, 0)
            stat_raw = int(round(stat_val * self.multiplier))
            if stat_raw > 0:
                working_map[DamageType.PHYSICAL] = working_map.get(DamageType.PHYSICAL, 0) + stat_raw

        parts = []
        crit_occurred = False
        total_damage = 0

        # (B) Compute each damage type separately, but do NOT call take_damage yet
        for dt, base_amt in working_map.items():
            if base_amt <= 0:
                continue

            amt = base_amt

            # (1) Variance roll: ± variance (e.g. ±10% if variance=1.0)
            if self.variance != 1.0:
                factor = rng.uniform(1.0 - self.variance, 1.0 + self.variance)
                amt = int(round(amt * factor))

            # (2) Crit roll: if crit, double this type’s raw damage
            if rng.random() < self.crit_chance:
                amt *= 2
                crit_occurred = True

            # (3) Apply weakness/resistance multipliers
            weak_mul = target.get_weakness_multiplier(dt)
            res_mul = target.get_resistance_multiplier(dt)
            final_amt = int(round(amt * weak_mul * res_mul))

            # Accumulate for single take_damage call later
            total_damage += final_amt

            # Build a per-type log fragment
            frag = f"{final_amt} {dt.name.lower()}"
            if weak_mul > 1.0:
                frag += " (super-effective!)"
            elif res_mul < 1.0:
                frag += " (ineffective…)"
            parts.append(frag)

        # (C) Now apply all damage at once
        if total_damage > 0:
            target.take_damage(total_damage)
        else:
            # If no damage was dealt (e.g. all base_amt=0), we still call take_damage(0) to log anything if necessary
            target.take_damage(0)

        # (D) Construct the combined log string
        if not parts:
            return f"{caster.name} dealt no damage."

        breakdown = " + ".join(parts)
        log_str = f"{caster.name} deals {breakdown} to {target.name}."
        if crit_occurred:
            log_str += " (CRITICAL HIT!)"
        if target.current_health == 0:
            log_str += f" {target.name} has been defeated!"

        return log_str
