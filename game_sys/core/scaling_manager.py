from __future__ import annotations
from locale import LC_NUMERIC
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

    @staticmethod
    def apply_enemy_stat_boost(enemy):
        """
        Apply a stat boost to an enemy based on level, grade, and rarity.
        Uses config-driven multipliers for all grades, rarities, and levels.
        """
        cfg = ConfigManager()
        level = getattr(enemy, 'level', 1)
        grade = getattr(enemy, 'grade', None)
        rarity = getattr(enemy, 'rarity', None)

        # Get grade and rarity names/keys
        grade_key = None
        rarity_key = None
        grade_list = cfg.get('defaults.grades', []) or []
        rarity_list = cfg.get('defaults.rarities', []) or []
        if isinstance(grade, int) and 0 <= grade < len(grade_list):
            grade_key = grade_list[grade]
        elif isinstance(grade, str):
            grade_key = grade
        if isinstance(rarity, int) and 0 <= rarity < len(rarity_list):
            rarity_key = rarity_list[rarity]
        elif isinstance(rarity, str):
            rarity_key = rarity

        # Get multipliers from config
        grade_mult_map = (
            cfg.get('constants.grade.stat_multiplier', None)
            or cfg.get('grade.stat_multiplier', None)
        )
        rarity_mult_map = (
            cfg.get('constants.rarity.stat_multiplier', None)
            or cfg.get('rarity.stat_multiplier', None)
        )
        grade_mult = 0.0
        rarity_mult = 0.0
        if isinstance(grade_mult_map, dict) and grade_key in grade_mult_map:
            grade_mult = grade_mult_map[grade_key]
        elif isinstance(grade_mult_map, (float, int)):
            grade_mult = float(grade_mult_map)
        if isinstance(rarity_mult_map, dict) and rarity_key in rarity_mult_map:
            rarity_mult = rarity_mult_map[rarity_key]
        elif isinstance(rarity_mult_map, (float, int)):
            rarity_mult = float(rarity_mult_map)

        # Calculate final multiplier
        multiplier = 1.0 + grade_mult + rarity_mult

        # Get strength boost multiplier from config
        strength_boost_mult = cfg.get('constants.combat.strength_multiplier', 1)
        dexterity_boost_mult = cfg.get('constants.combat.dexterity_multiplier', 0.8)
        vitality_boost_mult = cfg.get('constants.combat.vitality_multiplier', 10)
        intelligence_boost_mult = cfg.get('constants.combat.intelligence_multiplier', 5)
        wisdom_boost_mult = cfg.get('constants.combat.wisdom_multiplier', 5)
        constitution_boost_mult = cfg.get('constants.combat.constitution_multiplier', 0.5)
        luck_boost_mult = cfg.get('constants.combat.luck_multiplier', 0.5)
        agility_boost_mult = cfg.get('constants.combat.agility_multiplier', 1)

        # Validate the multiplier value
        if not isinstance(strength_boost_mult, (int, float)):
            scaling_logger.error(
                f"Invalid strength_multiplier: {strength_boost_mult}, using default 1"
            )
            strength_boost_mult = 1
        if not isinstance(dexterity_boost_mult, (int, float)):
            scaling_logger.error(
                f"Invalid dexterity_multiplier: {dexterity_boost_mult}, using default 0.8"
            )
            dexterity_boost_mult = 0.8
        if not isinstance(vitality_boost_mult, (int, float)):
            scaling_logger.error(
                f"Invalid vitality_multiplier: {vitality_boost_mult}, using default 10"
            )
            vitality_boost_mult = 10
        if not isinstance(intelligence_boost_mult, (int, float)):
            scaling_logger.error(
                f"Invalid intelligence_multiplier: {intelligence_boost_mult}, using default 5"
            )
            intelligence_boost_mult = 5
        if not isinstance(wisdom_boost_mult, (int, float)):
            scaling_logger.error(
                f"Invalid wisdom_multiplier: {wisdom_boost_mult}, using default 5"
            )
            wisdom_boost_mult = 5
        if not isinstance(constitution_boost_mult, (int, float)):
            scaling_logger.error(
                f"Invalid constitution_multiplier: {constitution_boost_mult}, using default 0.5"
            )
            constitution_boost_mult = 0.5
        if not isinstance(luck_boost_mult, (int, float)):
            scaling_logger.error(
                f"Invalid luck_multiplier: {luck_boost_mult}, using default 0.5"
            )
            luck_boost_mult = 0.5
        if not isinstance(agility_boost_mult, (int, float)):
            scaling_logger.error(
                f"Invalid agility_multiplier: {agility_boost_mult}, using default 1"
            )
            agility_boost_mult = 1
            
        # Calculate the boost 
        strength_boost = int(level * multiplier * strength_boost_mult)
        dexterity_boost = int(level * multiplier * dexterity_boost_mult)
        vitality_boost = int(level * multiplier * vitality_boost_mult)
        intelligence_boost = int(level * multiplier * intelligence_boost_mult)
        wisdom_boost = int(level * multiplier * wisdom_boost_mult)
        constitution_boost = int(level * multiplier * constitution_boost_mult)
        luck_boost = int(level * multiplier * luck_boost_mult)
        agility_boost = int(level * multiplier * agility_boost_mult)
        boost = {
            'strength': strength_boost,
            'dexterity': dexterity_boost,
            'vitality': vitality_boost,
            'intelligence': intelligence_boost,
            'wisdom': wisdom_boost,
            'constitution': constitution_boost,
            'luck': luck_boost,
            'agility': agility_boost
        }
        if hasattr(enemy, 'base_stats'):
            for stat, value in boost.items():
                old_value = enemy.base_stats.get(stat, 0)
                enemy.base_stats[stat] = old_value + value
                scaling_logger.debug(f"Enemy stat boost: {stat} {old_value} -> {enemy.base_stats[stat]}")

        # Force stat recalculation if the enemy has an update method
        if hasattr(enemy, 'update_stats'):
            enemy.update_stats()
            scaling_logger.debug("Enemy stats updated after boost")
        

    """
    Computes stats and damage with optional effect mods,
    then applies grade & rarity multipliers, and finally weaknesses.
    """

    _derived_map = {
        'attack': 'strength',
        'defense': 'vitality',
        'speed': 'agility',
        'dodge_chance': 'agility',
        'block_chance': 'strength',
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
        'magic_power': 'intelligence',
        # Modernized derived stats
        'accuracy': 'dexterity',
        'evasion': 'agility',
        'parry_chance': 'agility',
        'resilience': 'constitution',
        'focus': 'wisdom',
        'initiative': 'agility'
    }
    
    @classmethod
    @log_exception
    def compute_stat(cls, actor, stat_name: str) -> float:
        """
        Calculate a stat:
          1) Base or derived stat
          2) Apply all active status-effects that modify stats
          3) Apply grade multiplier
          4) Apply rarity (job_level) multiplier
        """
        actor_name = getattr(actor, 'name', 'Unknown Actor')
        scaling_logger.debug(f"Computing stat '{stat_name}' for {actor_name}")
        
        cfg = ConfigManager()

        # 1) Base vs derived
        if stat_name in cls._derived_map:
            base_key = cls._derived_map[stat_name]
            # Use computed base stat (includes buffs/effects) for derived calculations
            # But be careful to avoid circular dependencies
            if base_key == stat_name:
                # Avoid infinite recursion - use raw base stat if computing same stat
                base_val = actor.base_stats.get(base_key, 0.0)
            else:
                # Use computed stat (with buffs) for derived calculations
                base_val = actor.get_stat(base_key)
            
            mult = cfg.get(f'constants.derived_stats.{stat_name}', 1.0)
            
            # Validate numeric types
            if not isinstance(base_val, (int, float)):
                scaling_logger.error(f"Non-numeric base value for {stat_name}: {base_val}, defaulting to 0.0")
                base_val = 0.0
            if not isinstance(mult, (int, float)):
                scaling_logger.error(f"Non-numeric multiplier for {stat_name}: {mult}, defaulting to 1.0")
                mult = 1.0
                
            # Convert to float for consistent multiplication
            base_val = float(base_val)
            mult = float(mult)
            
            derived_component = base_val * mult
            # For defense, also include any direct base defense bonuses
            if stat_name == 'defense':
                base_defense = actor.base_stats.get('defense', 0.0)
                if not isinstance(base_defense, (int, float)):
                    scaling_logger.error(f"Non-numeric base defense: {base_defense}, defaulting to 0.0")
                    base_defense = 0.0
                base_defense = float(base_defense)
                raw = derived_component + base_defense
                scaling_logger.debug(
                    f"Hybrid stat: {stat_name} = derived({base_key}={base_val} "
                    f"* {mult}) + base_defense({base_defense}) = {raw}"
                )
            else:
                raw = derived_component
                scaling_logger.debug(
                    f"Derived stat: {stat_name} from {base_key}={base_val}, "
                    f"multiplier={mult}, result={raw}"
                )

            # Clamp chance-based stats to [0, 1]
            if stat_name in ['parry_chance', 'block_chance', 'dodge_chance', 'critical_chance', 'luck_factor', 'critical_chance_default']:
                if isinstance(raw, (int, float)):
                    if raw < 0:
                        raw = 0.0
                    elif raw > 1:
                        raw = 1.0
        else:
            raw = actor.base_stats.get(stat_name, 0.0)
            scaling_logger.debug(f"Base stat: {stat_name}={raw}")

        # 2) Equipment effects from all equipped items
        if flags.is_enabled('effects'):
            scaling_logger.debug("Applying equipment effects to stat calculation")
            
            # Check all equipped items for effect_ids
            equipped_items = []
            
            # Collect equipped items from various slots
            if hasattr(actor, 'weapon') and actor.weapon:
                equipped_items.append(actor.weapon)
            if hasattr(actor, 'offhand') and actor.offhand:
                equipped_items.append(actor.offhand)
            
            # Armor slots
            for slot in ['body', 'helmet', 'legs', 'feet', 'gloves', 'boots']:
                slot_attr = f'equipped_{slot}'
                if hasattr(actor, slot_attr):
                    item = getattr(actor, slot_attr)
                    if item:
                        equipped_items.append(item)
            
            # Apply effects from all equipped items
            for item in equipped_items:
                if hasattr(item, 'effect_ids'):
                    for eid in item.effect_ids:
                        try:
                            effect = EffectFactory.create_from_id(eid)
                            # Only apply effects that modify stats (like EquipmentStatEffect)
                            # Skip effects that work via other mechanisms (like RegenerationEffect)
                            if (hasattr(effect, 'modify_stat') and 
                                hasattr(effect, 'stat_name')):
                                old_val = raw
                                raw = effect.modify_stat(raw, actor, stat_name)
                                scaling_logger.debug(
                                    f"Equipment effect {eid} from {item.name} "
                                    f"modified {stat_name}: {old_val} -> {raw}"
                                )
                        except Exception as e:
                            scaling_logger.warning(
                                f"Failed to apply equipment effect {eid}: {e}"
                            )

        # 3) Status‐effect stat modifiers (e.g. StatBonusEffect)
        if flags.is_enabled('effects'):
            scaling_logger.debug("Applying status effects to stat calculation")
            # actor.active_statuses: id -> (Effect instance, duration)
            for eff_id, (eff, _) in getattr(
                actor, 'active_statuses', {}
            ).items():
                if hasattr(eff, 'modify_stat'):
                    old_val = raw
                    # Try to pass stat_name parameter for effects that support it,
                    # fall back to 2-parameter call for backward compatibility
                    try:
                        raw = eff.modify_stat(raw, actor, stat_name)
                    except TypeError:
                        # Fallback for effects with 2-parameter modify_stat
                        raw = eff.modify_stat(raw, actor)
                    scaling_logger.debug(
                        f"Effect {eff_id} modified {stat_name}: {old_val} -> {raw}"
                    )
            

        # 3) Grade multiplier (per-grade config mapping)
        # 3) Grade multiplier (per-grade config mapping, robust to float fallback)
        grade_mult_map = (
            cfg.get('constants.grade.stat_multiplier', None)
            or cfg.get('grade.stat_multiplier', None)
        )
        grade_mult = 0.0
        grade_key = None
        if getattr(actor, 'grade_name', None):
            grade_key = actor.grade_name
        elif hasattr(actor, 'grade') and isinstance(actor.grade, str):
            grade_key = actor.grade
        elif hasattr(actor, 'grade') and isinstance(actor.grade, int):
            grade_list = cfg.get('defaults.grades', []) or []
            if isinstance(grade_list, list) and 0 <= actor.grade < len(grade_list):
                grade_key = grade_list[actor.grade]
        # If mapping, use mapping; if float, use as flat multiplier
        if isinstance(grade_mult_map, dict):
            if grade_key and grade_key in grade_mult_map:
                grade_mult = grade_mult_map[grade_key]
        elif isinstance(grade_mult_map, (float, int)):
            grade_mult = float(grade_mult_map)
        # Only apply multiplier to numeric stats
        if grade_mult > 0.0 and isinstance(raw, (int, float)):
            try:
                old_val = raw
                raw = float(raw) * (1.0 + float(grade_mult))
                scaling_logger.debug(
                    f"Applied grade {grade_key} multiplier: {old_val} -> {raw}"
                )
            except Exception as e:
                scaling_logger.error(f"Grade multiplier error for stat '{stat_name}': {e}")

        # 4) Rarity multiplier (per-rarity config mapping, robust to float fallback)
        rarity_mult_map = (
            cfg.get('constants.rarity.stat_multiplier', None)
            or cfg.get('rarity.stat_multiplier', None)
        )
        rarity_mult = 0.0
        rarity_key = None
        if getattr(actor, 'rarity_name', None):
            rarity_key = actor.rarity_name
        elif hasattr(actor, 'rarity') and isinstance(actor.rarity, str):
            rarity_key = actor.rarity
        elif hasattr(actor, 'job_level') and isinstance(actor.job_level, int):
            rarity_list = cfg.get('defaults.rarities', []) or []
            if isinstance(rarity_list, list) and 0 <= actor.job_level < len(rarity_list):
                rarity_key = rarity_list[actor.job_level]
        if isinstance(rarity_mult_map, dict):
            if rarity_key and rarity_key in rarity_mult_map:
                rarity_mult = rarity_mult_map[rarity_key]
        elif isinstance(rarity_mult_map, (float, int)):
            rarity_mult = float(rarity_mult_map)
        # Only apply multiplier to numeric stats
        if rarity_mult > 0.0 and isinstance(raw, (int, float)):
            try:
                old_val = raw
                raw = float(raw) * (1.0 + float(rarity_mult))
                scaling_logger.debug(
                    f"Applied rarity {rarity_key} multiplier: {old_val} -> {raw}"
                )
            except Exception as e:
                scaling_logger.error(f"Rarity multiplier error for stat '{stat_name}': {e}")

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
            f"Computing damage: {attacker_name} -> {defender_name}"
        )
        
        # 1) Effective base damage
        dmg = packet.get_effective_damage()
        scaling_logger.debug(f"Base effective damage: {dmg}")
        
        # Apply a reasonable damage cap based on attacker level and target health
        attacker_level = getattr(attacker, 'level', 1)
        target_max_health = getattr(defender, 'max_health', 100.0)
        
        # Cap damage to a percentage of target's max health based on level difference
        level_diff = max(0, attacker_level - getattr(defender, 'level', 1))
        max_percent_damage = min(0.50, 0.25 + (level_diff * 0.05))  # 25% base, +5% per level diff, max 80%
        damage_cap = target_max_health * max_percent_damage
        
        # Apply damage cap if damage is unreasonably high
        if dmg > damage_cap:
            old_dmg = dmg
            dmg = damage_cap
            scaling_logger.warning(
                f"Damage capped from {old_dmg:.2f} to {dmg:.2f} ({max_percent_damage*100:.0f}% of target health)"
            )
            
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

    @staticmethod
    def auto_allocate_stat_points(character):
        """
        Automatically allocate all available stat points for a character.
        Uses the character's leveling manager if available.
        """
        if not hasattr(character, 'leveling_manager'):
            scaling_logger.warning(f"Character {getattr(character, 'name', 'Unknown')} has no leveling manager for stat allocation")
            return
            
        leveling_manager = character.leveling_manager
        
        # Check if the character has available stat points
        if not hasattr(leveling_manager, 'calculate_stat_points_available'):
            scaling_logger.warning("Leveling manager has no calculate_stat_points_available method")
            return
            
        available_points = leveling_manager.calculate_stat_points_available(character)
        is_enemy = hasattr(character, 'type') and getattr(character, 'type', None) == 'enemy'
        if not is_enemy:
            scaling_logger.info(f"Character {getattr(character, 'name', 'Unknown')} has {available_points} stat points to allocate")
        
        if available_points <= 0:
            if not is_enemy:
                scaling_logger.info("No stat points to allocate")
            return
            
        # Get allocatable stats
        if not hasattr(leveling_manager, 'get_allocatable_stats'):
            scaling_logger.warning("Leveling manager has no get_allocatable_stats method")
            return
            
        allocatable_stats = leveling_manager.get_allocatable_stats()
        if not allocatable_stats:
            scaling_logger.warning("No allocatable stats available")
            return
            
        # Filter to only base RPG stats (not derived stats like attack, defense, etc.)
        base_rpg_stats = ['strength', 'dexterity', 'vitality', 'intelligence', 'wisdom', 'constitution', 'luck', 'agility']
        filtered_stats = [stat for stat in allocatable_stats if stat in base_rpg_stats]
        
        if not filtered_stats:
            scaling_logger.warning("No base RPG stats available for allocation")
            return
            
        if not is_enemy:
            scaling_logger.info(f"Base RPG stats for allocation: {filtered_stats}")
        
        # Distribute points evenly across base RPG stats only
        points_allocated = 0
        for i in range(available_points):
            stat_to_allocate = filtered_stats[i % len(filtered_stats)]
            if hasattr(leveling_manager, 'allocate_stat_point'):
                success = leveling_manager.allocate_stat_point(character, stat_to_allocate)
                if success:
                    points_allocated += 1
                    if not is_enemy:
                        scaling_logger.debug(f"Allocated 1c point to {stat_to_allocate}")
                else:
                    if not is_enemy:
                        scaling_logger.warning(f"Failed to allocate point to {stat_to_allocate}")
            else:
                scaling_logger.warning("Leveling manager has no allocate_stat_point method")
                break
                
        if not is_enemy:
            scaling_logger.info(f"Successfully allocated {points_allocated} out of {available_points} stat points")
        
        # Force stat recalculation
        if hasattr(character, 'update_stats'):
            character.update_stats()
            character.restore_all()
            if not is_enemy:
                scaling_logger.info("Character stats updated after point allocation")