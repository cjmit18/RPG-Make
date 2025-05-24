
from character_creation import Player
from class_creation import Mage,Knight,Rogue,Healer
from potion_list import Mana_Potion, Health_Potion, Stamina_Potion
from amulet_list import Amulet
def test_mana_caps():
    
    character = Player("TestChar", level=10)
    character.change_class(Knight)
  #  character.inventory.use_by_name("Mage's Potion")
    return print(character)
test_mana_caps()