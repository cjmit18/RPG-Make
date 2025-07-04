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
from game_sys.logging import magic_logger, log_exception


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
        target_group: str = 'target',
        level_requirement: int = 1,
        stat_requirements: Dict[str, int] = None
    ):
        self.id = spell_id
        self.name = name
        self.mana_cost = mana_cost
        self.cast_time = cast_time
        self.cooldown = cooldown
        self.base_power = base_power
        self.level_requirement = level_requirement
        self.stat_requirements = stat_requirements or {}
        
        try:
            self.damage_type = DamageType[damage_type.upper()]
            magic_logger.debug(
                f"Spell {name} using damage type: {self.damage_type.name}"
            )
        except KeyError:
            magic_logger.warning(
                f"Invalid damage type '{damage_type}' for spell {name}, "
                f"defaulting to MAGIC"
            )
            self.damage_type = DamageType.MAGIC
        
        self.effects = [EffectFactory.create(d) for d in effect_defs]
        magic_logger.debug(f"Spell {name} loaded with {len(self.effects)} effects")
        
        self.shape = self._build_shape(shape_def)
        self.target_group = target_group
        
        magic_logger.info(
            f"Created spell: {name} (id={spell_id}), power={base_power}, "
            f"cost={mana_cost}, targets={target_group}, level_req={level_requirement}"
        )

    def _build_shape(self, sd: Optional[Dict]):
        """Constructs an AOE shape from JSON definition."""
        if not sd:
            magic_logger.debug(f"Spell {self.name} has no AOE shape")
            return None
            
        st = sd.get('type', 'circle').lower()
        if st == 'circle':
            radius = sd['radius']
            magic_logger.debug(f"Spell {self.name} using circle shape: r={radius}")
            return CircleShape(radius)
        if st == 'cone':
            angle = sd['angle']
            length = sd['length']
            magic_logger.debug(
                f"Spell {self.name} using cone shape: angle={angle}, length={length}"
            )
            return ConeShape(angle, length)
        if st == 'line':
            width = sd['width']
            length = sd['length']
            magic_logger.debug(
                f"Spell {self.name} using line shape: width={width}, length={length}"
            )
            return LineShape(width, length)
            
        magic_logger.warning(f"Unknown shape type '{st}' for spell {self.name}")
        return None

    def can_be_learned_by(self, actor) -> bool:
        """Check if the actor meets the requirements to learn this spell."""
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
        """Get a text description of the spell's requirements."""
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

    @log_exception
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
            magic_logger.warning(
                f"Spell {self.name} cast failed: {caster.name} has insufficient mana "
                f"({caster.current_mana}/{self.mana_cost})"
            )
            return False
            
        magic_logger.info(
            f"{caster.name} casting {self.name} (cost: {self.mana_cost} mana)"
        )
        caster.current_mana -= self.mana_cost

        # 2) Cast delay
        if self.cast_time > 0:
            magic_logger.debug(
                f"{caster.name} spell {self.name} casting for {self.cast_time}s"
            )
            await asyncio.sleep(self.cast_time)

        # 3) Spatial query
        magic_logger.debug(f"Querying targets for {self.name}")
        actors = collision_manager.query(
            shape=self.shape,
            origin=caster.position,
            direction=caster.facing_vector
        )
        
        # 4) Group filter
        targets = filter_targets(
            actors, self.target_group, caster, primary_target
        )
        
        target_count = len(targets)
        magic_logger.debug(
            f"Spell {self.name} found {target_count} valid targets "
            f"(group: {self.target_group})"
        )

        # 5) Damage + effects
        last_dmg = 0.0
        for tgt in targets:
            class _Packet:
                base_damage = self.base_power
                damage_type = self.damage_type
                effect_ids = []
            dmg = ScalingManager.compute_damage(caster, tgt, _Packet())
            tgt.take_damage(dmg, caster)
            
            magic_logger.info(
                f"Spell {self.name} dealt {dmg:.2f} damage to {tgt.name}"
            )
            
            for eff in self.effects:
                result = eff.apply(caster, tgt)
                magic_logger.debug(
                    f"Applied effect {eff.id} to {tgt.name}: {result}"
                )
                
            last_dmg = dmg

        # 6) Emit event, record combo & cooldown
        magic_logger.debug(
            f"Emitting ON_ABILITY_CAST for {self.name} ({self.id})"
        )
        
        emit(
            ON_ABILITY_CAST, 
            actor=caster, 
            ability=self.id, 
            damage=last_dmg, 
            target=primary_target
        )
        
        ComboManager.record_cast(caster, self.id)
        
        if hasattr(caster, 'spell_cooldowns'):
            caster.spell_cooldowns[self.id] = self.cooldown
            magic_logger.debug(
                f"Set cooldown for {self.name}: {self.cooldown}s"
            )

        magic_logger.info(
            f"{caster.name} successfully cast {self.name}"
        )
        return True
