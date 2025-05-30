"""This module provides utility functions for generating random numbers,
clearing the screen, pausing execution, and waiting for a specified time."""
import random
import os
import time
from logs.logs import get_logger
log = get_logger(__name__)
def generate_random_number(min_value: int = 1, max_value: int = 10) -> int:
    """Generate a random integer between min_value and max_value."""
    return random.randint(min_value, max_value) 
def generate_random_float(min_value: float = 1.0, max_value: float = 10.0) -> float:
    """Generate a random float between min_value and max_value."""
    return random.uniform(min_value, max_value)
def clear_screen() -> None:
    """Clear the console screen."""
    os.system('cls' if os.name == 'nt' else 'clear')
def pause() -> None:
    """Pause the program and wait for user input."""
    input("Press Enter to continue...")
def wait(seconds: int) -> None:
    """Wait for a specified number of seconds, logging each second."""
    for i in range(seconds, 0, -1):
        log.info(f"Waiting {i} seconds...")
        time.sleep(1)
def random_choice(choices: list[str] = []) -> str:
    """Return a random choice from a list of choices."""
    return random.choice(choices)
class DummyRng:
    """A dummy random number generator that returns a fixed value."""
    def __init__(self, value: int = 42):
        self.value = value
    def randint(self, min_value: int, max_value: int) -> int:
        """Return the fixed value regardless of min and max."""
        return self.value
    def uniform(self, min_value: float, max_value: float) -> float:
        """Return the fixed value as a float."""
        return float(self.value)
    