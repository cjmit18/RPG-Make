import pytest
from game_sys.core.actor import Actor
from game_sys.jobs.knight import Knight

def test_take_damage_clamps_and_reports_defeat(capfd):
    hero = Actor("Hero", level=1)
    # set a known max so current_health is predictable
    hero.current_health = 10
    hero.take_damage(4)
    assert hero.current_health == 6

    # killing blow
    hero.take_damage(20)
    captured = capfd.readouterr()
    assert hero.current_health == 0
    assert "Hero has been defeated!" in captured.out

def test_assign_job_applies_stats_and_items():
    hero = Actor("Alice", level=2)
    # initially has Base job (no mods)
    base_health = hero.stats.effective().get("health")
    # now assign Knight
    hero.assign_job(Knight)
    eff = hero.stats.effective()
    # Knight base_health = 10 * lvl
    assert eff["health"] == 10 * hero.levels.lvl
    # inventory should contain starting items, and they should be auto-equipped
    from game_sys.items.item_base import Equipable
    for item in hero.job.starting_items:
        # equip slot now holds that item
        assert hero.inventory.equipment[item.slot].id == item.id
        # stats modifiers include the item bonus
        assert isinstance(item, Equipable)
        for stat, bonus in item.bonuses.items():
            # Stats.effective() already includes these bonuses
            assert eff[stat] >= hero.job.stats_mods.get(stat, 0) + bonus
