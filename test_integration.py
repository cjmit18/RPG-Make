#!/usr/bin/env python3
"""Test script to verify AI integration and resistance/weakness system."""

from game_sys.character.character_factory import create_character
from game_sys.combat.combat_service import CombatService

def test_ai_integration():
    """Test that AI integration is working."""
    print("=== Testing AI Integration ===")
    
    try:
        from game_sys.ai.ai_demo_integration import AIDemoController  
        
        combat_service = CombatService()
        ai_controller = AIDemoController(combat_service)
        
        # Create an enemy
        enemy = create_character('orc')
        print(f'Created enemy: {enemy.name}')
        
        # Test AI enablement
        success = ai_controller.enable_ai_for_enemy(enemy)
        print(f'AI enablement result: {success}')
        
        if success:
            print('✅ AI integration working!')
            return True
        else:
            print('❌ AI integration failed')
            return False
            
    except Exception as e:
        print(f'❌ AI integration error: {e}')
        return False

def test_resistance_weakness():
    """Test that resistance/weakness system is working."""
    print("\n=== Testing Resistance/Weakness System ===")
    
    try:
        # Create characters
        hero = create_character('hero') 
        orc = create_character('orc')
        
        print(f'Hero: {hero.name}')
        print(f'Orc: {orc.name}')
        print(f'Orc weaknesses: {orc.weaknesses}')
        
        # Test fireball against orc (should show fire weakness)
        service = CombatService()
        result = service.cast_spell_at_target(hero, 'fireball', orc)
        
        print(f'Fireball result:')
        print(f'  Success: {result["success"]}')
        print(f'  Damage: {result["damage"]}')
        
        # Check for resistance messages
        resistance_messages = result.get('resistance_messages', [])
        print(f'  Resistance messages: {resistance_messages}')
        
        if resistance_messages:
            print('✅ Resistance/weakness feedback working!')
            for msg in resistance_messages:
                print(f'    {msg}')
            return True
        else:
            print('❌ No resistance/weakness feedback found')
            return False
            
    except Exception as e:
        print(f'❌ Resistance/weakness error: {e}')
        return False

def main():
    """Run all tests."""
    print("Testing AI and Resistance/Weakness Systems")
    print("=" * 50)
    
    ai_ok = test_ai_integration()
    resist_ok = test_resistance_weakness()
    
    print("\n" + "=" * 50)
    if ai_ok and resist_ok:
        print("✅ ALL TESTS PASSED!")
        print("✅ Task completed successfully:")
        print("  - AI integration working")
        print("  - Resistance/weakness feedback moved to combat engine")
        print("  - Enemy class properly integrates with AI")
    else:
        print("❌ Some tests failed:")
        if not ai_ok:
            print("  - AI integration needs fixing")
        if not resist_ok:
            print("  - Resistance/weakness feedback needs fixing")

if __name__ == '__main__':
    main()
