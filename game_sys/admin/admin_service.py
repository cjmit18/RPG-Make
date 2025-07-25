#!/usr/bin/env python3
"""
Admin Service
=============

Service for admin/cheat functionality, extracted from newdemo.py 
as part of the decoupling effort.

This service handles:
- Admin mode toggle
- Character grade modification
- Character rarity modification
- Character level modification
- Stat point manipulation
- Admin status tracking
"""

from typing import Dict, Any
from game_sys.logging import get_logger
from game_sys.character.leveling_manager import LevelingManager


class AdminService:
    """Service for admin/cheat functionality."""
    
    def __init__(self):
        """Initialize the admin service."""
        self.logger = get_logger(__name__)
        self.admin_mode = False
        self.infinite_stat_points = False
        
        # Initialize leveling manager for proper stat point calculations
        self.leveling_manager = LevelingManager()
        
        # Admin configuration
        self.max_level = 100
        self.valid_rarities = ['COMMON', 'UNCOMMON', 'RARE', 'EPIC', 'LEGENDARY', 'MYTHIC', 'DIVINE']
        self.grade_mappings = {0: 'ONE', 1: 'TWO', 2: 'THREE', 3: 'FOUR', 4: 'FIVE', 5: 'SIX', 6: 'SEVEN'}
        
        self.logger.info("AdminService initialized")
    
    def toggle_admin_mode(self) -> Dict[str, Any]:
        """
        Toggle admin/cheat mode on or off.
        
        Returns:
            Result dictionary with admin mode status
        """
        try:
            self.admin_mode = not self.admin_mode
            
            if self.admin_mode:
                self.logger.info("Admin mode ENABLED - Cheat functions activated")
                message = "Admin mode ENABLED! Cheat functions are now available."
            else:
                # Disable infinite stat points when leaving admin mode
                self.infinite_stat_points = False
                self.logger.info("Admin mode DISABLED - Cheat functions deactivated")
                message = "Admin mode DISABLED. Cheat functions deactivated."
            
            return {
                'success': True,
                'admin_mode': self.admin_mode,
                'message': message
            }
            
        except Exception as e:
            self.logger.error(f"Failed to toggle admin mode: {e}")
            return {
                'success': False,
                'error': str(e),
                'message': 'Failed to toggle admin mode'
            }
    
    def is_admin_enabled(self) -> bool:
        """Check if admin mode is enabled."""
        return self.admin_mode
    
    def toggle_infinite_stat_points(self) -> Dict[str, Any]:
        """
        Toggle infinite stat points cheat on or off.
        
        Returns:
            Result dictionary with infinite stat points status
        """
        try:
            if not self.admin_mode:
                raise ValueError("Admin mode must be enabled to use cheats")
            
            self.infinite_stat_points = not self.infinite_stat_points
            
            if self.infinite_stat_points:
                message = "Infinite stat points ENABLED! You now have unlimited stat points."
                self.logger.info("Infinite stat points cheat enabled")
            else:
                message = "Infinite stat points DISABLED. Stat points reset to normal."
                self.logger.info("Infinite stat points cheat disabled")
            
            return {
                'success': True,
                'infinite_stat_points': self.infinite_stat_points,
                'message': message
            }
            
        except Exception as e:
            self.logger.error(f"Failed to toggle infinite stat points: {e}")
            return {
                'success': False,
                'error': str(e),
                'message': 'Failed to toggle infinite stat points'
            }
    
    def set_character_grade(self, character: Any, grade: int, grade_name: str = None) -> Dict[str, Any]:
        """
        Set character grade (admin cheat).
        
        Args:
            character: Character object to modify
            grade: Numeric grade (0-6)
            grade_name: Optional grade name override
            
        Returns:
            Result dictionary with grade change status
        """
        try:
            if not self.admin_mode:
                raise ValueError("Admin mode must be enabled to use cheats")
            
            if not character:
                raise ValueError("No character provided")
            
            # Validate grade range - allow 0-6 for grades ONE through SEVEN
            if grade < 0 or grade > 6:
                raise ValueError("Grade must be between 0-6")
            
            old_grade = getattr(character, 'grade', 0)
            old_grade_name = getattr(character, 'grade_name', 'ONE')
            
            # Set the grade
            character.grade = grade
            if grade_name:
                setattr(character, 'grade_name', grade_name)
            else:
                setattr(character, 'grade_name', self.grade_mappings.get(grade, 'ONE'))
            
            # Update character stats to reflect grade changes
            character.update_stats()
            
            new_grade_name = getattr(character, 'grade_name', 'ONE')
            
            self.logger.info(f"Changed character grade from {old_grade_name} to {new_grade_name}")
            return {
                'success': True,
                'old_grade': old_grade,
                'new_grade': grade,
                'old_grade_name': old_grade_name,
                'new_grade_name': new_grade_name,
                'message': f"Character grade changed from {old_grade_name} to {new_grade_name}"
            }
            
        except Exception as e:
            self.logger.error(f"Failed to set character grade: {e}")
            return {
                'success': False,
                'error': str(e),
                'message': 'Failed to set character grade'
            }
    
    def set_character_rarity(self, character: Any, rarity: str) -> Dict[str, Any]:
        """
        Set character rarity (admin cheat).
        
        Args:
            character: Character object to modify
            rarity: Rarity string (COMMON, UNCOMMON, RARE, etc.)
            
        Returns:
            Result dictionary with rarity change status
        """
        try:
            if not self.admin_mode:
                raise ValueError("Admin mode must be enabled to use cheats")
            
            if not character:
                raise ValueError("No character provided")
            
            # Validate rarity
            rarity_upper = rarity.upper()
            if rarity_upper not in self.valid_rarities:
                raise ValueError(f"Invalid rarity '{rarity}'. Valid options: {', '.join(self.valid_rarities)}")
            
            old_rarity = getattr(character, 'rarity', 'COMMON')
            
            # Set the rarity
            character.rarity = rarity_upper
            
            # Update character stats to reflect rarity changes
            character.update_stats()
            
            self.logger.info(f"Changed character rarity from {old_rarity} to {rarity_upper}")
            return {
                'success': True,
                'old_rarity': old_rarity,
                'new_rarity': rarity_upper,
                'message': f"Character rarity changed from {old_rarity} to {rarity_upper}"
            }
            
        except Exception as e:
            self.logger.error(f"Failed to set character rarity: {e}")
            return {
                'success': False,
                'error': str(e),
                'message': 'Failed to set character rarity'
            }
    
    def set_character_level(self, character: Any, level: int) -> Dict[str, Any]:
        """
        Set character level (admin cheat) using proper level-up system.
        
        Args:
            character: Character object to modify
            level: Character level (1-100)
            
        Returns:
            Result dictionary with level change status
        """
        try:
            if not self.admin_mode:
                raise ValueError("Admin mode must be enabled to use cheats")
            
            if not character:
                raise ValueError("No character provided")
            
            # Validate level range
            if level < 1 or level > self.max_level:
                raise ValueError(f"Level must be between 1-{self.max_level}")
            
            old_level = getattr(character, 'level', 1)
            
            if level == old_level:
                return {
                    'success': True,
                    'old_level': old_level,
                    'new_level': level,
                    'available_stat_points': self.leveling_manager.calculate_stat_points_available(character),
                    'message': f"Character is already level {level}"
                }
            
            # Initialize character attributes if they don't exist
            if not hasattr(character, 'level'):
                character.level = 1
            if not hasattr(character, 'experience'):
                character.experience = 0
            if not hasattr(character, 'spent_stat_points'):
                character.spent_stat_points = 0
            
            levels_to_gain = level - old_level
            
            if levels_to_gain > 0:
                # Use proper experience-based leveling system instead of direct level_up()
                # Calculate total XP needed to reach target level
                target_xp = self.leveling_manager.get_total_xp_for_level(level)
                current_xp = getattr(character, 'experience', 0)
                xp_to_add = max(0, target_xp - current_xp)
                
                if xp_to_add > 0:
                    # Use the experience gain system which properly handles level-ups, hooks, and stat points
                    self.leveling_manager.gain_experience(character, xp_to_add)
                
                self.logger.info(f"Admin leveled character from {old_level} to {level} via experience system")
            else:
                # Level down (set level directly and recalculate)
                # This is a cheat so we allow going backwards
                character.level = level
                
                # Reset experience to match the new level
                if hasattr(character, 'experience'):
                    # Set experience to the minimum for this level
                    character.experience = sum(self.leveling_manager._xp_for_next_level(i) for i in range(1, level))
                
                # Update stats to reflect level changes
                if hasattr(character, 'update_stats'):
                    character.update_stats()
                    
                self.logger.info(f"Set character level from {old_level} to {level} (level down)")
            
            # Get final available points after level changes
            available_points = self.leveling_manager.calculate_stat_points_available(character)
            
            return {
                'success': True,
                'old_level': old_level,
                'new_level': level,
                'levels_gained': levels_to_gain,
                'available_stat_points': available_points,
                'message': f"Character level changed from {old_level} to {level} using proper level-up system. Available stat points: {available_points}"
            }
            
        except Exception as e:
            self.logger.error(f"Failed to set character level: {e}")
            return {
                'success': False,
                'error': str(e),
                'message': 'Failed to set character level'
            }
    
    def level_up_character_to_level(self, character: Any, target_level: int) -> Dict[str, Any]:
        """
        Level up character to a specific level using experience gain (most proper method).
        
        Args:
            character: Character object to modify
            target_level: Target level to reach
            
        Returns:
            Result dictionary with level up status
        """
        try:
            if not self.admin_mode:
                raise ValueError("Admin mode must be enabled to use cheats")
            
            if not character:
                raise ValueError("No character provided")
            
            # Validate level range
            if target_level < 1 or target_level > self.max_level:
                raise ValueError(f"Level must be between 1-{self.max_level}")
            
            old_level = getattr(character, 'level', 1)
            
            if target_level <= old_level:
                return {
                    'success': False,
                    'message': f"Target level {target_level} must be higher than current level {old_level}. Use set_character_level for level down."
                }
            
            # Initialize character attributes if they don't exist
            if not hasattr(character, 'level'):
                character.level = 1
            if not hasattr(character, 'experience'):
                character.experience = 0
            
            # Calculate experience needed to reach target level
            current_xp = getattr(character, 'experience', 0)
            current_level = getattr(character, 'level', 1)
            
            # Calculate XP needed step by step from current level to target level
            xp_to_add = 0
            for level in range(current_level, target_level):
                xp_to_add += self.leveling_manager._xp_for_next_level(level)
            
            # Debug logging to see what we're calculating
            self.logger.info(f"Character at level {current_level} with {current_xp} XP, needs {xp_to_add} more XP to reach level {target_level}")
            
            if xp_to_add > 0:
                # Use the proper experience gain system which handles level-ups and stat points
                self.leveling_manager.gain_experience(character, xp_to_add)
            
            new_level = getattr(character, 'level', old_level)
            available_points = self.leveling_manager.calculate_stat_points_available(character)
            
            self.logger.info(f"Leveled up character from {old_level} to {new_level} using experience gain system")
            
            return {
                'success': True,
                'old_level': old_level,
                'new_level': new_level,
                'levels_gained': new_level - old_level,
                'experience_gained': xp_to_add,
                'available_stat_points': available_points,
                'message': f"Character leveled up from {old_level} to {new_level} via experience gain. Available stat points: {available_points}"
            }
            
        except Exception as e:
            self.logger.error(f"Failed to level up character: {e}")
            return {
                'success': False,
                'error': str(e),
                'message': 'Failed to level up character'
            }
    
    def get_character_stat_points_info(self, character: Any) -> Dict[str, Any]:
        """
        Get detailed stat point information for a character.
        
        Args:
            character: Character object to examine
            
        Returns:
            Dictionary with stat point information
        """
        try:
            if not character:
                return {'error': 'No character provided'}
            
            level = getattr(character, 'level', 1)
            spent_points = getattr(character, 'spent_stat_points', 0)
            available_points = self.leveling_manager.calculate_stat_points_available(character)
            points_per_level = self.leveling_manager.get_stat_points_per_level(character)
            # Characters start with base points at level 1, then gain points_per_level for each additional level
            total_points = points_per_level + (level - 1) * points_per_level
            
            return {
                'success': True,
                'level': level,
                'points_per_level': points_per_level,
                'total_points_earned': total_points,
                'spent_points': spent_points,
                'available_points': available_points,
                'message': f"Level {level}: {available_points}/{total_points} stat points available"
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get stat points info: {e}")
            return {
                'success': False,
                'error': str(e),
                'message': 'Failed to get stat points information'
            }
    
    def add_stat_points(self, amount: int = 10) -> Dict[str, Any]:
        """
        Add stat points to available pool (admin cheat).
        
        Args:
            amount: Number of stat points to add
            
        Returns:
            Result dictionary with stat points addition status
        """
        try:
            if not self.admin_mode:
                raise ValueError("Admin mode must be enabled to use cheats")
            
            if amount <= 0:
                raise ValueError("Amount must be positive")
            
            self.logger.info(f"Added {amount} stat points (admin cheat)")
            return {
                'success': True,
                'points_added': amount,
                'message': f"Added {amount} stat points"
            }
            
        except Exception as e:
            self.logger.error(f"Failed to add stat points: {e}")
            return {
                'success': False,
                'error': str(e),
                'message': 'Failed to add stat points'
            }
    
    def get_admin_status(self) -> Dict[str, Any]:
        """
        Get current admin mode status and settings.
        
        Returns:
            Result dictionary with admin status
        """
        try:
            status = {
                'admin_mode': self.admin_mode,
                'infinite_stat_points': self.infinite_stat_points,
                'max_level': self.max_level,
                'valid_rarities': self.valid_rarities,
                'grade_mappings': self.grade_mappings
            }
            
            return {
                'success': True,
                'status': status,
                'message': 'Admin status retrieved successfully'
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get admin status: {e}")
            return {
                'success': False,
                'error': str(e),
                'message': 'Failed to get admin status'
            }
    
    def validate_admin_operation(self, operation_name: str) -> Dict[str, Any]:
        """
        Validate if an admin operation can be performed.
        
        Args:
            operation_name: Name of the operation to validate
            
        Returns:
            Result dictionary with validation status
        """
        try:
            if not self.admin_mode:
                return {
                    'success': False,
                    'error': 'Admin mode disabled',
                    'message': f"Cannot perform '{operation_name}' - admin mode is disabled"
                }
            
            return {
                'success': True,
                'message': f"'{operation_name}' operation is allowed"
            }
            
        except Exception as e:
            self.logger.error(f"Failed to validate admin operation: {e}")
            return {
                'success': False,
                'error': str(e),
                'message': 'Failed to validate admin operation'
            }
    
    def reset_admin_state(self) -> Dict[str, Any]:
        """
        Reset all admin settings to default values.
        
        Returns:
            Result dictionary with reset status
        """
        try:
            self.admin_mode = False
            self.infinite_stat_points = False
            
            self.logger.info("Admin state reset to defaults")
            return {
                'success': True,
                'message': 'Admin state reset to defaults'
            }
            
        except Exception as e:
            self.logger.error(f"Failed to reset admin state: {e}")
            return {
                'success': False,
                'error': str(e),
                'message': 'Failed to reset admin state'
            }
