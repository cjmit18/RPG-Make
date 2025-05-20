"""This module provides utility functions for generating random numbers,
clearing the screen, pausing execution, and waiting for a specified time."""
import random
import os
import time
import logging
logging.basicConfig(level=logging.INFO)
log = logging.getLogger()
def generate_random_number(min_value=1, max_value=10):
    """Generate a random integer between min_value and max_value."""
    return random.randint(min_value, max_value)
def generate_random_float(min_value=1.0, max_value=10.0):
    """Generate a random float between min_value and max_value."""
    return random.uniform(min_value, max_value)
def clear_screen():
    """Clear the console screen."""
    os.system('cls' if os.name == 'nt' else 'clear')
def pause():
    """Pause the program and wait for user input."""
    input("Press Enter to continue...")
def wait(seconds):
    """Wait for a specified number of seconds, logging each second."""
    for i in range(seconds, 0, -1):
        log.info(f"Waiting {i} seconds...")
        time.sleep(1)
def random_choice(choices: list = []):
    """Return a random choice from a list of choices."""
    return random.choice(choices)