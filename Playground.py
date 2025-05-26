from jobs.knight import Knight
from jobs.base import Base
from jobs.mage import Mage
from jobs.healer import Healer
from jobs.rogue import Rogue
from core.character_creation import Player, Enemy


def test_mana_caps():
    character = Player("TestChar", level=1)
    enemy = Enemy("TestEnemy", level=1)
    character.lvls.add_experience(10000)  # Level up to ensure mana is set correctly
    print(character)
test_mana_caps()
