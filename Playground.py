
from character_creation import Player
from class_creation import Mage,Knight,Rogue,Healer
from potion_list import Mana_Potion, Health_Potion, Stamina_Potion
from amulet_list import Amulet
def test_mana_caps():
    character = Player("TestChar", level=1)
    character.change_class(Mage)
    character.drain_mana(5)
    print(character)
    character.inventory.use_by_name("Mana Potion")
    return print(character.inventory.equipped_items)
test_mana_caps()