from jobs.knight import Knight
from jobs.base import Base
from jobs.mage import Mage
from jobs.healer import Healer
from jobs.rogue import Rogue
from core.character_creation import Player, Enemy
from core.encounter import Encounter
from core.combat_functions import Combat
from logs import setup_logging
def main():
    setup_logging()

def Test_combat():
    character = Player("TestChar", level=10)
    enemy = Enemy("TestEnemy", level=1)
    enemies = [Enemy("Goblin", level=1), Enemy("Orc", level=2)]
    combat = Encounter(character, enemies).start()
    print(combat)
if __name__ == "__main__":
    Test_combat()
