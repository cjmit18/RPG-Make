# File: game_sys/combat/combat_engine.py

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
        """
        Initialize the combat engine.

        Args:
            party: List of friendly actors.
            enemies: List of hostile actors.
            rng: Optional random number generator.
            action_fn: Optional function to determine actor actions.
            max_turns: Cap on number of turns before draw.
        """
        self.party = party
        self.enemies = enemies
        self.rng = rng or random.Random()
        self.action_fn = action_fn
        self.max_turns = max_turns
        self.turn = 0

    def _perform_actor_turn(self, actor: Actor, foes: List[Actor]) -> Optional[str]:
        """
        Execute a single actor's turn against a list of foes.

        Args:
            actor: The acting entity.
            foes: List of enemies to target.

        Returns:
            Combat result string if battle is resolved, else None.
        """
        from game_sys.core.hooks import hook_dispatcher
        hook_dispatcher.fire("combat.round_start", engine=self, round=self.turn)

        living_foes = [f for f in foes if f.current_health > 0]
        if not living_foes:
            return None

        target = self.rng.choice(living_foes)
        action = "attack"

        combat = CombatCapabilities(actor, target, rng=self.rng)

        if action == "attack":
            # Attempt to resolve equipped weapon object
            weapon = actor.inventory.get_primary_weapon()
            if isinstance(weapon, EquipableItem):
                # Use full damage map (includes elemental and enchantment bonuses)
                base_map = weapon.total_damage_map()
                dmg_map = {
                    dtype: amount + actor.attack
                    for dtype, amount in base_map.items()
                }
            else:
                # Fallback to flat physical damage using actor attack and target defense
                log.info(f"{weapon} is not an EquipableItem, using base attack damage.  ")
                base_amount = actor.attack - (target.defense * 0.05)
                base_amount = max(0, base_amount)
                dmg_map = {DamageType.PHYSICAL: base_amount}

            # Perform combat roll
            combat.calculate_damage(
                attacker=actor,
                defender=target,
                damage_map=dmg_map,
                stat_name=None,  # Use base attack only, not scaled by stat
                multiplier=1.0,
                crit_chance=0.10, # 10% crit chance
                variance=0.10, # 10% variance in damage
            )

            # Handle defeat and XP/loot distribution
            if target.current_health <= 0:
                xp_share = target.stats_mgr.levels.experience
                if xp_share > 0:
                    living_members = [m for m in self.party if m.current_health > 0]
                    if living_members:
                        share = xp_share // len(living_members)
                        for member in living_members:
                            member.stats_mgr.levels.add_experience(share)
                            log.info("%s receives %d XP from defeating %s.", member.name, share, target.name)

                combat.transfer_loot(winner=actor, defeated=target)

                # Check if combat ends
                if all(f.current_health <= 0 for f in foes):
                    result = "Enemies win! (All party members defeated)" if isinstance(actor, Enemy) else "Party wins! (All enemies defeated)"
                    hook_dispatcher.fire("combat.end", engine=self, result=result)
                    return result

        return None

    def start(self) -> str:
        """
        Begins the main turn loop until combat resolution or turn cap is hit.

        Returns:
            Final combat result string.
        """
        for turn in range(1, self.max_turns + 1):
            self.party.sort(key=lambda a: a.speed, reverse=True)
            for member in self.party:
                if member.current_health <= 0:
                    continue
                result = self._perform_actor_turn(member, self.enemies)
                if result:
                    return result

            self.enemies.sort(key=lambda e: e.speed, reverse=True)
            for foe in self.enemies:
                if foe.current_health <= 0:
                    continue
                result = self._perform_actor_turn(foe, self.party)
                if result:
                    return result

        return "Draw?"

    def run(self) -> str:
        """
        Public method to run the combat loop.

        Returns:
            Final combat result.
        """
        return self.start()
