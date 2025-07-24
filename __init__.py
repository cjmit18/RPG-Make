"""
Testing-folder: RPG Engine Development Project
==============================================

A comprehensive RPG engine with character creation, combat systems, 
inventory management, and extensive testing capabilities.

Features:
- Character creation and management
- Combat system with various mechanics
- Equipment and inventory systems
- Configuration management
- Comprehensive logging
- UI services and controllers
- Admin tools and debugging utilities

Author: CJ
Version: 0.1.0
"""

__version__ = "0.1.0"
__author__ = "CJ"

# Core system imports for easy access
from game_sys.config.config_manager import ConfigManager
from game_sys.logging import get_logger

# Main demo application
from demo_v3 import RPGEngineDemoV3

__all__ = [
    "ConfigManager",
    "get_logger", 
    "RPGEngineDemoV3",
    "__version__",
    "__author__"
]