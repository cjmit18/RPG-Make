# game_sys/combat/encounter.py

"""
A turn-based encounter between two groups: `party` and `enemies`.
This module defines the Encounter class, which manages the combat logic
between actors and now correctly uses “last-hit” for loot and XP.
"""

import random
from typing import List, Callable, Optional
from game_sys.combat.status import StatusEffect
from logs.logs import get_logger
from game_sys.core.actor import Actor
from game_sys.combat.combat import CombatCapabilities
from game_sys.character.character_creation import Enemy

log = get_logger(__name__)


class Encounter:
    """
    A turn-based encounter between two groups: "party" and "enemies".
    This class manages combat logic and awards loot/XP to the character
    who lands the final blow.
    """

    def __init__(
        self,
        party: Actor | list[Actor],
        enemies: Actor | list[Actor],
        rng: Optional[random.Random] = None,
        action_fn: Optional[Callable[[Actor], str]] = None,
    ):
        # 1) Coerce single Actor → list, or leave list as-is
        self.party: List[Actor] = party if isinstance(party, list) else [party]
        self.enemies: List[Actor] = enemies if isinstance(enemies, list) else [enemies]

        # 2) Flatten into one list of Actors
        self.participants: List[Actor] = self.party + self.enemies

        self.rng = rng or random.Random()
        self.action_fn = action_fn or (lambda actor: "attack")

        # We’ll reuse CombatCapabilities for each 1-on-1 attack
        self._solo_combat = CombatCapabilities

        # Ensure each actor has defending flag and last_damager
        for actor in self.participants:
            actor.defending = False
            actor.last_damager = None  # track who last dealt lethal damage

    def _turn_order(self) -> List[Actor]:
        # Sort alive participants by descending speed; dead ones are filtered out later
        return sorted(self.participants, key=lambda a: a.speed, reverse=True)

    def start(self) -> str:
        """
        Runs the encounter loop until one side is wiped out.
        Returns a result string, e.g. "Alice, Bob win!" or "Enemies (Gob1, Gob2) win!".
        """
        for actor in self._turn_order():
            #0 Tick down status effects at the start of each turn
            for eff in list(actor.status_effects):
                eff.tick()
                if eff.is_expired():
                    actor.status_effects.remove(eff)
                    log.info(f"{actor.name} is no longer affected by {eff.name}.")
            # If actor is dead, skip their turn
            if actor.health <= 0:
                continue
        while self.party and self.enemies:
            for actor in self._turn_order():
                # Skip if already dead
                if actor.health <= 0:
                    continue

                # Determine opponents: if actor in party → target an enemy; else → target a party member
                foes = self.enemies if actor in self.party else self.party
                if not foes:
                    break  # no foes left

                target = self.rng.choice(foes)
                action = self.action_fn(actor)

                # Perform the attack/defend using CombatCapabilities._attack so we can tag last_damager
                combat = self._solo_combat(actor, target, rng=self.rng)
                if action.lower() == "attack":
                    outcome = combat._attack(actor, target)
                    log.info(outcome)
                    # If this hit killed the target, tag the killer
                    if target.health <= 0:
                        target.last_damager = actor
                elif action.lower() == "defend":
                    actor.defending = True
                    outcome = f"{actor.name} defends."
                    log.info(outcome)
                else:
                    outcome = f"{actor.name} does nothing."
                    log.info(outcome)

                # If the target just died, handle loot + XP
                if target.health <= 0:
                    log.info(f"{target.name} has fallen!")

                    # Determine killer: use last_damager if set, else default to actor
                    killer = target.last_damager or actor

                    # 1) Award loot to killer (only if target was an enemy)
                    if target in self.enemies and self.party:
                        combat.loot(killer, target)

                    # 2) Award experience: only if target was an Enemy
                    if isinstance(target, Enemy):
                        xp_value = target.levels.experience
                        if xp_value > 0:
                            # Split equally among surviving party members
                            survivors = [p for p in self.party if p.health > 0]
                            if survivors:
                                share = xp_value // len(survivors)
                                for member in survivors:
                                    member.levels.add_experience(share)
                                    log.info(f"{member.name} gains {share} XP from defeating {target.name}.")

                    # 3) Remove the dead target from its side
                    if target in self.enemies:
                        self.enemies.remove(target)
                    elif target in self.party:
                        self.party.remove(target)

            # After the full round, check for victory
            if not self.enemies:
                names = ", ".join(p.name for p in self.party if p.health > 0)
                return f"{names} win!"
            if not self.party:
                names = ", ".join(e.name for e in self.enemies if e.health > 0)
                return f"Enemies ({names}) win!"

        # Should not normally reach here
        return "Draw?"
