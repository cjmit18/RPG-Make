# game_sys/enchantments/loader.py

import json
from pathlib import Path
from typing import Dict, Any

def load_templates() -> Dict[str, Any]:
    """
    Load every .json file in game_sys/enchantments/data/ and return a dict
    mapping each entry's 'id' to its JSON object.
    """
    templates: Dict[str, Any] = {}
    data_dir = Path(__file__).parent / "data"
    for json_file in data_dir.glob("*.json"):
        with json_file.open(encoding="utf-8") as f:
            entries = json.load(f)
            for entry in entries:
                templates[entry["id"]] = entry
    return templates
