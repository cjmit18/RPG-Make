# game_sys/items/loader.py

import json
from pathlib import Path
from typing import Any, Dict, Union

def load_templates() -> Dict[str, Any]:
    """
    Load item definitions from 'items.json'. Handle these cases:
      - File missing            → return {}
      - File empty/whitespace   → return {}
      - File contains invalid JSON → print warning, return {}
      - File contains a JSON object (dict) → return it unchanged
      - File contains a JSON array (list) → convert list of entries into dict by 'id'
    """
    templates_path = Path(__file__).parent / "data" / "items.json"
    try:
        raw_text = templates_path.read_text(encoding="utf-8")
    except FileNotFoundError:
        # No items.json at all: return empty dict
        return {}

    if not raw_text.strip():
        # File exists but is empty or only whitespace: return empty dict
        return {}

    try:
        parsed: Union[Dict[str, Any], list] = json.loads(raw_text)
    except json.JSONDecodeError as e:
        # Malformed JSON: warn and return empty dict
        print(f"[Warning] Could not parse {templates_path}: {e}")
        return {}

    # If parsed is a dict, return it directly
    if isinstance(parsed, dict):
        return parsed

    # If parsed is a list, convert to a dict keyed by each entry’s "id"
    if isinstance(parsed, list):
        result: Dict[str, Any] = {}
        for entry in parsed:
            if not isinstance(entry, dict):
                continue
            item_id = entry.get("id")
            if not item_id:
                continue
            result[item_id] = entry
        return result

    # Otherwise, the JSON is something unexpected (e.g. a number/string); warn and return {}
    print(f"[Warning] Expected top-level JSON object or array in {templates_path}, got {type(parsed)}")
    return {}
