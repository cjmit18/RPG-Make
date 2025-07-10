# game_sys/skills/base.py

from typing import Any, Dict, List
from game_sys.effects.factory import EffectFactory
from game_sys.core.damage_types import DamageType


class Skill:
    # --- ASYNC HOOKS: can be monkey-patched or subclassed --- #
    async def on_pre_execute(self, caster, target):
        """Async hook before skill execution. Override for effects, UI, etc."""
        pass

    async def on_post_execute(self, caster, target, damage):
        """Async hook after skill execution. Override for effects, UI, etc."""
        pass

    async def on_effect_applied(self, effect, caster, target):
        """Async hook after each effect is applied. Override for effects, UI, etc."""
        pass

    async def execute_async(self, caster: Any, target: Any) -> float:
        """Async version of execute with awaitable hooks/effects."""
        from game_sys.core.scaling_manager import ScalingManager
        await self.on_pre_execute(caster, target)
        class _Packet:
            base_damage = self.base_power
            effect_ids = []
            damage_type = self.damage_type
        dmg = ScalingManager.compute_damage(caster, target, _Packet())
        target.take_damage(dmg, caster)
        for eff in self.effects:
            if hasattr(eff, 'apply_async') and callable(getattr(eff, 'apply_async')):
                await eff.apply_async(caster, target)
            else:
                eff.apply(caster, target)
            await self.on_effect_applied(eff, caster, target)
        await self.on_post_execute(caster, target, dmg)
        return dmg
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
        effect_defs: List[Dict],
        level_requirement: int = 1,
        stat_requirements: Dict[str, int] = None
    ):
        self.id = skill_id
        self.name = name
        self.stamina_cost = stamina_cost
        self.cooldown = cooldown
        self.base_power = base_power
        self.level_requirement = level_requirement
        self.stat_requirements = stat_requirements or {}
        
        try:
            self.damage_type = DamageType[damage_type.upper()]
        except KeyError:
            self.damage_type = DamageType.PHYSICAL
        # instantiate effects
        self.effects = [EffectFactory.create(d) for d in effect_defs]

    def can_be_learned_by(self, actor) -> bool:
        """Check if the actor meets the requirements to learn this skill."""
        # Check level requirement
        if hasattr(actor, 'level') and actor.level < self.level_requirement:
            return False
            
        # Check stat requirements
        if hasattr(actor, 'base_stats') and self.stat_requirements:
            for stat, required_value in self.stat_requirements.items():
                current_value = actor.base_stats.get(stat, 0)
                if current_value < required_value:
                    return False
                    
        return True
    
    def get_requirement_text(self) -> str:
        """Get a text description of the skill's requirements."""
        requirements = []
        
        if self.level_requirement > 1:
            requirements.append(f"Level {self.level_requirement}")
            
        if self.stat_requirements:
            for stat, value in self.stat_requirements.items():
                stat_name = stat.replace('_', ' ').title()
                requirements.append(f"{stat_name} {value}")
                
        if requirements:
            return f"Requires: {', '.join(requirements)}"
        else:
            return "No requirements"

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
