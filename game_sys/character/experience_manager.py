# game_sys/character/experience_manager.py
"""
Experience Manager
=================

Handles experience gain, level-ups, and related calculations.
"""

from typing import Optional
from game_sys.character.actor import Actor
from game_sys.logging import character_logger


class ExperienceManager:
    """Manages experience gain and level-ups for characters."""
    
    def award_experience(self, actor: Actor, amount: float) -> bool:
        """
        Award experience to an actor and handle level-ups.
        
        Args:
            actor: The actor to award experience to
            amount: Amount of experience to award
            
        Returns:
            True if the actor leveled up, False otherwise
        """
        if not actor:
            return False
            
        # Ensure actor has XP attribute
        if not hasattr(actor, 'xp'):
            actor.xp = 0.0
            
        # Log XP gain
        character_logger.info(f"{actor.name} gained {amount} XP")
        
        # Add XP to actor
        actor.xp += amount
        
        # Check for level-up
        leveled_up = False
        while actor.xp >= self._calculate_xp_for_next_level(actor):
            # Perform level-up
            leveled_up = True
            actor.xp -= self._calculate_xp_for_next_level(actor)
            actor.level += 1
            
            # Restore resources on level-up (optional)
            if hasattr(actor, 'max_health'):
                actor.current_health = actor.max_health
            if hasattr(actor, 'max_mana'):
                actor.current_mana = actor.max_mana
            if hasattr(actor, 'max_stamina'):
                actor.current_stamina = actor.max_stamina
                
            character_logger.info(
                f"{actor.name} leveled up to level {actor.level}"
            )
        
        return leveled_up
    
    def _calculate_xp_for_next_level(self, actor: Actor) -> float:
        """
        Calculate the XP needed for the actor's next level.
        
        Args:
            actor: The actor to calculate for
            
        Returns:
            Amount of XP needed to reach the next level
        """
        if hasattr(actor, '_xp_for_next'):
            # Use actor's built-in method if available
            return actor._xp_for_next()
        else:
            # Default formula: 100 * current level
            return 100.0 * actor.level


# Singleton instance
experience_manager = ExperienceManager()
