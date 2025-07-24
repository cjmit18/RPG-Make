"""
Configuration Management Package
===============================

Centralized configuration management for the RPG engine.

Components:
- ConfigManager: Main configuration interface
- Configuration file handling (JSON, YAML, etc.)
- Environment-specific settings
- Configuration validation and defaults

Features:
- Hot-reloading of configuration changes
- Configuration schema validation
- Environment variable integration
- Secure configuration handling
"""

from .config_manager import ConfigManager

__all__ = [
    "ConfigManager"
]