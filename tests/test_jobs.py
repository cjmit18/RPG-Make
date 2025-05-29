import pytest
from game_sys.jobs.factory import create_job
def test_job_stats_and_items():
    knight = create_job("knight", level=3)
    # base_stats scaled by level
    assert knight.stats_mods["attack"] == 5 * 3
    assert knight.stats_mods["defense"] == 7 * 3
    # starting_items are actual Item instances
    assert len(knight.starting_items) >= 1
    for itm in knight.starting_items:
        assert hasattr(itm, "id")
        assert hasattr(itm, "name")

def test_different_jobs_have_different_mods():
    k = create_job("knight", level=2)
    m = create_job("mage", level=2)
    assert k.stats_mods["defense"] > m.stats_mods["defense"]
    assert m.stats_mods["mana"] >= k.stats_mods.get("mana", 0)
