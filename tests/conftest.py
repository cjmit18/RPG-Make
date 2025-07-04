"""
Shared test fixtures and configuration for game_sys test suite.

This module provides centralized fixtures for testing the game system,
reducing code duplication and improving test maintainability.
"""

import pytest
import random
from typing import Dict, Optional

from game_sys.character.actor import Actor, Player, Enemy
from game_sys.items.factory import ItemFactory
from game_sys.items.equipment import Equipment
from game_sys.items.consumable import Consumable


class DeterministicRNG(random.Random):
    """
    A deterministic RNG for predictable testing.
    
    This class allows tests to specify exact values for random operations,
    making tests reproducible and debugging easier.
    """
    
    def __init__(
        self,
        uniform_val: float = 0.5,
        random_val: float = 0.5,
        randint_val: int = 1
    ):
        super().__init__()
        self._uniform_val = uniform_val
        self._random_val = random_val
        self._randint_val = randint_val
        
    def uniform(self, a, b):
        """Return a fixed value for uniform distribution."""
        return self._uniform_val
        
    def random(self):
        """Return a fixed value for random() calls."""
        return self._random_val
        
    def randint(self, a, b):
        """Return a fixed value for randint() calls."""
        return self._randint_val


@pytest.fixture
def deterministic_rng():
    """Provide a deterministic RNG for testing."""
    return DeterministicRNG()


@pytest.fixture
def random_seed():
    """Set a fixed random seed for reproducible tests."""
    random.seed(42)
    yield
    # Reset to default behavior after test
    random.seed()


@pytest.fixture
def basic_actor():
    """Create a basic Actor with default stats."""
    return Actor(
        name="Test Actor",
        base_stats={
            'health': 100,
            'mana': 50,
            'stamina': 75,
            'attack': 10,
            'defense': 5,
            'intellect': 8
        }
    )


@pytest.fixture
def player_factory():
    """
    Factory function for creating Player characters with custom stats.
    
    Returns:
        Callable that creates a Player with specified name, level, and stats.
    """
    def _create_player(
        name: str = "Test Player",
        level: int = 1,
        base_stats: Optional[Dict[str, float]] = None
    ) -> Player:
        if base_stats is None:
            base_stats = {
                'health': 100,
                'mana': 50,
                'stamina': 75,
                'attack': 10,
                'defense': 5,
                'intellect': 8
            }
        
        player = Player(name=name, base_stats=base_stats)
        player.level = level
        
        # Refresh health/mana/stamina pools
        player.max_health = player.get_stat('health')
        player.current_health = player.max_health
        player.max_mana = player.get_stat('mana')
        player.current_mana = player.max_mana
        player.max_stamina = player.get_stat('stamina')
        player.current_stamina = player.max_stamina
        
        return player
    
    return _create_player


@pytest.fixture
def enemy_factory():
    """
    Factory function for creating Enemy characters with custom stats.
    
    Returns:
        Callable that creates an Enemy with specified name, level, and stats.
    """
    def _create_enemy(
        name: str = "Test Enemy",
        level: int = 1,
        base_stats: Optional[Dict[str, float]] = None
    ) -> Enemy:
        if base_stats is None:
            base_stats = {
                'health': 80,
                'mana': 30,
                'stamina': 60,
                'attack': 8,
                'defense': 4,
                'intellect': 6
            }
        
        enemy = Enemy(name=name, base_stats=base_stats)
        enemy.level = level
        
        # Refresh health/mana/stamina pools
        enemy.max_health = enemy.get_stat('health')
        enemy.current_health = enemy.max_health
        enemy.max_mana = enemy.get_stat('mana')
        enemy.current_mana = enemy.max_mana
        enemy.max_stamina = enemy.get_stat('stamina')
        enemy.current_stamina = enemy.max_stamina
        
        return enemy
    
    return _create_enemy


@pytest.fixture
def clean_player():
    """
    Create a Player with cleared inventory for testing.
    
    This fixture provides a player with no starting items or equipment,
    ideal for testing inventory and equipment systems from a clean state.
    """
    player = Player(
        name="Clean Player",
        base_stats={
            'health': 100,
            'mana': 50,
            'stamina': 75,
            'attack': 10,
            'defense': 5,
            'intellect': 8
        }
    )
    
    # Clear inventory if it has clear methods
    if hasattr(player.inventory, 'clear'):
        player.inventory.clear()
    
    return player


@pytest.fixture
def sample_items():
    """Provide a set of sample items for testing."""
    try:
        return {
            'weapon': ItemFactory.create("iron_sword"),
            'armor': ItemFactory.create("leather_armor"),
            'consumable': ItemFactory.create("health_potion"),
        }
    except Exception:
        # Return None if items can't be created
        return {
            'weapon': None,
            'armor': None,
            'consumable': None,
        }


