# game_sys/magic/learning_system.py

from typing import Any, Dict, List, Optional
from game_sys.hooks.hooks_setup import emit

# Events you can hook into
ON_SPELL_LEARNED  = 'spell_learned'
ON_SPELL_UPGRADED = 'spell_upgraded'

class MagicLearningSystem:
    """
    Tracks which spells an actor has learned, their levels,
    and provides methods to learn or upgrade them.
    """

    def __init__(self, actor: Any):
        self.actor = actor
        # spell_id -> current level
        self.learned_spells: Dict[str, int] = {}

    def learn(self, spell_id: str) -> bool:
        """
        Learn a new spell if not already known.
        Returns True if successfully learned.
        """
        if spell_id in self.learned_spells:
            return False
        self.learned_spells[spell_id] = 1
        emit(ON_SPELL_LEARNED, actor=self.actor, spell_id=spell_id, level=1)
        return True

    def upgrade(self, spell_id: str) -> bool:
        """
        Increase the level of an existing spell.
        Returns True if successfully upgraded.
        """
        if spell_id not in self.learned_spells:
            return False
        new_level = self.learned_spells[spell_id] + 1
        self.learned_spells[spell_id] = new_level
        emit(ON_SPELL_UPGRADED, actor=self.actor, spell_id=spell_id, level=new_level)
        return True

    def get_spell_level(self, spell_id: str) -> Optional[int]:
        """
        Return the current level of the specified spell, or None if unlearned.
        """
        return self.learned_spells.get(spell_id)

    def list_spells(self) -> List[str]:
        """
        Return a list of all spell IDs this actor has learned.
        """
        return list(self.learned_spells.keys())
    
    def can_learn_spell(self, spell_id: str) -> bool:
        """
        Check if the actor can learn a new spell based on level and stats.
        """
        # Check if already learned
        if spell_id in self.learned_spells:
            return False
            
        # Check level and stat requirements
        try:
            from game_sys.character.leveling_manager import leveling_manager
            return leveling_manager.check_spell_requirements(self.actor, spell_id)
        except ImportError:
            # If leveling manager not available, allow all spells
            return True
    
    def get_available_spells(self) -> List[str]:
        """
        Get all spells that can be learned at the current level.
        """
        try:
            from game_sys.character.leveling_manager import leveling_manager
            available = leveling_manager.get_available_spells_for_level(self.actor)
            
            # Filter out already learned spells
            return [spell_id for spell_id in available 
                   if spell_id not in self.learned_spells]
        except ImportError:
            # If leveling manager not available, return default list
            default_spells = ['fireball', 'ice_shard', 'lightning_bolt', 'heal']
            return [spell_id for spell_id in default_spells 
                   if spell_id not in self.learned_spells]
    
    def learn_if_allowed(self, spell_id: str) -> bool:
        """
        Learn a spell only if requirements are met.
        Returns True if successfully learned.
        """
        if self.can_learn_spell(spell_id):
            return self.learn(spell_id)
        return False
