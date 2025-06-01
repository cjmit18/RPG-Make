import pytest

from game_sys.skills.learning import SkillRegistry, SkillRecord, LearningSystem
from game_sys.effects.base import DamageEffect
from game_sys.character.character_creation import Player, Enemy


@pytest.fixture(autouse=True)
def clear_registry():
    """
    Clear the SkillRegistry before each test to avoid cross-test pollution.
    """
    SkillRegistry._registry.clear()


def test_learning_system_basic_flow():
    # 1) Register a simple damage skill
    rec = SkillRecord(
        skill_id="hit",
        name="Hit",
        description="Deals 10 damage.",
        mana_cost=0,
        cooldown=0,
        effects=[DamageEffect(amount=10)],
        sp_cost=1,
        min_level=1,
        prereq_skills=[]
    )
    SkillRegistry.register(rec)

    # 2) Create a Player, award 1 SP
    player = Player(name="Tester", level=1, experience=0)
    assert player.learning.unspent_sp() == 0
    player.learning.add_sp(1)
    assert player.learning.unspent_sp() == 1

    # 3) "hit" should be available to learn
    avail = player.learning.available_to_learn()
    assert "hit" in avail

    # 4) Learn "hit", SP should go to 0
    player.learning.learn("hit")
    assert "hit" in player.learning.get_known_skills()
    assert player.learning.unspent_sp() == 0

    # 5) Retrieve the Skill and cast on an Enemy
    skill_obj = player.learning.get_skill_object("hit")
    enemy = Enemy(name="Dummy", level=1, experience=0)
    enemy.current_health = 30
    skill_obj.cast(player, enemy)
    assert enemy.current_health == 20  # 30 - 10 = 20


def test_prerequisite_and_sp_logic():
    # 1) Register base and advanced skills
    base = SkillRecord(
        skill_id="base",
        name="BaseSkill",
        description="Base skill, no prereq.",
        mana_cost=0,
        cooldown=0,
        effects=[],
        sp_cost=1,
        min_level=1,
        prereq_skills=[]
    )
    adv = SkillRecord(
        skill_id="adv",
        name="AdvSkill",
        description="Requires base.",
        mana_cost=0,
        cooldown=0,
        effects=[],
        sp_cost=1,
        min_level=1,
        prereq_skills=["base"]
    )
    SkillRegistry.register(base)
    SkillRegistry.register(adv)

    # 2) Create Player with 1 SP
    player = Player(name="Rogue", level=1, experience=0)
    player.learning.add_sp(1)

    # 3) "adv" should NOT be available (missing prereq)
    assert "adv" not in player.learning.available_to_learn()

    # 4) Learn "base"
    player.learning.learn("base")
    assert "base" in player.learning.get_known_skills()
    assert player.learning.unspent_sp() == 0

    # 5) Award 1 more SP
    player.learning.add_sp(1)
    assert player.learning.unspent_sp() == 1

    # 6) Now "adv" should be available
    assert "adv" in player.learning.available_to_learn()

    # 7) Learn "adv"
    player.learning.learn("adv")
    assert "adv" in player.learning.get_known_skills()
    assert player.learning.unspent_sp() == 0
