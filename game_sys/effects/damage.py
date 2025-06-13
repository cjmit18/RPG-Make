# game_sys/effects/damage.py

"""
Deals damage of one or more types, with scaling, crits, variance,
and delegates all resistance/weakness/defend logic to Actor.take_damage.
"""

import random
from typing import Any, Dict, Optional, Union
from game_sys.core.damage_types import DamageType
from game_sys.effects.base import Effect
from logs.logs import get_logger
from game_sys.core.hooks import hook_dispatcher

log = get_logger(__name__)


class DamageEffect(Effect):
    def __init__(
        self,
        damage_map: Dict[DamageType, int],
        stat_name: Optional[str] = None,
        multiplier: float = 1.0,
        crit_chance: float = 0.1,
        variance: float = 0.0
    ) -> None:
        self._base_damage_map = dict(damage_map)
        self.stat_name = stat_name
        self.multiplier = multiplier
        self.crit_chance = crit_chance
        self.variance = variance

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> Effect:
        dm: Dict[DamageType, int] = {}
        raw = data.get("damage", {})
        for k, v in raw.items():
            try:
                dt = DamageType[k.upper()]
            except KeyError:
                continue
            # support fixed or ranged damage
            if isinstance(v, dict):
                lo = int(v.get("min", 0))
                hi = int(v.get("max", lo))
                amt = random.randint(lo, hi)
            else:
                amt = int(v)
            dm[dt] = amt
        return cls(
            damage_map=dm,
            stat_name=data.get("stat_name"),
            multiplier=float(data.get("multiplier", 1.0)),
            crit_chance=float(data.get("crit_chance", 0.1)),
            variance=float(data.get("variance", 0.0)),
        )

    def apply(
        self,
        caster: Any,
        target: Any,
        combat_engine: Optional[Any] = None
    ) -> str:
        rng = getattr(combat_engine, "rng", random.Random())
        summary: list[str] = []
        crit = False

        for dt, base in self._base_damage_map.items():
            amt = int(round(base * (1 + getattr(caster, "level", 1) * 0.02)))
            if self.stat_name:
                bonus = int(round(getattr(caster, self.stat_name, 0) * self.multiplier))
                amt += bonus

            if self.variance > 0:
                amt = int(round(amt * rng.uniform(1 - self.variance, 1 + self.variance)))
            if rng.random() < self.crit_chance:
                amt *= 2
                crit = True

            before = target.current_health
            target.take_damage(amt, damage_type=dt)
            lost = before - target.current_health
            if lost > 0:
                summary.append(f"{lost} {dt.name.lower()}")

        result = (
            f"{caster.name} deals {' + '.join(summary)} to {target.name}"
            + (" (CRITICAL!)" if crit else "")
            + (" and defeats them!" if target.current_health == 0 else "")
        )

        log.info(result)
        hook_dispatcher.fire("effect.apply", target=target, effect=self)
        return result
