from typing import List, Any, Tuple
import math

class Shape:
    """Base class for area shapes."""
    def get_targets(
        self,
        origin: Tuple[float, float],
        direction: Tuple[float, float],
        actors: List[Any]
    ) -> List[Any]:
        raise NotImplementedError

class CircleShape(Shape):
    def __init__(self, radius: float):
        self.radius = radius

    def get_targets(self, origin, direction, actors):
        ox, oy = origin
        return [
            actor for actor in actors
            if (actor.position[0]-ox)**2 + (actor.position[1]-oy)**2 <= self.radius**2
        ]

class ConeShape(Shape):
    def __init__(self, angle: float, length: float):
        self.angle  = math.radians(angle)
        self.length = length

    def get_targets(self, origin, direction, actors):
        ox, oy = origin
        dx, dy = direction
        mag = math.hypot(dx, dy)
        if mag == 0: return []
        ndx, ndy = dx/mag, dy/mag

        result = []
        for actor in actors:
            tx, ty = actor.position
            vx, vy = tx-ox, ty-oy
            dist = math.hypot(vx, vy)
            if dist > self.length or dist == 0: 
                continue
            dot   = vx*ndx + vy*ndy
            if dot < 0: 
                continue
            theta = math.acos(dot/dist)
            if theta <= self.angle/2:
                result.append(actor)
        return result

class LineShape(Shape):
    def __init__(self, width: float, length: float):
        self.width  = width
        self.length = length

    def get_targets(self, origin, direction, actors):
        ox, oy = origin
        dx, dy = direction
        mag = math.hypot(dx, dy)
        if mag == 0: return []
        ndx, ndy = dx/mag, dy/mag

        result = []
        for actor in actors:
            tx, ty = actor.position
            vx, vy = tx-ox, ty-oy
            proj = vx*ndx + vy*ndy
            if proj < 0 or proj > self.length:
                continue
            perp = abs(vx*ndy - vy*ndx)
            if perp <= self.width/2:
                result.append(actor)
        return result
