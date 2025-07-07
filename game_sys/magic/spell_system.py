# game_sys/magic/spell_system.py

from typing import Dict, List
from game_sys.logging import character_logger
from game_sys.config.config_manager import ConfigManager

class SpellSystem:
    """
    System for managing spells for a character.
    Allows learning and casting spells.
    """

    def __init__(self, actor):
        self.actor = actor
        # Only initialize known_spells if actor is not None
        if actor is not None and not hasattr(actor, 'known_spells'):
            actor.known_spells = []
        self.config_manager = ConfigManager()
        self._load_spells()

    def _load_spells(self):
        """Load available spells from config."""
        self.available_spells = {}
        spells = self.config_manager.get_section('spells', {})
        for spell_id, spell_data in spells.items():
            self.available_spells[spell_id] = spell_data

    def learn_spell(self, spell_id: str) -> bool:
        """
        Learn a new spell if requirements are met.
        
        Args:
            spell_id: The ID of the spell to learn
            
        Returns:
            bool: True if learned, False otherwise
        """
        # Check if already learned
        if spell_id in self.actor.known_spells:
            character_logger.info(
                f"{self.actor.name} already knows spell: {spell_id}"
            )
            return False
            
        # Check requirements (using leveling manager if available)
        if hasattr(self.actor, 'leveling_manager'):
            if not self.actor.leveling_manager.check_spell_requirements(
                self.actor, spell_id
            ):
                character_logger.info(
                    f"{self.actor.name} doesn't meet requirements for spell: {spell_id}"
                )
                return False
        
        # Learn the spell
        self.actor.known_spells.append(spell_id)
        character_logger.info(f"{self.actor.name} learned spell: {spell_id}")
        return True
    
    def get_known_spells(self) -> List[str]:
        """Get list of known spell IDs."""
        return self.actor.known_spells
    
    def get_available_spells(self) -> List[str]:
        """Get list of all spells that can be learned (including already known)."""
        return list(self.available_spells.keys())
    
    def get_unlearned_spells(self) -> List[str]:
        """Get list of spells that can be learned but haven't been yet."""
        return [
            s_id for s_id in self.available_spells 
            if s_id not in self.actor.known_spells
        ]
    
    def cast_spell(self, spell_id: str, target=None) -> bool:
        """
        Cast a known spell on a target.
        
        Args:
            spell_id: The ID of the spell to cast
            target: The target of the spell (default: None)
            
        Returns:
            bool: True if cast successfully, False otherwise
        """
        if spell_id not in self.actor.known_spells:
            character_logger.info(
                f"{self.actor.name} doesn't know spell: {spell_id}"
            )
            return False
            
        # Get spell data
        spell_data = self.available_spells.get(spell_id)
        if not spell_data:
            character_logger.error(f"No data for spell: {spell_id}")
            return False
            
        # Check mana cost
        mana_cost = spell_data.get('mana_cost', 0)
        if hasattr(self.actor, 'current_mana'):
            if self.actor.current_mana < mana_cost:
                character_logger.info(
                    f"{self.actor.name} doesn't have enough mana to cast {spell_id}"
                )
                return False
            self.actor.current_mana -= mana_cost
        
        # TODO: Implement actual spell effects
        character_logger.info(
            f"{self.actor.name} cast {spell_id} on {target.name if target else 'self'}"
        )
        return True
    
    def get_spell_info(self, spell_id: str) -> Dict:
        """Get information about a spell."""
        return self.available_spells.get(spell_id, {})


# Create a global instance for convenience
spell_system = SpellSystem(None)
