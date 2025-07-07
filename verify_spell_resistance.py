#!/usr/bin/env python3
"""
Quick verification script to test spell resistance/weakness feedback.
"""

from game_sys.character.actor import Actor, Enemy
from game_sys.combat.combat_service import CombatService
from game_sys.core.damage_types import DamageType
from game_sys.character.job_manager import JobManager

def test_spell_resistance_feedback():
    """Test that spell casting generates resistance/weakness feedback."""
    print("Testing spell resistance/weakness feedback...")
    
    # Create a fire mage
    mage_stats = {
        'strength': 10.0, 'dexterity': 15.0, 'intellect': 20.0,
        'vitality': 12.0, 'luck': 10.0
    }
    mage = Actor("Fire Mage", mage_stats)
    job_manager = JobManager()
    job_manager.assign(mage, 'mage')
    mage.current_mana = 100
    
    # Create an enemy with fire resistance
    enemy_stats = {
        'strength': 15.0, 'dexterity': 10.0, 'intellect': 8.0,
        'vitality': 18.0, 'luck': 5.0
    }
    enemy = Enemy("Fire Resistant Goblin", enemy_stats)
    enemy.current_health = 100
    enemy.max_health = 100
    enemy.resistances = {DamageType.FIRE: 0.5}  # 50% fire resistance
    
    # Create combat service
    combat_service = CombatService()
    
    # Cast fireball at the enemy
    result = combat_service.cast_spell_at_target(mage, 'fireball', enemy)
    
    print(f"Spell cast result: {result}")
    print(f"Success: {result.get('success', False)}")
    print(f"Damage dealt: {result.get('damage', 0)}")
    print(f"Resistance messages: {result.get('resistance_messages', [])}")
    
    # Check if resistance feedback was generated
    if result.get('resistance_messages'):
        print("✅ SUCCESS: Resistance/weakness feedback is working!")
        for message in result.get('resistance_messages', []):
            print(f"   - {message}")
    else:
        print("❌ FAILURE: No resistance/weakness feedback generated")
    
    return len(result.get('resistance_messages', [])) > 0

if __name__ == "__main__":
    success = test_spell_resistance_feedback()
    if success:
        print("\n🎉 Spell resistance feedback is now working correctly!")
    else:
        print("\n💥 Still need to debug spell resistance feedback")
