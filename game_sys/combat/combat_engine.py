# game_sys/combat/combat_engine.py

import random
from typing import List, Optional, Callable
from logs.logs import get_logger
from game_sys.core.damage_types import DamageType
from game_sys.character.actor import Actor
from game_sys.combat.combat import CombatCapabilities
from game_sys.character.character_creation import Enemy
from game_sys.items.item_base import EquipableItem

log = get_logger(__name__)

class CombatEngine:
    """
    Orchestrates turn-based combat between two teams of actors.
    Handles initiative, attacks, loot, XP distribution, and combat resolution.
    """

    def __init__(
        self,
        party: List[Actor],
        enemies: List[Actor],
        rng: Optional[random.Random] = None,
        action_fn: Optional[Callable] = None,
        max_turns: int = 100,
    ):
        self.party = party
        self.enemies = enemies
        self.rng = rng or random.Random()
        self.action_fn = action_fn
        self.max_turns = max_turns
        self.turn = 0
        self.combat = CombatCapabilities(self.rng)

    def _perform_actor_turn(self, actor: Actor, foes: List[Actor]) -> Optional[str]:
        from game_sys.hooks.hooks import hook_dispatcher
        hook_dispatcher.fire("combat.round_start", engine=self, round=self.turn)

        living_foes = [f for f in foes if f.current_health > 0]
        if not living_foes:
            return None

        target = self.rng.choice(living_foes)
        # Attack logic
        weapon = actor.inventory.get_primary_weapon()
        if isinstance(weapon, EquipableItem):
            base_map = weapon.total_damage_map()
            dmg_map = {dt: amt + actor.attack for dt, amt in base_map.items()}
        else:
            log.info("%s is not an EquipableItem, using base attack damage.", weapon)
            amt = max(0, actor.attack - int(target.defense * 0.05))
            dmg_map = {DamageType.PHYSICAL: amt}

        # Damage roll
        self.combat.calculate_damage(
            attacker=actor,
            defender=target,
            damage_map=dmg_map,
            stat_name=None
        )

        # If defeated, distribute XP & loot
        if target.current_health <= 0:
            xp_share = target.stats_mgr.levels.experience
            if xp_share > 0:
                living = [m for m in self.party if m.current_health > 0]
                if living:
                    share = xp_share // len(living)
                    for m in living:
                        m.stats_mgr.levels.add_experience(share)
                        log.info("%s receives %d XP from defeating %s.", m.name, share, target.name)
            self.combat.transfer_loot(winner=actor, defeated=target)

            if all(f.current_health <= 0 for f in foes):
                result = (
                    "Enemies win! (All party members defeated)"
                    if isinstance(actor, Enemy)
                    else "Party wins! (All enemies defeated)"
                )
                hook_dispatcher.fire("combat.end", engine=self, result=result)
                return result
        return None

    def start(self) -> str:
        for turn in range(1, self.max_turns + 1):
            self.turn = turn
            log.info(f"--- Turn {self.turn} ---")

            self.party.sort(key=lambda a: a.speed, reverse=True)
            for member in self.party:
                if member.current_health <= 0:
                    continue
                res = self._perform_actor_turn(member, self.enemies)
                member.log_turn_summary()
                if res:
                    return res

            self.enemies.sort(key=lambda e: e.speed, reverse=True)
            for foe in self.enemies:
                if foe.current_health <= 0:
                    continue
                res = self._perform_actor_turn(foe, self.party)
                foe.log_turn_summary()
                if res:
                    return res

        return "Draw?"

    def run(self) -> str:
        return self.start()
