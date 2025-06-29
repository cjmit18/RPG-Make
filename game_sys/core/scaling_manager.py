# game_sys/core/scaling_manager.py
"""
Module: game_sys.core.scaling_manager

Computes both base and derived stats, then applies any stat_bonus effects.
If the 'effects' toggle is off, all effect-based adjustments are skipped.
"""
from game_sys.effects.registry import EffectRegistry
from game_sys.config.config_manager import ConfigManager
from game_sys.config.feature_flags import FeatureFlags

flags = FeatureFlags()

class ScalingManager:
    # Derived stat multipliers mapping
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
        cfg = ConfigManager()
        # 1) Base or derived
        if stat_name in cls._derived_map:
            base = actor.base_stats.get(cls._derived_map[stat_name], 0.0)
            mult = cfg.get(f'constants.derived_stats.{stat_name}', 1.0)
            raw = base * mult
        else:
            raw = actor.base_stats.get(stat_name, 0.0)

        # 2) Skip effects if disabled
        if not flags.is_enabled('effects'):
            return raw

        # 3) Apply stat bonuses
        for eid in getattr(actor, 'stat_bonus_ids', []):
            eff = EffectRegistry.get(eid)
            raw = eff.modify_stat(raw, actor)
        return raw

    @classmethod
    def compute_damage(cls, attacker, defender, weapon) -> float:
        """
        Compute final damage, applying passive, skill, and weapon effects,
        and clamping at zero.
        """
        dmg = getattr(weapon, 'base_damage', 0.0)
        if not flags.is_enabled('effects'):
            return max(dmg, 0.0)

        effect_ids = [*getattr(attacker, 'passive_ids', []),
                      *getattr(attacker, 'skill_effect_ids', []),
                      *getattr(weapon, 'effect_ids', [])]
        for eid in effect_ids:
            eff = EffectRegistry.get(eid)
            dmg = eff.modify_damage(dmg, attacker, defender)
        return max(dmg, 0.0)
