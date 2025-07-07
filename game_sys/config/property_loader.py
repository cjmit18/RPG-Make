# game_sys/config/property_loader.py
"""
Module for loading and providing access to game properties like
damage types, item grades, and rarities from JSON configuration files.
"""

import json
import os
from typing import Dict, Any

from game_sys.logging import character_logger


class PropertyLoader:
    """Loader for game properties from JSON configuration."""
    
    _damage_types = None
    _item_grades = None
    _item_rarities = None
    
    @classmethod
    def load_damage_types(cls) -> Dict[str, Dict[str, Any]]:
        """Load damage types from configuration."""
        if cls._damage_types is None:
            try:
                damage_types_file = os.path.join(
                    os.path.dirname(__file__), 
                    "damage_types.json"
                )
                with open(damage_types_file, 'r') as f:
                    data = json.load(f)
                    cls._damage_types = data.get('damage_types', {})
                    character_logger.info(
                        f"Loaded {len(cls._damage_types)} damage types from configuration"
                    )
            except Exception as e:
                character_logger.error(f"Error loading damage types: {e}")
                cls._damage_types = {}
        
        return cls._damage_types
    
    @classmethod
    def load_item_properties(cls) -> None:
        """Load item grades and rarities from configuration."""
        if cls._item_grades is None or cls._item_rarities is None:
            try:
                item_props_file = os.path.join(
                    os.path.dirname(__file__), 
                    "item_properties.json"
                )
                with open(item_props_file, 'r') as f:
                    data = json.load(f)
                    cls._item_grades = data.get('item_grades', {})
                    cls._item_rarities = data.get('item_rarities', {})
                    character_logger.info(
                        f"Loaded {len(cls._item_grades)} item grades and "
                        f"{len(cls._item_rarities)} rarities from configuration"
                    )
            except Exception as e:
                character_logger.error(f"Error loading item properties: {e}")
                cls._item_grades = {}
                cls._item_rarities = {}
    
    @classmethod
    def get_damage_types(cls) -> Dict[str, Dict[str, Any]]:
        """Get the damage types configuration."""
        if cls._damage_types is None:
            cls.load_damage_types()
        return cls._damage_types
    
    @classmethod
    def get_item_grades(cls) -> Dict[str, Dict[str, Any]]:
        """Get the item grades configuration."""
        if cls._item_grades is None:
            cls.load_item_properties()
        return cls._item_grades
    
    @classmethod
    def get_item_rarities(cls) -> Dict[str, Dict[str, Any]]:
        """Get the item rarities configuration."""
        if cls._item_rarities is None:
            cls.load_item_properties()
        return cls._item_rarities
