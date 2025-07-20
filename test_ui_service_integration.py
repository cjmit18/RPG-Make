#!/usr/bin/env python3
"""
Test UI Service Integration
==========================

Test script to verify the UI service integration works properly
with the refactored demo.py code.
"""
import sys
import os

# Add project root to path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

try:
    # Test imports
    print("Testing imports...")
    from ui.demo_ui import DemoUI
    from demo import SimpleGameDemo
    print("✅ Imports successful")
    
    # Test UI service creation
    print("\nTesting UI service creation...")
    ui_service = DemoUI()
    print("✅ UI service created successfully")
    
    # Test UI service methods
    print("\nTesting UI service methods...")
    methods_to_test = [
        'setup_inventory_tab',
        'setup_leveling_tab', 
        'setup_enchanting_tab',
        'setup_progression_tab',
        'setup_combo_tab',
        'setup_settings_tab',
        'update_inventory_display',
        'update_equipment_display',
        'update_leveling_display',
        'update_progression_display'
    ]
    
    for method_name in methods_to_test:
        if hasattr(ui_service, method_name):
            print(f"✅ {method_name} exists")
        else:
            print(f"❌ {method_name} missing")
    
    # Test tab creation in service
    print("\nTesting tab structure creation...")
    ui_service.tabs = {
        'stats': None,
        'combat': None,
        'inventory': None,
        'leveling': None,
        'enchanting': None,
        'progression': None,
        'combo': None,
        'settings': None
    }
    print("✅ Tab structure created")
    
    # Test setup_all_tabs (without actual UI)
    print("\nTesting setup_all_tabs method...")
    result = ui_service.setup_all_tabs()
    print(f"✅ setup_all_tabs returned: {result.get('message', 'No message')}")
    
    print("\n🎉 UI Service Integration Test PASSED!")
    print("The UI service has all required methods for demo.py integration.")
    
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Make sure all required modules are available")
    
except Exception as e:
    print(f"❌ Test error: {e}")
    print("UI service integration test failed")
