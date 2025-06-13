# game_sys/combat/drop_tables.py

import json
from pathlib import Path
from typing import Dict, List, Any
from game_sys.core.hooks import hook_dispatcher
# 1) Locate JSON file under data/drop_tables.json
_DROP_TABLES_PATH = Path(__file__).parent / "data" / "drop_tables.json"

# 2) Load at import time
try:
    with open(_DROP_TABLES_PATH, "r", encoding="utf-8") as f:
        DROP_TABLES: Dict[str, List[Dict[str, Any]]] = json.load(f)
except FileNotFoundError:
    DROP_TABLES = {}
hook_dispatcher.fire("data.loaded", module=__name__, data=DROP_TABLES)
