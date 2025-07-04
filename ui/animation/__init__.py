#!/usr/bin/env python3
"""
Animation __init__ file
"""

from .animation import (
    Animation, PropertyAnimation, SequenceAnimation, ParallelAnimation,
    EasingType, AnimationManager, animation_manager
)

__all__ = [
    'Animation', 
    'PropertyAnimation', 
    'SequenceAnimation', 
    'ParallelAnimation',
    'EasingType', 
    'AnimationManager', 
    'animation_manager'
]
