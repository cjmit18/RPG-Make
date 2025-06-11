# File: game_sys/jobs/factory.py

import json
import random
import copy
from pathlib import Path
from typing import Any, Dict, List, Optional

from game_sys.items.factory import create_item
from game_sys.core.rarity import Rarity
from game_sys.core.scaler import scale_stat, _GRADE_STATS_MULTIPLIER as _GRADE_MODIFIERS
from game_sys.jobs.base import Job

def load_templates() -> Dict[str, Any]:
    """
    Load all job templates from JSON files under game_sys/jobs/data/.
    Returns a dict mapping job_id to its template.
    """
    templates: Dict[str, Any] = {}
    data_dir = Path(__file__).parent / "data"
    for json_file in data_dir.glob("*.json"):
        with json_file.open(encoding="utf-8") as f:
            entries = json.load(f)
            for entry in entries:
                jid = (
                    entry.get("id")
                    or entry.get("job_id")
                    or entry.get("name")
                )
                templates[jid] = entry
    return templates


_TEMPLATES = load_templates()


def list_all_ids() -> List[str]:
    """Return all defined job IDs."""
    return list(_TEMPLATES.keys())


def create_job(
    job_id: str,
    level: int,
    grade: int = 1,
    rarity: Rarity = Rarity.COMMON,
    seed: Optional[int] = None,
    rng: Optional[random.Random] = None
) -> Job:
    """
    Instantiate a Job with scaled base stats and starting items.
    - Rolls any min/max ranges in base_stats via RNG.
    - Scales via scale_stat and applies grade modifiers.
    """
    # Prepare RNG
    if rng is None:
        rng = random.Random(seed) if seed is not None else random.Random()

    # Fetch and copy template
    template = _TEMPLATES.get(job_id)
    if template is None:
        raise KeyError(f"No job template for id={job_id!r}")
    templ = copy.deepcopy(template)

    # Scale base stats
    raw_stats = templ.get("base_stats", {})
    scaled_stats: Dict[str, int] = {}
    for stat_name, spec in raw_stats.items():
        # Roll if spec is a dict range
        if isinstance(spec, dict):
            lo = int(spec.get("min", 0))
            hi = int(spec.get("max", lo))
            rolled = rng.randint(lo, hi) if hi >= lo else lo
        else:
            rolled = int(spec)
        # Scale and apply grade multiplier
        val = scale_stat(rolled, level, grade=grade, rarity=rarity)
        val = int(val * _GRADE_MODIFIERS.get(grade, 1.0))
        scaled_stats[stat_name] = val

    # Instantiate starting items
    items: List[Any] = []
    for item_id in templ.get("starting_items", []):
        try:
            items.append(create_item(item_id, seed=seed,
                                     rng=rng,
                                     level=level,
                                     grade=1,
                                     rarity=rarity
                                     ))
        # If create_item fails, it will raise an exception;
        # we can handle it or skip
        except KeyError:
            continue

    # Finally, return a Job instance (adjust signature if needed by your Job
    # class). Here we pass level and scaled_stats; your Job.__init__ may vary.
    return Job(
            level=level, base_stats=scaled_stats,
            starting_items=items,
            job_id=job_id
            )
