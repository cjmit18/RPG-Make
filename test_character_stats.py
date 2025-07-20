#!/usr/bin/env python3
"""
Test script to verify character stats display is working properly with actual data.
"""

import tkinter as tk
from demo import SimpleGameDemo
import time


def test_character_stats_display():
    """Test that character stats display shows actual character data."""
    print("📊 Testing character stats display...")
    
    try:
        # Create demo instance
        demo = SimpleGameDemo()
        
        # Wait a moment for initialization
        demo.root.update()
        time.sleep(1.0)
        
        print("✅ Demo initialized successfully")
        
        # Check if player exists and has stats
        if not hasattr(demo, 'player') or not demo.player:
            print("❌ No player character found")
            return False
            
        player = demo.player
        print(f"✅ Player character found: {player.name}")
        
        # Check if player has required attributes
        required_attrs = ['level', 'current_health', 'max_health', 'base_stats']
        missing_attrs = []
        for attr in required_attrs:
            if not hasattr(player, attr):
                missing_attrs.append(attr)
                
        if missing_attrs:
            print(f"⚠️ Player missing attributes: {missing_attrs}")
        else:
            print("✅ Player has all required attributes")
            
        # Check base stats
        if hasattr(player, 'base_stats') and player.base_stats:
            print(f"✅ Player has {len(player.base_stats)} base stats:")
            for stat_name, value in list(player.base_stats.items())[:5]:  # Show first 5
                print(f"   - {stat_name}: {value}")
        else:
            print("❌ Player missing base_stats")
            return False
            
        # Test character info building methods
        print("🔧 Testing character info building methods...")
        
        try:
            basic_info = demo._build_basic_character_info()
            if basic_info and len(basic_info) > 50:  # Reasonable length check
                print("✅ Basic character info generation works")
                print(f"   Preview: {basic_info[:100]}...")
            else:
                print("❌ Basic character info generation failed or too short")
                return False
        except Exception as e:
            print(f"❌ Basic character info generation error: {e}")
            return False
            
        try:
            detailed_info = demo._build_detailed_character_info()
            if detailed_info and len(detailed_info) > 100:  # Reasonable length check
                print("✅ Detailed character info generation works")
                print(f"   Preview: {detailed_info[:100]}...")
            else:
                print("❌ Detailed character info generation failed or too short")
                return False
        except Exception as e:
            print(f"❌ Detailed character info generation error: {e}")
            return False
            
        # Test status effects (optional)
        try:
            status_info = demo._build_status_effects_info()
            print("✅ Status effects info generation works")
            print(f"   Status: {status_info[:50]}...")
        except Exception as e:
            print(f"⚠️ Status effects generation error (non-critical): {e}")
            
        # Test character display update
        print("🎨 Testing character display update...")
        try:
            demo._update_character_display_enhanced()
            print("✅ Character display update completed")
        except Exception as e:
            print(f"❌ Character display update error: {e}")
            return False
            
        # Test equipment display
        print("⚔️ Testing equipment display...")
        try:
            # Check if player has any equipment
            equipment_found = False
            equipment_slots = ['weapon', 'offhand', 'equipped_body', 'equipped_helmet', 'equipped_feet']
            
            for slot in equipment_slots:
                item = getattr(player, slot, None)
                if item:
                    print(f"   - {slot}: {getattr(item, 'name', 'Unknown')}")
                    equipment_found = True
                    
            if equipment_found:
                print("✅ Equipment data found")
            else:
                print("⚠️ No equipment found (player may be unequipped)")
                
            # Test equipment display update
            if hasattr(demo, '_update_equipment_slots_display'):
                demo._update_equipment_slots_display()
                print("✅ Equipment display update completed")
            else:
                print("⚠️ Equipment display update method not found")
                
        except Exception as e:
            print(f"⚠️ Equipment display error (non-critical): {e}")
            
        print("✅ Character stats display tests completed successfully!")
        
        # Cleanup
        demo.root.quit()
        demo.root.destroy()
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        return False


if __name__ == "__main__":
    print("=" * 60)
    print("🧪 CHARACTER STATS DISPLAY TEST")
    print("=" * 60)
    
    success = test_character_stats_display()
    
    print("=" * 60)
    if success:
        print("🎉 ALL TESTS PASSED - Character stats display working correctly!")
    else:
        print("💥 TESTS FAILED - Character stats display has issues")
    print("=" * 60)
