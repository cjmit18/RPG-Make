# File: game_sys/combat/combat_engine.py

import random
from typing import List, Optional, Callable

from logs.logs import get_logger
from game_sys.core.damage_types import DamageType
from game_sys.character.actor import Actor
from game_sys.combat.combat import CombatCapabilities
from game_sys.character.character_creation import Enemy

log = get_logger(__name__)


class CombatEngine:
    """
    A simple turn-based engine. Each turn,
    party members attack first (in speed order),
    then enemies attack. If someone dies,
    award XP/loot and maybe end the fight.

    For backward compatibility,
    this constructor now accepts an optional action_fn
    parameter (but does not use it internally).
    A caller can invoke `run()` (alias for `start()`) to drive the combat loop.
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

    def _perform_actor_turn(
            self,
            actor: Actor,
            foes: List[Actor]
            ) -> Optional[str]:
        """
        Let actor take an action against one randomly chosen foe
        (among those still alive).
        If the action kills the target, award XP and loot.
        Return a result string if fight over.
        Otherwise return None.
        """
        # 1) Choose a random foe who is still alive
        living_foes = [f for f in foes if f.current_health > 0]
        if not living_foes:
            return None

        target = self.rng.choice(living_foes)

        # 2) Decide action (for now, always "attack")
        action = "attack"

        # 3) Build a CombatCapabilities instance
        combat = CombatCapabilities(actor, target, rng=self.rng)

        if action == "attack":
            # (a) Determine damage by looking at the
            # equipped weapon’s damage map,
            # and always add the actor's attack stat to each entry.
            weapon = actor.inventory.equipment.get("weapon")
            if weapon and getattr(weapon, "damage_map", None):
                # Copy the weapon's base damage map
                base_map = dict(weapon.damage_map)
                # Add the actor's attack to each damage type
                dmg_map = {
                    dtype: amount + actor.attack
                    for dtype, amount in base_map.items()
                }
            else:
                # Fallback: pure physical using attack minus defense
                base_amount = actor.attack - (target.defense * 0.05)
                base_amount = max(0, base_amount)
                dmg_map = {DamageType.PHYSICAL: base_amount}

            # (b) Call calculate_damage with the fully constructed dmg_map,
            #     no further stat-based addition (stat_name=None)
            combat.calculate_damage(
                attacker=actor,
                defender=target,
                damage_map=dmg_map,
                stat_name=None,
                multiplier=1.0,
                crit_chance=0.10,
                variance=0.10,
            )

            # (d) If the target died, award XP/loot and possibly end the fight
            if target.current_health <= 0:
                # Award XP to entire living party (including `actor`)
                xp_share = target.levels.experience
                if xp_share > 0:
                    living_members = [m for m in self.party
                                      if m.current_health > 0]
                    if living_members:
                        share = xp_share // len(living_members)
                        for member in living_members:
                            member.levels.add_experience(share)
                            log.info(
                                "%s receives %d XP from defeating %s.",
                                member.name,
                                share,
                                target.name,
                            )

                # Transfer loot to the actor who landed the killing blow
                combat.transfer_loot(winner=actor, defeated=target)

                # Check if all foes are now dead
                if all(f.current_health <= 0 for f in foes):
                    if isinstance(actor, Enemy):
                        return "Enemies win! (All party members defeated)"
                    else:
                        return "Party wins! (All enemies defeated)"

        # In future, extend this block to support other action types
        return None

    def start(self) -> str:
        """
        Run turns until someone wins or we hit max_turns.
        Returns a final result string like
        “Party wins!”, “Enemies win!”, or “Draw?”
        """
        for turn in range(1, self.max_turns + 1):
            # 1) Party acts in descending speed order
            self.party.sort(key=lambda a: a.speed, reverse=True)
            for member in self.party:
                if member.current_health <= 0:
                    continue  # Member is already dead
                result = self._perform_actor_turn(member, self.enemies)
                if result:
                    return result

            # 2) Enemies act in descending speed order
            self.enemies.sort(key=lambda e: e.speed, reverse=True)
            for foe in self.enemies:
                if foe.current_health <= 0:
                    continue  # Enemy is dead
                result = self._perform_actor_turn(foe, self.party)
                if result:
                    return result

        return "Draw?"

    # To preserve backward compatibility with Encounter.start(),
    # we expose run() as an alias
    def run(self) -> str:
        return self.start()
