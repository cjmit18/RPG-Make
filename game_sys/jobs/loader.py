import json
from pathlib import Path
from typing import Dict, Any

DATA_PATH = Path(__file__).parent / "data" / "jobs.json"


def load_job_templates() -> Dict[str, Dict[str, Any]]:
    """
    Load raw JSON entries into a dict of job_id -> template dict.
    """
    with open(DATA_PATH, 'r', encoding='utf-8') as f:
        raw = json.load(f)
    from game_sys.hooks.hooks import hook_dispatcher
    hook_dispatcher.fire("data.loaded", module=__name__, data=raw)
    return {tpl['id']: tpl for tpl in raw}
