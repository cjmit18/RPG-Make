# game_sys/managers/collision_manager.py

from typing import Any, List, Optional, Tuple, TypeAlias
from game_sys.targeting.shapes import Shape

Position: TypeAlias = Tuple[float, float]
Direction: TypeAlias = Tuple[float, float]

class CollisionManager:
    """
    Manages spatial registration of actors and provides querying by
    optional area shapes, origin/direction, and layer filtering.
    """

    def __init__(self):
        # All registered actors
        self._actors: List[Any] = []

    def register(self, actor: Any) -> None:
        """
        Register an actor to participate in spatial queries.
        The actor may have attributes:
          - position: (x, y)
          - layer: str (for grouping)
        """
        if actor not in self._actors:
            self._actors.append(actor)

    def unregister(self, actor: Any) -> None:
        """
        Unregister an actor so it's no longer returned in queries.
        """
        if actor in self._actors:
            self._actors.remove(actor)

    def query(
        self,
        shape: Optional[Shape] = None,
        origin: Optional[Position] = None,
        direction: Optional[Direction] = None,
        layer: Optional[str] = None
    ) -> List[Any]:
        """
        Retrieve registered actors, optionally filtered by:
        
        - layer: only actors where actor.layer == layer
        - shape + origin + direction: only actors within the AOE
        
        If no filters are given, returns all actors.
        """
        # 1) Filter by layer if requested
        results = (
            [a for a in self._actors if getattr(a, "layer", None) == layer]
            if layer is not None
            else list(self._actors)
        )

        # 2) Filter by shape if requested
        if shape:
            if origin is None or direction is None:
                raise ValueError("Origin and direction must be provided when using a shape filter")
            results = shape.get_targets(origin, direction, results)

        return results

    def raycast(
        self,
        origin: Position,
        direction: Direction,
        distance: float,
        layer: Optional[str] = None
    ) -> Optional[Any]:
        """
        Perform a raycast from `origin` along `direction` up to `distance`.
        Returns the first actor hit, or None.
        
        Note: Actors should have `position: (x,y)` and optionally `bounding_radius: float`.
        This stub does a simple linear search; replace with your spatial structure for performance.
        """
        candidates = self.query(layer=layer)
        closest = None
        min_t = distance
        dx, dy = direction
        # Normalize direction
        mag = (dx*dx + dy*dy) ** 0.5
        if mag == 0:
            return None
        ndx, ndy = dx/mag, dy/mag

        for actor in candidates:
            pos = getattr(actor, "position", None)
            radius = getattr(actor, "bounding_radius", 0.0)
            if pos is None:
                continue
            ox, oy = origin
            tx, ty = pos
            # Vector to target
            vx, vy = tx-ox, ty-oy
            # Project onto ray direction
            t = vx*ndx + vy*ndy
            if 0 <= t <= min_t:
                # Closest approach distance
                perp = abs(vx*ndy - vy*ndx)
                if perp <= radius:
                    min_t = t
                    closest = actor
        return closest

# Global singleton instance
collision_manager = CollisionManager()
