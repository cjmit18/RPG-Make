# playground.py

from logs.logs import setup_logging, get_logger
from game_sys.character.character_creation import create_character
from game_sys.skills.learning import SkillRegistry
from game_sys.inventory.inventory import Inventory
from game_sys.items.factory import create_item
from game_sys.combat.encounter import Encounter
from game_sys.effects.base import DamageEffect

log = get_logger(__name__)
setup_logging()

# ------------------------------------------------------------------------------
# Load & Register All Skills (Must be done once at startup)
# ------------------------------------------------------------------------------
# We assume 'skills.json' lives in 'game_sys/skills/data/skills.json' and is UTF-8 encoded.
SkillRegistry.load_from_file("game_sys/skills/data/skills.json")
log.info("Skills loaded into registry: %s", SkillRegistry.all_ids())


def view_character_test():
    """
    Demonstrate character creation and basic stats display.
    """
    # Create a level-1 Knight named Aria
    character = create_character("Player", name="Aria", level=10, job_id="knight")
    #character.inventory.unequip_item("knife")
    log.info("=== Character View Test ===")
    log.info(character)  # __str__ will show name, level, stats, inventory, etc.


def learning_system_test():
    """
    Demonstrate the LearningSystem: awarding SP, listing available skills,
    learning a skill, and casting it on a dummy enemy.
    """
    log.info("=== Learning System Test ===")

    # 1) Create a Player at level 1 with no SP initially
    player = create_character("Player", name="Mage", level=100, job_id="mage")
    log.info("Player created: %s", player.name)

    # 2) Show unspent SP (should be zero)
    log.info("Unspent SP before leveling: %d", player.learning.unspent_sp())

    # 3) Award 2 skill points manually (simulate level-ups or rewards)
    player.learning.add_sp(20)
    log.info("Unspent SP after awarding 2 points: %d", player.learning.unspent_sp())

    # 4) List all skills the player can learn right now
    available = player.learning.available_to_learn()
    log.info("Available skills to learn (level %d): %s", player.levels.lvl, available)

    # 5) If "fireball" is available, learn it; otherwise learn another first
    #    (Assumes skills.json defines "fireball" with min_level=1 and sp_cost=1)
    if "fireball" in available:
        player.learning.learn("fireball")
        log.info("Learned skill: fireball")
    else:
        # Learn any available skill to demonstrate prerequisites
        first_skill = available[0] if available else None
        if first_skill:
            player.learning.learn(first_skill)
            log.info("Learned skill: %s", first_skill)

    log.info("Known skills after learning: %s", player.learning.get_known_skills())
    log.info("Remaining SP: %d", player.learning.unspent_sp())

    # 6) Create a dummy Enemy to test casting
    enemy = create_character("Enemy", name="Training Dummy", level=1)
    enemy.assign_job_by_id("dummy")  # Assign a dummy job for testing
    
    log.info("Enemy starting health: %d", enemy.current_health)

    # 7) Attempt to cast each known skill on the enemy
    for skill_id in player.learning.get_known_skills():
        skill_obj = player.learning.get_skill_object(skill_id)
        # Check if player has enough mana & cooldown is zero
        if skill_obj.can_cast(player):
            log.info("Casting skill '%s' on enemy...", skill_id)
            skill_obj.cast(player, enemy)
            log.info("Enemy health after '%s': %d", skill_id, enemy.current_health)
        else:
            log.info("Cannot cast '%s' (not enough mana or on cooldown).", skill_id)

    # 8) Demonstrate cooldown decrement (tick_all_cooldowns)
    log.info("Ticking all cooldowns...")
    player.learning.tick_all_cooldowns()
    for skill_id, skill_obj in player.learning.instantiated_skills.items():
        log.info("Skill '%s' cooldown now: %d", skill_id, skill_obj._current_cooldown)

    # 9) Demonstrate unlearning a skill (refund SP)
    if player.learning.get_known_skills():
        to_unlearn = player.learning.get_known_skills()[0]
        player.learning.unlearn(to_unlearn)
        log.info("Unlearned '%s'; SP refunded. Remaining SP: %d",
                 to_unlearn, player.learning.unspent_sp())
        log.info("Known skills now: %s", player.learning.get_known_skills())


def inventory_system_test():
    """
    Demonstrate inventory operations: adding items, auto-equipping,
    using consumables, and inspecting inventory state.
    """
    log.info("=== Inventory System Test ===")

    # 1) Create a Player
    hero = create_character("Player", name="Rogue", level=1)
    log.info("Hero created: %s", hero.name)

    # 2) Create items using the factory
    iron_sword = create_item("iron_sword")      # Equipable item
    leather_armor = create_item("leather_armor")  # Equipable item
    health_potion = create_item("health_potion")  # Consumable item
    mana_potion = create_item("mana_potion")      # Another consumable

    # 3) Add items to inventory without auto-equip
    hero.inventory.add_item(iron_sword, quantity=1, auto_equip=False)
    hero.inventory.add_item(leather_armor, quantity=1, auto_equip=False)
    hero.inventory.add_item(health_potion, quantity=3)
    hero.inventory.add_item(mana_potion, quantity=2)

    log.info("Inventory after adding items (no auto-equip):")
    log.info(hero.inventory)

    # 4) Manually equip sword and armor
    hero.inventory.equip_item(iron_sword)
    hero.inventory.equip_item(leather_armor)
    log.info("Equipped iron_sword and leather_armor:")
    log.info(hero.inventory)

    # 5) Add + auto-equip a special ring in one call
    emerald_ring = create_item("emerald_loop")
    hero.inventory.add_item(emerald_ring, quantity=1, auto_equip=True)
    log.info("Added and auto-equipped emerald_ring:")
    log.info(hero.inventory)

    # 6) Simulate taking damage, then use a health potion
    hero.take_damage(10)
    before_hp = hero.current_health
    max_hp = hero.stats.effective().get("health")
    log.info("Hero took 10 damage: HP = %d/%d", before_hp, max_hp)

    hero.inventory.use_item(health_potion)
    after_hp = hero.current_health
    log.info("Used health_potion: HP = %d/%d", after_hp, max_hp)

    # 7) Use a mana potion to restore mana
    before_mp = hero.current_mana
    max_mp = hero.stats.effective().get("mana")
    log.info("Hero MP before potion: %d/%d", before_mp, max_mp)

    hero.inventory.use_item(mana_potion)
    after_mp = hero.current_mana
    log.info("Used mana_potion: MP = %d/%d", after_mp, max_mp)

    # 8) Attempt to use consumable when none remain (should handle gracefully)
    #    Remove all health potions first
    hero.inventory.remove_item(health_potion, quantity=2)
    try:
        hero.inventory.use_item(health_potion)
    except Exception as e:
        log.info("Expected error when using health_potion with none left: %s", e)

    # 9) Display final inventory state
    log.info("Final inventory state:")
    log.info(hero.inventory)


def combat_system_test():
    """
    Demonstrate a simple combat encounter with one player vs. multiple enemies.
    """
    log.info("=== Combat System Test ===")

    # 1) Create a high-level Player (combat-ready) and assign job "knight"
    player = create_character(name="Warrior", level=30, job_id="knight")
    log.info("Created player: %s (Level %d)", player.name, player.levels.lvl)

    # 2) Create two enemies: goblin and orc
    goblin = create_character("Enemy", name="Goblin", level=10, job_id="goblin")
    orc = create_character("Enemy", name="Orc", level=10, job_id="orc")
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
    log.info("Player post-combat stats: %s", player)
if __name__ == "__main__":
    # Run each test in sequence
    combat_system_test()
