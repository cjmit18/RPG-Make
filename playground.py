# playground.py

from logs.logs import setup_logging, get_logger
from game_sys.character.character_creation import create_character
from game_sys.skills.learning import SkillRegistry
from game_sys.items.factory import create_item
from game_sys.combat.encounter import Encounter, CombatEngine
from game_sys.core.damage_types import DamageType
from game_sys.enchantments.factory import create_enchantment
import random
setup_logging()
log = get_logger(__name__)


# ------------------------------------------------------------------------------
# Load & Register All Skills (Must be done once at startup)
# ------------------------------------------------------------------------------
# We assume 'skills.json' lives in 'game_sys/skills/data/skills.json' and is
# UTF-8 encoded.
SkillRegistry.load_from_file("game_sys/skills/data/skills.json")
log.info("Skills loaded into registry: %s", SkillRegistry.all_ids())


def view_character_test():
    """
    Demonstrate character creation and basic stats display.
    """
    person = create_character("wizard", name="Hero", level=1)
    # Create a level-1 Knight named Aria
    character = create_character(
        "Goblin",
        name="goblin",
        job_id="goblin"
    )
    log.info("=== Character View Test ===")
    health = create_item("health_potion", level=10, grade=5, rarity="rare")
    person.inventory.add_item(health, quantity=1)
    log.info(person)  # Should show 20 SP available
    # log.info(character)  # __str__ will show name, level, stats,
    # inventory, etc.


def learning_system_test():
    """
    Demonstrate the LearningSystem: awarding SP, listing available skills,
    learning a skill, and casting it on a dummy enemy.
    """
    log.info("=== Learning System Test ===")

    # 1) Create a Player at level 1 with no SP initially
    player = create_character(
        "wizard"
        )
    log.info("Player created: %s", player.name)

    # 2) Show unspent SP (should be zero)
    log.info("Unspent SP before leveling: %d", player.learning.unspent_sp())

    # 3) Award 2 skill points manually (simulate level-ups or rewards)
    player.learning.add_sp(20)
    log.info(
            "Unspent SP after awarding 20 points: %d",
            player.learning.unspent_sp()
            )

    # 4) List all skills the player can learn right now
    available = player.learning.available_to_learn()
    log.info(
            "Available skills to learn (level %d): %s",
            player.stats_mgr.levels.lvl, available
            )

    # 5) If "fireball" is available, learn it; otherwise learn another first
    #    (Assumes skills.json defines "fireball" with min_level=1 and
    #     sp_cost=1)
    if "fireball" in available:
        player.learning.learn("fireball")
        log.info("Learned skill: fireball")
    else:
        # Learn any available skill to demonstrate prerequisites
        first_skill = available[0] if available else None
        if first_skill:
            player.learning.learn(first_skill)
            log.info("Learned skill: %s", first_skill)

    log.info(
            "Known skills after learning: %s",
            player.learning.get_known_skills()
            )
    log.info("Remaining SP: %d", player.learning.unspent_sp())

    # 6) Create a dummy Enemy to test casting
    enemy = create_character(
            "NPC", name="Training Dummy",
            level=1, job_id="dummy")
    log.info("Enemy starting health: %d", enemy.current_health)

    # 7) Attempt to cast each known skill on the enemy
    for skill_id in player.learning.get_known_skills():
        skill_obj = player.learning.get_skill_object(skill_id)
        # Check if player has enough mana & cooldown is zero
        if skill_obj.can_cast(player):
            log.info("Casting skill '%s' on enemy...", skill_id)
            skill_obj.use(player, enemy, CombatEngine(player, enemy))
            log.info("Enemy health after '%s': %d",
                     skill_id, enemy.current_health)
        else:
            log.info(
                    "Cannot cast '%s' (not enough mana or on cooldown).",
                    skill_id
                    )

    # 8) Demonstrate cooldown decrement (tick_all_cooldowns)
    log.info("Ticking all cooldowns...")
    player.learning.tick_all_cooldowns()
    for skill_id, skill_obj in player.learning.instantiated_skills.items():
        log.info(
                "Skill '%s' cooldown now: %d",
                skill_id, skill_obj._current_cooldown
                )

    # 9) Demonstrate unlearning a skill (refund SP)
    if player.learning.get_known_skills():
        to_unlearn = player.learning.get_known_skills()[0]
        player.learning.unlearn(to_unlearn)
        log.info("Unlearned '%s'; SP refunded. Remaining SP: %d",
                 to_unlearn, player.learning.unspent_sp())
        log.info("Known skills now: %s", player.learning.get_known_skills())

    log.info(f"Final Player State{player}:")


