# game_sys/character/character_service.py
"""
Character Service
=================

High-level service for character creation and management.
Handles random assignment of grades, rarities, and levels based on templates.
"""

import random
from typing import Dict, Any, Optional
from game_sys.character.character_factory import CharacterFactory
from game_sys.config.config_manager import ConfigManager
from game_sys.logging import character_logger


class CharacterService:
    """Service for character creation and management."""
    
    def __init__(self):
        """Initialize the character service."""
        self.cfg = ConfigManager()
        
        # Get available grades and rarities from config
        self.grades = self.cfg.get('defaults.grades', [
            "ONE", "TWO", "THREE", "FOUR", "FIVE", "SIX", "SEVEN"
        ])
        
        self.rarities = self.cfg.get('defaults.rarities', [
            "COMMON", "UNCOMMON", "RARE", "EPIC", 
            "LEGENDARY", "MYTHIC", "DIVINE"
        ])
    
    def create_character_with_random_stats(
        self, template_id: str, **overrides
    ) -> Optional[Any]:
        """
        Create a character with randomly assigned grade, rarity, and level
        based on template constraints.
        
        Args:
            template_id: ID of the character template
            **overrides: Optional overrides for specific attributes
            
        Returns:
            Created character or None if creation failed
        """
        try:
            # Load the template to get constraints
            template = self._get_template_data(template_id)
            if not template:
                character_logger.error(f"Template not found: {template_id}")
                return None
            
            # Generate random stats based on template constraints
            random_stats = self._generate_random_stats(template)
            
            # Apply any overrides
            random_stats.update(overrides)
            
            # Create the character
            character = CharacterFactory.create(
                template_id=template_id,
                **random_stats
            )
            
            if character:
                character_logger.info(
                    f"Created {character.name} - Level: {character.level}, "
                    f"Grade: {character.grade}, Rarity: {character.rarity}"
                )
            
            return character
            
        except Exception as e:
            character_logger.error(f"Error creating character {template_id}: {e}")
            return None
    
    def _get_template_data(self, template_id: str) -> Optional[Dict[str, Any]]:
        """Get template data from the character factory."""
        try:
            # Access the template data directly from the CharacterFactory class
            # First, ensure templates are loaded
            CharacterFactory._load_templates()
            return CharacterFactory._templates.get(template_id.lower())
        except Exception as e:
            character_logger.error(f"Error loading template {template_id}: {e}")
            return None
    
    def _generate_random_stats(self, template: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate random stats based on template constraints.
        
        Args:
            template: Character template data
            
        Returns:
            Dictionary with randomly generated stats
        """
        stats = {}
        
        # Generate random level
        level_constraint = template.get('level', 1)
        if isinstance(level_constraint, dict):
            # Handle template format: {"start": X, "start_xp": Y}
            if 'start' in level_constraint:
                max_level = level_constraint['start']
                stats['level'] = random.randint(1, max_level)
            else:
                # Handle explicit min/max format
                min_level = level_constraint.get('min', 1)
                max_level = level_constraint.get('max', 10)
                stats['level'] = random.randint(min_level, max_level)
        elif isinstance(level_constraint, int):
            # If it's just a number, treat it as max level
            stats['level'] = random.randint(1, level_constraint)
        else:
            stats['level'] = 1
        
        # Generate random grade
        grade_constraint = template.get('grade', 5)
        if isinstance(grade_constraint, dict):
            max_grade_name = grade_constraint.get('max', 'FIVE')
            max_grade_index = self._get_grade_index(max_grade_name)
            random_grade_index = random.randint(0, max_grade_index)
            stats['grade'] = random_grade_index + 1  # Convert to 1-based
        elif isinstance(grade_constraint, str):
            # If it's a string, treat it as max grade
            max_grade_index = self._get_grade_index(grade_constraint)
            random_grade_index = random.randint(0, max_grade_index)
            stats['grade'] = random_grade_index + 1  # Convert to 1-based
        elif isinstance(grade_constraint, int):
            # Direct integer value - use as max grade
            stats['grade'] = random.randint(1, grade_constraint)
        else:
            stats['grade'] = 1
        
        # Generate random rarity
        rarity_constraint = template.get('rarity', 'DIVINE')
        if isinstance(rarity_constraint, dict):
            max_rarity_name = rarity_constraint.get('max', 'DIVINE')
            max_rarity_index = self._get_rarity_index(max_rarity_name)
            # Use weighted selection for rarity (less common = higher)
            stats['rarity'] = self._weighted_rarity_selection(max_rarity_index)
        elif isinstance(rarity_constraint, str):
            # If it's a string, treat it as max rarity
            max_rarity_index = self._get_rarity_index(rarity_constraint)
            stats['rarity'] = self._weighted_rarity_selection(max_rarity_index)
        else:
            stats['rarity'] = 'COMMON'
        
        return stats
    
    def _get_grade_index(self, grade_name: str) -> int:
        """Get the index of a grade in the grades list."""
        try:
            if self.grades and isinstance(self.grades, list):
                return self.grades.index(grade_name.upper())
            return 0
        except (ValueError, AttributeError):
            character_logger.warning(f"Unknown grade: {grade_name}, using 1")
            return 0
    
    def _get_rarity_index(self, rarity_name: str) -> int:
        """Get the index of a rarity in the rarities list."""
        try:
            if self.rarities and isinstance(self.rarities, list):
                return self.rarities.index(rarity_name.upper())
            return 0
        except (ValueError, AttributeError):
            character_logger.warning(f"Unknown rarity: {rarity_name}, using COMMON")
            return 0
    
    def _weighted_rarity_selection(self, max_rarity_index: int) -> str:
        """
        Select a rarity using weighted probabilities.
        Higher rarities are less likely to be selected.
        
        Args:
            max_rarity_index: Maximum rarity index to consider
            
        Returns:
            Selected rarity name
        """
        # Safety check
        if not self.rarities or not isinstance(self.rarities, list):
            return 'COMMON'
            
        # Define weights (higher index = lower probability)
        # Common: 60%, Uncommon: 20%, Rare: 10%, Epic: 5%, etc.
        base_weights = [0.60, 0.20, 0.10, 0.05, 0.03, 0.015, 0.005]
        
        # Only consider rarities up to the max index
        available_rarities = self.rarities[:max_rarity_index + 1]
        weights = base_weights[:max_rarity_index + 1]
        
        # Normalize weights to sum to 1.0
        total_weight = sum(weights)
        if total_weight > 0:
            weights = [w / total_weight for w in weights]
        else:
            weights = [1.0 / len(weights)] * len(weights)
        
        # Select based on weights
        rand_value = random.random()
        cumulative = 0.0
        
        for i, weight in enumerate(weights):
            cumulative += weight
            if rand_value <= cumulative:
                return available_rarities[i]
        
        # Fallback to the lowest rarity
        return available_rarities[0] if available_rarities else 'COMMON'


# Global service instance
character_service = CharacterService()


def create_character_with_random_stats(template_id: str, **overrides):
    """
    Convenience function for creating characters with random stats.
    
    Args:
        template_id: ID of the character template
        **overrides: Optional overrides for specific attributes
        
    Returns:
        Created character or None if creation failed
    """
    return character_service.create_character_with_random_stats(
        template_id, **overrides
    )
