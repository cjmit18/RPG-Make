from logs.logs import setup_logging
from game_sys.core.character_creation import Player, Enemy
from game_sys.core.inventory_functions import Inventory
from game_sys.core.encounter import Encounter
from game_sys.jobs import Knight, Mage, Rogue
from game_sys.items.factory         import create_item

setup_logging()
def combat_test():
    """Test combat functionality with a player and enemies."""
    # Create a player character and some enemies for combat
    character = Player("TestChar", level=5)
    enemy = Enemy("TestEnemy", level=6)
    enemies = [Enemy("Goblin", level=4), Enemy("Orc", level=2)]

    combat = Encounter(character, enemies).start()
    print(combat)
def view_test():
    character = Player("TestChar", level=1)
    character.assign_job(Knight)
    print(character)
def inventory_test():
    # 1) Make a player
    hero = Player("Aria", level=1)
    
    # 2) Create some items from your JSON templates
    sword  = create_item("iron_sword")     # Equipable
    armor  = create_item("leather_armor")  # Equipable
    potion = create_item("health_potion")  # Consumable

    # 3) Add to inventory (without equipping)
    hero.inventory.add_item(sword,  quantity=1)
    hero.inventory.add_item(armor,  quantity=1)
    hero.inventory.add_item(potion, quantity=2)

    # 4) Equip the sword and armor manually
    hero.inventory.equip_item(sword.id)
    hero.inventory.equip_item(armor.id)

    # 5) Or add+auto-equip in one go
    # (uses the `auto_equip=True` flag you added)
    ring = create_item("emerald_loop")
    hero.inventory.add_item(ring, quantity=1, auto_equip=True)

    # 6) Use a consumable
    hero.take_damage(10)  # Simulate taking damage
    print(f"Before potion: HP = {hero.current_health}/{hero.stats.effective().get('health')}")
    hero.inventory.use_item(potion)  
    print(f"After potion:  HP = {hero.current_health}/{hero.stats.effective().get('health')}")

    # 7) Inspect
    print(hero.inventory)
if __name__ == "__main__":
    inventory_test()