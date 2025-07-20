# game_sys/items/equipment_manager.py
"""
Equipment Manager Reference
===========================

This module provides a reference to the main equipment manager located in 
game_sys.managers.equipment_manager for backward compatibility and convenience.
"""

# Import the main equipment manager
from game_sys.managers.equipment_manager import EquipmentManager, equipment_manager

# Re-export for backward compatibility
__all__ = ['EquipmentManager', 'equipment_manager']