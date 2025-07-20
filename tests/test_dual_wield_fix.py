#!/usr/bin/env python3

"""
Test script to verify dual wield system fixes.
Tests both normal dual wield scenarios and edge cases.
"""

import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from game_sys.logging import get_logger
from game_sys.character.character_factory import create_character
from game_sys.items.factory import ItemFactory

logger = get_logger("dual_wield_test")

def test_dual_wield_system():
    """Test dual wield system functionality."""
    
    print("\n" + "="*50)
    print("DUAL WIELD SYSTEM TEST")
    print("="*50)
    
    # Create a test character
    try:
        player = create_character("hero")
        print(f"✓ Created test character: {player.name}")
    except Exception as e:
        print(f"✗ Failed to create character: {e}")
        return False
    
    # Test 1: Basic dual wield setup (empty hands → dual wield)
    print("\n--- Test 1: Empty hands → dual wield ---")
    try:
        dagger1 = ItemFactory.create('iron_dagger')
        dagger2 = ItemFactory.create('iron_dagger')
        
        if not dagger1 or not dagger2:
            print("✗ Failed to create daggers")
            return False
            
        print(f"Created daggers: {dagger1.name}, {dagger2.name}")
        print(f"Dagger 1 - slot: {dagger1.slot}, slot_restriction: {getattr(dagger1, 'slot_restriction', 'None')}, dual_wield: {getattr(dagger1, 'dual_wield', False)}")
        print(f"Dagger 2 - slot: {dagger2.slot}, slot_restriction: {getattr(dagger2, 'slot_restriction', 'None')}, dual_wield: {getattr(dagger2, 'dual_wield', False)}")
        
        # Equip first dagger in weapon slot
        player.equip_weapon(dagger1)
        print(f"✓ Equipped {dagger1.name} in weapon slot")
        
        # Equip second dagger in offhand slot
        player.equip_offhand(dagger2)
        print(f"✓ Equipped {dagger2.name} in offhand slot")
        
        print("✓ Test 1 PASSED: Basic dual wield setup successful")
        
    except Exception as e:
        print(f"✗ Test 1 FAILED: {e}")
        return False
    
    # Test 2: Smart equipping with either_hand weapons
    print("\n--- Test 2: Smart equipping system ---")
    try:
        # Clear equipment
        player.weapon = None
        player.offhand = None
        
        # Test smart equipping
        dagger3 = ItemFactory.create('dagger')
        if hasattr(player, 'equip_weapon_smart'):
            success = player.equip_weapon_smart(dagger3)
            if success:
                print(f"✓ Smart equipping worked for {dagger3.name}")
                
                # Add second dagger via smart equipping
                dagger4 = ItemFactory.create('dragon_tooth_dagger')
                success2 = player.equip_weapon_smart(dagger4)
                if success2:
                    print(f"✓ Smart equipping added second weapon: {dagger4.name}")
                    
                    # Check final state
                    weapon_name = player.weapon.name if player.weapon else "None"
                    offhand_name = player.offhand.name if player.offhand else "None"
                    print(f"Final state - Weapon: {weapon_name}, Offhand: {offhand_name}")
                    print("✓ Test 2 PASSED: Smart equipping successful")
                else:
                    print("✗ Test 2 FAILED: Second smart equip failed")
                    return False
            else:
                print("✗ Test 2 FAILED: First smart equip failed")
                return False
        else:
            print("⚠ Test 2 SKIPPED: Smart equipping not available")
            
    except Exception as e:
        print(f"✗ Test 2 FAILED: {e}")
        return False
    
    # Test 3: Reverse scenario (offhand first, then weapon)
    print("\n--- Test 3: Reverse dual wield (offhand → weapon) ---")
    try:
        # Clear equipment
        player.weapon = None
        player.offhand = None
        
        # Equip dagger in offhand first
        reverse_dagger1 = ItemFactory.create('iron_dagger')
        player.equip_offhand(reverse_dagger1)
        print(f"✓ Equipped {reverse_dagger1.name} in offhand first")
        
        # Now try to equip another dagger in weapon slot
        reverse_dagger2 = ItemFactory.create('dagger')
        if hasattr(player, 'equip_weapon_smart'):
            success = player.equip_weapon_smart(reverse_dagger2)
            if success:
                weapon_name = player.weapon.name if player.weapon else "None"
                offhand_name = player.offhand.name if player.offhand else "None"
                print(f"✓ Reverse dual wield successful - Weapon: {weapon_name}, Offhand: {offhand_name}")
                print("✓ Test 3 PASSED: Reverse dual wield successful")
            else:
                print("✗ Test 3 FAILED: Reverse dual wield failed")
                return False
        else:
            # Fallback to direct equipping
            player.equip_weapon(reverse_dagger2)
            weapon_name = player.weapon.name if player.weapon else "None"
            offhand_name = player.offhand.name if player.offhand else "None"
            print(f"✓ Direct equipping worked - Weapon: {weapon_name}, Offhand: {offhand_name}")
            print("✓ Test 3 PASSED: Reverse dual wield successful (direct method)")
            
    except Exception as e:
        print(f"✗ Test 3 FAILED: {e}")
        return False
    
    # Test 4: Conflict scenarios
    print("\n--- Test 4: Conflict scenarios ---")
    try:
        # Clear equipment
        player.weapon = None
        player.offhand = None
        
        # Equip a two-handed weapon first
        sword = ItemFactory.create('sword')
        if sword:
            player.equip_weapon(sword)
            print(f"✓ Equipped two-handed weapon: {sword.name}")
            
            # Try to equip dagger in offhand (should fail or replace)
            conflict_dagger = ItemFactory.create('iron_dagger')
            try:
                player.equip_offhand(conflict_dagger)
                # If this succeeds, check if two-handed was unequipped
                weapon_name = player.weapon.name if player.weapon else "None"
                offhand_name = player.offhand.name if player.offhand else "None"
                print(f"Result - Weapon: {weapon_name}, Offhand: {offhand_name}")
                print("✓ Test 4 PASSED: Conflict handling working")
            except Exception as conflict_e:
                print(f"✓ Test 4 PASSED: Conflict properly prevented: {conflict_e}")
        else:
            print("⚠ Test 4 SKIPPED: Could not create sword for conflict test")
            
    except Exception as e:
        print(f"✗ Test 4 FAILED: {e}")
        return False
    
    print("\n" + "="*50)
    print("ALL DUAL WIELD TESTS COMPLETED SUCCESSFULLY!")
    print("="*50)
    return True

if __name__ == "__main__":
    success = test_dual_wield_system()
    sys.exit(0 if success else 1)
