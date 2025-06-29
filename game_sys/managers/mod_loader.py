# game_sys/managers/mod_loader.py
"""
Module: game_sys.managers.mod_loader

Loads and applies game mods (overrides) from a directory.
"""
import os
import importlib.util
from typing import Any

class ModLoader:
    """Discovers Python-based mods and applies overrides."""
    def __init__(self, mods_path: str = 'mods'):
        self.mods_path = mods_path
        self._overrides: dict[str, Any] = {}

    def load_mods(self):
        """Scan the mods directory, import each mod, and collect overrides."""
        if not os.path.isdir(self.mods_path):
            return []
        loaded = []
        for fname in os.listdir(self.mods_path):
            if fname.endswith('.py'):
                path = os.path.join(self.mods_path, fname)
                spec = importlib.util.spec_from_file_location(fname[:-3], path)
                mod = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(mod)
                if hasattr(mod, 'OVERRIDES'):
                    self._overrides.update(mod.OVERRIDES)
                loaded.append(fname)
        return loaded

    def get_override(self, key: str) -> Any:
        """Return a mod-provided override for the given config key, if any."""
        return self._overrides.get(key)
