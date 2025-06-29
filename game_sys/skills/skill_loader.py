# game_sys/skills/skill_loader.py

from game_sys.skills.factory import SkillFactory


def load_skill(skill_id: str):
    """
    Public API to get a Skill instance by ID.
    """
    return SkillFactory.create(skill_id)
