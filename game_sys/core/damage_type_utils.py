# game_sys/core/damage_type_utils.py
"""
Utility functions for working with damage types, converting between
the enum representation and the configuration-based representation.
"""

from game_sys.core.damage_types import DamageType
from game_sys.config.property_loader import PropertyLoader


def get_damage_type_by_name(name: str) -> DamageType:
    """
    Get a DamageType enum value by its name.
    
    Args:
        name: The name of the damage type (case-insensitive)
        
    Returns:
        The corresponding DamageType enum value
    """
    try:
        # Try to match by exact name
        return DamageType[name.upper()]
    except KeyError:
        # Try to find a close match
        for dt in DamageType:
            if dt.name.lower() == name.lower():
                return dt
        
        # Default to physical if no match
        return DamageType.PHYSICAL


def get_damage_type_properties(damage_type: DamageType) -> dict:
    """
    Get the display properties for a damage type from the configuration.
    
    Args:
        damage_type: The DamageType enum value
        
    Returns:
        A dictionary with display properties like color and name
    """
    damage_types = PropertyLoader.get_damage_types()
    
    # Try to find by name
    key = damage_type.name
    if key in damage_types:
        return damage_types[key]
    
    # Default properties if not found
    return {
        "name": damage_type.name.title(),
        "color": "white"
    }


def get_all_damage_type_properties() -> dict:
    """
    Get all damage type properties from the configuration.
    
    Returns:
        A dictionary mapping damage type names to their properties
    """
    return PropertyLoader.get_damage_types()
