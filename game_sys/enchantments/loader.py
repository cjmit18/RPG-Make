

# game_sys/enchantments/loader.py

import json
from pathlib import Path
from typing import Dict, Any
from logs.logs import get_logger

log = get_logger(__name__)


def load_templates() -> Dict[str, Any]:
    """
    Load every JSON file under this module's data/ folder into a template dict.
    """
    templates: Dict[str, Any] = {}
    data_dir = Path(__file__).parent / "data"
    for json_file in data_dir.glob("*.json"):
        try:
            raw = json.loads(json_file.read_text(encoding="utf-8"))
            for entry in raw:
                templates[entry.get("id")] = entry
        except Exception as e:
            log.warning(f"Could not load {json_file}: {e}")
    return templates
