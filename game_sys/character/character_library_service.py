#!/usr/bin/env python3
"""
Character Library Service
========================

Service for managing the character library (save/load functionality),
extracted from newdemo.py as part of the decoupling effort.

This service handles:
- Character saving to library
- Character loading from library
- Character deletion from library
- Library persistence to disk
- Character library listing
"""

import json
import os
from datetime import datetime
from typing import Dict, Any, Optional, List
from game_sys.character.character_factory import create_character
from game_sys.character.template_service import TemplateService
from game_sys.logging import get_logger


class CharacterLibraryService:
    """Service for managing the character library (save/load)."""
    
    def __init__(self, library_path: str = "save/character_library.json"):
        """
        Initialize the character library service.
        
        Args:
            library_path: Path to the character library file
        """
        self.logger = get_logger(__name__)
        self.library_path = library_path
        self.character_library = {}
        self.template_service = TemplateService()
        self._load_library()
    
    def _load_library(self) -> None:
        """Load the character library from saved characters."""
        try:
            if os.path.exists(self.library_path):
                with open(self.library_path, 'r', encoding='utf-8') as f:
                    self.character_library = json.load(f)
                self.logger.info(f"Loaded {len(self.character_library)} saved characters")
            else:
                self.character_library = {}
                self.logger.info("No character library found, starting fresh")
        except Exception as e:
            self.logger.error(f"Failed to load character library: {e}")
            self.character_library = {}
    
    def _save_library(self) -> Dict[str, Any]:
        """Save the character library to disk."""
        try:
            # Ensure save directory exists
            os.makedirs(os.path.dirname(self.library_path), exist_ok=True)
            
            with open(self.library_path, 'w', encoding='utf-8') as f:
                json.dump(self.character_library, f, indent=2, ensure_ascii=False)
            
            self.logger.info("Character library saved successfully")
            return {
                'success': True,
                'message': 'Character library saved'
            }
            
        except Exception as e:
            self.logger.error(f"Failed to save character library: {e}")
            return {
                'success': False,
                'error': str(e),
                'message': 'Failed to save character library'
            }
    
    def save_character(self, character: Any, save_name: str, template_id: str) -> Dict[str, Any]:
        """
        Save a character to the library.
        
        Args:
            character: Character object to save
            save_name: Name to save the character under
            template_id: ID of the template used to create the character
            
        Returns:
            Result dictionary with save status
        """
        try:
            if not character:
                raise ValueError("No character provided")
            
            if not save_name or not save_name.strip():
                raise ValueError("Save name is required")
            
            if not template_id:
                raise ValueError("Template ID is required")
            
            # Create character save data
            character_data = {
                'name': character.name,
                'original_name': character.name,
                'template_id': template_id,
                'save_name': save_name.strip(),
                'created_date': datetime.now().isoformat(),
                'character_data': character.serialize()
            }
            
            self.logger.info(f"Saving character with template_id: {template_id}")
            
            # Save to library
            self.character_library[save_name.strip()] = character_data
            
            # Save library to disk
            library_result = self._save_library()
            if not library_result['success']:
                return library_result
            
            self.logger.info(f"Saved character '{character.name}' as '{save_name}'")
            return {
                'success': True,
                'character': character,
                'save_name': save_name.strip(),
                'message': f"Character saved as '{save_name.strip()}'"
            }
            
        except Exception as e:
            self.logger.error(f"Failed to save character: {e}")
            return {
                'success': False,
                'error': str(e),
                'message': 'Failed to save character'
            }
    
    def load_character(self, save_name: str) -> Dict[str, Any]:
        """
        Load a character from the library.
        
        Args:
            save_name: Name of the saved character
            
        Returns:
            Result dictionary with loaded character
        """
        try:
            if save_name not in self.character_library:
                raise ValueError(f"Character '{save_name}' not found in library")
            
            character_data = self.character_library[save_name]
            
            # Extract template ID with debugging
            template_id = character_data.get('template_id')
            self.logger.info(f"Loading character '{save_name}' with template_id: {template_id}")
            
            if not template_id:
                raise ValueError(f"No template_id found for character '{save_name}'")
            
            if not self.template_service.validate_template(template_id):
                available_templates = list(self.template_service.get_available_templates().keys())
                self.logger.error(f"Available templates: {available_templates}")
                raise ValueError(f"Template '{template_id}' not available for character '{save_name}'")
            
            # Reconstruct the character from saved data
            char_json = character_data['character_data']
            
            # Create a new character using the saved template
            preview_character = create_character(template_id)
            
            # Apply the saved character data
            preview_character.deserialize(char_json)
            
            self.logger.info(f"Loaded character '{save_name}' from library")
            return {
                'success': True,
                'character': preview_character,
                'save_name': save_name,
                'template_id': template_id,
                'message': f"Character '{save_name}' loaded successfully"
            }
                
        except Exception as e:
            self.logger.error(f"Failed to load character '{save_name}': {e}")
            return {
                'success': False,
                'error': str(e),
                'message': f"Failed to load character '{save_name}'"
            }
    
    def delete_character(self, save_name: str) -> Dict[str, Any]:
        """
        Delete a character from the library.
        
        Args:
            save_name: Name of the character to delete
            
        Returns:
            Result dictionary with deletion status
        """
        try:
            if save_name not in self.character_library:
                raise ValueError(f"Character '{save_name}' not found in library")
            
            # Remove from library
            del self.character_library[save_name]
            
            # Save updated library
            library_result = self._save_library()
            if not library_result['success']:
                return library_result
            
            self.logger.info(f"Deleted character '{save_name}' from library")
            return {
                'success': True,
                'deleted_character': save_name,
                'message': f"Character '{save_name}' deleted successfully"
            }
            
        except Exception as e:
            self.logger.error(f"Failed to delete character '{save_name}': {e}")
            return {
                'success': False,
                'error': str(e),
                'message': f"Failed to delete character '{save_name}'"
            }
    
    def list_characters(self) -> Dict[str, Any]:
        """
        Get a list of all saved characters.
        
        Returns:
            Result dictionary with character list
        """
        try:
            character_info = []
            for save_name, data in self.character_library.items():
                info = {
                    'save_name': save_name,
                    'character_name': data.get('original_name', 'Unknown'),
                    'template_id': data.get('template_id', 'Unknown'),
                    'created_date': data.get('created_date', 'Unknown')
                }
                
                # Try to extract level and other stats
                try:
                    char_data = data.get('character_data', '{}')
                    if isinstance(char_data, str):
                        char_info = json.loads(char_data)
                    else:
                        char_info = char_data
                    
                    info['level'] = char_info.get('level', 1)
                    info['grade'] = char_info.get('grade', 0)
                    info['rarity'] = char_info.get('rarity', 'COMMON')
                except:
                    info['level'] = 'Unknown'
                    info['grade'] = 'Unknown'
                    info['rarity'] = 'Unknown'
                
                character_info.append(info)
            
            return {
                'success': True,
                'characters': character_info,
                'count': len(character_info),
                'message': f'Found {len(character_info)} saved characters'
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get character list: {e}")
            return {
                'success': False,
                'error': str(e),
                'message': 'Failed to retrieve character list'
            }
    
    def get_character_count(self) -> int:
        """Get the number of characters in the library."""
        return len(self.character_library)
    
    def character_exists(self, save_name: str) -> bool:
        """Check if a character with the given save name exists."""
        return save_name in self.character_library
    
    def get_character_info(self, save_name: str) -> Optional[Dict[str, Any]]:
        """
        Get information about a specific saved character.
        
        Args:
            save_name: Name of the saved character
            
        Returns:
            Character info dictionary or None if not found
        """
        if save_name not in self.character_library:
            return None
        
        data = self.character_library[save_name]
        info = {
            'save_name': save_name,
            'character_name': data.get('original_name', 'Unknown'),
            'template_id': data.get('template_id', 'Unknown'),
            'created_date': data.get('created_date', 'Unknown')
        }
        
        # Try to extract level and other stats
        try:
            char_data = data.get('character_data', '{}')
            if isinstance(char_data, str):
                char_info = json.loads(char_data)
            else:
                char_info = char_data
            
            info['level'] = char_info.get('level', 1)
            info['grade'] = char_info.get('grade', 0)
            info['rarity'] = char_info.get('rarity', 'COMMON')
        except:
            info['level'] = 'Unknown'
            info['grade'] = 'Unknown'
            info['rarity'] = 'Unknown'
        
        return info
    
    def reload_library(self) -> Dict[str, Any]:
        """
        Reload the character library from disk.
        
        Returns:
            Result dictionary with reload status
        """
        try:
            old_count = len(self.character_library)
            self._load_library()
            new_count = len(self.character_library)
            
            self.logger.info(f"Reloaded character library: {old_count} -> {new_count} characters")
            return {
                'success': True,
                'old_count': old_count,
                'new_count': new_count,
                'message': f'Library reloaded: {new_count} characters available'
            }
            
        except Exception as e:
            self.logger.error(f"Failed to reload library: {e}")
            return {
                'success': False,
                'error': str(e),
                'message': 'Failed to reload character library'
            }
