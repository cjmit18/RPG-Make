# game_sys/character/resistance_manager.py
"""
Module for managing character resistances and weaknesses.
Loads data from JSON and applies it correctly to characters.
"""

from typing import Dict, Any
import json
import os
from game_sys.core.damage_types import DamageType
from game_sys.logging import character_logger


class ResistanceManager:
    """Manager for handling character resistances and weaknesses"""
    
    def __init__(self):
        self.templates_path = os.path.join(
            os.path.dirname(__file__), "data", "character_templates.json"
        )
        self._templates = None
    
    @property
    def templates(self) -> Dict[str, Any]:
        """Lazy-load the templates"""
        if self._templates is None:
            try:
                with open(self.templates_path, 'r') as f:
                    self._templates = json.load(f)
            except Exception as e:
                character_logger.error(
                    f"Failed to load character templates: {e}"
                )
                self._templates = {}
        return self._templates
    
    def apply_resistances_and_weaknesses(
        self, character, template_id: str
    ) -> None:
        """
        Apply resistances and weaknesses from the template to the character.
        
        Args:
            character: The character to modify
            template_id: The ID of the template to use
        """
        character_logger.debug(
            f"Applying resistances/weaknesses from template '{template_id}'"
        )
        
        # Initialize or clear existing resistances/weaknesses
        character.resistances = {}
        character.weaknesses = {}
        
        # Get template data
        template = self.templates.get(template_id.lower(), {})
        
        # Process resistances
        resistance_data = template.get('resistance', {})
        for element, value in resistance_data.items():
            try:
                # Convert string to DamageType enum
                damage_type = DamageType[element.upper()]
                character.resistances[damage_type] = float(value)
                character_logger.debug(
                    f"Applied resistance: {damage_type.name} = {value}"
                )
            except (KeyError, ValueError) as e:
                character_logger.error(
                    f"Invalid resistance data: {element}={value}, error: {e}"
                )
        
        # Process weaknesses
        weakness_data = template.get('weakness', {})
        for element, value in weakness_data.items():
            try:
                # Convert string to DamageType enum
                damage_type = DamageType[element.upper()]
                character.weaknesses[damage_type] = float(value)
                character_logger.debug(
                    f"Applied weakness: {damage_type.name} = {value}"
                )
            except (KeyError, ValueError) as e:
                character_logger.error(
                    f"Invalid weakness data: {element}={value}, error: {e}"
                )


# Global instance
resistance_manager = ResistanceManager()
