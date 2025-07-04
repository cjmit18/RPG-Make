#!/usr/bin/env python3
"""
Test script to verify that the burn effect from fireball spells is working correctly.
"""

from game_sys.character.actor import Actor
from game_sys.magic.spell_loader import load_spell
from game_sys.effects.factory import EffectFactory
from game_sys.effects.status_manager import status_manager

def test_burn_effect():
    """Test that the burn effect from fireball works correctly."""
    print("=== Burn Effect Test ===")
    
    # Create test characters
    mage = Actor(
        name="Test Mage",
        base_stats={'health': 100, 'intellect': 20}
    )
    
    target = Actor(
        name="Test Target",
        base_stats={'health': 100}
    )
    
    print(f"Target initial health: {target.current_health}")
    
    # Load the fireball spell
    fireball = load_spell("fireball")
    if not fireball:
        print("ERROR: Could not load fireball spell")
        return
    
    print(f"Loaded fireball with {len(fireball.effects)} effects")
    
    # Apply the burn effect directly
    for effect in fireball.effects:
        print(f"Applying effect: {effect.id}")
        effect.apply(mage, target)
    
    print(f"Target has {len(target.active_statuses)} active statuses")
    
    # Simulate time passing to trigger burn damage
    dt = 1.0  # 1 second
    
    # Tick status effects for 5 seconds
    for i in range(5):
        health_before = target.current_health
        status_manager.tick(dt)
        health_after = target.current_health
        damage = health_before - health_after
        
        print(f"Second {i+1}: Health {health_before} -> {health_after} (Damage: {damage})")
    
    print(f"Target final health: {target.current_health}")
    print(f"Target has {len(target.active_statuses)} active statuses remaining")
    
    # Tick one more time to ensure effect expires
    status_manager.tick(dt)
    print(f"After expiration: Target has {len(target.active_statuses)} active statuses")
    
    print("Burn effect test completed!")

if __name__ == "__main__":
    test_burn_effect()
