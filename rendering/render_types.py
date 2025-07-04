#!/usr/bin/env python3
"""
Render Types
===========

This module defines basic types and enums for the rendering system.
"""

from enum import Enum, auto
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple, Union


class RenderLayer(Enum):
    """Enum defining render layers from back to front."""
    BACKGROUND = 0
    TERRAIN = 10
    OBJECTS = 20
    CHARACTERS = 30
    EFFECTS = 40
    UI_BACKGROUND = 50
    UI = 60
    UI_FOREGROUND = 70
    OVERLAY = 80
    DEBUG = 90


class RenderPriority(Enum):
    """Enum defining render priority within a layer."""
    LOWEST = 0
    LOW = 25
    NORMAL = 50
    HIGH = 75
    HIGHEST = 100


@dataclass
class RenderCommand:
    """A command to render something to the screen."""
    layer: RenderLayer
    priority: RenderPriority = RenderPriority.NORMAL
    data: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.data is None:
            self.data = {}


@dataclass
class Rect:
    """A simple rectangle class for rendering."""
    x: int
    y: int
    width: int
    height: int
    
    @property
    def left(self) -> int:
        return self.x
    
    @property
    def top(self) -> int:
        return self.y
    
    @property
    def right(self) -> int:
        return self.x + self.width
    
    @property
    def bottom(self) -> int:
        return self.y + self.height
    
    @property
    def center(self) -> Tuple[int, int]:
        return (self.x + self.width // 2, self.y + self.height // 2)
    
    def contains_point(self, x: int, y: int) -> bool:
        """Check if the rectangle contains the given point."""
        return (self.left <= x < self.right and
                self.top <= y < self.bottom)
    
    def intersects(self, other: 'Rect') -> bool:
        """Check if this rectangle intersects with another."""
        return (self.left < other.right and
                self.right > other.left and
                self.top < other.bottom and
                self.bottom > other.top)


@dataclass
class Color:
    """A simple color class."""
    r: int
    g: int
    b: int
    a: int = 255
    
    def as_tuple(self) -> Tuple[int, int, int, int]:
        """Get the color as a tuple."""
        return (self.r, self.g, self.b, self.a)
    
    def as_hex(self) -> str:
        """Get the color as a hex string."""
        return f"#{self.r:02x}{self.g:02x}{self.b:02x}"
    
    @classmethod
    def from_hex(cls, hex_string: str) -> 'Color':
        """Create a color from a hex string."""
        hex_string = hex_string.lstrip('#')
        if len(hex_string) == 6:
            r, g, b = tuple(int(hex_string[i:i+2], 16) for i in (0, 2, 4))
            return cls(r, g, b)
        elif len(hex_string) == 8:
            r, g, b, a = tuple(int(hex_string[i:i+2], 16) for i in (0, 2, 4, 6))
            return cls(r, g, b, a)
        else:
            raise ValueError(f"Invalid hex color: {hex_string}")


# Common colors
BLACK = Color(0, 0, 0)
WHITE = Color(255, 255, 255)
RED = Color(255, 0, 0)
GREEN = Color(0, 255, 0)
BLUE = Color(0, 0, 255)
YELLOW = Color(255, 255, 0)
CYAN = Color(0, 255, 255)
MAGENTA = Color(255, 0, 255)
TRANSPARENT = Color(0, 0, 0, 0)
