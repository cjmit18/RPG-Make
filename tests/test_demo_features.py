# tests/test_demo_features.py
"""
Comprehensive test script to verify all features in the demo application.
Tests functionality of the demo with the consolidated configuration system.
"""

import os
import sys
import unittest
from pathlib import Path

# Add the parent directory to the path so we can import the game modules
parent_dir = Path(__file__).parent.parent
sys.path.append(str(parent_dir))

# Import game modules
from game_sys.config.config_manager import ConfigManager
from game_sys.character.actor import Actor
from game_sys.magic.spell_system import SpellSystem
from game_sys.magic.enchanting_system import EnchantingSystem
from game_sys.skills.learning_system import LearningSystem
from game_sys.character.leveling_manager import LevelingManager
from game_sys.items.item_loader import load_item
from game_sys.items.item_factory import create_item

class TestDemoFeatures(unittest.TestCase):
    """Test all features used in the demo to ensure they work with the consolidated config."""
    
    def setUp(self):
        """Set up test environment before each test."""
        # Initialize config
        self.config = ConfigManager()
        
        # Create test player
        self.player = Actor(name="TestPlayer")
        self.player.level = 5  # Set a reasonable level for testing
        
        # Initialize systems
        self.player.leveling_manager = LevelingManager()
        self.player.spell_system = SpellSystem(self.player)
        self.player.enchanting_system = EnchantingSystem(self.player)
        self.player.learning = LearningSystem(self.player)
        
        # Add some starting resources
        self.player.max_health = 100
        self.player.current_health = 100
        self.player.max_mana = 50
        self.player.current_mana = 50
        self.player.max_stamina = 80
        self.player.current_stamina = 80
    
    def test_config_loaded(self):
        """Test that config loads correctly after consolidation."""
        # Check that we have the expected config sections
        self.assertIn('toggles', self.config._data)
        self.assertIn('modules', self.config._data)
        self.assertIn('leveling', self.config._data)
        self.assertIn('skills', self.config._data)
        self.assertIn('spells', self.config._data)
        self.assertIn('enchantments', self.config._data)
        self.assertIn('ui', self.config._data)
        
        # Check that we can get a specific config value
        self.assertIsNotNone(self.config.get('leveling.points_per_level'))
        
        # Check that we can get a section
        spells = self.config.get_section('spells')
        self.assertIsNotNone(spells)
        self.assertIn('fireball', spells)
    
    def test_leveling_system(self):
        """Test leveling system with consolidated config."""
        # Check that we can get points per level
        points_per_level = self.config.get('leveling.points_per_level')
        self.assertIsNotNone(points_per_level)
        
        # Test XP gain
        old_level = self.player.level
        old_xp = getattr(self.player.leveling_manager, 'current_experience', 0)
        
        # Gain some XP
        self.player.leveling_manager.gain_experience(self.player, 500)
        
        # Check that XP increased
        new_xp = getattr(self.player.leveling_manager, 'current_experience', 0)
        self.assertGreater(new_xp, old_xp)
        
        # Reset the actor's level for other tests
        self.player.level = old_level
    
    def test_stat_allocation(self):
        """Test stat allocation with consolidated config."""
        # Make sure we have stat points available
        if not hasattr(self.player.leveling_manager, 'available_stat_points'):
            self.player.leveling_manager.available_stat_points = 5
        else:
            self.player.leveling_manager.available_stat_points = 5
        
        # Ensure base_stats exist
        if not hasattr(self.player, 'base_stats'):
            self.player.base_stats = {
                'strength': 10,
                'dexterity': 10,
                'vitality': 10,
                'intelligence': 10,
                'wisdom': 10,
                'constitution': 10,
                'luck': 10
            }
        
        # Try to allocate a stat point
        old_str = self.player.base_stats.get('strength', 10)
        result = self.player.leveling_manager.allocate_stat_point(self.player, 'strength')
        
        # Check that allocation worked
        self.assertTrue(result)
        new_str = self.player.base_stats.get('strength', 10)
        self.assertEqual(new_str, old_str + 1)
        
        # Check that available points decreased
        self.assertEqual(self.player.leveling_manager.available_stat_points, 4)
        
        # Test reset stat points
        self.player.leveling_manager.reset_stat_points(self.player)
        reset_str = self.player.base_stats.get('strength', 10)
        self.assertEqual(reset_str, 10)  # Should be reset to default
        
        # Check that available points were restored
        self.assertEqual(self.player.leveling_manager.available_stat_points, 5)
    
    def test_spell_learning(self):
        """Test spell learning with consolidated config."""
        # Check that we have spells in config
        spells = self.config.get_section('spells')
        self.assertIsNotNone(spells)
        self.assertGreater(len(spells), 0)
        
        # Pick the first spell to learn
        spell_id = next(iter(spells.keys()))
        
        # Make sure player meets requirements
        self.player.level = 10  # High enough for any spell
        if not hasattr(self.player, 'base_stats'):
            self.player.base_stats = {
                'intelligence': 20,  # High enough for any spell
                'wisdom': 20
            }
        else:
            self.player.base_stats['intelligence'] = 20
            self.player.base_stats['wisdom'] = 20
        
        # Try to learn the spell
        result = self.player.spell_system.learn_spell(spell_id)
        
        # Check that learning worked
        self.assertTrue(result)
        self.assertIn(spell_id, self.player.known_spells)
        
        # Check that spell appears in known spells
        known_spells = self.player.spell_system.get_known_spells()
        self.assertIn(spell_id, known_spells)
        
        # Try to learn it again (should fail)
        result = self.player.spell_system.learn_spell(spell_id)
        self.assertFalse(result)  # Already known
    
    def test_enchantment_learning(self):
        """Test enchantment learning with consolidated config."""
        # Check that we have enchantments in config
        enchantments = self.config.get_section('enchantments')
        self.assertIsNotNone(enchantments)
        self.assertGreater(len(enchantments), 0)
        
        # Pick the first enchantment to learn
        enchant_id = next(iter(enchantments.keys()))
        
        # Make sure player meets requirements
        self.player.level = 10  # High enough for any enchantment
        if not hasattr(self.player, 'base_stats'):
            self.player.base_stats = {
                'intelligence': 20,  # High enough for any enchantment
                'strength': 20
            }
        else:
            self.player.base_stats['intelligence'] = 20
            self.player.base_stats['strength'] = 20
        
        # Try to learn the enchantment
        result = self.player.enchanting_system.learn_enchantment(enchant_id)
        
        # Check that learning worked
        self.assertTrue(result)
        self.assertIn(enchant_id, self.player.known_enchantments)
        
        # Check that enchantment appears in known enchantments
        known_enchants = self.player.enchanting_system.get_known_enchantments()
        self.assertIn(enchant_id, known_enchants)
        
        # Try to learn it again (should fail)
        result = self.player.enchanting_system.learn_enchantment(enchant_id)
        self.assertFalse(result)  # Already known
    
    def test_skill_learning(self):
        """Test skill learning with consolidated config."""
        # Check that we have skills in config
        skills = self.config.get_section('skills')
        self.assertIsNotNone(skills)
        self.assertGreater(len(skills), 0)
        
        # Pick a skill to learn
        skill_id = next(iter(skills.keys()))
        
        # Make sure player meets requirements
        self.player.level = 10  # High enough for any skill
        if not hasattr(self.player, 'base_stats'):
            self.player.base_stats = {
                'strength': 20,  # High enough for any skill
                'dexterity': 20,
                'constitution': 20
            }
        else:
            self.player.base_stats['strength'] = 20
            self.player.base_stats['dexterity'] = 20
            self.player.base_stats['constitution'] = 20
        
        # Try to learn the skill
        result = self.player.learning.learn_if_allowed(skill_id)
        
        # Check that learning worked
        self.assertTrue(result)
        self.assertIn(skill_id, self.player.learning.learned_skills)
        
        # Try to learn it again (should fail)
        result = self.player.learning.learn_if_allowed(skill_id)
        self.assertFalse(result)  # Already known
    
    def test_item_creation(self):
        """Test item creation with consolidated config."""
        try:
            # Try to create a simple item
            item = create_item(
                "test_sword",
                "Test Sword",
                "A test sword",
                item_type="weapon",
                rarity="COMMON",
                grade="ONE"
            )
            
            # Check that item was created
            self.assertIsNotNone(item)
            self.assertEqual(item.name, "Test Sword")
            self.assertEqual(item.type, "weapon")
            
            # Check item properties
            self.assertEqual(item.rarity, "COMMON")
            self.assertEqual(item.grade, "ONE")
        except Exception as e:
            self.fail(f"Item creation failed: {e}")
    
    def test_config_get_section(self):
        """Test the new get_section method in ConfigManager."""
        # Test getting various sections
        sections = [
            'toggles', 'modules', 'constants', 'defaults', 
            'leveling', 'skills', 'spells', 'enchantments', 'ui'
        ]
        
        for section in sections:
            data = self.config.get_section(section)
            self.assertIsNotNone(data, f"Failed to get section: {section}")
            self.assertIsInstance(data, dict, f"Section {section} is not a dict")
        
        # Test getting non-existent section with default
        default_value = {"test": "value"}
        result = self.config.get_section("non_existent_section", default_value)
        self.assertEqual(result, default_value)
    
    def test_ui_config(self):
        """Test UI configuration from the consolidated config."""
        # Check that UI config is available
        ui_config = self.config.get_section('ui')
        self.assertIsNotNone(ui_config)
        
        # Check for UI colors
        self.assertIn('colors', ui_config)
        colors = ui_config['colors']
        self.assertIn('background', colors)
        self.assertIn('text', colors)
        
        # Check for UI fonts
        self.assertIn('fonts', ui_config)
        fonts = ui_config['fonts']
        self.assertIn('default', fonts)

    def tearDown(self):
        """Clean up after each test."""
        pass

if __name__ == "__main__":
    unittest.main()
