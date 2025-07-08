"""
Test file for ScalingManager functionality.

Tests enemy stat boosts, player stat point allocation, and derived stat calculations.
"""

import unittest
from unittest.mock import Mock, MagicMock, patch
import sys
import os

# Add the project root to sys.path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from game_sys.core.scaling_manager import ScalingManager
from game_sys.character.leveling_manager import LevelingManager


class TestScalingManager(unittest.TestCase):
    """Test cases for ScalingManager functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_config = Mock()
        self.mock_config.get.return_value = {
            'DIVINE': 1.0,
            'LEGENDARY': 0.8,
            'EPIC': 0.6,
            'RARE': 0.4,
            'UNCOMMON': 0.2,
            'COMMON': 0.0
        }

    @patch('game_sys.core.scaling_manager.ConfigManager')
    def test_enemy_stat_boost_basic(self, mock_config_class):
        """Test basic enemy stat boost functionality."""
        # Setup mock config
        mock_config = Mock()
        mock_config.get.side_effect = lambda key, default=None: {
            'defaults.grades': ['COMMON', 'UNCOMMON', 'RARE', 'EPIC', 'LEGENDARY', 'MYTHIC', 'DIVINE'],
            'defaults.rarities': ['COMMON', 'UNCOMMON', 'RARE', 'EPIC', 'LEGENDARY', 'MYTHIC', 'DIVINE'],
            'constants.grade.stat_multiplier': {
                'DIVINE': 1.0,
                'MYTHIC': 0.8,
                'LEGENDARY': 0.6,
                'EPIC': 0.4,
                'RARE': 0.3,
                'UNCOMMON': 0.2,
                'COMMON': 0.0
            },
            'constants.rarity.stat_multiplier': {
                'DIVINE': 1.0,
                'MYTHIC': 0.8,
                'LEGENDARY': 0.6,
                'EPIC': 0.4,
                'RARE': 0.3,
                'UNCOMMON': 0.2,
                'COMMON': 0.0
            }
        }.get(key, default)
        mock_config_class.return_value = mock_config

        # Create mock enemy
        enemy = Mock()
        enemy.name = "Test Dragon"
        enemy.level = 100
        enemy.grade = 6  # DIVINE (0-indexed)
        enemy.rarity = "DIVINE"
        enemy.base_stats = {}
        enemy.update_stats = Mock()
        enemy.get_stat = Mock(return_value=10000)  # Mock strength return

        # Apply stat boost
        ScalingManager.apply_enemy_stat_boost(enemy)

        # Verify boosts were applied
        self.assertIn('strength', enemy.base_stats)
        self.assertIn('defense', enemy.base_stats)
        self.assertIn('health', enemy.base_stats)

        # With level 100, grade DIVINE (1.0), rarity DIVINE (1.0)
        # multiplier = 1.0 + 1.0 + 1.0 = 3.0
        # strength should be: int(100 * 3.0 * 100) = 30000
        expected_strength = int(100 * 3.0 * 100)
        self.assertEqual(enemy.base_stats['strength'], expected_strength)

        # Verify update_stats was called
        enemy.update_stats.assert_called_once()

    @patch('game_sys.core.scaling_manager.ConfigManager')
    def test_enemy_stat_boost_no_multipliers(self, mock_config_class):
        """Test enemy stat boost with no grade/rarity multipliers."""
        # Setup mock config with no multipliers
        mock_config = Mock()
        mock_config.get.return_value = None
        mock_config_class.return_value = mock_config

        # Create mock enemy
        enemy = Mock()
        enemy.name = "Test Goblin"
        enemy.level = 50
        enemy.grade = None
        enemy.rarity = None
        enemy.base_stats = {}
        enemy.update_stats = Mock()

        # Apply stat boost
        ScalingManager.apply_enemy_stat_boost(enemy)

        # With no multipliers, base multiplier = 1.0
        # strength should be: int(50 * 1.0 * 100) = 5000
        expected_strength = int(50 * 1.0 * 100)
        self.assertEqual(enemy.base_stats['strength'], expected_strength)

    def test_auto_allocate_stat_points(self):
        """Test automatic stat point allocation."""
        # Create mock character
        character = Mock()
        character.name = "Test Player"
        
        # Create mock leveling manager
        leveling_manager = Mock(spec=LevelingManager)
        leveling_manager.calculate_stat_points_available.return_value = 21  # 3 rounds of 7 stats
        leveling_manager.get_allocatable_stats.return_value = [
            'strength', 'dexterity', 'vitality', 'intelligence', 
            'wisdom', 'constitution', 'luck', 'attack', 'defense'
        ]
        leveling_manager.allocate_stat_point.return_value = True
        
        character.leveling_manager = leveling_manager
        character.update_stats = Mock()

        # Apply auto allocation
        ScalingManager.auto_allocate_stat_points(character)

        # Verify correct number of allocations (only to base RPG stats)
        expected_calls = 21  # All 21 points should be allocated
        self.assertEqual(leveling_manager.allocate_stat_point.call_count, expected_calls)

        # Verify only base RPG stats were allocated to
        allocated_stats = [call[0][1] for call in leveling_manager.allocate_stat_point.call_args_list]
        base_rpg_stats = ['strength', 'dexterity', 'vitality', 'intelligence', 'wisdom', 'constitution', 'luck']
        
        for stat in allocated_stats:
            self.assertIn(stat, base_rpg_stats, f"Invalid stat allocated: {stat}")

        # Verify update_stats was called
        character.update_stats.assert_called_once()

    def test_auto_allocate_no_leveling_manager(self):
        """Test auto allocation with no leveling manager."""
        character = Mock()
        character.name = "Test Player"
        del character.leveling_manager  # Remove leveling manager

        # Should not raise exception
        ScalingManager.auto_allocate_stat_points(character)

    def test_auto_allocate_no_points_available(self):
        """Test auto allocation with no points available."""
        character = Mock()
        character.name = "Test Player"
        
        leveling_manager = Mock()
        leveling_manager.calculate_stat_points_available.return_value = 0
        character.leveling_manager = leveling_manager

        # Apply auto allocation
        ScalingManager.auto_allocate_stat_points(character)

        # Should not attempt any allocations
        self.assertFalse(hasattr(leveling_manager, 'allocate_stat_point') and 
                        leveling_manager.allocate_stat_point.called)

    @patch('game_sys.core.scaling_manager.ConfigManager')
    def test_compute_stat_derived(self, mock_config_class):
        """Test derived stat computation."""
        # Setup mock config
        mock_config = Mock()
        mock_config.get.return_value = 2.0  # 2x multiplier for attack from strength
        mock_config_class.return_value = mock_config

        # Create mock actor
        actor = Mock()
        actor.name = "Test Actor"
        actor.base_stats = {'strength': 100}
        
        # Test derived stat calculation (attack from strength)
        result = ScalingManager.compute_stat(actor, 'attack')
        
        # Should be strength * multiplier = 100 * 2.0 = 200
        self.assertEqual(result, 200.0)

    @patch('game_sys.core.scaling_manager.ConfigManager')
    def test_compute_stat_base(self, mock_config_class):
        """Test base stat computation."""
        # Setup mock config
        mock_config = Mock()
        mock_config_class.return_value = mock_config

        # Create mock actor
        actor = Mock()
        actor.name = "Test Actor"
        actor.base_stats = {'strength': 150}
        
        # Test base stat calculation
        result = ScalingManager.compute_stat(actor, 'strength')
        
        # Should be the base value
        self.assertEqual(result, 150.0)

    def test_integration_enemy_boost_and_stat_calculation(self):
        """Integration test: enemy boost + stat calculation."""
        with patch('game_sys.core.scaling_manager.ConfigManager') as mock_config_class:
            # Setup mock config for boost
            mock_config = Mock()
            mock_config.get.side_effect = lambda key, default=None: {
                'defaults.grades': ['COMMON', 'UNCOMMON', 'RARE', 'EPIC', 'LEGENDARY', 'MYTHIC', 'DIVINE'],
                'defaults.rarities': ['COMMON', 'UNCOMMON', 'RARE', 'EPIC', 'LEGENDARY', 'MYTHIC', 'DIVINE'],
                'constants.grade.stat_multiplier': {'LEGENDARY': 0.6},
                'constants.rarity.stat_multiplier': {'EPIC': 0.4},
                'constants.derived_stats.attack': 2.0  # attack = strength * 2
            }.get(key, default)
            mock_config_class.return_value = mock_config

            # Create mock enemy
            enemy = Mock()
            enemy.name = "Elite Warrior"
            enemy.level = 50
            enemy.grade = 4  # LEGENDARY (0-indexed)
            enemy.rarity = "EPIC"
            enemy.base_stats = {'strength': 10}  # Starting strength
            enemy.update_stats = Mock()
            enemy.get_stat = Mock()

            # Apply enemy stat boost
            ScalingManager.apply_enemy_stat_boost(enemy)

            # Calculate expected strength boost
            # multiplier = 1.0 + 0.6 (grade) + 0.4 (rarity) = 2.0
            # strength boost = int(50 * 2.0 * 100) = 10000
            # final strength = 10 + 10000 = 10010
            expected_strength = 10 + int(50 * 2.0 * 100)
            self.assertEqual(enemy.base_stats['strength'], expected_strength)

            # Now test derived stat calculation
            attack_value = ScalingManager.compute_stat(enemy, 'attack')
            # attack = strength * 2.0 = 10010 * 2.0 = 20020
            expected_attack = expected_strength * 2.0
            self.assertEqual(attack_value, expected_attack)


if __name__ == '__main__':
    # Configure logging to reduce noise during tests
    import logging
    logging.getLogger('game_sys.core.scaling').setLevel(logging.CRITICAL)
    
    unittest.main(verbosity=2)