def inventory_system_test():
    """
    Demonstrate inventory operations: adding items, auto-equipping,
    using consumables, and inspecting inventory state.
    """
    log.info("=== Inventory System Test ===")

    # 1) Create a Player
    hero = create_character("wizard", level=1)
    log.info("Hero created: %s", hero.name)

    # 2) Create items using the factory
    iron_sword = create_item("iron_sword")      # Equipable item
    leather_armor = create_item("leather_armor")  # Equipable item
    health_potion = create_item("health_potion")  # Consumable item
    mana_potion = create_item("mana_potion")      # Another consumable

    # 3) Add items to inventory without auto-equip
    # hero.inventory.add_item(iron_sword, quantity=1, auto_equip=True)
    hero.inventory.add_item(leather_armor, quantity=1, auto_equip=False)
    hero.inventory.add_item(health_potion, quantity=3)
    hero.inventory.add_item(mana_potion, quantity=2)

    log.info("Inventory after adding items (no auto-equip):")
    # 4) Manually equip sword and armor
    # hero.inventory.equip_item(iron_sword)
    hero.inventory.equip_item(leather_armor)
    log.info("Equipped iron_sword and leather_armor:")

    # 5) Add + auto-equip a special ring in one call
    item = create_item("ruby_band")
    hero.inventory.add_item(item, quantity=1, auto_equip=True)
    log.info("Added and auto-equipped:")

    # 6) Simulate taking damage, then use a health potion
    hero.take_damage(random.randint(1, 100), damage_type=DamageType.FIRE)
    before_hp = hero.current_health
    log.info("Hero's health before potion: %d", before_hp)
    hero.inventory.use_item(health_potion)
    max_hp = hero.stats.effective().get("health")
    after_hp = hero.current_health
    log.info("Hero's health after potion: %d (max: %d)", after_hp, max_hp)
    # 7) Use a mana potion to restore mana
    hero.drain_mana(5)
    before_mp = hero.current_mana  # Simulate mana usage
    log.info("Hero's mana before potion: %d", before_mp)
    max_mp = hero.stats.effective().get("mana")
    hero.inventory.use_item(mana_potion)
    after_mp = hero.current_mana
    log.info("Hero's mana after potion: %d (max: %d)", after_mp, max_mp)
    # 8) Attempt to use consumable when none remain (should handle gracefully)
    #    Remove all health potions first
    hero.inventory.remove_item(health_potion, quantity=2)
    try:
        hero.inventory.use_item(health_potion)
    except Exception as e:
        log.info(
                "Expected error when using health_potion with none left: %s",
                e
                )

    # 9) Display final inventory state
    log.info("Final inventory state:\n%s", hero)


def combat_system_test():
    """
    Demonstrate a simple combat encounter with one player vs. multiple enemies.
    """
    log.info("=== Combat System Test ===")

    # 1) Create a high-level Player (combat-ready) and assign job "knight"
    player = create_character(
        "Player",
        name="Sir Lancelot",
        level= 100,
        job_id="knight",
        grade=7,
        rarity="DIVINE",
        )
    log.info("Created player: %s (Level %d)", player.name, player.stats_mgr.levels.lvl)
    # 2) Create two enemies: goblin and orc
    goblin = create_character(
        "goblin",
        name="Grim",
        level=50,
        )
    orc = create_character("Orc", job_id="orc", level=50, name="Grom")
    enemies = [goblin, orc]
    log.info("Enemies: %s, %s", goblin.name, orc.name)

    # 3) Equip player with a sword and armor for combat
    sword = create_item("steel_sword")
    armor = create_item("plate_armor")
    player.inventory.add_item(sword, quantity=1, auto_equip=True)
    player.inventory.add_item(armor, quantity=1, auto_equip=True)
    log.info("Player equipped for combat.")
    # 4) Start the encounter
    encounter = Encounter(player, enemies)
    result = encounter.start()
    log.info("Combat result:\n%s", result)

    # 5) After combat, log player’s remaining health and status
    log.info(sword)

if __name__ == "__main__":
    # Run each test in sequence
    # view_character_test()
    # learning_system_test()
    # inventory_system_test()
    # combat_system_test()
