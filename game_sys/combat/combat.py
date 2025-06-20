import random
from typing import Any, Dict, Optional, List
from logs.logs import get_logger

from game_sys.config.config import (
    DEFENSE_PIVOT,
    DEFENSE_ALPHA,
    FLAT_DEFENSE_FACTOR,
    MIN_DAMAGE_PERCENT,
)
from game_sys.core.damage_types import DamageType
from game_sys.hooks.hooks import hook_dispatcher
from game_sys.managers.loot_manager import roll_loot, roll_gold
from game_sys.items.item_base import EquipableItem

log = get_logger(__name__)


class CombatCapabilities:
    def __init__(self, rng: Optional[random.Random] = None) -> None:
        self.rng = rng or random.Random()

    def calculate_damage(
        self,
        attacker: Any,
        defender: Any,
        damage_map: Optional[Dict[DamageType, float]],
        stat_name: Optional[str],
        multiplier: float = 1.0,
        crit_chance: float = 0.10,
        variance: float = 0.10,
    ) -> str:
        # 1) Gather all damage components
        hits: List[tuple[DamageType, int, bool, float]] = []

        if damage_map is None and hasattr(attacker, "inventory"):
            w = attacker.inventory.get_primary_weapon()
            if isinstance(w, EquipableItem):
                damage_map = w.total_damage_map()

        if not damage_map or sum(damage_map.values()) <= 0:
            fallback = getattr(attacker, stat_name, 1) if stat_name else 1
            damage_map = {DamageType.PHYSICAL: fallback}

        for dt, base in damage_map.items():
            roll = base + (getattr(attacker, stat_name, 0) * multiplier if stat_name else 0)
            if variance:
                roll *= self.rng.uniform(1 - variance, 1 + variance)

            is_crit = self.rng.random() < crit_chance
            if is_crit:
                roll *= 2

            raw = int(round(roll))
            defense = getattr(defender, "defense", 0)

            # Hybrid flat subtraction
            flat = max(raw - defense * FLAT_DEFENSE_FACTOR, raw * MIN_DAMAGE_PERCENT)

            # Percentage‐based reduction with exponent
            if defense >= 0:
                reduced = flat * DEFENSE_PIVOT / (DEFENSE_PIVOT + (defense ** DEFENSE_ALPHA))
            else:
                reduced = flat
            post_def = int(round(reduced))
            post_def = max(post_def, 1)

            # Apply weakness/resist
            res_mult = (
                defender._resistance_multiplier(dt)
                if hasattr(defender, "_resistance_multiplier")
                else 1.0
            )
            final_dmg = int(round(post_def * res_mult))

            hits.append((dt, final_dmg, is_crit, res_mult))

        # 2) Apply all hits
        for dt, dmg, is_crit, res_mult in hits:
            dealt = defender._apply_damage(dmg, dt)
            log.info(
                "%s hits %s for %d %s damage%s%s",
                attacker.name,
                defender.name,
                dealt,
                dt.name.lower(),
                f" (weakness×{res_mult:.2f})" if res_mult > 1 else
                (f" (resist×{res_mult:.2f})" if res_mult < 1 else ""),
                " (CRITICAL!)" if is_crit else ""
            )

            # ←— **necessary**: fire this so LifeStealPassive sees the hit
            hook_dispatcher.fire(
                "effect.after_apply",
                effect={"id": "weapon_hit"},
                caster=attacker,
                target=defender,
                result={"damage": dealt}
            )

        # 3) Grouped summary
        lines = [f"{attacker.name} hits {defender.name}:"]
        for dt, dmg, is_crit, res_mult in hits:
            label = f"{dmg} {dt.name.lower()}"
            if res_mult != 1.0:
                label += f" ({'weakness' if res_mult > 1 else 'resist'}×{res_mult:.2f})"
            if is_crit:
                label += " (CRITICAL!)"
            lines.append(f"  → {label}")

        lines.append(
            f"  [HP: {defender.current_health}/{getattr(defender, 'max_health', '?')}]"
            + (" Defeated!" if defender.current_health <= 0 else "")
        )
        summary = "\n".join(lines)
        log.info(summary)
        return summary

    def transfer_loot(self, winner: Any, defeated: Any) -> None:
        for item in roll_loot(defeated, self.rng):
            winner.inventory.add_item(item)
            log.info("%s looted 1x %s from %s.", winner.name, item.name, defeated.name)

        gold = roll_gold(defeated, self.rng)
        if gold:
            winner.gold += gold
            log.info("%s looted %d gold from %s.", winner.name, gold, defeated.name)
