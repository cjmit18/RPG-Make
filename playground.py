from logs.logs import setup_logging, get_logger
from game_sys.character.character_creation import create_character
from game_sys.inventory.inventory import Inventory
from game_sys.core.encounter import Encounter
from game_sys.items.factory import create_item
log = get_logger(__name__)
setup_logging()

def combat_test():
    """Test combat functionality with a player and enemies."""
    # Create a player character and some enemies for combat
    character = create_character("Hero", level=5, job_id="knight")
    enemy = create_character("Goblin", level=2)
    enemies = [enemy,enemy]
    combat = Encounter(character, enemies).start()
    log.info(f"\nCombat result: \n{combat}")
    log.info(character)
def view_test():
    character = create_character("Player", job_id="rogue", name="Aria", level=1)
    # Create a job and assign it to the character
    log.info(character)
def inventory_test():
    # 1) Make a player
    hero = create_character("Player", name="Aria", level=1)
    
    # 2) Create some items from your JSON templates
    sword  = create_item("iron_sword")     # Equipable
    armor  = create_item("leather_armor")  # Equipable
    potion = create_item("health_potion")  # Consumable

    # 3) Add to inventory (without equipping)
    hero.inventory.add_item(sword,  quantity=1, auto_equip=False)
    hero.inventory.add_item(armor,  quantity=1)
    hero.inventory.add_item(potion, quantity=2)

    # 4) Equip the sword and armor manually
    hero.inventory.equip_item(sword)
    hero.inventory.equip_item(armor)

    # 5) Or add+auto-equip in one go
    # (uses the `auto_equip=True` flag you added)
    ring = create_item("emerald_loop")
    hero.inventory.add_item(ring, quantity=1, auto_equip=True)

    # 6) Use a consumable
    hero.take_damage(5)  # Simulate taking damage
    log.info(f"Before potion: HP = {hero.current_health}/{hero.stats.effective().get('health')}")
    hero.inventory.use_item(potion)  
    log.info(f"After potion:  HP = {hero.current_health}/{hero.stats.effective().get('health')}")

    # 7) Inspect
    log.info(hero)
if __name__ == "__main__":
   inventory_test()
