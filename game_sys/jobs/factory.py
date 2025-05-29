import copy
from typing import Any, Dict
import random

from game_sys.jobs.loader import load_job_templates
from game_sys.items.factory import create_item
from game_sys.jobs.base import Job

# load once
_TEMPLATES: Dict[str, Dict[str, Any]] = load_job_templates()

def create_job(job_id: str, level: int, rng: Any = random) -> Job:
    """
    Instantiate a generic Job from a template, scaling base_stats by level and
    creating starting items via the item factory.
    """
    template = _TEMPLATES.get(job_id)
    if template is None:
        raise KeyError(f"No job template for id={job_id!r}")

    # deep copy to avoid mutating the template
    tpl = copy.deepcopy(template)
    name = tpl.get('name')
    description = tpl.get('description')
    raw_stats = tpl.get('base_stats', {})
    # scale stats
    stats_mods = {stat: val * level for stat, val in raw_stats.items()}

    # instantiate items
    items = [create_item(item_id, rng) for item_id in tpl.get('starting_items', [])]

    # create a generic Job instance
    job = Job(level=level)
    job.name = name
    job.description = lambda: description
    job.stats_mods = stats_mods
    job.starting_items = items
    return job

def list_job_ids() -> list[str]:
    return list(_TEMPLATES.keys())
