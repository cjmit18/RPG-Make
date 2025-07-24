# game_sys/character/character_info_service.py
"""
Character Information Service
============================

Comprehensive service for gathering and formatting character information from all
relevant systems including stats, equipment, skills, spells, combat, loot, and progression.
"""

from typing import Dict, List, Any, Optional, Tuple
from game_sys.config.config_manager import ConfigManager
from game_sys.core.scaling_manager import ScalingManager
from game_sys.logging import get_logger
from game_sys.core.damage_types import DamageType

logger = get_logger(__name__)


class CharacterInfoService:
    """Service for comprehensive character information gathering and formatting."""
    
    def __init__(self):
        """Initialize the character info service."""
        self.config = ConfigManager()
    
    def get_comprehensive_character_info(self, character) -> Dict[str, Any]:
        """
        Get all available character information in organized sections.
        
        Args:
            character: The character/actor to analyze
            
        Returns:
            Dictionary with organized character information
        """
        if not character:
            return {'error': 'No character provided'}
        
        try:
            info = {
                'basic_info': self._get_basic_info(character),
                'primary_stats': self._get_primary_stats(character),
                'derived_stats': self._get_derived_stats(character),
                'resource_pools': self._get_resource_pools(character),
                'equipment': self._get_equipment_info(character),
                'combat_stats': self._get_combat_stats(character),
                'resistances': self._get_resistance_info(character),
                'status_effects': self._get_status_effects(character),
                'skills': self._get_skill_info(character),
                'spells': self._get_spell_info(character),
                'progression': self._get_progression_info(character),
                'inventory_summary': self._get_inventory_summary(character)
            }
            
            return info
            
        except Exception as e:
            logger.error(f"Error gathering character info: {e}")
            return {'error': f'Failed to gather character info: {e}'}
    
    def _get_basic_info(self, character) -> Dict[str, Any]:
        """Get basic character information."""
        return {
            'name': getattr(character, 'name', 'Unknown'),
            'level': getattr(character, 'level', 1),
            'experience': getattr(character, 'xp', 0),
            'grade': getattr(character, 'grade', None),
            'grade_name': getattr(character, 'grade_name', 'Unknown'),
            'rarity': getattr(character, 'rarity', 'COMMON'),
            'job': getattr(character, 'job_id', 'None'),
            'gold': getattr(character, 'gold', 0),
            'team': getattr(character, 'team', 'neutral')
        }
    
    def _get_primary_stats(self, character) -> Dict[str, float]:
        """Get primary character stats."""
        primary_stats = {}
        
        # Core stats from RPG systems
        stat_names = [
            'strength', 'dexterity', 'vitality', 'intelligence',
            'wisdom', 'constitution', 'luck', 'agility', 'charisma'
        ]
        
        for stat in stat_names:
            try:
                # Get effective stat value (includes all bonuses)
                value = character.get_stat(stat) if hasattr(character, 'get_stat') else 0
                primary_stats[stat] = value
            except Exception as e:
                logger.warning(f"Failed to get stat {stat}: {e}")
                primary_stats[stat] = 0
        
        return primary_stats
    
    def _get_derived_stats(self, character) -> Dict[str, float]:
        """Get derived/calculated stats."""
        derived_stats = {}
        
        # Combat-related derived stats
        derived_stat_names = [
            'attack', 'defense', 'speed', 'dodge_chance', 'block_chance',
            'critical_chance', 'magic_resistance', 'physical_damage',
            'damage_reduction', 'accuracy', 'evasion', 'parry_chance',
            'resilience', 'focus', 'initiative', 'luck_factor'
        ]
        
        for stat in derived_stat_names:
            try:
                value = character.get_stat(stat) if hasattr(character, 'get_stat') else 0
                derived_stats[stat] = value
            except Exception as e:
                logger.warning(f"Failed to get derived stat {stat}: {e}")
                derived_stats[stat] = 0
        
        return derived_stats
    
    def _get_resource_pools(self, character) -> Dict[str, Dict[str, float]]:
        """Get resource pool information."""
        pools = {}
        
        # Health
        pools['health'] = {
            'current': getattr(character, 'current_health', 0),
            'max': getattr(character, 'max_health', 0),
            'regeneration': character.get_stat('health_regeneration') if hasattr(character, 'get_stat') else 0
        }
        
        # Mana
        pools['mana'] = {
            'current': getattr(character, 'current_mana', 0),
            'max': getattr(character, 'max_mana', 0),
            'regeneration': character.get_stat('mana_regeneration') if hasattr(character, 'get_stat') else 0
        }
        
        # Stamina
        pools['stamina'] = {
            'current': getattr(character, 'current_stamina', 0),
            'max': getattr(character, 'max_stamina', 0),
            'regeneration': character.get_stat('stamina_regeneration') if hasattr(character, 'get_stat') else 0
        }
        
        return pools
    
    def _get_equipment_info(self, character) -> Dict[str, Any]:
        """Get equipment information."""
        equipment = {
            'weapon': None,
            'offhand': None,
            'body_armor': None,
            'helmet': None,
            'feet': None,
            'cloak': None,
            'ring': None,
            'equipment_effects': []
        }
        
        # Get equipped items
        equipment_slots = [
            ('weapon', 'weapon'),
            ('offhand', 'offhand'),
            ('body_armor', 'equipped_body'),
            ('helmet', 'equipped_helmet'),
            ('feet', 'equipped_feet'),
            ('cloak', 'equipped_cloak'),
            ('ring', 'equipped_ring')
        ]
        
        for slot_name, attr_name in equipment_slots:
            if hasattr(character, attr_name):
                item = getattr(character, attr_name)
                if item:
                    equipment[slot_name] = {
                        'name': getattr(item, 'name', 'Unknown'),
                        'type': getattr(item, 'type', 'Unknown'),
                        'level': getattr(item, 'level', 1),
                        'grade': getattr(item, 'grade', 'ONE'),
                        'rarity': getattr(item, 'rarity', 'COMMON'),
                        'stats': self._extract_item_stats(item),
                        'effects': getattr(item, 'effect_ids', [])
                    }
                    
                    # Add effects to overall equipment effects
                    if hasattr(item, 'effect_ids'):
                        equipment['equipment_effects'].extend(item.effect_ids)
        
        return equipment
    
    def _extract_item_stats(self, item) -> Dict[str, Any]:
        """Extract stat bonuses from an item."""
        stats = {}
        
        # Common item attributes that affect stats
        stat_attributes = [
            'attack_bonus', 'defense_bonus', 'health_bonus', 'mana_bonus',
            'strength_bonus', 'dexterity_bonus', 'vitality_bonus',
            'intelligence_bonus', 'wisdom_bonus', 'constitution_bonus',
            'luck_bonus', 'agility_bonus', 'charisma_bonus'
        ]
        
        for attr in stat_attributes:
            if hasattr(item, attr):
                value = getattr(item, attr)
                if value and value != 0:
                    stats[attr] = value
        
        return stats
    
    def _get_combat_stats(self, character) -> Dict[str, Any]:
        """Get combat-related statistics."""
        combat = {
            'last_hit_by': None,
            'last_hit_damage': getattr(character, 'last_hit_damage', 0),
            'kills': len(getattr(character, 'kills', [])),
            'killed_by': None
        }
        
        # Handle complex objects
        if hasattr(character, 'last_hit_by') and character.last_hit_by:
            combat['last_hit_by'] = getattr(character.last_hit_by, 'name', 'Unknown')
        
        if hasattr(character, 'killed_by') and character.killed_by:
            combat['killed_by'] = getattr(character.killed_by, 'name', 'Unknown')
        
        # Cooldowns
        combat['skill_cooldowns'] = getattr(character, 'skill_cooldowns', {})
        combat['spell_cooldowns'] = getattr(character, 'spell_cooldowns', {})
        
        return combat
    
    def _get_resistance_info(self, character) -> Dict[str, Dict[str, float]]:
        """Get resistance and weakness information."""
        resistance_info = {
            'resistances': {},
            'weaknesses': {}
        }
        
        if hasattr(character, 'resistances'):
            for damage_type, value in character.resistances.items():
                resistance_info['resistances'][damage_type.name if hasattr(damage_type, 'name') else str(damage_type)] = value
        
        if hasattr(character, 'weaknesses'):
            for damage_type, value in character.weaknesses.items():
                resistance_info['weaknesses'][damage_type.name if hasattr(damage_type, 'name') else str(damage_type)] = value
        
        return resistance_info
    
    def _get_status_effects(self, character) -> List[Dict[str, Any]]:
        """Get active status effects."""
        effects = []
        
        if hasattr(character, 'active_statuses'):
            for effect_id, (effect_obj, remaining_time) in character.active_statuses.items():
                effects.append({
                    'id': effect_id,
                    'name': getattr(effect_obj, 'name', effect_id),
                    'description': getattr(effect_obj, 'description', 'No description'),
                    'remaining_time': remaining_time,
                    'is_permanent': remaining_time <= 0 and getattr(effect_obj, 'duration', 1) == 0
                })
        
        return effects
    
    def _get_skill_info(self, character) -> Dict[str, Any]:
        """Get skill information."""
        skills = {
            'known_skills': [],
            'available_skills': [],
            'skill_system_active': False
        }
        
        # Check if character has skill system
        if hasattr(character, 'skill_system'):
            skills['skill_system_active'] = True
            try:
                if hasattr(character.skill_system, 'get_known_skills'):
                    skills['known_skills'] = character.skill_system.get_known_skills()
                
                if hasattr(character.skill_system, 'get_available_skills'):
                    skills['available_skills'] = character.skill_system.get_available_skills()
            except Exception as e:
                logger.warning(f"Error getting skill info: {e}")
        
        return skills
    
    def _get_spell_info(self, character) -> Dict[str, Any]:
        """Get spell information."""
        spells = {
            'known_spells': [],
            'available_spells': [],
            'spell_system_active': False,
            'pending_spell': getattr(character, 'pending_spell', None),
            'magic_power': character.get_stat('magic_power') if hasattr(character, 'get_stat') else 0
        }
        
        # Check if character has spell system
        if hasattr(character, 'spell_system'):
            spells['spell_system_active'] = True
            try:
                if hasattr(character.spell_system, 'get_known_spells'):
                    spells['known_spells'] = character.spell_system.get_known_spells()
                
                if hasattr(character.spell_system, 'get_unlearned_spells'):
                    spells['available_spells'] = character.spell_system.get_unlearned_spells()
            except Exception as e:
                logger.warning(f"Error getting spell info: {e}")
        
        return spells
    
    def _get_progression_info(self, character) -> Dict[str, Any]:
        """Get progression and leveling information."""
        progression = {
            'current_level': getattr(character, 'level', 1),
            'current_experience': getattr(character, 'xp', 0),
            'max_level': getattr(character, 'max_level', 100),
            'experience_to_next_level': 0,
            'stat_points_spent': getattr(character, 'spent_stat_points', 0)
        }
        
        # Calculate experience needed for next level
        try:
            if hasattr(character, 'level'):
                current_level = character.level
                # Use leveling manager calculation if available
                if hasattr(character, 'leveling_manager'):
                    progression['experience_to_next_level'] = character.leveling_manager._xp_for_next_level(current_level)
                else:
                    # Fallback calculation
                    base_xp = self.config.get('constants.leveling.xp_base', 100)
                    exponent = self.config.get('constants.leveling.xp_exponent', 1.0)
                    progression['experience_to_next_level'] = int(base_xp * (current_level ** int(exponent)))
        except Exception as e:
            logger.warning(f"Error calculating experience to next level: {e}")
        
        return progression
    
    def _get_inventory_summary(self, character) -> Dict[str, Any]:
        """Get inventory summary information."""
        inventory = {
            'total_items': 0,
            'max_capacity': 0,
            'item_categories': {},
            'valuable_items': []
        }
        
        if hasattr(character, 'inventory'):
            inv_manager = character.inventory
            inventory['total_items'] = len(getattr(inv_manager, 'items', []))
            inventory['max_capacity'] = getattr(inv_manager, 'max_size', 0)
            
            # Categorize items
            categories = {}
            valuable_threshold = 100  # Gold value threshold for "valuable" items
            
            for item in getattr(inv_manager, 'items', []):
                item_type = getattr(item, 'type', 'Misc')
                if item_type not in categories:
                    categories[item_type] = 0
                categories[item_type] += 1
                
                # Check for valuable items
                value = getattr(item, 'value', 0)
                if value >= valuable_threshold:
                    inventory['valuable_items'].append({
                        'name': getattr(item, 'name', 'Unknown'),
                        'value': value,
                        'type': item_type
                    })
            
            inventory['item_categories'] = categories
        
        return inventory
    
    def format_character_display(self, character) -> str:
        """
        Create a formatted text display of comprehensive character information.
        
        Args:
            character: The character to format
            
        Returns:
            Formatted string with all character information
        """
        try:
            info = self.get_comprehensive_character_info(character)
            
            if 'error' in info:
                return f"❌ Error: {info['error']}"
            
            lines = []
            
            # Header with basic info
            basic = info['basic_info']
            lines.append("=" * 80)
            lines.append(f"⚔️ CHARACTER: {basic['name'].upper()}")
            lines.append("=" * 80)
            lines.append(f"📊 Level: {basic['level']} | Grade: {basic['grade_name']} | Rarity: {basic['rarity']}")
            lines.append(f"💼 Job: {basic['job']} | Team: {basic['team']} | Gold: {basic['gold']:,} 💰")
            lines.append(f"✨ Experience: {basic['experience']:,} XP")
            lines.append("")
            
            # Primary Stats Section
            lines.append("📈 PRIMARY ATTRIBUTES")
            lines.append("─" * 50)
            primary = info['primary_stats']
            
            # Format stats in organized columns
            stat_pairs = [
                ('💪 Strength', primary.get('strength', 0), '🎯 Dexterity', primary.get('dexterity', 0)),
                ('❤️ Vitality', primary.get('vitality', 0), '🧠 Intelligence', primary.get('intelligence', 0)),
                ('🔮 Wisdom', primary.get('wisdom', 0), '🛡️ Constitution', primary.get('constitution', 0)),
                ('🍀 Luck', primary.get('luck', 0), '⚡ Agility', primary.get('agility', 0)),
                ('✨ Charisma', primary.get('charisma', 0), '', '')
            ]
            
            for left_name, left_val, right_name, right_val in stat_pairs:
                if right_name:  # Both stats present
                    lines.append(f"{left_name:<20} {left_val:>8.1f}    {right_name:<20} {right_val:>8.1f}")
                else:  # Only left stat
                    lines.append(f"{left_name:<20} {left_val:>8.1f}")
            
            lines.append("")
            
            # Resource Pools Section
            lines.append("🔋 RESOURCE POOLS")
            lines.append("─" * 50)
            pools = info['resource_pools']
            
            for pool_name, pool_data in pools.items():
                current = pool_data['current']
                maximum = pool_data['max']
                regen = pool_data['regeneration']
                percentage = (current / maximum * 100) if maximum > 0 else 0
                
                pool_icons = {'health': '❤️', 'mana': '💙', 'stamina': '💚'}
                icon = pool_icons.get(pool_name, '🔋')
                
                lines.append(f"{icon} {pool_name.title():<12} {current:>6.1f}/{maximum:<6.1f} ({percentage:>5.1f}%) | Regen: {regen:>4.1f}")
            
            lines.append("")
            
            # Combat Stats Section
            lines.append("⚔️ COMBAT STATISTICS")
            lines.append("─" * 50)
            derived = info['derived_stats']
            
            combat_stats = [
                ('Attack Power', derived.get('attack', 0)),
                ('Defense', derived.get('defense', 0)),
                ('Critical Chance', derived.get('critical_chance', 0)),
                ('Dodge Chance', derived.get('dodge_chance', 0)),
                ('Block Chance', derived.get('block_chance', 0)),
                ('Accuracy', derived.get('accuracy', 0)),
                ('Speed', derived.get('speed', 0)),
                ('Initiative', derived.get('initiative', 0))
            ]
            
            for i in range(0, len(combat_stats), 2):
                left = combat_stats[i]
                right = combat_stats[i + 1] if i + 1 < len(combat_stats) else ('', 0)
                
                lines.append(f"{left[0]:<20} {left[1]:>8.1f}    {right[0]:<20} {right[1]:>8.1f}")
            
            lines.append("")
            
            # Equipment Section
            lines.append("🛡️ EQUIPMENT")
            lines.append("─" * 50)
            equipment = info['equipment']
            
            equipment_order = [
                ('Weapon', 'weapon', '⚔️'),
                ('Offhand', 'offhand', '🛡️'),
                ('Body Armor', 'body_armor', '🦺'),
                ('Helmet', 'helmet', '⛑️'),
                ('Feet', 'feet', '👢'),
                ('Cloak', 'cloak', '🧥'),
                ('Ring', 'ring', '💍')
            ]
            
            equipped_count = 0
            for display_name, slot_key, icon in equipment_order:
                item = equipment.get(slot_key)
                if item:
                    equipped_count += 1
                    lines.append(f"{icon} {display_name:<15} {item['name']} (Lvl {item['level']}, {item['rarity']})")
                else:
                    lines.append(f"{icon} {display_name:<15} [Empty]")
            
            lines.append(f"\n📊 Equipment Slots: {equipped_count}/7 filled")
            
            # Equipment Effects
            if equipment['equipment_effects']:
                lines.append(f"✨ Active Effects: {', '.join(equipment['equipment_effects'][:5])}")
                if len(equipment['equipment_effects']) > 5:
                    lines.append(f"    ... and {len(equipment['equipment_effects']) - 5} more")
            
            lines.append("")
            
            # Status Effects Section
            status_effects = info['status_effects']
            if status_effects:
                lines.append("🔮 STATUS EFFECTS")
                lines.append("─" * 50)
                
                for effect in status_effects[:8]:  # Show up to 8 effects
                    if effect['is_permanent']:
                        lines.append(f"♾️ {effect['name']} (Permanent)")
                    else:
                        lines.append(f"⏱️ {effect['name']} ({effect['remaining_time']:.1f}s remaining)")
                
                if len(status_effects) > 8:
                    lines.append(f"    ... and {len(status_effects) - 8} more effects")
                
                lines.append("")
            
            # Skills & Spells Section
            skills = info['skills']
            spells = info['spells']
            
            if skills['skill_system_active'] or spells['spell_system_active']:
                lines.append("🎯 ABILITIES")
                lines.append("─" * 50)
                
                if skills['skill_system_active']:
                    known_count = len(skills['known_skills'])
                    available_count = len(skills['available_skills'])
                    lines.append(f"⚔️ Skills: {known_count} known, {available_count} available")
                
                if spells['spell_system_active']:
                    known_count = len(spells['known_spells'])
                    available_count = len(spells['available_spells'])
                    magic_power = spells['magic_power']
                    lines.append(f"🔮 Spells: {known_count} known, {available_count} available | Magic Power: {magic_power:.1f}")
                
                if spells['pending_spell']:
                    lines.append(f"⏳ Casting: {spells['pending_spell']}")
                
                lines.append("")
            
            # Resistances & Weaknesses
            resistances = info['resistances']
            if resistances['resistances'] or resistances['weaknesses']:
                lines.append("🛡️ RESISTANCES & WEAKNESSES")
                lines.append("─" * 50)
                
                if resistances['resistances']:
                    lines.append("🛡️ Resistances:")
                    for damage_type, value in resistances['resistances'].items():
                        lines.append(f"   {damage_type}: -{value:.1%}")
                
                if resistances['weaknesses']:
                    lines.append("💥 Weaknesses:")
                    for damage_type, value in resistances['weaknesses'].items():
                        lines.append(f"   {damage_type}: +{value:.1%}")
                
                lines.append("")
            
            # Progression Section
            progression = info['progression']
            lines.append("📊 PROGRESSION")
            lines.append("─" * 50)
            lines.append(f"🎯 Level: {progression['current_level']}/{progression['max_level']}")
            lines.append(f"✨ Experience: {progression['current_experience']:,}")
            lines.append(f"📈 Next Level: {progression['experience_to_next_level']:,} XP needed")
            lines.append(f"📊 Stat Points Spent: {progression['stat_points_spent']}")
            lines.append("")
            
            # Inventory Summary
            inventory = info['inventory_summary']
            lines.append("🎒 INVENTORY SUMMARY")
            lines.append("─" * 50)
            lines.append(f"📦 Items: {inventory['total_items']}/{inventory['max_capacity']}")
            
            if inventory['item_categories']:
                lines.append("📋 Categories:")
                for category, count in inventory['item_categories'].items():
                    lines.append(f"   {category}: {count}")
            
            if inventory['valuable_items']:
                lines.append(f"💎 Valuable Items ({len(inventory['valuable_items'])}):")
                for item in inventory['valuable_items'][:3]:  # Show top 3
                    lines.append(f"   {item['name']} - {item['value']:,} gold")
                if len(inventory['valuable_items']) > 3:
                    lines.append(f"   ... and {len(inventory['valuable_items']) - 3} more")
            
            lines.append("")
            lines.append("=" * 80)
            
            return "\n".join(lines)
            
        except Exception as e:
            logger.error(f"Error formatting character display: {e}")
            return f"❌ Error formatting character information: {e}"
