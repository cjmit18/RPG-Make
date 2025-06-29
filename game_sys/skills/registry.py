# game_sys/skills/registry.py

from typing import Type, Dict
from game_sys.skills.base import Skill


class SkillRegistry:
    """
    Maps skill_id to Skill subclasses or prototypes.
    """
    _registry: Dict[str, Type[Skill]] = {}

    @classmethod
    def register(cls, skill_id: str, skill_cls: Type[Skill]):
        cls._registry[skill_id] = skill_cls

    @classmethod
    def get(cls, skill_id: str) -> Type[Skill]:
        return cls._registry.get(skill_id, Skill)