@pytest.fixture
def combat_pair(player_factory, enemy_factory):
    """
    Create a matched pair of Player and Enemy for combat testing.
    
    Returns:
        Tuple of (player, enemy) with balanced stats for testing.
    """
    player = player_factory(
        name="Combat Player",
        level=2,
        base_stats={
            'health': 120,
            'mana': 60,
            'stamina': 90,
            'attack': 15,
            'defense': 8,
            'intellect': 10
        }
    )
    
    enemy = enemy_factory(
        name="Combat Enemy",
        level=2,
        base_stats={
            'health': 100,
            'mana': 40,
            'stamina': 70,
            'attack': 12,
            'defense': 6,
            'intellect': 8
        }
    )
    
    return player, enemy


@pytest.fixture
def test_equipment():
    """Create a set of test equipment items."""
    
    class TestSword(Equipment):
        def __init__(self):
            super().__init__(
                item_id="test_sword",
                name="Test Sword",
                description="A sword for testing.",
                slot="weapon",
                stats={"attack": 5},
                effect_ids=[],
                price=50,
                level=1
            )
    
    class TestShield(Equipment):
        def __init__(self):
            super().__init__(
                item_id="test_shield",
                name="Test Shield",
                description="A shield for testing.",
                slot="offhand",
                stats={"defense": 3},
                effect_ids=[],
                price=30,
                level=1
            )
            self.can_block = True
            self.block_chance = 0.2
    
    class TestArmor(Equipment):
        def __init__(self):
            super().__init__(
                item_id="test_armor",
                name="Test Armor",
                description="Armor for testing.",
                slot="armor",
                stats={"defense": 7, "health": 20},
                effect_ids=[],
                price=100,
                level=1
            )
    
    return {
        'sword': TestSword(),
        'shield': TestShield(),
        'armor': TestArmor()
    }


@pytest.fixture
def test_consumables():
    """Create a set of test consumable items."""
    
    class TestPotion(Consumable):
        def __init__(self, name: str, effect: str, amount: int):
            super().__init__(
                item_id=f"test_{name.lower().replace(' ', '_')}",
                name=name,
                description=f"A {name.lower()} for testing.",
                effects=[{"type": effect, "amount": amount, "duration": 0}],
                price=10,
                level=1
            )
    
    return {
        'health_potion': TestPotion("Health Potion", "health", 50),
        'mana_potion': TestPotion("Mana Potion", "mana", 30),
        'stamina_potion': TestPotion("Stamina Potion", "stamina", 40)
    }


@pytest.fixture
def job_test_data():
    """Provide test data for job-related tests."""
    return {
        'knight': {
            'expected_stats': {'attack': 5, 'defense': 7, 'health': 10},
            'expected_items': ['iron_sword', 'iron_shield']
        },
        'mage': {
            'expected_stats': {'intellect': 8, 'mana': 15, 'attack': 2},
            'expected_items': ['apprentice_staff']
        },
        'warrior': {
            'expected_stats': {'attack': 6, 'defense': 5, 'health': 8},
            'expected_items': ['iron_sword', 'leather_armor']
        }
    }


@pytest.fixture(autouse=True)
def reset_singletons():
    """
    Reset any singleton state between tests.
    
    This fixture runs automatically for every test to ensure clean state.
    Add any singleton reset logic here as the codebase grows.
    """
    # Reset any global state, registries, or singletons here
    yield
    # Cleanup after test if needed


@pytest.fixture
def mock_combat_rng():
    """Provide RNG configurations for common combat scenarios."""
    return {
        'no_crit_max_damage': DeterministicRNG(
            uniform_val=1.0, random_val=0.5, randint_val=1
        ),
        'crit_max_damage': DeterministicRNG(
            uniform_val=1.0, random_val=0.05, randint_val=1
        ),
        'no_crit_min_damage': DeterministicRNG(
            uniform_val=0.8, random_val=0.5, randint_val=1
        ),
        'miss': DeterministicRNG(
            uniform_val=0.0, random_val=0.5, randint_val=1
        )
    }


# Parameterized test data
STAT_TEST_CASES = [
    ("health", 100, 150),
    ("mana", 50, 75),
    ("stamina", 75, 100),
    ("attack", 10, 15),
    ("defense", 5, 10),
    ("intellect", 8, 12)
]

JOB_TEST_CASES = [
    ("knight", 3),
    ("mage", 2),
    ("warrior", 4),
    ("commoner", 1)
]

ITEM_TYPE_TEST_CASES = [
    ("weapon", "iron_sword"),
    ("armor", "leather_armor"),
    ("consumable", "health_potion")
]
