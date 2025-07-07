# game_sys/magic/spell_manager.py

from typing import List, Dict, Any


class SpellManager:
    """
    Manager for handling spell operations between UI and the spell system.
    Provides a centralized interface for spell-related functions.
    """

    def __init__(self):
        """Initialize the spell manager."""
        pass

    def initialize_actor_spells(self, actor) -> None:
        """
        Initialize spell system for an actor if needed.
        
        Args:
            actor: The actor to initialize spells for
        """
        if (not hasattr(actor, 'spell_system') or 
                actor.spell_system is None):
            from game_sys.magic.spell_system import SpellSystem
            actor.spell_system = SpellSystem(actor)
        
        # Ensure known_spells list exists
        if not hasattr(actor, 'known_spells'):
            actor.known_spells = []
            
    def get_known_spells(self, actor) -> List[str]:
        """
        Get the spells known by an actor.
        
        Args:
            actor: The actor to get spells for
            
        Returns:
            List[str]: List of spell IDs
        """
        self.initialize_actor_spells(actor)
        return actor.spell_system.get_known_spells()
    
    def get_unlearned_spells(self, actor) -> List[str]:
        """
        Get spells not yet learned by an actor.
        
        Args:
            actor: The actor to get unlearned spells for
            
        Returns:
            List[str]: List of unlearned spell IDs
        """
        self.initialize_actor_spells(actor)
        return actor.spell_system.get_unlearned_spells()
    
    def learn_spell(self, actor, spell_id: str) -> bool:
        """
        Have the actor learn a new spell.
        
        Args:
            actor: The actor learning the spell
            spell_id: The ID of the spell to learn
            
        Returns:
            bool: True if learned successfully, False otherwise
        """
        self.initialize_actor_spells(actor)
        return actor.spell_system.learn_spell(spell_id)
    
    def cast_spell(self, actor, spell_id: str, target=None) -> bool:
        """
        Cast a spell on a target.
        
        Args:
            actor: The actor casting the spell
            spell_id: The ID of the spell to cast
            target: The target of the spell (default: None for self)
            
        Returns:
            bool: True if cast successfully, False otherwise
        """
        self.initialize_actor_spells(actor)
        return actor.spell_system.cast_spell(spell_id, target)
    
    def get_spell_info(self, actor, spell_id: str) -> Dict:
        """
        Get information about a spell.
        
        Args:
            actor: The actor requesting spell info
            spell_id: The ID of the spell
            
        Returns:
            Dict: Spell information
        """
        self.initialize_actor_spells(actor)
        return actor.spell_system.get_spell_info(spell_id)


# Create a global instance for convenient access
spell_manager = SpellManager()
