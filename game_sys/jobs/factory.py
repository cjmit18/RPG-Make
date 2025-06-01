# game_sys/jobs/factory.py

"""
Job factory that reads all job definitions from a JSON file under
`game_sys/jobs/data/jobs.json`. Supports both object and array formats.
Each template must include:
  - "base_stats": a dict mapping stat names → base value at level 1.
       (Valid keys: "health", "attack", "defense", "speed", "mana", "stamina", "intellect")
  - "starting_items": a list of item_id strings (optional)
  - "id" (or "job_id" or "name"): the job’s string ID
"""

import json
import random
from pathlib import Path
from typing import Any, Dict, List, Optional

from game_sys.items.factory import create_item

# --------------------------------------------------------------------------
# 1) Load raw JSON; handle both "dict" and "list" formats
# --------------------------------------------------------------------------
_JOBS_PATH = Path(__file__).parent / "data" / "jobs.json"
try:
    _raw_data = json.loads(_JOBS_PATH.read_text(encoding="utf-8"))
    if isinstance(_raw_data, list):
        _RAW_JOB_TEMPLATES: Dict[str, Dict[str, Any]] = {}
        for entry in _raw_data:
            key = entry.get("id") or entry.get("job_id") or entry.get("name")
            if isinstance(key, str) and entry:
                _RAW_JOB_TEMPLATES[key] = entry
    elif isinstance(_raw_data, dict):
        _RAW_JOB_TEMPLATES = _raw_data  # type: ignore[var-annotated]
    else:
        _RAW_JOB_TEMPLATES = {}
except FileNotFoundError:
    _RAW_JOB_TEMPLATES: Dict[str, Dict[str, Any]] = {}


class Job:
    """
    Minimal Job object holding:
      - stats_mods: Dict[str, int]   (final rolled stats at this level)
      - starting_items: List[Any]    (instantiated item objects)
      - name: str                    (job_id)
    """

    def __init__(
        self,
        stats_mods: Dict[str, int],
        starting_items: List[Any],
        name: str,
    ) -> None:
        self.stats_mods: Dict[str, int] = stats_mods
        self.starting_items: List[Any] = starting_items
        self.name: str = name


def list_job_ids() -> List[str]:
    """Return a list of all valid job IDs (keys from JSON)."""
    return list(_RAW_JOB_TEMPLATES.keys())


def roll_stat_triangular(
    base: int,
    level: int,
    rng: random.Random,
    low_pct: float = 0.5,
    high_pct: float = 1.0,
    mode_pct: float = 0.8,
) -> int:
    """
    Triangular‐distribution roll between [base * level * low_pct, base * level * high_pct],
    peaking (most likely) at base * level * mode_pct. Returns an int.

    Args:
        base: Base stat value at level 1.
        level: Character level.
        rng: A random.Random instance for reproducibility.
        low_pct: Minimum percentage multiplier (default 0.5).
        high_pct: Maximum percentage multiplier (default 1.0).
        mode_pct: Mode percentage multiplier (default 0.8).

    Returns:
        Rolled stat as an integer.
    """
    low = int(base * level * low_pct)
    high = int(base * level * high_pct)
    mode = int(base * level * mode_pct)
    return int(round(rng.triangular(low, high, mode)))


def create_job(
    job_id: str,
    level: int,
    rng: Optional[random.Random] = None,
) -> Job:
    """
    Instantiate a Job for `job_id` at the given `level`.

      - Reads raw_stats from JSON under "base_stats" (missing keys → treated as 0).
      - For each of the seven stats, does a triangular roll → final stat_mods[stat].
      - Instantiates each starting item via create_item(item_id).

    Raises:
        KeyError: If `job_id` not found in JSON.
    """
    rng = rng or random.Random()
    template = _RAW_JOB_TEMPLATES.get(job_id)
    if template is None:
        available = ", ".join(list_job_ids())
        raise KeyError(f"No job template for '{job_id}'. Available: {available}")

    # ------------------------------------------------------------------------
    # 2) Read "base_stats" from JSON, default‐to‐0 for any missing stat
    # ------------------------------------------------------------------------
    raw_stats = template.get("base_stats", {})
    allowed_keys = ["health", "attack", "defense", "speed", "mana", "stamina", "intellect"]
    stats_mods: Dict[str, int] = {}
    for stat_name in allowed_keys:
        base_val = int(raw_stats.get(stat_name, 0))
        stats_mods[stat_name] = roll_stat_triangular(base_val, level, rng)

    # ------------------------------------------------------------------------
    # 3) Instantiate starting_items (if any)
    # ------------------------------------------------------------------------
    starting_items: List[Any] = []
    for item_id in template.get("starting_items", []):
        if not isinstance(item_id, str):
            continue
        try:
            item = create_item(item_id)
            starting_items.append(item)
        except KeyError:
            # Skip unknown item IDs silently
            continue

    return Job(stats_mods, starting_items, job_id)
