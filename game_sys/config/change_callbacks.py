"""
Change Callbacks Module
=====================

This module provides a way to register callbacks for configuration changes.
"""

from typing import Dict, List, Callable, Any


class ChangeCallbacks:
    """Manages callbacks for configuration changes."""
    
    def __init__(self):
        """Initialize the change callbacks."""
        self._callbacks: Dict[str, List[Callable[[Any], None]]] = {}
    
    def register(self, key: str, callback: Callable[[Any], None]) -> None:
        """Register a callback for a configuration key.
        
        Args:
            key: The configuration key to watch
            callback: The function to call when the key changes
        """
        if key not in self._callbacks:
            self._callbacks[key] = []
        self._callbacks[key].append(callback)
    
    def notify(self, key: str, value: Any) -> None:
        """Notify all callbacks for a key.
        
        Args:
            key: The configuration key that changed
            value: The new value
        """
        if key in self._callbacks:
            for callback in self._callbacks[key]:
                callback(value)
    
    def clear(self, key: str = None) -> None:
        """Clear callbacks for a key or all callbacks.
        
        Args:
            key: The key to clear callbacks for, or None to clear all
        """
        if key is None:
            self._callbacks.clear()
        elif key in self._callbacks:
            del self._callbacks[key]
