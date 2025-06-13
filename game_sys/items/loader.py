# game_sys/items/loader.py

import json
from pathlib import Path
from typing import Any, Dict, List, Union


def load_templates() -> List[Dict[str, Any]]:
    """
    Load item templates from 'items.json' and return as a list of dicts.
    Handles:
      - Missing file or empty content → empty list
      - Invalid JSON → empty list
      - JSON array → return it directly
      - JSON object → return list(parsed.values())
    """
    templates_path = Path(__file__).parent / "data" / "items.json"

    try:
        raw = templates_path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return []

    if not raw.strip():
        return []

    try:
        parsed: Union[Dict[str, Any], List[Any]] = json.loads(raw)
    except json.JSONDecodeError:
        return []
    
    from game_sys.core.hooks import hook_dispatcher
    hook_dispatcher.fire("data.loaded", module=__name__, data=parsed)

    if isinstance(parsed, list):
        # Only keep dict entries
        return [e for e in parsed if isinstance(e, dict)]

    if isinstance(parsed, dict):
        # Convert dict-of-templates into a list
        items: List[Dict[str, Any]] = []
        for entry in parsed.values():
            if isinstance(entry, dict):
                items.append(entry)
        return items
    
    # Unexpected top-level type
    return []
