#!/usr/bin/env python3
"""
Base Widget
==========

This module defines the base widget class for all UI components.
"""

from abc import ABC, abstractmethod
from typing import Any, Callable, Dict, List, Optional, Tuple, Type, Union
import tkinter as tk
from tkinter import ttk

from logs.logs import get_logger
from .event_types import UIEvent, UIEventType

# Set up logger
logger = get_logger("ui.base_widget")


class BaseWidget(ABC):
    """Base class for all UI widgets.
    
    This abstract class defines the common interface and behavior for all
    UI widgets in the system.
    """
    
    def __init__(self, parent=None, **kwargs):
        """Initialize the base widget.
        
        Args:
            parent: The parent widget or None for top-level widgets
            **kwargs: Additional keyword arguments to configure the widget
        """
        self.parent = parent
        self.children: List[BaseWidget] = []
        self.event_handlers: Dict[UIEventType, List[Callable[[UIEvent], None]]] = {}
        self.widget_id: str = kwargs.get('id', None)
        self.visible: bool = True
        self.enabled: bool = True
        self._tk_widget = None  # Reference to the actual tkinter widget
        
    @property
    def tk_widget(self):
        """Get the Tkinter widget associated with this UI widget."""
        return self._tk_widget
    
    @abstractmethod
    def create_widget(self, tk_parent) -> Union[tk.Widget, ttk.Widget]:
        """Create the actual Tkinter widget.
        
        This method should be implemented by subclasses to create the
        specific Tkinter widget represented by this UI widget.
        
        Args:
            tk_parent: The Tkinter parent widget
            
        Returns:
            The created Tkinter widget
        """
        pass
    
    def add_child(self, child: 'BaseWidget') -> 'BaseWidget':
        """Add a child widget to this widget.
        
        Args:
            child: The child widget to add
            
        Returns:
            The added child widget for method chaining
        """
        self.children.append(child)
        child.parent = self
        return child
    
    def remove_child(self, child: 'BaseWidget') -> bool:
        """Remove a child widget from this widget.
        
        Args:
            child: The child widget to remove
            
        Returns:
            True if the child was removed, False otherwise
        """
        if child in self.children:
            self.children.remove(child)
            return True
        return False
    
    def on(self, event_type: UIEventType, handler: Callable[[UIEvent], None]):
        """Register an event handler for the specified event type.
        
        Args:
            event_type: The type of event to handle
            handler: The function to call when the event occurs
            
        Returns:
            self for method chaining
        """
        if event_type not in self.event_handlers:
            self.event_handlers[event_type] = []
        self.event_handlers[event_type].append(handler)
        return self
    
    def off(self, event_type: UIEventType, handler: Optional[Callable] = None):
        """Remove an event handler for the specified event type.
        
        Args:
            event_type: The type of event to remove the handler for
            handler: The handler to remove, or None to remove all handlers
            
        Returns:
            self for method chaining
        """
        if event_type not in self.event_handlers:
            return self
            
        if handler is None:
            # Remove all handlers for this event type
            self.event_handlers[event_type] = []
        else:
            # Remove specific handler
            handlers = self.event_handlers[event_type]
            if handler in handlers:
                handlers.remove(handler)
                
        return self
    
    def trigger_event(self, event: UIEvent):
        """Trigger an event on this widget.
        
        This will call all registered handlers for the event type.
        
        Args:
            event: The event to trigger
        """
        if event.type in self.event_handlers:
            for handler in self.event_handlers[event.type]:
                handler(event)
                
        # Propagate to parent if allowed
        if event.propagate and self.parent:
            self.parent.trigger_event(event)
            
    def show(self):
        """Show this widget."""
        self.visible = True
        if self._tk_widget:
            self._tk_widget.pack()  # Basic show, subclasses may override
            
    def hide(self):
        """Hide this widget."""
        self.visible = False
        if self._tk_widget:
            self._tk_widget.pack_forget()  # Basic hide, subclasses may override
            
    def enable(self):
        """Enable this widget."""
        self.enabled = True
        if self._tk_widget:
            self._tk_widget.configure(state='normal')
            
    def disable(self):
        """Disable this widget."""
        self.enabled = False
        if self._tk_widget:
            self._tk_widget.configure(state='disabled')
            
    def update(self):
        """Update this widget's visual state.
        
        This should be called when the underlying data changes.
        """
        pass  # Default implementation does nothing, subclasses should override
