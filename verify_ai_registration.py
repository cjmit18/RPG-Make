#!/usr/bin/env python3
"""
Quick verification script to test AI registration.
"""

from game_sys.character.actor import Actor, Enemy
from game_sys.ai.ai_service import AIService

def test_ai_registration():
    """Test that AI registration works correctly."""
    print("Testing AI registration...")
    
    # Create an enemy
    enemy_stats = {
        'strength': 15.0, 'dexterity': 10.0, 'intellect': 8.0,
        'vitality': 18.0, 'luck': 5.0
    }
    enemy = Enemy("Test Goblin", enemy_stats)
    
    # Get AI service
    ai_service = AIService()
    
    # Test AI registration
    print(f"Before: AI enabled = {enemy.ai_enabled}")
    
    # Enable AI for the enemy
    enemy.enable_ai()
    ai_service.register_ai_actor(enemy)
    
    print(f"After: AI enabled = {enemy.ai_enabled}")
    print(f"Registered actors: {len(ai_service.ai_actors)}")
    
    if enemy.ai_enabled and len(ai_service.ai_actors) > 0:
        print("✅ SUCCESS: AI registration is working!")
        return True
    else:
        print("❌ FAILURE: AI registration is not working")
        return False

if __name__ == "__main__":
    success = test_ai_registration()
    if success:
        print("\n🎉 AI registration is working correctly!")
    else:
        print("\n💥 AI registration needs debugging")
