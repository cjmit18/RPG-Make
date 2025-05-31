"""Drop tables for combat encounters.
This module handles the loading and parsing of drop tables from a JSON file,"""
import json
from pathlib import Path
from typing import Dict, List, Tuple
from game_sys.items.item_base import Item
from game_sys.items.factory import create_item
# 1) Locate the JSON file
_DROP_TABLES_PATH = (
    Path(__file__).parent / "data" / "drop_tables.json"
)

# 2) Load raw JSON once at import time
try:
    with open(_DROP_TABLES_PATH, "r", encoding="utf-8") as f:
        _RAW_DROP_TABLES: Dict[str, List[Dict]] = json.load(f)
except FileNotFoundError:
    _RAW_DROP_TABLES = {}

# 3) Convert raw JSON into a Python‐friendly structure:
#    Dict[job_id, List[(factory_callable, chance, min, max)]]
DROP_TABLES: Dict[str, List[Tuple[callable, float, int, int]]] = {}

for job_id, entries in _RAW_DROP_TABLES.items():
    parsed_list = []
    for entry in entries:
        template_id = entry["template_id"]
        chance = float(entry["chance"])
        min_qty = int(entry["min_qty"])
        max_qty = int(entry["max_qty"])
        # Wrap a lambda around Item.from_template_id so each call makes a fresh Item
        factory = lambda tid=template_id: create_item(tid)
        parsed_list.append((factory, chance, min_qty, max_qty))
    DROP_TABLES[job_id] = parsed_list
