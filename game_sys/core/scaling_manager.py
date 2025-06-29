# game_sys/core/scaling_manager.py

from game_sys.core.damage_types import DamageType
from game_sys.config.config_manager import ConfigManager
from game_sys.config.feature_flags import FeatureFlags
from game_sys.effects.factory import EffectFactory

flags = FeatureFlags()

class ScalingManager:
    """
    Computes stats and damage with optional effect mods,
    then applies defender weaknesses & resistances.
    """

    _derived_map = {
        'dodge_chance':       'speed',
        'block_chance':       'stamina',
        'magic_damage':       'intellect',
        'magic_resistance':   'intellect',
        'physical_damage':    'attack',
        'damage_reduction':   'defense',
        'mana_regeneration':  'mana',
        'health_regeneration':'health',
        'stamina_regeneration':'stamina'
    }

    @classmethod
    def compute_stat(cls, actor, stat_name: str) -> float:
        cfg  = ConfigManager()
        # 1) Base vs derived
        if stat_name in cls._derived_map:
            base = actor.base_stats.get(cls._derived_map[stat_name], 0.0)
            mult = cfg.get(f'constants.derived_stats.{stat_name}', 1.0)
            raw  = base * mult
        else:
            raw = actor.base_stats.get(stat_name, 0.0)

        # 2) Apply stat bonuses if enabled
        if flags.is_enabled('effects'):
            for eid in getattr(actor, 'stat_bonus_ids', []):
                eff = EffectFactory.create_from_id(eid)
                raw = eff.modify_stat(raw, actor)
        return raw

    @classmethod
    def compute_damage(cls, attacker, defender, packet) -> float:
        # 0) Base damage
        dmg = getattr(packet, 'base_damage', 0.0)

        # 1) Apply effect‐based modifiers
        if flags.is_enabled('effects'):
            effect_ids = (
                getattr(attacker, 'passive_ids', []) +
                getattr(attacker, 'skill_effect_ids', []) +
                getattr(packet, 'effect_ids', [])
            )
            for eid in effect_ids:
                eff = EffectFactory.create_from_id(eid)
                dmg = eff.modify_damage(dmg, attacker, defender)

        # 2) Weakness → increases damage by (1 + value)
        dtype = getattr(packet, 'damage_type', DamageType.PHYSICAL)
        weak  = defender.weaknesses.get(dtype, 0.0)
        dmg  *= (1.0 + weak)

        # 3) Resistance → reduces damage by (1 - value)
        res   = defender.resistances.get(dtype, 0.0)
        dmg  *= max(0.0, 1.0 - res)

        # 4) Final clamp
        return max(0.0, dmg)
