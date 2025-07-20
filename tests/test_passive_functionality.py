#!/usr/bin/env python3
"""Test passive system functionality in detail."""

from game_sys.character.character_factory import create_character
from game_sys.skills.passive_manager import PassiveManager

def test_passive_functionality():
    """Test that passives are properly registered and functioning."""
    print('Testing passive system functionality...')
    
    # Test warrior with berserker_rage passive
    print('\n--- Testing Warrior Passive (berserker_rage) ---')
    warrior = create_character('warrior')
    print(f'Created warrior: {warrior.name}')
    print(f'Job: {warrior.job_id}')
    
    # Check if PassiveManager has the character registered
    print(f'Character name: {warrior.name}')
    
    # Check if the character has passive_ids attribute
    if hasattr(warrior, 'passive_ids'):
        print(f'Character passive IDs: {warrior.passive_ids}')
    else:
        print('Character has no passive_ids attribute')
    
    # Get registered passives using PassiveManager class methods
    try:
        # Check if PassiveManager has methods to query passives
        if hasattr(PassiveManager, 'get_registered_passives'):
            passives = PassiveManager.get_registered_passives(warrior.name)
            print(f'Registered passives: {passives}')
        elif hasattr(PassiveManager, '_passive_registry'):
            print(f'Passive registry keys: {list(PassiveManager._passive_registry.keys())}')
            if warrior.name in PassiveManager._passive_registry:
                passives = PassiveManager._passive_registry[warrior.name]
                print(f'Warrior passives: {[p.passive_id for p in passives]}')
        else:
            print('PassiveManager structure unknown - checking instance methods')
            pm_instance = PassiveManager()
            print(f'PassiveManager methods: {[m for m in dir(pm_instance) if not m.startswith("_")]}')
    except Exception as e:
        print(f'Error checking passives: {e}')
    
    # Test mage with battle_meditation passive  
    print('\n--- Testing Mage Passive (battle_meditation) ---')
    mage = create_character('mage')
    print(f'Created mage: {mage.name}')
    print(f'Job: {mage.job_id}')
    if hasattr(mage, 'passive_ids'):
        print(f'Mage passive IDs: {mage.passive_ids}')
    else:
        print('Mage has no passive_ids attribute')
    
    # Test rogue with endless_sprint passive
    print('\n--- Testing Rogue Passive (endless_sprint) ---')
    rogue = create_character('rogue')
    print(f'Created rogue: {rogue.name}')
    print(f'Job: {rogue.job_id}')
    if hasattr(rogue, 'passive_ids'):
        print(f'Rogue passive IDs: {rogue.passive_ids}')
    else:
        print('Rogue has no passive_ids attribute')
    
    # Check if passives affect stats or provide abilities
    print('\n--- Testing Passive Effects ---')
    
    # Check warrior stats for berserker effects
    print(f'Warrior base strength: {warrior.get_stat("strength")}')
    print(f'Warrior computed strength: {warrior.get_stat("strength")}')
    
    # Check mage mana-related stats for meditation effects  
    print(f'Mage base intelligence: {mage.get_stat("intelligence")}')
    print(f'Mage mana: {mage.get_stat("mana")}')
    
    # Check rogue stamina for sprint effects
    print(f'Rogue base dexterity: {rogue.get_stat("dexterity")}')
    print(f'Rogue stamina: {rogue.get_stat("stamina")}')
    
    print('\nPassive functionality test complete!')

if __name__ == "__main__":
    test_passive_functionality()
