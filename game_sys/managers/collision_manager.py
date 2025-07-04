# game_sys/managers/collision_manager.py

from typing import Any, List, Optional, Tuple, TypeAlias, Dict, Set
from game_sys.targeting.shapes import Shape
import math

Position: TypeAlias = Tuple[float, float]
Direction: TypeAlias = Tuple[float, float]


class SpatialGrid:
    """
    Simple spatial grid for faster collision detection.
    Divides space into cells and only checks nearby cells for queries.
    """
    
    def __init__(self, cell_size: float = 100.0):
        self.cell_size = cell_size
        self.grid: Dict[Tuple[int, int], Set[Any]] = {}
        self.actor_cells: Dict[Any, Set[Tuple[int, int]]] = {}
    
    def _get_cell(self, x: float, y: float) -> Tuple[int, int]:
        """Get the grid cell for a position."""
        return (int(x // self.cell_size), int(y // self.cell_size))

    def _get_nearby_cells(self, x: float, y: float,
                          radius: float) -> Set[Tuple[int, int]]:
        """Get all cells that could contain objects within radius of (x, y)."""
        cells = set()
        # Calculate the range of cells to check
        cell_radius = int(math.ceil(radius / self.cell_size))
        center_cell = self._get_cell(x, y)
        
        for dx in range(-cell_radius, cell_radius + 1):
            for dy in range(-cell_radius, cell_radius + 1):
                cells.add((center_cell[0] + dx, center_cell[1] + dy))
        
        return cells
    
    def add(self, actor: Any) -> None:
        """Add an actor to the spatial grid."""
        if not hasattr(actor, 'position'):
            return
        
        self.remove(actor)  # Remove from old cells if any
        
        x, y = actor.position
        cell = self._get_cell(x, y)
        
        # Add to grid
        if cell not in self.grid:
            self.grid[cell] = set()
        self.grid[cell].add(actor)
        
        # Track which cells this actor is in
        self.actor_cells[actor] = {cell}
    
    def remove(self, actor: Any) -> None:
        """Remove an actor from the spatial grid."""
        if actor not in self.actor_cells:
            return
        
        # Remove from all cells
        for cell in self.actor_cells[actor]:
            if cell in self.grid:
                self.grid[cell].discard(actor)
                if not self.grid[cell]:  # Clean up empty cells
                    del self.grid[cell]
        
        del self.actor_cells[actor]
    
    def query_radius(self, x: float, y: float, radius: float) -> Set[Any]:
        """Find all actors within radius of (x, y)."""
        nearby_cells = self._get_nearby_cells(x, y, radius)
        candidates = set()
        
        for cell in nearby_cells:
            if cell in self.grid:
                candidates.update(self.grid[cell])
        
        # Filter by actual distance
        results = set()
        for actor in candidates:
            if hasattr(actor, 'position'):
                ax, ay = actor.position
                distance = math.sqrt((ax - x) ** 2 + (ay - y) ** 2)
                if distance <= radius:
                    results.add(actor)
        
        return results
    
    def update_actor(self, actor: Any) -> None:
        """Update an actor's position in the grid."""
        if hasattr(actor, 'position'):
            self.add(actor)  # This will remove from old position first


class CollisionManager:
    """
    Manages spatial registration of actors and provides querying by
    optional area shapes, origin/direction, and layer filtering.
    Now uses spatial partitioning for better performance.
    """

    def __init__(self, cell_size: float = 100.0):
        # All registered actors (for compatibility)
        self._actors: List[Any] = []
        # Spatial grid for fast queries
        self._spatial_grid = SpatialGrid(cell_size)

    def register(self, actor: Any) -> None:
        """
        Register an actor to participate in spatial queries.
        The actor may have attributes:
          - position: (x, y)
          - layer: str (for grouping)
        """
        if actor not in self._actors:
            self._actors.append(actor)
            self._spatial_grid.add(actor)

    def unregister(self, actor: Any) -> None:
        """
        Unregister an actor so it's no longer returned in queries.
        """
        if actor in self._actors:
            self._actors.remove(actor)
            self._spatial_grid.remove(actor)

    def update_actor_position(self, actor: Any) -> None:
        """
        Call this when an actor's position changes to update spatial grid.
        """
        self._spatial_grid.update_actor(actor)

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
        Uses spatial grid for better performance when shape is provided.
        """
        # If shape filtering is requested, use spatial grid for efficiency
        if shape and origin is not None:
            if direction is None:
                raise ValueError("Origin and direction must be provided "
                                 "when using a shape filter")
            
            # Get rough radius for spatial query (shape-dependent)
            if hasattr(shape, 'radius'):
                radius = getattr(shape, 'radius', 50.0)
            else:
                radius = 100.0  # Default search radius
            
            # Use spatial grid to get candidates
            candidates = self._spatial_grid.query_radius(origin[0], origin[1],
                                                         radius)
            results = list(candidates)
            
            # Apply shape filtering
            results = shape.get_targets(origin, direction, results)
        else:
            # Fallback to linear search for non-spatial queries
            results = list(self._actors)
        
        # Filter by layer if requested
        if layer is not None:
            results = [a for a in results
                       if getattr(a, "layer", None) == layer]

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
