#!/usr/bin/env python3
"""
Stat Allocation Service
======================

Service for managing stat point allocation, extracted from newdemo.py
as part of the decoupling effort.

This service handles:
- Stat point allocation to characters
- Stat allocation validation
- Stat reset functionality
- Available points calculation
"""

from typing import Dict, Any, Optional
from game_sys.logging import get_logger
from game_sys.character.leveling_manager import LevelingManager
from game_sys.config.config_manager import ConfigManager


class StatAllocationService:
    """Service for managing stat point allocation using leveling manager as base."""
    
    def __init__(self, admin_service=None, leveling_manager=None):
        """
        Initialize the stat allocation service.
        
        Args:
            admin_service: Admin service instance for cheat functionality
            leveling_manager: Leveling manager for stat calculations (optional)
        """
        self.logger = get_logger(__name__)
        self.admin_service = admin_service
        self.leveling_manager = leveling_manager or LevelingManager()
        self.config = ConfigManager()
        
        # Get default stat points from config or leveling manager
        self.default_stat_points = self.config.get('constants.leveling.stat_points_per_level', 3)
        
        self.logger.info("StatAllocationService initialized with leveling manager integration")
    
    def allocate_stat_point(self, character: Any, stat_name: str, 
                           available_points: int, amount: int = 1) -> Dict[str, Any]:
        """
        Allocate stat points to a character.
        
        Args:
            character: Character object to modify
            stat_name: Name of the stat to increase
            available_points: Currently available stat points
            amount: Number of points to allocate
            
        Returns:
            Result dictionary with allocation status
        """
        try:
            if not character:
                raise ValueError("No character provided")
            
            if not stat_name:
                raise ValueError("Stat name is required")
            
            if amount <= 0:
                raise ValueError("Amount must be positive")
            
            # Check if infinite stat points is enabled
            infinite_mode = (self.admin_service and 
                           self.admin_service.is_admin_enabled() and 
                           getattr(self.admin_service, 'infinite_stat_points', False))
            
            # Check stat points availability (unless infinite stat points is enabled)
            if not infinite_mode and available_points < amount:
                raise ValueError(f"Not enough stat points available (need {amount}, have {available_points})")
            
            # Apply stat increase - use BASE stat, not scaled stat
            current_base_value = character.base_stats.get(stat_name, 0)
            new_base_value = current_base_value + amount
            
            # Ensure the stat exists in base_stats (fix for agility, luck, vitality showing as 0)
            if stat_name not in character.base_stats:
                # Get the current scaled value and use it as base if stat wasn't in base_stats
                current_scaled = character.get_stat(stat_name)
                character.base_stats[stat_name] = current_scaled + amount
                self.logger.info(f"Added missing stat {stat_name} to base_stats with value {current_scaled + amount}")
            else:
                # Update the base stat directly
                character.base_stats[stat_name] = new_base_value
            
            # Track spent stat points (important for UI display)
            if not hasattr(character, 'spent_stat_points'):
                character.spent_stat_points = 0
            character.spent_stat_points += amount
                
            character.update_stats()  # Refresh derived stats
            
            # Get the final scaled value for display
            final_scaled_value = character.get_stat(stat_name)
            
            # Calculate remaining points
            if infinite_mode:
                points_remaining = 999  # Keep high number for display
            else:
                points_remaining = available_points - amount
            
            cheat_note = " (CHEAT MODE)" if infinite_mode else ""
            self.logger.info(f"Allocated {amount} points to {stat_name} (new value: {final_scaled_value}){cheat_note}")
            
            return {
                'success': True,
                'stat_name': stat_name,
                'new_value': final_scaled_value,
                'points_remaining': points_remaining,
                'infinite_mode': infinite_mode,
                'message': f"Added {amount} point(s) to {stat_name}{cheat_note}"
            }
            
        except Exception as e:
            self.logger.error(f"Failed to allocate stat point: {e}")
            return {
                'success': False,
                'error': str(e),
                'message': 'Failed to allocate stat point'
            }
    
    def reset_stat_allocation(self, character: Any, template_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Reset character stats to template defaults.
        
        Args:
            character: Character object to reset
            template_data: Template data with base stats
            
        Returns:
            Result dictionary with reset status
        """
        try:
            if not character:
                raise ValueError("No character provided")
            
            if not template_data:
                raise ValueError("Template data is required")
            
            # Store current character's grade and rarity to preserve them
            current_grade = getattr(character, 'grade', 0)
            current_grade_name = getattr(character, 'grade_name', 'ONE')
            current_rarity = getattr(character, 'rarity', 'COMMON')
            current_name = character.name
            
            # Get base stats from template
            base_stats = template_data.get('base_stats', {})
            if not base_stats:
                raise ValueError("Template has no base stats")
            
            # Reset each stat to its base template value
            for stat_name, base_value in base_stats.items():
                character.base_stats[stat_name] = base_value
            
            # Reset spent stat points to 0 since we're going back to base template values
            character.spent_stat_points = 0
            
            # Restore preserved attributes
            character.grade = current_grade
            setattr(character, 'grade_name', current_grade_name)
            character.rarity = current_rarity
            character.name = current_name
            
            # Refresh derived stats
            character.update_stats()
            
            self.logger.info(f"Reset {current_name}'s stats to base values (preserved Grade: {current_grade_name}, Rarity: {current_rarity})")
            return {
                'success': True,
                'character': character,
                'message': f'Stats reset to base values (Grade: {current_grade_name}, Rarity: {current_rarity} preserved)'
            }
                
        except Exception as e:
            self.logger.error(f"Failed to reset stats: {e}")
            return {
                'success': False,
                'error': str(e),
                'message': 'Failed to reset character stats'
            }
    
    def calculate_available_points(self, character: Any) -> int:
        """
        Calculate available stat points for character using leveling manager.
        
        Args:
            character: Character object
            
        Returns:
            Number of available stat points
        """
        try:
            # Use leveling manager for accurate calculation
            return self.leveling_manager.calculate_stat_points_available(character)
            
        except Exception as e:
            self.logger.error(f"Failed to calculate available points: {e}")
            return 0
    
    def validate_stat_allocation(self, stat_name: str, amount: int, available_points: int) -> bool:
        """
        Validate stat allocation request.
        
        Args:
            stat_name: Name of the stat to allocate to
            amount: Number of points to allocate
            available_points: Currently available points
            
        Returns:
            True if allocation is valid, False otherwise
        """
        try:
            if not stat_name:
                return False
            
            if amount <= 0:
                return False
            
            # Check if infinite stat points is enabled
            infinite_mode = (self.admin_service and 
                           self.admin_service.is_admin_enabled() and 
                           getattr(self.admin_service, 'infinite_stat_points', False))
            
            if infinite_mode:
                return True
            
            return available_points >= amount
            
        except Exception as e:
            self.logger.error(f"Failed to validate stat allocation: {e}")
            return False
    
    def get_allocatable_stats(self) -> list:
        """
        Get list of stats that can be allocated to using leveling manager.
        
        Returns:
            List of allocatable stat names
        """
        try:
            return self.leveling_manager.get_allocatable_stats()
        except Exception as e:
            self.logger.error(f"Failed to get allocatable stats: {e}")
            # Fallback to hardcoded list
            return ['strength', 'dexterity', 'vitality', 'intelligence', 
                    'wisdom', 'constitution', 'luck', 'agility', 'charisma']
    
    def get_stat_descriptions(self) -> Dict[str, str]:
        """
        Get descriptions for all allocatable stats using leveling manager.
        
        Returns:
            Dictionary mapping stat names to descriptions
        """
        try:
            return self.leveling_manager.get_stat_descriptions()
        except Exception as e:
            self.logger.error(f"Failed to get stat descriptions: {e}")
            # Fallback to hardcoded descriptions
            return {
                'strength': 'Increases physical damage and carrying capacity',
                'dexterity': 'Improves accuracy, critical hit chance, and evasion',
                'vitality': 'Increases health and health regeneration',
                'intelligence': 'Boosts mana pool and magical damage',
                'wisdom': 'Enhances mana regeneration and magical resistance',
                'constitution': 'Improves defense and damage resistance',
                'luck': 'Affects critical hits, item drops, and random events',
                'agility': 'Increases movement speed and dodge chance',
                'charisma': 'Enhances negotiation, leadership, and social interactions'
            }
    
    def get_stat_impact(self, stat_name: str) -> Dict[str, Any]:
        """
        Get information about what a stat affects using leveling manager.
        
        Args:
            stat_name: Name of the stat
            
        Returns:
            Dictionary with stat impact information
        """
        try:
            # Get numerical impacts from leveling manager
            numerical_impacts = self.leveling_manager.get_stat_impact(stat_name)
            
            # Convert to expected format with additional context
            impact_info = {
                'primary_effects': list(numerical_impacts.keys()) if numerical_impacts else ['Unknown'],
                'derived_stats': list(numerical_impacts.keys()) if numerical_impacts else ['Unknown'],
                'numerical_values': numerical_impacts
            }
            
            # Add skill context based on stat type
            skill_context = {
                'strength': ['Melee combat', 'Heavy weapon usage'],
                'dexterity': ['Ranged combat', 'Stealth', 'Lockpicking'],
                'vitality': ['Endurance', 'Disease resistance'],
                'intelligence': ['All magic schools', 'Research', 'Crafting'],
                'wisdom': ['Divine magic', 'Meditation', 'Awareness'],
                'constitution': ['Poison resistance', 'Disease immunity'],
                'luck': ['Gambling', 'Treasure finding', 'Lucky breaks'],
                'agility': ['Acrobatics', 'Escape', 'Dance'],
                'charisma': ['Persuasion', 'Intimidation', 'Bartering']
            }
            
            impact_info['skills_affected'] = skill_context.get(stat_name, ['Unknown'])
            return impact_info
            
        except Exception as e:
            self.logger.error(f"Failed to get stat impact for {stat_name}: {e}")
            # Fallback to basic info
            return {
                'primary_effects': ['Unknown'],
                'derived_stats': ['Unknown'],
                'skills_affected': ['Unknown'],
                'numerical_values': {}
            }
