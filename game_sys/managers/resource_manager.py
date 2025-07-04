# game_sys/managers/resource_manager.py
"""
Module: game_sys.managers.resource_manager

Handles loading and caching of game resources (images, sounds, data files).
"""
from typing import Any, List, Dict, Union
import time

class ResourceManager:
    """
    Loads assets on demand and caches them in memory.
    """
    def __init__(self, max_cache_size: int = 1000):
        self._cache: Dict[str, Any] = {}
        self._access_times: Dict[str, float] = {}
        self._max_cache_size = max_cache_size

    def _evict_lru(self):
        """Remove least recently used item if cache is full."""
        if len(self._cache) >= self._max_cache_size:
            lru_key = min(self._access_times.keys(),
                          key=lambda k: self._access_times[k])
            del self._cache[lru_key]
            del self._access_times[lru_key]

    def load(self, path: str) -> Any:
        """
        Load the resource at the given path, or return it from cache.
        """
        if path in self._cache:
            self._access_times[path] = time.time()
            return self._cache[path]
        
        self._evict_lru()
        # TODO: replace the following stub with real loading logic:
        resource = None
        self._cache[path] = resource
        self._access_times[path] = time.time()
        return resource

    def preload(self, paths: List[str]):
        """
        Preload a list of resource paths into the cache.
        """
        for p in paths:
            self.load(p)

    def clear_cache(self):
        """Clear the entire cache."""
        self._cache.clear()
        self._access_times.clear()

    def get_cache_stats(self) -> Dict[str, int]:
        """Return cache statistics."""
        return {
            'size': len(self._cache),
            'max_size': self._max_cache_size,
        }