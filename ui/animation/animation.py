#!/usr/bin/env python3
"""
Animation System
==============

This module provides animation support for UI elements.
"""

import time
from enum import Enum, auto
from typing import Any, Callable, Dict, List, Optional, Tuple, Union

from game_sys.logging import get_logger

logger = get_logger(__name__)


class EasingType(Enum):
    """Enum defining animation easing functions."""
    LINEAR = auto()
    EASE_IN = auto()
    EASE_OUT = auto()
    EASE_IN_OUT = auto()
    BOUNCE = auto()
    ELASTIC = auto()


class Animation:
    """Base class for animations."""
    
    def __init__(self, duration: float = 1.0, easing: EasingType = EasingType.LINEAR):
        """Initialize the animation.
        
        Args:
            duration: Duration in seconds
            easing: Easing function to use
        """
        self.duration = max(0.01, duration)  # Minimum duration of 10ms
        self.easing = easing
        self.time_elapsed = 0.0
        self.is_finished = False
        self.is_running = False
        self.on_complete_callbacks: List[Callable[[], None]] = []
        
    def start(self):
        """Start the animation."""
        self.time_elapsed = 0.0
        self.is_finished = False
        self.is_running = True
        
    def stop(self):
        """Stop the animation."""
        self.is_running = False
        
    def reset(self):
        """Reset the animation to its initial state."""
        self.time_elapsed = 0.0
        self.is_finished = False
        self.is_running = False
        
    def update(self, dt: float) -> bool:
        """Update the animation.
        
        Args:
            dt: Time delta in seconds
            
        Returns:
            True if the animation is still running, False if it's finished
        """
        if not self.is_running:
            return False
            
        self.time_elapsed += dt
        
        if self.time_elapsed >= self.duration:
            self.time_elapsed = self.duration
            self.is_finished = True
            self.is_running = False
            self._trigger_complete_callbacks()
            return False
            
        return True
        
    def get_progress(self) -> float:
        """Get the progress of the animation (0.0 to 1.0)."""
        if self.duration <= 0:
            return 1.0
            
        raw_progress = min(1.0, self.time_elapsed / self.duration)
        return self._apply_easing(raw_progress)
        
    def _apply_easing(self, t: float) -> float:
        """Apply the easing function to the raw progress.
        
        Args:
            t: Raw progress (0.0 to 1.0)
            
        Returns:
            Eased progress (0.0 to 1.0)
        """
        if self.easing == EasingType.LINEAR:
            return t
        elif self.easing == EasingType.EASE_IN:
            return t * t
        elif self.easing == EasingType.EASE_OUT:
            return t * (2 - t)
        elif self.easing == EasingType.EASE_IN_OUT:
            return 2 * t * t if t < 0.5 else -1 + (4 - 2 * t) * t
        elif self.easing == EasingType.BOUNCE:
            # Simple bounce effect
            if t < 0.5:
                return 4 * t * t
            else:
                return (t - 1) * (t - 1) * (t - 1) * (t - 1) + 1
        elif self.easing == EasingType.ELASTIC:
            # Simple elastic effect
            p = 0.3
            s = p / 4
            if t == 0 or t == 1:
                return t
            t = t - 1
            return -(2 ** (10 * t)) * (t - s) * (2 * 3.14159 / p)
            
        return t  # Default to linear
        
    def on_complete(self, callback: Callable[[], None]):
        """Add a callback to be called when the animation completes.
        
        Args:
            callback: Function to call
            
        Returns:
            self for method chaining
        """
        self.on_complete_callbacks.append(callback)
        return self
        
    def _trigger_complete_callbacks(self):
        """Trigger all completion callbacks."""
        for callback in self.on_complete_callbacks:
            try:
                callback()
            except Exception as e:
                logger.error(f"Error in animation completion callback: {e}")


class PropertyAnimation(Animation):
    """Animation that changes a property over time."""
    
    def __init__(
        self, 
        target: Any, 
        property_name: str, 
        start_value: Any, 
        end_value: Any,
        duration: float = 1.0, 
        easing: EasingType = EasingType.LINEAR
    ):
        """Initialize the property animation.
        
        Args:
            target: Object whose property will be animated
            property_name: Name of the property to animate
            start_value: Starting value
            end_value: Ending value
            duration: Duration in seconds
            easing: Easing function to use
        """
        super().__init__(duration, easing)
        self.target = target
        self.property_name = property_name
        self.start_value = start_value
        self.end_value = end_value
        
    def update(self, dt: float) -> bool:
        """Update the animation.
        
        Args:
            dt: Time delta in seconds
            
        Returns:
            True if the animation is still running, False if it's finished
        """
        if not super().update(dt):
            # Animation is finished
            self._update_property(1.0)  # Ensure the final value is set
            return False
            
        # Update the property
        progress = self.get_progress()
        self._update_property(progress)
        return True
        
    def _update_property(self, progress: float):
        """Update the target property based on the current progress.
        
        Args:
            progress: Current progress (0.0 to 1.0)
        """
        if self.target is None:
            return
            
        # Calculate the interpolated value
        if isinstance(self.start_value, (int, float)) and isinstance(self.end_value, (int, float)):
            # Numeric interpolation
            value = self.start_value + progress * (self.end_value - self.start_value)
            # Round to int if both start and end are ints
            if isinstance(self.start_value, int) and isinstance(self.end_value, int):
                value = int(round(value))
        elif isinstance(self.start_value, tuple) and isinstance(self.end_value, tuple):
            # Tuple interpolation (for colors, positions, etc.)
            if len(self.start_value) != len(self.end_value):
                raise ValueError("Start and end tuples must have the same length")
                
            value = tuple(
                self.start_value[i] + progress * (self.end_value[i] - self.start_value[i])
                for i in range(len(self.start_value))
            )
        else:
            # Default to linear between values
            if progress >= 0.5:
                value = self.end_value
            else:
                value = self.start_value
                
        # Set the property
        try:
            setattr(self.target, self.property_name, value)
        except Exception as e:
            logger.error(f"Error setting property {self.property_name}: {e}")


