# game_sys/magic/base.py

import asyncio
from typing import Any, Dict, List, Optional
from game_sys.effects.factory import EffectFactory
from game_sys.core.damage_types import DamageType
from game_sys.managers.collision_manager import collision_manager
from game_sys.targeting.groups import filter_targets
from game_sys.targeting.shapes import CircleShape, ConeShape, LineShape
from game_sys.hooks.hooks_setup import emit, ON_ABILITY_CAST
from game_sys.magic.combo import ComboManager
from game_sys.core.scaling_manager import ScalingManager


class Spell:
    """
    Represents a mana-consuming spell with optional AOE,
    target-group filtering,
    and combo-triggered effects.

    Attributes:
      - id, name
      - mana_cost, cast_time, cooldown
      - base_power, damage_type
      - effects: List[Effect] after damage
      - shape: optional AOE shape instance
      - target_group: 'enemies', 'allies', 'all', 'self', or 'target'
    """

    def __init__(
        self,
        spell_id: str,
        name: str,
        mana_cost: float,
        cast_time: float,
        cooldown: float,
        base_power: float,
        damage_type: str,
        effect_defs: List[Dict],
        shape_def: Optional[Dict] = None,
        target_group: str = 'target'
    ):
        self.id = spell_id
        self.name = name
        self.mana_cost = mana_cost
        self.cast_time = cast_time
        self.cooldown = cooldown
        self.base_power = base_power
        try:
            self.damage_type = DamageType[damage_type.upper()]
        except KeyError:
            self.damage_type = DamageType.MAGIC
        self.effects = [EffectFactory.create(d) for d in effect_defs]
        self.shape = self._build_shape(shape_def)
        self.target_group = target_group

    def _build_shape(self, sd: Optional[Dict]):
        """Constructs an AOE shape from JSON definition."""
        if not sd:
            return None
        st = sd.get('type', 'circle').lower()
        if st == 'circle':
            return CircleShape(sd['radius'])
        if st == 'cone':
            return ConeShape(sd['angle'], sd['length'])
        if st == 'line':
            return LineShape(sd['width'], sd['length'])
        return None

    async def cast(self, caster: Any, primary_target: Any) -> bool:
        """
        Casts the spell:
         1) Checks and consumes mana,
         2) Waits cast_time,
         3) Queries collision_manager for actors in shape,
         4) Filters by target_group,
         5) Deals damage + applies effects,
         6) Emits ON_ABILITY_CAST & records combos & cooldown.
        """
        # 1) Mana check
        if caster.current_mana < self.mana_cost:
            return False
        caster.current_mana -= self.mana_cost

        # 2) Cast delay
        await asyncio.sleep(self.cast_time)

        # 3) Spatial query
        actors = collision_manager.query(
            shape=self.shape,
            origin=caster.position,
            direction=caster.facing_vector
        )
        # 4) Group filter
        targets = filter_targets(actors, self.target_group, caster, primary_target)

        # 5) Damage + effects
        last_dmg = 0.0
        for tgt in targets:
            class _Packet:
                base_damage = self.base_power
                damage_type = self.damage_type
                effect_ids = []
            dmg = ScalingManager.compute_damage(caster, tgt, _Packet())
            tgt.take_damage(dmg, caster)
            for eff in self.effects:
                eff.apply(caster, tgt)
            last_dmg = dmg

        # 6) Emit event, record combo & cooldown
        emit(ON_ABILITY_CAST, actor=caster, ability=self.id, damage=last_dmg, target=primary_target)
        ComboManager.record_cast(caster, self.id)
        if hasattr(caster, 'spell_cooldowns'):
            caster.spell_cooldowns[self.id] = self.cooldown

        return True
