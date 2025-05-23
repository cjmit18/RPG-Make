
from character_creation import Player
from class_creation import Mage
from potion_list import Mana_Potion
def test_mana_caps():
    
    character = Player("TestChar")
    print(character)
    #character.change_class(Mage)
    print("Before potion:", character.mana, "/", character.max_mana)
    character.mana -= 24
    character.update_stats()
    print("After damage:", character.mana, "/", character.max_mana)
    potion = Mana_Potion()
    character.inventory.add_item(potion)
    character.inventory.use_item(potion)
    print("After potion:", character.mana, "/", character.max_mana)
test_mana_caps()