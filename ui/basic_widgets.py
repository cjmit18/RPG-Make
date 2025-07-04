#!/usr/bin/env python3
"""
Basic Widgets
============

This module defines basic UI widgets that build on the BaseWidget class.
"""

import tkinter as tk
from tkinter import ttk
from typing import Callable, Dict, List, Optional, Union

from .base_widget import BaseWidget
from .event_types import UIEvent, UIEventType, ClickEvent, ValueChangeEvent


class Button(BaseWidget):
    """A button widget."""
    
    def __init__(self, parent=None, **kwargs):
        """Initialize a button widget.
        
        Args:
            parent: The parent widget
            **kwargs: Additional arguments:
                text: The button text
                command: The function to call when clicked
                style: The ttk style to use
        """
        super().__init__(parent, **kwargs)
        self.text = kwargs.get('text', 'Button')
        self.command = kwargs.get('command', None)
        self.style = kwargs.get('style', None)
        
        # Handle click events
        self.on(UIEventType.CLICK, self._handle_click)
        
    def create_widget(self, tk_parent) -> Union[tk.Widget, ttk.Widget]:
        """Create the actual Tkinter button widget."""
        def on_click():
            # Generate a click event
            event = ClickEvent(source=self, position=None)
            self.trigger_event(event)
        
        kwargs = {
            'text': self.text,
            'command': on_click,
        }
        
        if self.style:
            kwargs['style'] = self.style
            
        self._tk_widget = ttk.Button(tk_parent, **kwargs)
        return self._tk_widget
        
    def _handle_click(self, event: ClickEvent):
        """Handle a click event."""
        if self.command and self.enabled:
            self.command()
            
    def set_text(self, text: str):
        """Set the button text."""
        self.text = text
        if self._tk_widget:
            self._tk_widget.configure(text=text)
            
    def set_command(self, command: Callable):
        """Set the button command."""
        self.command = command


class Label(BaseWidget):
    """A label widget."""
    
    def __init__(self, parent=None, **kwargs):
        """Initialize a label widget.
        
        Args:
            parent: The parent widget
            **kwargs: Additional arguments:
                text: The label text
                style: The ttk style to use
        """
        super().__init__(parent, **kwargs)
        self.text = kwargs.get('text', '')
        self.style = kwargs.get('style', None)
        
    def create_widget(self, tk_parent) -> Union[tk.Widget, ttk.Widget]:
        """Create the actual Tkinter label widget."""
        kwargs = {
            'text': self.text,
        }
        
        if self.style:
            kwargs['style'] = self.style
            
        self._tk_widget = ttk.Label(tk_parent, **kwargs)
        return self._tk_widget
        
    def set_text(self, text: str):
        """Set the label text."""
        self.text = text
        if self._tk_widget:
            self._tk_widget.configure(text=text)


class TextInput(BaseWidget):
    """A text input widget."""
    
    def __init__(self, parent=None, **kwargs):
        """Initialize a text input widget.
        
        Args:
            parent: The parent widget
            **kwargs: Additional arguments:
                text: The initial text
                style: The ttk style to use
                width: The width in characters
                on_change: Callback for when the text changes
        """
        super().__init__(parent, **kwargs)
        self.text = kwargs.get('text', '')
        self.style = kwargs.get('style', None)
        self.width = kwargs.get('width', 20)
        self.on_change = kwargs.get('on_change', None)
        self.text_var = None  # Will be created when the widget is created
        
    def create_widget(self, tk_parent) -> Union[tk.Widget, ttk.Widget]:
        """Create the actual Tkinter entry widget."""
        self.text_var = tk.StringVar(value=self.text)
        
        def on_text_change(*args):
            old_value = self.text
            new_value = self.text_var.get()
            self.text = new_value
            
            # Generate a value change event
            event = ValueChangeEvent(
                source=self,
                old_value=old_value,
                new_value=new_value
            )
            self.trigger_event(event)
            
            # Call the on_change callback if provided
            if self.on_change:
                self.on_change(new_value)
        
        # Register the callback for when the text changes
        self.text_var.trace_add('write', on_text_change)
        
        kwargs = {
            'textvariable': self.text_var,
            'width': self.width,
        }
        
        if self.style:
            kwargs['style'] = self.style
            
        self._tk_widget = ttk.Entry(tk_parent, **kwargs)
        return self._tk_widget
        
    def get_text(self) -> str:
        """Get the current text."""
        if self.text_var:
            return self.text_var.get()
        return self.text
        
    def set_text(self, text: str):
        """Set the text input text."""
        self.text = text
        if self.text_var:
            self.text_var.set(text)


class Panel(BaseWidget):
    """A panel widget that can contain other widgets."""
    
    def __init__(self, parent=None, **kwargs):
        """Initialize a panel widget.
        
        Args:
            parent: The parent widget
            **kwargs: Additional arguments:
                title: Optional title for the panel
                style: The ttk style to use
                layout: The layout style ('pack', 'grid', 'place')
                pack_args: Arguments for pack layout
                grid_args: Arguments for grid layout
                place_args: Arguments for place layout
        """
        super().__init__(parent, **kwargs)
        self.title = kwargs.get('title', None)
        self.style = kwargs.get('style', None)
        self.layout = kwargs.get('layout', 'pack')
        self.pack_args = kwargs.get('pack_args', {})
        self.grid_args = kwargs.get('grid_args', {})
        self.place_args = kwargs.get('place_args', {})
        
    def create_widget(self, tk_parent) -> Union[tk.Widget, ttk.Widget]:
        """Create the actual Tkinter frame or labelframe widget."""
        kwargs = {}
        
        if self.style:
            kwargs['style'] = self.style
            
        if self.title:
            self._tk_widget = ttk.LabelFrame(tk_parent, text=self.title, **kwargs)
        else:
            self._tk_widget = ttk.Frame(tk_parent, **kwargs)
            
        return self._tk_widget
        
    def add_child(self, child: BaseWidget) -> BaseWidget:
        """Add a child widget to this panel.
        
        Override to handle layout management.
        """
        super().add_child(child)
        
        # Create the child's tkinter widget if the panel's widget exists
        if self._tk_widget and not child.tk_widget:
            child_tk_widget = child.create_widget(self._tk_widget)
            
            # Position the widget according to the layout style
            if self.layout == 'pack':
                child_tk_widget.pack(**self.pack_args)
            elif self.layout == 'grid':
                # Use child-specific grid args if available, otherwise default
                grid_args = getattr(child, 'grid_args', self.grid_args)
                child_tk_widget.grid(**grid_args)
            elif self.layout == 'place':
                # Use child-specific place args if available, otherwise default
                place_args = getattr(child, 'place_args', self.place_args)
                child_tk_widget.place(**place_args)
                
        return child
        
    def set_title(self, title: str):
        """Set the panel title."""
        self.title = title
        if self._tk_widget and isinstance(self._tk_widget, ttk.LabelFrame):
            self._tk_widget.configure(text=title)
