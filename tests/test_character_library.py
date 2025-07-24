#!/usr/bin/env python3
"""
Test script for character library functionality
"""

import os
import json
import sys

# Add project root to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from newdemo import CharacterCreationService

def test_character_library():
    """Test the character library functionality."""
    print("Testing Character Library Functionality")
    print("=" * 50)
    
    # Initialize service
    service = CharacterCreationService()
    
    # Test 1: Check initial state
    print("\nTest 1: Initial Library State")
    result = service.get_saved_character_list()
    print(f"Success: {result['success']}")
    print(f"Character count: {result['count']}")
    print(f"Characters: {result.get('characters', [])}")
    
    # Test 2: Create a character and save it
    print("\nTest 2: Create and Save Character")
    
    # Select a template
    templates = service.get_available_templates()
    if templates:
        template_id = list(templates.keys())[0]  # Get first template
        print(f"Using template: {template_id}")
        
        # Create character preview
        create_result = service.create_character_preview(template_id)
        print(f"Character creation: {create_result['success']}")
        
        if create_result['success']:
            # Save the character
            save_result = service.save_current_character("Test Hero")
            print(f"Save result: {save_result['success']}")
            print(f"Message: {save_result['message']}")
            
            if save_result['success']:
                # Test 3: List characters again
                print("\nTest 3: List Characters After Save")
                list_result = service.get_saved_character_list()
                print(f"Character count: {list_result['count']}")
                for char in list_result.get('characters', []):
                    print(f"  - {char['save_name']}: '{char['character_name']}' (Level {char['level']})")
                
                # Test 4: Load the character
                print("\nTest 4: Load Saved Character")
                load_result = service.load_saved_character("Test Hero")
                print(f"Load result: {load_result['success']}")
                print(f"Message: {load_result['message']}")
                
                if load_result['success']:
                    char_name = load_result['character'].name
                    char_level = load_result['stats']['level']
                    print(f"Loaded character: {char_name} (Level {char_level})")
                
                # Test 5: Delete the character
                print("\nTest 5: Delete Saved Character")
                delete_result = service.delete_saved_character("Test Hero")
                print(f"Delete result: {delete_result['success']}")
                print(f"Message: {delete_result['message']}")
                
                # Test 6: Final library state
                print("\nTest 6: Final Library State")
                final_result = service.get_saved_character_list()
                print(f"Character count: {final_result['count']}")
    
    print("\nTest completed!")

if __name__ == "__main__":
    test_character_library()
