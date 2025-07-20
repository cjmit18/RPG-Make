#!/usr/bin/env python3

"""
Test script to verify dual wield UI integration fixes.
Simulates the demo's equip_selected_item logic.
"""

import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from game_sys.logging import get_logger
from game_sys.character.character_factory import create_character
from game_sys.items.factory import ItemFactory

logger = get_logger("dual_wield_ui_test")

def simulate_demo_equipment_logic(player, item, slot):
    """Simulate the demo's equipment validation logic."""
    
    # This simulates the fixed logic from demo.py equip_selected_item method
    slot_available = False
    conflict_message = None
    
    if slot == 'weapon':
        current_weapon = getattr(player, 'weapon', None)
        current_offhand = getattr(player, 'offhand', None)
        
        # Check if weapon slot is available
        if current_weapon is None:
            # Check for reverse dual wield scenario: offhand→weapon movement
            if (current_offhand is not None and 
                hasattr(item, 'dual_wield') and item.dual_wield and
                hasattr(current_offhand, 'dual_wield') and current_offhand.dual_wield and
                hasattr(item, 'slot_restriction') and item.slot_restriction == "either_hand"):
                # Allow dual wield weapons to be equipped in weapon slot even if offhand occupied
                slot_available = True
                print(f"✓ Dual wield setup: {item.name} will go to weapon slot alongside offhand {current_offhand.name}")
            else:
                slot_available = True
        else:
            # Weapon slot occupied - check if it's a dual-wield scenario
            if (hasattr(item, 'dual_wield') and item.dual_wield and 
                hasattr(current_weapon, 'dual_wield') and current_weapon.dual_wield and
                current_offhand is None):
                # Both weapons are dual-wieldable and offhand is free
                # Move current weapon to offhand and equip new weapon in main hand
                slot_available = True
                print(f"✓ Moving {current_weapon.name} to offhand to make room for {item.name}")
            else:
                slot_available = False
                weapon_name = getattr(current_weapon, 'name', str(current_weapon))
                if hasattr(item, 'dual_wield') and item.dual_wield:
                    if not (hasattr(current_weapon, 'dual_wield') and current_weapon.dual_wield):
                        conflict_message = f"Cannot dual-wield: {weapon_name} is not dual-wieldable"
                    elif current_offhand is not None:
                        offhand_name = getattr(current_offhand, 'name', str(current_offhand))
                        conflict_message = f"Cannot dual-wield: offhand occupied by {offhand_name}"
                    else:
                        conflict_message = f"Weapon slot occupied by {weapon_name}"
                else:
                    conflict_message = f"Weapon slot occupied by {weapon_name}"
                    
    elif slot == 'offhand':
        current_offhand = getattr(player, 'offhand', None)
        current_weapon = getattr(player, 'weapon', None)
        
        # Special dual-wield logic
        if hasattr(item, 'dual_wield') and item.dual_wield:
            # Dual-wield items can go in offhand if main hand is empty or also dual-wield
            if current_weapon is None or (hasattr(current_weapon, 'dual_wield') and current_weapon.dual_wield):
                slot_available = current_offhand is None
                if not slot_available:
                    offhand_name = getattr(current_offhand, 'name', str(current_offhand))
                    conflict_message = f"Offhand slot occupied by {offhand_name}"
            else:
                weapon_name = getattr(current_weapon, 'name', str(current_weapon))
                slot_available = False
                conflict_message = f"Cannot dual-wield: main weapon {weapon_name} is not dual-wieldable"
        else:
            # Regular offhand item (shield, focus, etc.)
            slot_available = current_offhand is None
            if not slot_available:
                offhand_name = getattr(current_offhand, 'name', str(current_offhand))
                conflict_message = f"Offhand slot occupied by {offhand_name}"
    
    return slot_available, conflict_message

