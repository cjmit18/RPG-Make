# game_sys/skills/skill_base.py

from typing import List, Any, Dict
from game_sys.character.actor import Actor
from game_sys.combat.combat import CombatCapabilities


class Skill:
    """
    Tracks id, name, mana_cost, stamina_cost, cooldown, and a list of Effects.
    """

    def __init__(
        self,
        skill_id: str,
        name: str,
        description: str,
        mana_cost: int,
        stamina_cost: int,
        cooldown: int,
        effects: List[Any],  # Actually List[Effect]
        requirements: Dict[str, int] = None,
    ) -> None:
        self.id: str = skill_id
        self.name: str = name
        self.description: str = description
        self.mana_cost: int = mana_cost
        self.stamina_cost: int = stamina_cost
        self.cooldown: int = cooldown
        self.effects: List[Any] = list(effects)
        self._current_cooldown: int = 0
        self.requirements: Dict[str, int] = requirements or {}

    def can_cast(self, caster: Actor) -> bool:
        """
        Return True if caster has enough resources and no cooldown.
        """
        if (caster.current_mana < self.mana_cost or
                caster.current_stamina < self.stamina_cost):
            return False
        if self._current_cooldown > 0:
            return False
        for req, amount in self.requirements.items():
            if getattr(caster, req, 0) < amount:
                return False
        return True

    def use(
        self,
        caster: Actor,
        target: Actor,
        combat_engine: CombatCapabilities
    ) -> str:
        """
        1) Check can_cast. If false, return a warning string.
        2) Deduct mana/stamina, set cooldown.
        3) For each effect in self.effects, call
           eff.apply(caster, target, combat_engine)
           and collect its return string.
        4) Return the concatenated log lines.
        """
        if not self.can_cast(caster):
            return f"{caster.name} cannot cast {self.name} right now."

        # (A) Deduct resources
        caster.current_mana -= self.mana_cost
        caster.current_stamina -= self.stamina_cost

        # (B) Apply each Effect
        log_parts: List[str] = []
        for eff in self.effects:
            try:
                msg = eff.apply(caster, target, combat_engine)
                log_parts.append(msg)
            except Exception as e:
                log_parts.append(
                    f"Error applying effect {type(eff).__name__}: {e}"
                )

        # (C) Set cooldown
        self._current_cooldown = self.cooldown

        # (D) Combine all logs into one response string
        return "\n".join(log_parts)
    cast = use  # Alias for compatibility

    def tick_cooldown(self) -> None:
        """
        Decrement cooldown by 1 (clamped at zero).
        """
        if self._current_cooldown > 0:
            self._current_cooldown -= 1
