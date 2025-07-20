#!/usr/bin/env python3

"""
Test the exact dual wield scenario from the demo logs.
This simulates the user's specific workflow.
"""

import sys
import os
import uuid

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from game_sys.logging import get_logger
from game_sys.character.character_factory import create_character
from game_sys.items.factory import ItemFactory

logger = get_logger("demo_dual_wield_test")

def test_demo_dual_wield_scenario():
    """Test the exact scenario from the demo logs."""
    
    print("\n" + "="*60)
    print("DEMO DUAL WIELD SCENARIO TEST")
    print("="*60)
    
    # Create a test character
    try:
        player = create_character("hero")
        print(f"✓ Created test character: {player.name}")
    except Exception as e:
        print(f"✗ Failed to create character: {e}")
        return False
    
    # Simulate demo startup - unequip starting gear
    print("\n--- Simulating Demo Startup ---")
    try:
        # Unequip body armor (basic clothes)
        if hasattr(player, 'equipped_body') and player.equipped_body:
            body_item = player.equipped_body
            player.equipped_body = None
            player.inventory.add_item(body_item)
            print(f"✓ Unequipped and stored body armor: {body_item.name}")
        
        # Unequip weapon (wooden stick)
        if hasattr(player, 'weapon') and player.weapon:
            weapon_item = player.weapon
            player.weapon = None
            player.inventory.add_item(weapon_item)
            print(f"✓ Unequipped and stored weapon: {weapon_item.name}")
            
        # Ensure weapon slot is actually empty
        player.weapon = None
            
    except Exception as e:
        print(f"✗ Failed during startup simulation: {e}")
        return False
    
    # Test 1: Create first iron dagger and equip in offhand
    print("\n--- Test 1: First iron dagger to offhand ---")
    try:
        dagger1 = ItemFactory.create('iron_dagger')
        if not dagger1:
            print("✗ Failed to create first iron dagger")
            return False
            
        # Assign UUID like demo does
        dagger1.uuid = str(uuid.uuid4())
        
        # Add to inventory
        player.inventory.add_item(dagger1)
        print(f"✓ Created and added first dagger to inventory: {dagger1.name} (UUID: {dagger1.uuid})")
        
        # Remove from inventory and equip in offhand using smart equipping
        player.inventory.remove_item(dagger1)
        
        # Use smart equipping to place first dagger appropriately
        success = player.equip_weapon_smart(dagger1)
        if not success:
            print("✗ Failed to equip first dagger with smart equipping")
            return False
        print(f"✓ Equipped first dagger using smart equipping")
        
        # Verify state
        current_weapon_after = getattr(player, 'weapon', None)
        current_offhand_after = getattr(player, 'offhand', None)
        if current_weapon_after and current_weapon_after.name == "Iron Dagger":
            print("✓ First dagger correctly equipped with smart equipping")
        else:
            print("✗ Smart equipping failed to place first dagger correctly")
            return False
            
    except Exception as e:
        print(f"✗ Test 1 failed: {e}")
        return False
    
    # Test 2: Create second iron dagger and attempt to equip in weapon slot
    print("\n--- Test 2: Second iron dagger to weapon slot (CRITICAL TEST) ---")
    try:
        dagger2 = ItemFactory.create('iron_dagger')
        if not dagger2:
            print("✗ Failed to create second iron dagger")
            return False
            
        # Assign UUID like demo does
        dagger2.uuid = str(uuid.uuid4())
        
        # Add to inventory
        player.inventory.add_item(dagger2)
        print(f"✓ Created and added second dagger to inventory: {dagger2.name} (UUID: {dagger2.uuid})")
        
        # Check dagger properties
        print(f"Dagger properties:")
        print(f"  - slot: {dagger2.slot}")
        print(f"  - slot_restriction: {getattr(dagger2, 'slot_restriction', 'None')}")
        print(f"  - dual_wield: {getattr(dagger2, 'dual_wield', False)}")
        
        # Check current equipment state
        current_weapon = getattr(player, 'weapon', None)
        current_offhand = getattr(player, 'offhand', None)
        print(f"Current state:")
        print(f"  - Weapon: {current_weapon.name if current_weapon else 'None'}")
        print(f"  - Offhand: {current_offhand.name if current_offhand else 'None'}")
        
        # Now simulate the demo's equip logic with validation
        slot = dagger2.slot  # Should be "weapon"
        print(f"Item slot is: {slot}")
        
        if slot == 'weapon':
            # Check if weapon slot is available (should be None)
            if current_weapon is None:
                # Check for reverse dual wield scenario
                if (current_offhand is not None and 
                    hasattr(dagger2, 'dual_wield') and dagger2.dual_wield and
                    hasattr(current_offhand, 'dual_wield') and current_offhand.dual_wield and
                    hasattr(dagger2, 'slot_restriction') and dagger2.slot_restriction == "either_hand"):
                    print("✓ Detected reverse dual wield scenario")
                    slot_available = True
                else:
                    print("✓ Weapon slot available for normal equipping")
                    slot_available = True
            else:
                print("✗ Weapon slot occupied - should not happen in this test")
                return False
                
            if slot_available:
                print("✓ Slot validation passed")
                
                # Try smart equipping (this should work)
                if (hasattr(dagger2, 'dual_wield') and dagger2.dual_wield and 
                    hasattr(dagger2, 'slot_restriction') and dagger2.slot_restriction == "either_hand" and
                    hasattr(player, 'equip_weapon_smart')):
                    print("✓ Using smart equipping for dual wield weapon")
                    success = player.equip_weapon_smart(dagger2)
                    if success:
                        print("✓ Smart equipping succeeded!")
                        
                        # Remove from inventory if still there
                        if dagger2 in player.inventory.list_items():
                            player.inventory.remove_item(dagger2)
                            print("✓ Removed from inventory after equipping")
                        else:
                            print("✓ Already removed from inventory by equip method")
                            
                        # Check final state
                        final_weapon = getattr(player, 'weapon', None)
                        final_offhand = getattr(player, 'offhand', None)
                        print(f"Final state:")
                        print(f"  - Weapon: {final_weapon.name if final_weapon else 'None'}")
                        print(f"  - Offhand: {final_offhand.name if final_offhand else 'None'}")
                        
                        if final_weapon and final_offhand:
                            print("✓ Test 2 PASSED: Dual wield setup successful!")
                            return True
                        else:
                            print("✗ Test 2 FAILED: Final state incorrect")
                            return False
                    else:
                        print("✗ Smart equipping failed")
                        return False
                else:
                    print("✗ Smart equipping not available or conditions not met")
                    return False
            else:
                print("✗ Slot validation failed")
                return False
        else:
            print(f"✗ Unexpected slot: {slot}")
            return False
            
    except Exception as e:
        print(f"✗ Test 2 failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    print("\n" + "="*60)
    print("DEMO SCENARIO TEST FAILED - CHECK ABOVE FOR DETAILS")
    print("="*60)
    return False

if __name__ == "__main__":
    success = test_demo_dual_wield_scenario()
    sys.exit(0 if success else 1)
