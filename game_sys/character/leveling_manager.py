# game_sys/character/leveling_manager.py
"""
Module: game_sys.character.leveling_manager

Manages character leveling, experience gain, and stat point allocation.
Provides a framework for players to allocate stat points on level up.
Integrates with skills, spells, enchantments and items for level requirements.
"""

from typing import Dict, List, Optional, Set
from game_sys.config.config_manager import ConfigManager
from game_sys.logging import character_logger
from game_sys.hooks.hooks_setup import emit_with_hooks, ON_LEVEL_UP, ON_EXPERIENCE_GAINED, ON_PRELEVEL_UP, ON_POSTLEVEL_UP
import asyncio


class LevelingManager:

    def gain_experience(self, actor, amount):
        """
        Add experience to the actor and handle level up if needed.
        """
        if not hasattr(actor, 'experience'):
            actor.experience = 0
        if not hasattr(actor, 'level'):
            actor.level = 1

        actor.experience += amount
        character_logger.info(f"{getattr(actor, 'name', repr(actor))} gained {amount} XP (total: {actor.experience})")
        emit_with_hooks(ON_EXPERIENCE_GAINED, actor=actor, amount=amount)

        # Check for level up
        xp_for_next_level = self._xp_for_next_level(actor.level)
        while actor.experience >= xp_for_next_level:
            # Pre-level up hook
            emit_with_hooks(ON_PRELEVEL_UP, actor=actor, new_level=actor.level + 1)

            actor.level += 1
            character_logger.info(f"{getattr(actor, 'name', repr(actor))} leveled up to level {actor.level}!")
            emit_with_hooks(ON_LEVEL_UP, actor=actor, new_level=actor.level)

            # Post-level up hook
            emit_with_hooks(ON_POSTLEVEL_UP, actor=actor, new_level=actor.level)

            # Recalculate XP needed for next level
            xp_for_next_level = self._xp_for_next_level(actor.level)
        
    def _xp_for_next_level(self, level):
        cfg = ConfigManager()
        base_xp = cfg.get('constants.leveling.xp_base', 100)
        exponent = cfg.get('constants.leveling.xp_exponent', 1.0)
        return int(base_xp * (level ** int(exponent)))

    def reset_stat_points(self, actor):
        """Reset all allocated stat points for the actor."""
        if not hasattr(actor, 'base_stats'):
            return
        if not hasattr(actor, 'spent_stat_points'):
            actor.spent_stat_points = 0
        # Reset stats to base (10) and refund spent points
        base = 10
        refunded = 0
        for stat in self.allocatable_stats:
            val = actor.base_stats.get(stat, base)
            if val > base:
                refunded += (val - base)
                actor.base_stats[stat] = base
        actor.spent_stat_points = max(0, actor.spent_stat_points - refunded)
        if hasattr(actor, 'update_stats'):
            actor.update_stats()

    def level_up(self, actor):
        """
        Force the actor to level up by one level.
        """
        if not hasattr(actor, 'level'):
            actor.level = 1
        actor.level += 1
        # Optionally, refill health/mana/stamina
        if hasattr(actor, 'max_health'):
            actor.current_health = actor.max_health
        if hasattr(actor, 'max_mana'):
            actor.current_mana = actor.max_mana
        if hasattr(actor, 'max_stamina'):
            actor.current_stamina = actor.max_stamina
    """
    Manages leveling and stat point allocation for characters.
    """
    
    def __init__(self):
        self.cfg = ConfigManager()
        
        # All stats that can be improved with stat points
        # Include both traditional RPG stats and game-specific stats
        self.allocatable_stats = [
            # Traditional RPG stats
            'strength',
            'dexterity', 
            'vitality',
            'intelligence',
            'wisdom',
            'constitution',
            'luck',
            'agility',
        ]
        

    def get_stat_points_per_level(self, actor=None):
        """
        Get the number of stat points awarded per level from config.
        
        If actor is provided, applies grade and rarity multipliers to the base
        stat points per level value, providing more points for higher grades/rarities.
        
        Args:
            actor: Optional actor to calculate bonus points based on grade/rarity
            
        Returns:
            int: Base stat points (default 3) plus any grade/rarity bonuses
        """
        base_points = self.cfg.get('constants.leveling.stat_points_per_level', 3)
        
        if not actor:
            return base_points
            
        # Get grade multiplier
        grade_mult_map = (
            self.cfg.get('constants.grade.stat_multiplier', None)
            or self.cfg.get('grade.stat_multiplier', None)
        )
        grade_mult = 0.0
        grade_key = None
        
        if getattr(actor, 'grade_name', None):
            grade_key = actor.grade_name
        elif hasattr(actor, 'grade') and isinstance(actor.grade, str):
            grade_key = actor.grade
        elif hasattr(actor, 'grade') and isinstance(actor.grade, int):
            grade_list = self.cfg.get('defaults.grades', [])
            if grade_list and 0 <= actor.grade < len(grade_list):
                grade_key = grade_list[actor.grade]
                
        # Calculate grade bonus points
        if isinstance(grade_mult_map, dict):
            if grade_key and grade_key in grade_mult_map:
                grade_mult = grade_mult_map[grade_key]
        elif isinstance(grade_mult_map, (float, int)):
            grade_mult = float(grade_mult_map)
            
        # Get rarity multiplier
        rarity_mult_map = (
            self.cfg.get('constants.rarity.stat_multiplier', None)
            or self.cfg.get('rarity.stat_multiplier', None)
        )
        rarity_mult = 0.0
        rarity_key = None
        
        if getattr(actor, 'rarity_name', None):
            rarity_key = actor.rarity_name
        elif hasattr(actor, 'rarity') and isinstance(actor.rarity, str):
            rarity_key = actor.rarity
        elif hasattr(actor, 'job_level') and isinstance(actor.job_level, int):
            rarity_list = self.cfg.get('defaults.rarities', [])
            if rarity_list and 0 <= actor.job_level < len(rarity_list):
                rarity_key = rarity_list[actor.job_level]
                
        # Calculate rarity bonus points
        if isinstance(rarity_mult_map, dict):
            if rarity_key and rarity_key in rarity_mult_map:
                rarity_mult = rarity_mult_map[rarity_key]
        elif isinstance(rarity_mult_map, (float, int)):
            rarity_mult = float(rarity_mult_map)
            
        # Calculate total bonus points (round to nearest int)
        # The formula boosts base points by grade and rarity multipliers
        total_points = base_points * (1.0 + grade_mult) * (1.0 + rarity_mult)
        return int(total_points)
    
    def get_allocatable_stats(self) -> List[str]:
        """Get the list of stats that can be allocated with stat points."""
        return self.allocatable_stats.copy()
    
    def calculate_stat_points_available(self, actor) -> int:
        """
        Calculate how many stat points an actor should have available.
        Uses the current config value for stat points per level.
        """
        if not hasattr(actor, 'level'):
            return 0
        points_per_level = self.get_stat_points_per_level(actor)
        total_points = (actor.level - 1) * points_per_level
        spent_points = getattr(actor, 'spent_stat_points', 0)
        return max(0, total_points - spent_points)
    
    def allocate_stat_point(self, actor, stat_name: str) -> bool:
        """
        Allocate one stat point to the specified stat.
        Returns True if successful, False if not enough points or invalid stat.
        """
        if stat_name not in self.allocatable_stats:
            character_logger.warning(
                f"Cannot allocate point to {stat_name}: not allocatable"
            )
            return False
            
        available_points = self.calculate_stat_points_available(actor)
        if available_points <= 0:
            character_logger.warning(
                "Cannot allocate point: no points available"
            )
            return False
            
        # Add the stat point
        if not hasattr(actor, 'base_stats'):
            actor.base_stats = {}
            
        current_value = actor.base_stats.get(stat_name, 0)
        actor.base_stats[stat_name] = current_value + 1
        
        # Track spent points
        if not hasattr(actor, 'spent_stat_points'):
            actor.spent_stat_points = 0
        actor.spent_stat_points += 1
        
        # Only log stat allocation if actor is not an enemy (robust check)
        is_enemy = False
        # Set is_enemy attribute if this actor is detected as an enemy
        if hasattr(actor, 'team') and getattr(actor, 'team', None) == 'enemy':
            is_enemy = True
            setattr(actor, 'is_enemy', True)
        elif hasattr(actor, 'enemy') and getattr(actor, 'enemy', False):
            is_enemy = True
            setattr(actor, 'is_enemy', True)
        elif hasattr(actor, 'name') and isinstance(actor.name, str) and actor.name.lower().startswith('enemy'):
            is_enemy = True
            setattr(actor, 'is_enemy', True)
        elif hasattr(actor, 'is_enemy') and getattr(actor, 'is_enemy', False):
            is_enemy = True
        if not is_enemy:
            character_logger.info(f"Allocated 1 point to {stat_name} for {getattr(actor, 'name', repr(actor))}")
        
        # Update derived stats
        if hasattr(actor, 'update_stats'):
            actor.update_stats()
            
        return True
    
    def get_stat_descriptions(self) -> Dict[str, str]:
        """Get descriptions for each allocatable stat."""
        return {
            'strength': 'Increases physical damage and carrying capacity',
            'dexterity': 'Improves accuracy, dodge chance, and critical hit rate',
            'vitality': 'Increases health and health regeneration',
            'intelligence': 'Boosts mana pool and spell damage',
            'wisdom': 'Improves mana regeneration and spell resistance',
            'constitution': 'Increases stamina and resistance to effects',
            'luck': 'Improves critical hit chance and rare item find rate'
        }
    
    def get_stat_impact(self, stat_name: str) -> Dict[str, float]:
        """
        Get the numerical impact of one point in a stat.
        This can be used to show players what each stat point does.
        """
        impacts = {
            'strength': {
                'attack': 0.5,
                'carrying_capacity': 5.0
            },
            'dexterity': {
                'speed': 0.2,
                'critical_chance': 0.01,
                'dodge_chance': 0.01
            },
            'vitality': {
                'health': 10.0,
                'health_regen': 0.1
            },
            'intelligence': {
                'mana': 5.0,
                'spell_damage': 0.3
            },
            'wisdom': {
                'mana_regen': 0.1,
                'spell_resistance': 0.02
            },
            'constitution': {
                'stamina': 3.0,
                'status_resistance': 0.01
            },
            'luck': {
                'critical_chance': 0.005,
                'item_find': 0.01
            }
        }
        
        return impacts.get(stat_name, {})

    def check_requirements(self, actor, requirements: Dict) -> bool:
        """
        Check if an actor meets the requirements for learning something.
        
        Args:
            actor: The actor to check requirements for
            requirements: Dict with 'level', 'stats', etc.
            
        Returns:
            bool: True if requirements are met
        """
        # Check level requirement
        if 'level' in requirements:
            if actor.level < requirements['level']:
                return False
        
        # Check stat requirements
        if 'stats' in requirements:
            if not hasattr(actor, 'base_stats'):
                return False
            for stat, required_value in requirements['stats'].items():
                current_value = actor.base_stats.get(stat, 0)
                if current_value < required_value:
                    return False
        
        # Check experience requirement
        if 'experience' in requirements:
            current_exp = getattr(actor, 'experience', 0)
            if current_exp < requirements['experience']:
                return False
        
        # Check skill prerequisites
        if 'skills' in requirements:
            known_skills = getattr(actor, 'known_skills', [])
            for required_skill in requirements['skills']:
                if required_skill not in known_skills:
                    return False
        
        # Check spell prerequisites
        if 'spells' in requirements:
            known_spells = getattr(actor, 'known_spells', [])
            for required_spell in requirements['spells']:
                if required_spell not in known_spells:
                    return False
        
        return True
    
    def check_enchantment_requirements(self, actor, enchant_data: Dict) -> bool:
        """
        Check if an actor can learn a specific enchantment.
        
        Args:
            actor: The actor to check
            enchant_data: Enchantment data with requirements
            
        Returns:
            bool: True if requirements are met
        """
        requirements = {}
        
        # Extract level requirement
        if 'level_requirement' in enchant_data:
            requirements['level'] = enchant_data['level_requirement']
        
        # Extract stat requirements
        if 'stat_requirements' in enchant_data:
            requirements['stats'] = enchant_data['stat_requirements']
        
        return self.check_requirements(actor, requirements)
    
    def check_spell_requirements(self, actor, spell_input) -> bool:
        """
        Check if an actor can learn a specific spell.
        
        Args:
            actor: The actor to check
            spell_input: Either spell_id (str), spell_data (dict), or Spell
            
        Returns:
            bool: True if requirements are met
        """
        # Handle different input types
        if isinstance(spell_input, str):
            # spell_id - load spell data from JSON
            from game_sys.magic.factory import SpellFactory
            try:
                spell_obj = SpellFactory.create(spell_input)
                spell_data = {
                    'level_requirement': spell_obj.level_requirement,
                    'stat_requirements': spell_obj.stat_requirements
                }
            except Exception:
                return False
        elif hasattr(spell_input, 'level_requirement'):
            # Spell object
            spell_data = {
                'level_requirement': spell_input.level_requirement,
                'stat_requirements': spell_input.stat_requirements
            }
        else:
            # Dictionary
            spell_data = spell_input
        
        requirements = {}
        
        # Extract level requirement
        if 'level_requirement' in spell_data:
            requirements['level'] = spell_data['level_requirement']
        
        # Extract stat requirements
        if 'stat_requirements' in spell_data:
            requirements['stats'] = spell_data['stat_requirements']
        
        # Extract prerequisite spells
        if 'prerequisite_spells' in spell_data:
            requirements['spells'] = spell_data['prerequisite_spells']
        
        return self.check_requirements(actor, requirements)
    
    def check_skill_requirements(self, actor, skill_data: Dict) -> bool:
        """
        Check if an actor can learn a specific skill.
        
        Args:
            actor: The actor to check
            skill_data: Skill data with requirements
            
        Returns:
            bool: True if requirements are met
        """
        requirements = {}
        
        # Extract level requirement
        if 'level_requirement' in skill_data:
            requirements['level'] = skill_data['level_requirement']
        
        # Extract stat requirements
        if 'stat_requirements' in skill_data:
            requirements['stats'] = skill_data['stat_requirements']
        
        # Extract prerequisite skills
        if 'prerequisite_skills' in skill_data:
            requirements['skills'] = skill_data['prerequisite_skills']
        
        return self.check_requirements(actor, requirements)
    
    def get_skill_level_requirement(self, skill_id: str) -> Optional[int]:
        """Get the minimum level required for a skill."""
        # Default level requirements for skills
        skill_level_reqs = {
            'cleave': 3,
            'pierce': 2,
            'whirlwind': 5,
            'berserker_rage': 8,
            'master_strike': 10,
            'double_strike': 4,
            'shield_bash': 3,
            'parry': 2,
            'riposte': 6
        }
        return skill_level_reqs.get(skill_id)
    
    def get_spell_level_requirement(self, spell_id: str) -> Optional[int]:
        """Get the minimum level required for a spell."""
        # Default level requirements for spells
        spell_level_reqs = {
            'fireball': 2,
            'ice_shard': 1,
            'lightning_bolt': 4,
            'heal': 1,
            'greater_heal': 5,
            'meteor': 15,
            'blizzard': 12,
            'teleport': 8,
            'time_stop': 20
        }
        return spell_level_reqs.get(spell_id)
    
    def get_item_level_requirement(self, item_id: str) -> Optional[int]:
        """Get the minimum level required for an item."""
        # Default level requirements for items
        item_level_reqs = {
            'iron_sword': 3,
            'steel_sword': 7,
            'mithril_sword': 12,
            'legendary_sword': 18,
            'leather_armor': 2,
            'chain_mail': 5,
            'plate_armor': 10,
            'dragon_armor': 15,
            'mage_robes': 4,
            'archmage_robes': 12,
            'wooden_shield': 1,
            'iron_shield': 4,
            'tower_shield': 8
        }
        return item_level_reqs.get(item_id)
    
    def get_enchantment_level_requirement(self, enchant_id: str) -> Optional[int]:
        """Get the minimum level required for an enchantment."""
        # Default level requirements for enchantments
        enchant_level_reqs = {
            'fire_enchant': 3,
            'ice_enchant': 3,
            'lightning_enchant': 5,
            'poison_enchant': 4,
            'strength_enchant': 2,
            'speed_enchant': 4,
            'master_enchant': 15,
            'legendary_enchant': 20
        }
        return enchant_level_reqs.get(enchant_id)
    
    def get_skill_stat_requirements(self, skill_id: str) -> Dict[str, int]:
        """Get the stat requirements for a skill."""
        # Default stat requirements for skills
        skill_stat_reqs = {
            'cleave': {'strength': 15},
            'pierce': {'dexterity': 12},
            'whirlwind': {'strength': 20, 'dexterity': 15},
            'berserker_rage': {'strength': 25, 'constitution': 20},
            'master_strike': {'strength': 30, 'dexterity': 25},
            'shield_bash': {'strength': 12, 'constitution': 15},
            'parry': {'dexterity': 15},
            'riposte': {'dexterity': 18, 'intelligence': 12}
        }
        return skill_stat_reqs.get(skill_id, {})
    
    def get_spell_stat_requirements(self, spell_id: str) -> Dict[str, int]:
        """Get the stat requirements for a spell."""
        # Default stat requirements for spells
        spell_stat_reqs = {
            'fireball': {'intelligence': 12},
            'ice_shard': {'intelligence': 10},
            'lightning_bolt': {'intelligence': 15, 'wisdom': 12},
            'heal': {'wisdom': 10},
            'greater_heal': {'wisdom': 20, 'intelligence': 15},
            'meteor': {'intelligence': 35, 'wisdom': 25},
            'blizzard': {'intelligence': 30, 'wisdom': 20},
            'teleport': {'intelligence': 20, 'wisdom': 18},
            'time_stop': {'intelligence': 40, 'wisdom': 35}
        }
        return spell_stat_reqs.get(spell_id, {})
    
    def get_item_stat_requirements(self, item_id: str) -> Dict[str, int]:
        """Get the stat requirements for an item."""
        # Default stat requirements for items
        item_stat_reqs = {
            'iron_sword': {'strength': 12},
            'steel_sword': {'strength': 18},
            'mithril_sword': {'strength': 25, 'dexterity': 20},
            'legendary_sword': {'strength': 35, 'dexterity': 30},
            'chain_mail': {'strength': 15},
            'plate_armor': {'strength': 22, 'constitution': 18},
            'dragon_armor': {'strength': 30, 'constitution': 25},
            'mage_robes': {'intelligence': 15, 'wisdom': 12},
            'archmage_robes': {'intelligence': 30, 'wisdom': 25},
            'tower_shield': {'strength': 20, 'constitution': 18}
        }
        return item_stat_reqs.get(item_id, {})
    
    def get_enchantment_stat_requirements(self, enchant_id: str) -> Dict[str, int]:
        """Get the stat requirements for an enchantment."""
        # Default stat requirements for enchantments
        enchant_stat_reqs = {
            'fire_enchant': {'intelligence': 12},
            'ice_enchant': {'intelligence': 12},
            'lightning_enchant': {'intelligence': 18, 'wisdom': 15},
            'poison_enchant': {'intelligence': 15, 'dexterity': 12},
            'strength_enchant': {'strength': 15},
            'speed_enchant': {'dexterity': 18},
            'master_enchant': {'intelligence': 30, 'wisdom': 25},
            'legendary_enchant': {'intelligence': 40, 'wisdom': 35}
        }
        return enchant_stat_reqs.get(enchant_id, {})
    
    def get_available_skills_for_level(self, actor) -> List[str]:
        """Get all skills that the actor can learn at their current level."""
        available_skills = []
        
        # List of all skills to check
        all_skills = [
            'cleave', 'pierce', 'whirlwind', 'berserker_rage', 'master_strike',
            'double_strike', 'shield_bash', 'parry', 'riposte'
        ]
        
        for skill_id in all_skills:
            if self.check_skill_requirements(actor, skill_id):
                available_skills.append(skill_id)
                
        return available_skills
    
    def get_available_spells_for_level(self, actor) -> List[str]:
        """Get all spells that the actor can learn at their current level."""
        available_spells = []
        
        # List of all spells to check
        all_spells = [
            'fireball', 'ice_shard', 'lightning_bolt', 'heal', 'greater_heal',
            'meteor', 'blizzard', 'teleport', 'time_stop'
        ]
        
        for spell_id in all_spells:
            if self.check_spell_requirements(actor, spell_id):
                available_spells.append(spell_id)
                
        return available_spells
    
    def get_available_items_for_level(self, actor) -> List[str]:
        """Get all items that the actor can use at their current level."""
        available_items = []
        
        # List of all items to check
        all_items = [
            'iron_sword', 'steel_sword', 'mithril_sword', 'legendary_sword',
            'leather_armor', 'chain_mail', 'plate_armor', 'dragon_armor',
            'mage_robes', 'archmage_robes', 'wooden_shield', 'iron_shield',
            'tower_shield'
        ]
        
        for item_id in all_items:
            if self.check_item_requirements(actor, item_id):
                available_items.append(item_id)
                
        return available_items
    
    def get_available_enchantments_for_level(self, actor) -> List[str]:
        """Get all enchantments that the actor can use at current level."""
        available_enchants = []
        
        # List of all enchantments to check
        all_enchants = [
            'fire_enchant', 'ice_enchant', 'lightning_enchant',
            'poison_enchant', 'strength_enchant', 'speed_enchant',
            'master_enchant', 'legendary_enchant'
        ]
        
        for enchant_id in all_enchants:
            if self.check_enchantment_requirements(actor, enchant_id):
                available_enchants.append(enchant_id)
                
        return available_enchants
    
    def get_progression_info(self, actor) -> Dict[str, any]:
        """Get comprehensive progression information for the actor."""
        return {
            'level': actor.level,
            'available_stat_points': self.calculate_stat_points_available(actor),
            'available_skills': self.get_available_skills_for_level(actor),
            'available_spells': self.get_available_spells_for_level(actor),
            'available_items': self.get_available_items_for_level(actor),
            'available_enchantments': self.get_available_enchantments_for_level(actor),
            'next_level_unlocks': self.get_next_level_unlocks(actor)
        }
    
    def get_next_level_unlocks(self, actor) -> Dict[str, List[str]]:
        """Get what will be unlocked at the next level."""
        next_level = actor.level + 1
        unlocks = {
            'skills': [],
            'spells': [],
            'items': [],
            'enchantments': []
        }
        
        # Temporarily increase level to check what becomes available
        original_level = actor.level
        actor.level = next_level
        
        try:
            # Check skills
            for skill_id in ['cleave', 'pierce', 'whirlwind', 'berserker_rage', 
                           'master_strike', 'double_strike', 'shield_bash', 
                           'parry', 'riposte']:
                level_req = self.get_skill_level_requirement(skill_id)
                if level_req == next_level:
                    if self.check_skill_requirements(actor, skill_id):
                        unlocks['skills'].append(skill_id)
            
            # Check spells
            for spell_id in ['fireball', 'ice_shard', 'lightning_bolt', 'heal',
                           'greater_heal', 'meteor', 'blizzard', 'teleport',
                           'time_stop']:
                level_req = self.get_spell_level_requirement(spell_id)
                if level_req == next_level:
                    if self.check_spell_requirements(actor, spell_id):
                        unlocks['spells'].append(spell_id)
            
            # Check items
            for item_id in ['iron_sword', 'steel_sword', 'mithril_sword',
                          'legendary_sword', 'leather_armor', 'chain_mail',
                          'plate_armor', 'dragon_armor', 'mage_robes',
                          'archmage_robes', 'wooden_shield', 'iron_shield',
                          'tower_shield']:
                level_req = self.get_item_level_requirement(item_id)
                if level_req == next_level:
                    if self.check_item_requirements(actor, item_id):
                        unlocks['items'].append(item_id)
            
            # Check enchantments
            for enchant_id in ['fire_enchant', 'ice_enchant', 'lightning_enchant',
                             'poison_enchant', 'strength_enchant', 'speed_enchant',
                             'master_enchant', 'legendary_enchant']:
                level_req = self.get_enchantment_level_requirement(enchant_id)
                if level_req == next_level:
                    if self.check_enchantment_requirements(actor, enchant_id):
                        unlocks['enchantments'].append(enchant_id)
                        
        finally:
            # Restore original level
            actor.level = original_level
            
        return unlocks

    def add_stat_points(self, actor, points):
        """Add a specified number of stat points to the actor."""
        if not hasattr(actor, 'spent_stat_points'):
            actor.spent_stat_points = 0
            
        # We decrease spent_stat_points to effectively add available points
        actor.spent_stat_points = max(0, actor.spent_stat_points - points)
        character_logger.info(f"Added {points} stat points to {actor.name}")
        return True

    def check_item_requirements(self, actor, item_id: str) -> bool:
        """Check if an actor meets the requirements for an item."""
        try:
            # Try to load the item to check its requirements
            from game_sys.items.item_loader import load_item
            item_data = load_item(item_id)
            if not item_data:
                return False
                
            # Check level requirement
            if hasattr(item_data, 'level_requirement'):
                if actor.level < item_data.level_requirement:
                    return False
                    
            # Check stat requirements
            if hasattr(item_data, 'stat_requirements'):
                for stat, required_value in item_data.stat_requirements.items():
                    if (hasattr(actor, 'base_stats') and
                            stat in actor.base_stats):
                        if actor.base_stats[stat] < required_value:
                            return False
                    elif hasattr(actor, stat):
                        if getattr(actor, stat) < required_value:
                            return False
                    else:
                        return False  # Actor doesn't have this stat
                        
            return True
            
        except Exception as e:
            msg = f"Error checking item requirements for {item_id}: {e}"
            character_logger.warning(msg)
            return False

    def get_learned_skills(self, actor) -> List[str]:
        """Get the list of skills the actor has learned."""
        if hasattr(actor, 'known_skills'):
            return actor.known_skills
        return []

    def get_learned_spells(self, actor) -> List[str]:
        """Get the list of spells the actor has learned."""
        if hasattr(actor, 'known_spells'):
            return actor.known_spells
        return []
        
    def get_learned_enchantments(self, actor) -> List[str]:
        """Get the list of enchantments the actor has learned."""
        if hasattr(actor, 'known_enchantments'):
            return actor.known_enchantments
        return []


# Global instance
leveling_manager = LevelingManager()