class SequenceAnimation(Animation):
    """Animation that runs a sequence of animations one after another."""
    
    def __init__(self, animations: List[Animation]):
        """Initialize the sequence animation.
        
        Args:
            animations: List of animations to run in sequence
        """
        # Calculate total duration
        total_duration = sum(anim.duration for anim in animations)
        super().__init__(total_duration)
        
        self.animations = animations
        self.current_index = 0
        
    def start(self):
        """Start the sequence animation."""
        super().start()
        self.current_index = 0
        if self.animations:
            self.animations[0].start()
            
    def update(self, dt: float) -> bool:
        """Update the sequence animation.
        
        Args:
            dt: Time delta in seconds
            
        Returns:
            True if the animation is still running, False if it's finished
        """
        if not self.is_running or not self.animations:
            return False
            
        # Update current animation
        current_anim = self.animations[self.current_index]
        if current_anim.update(dt):
            # Current animation is still running
            return True
            
        # Current animation finished, move to next
        self.current_index += 1
        if self.current_index >= len(self.animations):
            # All animations finished
            self.is_finished = True
            self.is_running = False
            self._trigger_complete_callbacks()
            return False
            
        # Start the next animation
        self.animations[self.current_index].start()
        return True


class ParallelAnimation(Animation):
    """Animation that runs multiple animations in parallel."""
    
    def __init__(self, animations: List[Animation]):
        """Initialize the parallel animation.
        
        Args:
            animations: List of animations to run in parallel
        """
        # Use the longest duration
        max_duration = max((anim.duration for anim in animations), default=0.0)
        super().__init__(max_duration)
        
        self.animations = animations
        
    def start(self):
        """Start all animations in parallel."""
        super().start()
        for anim in self.animations:
            anim.start()
            
    def update(self, dt: float) -> bool:
        """Update all animations in parallel.
        
        Args:
            dt: Time delta in seconds
            
        Returns:
            True if any animation is still running, False if all finished
        """
        if not self.is_running:
            return False
            
        # Update all animations
        all_finished = True
        for anim in self.animations:
            if anim.update(dt):
                all_finished = False
                
        if all_finished:
            self.is_finished = True
            self.is_running = False
            self._trigger_complete_callbacks()
            return False
            
        return True


class AnimationManager:
    """Manager for all animations in the system."""
    
    def __init__(self):
        """Initialize the animation manager."""
        self.animations: List[Animation] = []
        self.last_update_time = time.time()
        
    def add_animation(self, animation: Animation) -> Animation:
        """Add an animation to the manager.
        
        Args:
            animation: The animation to add
            
        Returns:
            The added animation for method chaining
        """
        self.animations.append(animation)
        animation.start()
        return animation
        
    def remove_animation(self, animation: Animation) -> bool:
        """Remove an animation from the manager.
        
        Args:
            animation: The animation to remove
            
        Returns:
            True if the animation was removed, False otherwise
        """
        if animation in self.animations:
            self.animations.remove(animation)
            return True
        return False
        
    def clear_animations(self):
        """Remove all animations."""
        self.animations.clear()
        
    def update(self):
        """Update all animations.
        
        This should be called once per frame.
        """
        current_time = time.time()
        dt = current_time - self.last_update_time
        self.last_update_time = current_time
        
        # Update all animations and remove finished ones
        self.animations = [anim for anim in self.animations if anim.update(dt)]
        
    def create_property_animation(
        self, 
        target: Any, 
        property_name: str, 
        start_value: Any, 
        end_value: Any,
        duration: float = 1.0, 
        easing: EasingType = EasingType.LINEAR
    ) -> PropertyAnimation:
        """Create and start a property animation.
        
        Args:
            target: Object whose property will be animated
            property_name: Name of the property to animate
            start_value: Starting value
            end_value: Ending value
            duration: Duration in seconds
            easing: Easing function to use
            
        Returns:
            The created animation
        """
        animation = PropertyAnimation(
            target, property_name, start_value, end_value, duration, easing
        )
        return self.add_animation(animation)
        
    def create_sequence(self, animations: List[Animation]) -> SequenceAnimation:
        """Create and start a sequence animation.
        
        Args:
            animations: List of animations to run in sequence
            
        Returns:
            The created animation
        """
        animation = SequenceAnimation(animations)
        return self.add_animation(animation)
        
    def create_parallel(self, animations: List[Animation]) -> ParallelAnimation:
        """Create and start a parallel animation.
        
        Args:
            animations: List of animations to run in parallel
            
        Returns:
            The created animation
        """
        animation = ParallelAnimation(animations)
        return self.add_animation(animation)


# Singleton instance
animation_manager = AnimationManager()
