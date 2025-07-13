#!/usr/bin/env python3
"""
Test script to verify penetration system is working correctly.
"""

from game_sys.character.character_factory import create_character
from game_sys.items.factory import ItemFactory
from game_sys.combat.combat_service import CombatService
from game_sys.logging import get_logger

logger = get_logger("penetration_test")

def test_armor_penetration():
    """Test armor penetration with wooden stick."""
    print("=== Testing Armor Penetration ===")
    
    # Create attacker and defender
    attacker = create_character("hero", level=5)
    defender = create_character("goblin", level=5)
    
    print(f"Attacker: {attacker.name} (Level {attacker.level})")
    print(f"Defender: {defender.name} (Level {defender.level})")
    print(f"Defender armor: {defender.get_stat('damage_reduction'):.3f}")
    
    # Create wooden stick with armor penetration
    wooden_stick = ItemFactory.create("wooden_stick")
    print(f"Weapon: {wooden_stick.name}")
    print(f"Base damage: {wooden_stick.base_damage}")
    print(f"Effect IDs: {wooden_stick.effect_ids}")
    
    # Equip weapon
    attacker.equip_weapon(wooden_stick)
    
    # Check if armor penetration is applied to attacker
    armor_pen = attacker.get_stat('armor_penetration')
    print(f"Attacker armor penetration: {armor_pen}")
    
    # Test combat
    combat_service = CombatService()
    
    print("\n--- Combat Test (5 attacks) ---")
    for i in range(5):
        defender.current_health = defender.max_health  # Reset health
        result = combat_service.perform_attack(attacker, defender, wooden_stick)
        if result['success']:
            print(f"Attack {i+1}: {result['damage']:.2f} damage")
        else:
            print(f"Attack {i+1}: Failed - {result['message']}")

def test_magic_penetration():
    """Test magic penetration with arcane focus."""
    print("\n=== Testing Magic Penetration ===")
    
    # Create mage and defender
    attacker = create_character("hero", level=5)
    attacker.base_stats['job_id'] = 'mage'  # Make them a mage
    defender = create_character("dragon", level=5)
    
    print(f"Attacker: {attacker.name} (Level {attacker.level}) - Mage")
    print(f"Defender: {defender.name} (Level {defender.level})")
    print(f"Defender magic resistance: {defender.get_stat('magic_resistance'):.3f}")
    
    # Create arcane focus with magic penetration
    arcane_focus = ItemFactory.create("arcane_focus")
    print(f"Offhand: {arcane_focus.name}")
    print(f"Effect IDs: {arcane_focus.effect_ids}")
    
    # Equip offhand
    attacker.equip_offhand(arcane_focus)
    
    # Check if magic penetration is applied to attacker
    magic_pen = attacker.get_stat('magic_penetration')
    print(f"Attacker magic penetration: {magic_pen}")
    
    # Test spell combat
    combat_service = CombatService()
    
    print("\n--- Spell Combat Test (5 casts) ---")
    for i in range(5):
        defender.current_health = defender.max_health  # Reset health
        result = combat_service.cast_spell_at_target(attacker, "fireball", defender)
        if result['success']:
            print(f"Spell {i+1}: {result['damage']:.2f} damage")
        else:
            print(f"Spell {i+1}: Failed - {result['message']}")

if __name__ == "__main__":
    try:
        test_armor_penetration()
        test_magic_penetration()
        print("\n=== Penetration Test Complete ===")
    except Exception as e:
        logger.error(f"Test failed: {e}")
        import traceback
        traceback.print_exc()
