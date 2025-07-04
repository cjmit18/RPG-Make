# game_sys/skills/passive_factory.py

import json
from pathlib import Path
from typing import Dict
from game_sys.skills.passive import Passive


class PassiveFactory:
    _passives: Dict[str, Passive] = {}

    @classmethod
    def load(cls):
        # Try the 'data' subfolder first
        candidates = [
            Path(__file__).parent / "data" / "passives.json",
            Path(__file__).parent / "passives.json"
        ]
        data = {}
        for p in candidates:
            if p.exists():
                data = json.loads(p.read_text()).get("passives", {})
                break
        else:
            pass

        for pid, defn in data.items():
            cls._passives[pid] = Passive(
                pid         = pid,
                name        = defn.get("name", pid),
                description = defn.get("description", ""),
                triggers    = defn.get("triggers", [])
            )

    @classmethod
    def get(cls, pid: str) -> Passive:
        if not cls._passives:
            cls.load()
        passive = cls._passives.get(pid)
        if passive is None:
            raise KeyError(f"Passive '{pid}' not found in registry")
        return passive
