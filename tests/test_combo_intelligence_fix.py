#!/usr/bin/env python3
"""Test combo system with the fixed intelligence stats."""

from game_sys.character.character_factory import create_character
from game_sys.magic.spell_manager import SpellManager

def test_combo_with_fixed_intelligence():
    """Test that combos properly increase intelligence and affect magic power."""
    print('=== Testing Combo System with Fixed Intelligence ===')
    
    # Create a mage character
    mage = create_character('mage')
    print(f'Created mage: {mage.name}')
    print(f'Mage job: {mage.job_id}')
    print(f'Mage passives: {mage.passive_ids}')
    
    # Check initial stats
    print(f'\n--- Initial Stats ---')
    print(f'Base intelligence: {mage.get_stat("intelligence")}')
    print(f'Magic power: {mage.get_stat("magic_power")}')
    print(f'Mana: {mage.get_stat("mana")}')
    
    # Initialize spell manager and start a combo
    spell_manager = SpellManager()
    print(f'\n--- Starting Combo ---')
    
    # Cast first spell to start combo
    result1 = spell_manager.cast_spell(mage, "fireball")
    print(f'Cast fireball: {result1}')
    
    # Check if combo started
    combo_context = spell_manager.get_combo_context(mage)
    print(f'Combo context: {combo_context}')
    
    if combo_context:
        print(f'Intelligence after combo start: {mage.get_stat("intelligence")}')
        print(f'Magic power after combo start: {mage.get_stat("magic_power")}')
        
        # Try to complete the combo with ice_shard
        print(f'\n--- Attempting to Complete Combo ---')
        result2 = spell_manager.cast_spell(mage, "ice_shard")
        print(f'Cast ice_shard: {result2}')
        
        # Check final stats
        print(f'\n--- Final Stats After Combo ---')
        print(f'Intelligence: {mage.get_stat("intelligence")}')
        print(f'Magic power: {mage.get_stat("magic_power")}')
        print(f'Mana: {mage.get_stat("mana")}')
    else:
        print('No combo context found - combo may not have started properly')

if __name__ == "__main__":
    test_combo_with_fixed_intelligence()
