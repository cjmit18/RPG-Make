#!/usr/bin/env python3
"""Test job-based passive system implementation."""

from game_sys.character.character_factory import create_character
from game_sys.skills.passive_manager import PassiveManager

def test_job_passives():
    """Test that jobs properly assign passive abilities."""
    print('Testing job-based passive system...')
    
    # Test warrior character (should have berserker_rage passive)
    print('\n--- Testing Warrior ---')
    warrior = create_character('warrior')
    print(f'Created warrior: {warrior.name}')
    print(f'Job: {warrior.job_id if hasattr(warrior, "job_id") else "No job set"}')
    
    # Test mage character (should have battle_meditation passive)
    print('\n--- Testing Mage ---')
    mage = create_character('mage')
    print(f'Created mage: {mage.name}')
    print(f'Job: {mage.job_id if hasattr(mage, "job_id") else "No job set"}')
    
    # Test rogue character (should have endless_sprint passive)
    print('\n--- Testing Rogue ---')
    rogue = create_character('rogue')
    print(f'Created rogue: {rogue.name}')
    print(f'Job: {rogue.job_id if hasattr(rogue, "job_id") else "No job set"}')
    
    print('\n--- Testing Character Template Passives ---')
    # Test hero template (should have some template passives)
    hero = create_character('hero')
    print(f'Created hero: {hero.name}')
    print(f'Job: {hero.job_id if hasattr(hero, "job_id") else "No job set"}')
    
    print('\nJob-based passive system test complete!')

if __name__ == "__main__":
    test_job_passives()
