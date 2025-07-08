#!/usr/bin/env python3
"""
Comprehensive test for ScalingManager strength boost functionality.
Tests edge cases and verifies the *100 multiplier is applied correctly.
"""

import unittest
from unittest.mock import Mock, patch
import sys
import os

# Add the project root to sys.path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from game_sys.core.scaling_manager import ScalingManager


class TestStrengthBoostComprehensive(unittest.TestCase):
    """Comprehensive tests for strength boost functionality."""

    def setUp(self):
        """Set up common test fixtures."""
        self.mock_config_values = {
            'defaults.grades': ['COMMON', 'UNCOMMON', 'RARE', 'EPIC', 'LEGENDARY', 'MYTHIC', 'DIVINE'],
            'defaults.rarities': ['COMMON', 'UNCOMMON', 'RARE', 'EPIC', 'LEGENDARY', 'MYTHIC', 'DIVINE'],
            'constants.grade.stat_multiplier': {
                'ONE': 0.05, 'TWO': 0.1, 'THREE': 0.15, 'FOUR': 0.2, 
                'FIVE': 0.25, 'SIX': 0.3, 'SEVEN': 0.35
            },
            'constants.rarity.stat_multiplier': {
                'COMMON': 0.02, 'UNCOMMON': 0.04, 'RARE': 0.06, 
                'EPIC': 0.08, 'LEGENDARY': 0.1, 'MYTHIC': 0.12, 'DIVINE': 0.15
            }
        }

    @patch('game_sys.core.scaling_manager.ConfigManager')
    def test_strength_boost_not_zero(self, mock_config_class):
        """Test that strength boost is never zero for any valid enemy."""
        mock_config = Mock()
        mock_config.get.side_effect = lambda key, default=None: self.mock_config_values.get(key, default)
        mock_config_class.return_value = mock_config

        # Create test enemy
        enemy = Mock()
        enemy.name = "Test Enemy"
        enemy.level = 1  # Even at level 1
        enemy.grade = "ONE"  # Minimal grade
        enemy.rarity = "COMMON"  # Minimal rarity
        enemy.base_stats = {'strength': 5}
        enemy.update_stats = Mock()

        ScalingManager.apply_enemy_stat_boost(enemy)
        
        # Verify strength boost was applied (not zero)
        strength_boost = enemy.base_stats['strength'] - 5
        self.assertGreater(strength_boost, 0, "Strength boost should not be zero")
        
        # Calculate expected: level=1, grade=0.05, rarity=0.02, multiplier=1.07
        # Expected boost: int(1 * 1.07 * 100) = 107
        expected_boost = int(1 * 1.07 * 100)
        self.assertEqual(strength_boost, expected_boost)

    @patch('game_sys.core.scaling_manager.ConfigManager')
    def test_strength_boost_scales_with_level(self, mock_config_class):
        """Test that strength boost scales properly with enemy level."""
        mock_config = Mock()
        mock_config.get.side_effect = lambda key, default=None: self.mock_config_values.get(key, default)
        mock_config_class.return_value = mock_config

        levels_to_test = [1, 10, 50, 100]
        
        for level in levels_to_test:
            with self.subTest(level=level):
                enemy = Mock()
                enemy.name = f"Level {level} Enemy"
                enemy.level = level
                enemy.grade = "THREE"  # 0.15 multiplier
                enemy.rarity = "RARE"  # 0.06 multiplier
                enemy.base_stats = {'strength': 10}
                enemy.update_stats = Mock()

                ScalingManager.apply_enemy_stat_boost(enemy)
                
                # Calculate expected: multiplier = 1.0 + 0.15 + 0.06 = 1.21
                # Expected boost: int(level * 1.21 * 100)
                expected_boost = int(level * 1.21 * 100)
                actual_boost = enemy.base_stats['strength'] - 10
                
                self.assertEqual(actual_boost, expected_boost, 
                    f"Level {level} should give boost of {expected_boost}, got {actual_boost}")

    @patch('game_sys.core.scaling_manager.ConfigManager')
    def test_strength_boost_with_high_multipliers(self, mock_config_class):
        """Test strength boost with maximum grade and rarity."""
        mock_config = Mock()
        mock_config.get.side_effect = lambda key, default=None: self.mock_config_values.get(key, default)
        mock_config_class.return_value = mock_config

        enemy = Mock()
        enemy.name = "Max Enemy"
        enemy.level = 200  # High level
        enemy.grade = "SEVEN"  # Highest grade (0.35)
        enemy.rarity = "DIVINE"  # Highest rarity (0.15)
        enemy.base_stats = {'strength': 50}
        enemy.update_stats = Mock()

        ScalingManager.apply_enemy_stat_boost(enemy)
        
        # Calculate expected: multiplier = 1.0 + 0.35 + 0.15 = 1.5
        # Expected boost: int(200 * 1.5 * 100) = 30000
        expected_boost = int(200 * 1.5 * 100)
        actual_boost = enemy.base_stats['strength'] - 50
        
        self.assertEqual(actual_boost, expected_boost)
        self.assertGreater(actual_boost, 25000, "High-level enemies should get significant strength boosts")

    @patch('game_sys.core.scaling_manager.ConfigManager')
    def test_strength_boost_with_unknown_grade_rarity(self, mock_config_class):
        """Test that unknown grade/rarity still gives strength boost."""
        mock_config = Mock()
        mock_config.get.side_effect = lambda key, default=None: self.mock_config_values.get(key, default)
        mock_config_class.return_value = mock_config

        enemy = Mock()
        enemy.name = "Unknown Enemy"
        enemy.level = 25
        enemy.grade = "UNKNOWN_GRADE"  # Not in config
        enemy.rarity = "UNKNOWN_RARITY"  # Not in config
        enemy.base_stats = {'strength': 15}
        enemy.update_stats = Mock()

        ScalingManager.apply_enemy_stat_boost(enemy)
        
        # Even with unknown grade/rarity, should still get base boost
        # multiplier = 1.0 + 0.0 + 0.0 = 1.0
        # Expected boost: int(25 * 1.0 * 100) = 2500
        expected_boost = int(25 * 1.0 * 100)
        actual_boost = enemy.base_stats['strength'] - 15
        
        self.assertEqual(actual_boost, expected_boost)
        self.assertGreater(actual_boost, 0, "Even unknown grade/rarity should give some strength boost")

    @patch('game_sys.core.scaling_manager.ConfigManager')
    def test_all_stats_boosted_not_just_strength(self, mock_config_class):
        """Test that all stats get boosted, not just strength."""
        mock_config = Mock()
        mock_config.get.side_effect = lambda key, default=None: self.mock_config_values.get(key, default)
        mock_config_class.return_value = mock_config

        enemy = Mock()
        enemy.name = "Full Stats Enemy"
        enemy.level = 30
        enemy.grade = "FOUR"  # 0.2 multiplier
        enemy.rarity = "EPIC"  # 0.08 multiplier
        enemy.base_stats = {
            'strength': 10,
            'defense': 8,
            'health': 100,
            'mana': 50,
            'stamina': 60,
            'speed': 12,
            'magic_power': 15
        }
        enemy.update_stats = Mock()

        original_stats = enemy.base_stats.copy()
        ScalingManager.apply_enemy_stat_boost(enemy)
        
        # Verify all stats were boosted
        for stat in ['strength', 'defense', 'health', 'mana', 'stamina', 'speed', 'magic_power']:
            with self.subTest(stat=stat):
                boost = enemy.base_stats[stat] - original_stats[stat]
                self.assertGreater(boost, 0, f"{stat} should be boosted")

        # Verify strength specifically gets the *100 multiplier
        # multiplier = 1.0 + 0.2 + 0.08 = 1.28
        expected_strength_boost = int(30 * 1.28 * 100)
        actual_strength_boost = enemy.base_stats['strength'] - original_stats['strength']
        self.assertEqual(actual_strength_boost, expected_strength_boost)


if __name__ == '__main__':
    unittest.main(verbosity=2)
