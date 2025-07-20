#!/usr/bin/env python3
"""
Test script to verify combat tab fixes
"""

import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_combat_canvas_fix():
    """Test that canvas widget is properly retrieved from UI service."""
    print("Testing combat canvas fix...")
    
    # Import demo class
    from demo import SimpleGameDemo
    
    try:
        # Create demo instance
        print("Creating demo instance...")
        demo = SimpleGameDemo()
        
        # Check if canvas is available
        if hasattr(demo, 'canvas') and demo.canvas:
            print("✅ Canvas widget successfully retrieved from UI service")
        else:
            print("❌ Canvas widget not available")
            return False
            
        # Check if enemy_info is available
        if hasattr(demo, 'enemy_info') and demo.enemy_info:
            print("✅ Enemy info widget successfully retrieved from UI service")
        else:
            print("❌ Enemy info widget not available")
            return False
            
        # Test draw_game_state method (should not crash)
        try:
            demo.draw_game_state()
            print("✅ draw_game_state() executed without errors")
        except Exception as e:
            print(f"❌ draw_game_state() failed: {e}")
            return False
            
        # Test attack button callback (should not crash)
        try:
            demo.on_attack_button_clicked()
            print("✅ Attack button callback executed without canvas errors")
        except AttributeError as e:
            if "'SimpleGameDemo' object has no attribute 'canvas'" in str(e):
                print(f"❌ Canvas error still present: {e}")
                return False
            else:
                print(f"⚠️ Attack failed for other reason: {e}")
        except Exception as e:
            print(f"⚠️ Attack failed (expected - no combat setup): {e}")
            
        print("🎉 Combat canvas fix verification completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Demo initialization failed: {e}")
        return False
    finally:
        # Clean up - destroy the demo window
        try:
            if 'demo' in locals() and hasattr(demo, 'root'):
                demo.root.destroy()
        except:
            pass

if __name__ == "__main__":
    success = test_combat_canvas_fix()
    sys.exit(0 if success else 1)
