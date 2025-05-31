# game_sys/items/loader.py

import json
from pathlib import Path
from typing import Dict, Any

DATA_PATH = Path(__file__).parent / "data" / "items.json"

def load_templates() -> Dict[str, Dict[str, Any]]:
    """
    Load raw JSON entries into a dict: item_id -> template dict.
    """
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        raw = json.load(f)
    return {entry["id"]: entry for entry in raw}
