# game_sys/skills/learning_system.py

from typing import Any, Dict, List, Optional
from game_sys.hooks.hooks_setup import emit

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
        return True

    def get_skill_level(self, skill_id: str) -> Optional[int]:
        """
        Return the current level of the specified skill, or None if unlearned.
        """
        return self.learned_skills.get(skill_id)

    def list_skills(self) -> List[str]:
        """
        Return a list of all learned skill IDs.
        """
        return list(self.learned_skills.keys())
