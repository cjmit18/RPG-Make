# game_sys/skills/base.py

from typing import Any, Dict, List
from game_sys.effects.factory import EffectFactory
from game_sys.core.damage_types import DamageType


class Skill:
    """
    Represents an active, stamina‐based ability.
    Attributes:
      - id
      - name
      - stamina_cost: float
      - cooldown: float
      - base_power: float
      - damage_type: DamageType
      - effects: List[Effect] (e.g. status, buff, debuff)
    """

    def __init__(
        self,
        skill_id: str,
        name: str,
        stamina_cost: float,
        cooldown: float,
        base_power: float,
        damage_type: str,
        effect_defs: List[Dict]
    ):
        self.id = skill_id
        self.name = name
        self.stamina_cost = stamina_cost
        self.cooldown = cooldown
        self.base_power = base_power
        try:
            self.damage_type = DamageType[damage_type.upper()]
        except KeyError:
            self.damage_type = DamageType.PHYSICAL
        # instantiate effects
        self.effects = [EffectFactory.create(d) for d in effect_defs]

    def execute(self, caster: Any, target: Any) -> float:
        """
        Instantly apply this skill:
        - Checks/consumes stamina (caller must do)
        - Computes damage via ScalingManager
        - Applies damage and extra effects
        Returns the damage dealt.
        """
        from game_sys.core.scaling_manager import ScalingManager
        # dummy “weapon” wrapper

        class _Packet:
            base_damage = self.base_power
            effect_ids = []  # skill‐defined effects are inline
            damage_type = self.damage_type

        dmg = ScalingManager.compute_damage(caster, target, _Packet())
        target.take_damage(dmg, caster)
        # extra effects
        for eff in self.effects:
            eff.apply(caster, target)
        return dmg
