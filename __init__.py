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

# Core RPG Engine imports for easy access
try:
    from rpg_engine.core.config import GameConfig
    from rpg_engine.core.engine import AsyncGameEngine
    from rpg_engine.core.event_bus import EventBus
    from rpg_engine.core.service_container import ServiceContainer
    from rpg_engine.ui import ModularUIManager, StartMenuManager
except ImportError:
    # Core systems should be available
    pass

__all__ = [
    # Current RPG Engine (v2.0)
    "GameConfig",
    "AsyncGameEngine", 
    "EventBus",
    "ServiceContainer",
    "ModularUIManager",
    "StartMenuManager",
    
    # Project metadata
    "__version__",
    "__author__"
]