# game_sys/managers/resource_manager.py
"""
Module: game_sys.managers.resource_manager

Handles loading and caching of game resources (images, sounds, data files).
"""
from typing import Any, List

class ResourceManager:
    """
    Loads assets on demand and caches them in memory.
    """
    def __init__(self):
        self._cache: Dict[str, Any] = {}

    def load(self, path: str) -> Any:
        """
        Load the resource at the given path, or return it from cache.
        """
        if path in self._cache:
            return self._cache[path]
        # TODO: replace the following stub with real loading logic:
        resource = None
        self._cache[path] = resource
        return resource

    def preload(self, paths: List[str]):
        """
        Preload a list of resource paths into the cache.
        """
        for p in paths:
            self.load(p)