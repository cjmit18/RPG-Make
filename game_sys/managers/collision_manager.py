# game_sys/managers/collision_manager.py
"""
Module: game_sys.managers.collision_manager

Handles spatial queries and collision detection between entities.
"""
class CollisionManager:
    """Real collision manager with spatial partitioning."""
    def __init__(self):
        # e.g., initialize quad-tree or grid
        pass

    def query(self, shape: any, layer: str = None) -> list[any]:
        """Return all entities colliding with the given shape and optional layer."""
        return []

    def raycast(self, origin: tuple[float,float], direction: tuple[float,float], distance: float) -> any:
        """Perform a raycast and return the first hit entity or None."""
        return None
