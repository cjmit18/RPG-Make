#!/usr/bin/env python3
"""Debug job passive assignment in detail."""

from game_sys.character.character_factory import create_character
from game_sys.character.job_manager import JobManager
import json

def debug_job_passives():
    """Debug the job passive assignment process."""
    print('=== Debugging Job Passive Assignment ===')
    
    # Load job definitions to see what we expect
    job_manager = JobManager()
    with open('game_sys/character/data/jobs.json', 'r') as f:
        jobs_data = json.load(f)
    
    warrior_job = jobs_data['jobs']['warrior']
    print(f"Warrior job definition passives: {warrior_job.get('passives', [])}")
    
    mage_job = jobs_data['jobs']['mage']
    print(f"Mage job definition passives: {mage_job.get('passives', [])}")
    
    rogue_job = jobs_data['jobs']['rogue']
    print(f"Rogue job definition passives: {rogue_job.get('passives', [])}")
    
    print('\n=== Creating Characters ===')
    
    # Create warrior and check passive assignment step by step
    print('\n--- Creating Warrior ---')
    warrior = create_character('warrior')
    print(f'Warrior created: {warrior.name}')
    print(f'Warrior job: {warrior.job_id}')
    print(f'Warrior has passive_ids attr: {hasattr(warrior, "passive_ids")}')
    if hasattr(warrior, 'passive_ids'):
        print(f'Warrior passive_ids: {warrior.passive_ids}')
    
    # Check if passive assignment happened during job assignment
    print('\n=== Manual Job Assignment Test ===')
    
    # Create a basic character first
    test_char = create_character('hero')  # Use hero template without specific job
    print(f'Test character: {test_char.name}')
    print(f'Test character job before assignment: {getattr(test_char, "job_id", "None")}')
    print(f'Test character passive_ids before job assignment: {getattr(test_char, "passive_ids", "None")}')
    
    # Now manually assign warrior job
    print('\n--- Manually assigning warrior job ---')
    try:
        job_manager.assign(test_char, 'warrior')
        print(f'Job assignment complete')
        print(f'Test character job after assignment: {getattr(test_char, "job_id", "None")}')
        print(f'Test character passive_ids after assignment: {getattr(test_char, "passive_ids", "None")}')
    except Exception as e:
        print(f'Error during manual job assignment: {e}')
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_job_passives()
