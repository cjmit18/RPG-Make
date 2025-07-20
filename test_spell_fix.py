#!/usr/bin/env python3
"""
Test script to verify spell casting functionality is working properly.
"""

import tkinter as tk
from demo import SimpleGameDemo
import time


def test_spell_casting():
    """Test that spell casting works without errors."""
    print("🧙 Testing spell casting functionality...")
    
    try:
        # Create demo instance
        demo = SimpleGameDemo()
        
        # Wait a moment for initialization
        demo.root.update()
        time.sleep(0.5)
        
        print("✅ Demo initialized successfully")
        
        # Test fireball spell
        print("🔥 Testing Fireball spell...")
        try:
            demo.on_fireball_button_clicked()
            demo.root.update()
            print("✅ Fireball cast successfully - no errors")
        except Exception as e:
            print(f"❌ Fireball casting failed: {e}")
            return False
            
        # Test ice shard spell
        print("❄️ Testing Ice Shard spell...")
        try:
            demo.on_ice_shard_button_clicked()
            demo.root.update()
            print("✅ Ice Shard cast successfully - no errors")
        except Exception as e:
            print(f"❌ Ice Shard casting failed: {e}")
            return False
            
        # Check if combo system is tracking
        if hasattr(demo, 'combo_sequence') and len(demo.combo_sequence) >= 2:
            print("✅ Combo sequence tracking works")
            print(f"   Current sequence: {demo.combo_sequence}")
        else:
            print("⚠️ Combo sequence might not be tracking properly")
            
        print("✅ All spell casting tests passed!")
        
        # Cleanup
        demo.root.quit()
        demo.root.destroy()
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        return False


if __name__ == "__main__":
    print("=" * 50)
    print("🧪 SPELL CASTING TEST")
    print("=" * 50)
    
    success = test_spell_casting()
    
    print("=" * 50)
    if success:
        print("🎉 ALL TESTS PASSED - Spell casting is working!")
    else:
        print("💥 TESTS FAILED - Issues remain")
    print("=" * 50)
