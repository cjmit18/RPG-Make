# game_sys/managers/input_manager.py
"""
Module: game_sys.managers.input_manager

Handles player input (keyboard, mouse) and dispatches events.
"""
class InputManager:
    """Real input manager using a library like pygame."""
    def __init__(self):
        self._state = {}

    def update(self):
        """Poll hardware/input devices and update internal state."""
        # e.g., pygame.event.pump()
        pass

    def is_key_pressed(self, key: str) -> bool:
        """Return whether the given key is currently pressed."""
        return self._state.get(key, False)

    def get_mouse_position(self) -> tuple[float, float]:
        """Return current mouse coordinates."""
        return (0.0, 0.0)
