#!/usr/bin/env python3

"""
Test script to verify dual wield system fixes work through the demo UI.
Tests inventory management and dual wield equipment scenarios.
"""

import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from game_sys.logging import get_logger
from game_sys.character.character_factory import create_character
from game_sys.items.factory import ItemFactory

logger = get_logger("dual_wield_demo_test")

def test_dual_wield_through_inventory():
    """Test dual wield system through inventory management like the demo does."""
    
    print("\n" + "="*60)
    print("DUAL WIELD DEMO INVENTORY INTEGRATION TEST")
    print("="*60)
    
    # Create a test character
    try:
        player = create_character("hero")
        print(f"✓ Created test character: {player.name}")
    except Exception as e:
        print(f"✗ Failed to create character: {e}")
        return False
    
    # Test 1: Create and add items to inventory (like demo does)
    print("\n--- Test 1: Create items and add to inventory ---")
    try:
        dagger1 = ItemFactory.create('iron_dagger')
        dagger2 = ItemFactory.create('iron_dagger')
        
        if not dagger1 or not dagger2:
            print("✗ Failed to create daggers")
            return False
            
        # Assign UUIDs like the demo does
        import uuid
        dagger1.uuid = str(uuid.uuid4())
        dagger2.uuid = str(uuid.uuid4())
        
        # Add to inventory
        success1 = player.inventory.add_item(dagger1)
        success2 = player.inventory.add_item(dagger2)
        
        if success1 and success2:
            print(f"✓ Added two daggers to inventory with UUIDs:")
            print(f"  - {dagger1.name} (UUID: {dagger1.uuid[:8]}...)")
            print(f"  - {dagger2.name} (UUID: {dagger2.uuid[:8]}...)")
        else:
            print("✗ Failed to add daggers to inventory")
            return False
            
    except Exception as e:
        print(f"✗ Test 1 FAILED: {e}")
        return False
    
    # Test 2: Simulate demo's equip_selected_item logic
    print("\n--- Test 2: Simulate demo equipment logic ---")
    try:
        # Get items from inventory (like demo does)
        items = player.inventory.list_items()
        print(f"Items in inventory: {len(items)}")
        
        # Equip first dagger in offhand
        item1 = items[0]
        slot1 = getattr(item1, 'slot', None)
        print(f"First item slot: {slot1}, dual_wield: {getattr(item1, 'dual_wield', False)}")
        
        # Simulate demo logic for offhand equipment
        if slot1 == 'weapon' and hasattr(item1, 'dual_wield') and item1.dual_wield:
            # Use smart equipping for dual wield weapons
            if hasattr(player, 'equip_weapon_smart'):
                success = player.equip_weapon_smart(item1)
                if success:
                    print(f"✓ Smart equipped {item1.name} successfully")
                    
                    # Check if item is still in inventory before removing (like our fix)
                    if item1 in player.inventory.list_items():
                        removal_success = player.inventory.remove_item(item1)
                        print(f"✓ Removed {item1.name} from inventory: {removal_success}")
                    else:
                        print(f"✓ {item1.name} already removed from inventory by equipment method")
                else:
                    print(f"✗ Failed to smart equip {item1.name}")
                    return False
            else:
                print("⚠ Smart equipping not available, using fallback")
                player.equip_offhand(item1)
                if item1 in player.inventory.list_items():
                    player.inventory.remove_item(item1)
                    
        # Now equip second dagger
        items = player.inventory.list_items()  # Refresh list
        if len(items) > 0:
            item2 = items[0]  # Should be the second dagger
            
            # Check current equipment state
            current_weapon = getattr(player, 'weapon', None)
            current_offhand = getattr(player, 'offhand', None)
            
            print(f"Current state - Weapon: {current_weapon.name if current_weapon else 'None'}")
            print(f"Current state - Offhand: {current_offhand.name if current_offhand else 'None'}")
            
            # Try to equip second dagger using smart equipping
            if hasattr(player, 'equip_weapon_smart'):
                success = player.equip_weapon_smart(item2)
                if success:
                    print(f"✓ Smart equipped second {item2.name} successfully")
                    
                    # Check if item is still in inventory before removing (like our fix)
                    if item2 in player.inventory.list_items():
                        removal_success = player.inventory.remove_item(item2)
                        print(f"✓ Removed {item2.name} from inventory: {removal_success}")
                    else:
                        print(f"✓ {item2.name} already removed from inventory by equipment method")
                        
                    print("✓ Test 2 PASSED: Dual wield setup successful through demo logic")
                else:
                    print(f"✗ Test 2 FAILED: Failed to smart equip second dagger")
                    return False
            else:
                print("✗ Test 2 FAILED: Smart equipping not available")
                return False
        else:
            print("✗ Test 2 FAILED: No second item available")
            return False
            
    except Exception as e:
        print(f"✗ Test 2 FAILED: {e}")
        return False
    
    # Test 3: Verify final dual wield state
    print("\n--- Test 3: Verify final dual wield state ---")
    try:
        final_weapon = getattr(player, 'weapon', None)
        final_offhand = getattr(player, 'offhand', None)
        final_inventory = player.inventory.list_items()
        
        print(f"Final weapon: {final_weapon.name if final_weapon else 'None'}")
        print(f"Final offhand: {final_offhand.name if final_offhand else 'None'}")
        print(f"Items remaining in inventory: {len(final_inventory)}")
        
        # Check that both slots are occupied by daggers
        weapon_is_dagger = final_weapon and 'dagger' in final_weapon.name.lower()
        offhand_is_dagger = final_offhand and 'dagger' in final_offhand.name.lower()
        inventory_empty_of_daggers = not any('dagger' in item.name.lower() for item in final_inventory)
        
        if weapon_is_dagger and offhand_is_dagger and inventory_empty_of_daggers:
            print("✓ Test 3 PASSED: Perfect dual wield setup achieved")
            print("  - Both weapon and offhand have daggers")
            print("  - No daggers left in inventory (properly removed)")
        else:
            print("✗ Test 3 FAILED: Dual wield state not as expected")
            return False
            
    except Exception as e:
        print(f"✗ Test 3 FAILED: {e}")
        return False
    
    # Test 4: Test reverse scenario (weapon first, then offhand)
    print("\n--- Test 4: Test reverse scenario (weapon → offhand) ---")
    try:
        # Clear equipment
        player.weapon = None
        player.offhand = None
        
        # Add two more daggers to inventory
        dagger3 = ItemFactory.create('dagger')
        dagger4 = ItemFactory.create('dragon_tooth_dagger')
        dagger3.uuid = str(uuid.uuid4())
        dagger4.uuid = str(uuid.uuid4())
        
        player.inventory.add_item(dagger3)
        player.inventory.add_item(dagger4)
        
        # Equip weapon slot first
        items = player.inventory.list_items()
        weapon_item = items[0]
        
        if hasattr(player, 'equip_weapon_smart'):
            success = player.equip_weapon_smart(weapon_item)
            if success:
                print(f"✓ Equipped {weapon_item.name} in weapon slot first")
                if weapon_item in player.inventory.list_items():
                    player.inventory.remove_item(weapon_item)
                    
                # Now equip offhand
                items = player.inventory.list_items()
                if len(items) > 0:
                    offhand_item = items[0]
                    success2 = player.equip_weapon_smart(offhand_item)
                    if success2:
                        print(f"✓ Equipped {offhand_item.name} in available slot")
                        if offhand_item in player.inventory.list_items():
                            player.inventory.remove_item(offhand_item)
                            
                        # Verify final state
                        final_weapon = getattr(player, 'weapon', None)
                        final_offhand = getattr(player, 'offhand', None)
                        
                        if final_weapon and final_offhand:
                            print(f"✓ Test 4 PASSED: Reverse dual wield successful")
                            print(f"  - Weapon: {final_weapon.name}")
                            print(f"  - Offhand: {final_offhand.name}")
                        else:
                            print("✗ Test 4 FAILED: Reverse dual wield incomplete")
                            return False
                    else:
                        print("✗ Test 4 FAILED: Second item equip failed")
                        return False
                else:
                    print("✗ Test 4 FAILED: No second item available")
                    return False
            else:
                print("✗ Test 4 FAILED: First item equip failed")
                return False
        else:
            print("⚠ Test 4 SKIPPED: Smart equipping not available")
            
    except Exception as e:
        print(f"✗ Test 4 FAILED: {e}")
        return False
    
    print("\n" + "="*60)
    print("ALL DUAL WIELD DEMO INTEGRATION TESTS PASSED!")
    print("The inventory management fix successfully prevents double removal!")
    print("="*60)
    return True

if __name__ == "__main__":
    success = test_dual_wield_through_inventory()
    sys.exit(0 if success else 1)
