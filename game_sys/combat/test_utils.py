# game_sys/combat/test_utils.py
"""
Combat testing utilities.

Provides helper functions to simplify combat testing and gameplay scripts
without exposing the underlying ActionQueue plumbing.
"""

from __future__ import annotations
from typing import TYPE_CHECKING, List
import time

if TYPE_CHECKING:
    from game_sys.character.actor import Actor

from .turn_manager import turn_manager
from game_sys.managers.time_manager import time_manager


def swing(attacker: "Actor", targets: List["Actor"]) -> bool:
    """
    Helper for tests: schedule an attack and advance time until it executes.
    
    Args:
        attacker: The attacking actor
        targets: List of target actors
        
    Returns:
        True if attack was scheduled successfully
        
    Usage:
        >>> swing(player, [enemy])  # Attack executes immediately
    """
    # Schedule the attack
    success = attacker.attack_targets(targets)
    if not success:
        return False
    
    # Fast-forward time by the attack cooldown
    cooldown = attacker.get_stat('attack_cooldown')
    time_manager.tick(cooldown + 0.1)  # Add small buffer
    
    return True


def setup_deterministic_combat(seed: int = 42):
    """
    Set up deterministic combat for testing.
    
    Args:
        seed: RNG seed for reproducible results
    """
    # Seed the turn manager's combat engine
    turn_manager._engine.set_rng_seed(seed)


def fast_forward_time(duration: float):
    """
    Fast-forward the game time by the specified duration.
    
    Args:
        duration: Time to advance in seconds
    """
    time_manager.tick(duration)


def wait_for_combat_completion(max_wait: float = 10.0):
    """
    Wait for all pending combat actions to complete.
    
    Args:
        max_wait: Maximum time to wait in seconds
    """
    start_time = time.time()
    dt = 0.1
    
    while time.time() - start_time < max_wait:
        time_manager.tick(dt)
        
        # Check if any actors have pending actions
        has_pending = False
        for actor in turn_manager._actors:
            from game_sys.managers.factories import get_action_queue
            action_queue = get_action_queue()
            ready_actions = action_queue.consume(actor)
            if ready_actions:
                has_pending = True
                # Put them back (they'll be processed on next tick)
                for name, payload in ready_actions:
                    action_queue.schedule(actor, name, 0.0, **payload)
                break
        
        if not has_pending:
            break


class CombatTestScenario:
    """
    Helper class for setting up combat test scenarios.
    """
    
    def __init__(self, seed: int = 42):
        """Initialize with deterministic RNG."""
        setup_deterministic_combat(seed)
        self.actors = []
    
    def add_actor(self, actor: "Actor") -> "CombatTestScenario":
        """Add an actor to the scenario."""
        self.actors.append(actor)
        turn_manager.register(actor)
        return self
    
    def execute_round(self, attacks: List[tuple]) -> List[bool]:
        """
        Execute a round of attacks.
        
        Args:
            attacks: List of (attacker, targets) tuples
            
        Returns:
            List of success flags for each attack
        """
        results = []
        for attacker, targets in attacks:
            success = swing(attacker, targets)
            results.append(success)
        
        # Wait for all attacks to complete
        wait_for_combat_completion()
        return results
    
    def get_survivors(self) -> List["Actor"]:
        """Get all actors that are still alive."""
        return [actor for actor in self.actors if actor.is_alive()]
    
    def cleanup(self):
        """Clean up the scenario."""
        for actor in self.actors:
            turn_manager.unregister(actor)
