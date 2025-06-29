# game_sys/config/feature_flags.py
"""
Module: game_sys.config.feature_flags

Provides a simple API to check whether named feature toggles are enabled
in the current configuration. Reads from the singleton ConfigManager.
"""

from typing import Any
from game_sys.config.config_manager import ConfigManager


class FeatureFlags:
    """
    Wrapper around ConfigManager for boolean feature toggles.
    """

    def __init__(self):
        # Hold a reference to ConfigManager for lookups
        self._cfg = ConfigManager()

    def is_enabled(self, feature: str, default: bool = False) -> bool:
        """
        Return True if the given feature toggle (path under 'toggles')
        is set to True in config, otherwise False.
        """
        return bool(self._cfg.get(f'toggles.{feature}', default))

    def enable(self, feature: str):
        """Enable a feature toggle at runtime."""
        self._cfg.set(f'toggles.{feature}', True)

    def disable(self, feature: str):
        """Disable a feature toggle at runtime."""
        self._cfg.set(f'toggles.{feature}', False)