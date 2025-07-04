#!/usr/bin/env python3
"""
UI Manager
=========

This module defines the UI manager class that coordinates all UI components.
"""

import tkinter as tk
from tkinter import ttk
from typing import Dict, List, Optional, Type, Any

from logs.logs import get_logger
from .base_widget import BaseWidget
from .event_types import UIEvent, UIEventType
from .animation import animation_manager
from .theme import theme_manager

# Set up logger
logger = get_logger("ui.manager")


class UIManager:
    """Manager class for all UI components.
    
    The UIManager is responsible for creating and managing UI widgets,
    handling events, and coordinating the overall UI system.
    """
    
    def __init__(self, root=None):
        """Initialize the UI manager.
        
        Args:
            root: The root Tkinter window, or None to create a new one
        """
        self.root = root or tk.Tk()
        self.widgets: Dict[str, BaseWidget] = {}  # ID -> widget mapping
        self.is_initialized = False
        self.update_callbacks: List[callable] = []
        
        # Animation system
        self.animation_manager = animation_manager
        
        # Theme system
        self.theme_manager = theme_manager
        
        logger.info("UI Manager initialized")
        
    def initialize(self, title: str = "Game UI", width: int = 800, 
                 height: int = 600):
        """Initialize the UI system.
        
        This sets up the root window and prepares the UI system for use.
        
        Args:
            title: The window title
            width: The window width
            height: The window height
        """
        if self.is_initialized:
            logger.warning("UI Manager already initialized")
            return
            
        self.root.title(title)
        self.root.geometry(f"{width}x{height}")
        
        # Set up style
        self.style = ttk.Style()
        
        # Configure theme
        self.theme_manager.set_tk_style(self.style)
        
        # Mark as initialized
        self.is_initialized = True
        logger.info(f"UI initialized with dimensions {width}x{height}")
        
        # Start the update loop
        self._setup_update_loop()
        
    def _setup_update_loop(self, interval_ms: int = 100):
        """Set up the periodic update loop.
        
        Args:
            interval_ms: The update interval in milliseconds
        """
        def update_loop():
            # Update animations
            self.animation_manager.update()
            
            # Update callbacks
            for callback in self.update_callbacks:
                try:
                    callback()
                except Exception as e:
                    logger.error(f"Error in UI update callback: {e}")
                    
            # Schedule the next update
            self.root.after(interval_ms, update_loop)
        
        logger.debug(f"Setting up UI update loop with interval {interval_ms}ms")    
        # Start the update loop
        self.root.after(interval_ms, update_loop)
        
    def add_update_callback(self, callback: callable):
        """Add a callback to be called on each UI update cycle.
        
        Args:
            callback: The function to call
        """
        self.update_callbacks.append(callback)
        
    def remove_update_callback(self, callback: callable):
        """Remove a callback from the update cycle.
        
        Args:
            callback: The function to remove
        """
        if callback in self.update_callbacks:
            self.update_callbacks.remove(callback)
            
    def register_widget(self, widget: BaseWidget, widget_id: str = None):
        """Register a widget with the UI manager.
        
        This allows the widget to be looked up by ID later.
        
        Args:
            widget: The widget to register
            widget_id: The ID to use, or None to use the widget's ID
        """
        widget_id = widget_id or widget.widget_id
        if not widget_id:
            logger.warning("Widget registered without an ID")
            return
        
        if widget_id in self.widgets:
            logger.warning(f"Widget ID '{widget_id}' already registered, overwriting")
            
        self.widgets[widget_id] = widget
        logger.debug(f"Registered widget '{widget_id}' of type {type(widget).__name__}")
        if not widget_id:
            raise ValueError("Widget must have an ID to be registered")
            
        self.widgets[widget_id] = widget
        
    def create_widget(self, widget_class: Type[BaseWidget], parent=None, **kwargs) -> BaseWidget:
        """Create a new widget of the specified type.
        
        Args:
            widget_class: The widget class to create
            parent: The parent widget or None for top-level widgets
            **kwargs: Additional keyword arguments to pass to the widget constructor
            
        Returns:
            The created widget
        """
        widget = widget_class(parent=parent, **kwargs)
        
        # Register the widget if it has an ID
        if widget.widget_id:
            self.register_widget(widget)
            
        # If it has a parent, add it as a child
        if parent and isinstance(parent, BaseWidget):
            parent.add_child(widget)
            
        return widget
    
    def get_widget(self, widget_id: str) -> Optional[BaseWidget]:
        """Get a widget by its ID.
        
        Args:
            widget_id: The ID of the widget to get
            
        Returns:
            The widget or None if not found
        """
        return self.widgets.get(widget_id)
    
    def broadcast_event(self, event: UIEvent):
        """Broadcast an event to all registered widgets.
        
        Args:
            event: The event to broadcast
        """
        for widget in self.widgets.values():
            widget.trigger_event(event)
            
    def run(self):
        """Run the UI main loop.
        
        This method blocks until the UI is closed.
        """
        if not self.is_initialized:
            self.initialize()
            
        self.root.mainloop()
        
    def quit(self):
        """Quit the UI system."""
        self.root.quit()
        
    def update(self):
        """Update all widgets.
        
        This is typically called when the game state changes.
        """
        for widget in self.widgets.values():
            widget.update()
            
    def set_theme(self, theme_name: str) -> bool:
        """Set the UI theme.
        
        Args:
            theme_name: The name of the theme to use
            
        Returns:
            True if the theme was set, False if not found
        """
        return self.theme_manager.set_theme(theme_name)
        
    def create_animation(self, *args, **kwargs):
        """Create an animation.
        
        This is a convenience method that delegates to the animation manager.
        
        Args:
            *args: Arguments to pass to the animation manager
            **kwargs: Keyword arguments to pass to the animation manager
            
        Returns:
            The created animation
        """
        return self.animation_manager.create_property_animation(*args, **kwargs)
