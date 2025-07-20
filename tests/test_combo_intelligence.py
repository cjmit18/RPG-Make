#!/usr/bin/env python3
"""Test combo intelligence boost system."""

from game_sys.character.character_factory import create_character
from game_sys.magic.spell_manager import SpellManager

def test_combo_intelligence():
    """Test that combo system properly boosts intelligence and magic power."""
    print('Testing combo intelligence boost...')
    
    # Create a mage character
    player = create_character('mage')
    spell_manager = SpellManager()
    
    print(f'Initial intelligence: {player.get_stat("intelligence")}')
    print(f'Initial magic_power: {player.get_stat("magic_power")}')
    
    # Cast fireball to start combo
    print('\nCasting fireball to start combo...')
    result = spell_manager.cast_spell(player, 'fireball', [player])
    print(f'Cast result: {result}')
    
    # Check if combo is active
    combo_context = spell_manager.get_combo_context(player)
    print(f'Combo active: {combo_context is not None}')
    
    if combo_context:
        print(f'Intelligence after combo: {player.get_stat("intelligence")}')
        print(f'Magic power after combo: {player.get_stat("magic_power")}')
    else:
        print('No combo was started - fireball may not be part of a combo')
    
    print('\nCombo intelligence test complete!')

if __name__ == "__main__":
    test_combo_intelligence()
