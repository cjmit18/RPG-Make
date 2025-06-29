# game_sys/skills/skill_loader.py
"""
Module: game_sys.skills.skill_loader

Loads skill definitions and returns a minimal Skill stub.
Stubbed to return the raw JSON dict or an empty dict.
"""

import json
from pathlib import Path
from typing import Any, Dict


def load_skill(skill_id: str) -> Dict[str, Any]:
    """
    Attempt to load <skill_id>.json from the same folder;
    returns the parsed dict or an empty dict if missing.
    """
    path = Path(__file__).parent / f"{skill_id}.json"
    if path.exists():
        try:
            return json.loads(path.read_text())
        except Exception:
            pass
    return {}
