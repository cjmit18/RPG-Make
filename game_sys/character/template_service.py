#!/usr/bin/env python3
"""
Template Service
================

Service for managing character templates, extracted from CharacterCreationService
as part of the newdemo.py decoupling effort.

This service handles:
- Loading templates from disk
- Template validation
- Template reloading
- Template information retrieval
"""

from typing import Dict, Any, Optional
from game_sys.character.character_factory import CharacterFactory
from game_sys.logging import get_logger


class TemplateService:
    """Service for managing character templates."""
    
    def __init__(self):
        """Initialize the template service."""
        self.logger = get_logger(__name__)
        self.available_templates = {}
        try:
            self._load_templates()
        except Exception as e:
            self.logger.error(f"Failed to load character templates during initialization: {e}")
            self.available_templates = {}
    
    def _load_templates(self) -> None:
        """Load character templates from disk."""
        CharacterFactory._load_templates()  # Let exceptions bubble up for reload_templates
        self.available_templates = CharacterFactory._templates
        self.logger.info(f"Loaded {len(self.available_templates)} character templates")
    
    def get_available_templates(self) -> Dict[str, Dict[str, Any]]:
        """
        Get all available templates.
        
        Returns:
            Dictionary of template_id -> template_data
        """
        return self.available_templates.copy()
    
    def get_template(self, template_id: str) -> Optional[Dict[str, Any]]:
        """
        Get specific template by ID.
        
        Args:
            template_id: ID of the template to retrieve
            
        Returns:
            Template data dictionary or None if not found
        """
        return self.available_templates.get(template_id)
    
    def reload_templates(self) -> Dict[str, Any]:
        """
        Reload templates from disk.
        
        Returns:
            Result dictionary with reload status
        """
        try:
            old_count = len(self.available_templates)
            self._load_templates()
            new_count = len(self.available_templates)
            
            self.logger.info(f"Reloaded templates: {old_count} -> {new_count}")
            return {
                'success': True,
                'old_count': old_count,
                'new_count': new_count,
                'message': f"Templates reloaded! Found {new_count} templates (was {old_count})"
            }
        except Exception as e:
            self.logger.error(f"Failed to reload templates: {e}")
            return {
                'success': False,
                'error': str(e),
                'message': 'Failed to reload templates'
            }
    
    def validate_template(self, template_id: str) -> bool:
        """
        Validate that a template exists and is valid.
        
        Args:
            template_id: ID of the template to validate
            
        Returns:
            True if template exists and is valid, False otherwise
        """
        if not template_id:
            return False
            
        template = self.get_template(template_id)
        if not template:
            return False
            
        # Basic validation - ensure required fields exist
        # Templates need either 'name' or 'display_name', and must have 'base_stats'
        has_name = 'name' in template or 'display_name' in template
        has_stats = 'base_stats' in template
        return has_name and has_stats
    
    def get_template_list(self) -> Dict[str, Any]:
        """
        Get a list of template names and IDs for UI display.
        
        Returns:
            Result dictionary with template list
        """
        try:
            template_list = []
            for template_id, template_data in self.available_templates.items():
                template_list.append({
                    'id': template_id,
                    'name': template_data.get('display_name', template_data.get('name', template_id)),
                    'job_id': template_data.get('job_id', 'Unknown'),
                    'description': template_data.get('description', 'No description available')
                })
            
            return {
                'success': True,
                'templates': template_list,
                'count': len(template_list),
                'message': f'Found {len(template_list)} available templates'
            }
        except Exception as e:
            self.logger.error(f"Failed to get template list: {e}")
            return {
                'success': False,
                'error': str(e),
                'templates': [],
                'count': 0,
                'message': 'Failed to retrieve template list'
            }
    
    def select_template(self, template_id: str) -> Dict[str, Any]:
        """
        Select and validate a template for character creation.
        
        Args:
            template_id: ID of the template to select
            
        Returns:
            Result dictionary with template information
        """
        try:
            if not template_id:
                return {
                    'success': False,
                    'error': 'No template ID provided',
                    'message': 'Please select a valid template'
                }
            
            if not self.validate_template(template_id):
                return {
                    'success': False,
                    'error': f'Invalid template: {template_id}',
                    'message': f'Template "{template_id}" not found or invalid'
                }
            
            template_data = self.get_template(template_id)
            template_name = template_data.get('display_name', template_data.get('name', template_id))
            
            self.logger.info(f"Selected template: {template_name} ({template_id})")
            return {
                'success': True,
                'template_id': template_id,
                'template_data': template_data,
                'message': f'Selected template: {template_name}'
            }
            
        except Exception as e:
            self.logger.error(f"Failed to select template {template_id}: {e}")
            return {
                'success': False,
                'error': str(e),
                'message': f'Failed to select template: {template_id}'
            }
