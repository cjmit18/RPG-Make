#!/usr/bin/env python3
"""Test script to verify spell damage types work with resistance/weakness system."""

from game_sys.character.character_factory import create_character
from game_sys.combat.combat_service import CombatService

def test_spell_resistance():
    """Test that spells apply damage types for resistance/weakness calculations."""
    
    # Create a hero and orc
    hero = create_character('hero')
    orc = create_character('orc')

    print(f'Hero: {hero.name}')
    print(f'Orc: {orc.name} (HP: {orc.current_health})')
    print(f'Orc weaknesses: {orc.weaknesses}')
    print(f'Orc resistances: {orc.resistances}')

    # Create combat service and cast fireball
    service = CombatService()
    print('\n=== Testing Fireball (FIRE damage) ===')
    print(f'Orc HP before: {orc.current_health}')
    
    result = service.cast_spell_at_target(hero, 'fireball', orc)

    print('Fireball cast result:')
    print(f'  Success: {result["success"]}')
    print(f'  Damage: {result["damage"]}')
    print(f'  Message: {result["message"]}')
    print(f'  Orc HP after: {orc.current_health}')
    
    # Expected: 50 base + int bonus = ~52.5, with 25% weakness = ~65.6 damage
    print('Expected: ~65-70 damage due to 25% fire weakness')
    
    # Test with a fresh orc and ice shard (no weakness)
    orc2 = create_character('orc')
    print('\n=== Testing Ice Shard (ICE damage) ===')
    print(f'Fresh Orc HP before: {orc2.current_health}')
    
    result2 = service.cast_spell_at_target(hero, 'ice_shard', orc2)
    
    print('Ice Shard cast result:')
    print(f'  Success: {result2["success"]}')
    print(f'  Damage: {result2["damage"]}')
    print(f'  Message: {result2["message"]}')
    print(f'  Orc HP after: {orc2.current_health}')
    
    # Expected: 20 base + int bonus = ~22.5, no weakness = normal damage
    print('Expected: ~22-25 damage (no ice weakness)')

if __name__ == '__main__':
    test_spell_resistance()
