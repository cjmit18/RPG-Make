# game_sys/skills/learning_system.py

from typing import Any, Dict, List, Optional
from game_sys.hooks.hooks_setup import emit, emit_async

# Events you can hook into
ON_SKILL_LEARNED  = 'skill_learned'
ON_SKILL_UPGRADED = 'skill_upgraded'

class LearningSystem:
    """
    Tracks which skills an actor has learned, their levels,
    and provides methods to learn or upgrade them.
    """

    def __init__(self, actor: Any):
        self.actor = actor
        # skill_id -> current level
        self.learned_skills: Dict[str, int] = {}

    def learn(self, skill_id: str) -> bool:
        """
        Learn a new skill if not already known.
        Returns True if successfully learned.
        """
        if skill_id in self.learned_skills:
            return False
        self.learned_skills[skill_id] = 1
        emit(ON_SKILL_LEARNED, actor=self.actor, skill_id=skill_id, level=1)
        # Optionally: await emit_async(ON_SKILL_LEARNED, ...)
        return True

    def upgrade(self, skill_id: str) -> bool:
        """
        Increase the level of an existing skill.
        Returns True if successfully upgraded.
        """
        if skill_id not in self.learned_skills:
            return False
        new_level = self.learned_skills[skill_id] + 1
        self.learned_skills[skill_id] = new_level
        emit(ON_SKILL_UPGRADED, actor=self.actor, skill_id=skill_id, level=new_level)
        # Optionally: await emit_async(ON_SKILL_UPGRADED, ...)
        return True

    def get_skill_level(self, skill_id: str) -> Optional[int]:
        """
        Return the current level of the specified skill, or None if unlearned.
        """
        return self.learned_skills.get(skill_id)

    def list_skills(self) -> List[str]:
        """
        Return a list of all skill IDs this actor has learned.
        """
        return list(self.learned_skills.keys())
    
    def can_learn_skill(self, skill_id: str) -> bool:
        """
        Check if the actor can learn a new skill based on level and stats.
        """
        # Check if already learned
        if skill_id in self.learned_skills:
            return False
            
        # Check level and stat requirements
        try:
            from game_sys.character.leveling_manager import leveling_manager
            return leveling_manager.check_skill_requirements(self.actor, skill_id)
        except ImportError:
            # If leveling manager not available, allow all skills
            return True
    
    def get_available_skills(self) -> List[str]:
        """
        Get all skills that can be learned at the current level.
        """
        try:
            from game_sys.character.leveling_manager import leveling_manager
            available = leveling_manager.get_available_skills_for_level(self.actor)
            
            # Filter out already learned skills
            return [skill_id for skill_id in available 
                   if skill_id not in self.learned_skills]
        except ImportError:
            # If leveling manager not available, return default list
            default_skills = ['cleave', 'pierce', 'whirlwind', 'berserker_rage']
            return [skill_id for skill_id in default_skills 
                   if skill_id not in self.learned_skills]
    
    def learn_if_allowed(self, skill_id: str) -> bool:
        """
        Learn a skill only if requirements are met.
        Returns True if successfully learned.
        """
        if self.can_learn_skill(skill_id):
            return self.learn(skill_id)
        return False
