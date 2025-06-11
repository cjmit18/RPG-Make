# game_sys/combat/combat.py

import random
from typing import Dict, Optional, List
from logs.logs import get_logger
from game_sys.character.actor import Actor
from game_sys.core.damage_types import DamageType
from game_sys.combat.loader import DROP_TABLES
from game_sys.items.factory import create_item
from game_sys.core.rarity import Rarity

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from game_sys.items.item_base import Item

log = get_logger(__name__)


class CombatCapabilities:
    def __init__(
        self,
        character: Actor,
        enemy: Actor,
        rng: Optional[random.Random] = None
    ):
        self.character = character
        self.enemy = enemy
        self.rng = rng or random.Random()

    def calculate_damage(
        self,
        attacker: Actor,
        defender: Actor,
        damage_map: Dict[DamageType, float],
        stat_name: Optional[str] = "attack",
        multiplier: float = 1.0,
        crit_chance: float = 0.10,
        variance: float = 0.10,
    ) -> None:
        for dtype, base_amount in damage_map.items():
            raw = base_amount
            if stat_name:
                raw += getattr(attacker.stats, stat_name, 0) * multiplier

            var_roll = raw * self.rng.uniform(1 - variance, 1 + variance)
            if self.rng.random() < crit_chance:
                var_roll *= 2
                log.info("(CRITICAL HIT!)")

            weak = defender.get_weakness_multiplier(dtype)
            resist = defender.get_resistance_multiplier(dtype)
            adjusted = round(var_roll * weak * resist)

            if defender.defending:
                adjusted = round(adjusted * 0.5)
                defender.defending = False

            defender.take_damage(adjusted, damage_type=dtype)

    def roll_loot(self, defeated: Actor) -> List['Item']:
        items: List['Item'] = []

        # determine key & fetch tiers
        key = (
            defeated.job.job_id.lower()
            if hasattr(defeated, "job")
            else type(defeated).__name__.lower()
        )
        tiers = DROP_TABLES.get(key, [])

        lvl = defeated.levels.lvl
        grade = getattr(defeated, "grade", 1)
        chosen = next(
            (
                tier for tier in tiers
                if (
                    tier["min_level"] <= lvl <= tier["max_level"]
                    and tier.get("min_grade", 0) <= grade
                    and grade <= tier.get("max_grade", grade)
                )
            ),
            None
        )
        if not chosen:
            return items

        for drop in chosen["drops"]:
            if self.rng.uniform(0, 1) <= drop["chance"]:
                qty = self.rng.randint(drop["min_qty"], drop["max_qty"])
                # sample rarity
                rarities = drop.get("rarity_weights", {"common": 1.0})
                names, weights = zip(*rarities.items())
                chosen_name = self.rng.choices(names, weights)[0]
                rarity_enum = Rarity[chosen_name.upper()]

                for _ in range(qty):
                    # pass both grade and rarity into your factory
                    item = create_item(
                        drop["item_id"],
                        grade=grade,
                        rarity=rarity_enum,
                        level=lvl)
                    items.append(item)

        return items

    def transfer_loot(self, winner: Actor, defeated: Actor) -> None:
        # Transfer item drops
        for itm in self.roll_loot(defeated):
            winner.inventory.add_item(itm)
            log.info("%s looted 1x %s from %s.",
                     winner.name,
                     itm.name,
                     defeated.name
                     )

        # Transfer gold
        gold_amt = 0
        if hasattr(defeated, "gold_min") and hasattr(defeated, "gold_max"):
            gm, gx = defeated.gold_min, defeated.gold_max
            gold_amt = self.rng.randint(gm, gx) if gx > gm else gm
        elif hasattr(defeated, "gold"):
            gold_amt = (
                self.rng.randint(1, defeated.gold)
                if defeated.gold > 0 else 0
            )

        if gold_amt:
            winner.gold += gold_amt
            log.info(
                "%s looted %d gold from %s.",
                winner.name,
                gold_amt,
                defeated.name
            )
        else:
            log.info("%s had no gold to drop.", defeated.name)
