#!/usr/bin/env python3
"""
Unit tests for TemplateService
==============================

Tests for the extracted template service functionality.
"""

import unittest
from unittest.mock import patch, MagicMock
from game_sys.character.template_service import TemplateService


class TestTemplateService(unittest.TestCase):
    """Test cases for TemplateService."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.mock_templates = {
            'warrior': {
                'name': 'Warrior',
                'display_name': 'Mighty Warrior',
                'job_id': 'warrior',
                'base_stats': {
                    'strength': 15,
                    'constitution': 12,
                    'dexterity': 8
                },
                'description': 'A strong melee fighter'
            },
            'mage': {
                'name': 'Mage',
                'display_name': 'Arcane Mage',
                'job_id': 'mage',
                'base_stats': {
                    'intelligence': 15,
                    'wisdom': 12,
                    'constitution': 6
                },
                'description': 'A powerful spellcaster'
            },
            'invalid_template': {
                'name': 'Invalid',
                # Missing base_stats - should be considered invalid
            }
        }
    
    @patch('game_sys.character.template_service.CharacterFactory')
    def test_load_templates_success(self, mock_factory):
        """Test successful template loading."""
        mock_factory._templates = self.mock_templates
        
        service = TemplateService()
        
        self.assertEqual(len(service.available_templates), 3)
        self.assertIn('warrior', service.available_templates)
        self.assertIn('mage', service.available_templates)
        mock_factory._load_templates.assert_called_once()
    
    @patch('game_sys.character.template_service.CharacterFactory')
    def test_load_templates_failure(self, mock_factory):
        """Test template loading failure handling."""
        mock_factory._load_templates.side_effect = Exception("Load failed")
        
        service = TemplateService()
        
        self.assertEqual(service.available_templates, {})
    
    @patch('game_sys.character.template_service.CharacterFactory')
    def test_get_available_templates(self, mock_factory):
        """Test getting available templates."""
        mock_factory._templates = self.mock_templates
        
        service = TemplateService()
        templates = service.get_available_templates()
        
        self.assertEqual(len(templates), 3)
        self.assertIsInstance(templates, dict)
        # Should return a copy, not the original
        self.assertIsNot(templates, service.available_templates)
    
    @patch('game_sys.character.template_service.CharacterFactory')
    def test_get_template_valid(self, mock_factory):
        """Test getting a specific valid template."""
        mock_factory._templates = self.mock_templates
        
        service = TemplateService()
        template = service.get_template('warrior')
        
        self.assertIsNotNone(template)
        self.assertEqual(template['name'], 'Warrior')
        self.assertEqual(template['job_id'], 'warrior')
    
    @patch('game_sys.character.template_service.CharacterFactory')
    def test_get_template_invalid(self, mock_factory):
        """Test getting a non-existent template."""
        mock_factory._templates = self.mock_templates
        
        service = TemplateService()
        template = service.get_template('nonexistent')
        
        self.assertIsNone(template)
    
    @patch('game_sys.character.template_service.CharacterFactory')
    def test_validate_template_valid(self, mock_factory):
        """Test validating a valid template."""
        mock_factory._templates = self.mock_templates
        
        service = TemplateService()
        
        self.assertTrue(service.validate_template('warrior'))
        self.assertTrue(service.validate_template('mage'))
    
    @patch('game_sys.character.template_service.CharacterFactory')
    def test_validate_template_invalid(self, mock_factory):
        """Test validating invalid templates."""
        mock_factory._templates = self.mock_templates
        
        service = TemplateService()
        
        # Missing required fields
        self.assertFalse(service.validate_template('invalid_template'))
        # Non-existent template
        self.assertFalse(service.validate_template('nonexistent'))
        # Empty template ID
        self.assertFalse(service.validate_template(''))
        self.assertFalse(service.validate_template(None))
    
    @patch('game_sys.character.template_service.CharacterFactory')
    def test_reload_templates_success(self, mock_factory):
        """Test successful template reloading."""
        # Initial load
        mock_factory._templates = {'warrior': self.mock_templates['warrior']}
        service = TemplateService()
        self.assertEqual(len(service.available_templates), 1)
        
        # Reload with more templates
        mock_factory._templates = self.mock_templates
        result = service.reload_templates()
        
        self.assertTrue(result['success'])
        self.assertEqual(result['old_count'], 1)
        self.assertEqual(result['new_count'], 3)
        self.assertEqual(len(service.available_templates), 3)
    
    @patch('game_sys.character.template_service.CharacterFactory')
    def test_reload_templates_failure(self, mock_factory):
        """Test template reloading failure handling."""
        mock_factory._templates = self.mock_templates
        service = TemplateService()
        
        # Make reload fail
        mock_factory._load_templates.side_effect = Exception("Reload failed")
        result = service.reload_templates()
        
        self.assertFalse(result['success'])
        self.assertIn('error', result)
    
    @patch('game_sys.character.template_service.CharacterFactory')
    def test_get_template_list(self, mock_factory):
        """Test getting template list for UI display."""
        mock_factory._templates = self.mock_templates
        
        service = TemplateService()
        result = service.get_template_list()
        
        self.assertTrue(result['success'])
        self.assertEqual(result['count'], 3)
        self.assertEqual(len(result['templates']), 3)
        
        # Check template structure
        warrior_template = next((t for t in result['templates'] if t['id'] == 'warrior'), None)
        self.assertIsNotNone(warrior_template)
        self.assertEqual(warrior_template['name'], 'Mighty Warrior')
        self.assertEqual(warrior_template['job_id'], 'warrior')
    
    @patch('game_sys.character.template_service.CharacterFactory')
    def test_select_template_valid(self, mock_factory):
        """Test selecting a valid template."""
        mock_factory._templates = self.mock_templates
        
        service = TemplateService()
        result = service.select_template('warrior')
        
        self.assertTrue(result['success'])
        self.assertEqual(result['template_id'], 'warrior')
        self.assertIn('template_data', result)
        self.assertEqual(result['template_data']['name'], 'Warrior')
    
    @patch('game_sys.character.template_service.CharacterFactory')
    def test_select_template_invalid(self, mock_factory):
        """Test selecting invalid templates."""
        mock_factory._templates = self.mock_templates
        
        service = TemplateService()
        
        # Non-existent template
        result = service.select_template('nonexistent')
        self.assertFalse(result['success'])
        
        # Empty template ID
        result = service.select_template('')
        self.assertFalse(result['success'])
        
        # Invalid template (missing required fields)
        result = service.select_template('invalid_template')
        self.assertFalse(result['success'])


if __name__ == '__main__':
    unittest.main()
