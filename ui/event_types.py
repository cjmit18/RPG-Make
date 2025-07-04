#!/usr/bin/env python3
"""
UI Event Types
=============

This module defines the event types and event data structures for the UI system.
"""

from enum import Enum, auto
from dataclasses import dataclass
from typing import Any, Dict, Optional, Tuple, Union


class UIEventType(Enum):
    """Enum defining the types of UI events that can occur."""
    CLICK = auto()
    HOVER = auto()
    DRAG_START = auto()
    DRAG_MOVE = auto()
    DRAG_END = auto()
    KEY_PRESS = auto()
    VALUE_CHANGE = auto()
    FOCUS = auto()
    BLUR = auto()
    CLOSE = auto()
    RESIZE = auto()
    ANIMATION_COMPLETE = auto()
    CUSTOM = auto()


@dataclass
class UIEvent:
    """Base class for UI events."""
    type: UIEventType
    source: Any  # The widget that generated the event
    data: Dict[str, Any] = None  # Additional event data
    position: Optional[Tuple[int, int]] = None  # x, y coordinates
    propagate: bool = True  # Whether the event should propagate to parent widgets
    
    def __post_init__(self):
        if self.data is None:
            self.data = {}
    
    def stop_propagation(self):
        """Stop the event from propagating to parent widgets."""
        self.propagate = False


@dataclass
class ClickEvent(UIEvent):
    """Event data for click events."""
    button: int = 1  # 1 = left, 2 = middle, 3 = right
    
    def __post_init__(self):
        super().__post_init__()
        self.type = UIEventType.CLICK
        self.data["button"] = self.button


@dataclass
class ValueChangeEvent(UIEvent):
    """Event data for value change events."""
    old_value: Any = None
    new_value: Any = None
    
    def __post_init__(self):
        super().__post_init__()
        self.type = UIEventType.VALUE_CHANGE
        self.data["old_value"] = self.old_value
        self.data["new_value"] = self.new_value
