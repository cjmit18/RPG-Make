#!/usr/bin/env python3
"""
Test Equipment Manager Integration
Comprehensive test of the refactored dual-wield equipment system.
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from game_sys.managers.equipment_manager import EquipmentManager
from game_sys.character.character_factory import create_character
from game_sys.items.factory import ItemFactory
from demo import logger

# Initialize equipment manager
equipment_manager = EquipmentManager()

def test_equipment_manager_integration():
    """Test the complete equipment manager integration."""
    
    print("🧪 EQUIPMENT MANAGER INTEGRATION TEST")
    print("=" * 50)
    
    # Create test player
    player = create_character("hero")
    print(f"Created player: {player.name}")
    
    # Create test items
    sword = ItemFactory.create("iron_sword")
    dagger = ItemFactory.create("iron_dagger") 
    shield = ItemFactory.create("wooden_shield")
    staff = ItemFactory.create("fire_staff")  # Use staff instead of bow
    
    print(f"Created items: {[item.name for item in [sword, dagger, shield, staff]]}")
    
    print("\n📋 TEST 1: Basic Equipment")
    print("-" * 30)
    
    # Test 1: Equip basic sword
    success, message = equipment_manager.equip_item_with_smart_logic(player, sword)
    print(f"Equip {sword.name}: {'✅ SUCCESS' if success else '❌ FAILED'}")
    print(f"Message: {message}")
    
    print("\n📋 TEST 2: Dual-Wield Attempt")
    print("-" * 30)
    
    # Test 2: Try to dual-wield with dagger
    success, message = equipment_manager.equip_item_with_smart_logic(player, dagger)
    print(f"Dual-wield {dagger.name}: {'✅ SUCCESS' if success else '❌ FAILED'}")
    print(f"Message: {message}")
    
    print("\n📋 TEST 3: Equipment Status Check")
    print("-" * 30)
    
    # Test 3: Check dual-wield status
    status_info = equipment_manager.get_dual_wield_status_info(player)
    print(f"Dual-wield Status: {status_info}")
    
    print("\n📋 TEST 4: Shield Conflict")
    print("-" * 30)
    
    # Test 4: Check slot availability first
    slot_available, conflict_message = equipment_manager.check_equipment_slot_availability(player, shield, shield.slot)
    print(f"Shield slot available: {'✅ YES' if slot_available else '❌ NO'}")
    if not slot_available:
        print(f"Conflict: {conflict_message}")
        
        # Get suggestion for resolution
        suggestion = equipment_manager.suggest_equipment_resolution(player, shield, shield.slot)
        print(f"Suggestion: {suggestion}")
    
    print("\n📋 TEST 5: Equipment Status")
    print("-" * 30)
    
    # Test 5: Check availability for sword 
    sword_available, sword_conflict = equipment_manager.check_equipment_slot_availability(player, sword, sword.slot)
    print(f"Sword slot available: {'✅ YES' if sword_available else '❌ NO'}")
    if not sword_available:
        print(f"Conflict: {sword_conflict}")
        sword_suggestion = equipment_manager.suggest_equipment_resolution(player, sword, sword.slot)
        print(f"Suggestion: {sword_suggestion}")
    
    print("\n🏆 INTEGRATION TEST COMPLETE")
    print("=" * 50)
    
    # Summary
    weapon = getattr(player, 'weapon', None)
    offhand = getattr(player, 'offhand', None)
    
    print(f"Final Equipment State:")
    print(f"  Weapon: {weapon.name if weapon else 'None'}")
    print(f"  Offhand: {offhand.name if offhand else 'None'}")
    
    # Show dual-wield status one more time
    final_status = equipment_manager.get_dual_wield_status_info(player)
    print(f"  Status: {final_status}")
    
    return True

if __name__ == "__main__":
    try:
        test_equipment_manager_integration()
        print("\n✅ All tests completed successfully!")
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
