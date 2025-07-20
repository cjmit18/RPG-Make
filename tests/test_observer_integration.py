#!/usr/bin/env python3
"""
Observer Pattern Integration Validation
=======================================

Test script to validate the observer pattern integration with demo.py
"""

import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.abspath('.'))

def test_observer_imports():
    """Test observer pattern imports."""
    try:
        print("🔍 Testing observer pattern imports...")
        
        # Test interfaces import
        from interfaces import GameEventType, UIObserver, GameEventPublisher
        print("✅ Observer interfaces imported successfully")
        
        # Test event types
        test_events = [
            GameEventType.SKILL_LEARNED,
            GameEventType.SPELL_LEARNED, 
            GameEventType.ENCHANTMENT_LEARNED,
            GameEventType.PLAYER_LEVEL_UP,
            GameEventType.PLAYER_XP_GAINED
        ]
        
        for event_type in test_events:
            print(f"✅ Event type available: {event_type.value}")
        
        print("✅ All observer pattern components available")
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def test_demo_integration():
    """Test demo.py integration with observer pattern."""
    try:
        print("\n🎮 Testing demo integration...")
        
        # Test demo import
        import demo
        print("✅ Demo module imported successfully")
        
        # Check for observer pattern constants
        if hasattr(demo, 'OBSERVER_PATTERN_AVAILABLE'):
            print(f"✅ Observer pattern availability flag: {demo.OBSERVER_PATTERN_AVAILABLE}")
        else:
            print("❌ Observer pattern availability flag not found")
            return False
            
        # Check for observer pattern imports
        observer_imports = ['GameEventType', 'UIObserver', 'GameEventPublisher']
        for import_name in observer_imports:
            if hasattr(demo, import_name):
                value = getattr(demo, import_name)
                print(f"✅ {import_name} available: {value is not None}")
            else:
                print(f"❌ {import_name} not found in demo module")
        
        print("✅ Demo integration test passed")
        return True
        
    except Exception as e:
        print(f"❌ Demo integration error: {e}")
        return False

def test_event_publishing():
    """Test event publishing functionality."""
    try:
        print("\n📡 Testing event publishing...")
        
        from interfaces import GameEventPublisher, GameEventType
        
        # Test publishing without errors (no observers attached yet)
        GameEventPublisher.publish_skill_learned("test_skill")
        print("✅ Skill learned event published")
        
        GameEventPublisher.publish_spell_learned("test_spell")
        print("✅ Spell learned event published")
        
        GameEventPublisher.publish_level_up(2)
        print("✅ Level up event published")
        
        GameEventPublisher.publish_error("Test error", "warning")
        print("✅ Error event published")
        
        print("✅ Event publishing test passed")
        return True
        
    except Exception as e:
        print(f"❌ Event publishing error: {e}")
        return False

def main():
    """Run all validation tests."""
    print("🚀 Observer Pattern Integration Validation")
    print("=" * 50)
    
    tests = [
        test_observer_imports,
        test_demo_integration,
        test_event_publishing
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"❌ Test failed with exception: {e}")
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 Observer Pattern Integration: SUCCESS!")
        print("\n✨ Ready to test in demo:")
        print("   1. Run: python demo.py")
        print("   2. Go to Leveling tab")
        print("   3. Try 'Learn Skill', 'Learn Spell', 'Gain XP (Test)'")
        print("   4. Watch for event-driven UI updates!")
    else:
        print("❌ Observer Pattern Integration: ISSUES FOUND")
        print("   Please check the error messages above")

if __name__ == "__main__":
    main()
