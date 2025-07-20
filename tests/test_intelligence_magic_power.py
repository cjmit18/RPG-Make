#!/usr/bin/env python3
"""Simple test to verify intelligence buffs affect magic power correctly."""

from game_sys.character.character_factory import create_character
from game_sys.effects.extensions import BuffEffect

def test_intelligence_magic_power_connection():
    """Test that intelligence buffs properly affect magic power through our fixed derived stat calculations."""
    print('=== Testing Intelligence -> Magic Power Connection ===')
    
    # Create a mage character
    mage = create_character('mage')
    print(f'Created mage: {mage.name}')
    print(f'Mage job: {mage.job_id}')
    print(f'Mage passives: {mage.passive_ids}')
    
    # Check initial stats
    print(f'\n--- Initial Stats ---')
    initial_intelligence = mage.get_stat("intelligence") 
    initial_magic_power = mage.get_stat("magic_power")
    print(f'Intelligence: {initial_intelligence}')
    print(f'Magic power: {initial_magic_power}')
    
    # Create and apply an intelligence buff (similar to what combo system would do)
    print(f'\n--- Applying Intelligence Buff ---')
    intel_buff = BuffEffect(effect_id="test_intel_buff", stat="intelligence", amount=5, duration=10)
    mage.apply_status(intel_buff)
    
    # Force stat update to recalculate derived stats
    mage.update_stats()
    
    # Check stats after buff
    print(f'\n--- Stats After Intelligence Buff ---')
    buffed_intelligence = mage.get_stat("intelligence")
    buffed_magic_power = mage.get_stat("magic_power") 
    print(f'Intelligence: {buffed_intelligence} (change: +{buffed_intelligence - initial_intelligence})')
    print(f'Magic power: {buffed_magic_power} (change: +{buffed_magic_power - initial_magic_power})')
    
    # Verify the fix is working
    if buffed_magic_power > initial_magic_power:
        print(f'\n✅ SUCCESS: Intelligence buff properly increased magic power!')
        print(f'   Intelligence boost: +{buffed_intelligence - initial_intelligence}')
        print(f'   Magic power boost: +{buffed_magic_power - initial_magic_power:.2f}')
    else:
        print(f'\n❌ FAILED: Intelligence buff did not increase magic power')
        
    # Test a warrior for comparison (they should have lower magic power due to lower intelligence)
    print(f'\n--- Warrior Comparison ---')
    warrior = create_character('warrior')
    print(f'Warrior intelligence: {warrior.get_stat("intelligence")}')
    print(f'Warrior magic power: {warrior.get_stat("magic_power")}')
    print(f'Warrior passives: {warrior.passive_ids}')

if __name__ == "__main__":
    test_intelligence_magic_power_connection()
