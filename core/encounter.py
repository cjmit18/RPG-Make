"""A turn-based encounter between two groups: `party` and `enemies`.
This module defines the Encounter class, which manages the combat logic between actors."""
import random
from typing import List, Callable, Optional
from core.actor import Actor
from core.combat_functions import CombatCapabilities
class Encounter:
    """
    A turn-based encounter between two groups: `party` and `enemies`.
    """
    def __init__(
        self,
        party: Actor | list[Actor],
        enemies: Actor | list[Actor],
        rng: Optional[random.Random] = None,
        action_fn: Optional[Callable[[Actor], str]] = None,
    ):
        # 1) coerce single Actor → list, or leave list as-is
        self.party   = party   if isinstance(party, list)   else [party]
        self.enemies = enemies if isinstance(enemies, list) else [enemies]

        # 2) FLATTEN into one list of Actors
        self.participants = self.party + self.enemies

        self.rng       = rng or random.Random()
        self.action_fn = action_fn or (lambda actor: "attack")

        # we’ll reuse CombatCapabilities for each 1-on-1 attack
        self._solo_combat = CombatCapabilities

    def _turn_order(self) -> List[Actor]:
        # sort *all* participants by effective speed descending
        return sorted(self.participants, key=lambda a: a.speed, reverse=True)

    def start(self) -> str:
        """Runs the encounter loop until one side is wiped out."""
        while self.party and self.enemies:
            for actor in self._turn_order():
                if actor.health <= 0:
                    continue  # skip dead actors

                # pick targets
                foes = self.enemies if actor in self.party else self.party
                if not foes:
                    break

                target = self.rng.choice(foes)
                action = self.action_fn(actor)

                # use your existing 1-on-1 logic
                combat = self._solo_combat(actor, target, rng=self.rng)
                result = combat.calculate_damage(actor, target)
                print(result)

                # remove dead target
                if target.health <= 0:
                    print(f"{target.name} has fallen!")
                    if target in self.enemies:
                        self.enemies.remove(target)
                    else:
                        self.party.remove(target)

            # optional: break early if one side is gone
            if not self.party:
                return "Enemies win!"
            if not self.enemies:
                return f"{self.party[0].name}'s Party wins!"
        return "Draw?"

