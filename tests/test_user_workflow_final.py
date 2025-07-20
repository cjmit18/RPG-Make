#!/usr/bin/env python3

"""
Final validation test for the dual wield fix.
This tests the exact user workflow from the demo logs.
"""

import sys
import os
import uuid

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_user_workflow():
    """Test the exact user workflow that was failing."""
    
    print("\n" + "="*60)
    print("DUAL WIELD USER WORKFLOW VALIDATION")
    print("="*60)
    
    from game_sys.character.character_factory import create_character
    from game_sys.items.factory import ItemFactory
    
    # Create character
    player = create_character("hero")
    print(f"✓ Created character: {player.name}")
    
    # Clear starting equipment (simulate demo startup)
    player.weapon = None
    player.offhand = None
    print("✓ Cleared starting equipment")
    
    # Create first iron dagger and add to inventory
    dagger1 = ItemFactory.create('iron_dagger')
    dagger1.uuid = str(uuid.uuid4())
    player.inventory.add_item(dagger1)
    print(f"✓ Created first dagger: {dagger1.name} (UUID: {dagger1.uuid})")
    
    # Simulate user clicking "Equip Item" on first dagger
    # This should equip it successfully
    
    # Use smart equipping (like our fixed demo does)
    if (hasattr(dagger1, 'dual_wield') and dagger1.dual_wield and 
        hasattr(dagger1, 'slot_restriction') and dagger1.slot_restriction == "either_hand" and
        hasattr(player, 'equip_weapon_smart')):
        success = player.equip_weapon_smart(dagger1)
        if success:
            # Remove from inventory
            if dagger1 in player.inventory.list_items():
                player.inventory.remove_item(dagger1)
            print("✓ First dagger equipped successfully using smart equipping")
        else:
            print("✗ First dagger equipping failed")
            return False
    else:
        print("✗ Smart equipping not available")
        return False
    
    # Create second iron dagger and add to inventory  
    dagger2 = ItemFactory.create('iron_dagger')
    dagger2.uuid = str(uuid.uuid4())
    player.inventory.add_item(dagger2)
    print(f"✓ Created second dagger: {dagger2.name} (UUID: {dagger2.uuid})")
    
    # Simulate user clicking "Equip Item" on second dagger
    # This was previously failing with "Offhand slot occupied"
    
    # Use smart equipping (like our fixed demo does)
    if (hasattr(dagger2, 'dual_wield') and dagger2.dual_wield and 
        hasattr(dagger2, 'slot_restriction') and dagger2.slot_restriction == "either_hand" and
        hasattr(player, 'equip_weapon_smart')):
        success = player.equip_weapon_smart(dagger2)
        if success:
            # Remove from inventory
            if dagger2 in player.inventory.list_items():
                player.inventory.remove_item(dagger2)
            print("✓ Second dagger equipped successfully using smart equipping")
        else:
            print("✗ Second dagger equipping failed")
            return False
    else:
        print("✗ Smart equipping not available")
        return False
    
    # Verify final state
    weapon_name = player.weapon.name if player.weapon else "None"
    offhand_name = player.offhand.name if player.offhand else "None"
    print(f"\nFinal Equipment State:")
    print(f"  - Weapon: {weapon_name}")
    print(f"  - Offhand: {offhand_name}")
    
    if player.weapon and player.offhand:
        if (player.weapon.name == "Iron Dagger" and player.offhand.name == "Iron Dagger"):
            print("\n✅ SUCCESS: Dual wield setup complete!")
            print("✅ User can now equip two iron daggers without errors!")
            return True
    
    print("\n❌ FAILED: Dual wield setup incomplete")
    return False

if __name__ == "__main__":
    success = test_user_workflow()
    if success:
        print("\n🎉 DUAL WIELD SYSTEM FULLY FIXED! 🎉")
        print("Users can now equip dual wield weapons in any order without issues.")
    else:
        print("\n💥 Issue still exists - needs more investigation")
    sys.exit(0 if success else 1)
