#!/usr/bin/env python3
"""
Comprehensive test to verify all the demo fixes are working correctly.
"""

import sys
import os

# Add the current directory to the path
sys.path.insert(0, os.path.dirname(__file__))

from demo import SimpleGameDemo

def test_comprehensive_functionality():
    print("🔬 Running comprehensive demo functionality test...", flush=True)
    success_count = 0
    total_tests = 0
    
    try:
        # Create a SimpleGameDemo instance
        demo = SimpleGameDemo()
        print("✅ Demo instance created successfully", flush=True)
        total_tests += 1
        success_count += 1
        
        # Test 1: Player exists and has inventory
        if hasattr(demo, 'player') and demo.player:
            print(f"✅ Player exists: {demo.player.name}", flush=True)
            total_tests += 1
            success_count += 1
            
            if hasattr(demo.player, 'inventory'):
                print("✅ Player has inventory system", flush=True)
                total_tests += 1
                success_count += 1
            else:
                print("❌ Player missing inventory system", flush=True)
                total_tests += 1
        else:
            print("❌ No player character found", flush=True)
            total_tests += 1
            
        # Test 2: Enemy exists 
        if hasattr(demo, 'enemy') and demo.enemy:
            print(f"✅ Enemy exists: {demo.enemy.name}", flush=True)
            total_tests += 1
            success_count += 1
        else:
            print("❌ No enemy character found", flush=True)
            total_tests += 1
            
        # Test 3: Combat service exists
        if hasattr(demo, 'combat_service') and demo.combat_service:
            print("✅ Combat service initialized", flush=True)
            total_tests += 1
            success_count += 1
        else:
            print("❌ Combat service missing", flush=True)
            total_tests += 1
            
        # Test 4: Core methods exist and are callable
        critical_methods = [
            'cast_fireball', 'cast_ice_shard', 'view_inventory', 
            'level_up', 'draw_game_state', 'update_char_info'
        ]
        
        for method_name in critical_methods:
            if hasattr(demo, method_name) and callable(getattr(demo, method_name)):
                print(f"✅ Method {method_name} exists and is callable", flush=True)
                total_tests += 1
                success_count += 1
            else:
                print(f"❌ Method {method_name} missing or not callable", flush=True)
                total_tests += 1
                
        # Test 5: Test view_inventory doesn't error
        try:
            # This should not raise an error anymore
            demo.view_inventory()
            print("✅ view_inventory() executes without error", flush=True)
            total_tests += 1
            success_count += 1
        except Exception as e:
            print(f"❌ view_inventory() failed: {e}", flush=True)
            total_tests += 1
            
        # Test 6: Check if draw_game_state has required variables
        try:
            demo.draw_game_state()
            print("✅ draw_game_state() executes without error", flush=True)
            total_tests += 1
            success_count += 1
        except Exception as e:
            print(f"❌ draw_game_state() failed: {e}", flush=True)
            total_tests += 1
            
        print("\n" + "="*50, flush=True)
        print(f"📊 Test Results: {success_count}/{total_tests} tests passed", flush=True)
        
        if success_count == total_tests:
            print("🎉 ALL TESTS PASSED! Demo is fully functional!", flush=True)
            return True
        else:
            print(f"⚠️  {total_tests - success_count} test(s) failed", flush=True)
            return False
            
    except Exception as e:
        print(f"💥 Critical error during testing: {e}", flush=True)
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_comprehensive_functionality()
    sys.exit(0 if success else 1)