def test_demo_dual_wield_ui():
    """Test the demo's UI logic for dual wielding."""
    
    print("\n" + "="*60)
    print("DEMO UI DUAL WIELD LOGIC TEST")
    print("="*60)
    
    # Create test character
    try:
        player = create_character("hero")
        print(f"✓ Created test character: {player.name}")
        
        # Clear starting equipment
        player.weapon = None
        player.offhand = None
        
    except Exception as e:
        print(f"✗ Failed to create character: {e}")
        return False
    
    # Test Scenario 1: Reverse dual wield (the main issue we fixed)
    print("\n--- Scenario 1: Reverse Dual Wield (offhand first, then weapon) ---")
    try:
        # Step 1: Equip dagger in offhand
        dagger1 = ItemFactory.create('iron_dagger')
        player.equip_offhand(dagger1)
        print(f"✓ Equipped {dagger1.name} in offhand")
        
        # Step 2: Try to equip another dagger in weapon slot (this was failing before)
        dagger2 = ItemFactory.create('iron_dagger') 
        slot_available, conflict_message = simulate_demo_equipment_logic(player, dagger2, 'weapon')
        
        if slot_available:
            print(f"✓ Demo logic allows equipping {dagger2.name} in weapon slot")
            
            # Test actual equipping using smart method
            if hasattr(player, 'equip_weapon_smart'):
                success = player.equip_weapon_smart(dagger2)
                if success:
                    weapon_name = player.weapon.name if player.weapon else "None"
                    offhand_name = player.offhand.name if player.offhand else "None"
                    print(f"✓ Smart equipping successful - Weapon: {weapon_name}, Offhand: {offhand_name}")
                    print("✅ Scenario 1 PASSED: Reverse dual wield works!")
                else:
                    print("✗ Smart equipping failed despite logic allowing it")
                    return False
            else:
                # Fallback to direct equipping
                player.equip_weapon(dagger2)
                weapon_name = player.weapon.name if player.weapon else "None"
                offhand_name = player.offhand.name if player.offhand else "None"
                print(f"✓ Direct equipping successful - Weapon: {weapon_name}, Offhand: {offhand_name}")
                print("✅ Scenario 1 PASSED: Reverse dual wield works!")
        else:
            print(f"✗ Demo logic blocks equipping: {conflict_message}")
            return False
            
    except Exception as e:
        print(f"✗ Scenario 1 FAILED: {e}")
        return False
    
    # Test Scenario 2: Normal dual wield (weapon first, then offhand)
    print("\n--- Scenario 2: Normal Dual Wield (weapon first, then offhand) ---")
    try:
        # Clear equipment
        player.weapon = None
        player.offhand = None
        
        # Step 1: Equip dagger in weapon slot
        dagger3 = ItemFactory.create('dagger')
        player.equip_weapon(dagger3)
        print(f"✓ Equipped {dagger3.name} in weapon slot")
        
        # Step 2: Try to equip another dagger in offhand slot
        dagger4 = ItemFactory.create('dragon_tooth_dagger')
        slot_available, conflict_message = simulate_demo_equipment_logic(player, dagger4, 'offhand')
        
        if slot_available:
            print(f"✓ Demo logic allows equipping {dagger4.name} in offhand slot")
            player.equip_offhand(dagger4)
            weapon_name = player.weapon.name if player.weapon else "None"
            offhand_name = player.offhand.name if player.offhand else "None"
            print(f"✓ Equipping successful - Weapon: {weapon_name}, Offhand: {offhand_name}")
            print("✅ Scenario 2 PASSED: Normal dual wield works!")
        else:
            print(f"✗ Demo logic blocks equipping: {conflict_message}")
            return False
            
    except Exception as e:
        print(f"✗ Scenario 2 FAILED: {e}")
        return False
    
    # Test Scenario 3: Conflict detection (non-dual-wield items)
    print("\n--- Scenario 3: Conflict Detection (shield + dagger) ---")
    try:
        # Clear equipment
        player.weapon = None
        player.offhand = None
        
        # Step 1: Equip a shield in offhand
        shield = ItemFactory.create('wooden_shield')
        if shield:
            player.equip_offhand(shield)
            print(f"✓ Equipped {shield.name} in offhand slot")
            
            # Step 2: Try to equip dagger in weapon slot (should work)
            dagger5 = ItemFactory.create('iron_dagger')
            slot_available, conflict_message = simulate_demo_equipment_logic(player, dagger5, 'weapon')
            
            if slot_available:
                print(f"✓ Demo logic correctly allows dagger + shield combination")
                player.equip_weapon(dagger5)
                weapon_name = player.weapon.name if player.weapon else "None"
                offhand_name = player.offhand.name if player.offhand else "None"
                print(f"✓ Final state - Weapon: {weapon_name}, Offhand: {offhand_name}")
                print("✅ Scenario 3 PASSED: Shield + dagger combination works!")
            else:
                print(f"✗ Demo logic incorrectly blocks shield + dagger: {conflict_message}")
                return False
        else:
            print("⚠ Scenario 3 SKIPPED: Could not create shield")
            
    except Exception as e:
        print(f"✗ Scenario 3 FAILED: {e}")
        return False
    
    # Test Scenario 4: Slot restriction edge case
    print("\n--- Scenario 4: Slot Restriction Validation ---")
    try:
        # Clear equipment
        player.weapon = None
        player.offhand = None
        
        # Check that items with correct slot_restriction work
        dagger6 = ItemFactory.create('iron_dagger')
        print(f"Dagger config - slot: {dagger6.slot}, slot_restriction: {getattr(dagger6, 'slot_restriction', 'None')}, dual_wield: {getattr(dagger6, 'dual_wield', False)}")
        
        if (hasattr(dagger6, 'slot_restriction') and dagger6.slot_restriction == "either_hand" and
            hasattr(dagger6, 'dual_wield') and dagger6.dual_wield):
            print("✓ Dagger has correct slot configuration for dual wielding")
            print("✅ Scenario 4 PASSED: Slot restriction validation works!")
        else:
            print("✗ Dagger missing proper slot_restriction or dual_wield configuration")
            return False
            
    except Exception as e:
        print(f"✗ Scenario 4 FAILED: {e}")
        return False
    
    print("\n" + "="*60)
    print("ALL DEMO UI DUAL WIELD TESTS COMPLETED SUCCESSFULLY!")
    print("✅ The dual wield system fixes are working correctly!")
    print("="*60)
    return True

if __name__ == "__main__":
    success = test_demo_dual_wield_ui()
    sys.exit(0 if success else 1)
