import json
import pytest
from pathlib import Path

from game_sys.skills.learning import SkillRecord, SkillRegistry
from game_sys.skills.skills import Skill
from game_sys.effects.base import DamageEffect, ApplyStatusEffect


@pytest.fixture(autouse=True)
def clear_registry():
    """
    Ensure SkillRegistry is empty before each test.
    """
    SkillRegistry._registry.clear()


def test_load_from_json_array_and_registry(tmp_path):
    # 1) Prepare a temporary JSON file with two skill entries
    skills_data = [
        {
            "skill_id": "foo_strike",
            "name": "Foo Strike",
            "description": "Deals 5 damage.",
            "mana_cost": 0,
            "cooldown": 0,
            "effects": [
                { "type": "Damage", "value": 5 }
            ],
            "sp_cost": 1,
            "min_level": 1,
            "prereq_skills": []
        },
        {
            "skill_id": "bar_shield",
            "name": "Bar Shield",
            "description": "Grants a shield status.",
            "mana_cost": 0,
            "cooldown": 2,
            "effects": [
                { "type": "ApplyStatus", "status": "Shielded", "duration": 3 }
            ],
            "sp_cost": 2,
            "min_level": 2,
            "prereq_skills": ["foo_strike"]
        }
    ]

    json_file = tmp_path / "skills.json"
    json_file.write_text(json.dumps(skills_data), encoding="utf-8")

    # 2) Load from JSON and register into SkillRegistry
    records = SkillRecord.load_from_json_array(str(json_file))
    # At this point, no automatic registration; we need to manually register
    for rec in records:
        SkillRegistry.register(rec)

    # 3) Verify that both IDs appear in SkillRegistry
    all_ids = SkillRegistry.all_ids()
    assert "foo_strike" in all_ids
    assert "bar_shield" in all_ids
    assert len(all_ids) == 2

    # 4) Retrieve each SkillRecord and check its fields
    rec_foo = SkillRegistry.get("foo_strike")
    assert rec_foo.name == "Foo Strike"
    assert rec_foo.sp_cost == 1
    assert rec_foo.min_level == 1
    assert rec_foo.prereq_skills == set()

    rec_bar = SkillRegistry.get("bar_shield")
    assert rec_bar.name == "Bar Shield"
    assert rec_bar.sp_cost == 2
    assert rec_bar.min_level == 2
    assert rec_bar.prereq_skills == {"foo_strike"}

    # 5) Test that build_skill_instance constructs a Skill with the correct properties
    skill_obj = rec_foo.build_skill_instance()
    assert isinstance(skill_obj, Skill)
    assert skill_obj.id == "foo_strike"
    assert skill_obj.name == "Foo Strike"
    assert skill_obj.mana_cost == 0
    # Effects list should contain a DamageEffect with amount=5
    assert any(isinstance(e, DamageEffect) and e.amount == 5 for e in skill_obj.effects)

    skill_obj2 = rec_bar.build_skill_instance()
    assert isinstance(skill_obj2, Skill)
    assert skill_obj2.id == "bar_shield"
    # Effects list should contain an ApplyStatusEffect with status="Shielded", duration=3
    assert any(isinstance(e, ApplyStatusEffect) and e.status == "Shielded" and e.duration == 3
               for e in skill_obj2.effects)


def test_duplicate_registration_raises():
    # 1) Register a simple dummy record
    rec1 = SkillRecord(
        skill_id="dup_skill",
        name="Duplicate Skill",
        description="Test skill",
        mana_cost=0,
        cooldown=0,
        effects=[],
        sp_cost=1,
        min_level=1,
        prereq_skills=[]
    )
    SkillRegistry.register(rec1)

    # 2) Attempting to register another record with the same ID should raise ValueError
    rec2 = SkillRecord(
        skill_id="dup_skill",
        name="Duplicate Skill V2",
        description="Another test",
        mana_cost=0,
        cooldown=0,
        effects=[],
        sp_cost=1,
        min_level=1,
        prereq_skills=[]
    )
    with pytest.raises(ValueError) as excinfo:
        SkillRegistry.register(rec2)
    assert "already registered" in str(excinfo.value)
