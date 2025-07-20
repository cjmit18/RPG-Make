#!/usr/bin/env python3
"""
Quick test of the enhanced dual-wield equipment system.
This script tests all the new dual-wield logic improvements.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from demo import SimpleGameDemo
import tkinter as tk

def test_equipment_logic():
    """Test the enhanced dual-wield equipment logic without UI."""
    print("=== Testing Enhanced Dual-Wield Equipment System ===")
    
    # Create a minimal demo instance for testing
    root = tk.Tk()
    root.withdraw()  # Hide the window
    
    try:
        demo = SimpleGameDemo()
        demo.setup_game_state()
        
        if not demo.player:
            print("❌ Failed to create player")
            return
            
        print(f"✅ Player created: {demo.player.name}")
        
        # Test the dual-wield status checker
        status = demo._get_dual_wield_status_info()
        print(f"📊 Current weapon status: {status}")
        
        # Create test items
        from game_sys.items.factory import ItemFactory
        
        # Test dual-wieldable weapons
        iron_dagger = ItemFactory.create('iron_dagger')
        dagger = ItemFactory.create('dagger')
        dragon_tooth_dagger = ItemFactory.create('dragon_tooth_dagger')
        
        # Test two-handed weapons
        fire_staff = ItemFactory.create('fire_staff')
        arcane_staff = ItemFactory.create('arcane_staff')
        
        # Test shields/focuses
        wooden_shield = ItemFactory.create('wooden_shield')
        spell_focus = ItemFactory.create('spell_focus')
        
        test_items = {
            'iron_dagger': iron_dagger,
            'dagger': dagger,
            'dragon_tooth_dagger': dragon_tooth_dagger,
            'fire_staff': fire_staff,
            'arcane_staff': arcane_staff,
            'wooden_shield': wooden_shield,
            'spell_focus': spell_focus
        }
        
        print("\n--- Created Test Items ---")
        for name, item in test_items.items():
            if item:
                dual_wield = getattr(item, 'dual_wield', False)
                two_handed = getattr(item, 'two_handed', False)
                slot_restriction = getattr(item, 'slot_restriction', 'none')
                print(f"✅ {item.name}: dual_wield={dual_wield}, two_handed={two_handed}, restriction={slot_restriction}")
            else:
                print(f"❌ Failed to create {name}")
        
        # Test slot availability checking
        print("\n--- Testing Slot Availability Logic ---")
        
        if iron_dagger:
            slot_available, conflict_msg = demo._check_equipment_slot_availability(iron_dagger, 'weapon')
            print(f"🗡️ Iron Dagger -> weapon slot: Available={slot_available}, Conflict='{conflict_msg}'")
            
        if wooden_shield:
            slot_available, conflict_msg = demo._check_equipment_slot_availability(wooden_shield, 'offhand')
            print(f"🛡️ Wooden Shield -> offhand slot: Available={slot_available}, Conflict='{conflict_msg}'")
            
        if fire_staff:
            slot_available, conflict_msg = demo._check_equipment_slot_availability(fire_staff, 'weapon')
            print(f"🔥 Fire Staff -> weapon slot: Available={slot_available}, Conflict='{conflict_msg}'")
        
        # Test dual-wield suggestions
        print("\n--- Testing Dual-Wield Suggestions ---")
        
        if iron_dagger:
            suggestion = demo._suggest_dual_wield_alternative(iron_dagger, 'weapon')
            print(f"💡 Iron Dagger suggestion: {suggestion}")
            
        print("\n✅ Equipment system test completed successfully!")
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        root.destroy()

if __name__ == "__main__":
    test_equipment_logic()
