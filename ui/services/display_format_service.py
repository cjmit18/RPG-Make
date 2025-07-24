#!/usr/bin/env python3
"""
Display Format Service
=====================

Service for formatting character display text, extracted from newdemo.py
as part of the decoupling effort.

This service handles:
- Character display formatting
- Template information formatting  
- Stat labels formatting
- Points display formatting
- Character statistics extraction
"""

from typing import Dict, Any
from game_sys.logging import get_logger


class DisplayFormatService:
    """Service for formatting character display text."""
    
    def __init__(self):
        """Initialize the display format service."""
        self.logger = get_logger(__name__)
        self.logger.info("DisplayFormatService initialized")
    
    def format_character_display(self, character: Any) -> str:
        """
        Format full character display text.
        
        Args:
            character: Character object to format
            
        Returns:
            Formatted display text
        """
        try:
            if not character:
                return "No character selected"
            
            stats = self.extract_character_stats(character)
            lines = []
            
            # Character header
            name = stats.get('name', 'Unknown')
            lines.append(f"Character: {name}")
            lines.append("─" * 50)
            
            # Basic information
            level = stats.get('level', 1)
            grade_name = stats.get('grade_name', 'UNKNOWN')
            rarity = stats.get('rarity', 'COMMON')
            lines.append(f"Level: {level}")
            lines.append(f"Grade: {grade_name}")
            lines.append(f"Rarity: {rarity}")
            lines.append("")
            
            # Primary stats with emojis
            lines.append("📊 Primary Stats:")
            stat_emojis = {
                'strength': '💪',
                'dexterity': '🏃',
                'vitality': '❤️',
                'intelligence': '🧠',
                'wisdom': '🔮',
                'constitution': '🛡️',
                'luck': '🍀',
                'agility': '⚡',
                'charisma': '✨'
            }
            
            primary_stats = ['strength', 'dexterity', 'vitality', 'intelligence', 
                           'wisdom', 'constitution', 'luck', 'agility', 'charisma']
            for stat in primary_stats:
                value = stats.get(stat, 0)
                emoji = stat_emojis.get(stat, '📊')
                lines.append(f"   {emoji} {stat.capitalize():<12}: {value:.2f}")
            lines.append("")
            
            # Derived/Combat stats
            lines.append("⚡ Combat Stats:")
            lines.append(f"   ❤️  Health: {stats.get('health', 0)}")
            lines.append(f"   💙 Mana: {stats.get('mana', 0)}")
            lines.append(f"   ⚔️  Attack: {stats.get('attack', 0)}")
            lines.append(f"   🛡️  Defense: {stats.get('defense', 0)}")
            
            return "\n".join(lines)
            
        except Exception as e:
            self.logger.error(f"Failed to format character display: {e}")
            return f"Error formatting character display: {e}"
    
    def format_template_info(self, template_data: Dict[str, Any]) -> str:
        """
        Format template information for display.
        
        Args:
            template_data: Template data dictionary
            
        Returns:
            Formatted template information text
        """
        try:
            lines = []
            
            # Header with template name
            template_name = template_data.get('display_name', template_data.get('name', 'Unknown'))
            lines.append(f"{template_name}")
            lines.append("─" * (len(template_name) + 4))
            
            # Basic info
            template_type = template_data.get('type', 'Unknown')
            job_id = template_data.get('job_id', 'None')
            lines.append(f"Class Type: {template_type}")
            lines.append(f"Job Role: {job_id}")
            lines.append("")
            
            # Description if available
            if 'description' in template_data:
                lines.append("📖 Description:")
                lines.append(f"   {template_data['description']}")
                lines.append("")
            
            # Base statistics with emojis
            if 'base_stats' in template_data:
                stats = template_data['base_stats']
                lines.append("📊 Base Statistics:")
                
                # Primary stats
                stat_emojis = {
                    'strength': '💪',
                    'dexterity': '🏃',
                    'vitality': '❤️',
                    'intelligence': '🧠',
                    'wisdom': '🔮',
                    'constitution': '🛡️',
                    'luck': '🍀',
                    'agility': '⚡',
                    'charisma': '✨'
                }
                
                for stat_name, value in stats.items():
                    emoji = stat_emojis.get(stat_name, '📊')
                    lines.append(f"   {emoji} {stat_name.capitalize():<12}: {value}")
                lines.append("")
            
            # Starting equipment
            if 'starting_items' in template_data and template_data['starting_items']:
                lines.append("🎒 Starting Equipment:")
                for item in template_data['starting_items']:
                    lines.append(f"   • {item}")
                lines.append("")
            
            return "\n".join(lines)
            
        except Exception as e:
            self.logger.error(f"Failed to format template info: {e}")
            return f"Error formatting template info: {e}"
    
    def format_stat_labels(self, character: Any) -> Dict[str, Any]:
        """
        Format stat labels for UI.
        
        Args:
            character: Character object
            
        Returns:
            Dictionary with formatted stat information
        """
        try:
            if not character:
                return {}
            
            stats = self.extract_character_stats(character)
            
            # Format stats for UI display
            formatted_stats = {}
            primary_stats = ['strength', 'dexterity', 'vitality', 'intelligence', 
                           'wisdom', 'constitution', 'luck', 'agility', 'charisma']
            
            for stat in primary_stats:
                value = stats.get(stat, 0)
                formatted_stats[stat] = {
                    'value': value,
                    'display': f"{stat.capitalize()}: {value}"
                }
            
            return {
                'primary_stats': formatted_stats,
                'combat_stats': {
                    'health': stats.get('health', 0),
                    'mana': stats.get('mana', 0),
                    'attack': stats.get('attack', 0),
                    'defense': stats.get('defense', 0)
                }
            }
            
        except Exception as e:
            self.logger.error(f"Failed to format stat labels: {e}")
            return {}
    
    def format_points_display(self, available_points: int, infinite_mode: bool) -> str:
        """
        Format available points display.
        
        Args:
            available_points: Number of available stat points
            infinite_mode: Whether infinite stat points mode is active
            
        Returns:
            Formatted points display string
        """
        try:
            if infinite_mode:
                return "Stat Points: ∞ (Cheat Mode)"
            else:
                return f"Stat Points: {available_points}"
                
        except Exception as e:
            self.logger.error(f"Failed to format points display: {e}")
            return "Stat Points: Error"
    
    def extract_character_stats(self, character: Any) -> Dict[str, Any]:
        """
        Extract character stats for display.
        
        Args:
            character: Character object
            
        Returns:
            Dictionary with character statistics
        """
        try:
            stats = {}
            
            # Basic character info
            stats['name'] = character.name
            stats['level'] = getattr(character, 'level', 1)
            stats['grade'] = getattr(character, 'grade', 0)
            stats['grade_name'] = getattr(character, 'grade_name', 'ONE')
            stats['rarity'] = getattr(character, 'rarity', 'COMMON')
            
            # Primary stats - using safe access
            primary_stats = ['strength', 'dexterity', 'vitality', 'intelligence', 
                           'wisdom', 'constitution', 'luck', 'agility', 'charisma']
            for stat in primary_stats:
                stats[stat] = self._safe_get_stat(character, stat)
            
            # Derived stats
            stats['health'] = self._safe_get_stat(character, 'health')
            stats['mana'] = self._safe_get_stat(character, 'mana')
            stats['attack'] = self._safe_get_stat(character, 'attack')
            stats['defense'] = self._safe_get_stat(character, 'defense')
            
            # Additional derived stats
            stats['stamina'] = self._safe_get_stat(character, 'stamina')
            stats['movement_speed'] = self._safe_get_stat(character, 'movement_speed')
            stats['critical_chance'] = self._safe_get_stat(character, 'critical_chance')
            stats['dodge_chance'] = self._safe_get_stat(character, 'dodge_chance')
            
            return stats
            
        except Exception as e:
            self.logger.error(f"Failed to extract character stats: {e}")
            return {}
    
    def _safe_get_stat(self, character, stat_name: str, default_value=0):
        """Safely get a character stat, returning default if stat doesn't exist."""
        try:
            return character.get_stat(stat_name)
        except (AttributeError, KeyError):
            return default_value
    
    def format_equipment_display(self, character: Any) -> str:
        """
        Get formatted equipment display.
        
        Args:
            character: Character object
            
        Returns:
            Formatted equipment display string
        """
        try:
            # Try to get equipment manager
            if hasattr(character, 'equipment_manager'):
                equipped_items = character.equipment_manager.get_all_equipped()
                if equipped_items:
                    lines = []
                    for slot, item in equipped_items.items():
                        if item:
                            lines.append(f"   {slot.capitalize()}: {item.name}")
                    return "\n".join(lines) if lines else "   No equipment equipped"
                else:
                    return "   No equipment equipped"
            else:
                return "   Equipment system not available"
                
        except Exception as e:
            self.logger.error(f"Error getting equipment display: {e}")
            return "   Error retrieving equipment"
    
    def format_inventory_display(self, character: Any) -> str:
        """
        Get formatted inventory display.
        
        Args:
            character: Character object
            
        Returns:
            Formatted inventory display string
        """
        try:
            if hasattr(character, 'inventory') and character.inventory:
                item_count = len(character.inventory)
                return f"   {item_count} items in inventory"
            else:
                return "   Inventory empty"
                
        except Exception as e:
            self.logger.error(f"Error getting inventory display: {e}")
            return "   Error retrieving inventory"
    
    def format_status_effects_display(self, character: Any) -> str:
        """
        Get formatted status effects display.
        
        Args:
            character: Character object
            
        Returns:
            Formatted status effects display string
        """
        try:
            # Try to get status effects
            if hasattr(character, 'status_manager'):
                active_effects = character.status_manager.get_active_effects()
                if active_effects:
                    status_lines = []
                    for effect_name, effect in active_effects.items():
                        duration = getattr(effect, 'duration', None)
                        if duration and duration > 0:
                            status_lines.append(f"   ✨ {effect_name}: {duration} turns")
                        else:
                            status_lines.append(f"   ⚡ {effect_name}: Permanent")
                    return "\n".join(status_lines)
                else:
                    return "No active status effects"
            else:
                return "No active status effects"
                
        except Exception as e:
            self.logger.error(f"Error getting status effects display: {e}")
            return "Error retrieving status effects"
