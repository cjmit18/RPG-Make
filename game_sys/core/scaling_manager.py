# game_sys/core/scaling_manager.py

from __future__ import annotations
from typing import TYPE_CHECKING

from game_sys.core.damage_types import DamageType
from game_sys.config.config_manager import ConfigManager
from game_sys.config.feature_flags import FeatureFlags
from game_sys.effects.factory import EffectFactory
from game_sys.logging import log_exception, get_logger

if TYPE_CHECKING:
    from game_sys.combat.damage_packet import DamagePacket

flags = FeatureFlags()
scaling_logger = get_logger("game_sys.core.scaling")


class ScalingManager:
    """
    Computes stats and damage with optional effect mods,
    then applies grade & rarity multipliers, and finally weaknesses.
    """

    _derived_map = {
        'attack': 'strength',
        'defense': 'vitality',
        'speed': 'dexterity',
        'dodge_chance': 'dexterity',
        'block_chance': 'constitution',
        'magic_damage': 'magic_power',
        'magic_resistance': 'wisdom',
        'physical_damage': 'strength',
        'damage_reduction': 'vitality',
        'mana_regeneration': 'wisdom',
        'health_regeneration': 'vitality',
        'stamina_regeneration': 'constitution',
        'critical_chance': 'dexterity',
        'luck_factor': 'luck',
        # Resource stats derived from traditional RPG stats
        'health': 'vitality',
        'mana': 'wisdom',
        'stamina': 'constitution',
        'magic_power': 'intelligence'
    }

    @classmethod
    @log_exception
    def compute_stat(cls, actor, stat_name: str) -> float:
        """
        Calculate a stat:
          1) Base or derived stat
          2) Apply all active status‐effects that modify stats
          3) Apply grade multiplier
          4) Apply rarity (job_level) multiplier
        """
        actor_name = getattr(actor, 'name', 'Unknown Actor')
        scaling_logger.debug(f"Computing stat '{stat_name}' for {actor_name}")
        
        cfg = ConfigManager()

        # 1) Base vs derived
        if stat_name in cls._derived_map:
            base_key = cls._derived_map[stat_name]
            base_val = actor.base_stats.get(base_key, 0.0)
            mult = cfg.get(f'constants.derived_stats.{stat_name}', 1.0)
            raw = base_val * mult
            scaling_logger.debug(
                f"Derived stat: {stat_name} from {base_key}={base_val}, "
                f"multiplier={mult}, result={raw}"
            )
        else:
            raw = actor.base_stats.get(stat_name, 0.0)
            scaling_logger.debug(f"Base stat: {stat_name}={raw}")

        # 2) Status‐effect stat modifiers (e.g. StatBonusEffect)
        if flags.is_enabled('effects'):
            scaling_logger.debug("Applying status effects to stat calculation")
            # actor.active_statuses: id -> (Effect instance, duration)
            for eff_id, (eff, _) in getattr(
                actor, 'active_statuses', {}
            ).items():
                if hasattr(eff, 'modify_stat'):
                    old_val = raw
                    raw = eff.modify_stat(raw, actor)
                    scaling_logger.debug(
                        f"Effect {eff_id} modified {stat_name}: {old_val} -> {raw}"
                    )
            
            # Also check stat_bonus_ids for StatBonusEffect instances
            for bonus_id in getattr(actor, 'stat_bonus_ids', []):
                if bonus_id in getattr(actor, 'active_statuses', {}):
                    eff, _ = actor.active_statuses[bonus_id]
                    if hasattr(eff, 'modify_stat'):
                        old_val = raw
                        raw = eff.modify_stat(raw, actor)
                        scaling_logger.debug(
                            f"Bonus {bonus_id} modified {stat_name}: {old_val} -> {raw}"
                        )

        # 3) Grade multiplier (e.g. grade 2 at 0.05 → +10%)
        grade_mult = cfg.get('constants.grade.stat_multiplier', 0.0)
        if getattr(actor, 'grade', None):
            old_val = raw
            raw *= (1.0 + actor.grade * grade_mult)
            scaling_logger.debug(
                f"Applied grade {actor.grade} multiplier: {old_val} -> {raw}"
            )

        # 4) rarity multiplier (e.g. job_level 3 at 0.02 → +6%)
        rarity_mult = cfg.get('constants.rarity.stat_multiplier', 0.0)
        if getattr(actor, 'job_level', None):
            old_val = raw
            raw *= (1.0 + actor.job_level * rarity_mult)
            scaling_logger.debug(
                f"Applied job level {actor.job_level} multiplier: {old_val} -> {raw}"
            )

        scaling_logger.debug(f"Final {stat_name} value for {actor_name}: {raw}")
        return raw

    @classmethod
    def compute_damage(cls, attacker, defender, packet) -> float:
        """
        Legacy method - use compute_damage_from_packet instead.
        
        Compute damage flowing through:
          1) base damage
          2) effect modifiers (flat, percent, elemental)
          3) defender weaknesses (+%)
          4) defender resistances (−%)
          5) final clamp ≥ 0
        """
        dmg = getattr(packet, 'base_damage', 0.0)

        # 1) Effects pipeline
        if flags.is_enabled('effects'):
            effect_ids = (
                getattr(attacker, 'passive_ids', []) +
                getattr(attacker, 'skill_effect_ids', []) +
                getattr(packet, 'effect_ids', [])
            )
            for eid in effect_ids:
                eff = EffectFactory.create_from_id(eid)
                dmg = eff.modify_damage(dmg, attacker, defender)

        # 2) Weakness increases damage
        dtype = getattr(packet, 'damage_type', DamageType.PHYSICAL)
        weak = defender.weaknesses.get(dtype, 0.0)
        dmg *= (1.0 + weak)

        # 3) Resistance reduces damage
        res = defender.resistances.get(dtype, 0.0)
        dmg *= max(0.0, 1.0 - res)

        # 4) Final clamp
        return max(0.0, dmg)

    @classmethod
    @log_exception
    def compute_damage_from_packet(cls, packet: "DamagePacket") -> float:
        """
        Modern damage calculation using DamagePacket struct.
        
        Compute damage flowing through:
          1) base damage with packet modifiers
          2) effect modifiers (flat, percent, elemental)
          3) defender weaknesses (+%)
          4) defender resistances (−%)
          5) armor penetration and final clamp ≥ 0
        """
        if not packet:
            scaling_logger.warning("Attempted to compute damage with null packet")
            return 0.0

        attacker = packet.attacker
        defender = packet.defender
        
        if not attacker or not defender:
            scaling_logger.warning(
                "Invalid damage packet: missing attacker or defender"
            )
            return 0.0

        attacker_name = getattr(attacker, 'name', 'Unknown Attacker')
        defender_name = getattr(defender, 'name', 'Unknown Defender')
        
        scaling_logger.info(
            f"Computing damage from {attacker_name} to {defender_name}"
        )
        
        # Debug packet details
        scaling_logger.debug("Processing damage packet details:")
        scaling_logger.debug(f"  base_damage: {packet.base_damage}")
        scaling_logger.debug(f"  weapon_type: {packet.weapon_type}")
        scaling_logger.debug(f"  modifiers: {packet.damage_modifiers}")
        
        # 1) Start with base damage and apply packet modifiers
        multiplier = packet.get_total_multiplier()
        dmg = packet.base_damage * multiplier
        scaling_logger.debug(f"Total multiplier from modifiers: {multiplier}")
        scaling_logger.debug(f"Initial damage after modifiers: {dmg}")
        
        # 2) Effects pipeline
        if flags.is_enabled('effects') and packet.attacker and packet.defender:
            effect_ids = (
                getattr(packet.attacker, 'passive_ids', []) +
                getattr(packet.attacker, 'skill_effect_ids', []) +
                packet.effect_ids
            )
            scaling_logger.debug(
                f"Processing {len(effect_ids)} effect(s) for damage calculation"
            )
            for eid in effect_ids:
                eff = EffectFactory.create_from_id(eid)
                old_dmg = dmg
                dmg = eff.modify_damage(dmg, packet.attacker, packet.defender)
                scaling_logger.debug(
                    f"Effect {eid} changed damage: {old_dmg:.2f} -> {dmg:.2f}"
                )

        # 3) Weakness increases damage
        if packet.damage_type and packet.defender:
            weak = packet.defender.weaknesses.get(packet.damage_type, 0.0)
            old_dmg = dmg
            dmg *= (1.0 + weak)
            if weak > 0:
                scaling_logger.debug(
                    f"Weakness to {packet.damage_type} increased damage: "
                    f"{old_dmg:.2f} -> {dmg:.2f}"
                )

        # 4) Resistance reduces damage
        if packet.damage_type and packet.defender:
            res = packet.defender.resistances.get(packet.damage_type, 0.0)
            old_dmg = dmg
            dmg *= max(0.0, 1.0 - res)
            if res > 0:
                scaling_logger.debug(
                    f"Resistance reduced damage: {old_dmg:.2f} -> {dmg:.2f}"
                )

        # 5) Apply armor penetration if present
        if packet.penetration > 0.0 and packet.defender:
            # Penetration reduces the effectiveness of armor/resistance
            armor_reduction = packet.defender.get_stat('damage_reduction')
            old_dmg = dmg
            effective_armor = max(0.0, armor_reduction - packet.penetration)
            dmg *= max(0.0, 1.0 - effective_armor)
            scaling_logger.debug(
                f"Armor penetration changed damage: {old_dmg:.2f} -> {dmg:.2f}"
            )

        # 6) Final clamp
        final_dmg = max(0.0, dmg)
        if final_dmg != dmg:
            scaling_logger.debug(f"Damage clamped from {dmg:.2f} to {final_dmg:.2f}")
        
        scaling_logger.info(
            f"Final damage from {attacker_name} to {defender_name}: {final_dmg:.2f}"
        )
        return final_dmg

    @classmethod
    @log_exception
    def calculate_hit_chance(cls, attacker, defender) -> float:
        """Calculate the chance for an attack to hit."""
        attacker_name = getattr(attacker, 'name', 'Unknown Attacker')
        defender_name = getattr(defender, 'name', 'Unknown Defender')
        
        scaling_logger.debug(
            f"Calculating hit chance: {attacker_name} -> {defender_name}"
        )
        
        try:
            # Try to get hit_chance directly first
            hit_chance = attacker.get_stat('hit_chance')
            if hit_chance > 0.0:
                scaling_logger.debug(f"Using direct hit_chance: {hit_chance}")
                # Still consider dodge
                dodge_chance = defender.get_stat('dodge_chance')
                final_hit_chance = max(0.0, min(1.0, hit_chance - dodge_chance))
                scaling_logger.debug(
                    f"Hit calculation: hit={hit_chance:.2f}, "
                    f"dodge={dodge_chance:.2f}, final={final_hit_chance:.2f}"
                )
                return final_hit_chance
            
            # If no hit_chance, fall back to accuracy
            accuracy = attacker.get_stat('accuracy')
            dodge_chance = defender.get_stat('dodge_chance')
            
            # Default accuracy to 0.8 if it's 0 or missing
            if accuracy <= 0.0:
                accuracy = 0.8
                
            # For spells, use a higher base accuracy
            if hasattr(attacker, '_spell_state') and attacker._spell_state:
                accuracy = max(accuracy, 0.9)
                
            hit_chance = max(0.0, min(1.0, accuracy - dodge_chance))
            print(f"DEBUG: calculate_hit_chance: accuracy={accuracy}, dodge={dodge_chance}, final={hit_chance}")
            return hit_chance
        except (AttributeError, KeyError):
            # If any stats are missing, default to 0.8 for weapons, 0.9 for spells
            is_spell = hasattr(attacker, '_spell_state') and attacker._spell_state
            default_hit = 0.9 if is_spell else 0.8
            print(f"DEBUG: Using fallback hit chance ({default_hit}) due to missing stats")
            return default_hit
