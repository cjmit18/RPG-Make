#!/usr/bin/env python3
"""
Renderer
=======

This module defines the base renderer class and Tkinter implementation.
"""

import tkinter as tk
from tkinter import ttk, Canvas
from typing import Any, Dict, List, Optional, Tuple, Union, Callable

from logs.logs import get_logger
from .render_types import (
    RenderCommand, RenderLayer, RenderPriority, Rect, Color,
    BLACK, WHITE, RED, GREEN, BLUE
)
from .render_pipeline import RenderPipeline

# Set up logger
logger = get_logger("rendering.renderer")


class Renderer:
    """Base class for renderers."""
    
    def __init__(self):
        """Initialize the renderer."""
        self.pipeline = RenderPipeline()
        
    def begin_frame(self):
        """Begin a new frame.
        
        This should be called at the start of each frame.
        """
        self.pipeline.clear_commands()
        
    def submit_command(self, command: RenderCommand):
        """Submit a render command to the pipeline.
        
        Args:
            command: The render command to submit
        """
        self.pipeline.add_command(command)
        
    def end_frame(self):
        """End the current frame and render it.
        
        This should be called at the end of each frame after all commands
        have been submitted.
        """
        commands = self.pipeline.process()
        self._render_commands(commands)
        
    def _render_commands(self, commands: List[RenderCommand]):
        """Render the given commands.
        
        This should be implemented by subclasses.
        
        Args:
            commands: The render commands to render
        """
        raise NotImplementedError("Subclasses must implement _render_commands")


class TkRenderer(Renderer):
    """A renderer implementation using Tkinter Canvas."""
    
    def __init__(self, canvas: Canvas, width: int = 800, height: int = 600):
        """Initialize the Tkinter renderer.
        
        Args:
            canvas: The Tkinter canvas to render to
            width: The canvas width
            height: The canvas height
        """
        super().__init__()
        self.canvas = canvas
        self.width = width
        self.height = height
        self._shapes = {}  # Maps object IDs to canvas shape IDs for updating
        
        # Configure the canvas
        self.canvas.config(width=self.width, height=self.height)
        
    def set_dimensions(self, width: int, height: int):
        """Set the canvas dimensions.
        
        Args:
            width: The new width
            height: The new height
        """
        self.width = width
        self.height = height
        self.canvas.config(width=self.width, height=self.height)
        
    def _render_commands(self, commands: List[RenderCommand]):
        """Render the given commands to the Tkinter canvas.
        
        Args:
            commands: The render commands to render
        """
        # Clear the canvas
        self.canvas.delete("all")
        
        # Process each command
        for cmd in commands:
            self._process_command(cmd)
            
    def _process_command(self, command: RenderCommand):
        """Process a single render command.
        
        Args:
            command: The render command to process
        """
        data = command.data
        cmd_type = data.get("type", "")
        
        if cmd_type == "rect":
            self._draw_rect(data)
        elif cmd_type == "text":
            self._draw_text(data)
        elif cmd_type == "line":
            self._draw_line(data)
        elif cmd_type == "image":
            self._draw_image(data)
        elif cmd_type == "circle":
            self._draw_circle(data)
        elif cmd_type == "polygon":
            self._draw_polygon(data)
        elif cmd_type == "clear":
            self._clear_area(data)
            
    def _draw_rect(self, data: Dict[str, Any]):
        """Draw a rectangle.
        
        Args:
            data: The rectangle data:
                x, y: The top-left corner
                width, height: The dimensions
                color: The fill color
                outline_color: The outline color (optional)
                outline_width: The outline width (optional)
                radius: The corner radius (optional)
                tags: Canvas tags (optional)
                object_id: Object ID for updating (optional)
        """
        x = data.get("x", 0)
        y = data.get("y", 0)
        width = data.get("width", 10)
        height = data.get("height", 10)
        color = data.get("color", BLACK)
        outline_color = data.get("outline_color", None)
        outline_width = data.get("outline_width", 1)
        radius = data.get("radius", 0)
        tags = data.get("tags", None)
        object_id = data.get("object_id", None)
        
        # Convert colors to hex
        fill = color.as_hex() if color else ""
        outline = outline_color.as_hex() if outline_color else ""
        
        # Draw the rectangle
        if radius > 0:
            # Rounded rectangle (approximate with arcs and lines)
            r = radius
            shape_id = self.canvas.create_polygon(
                x+r, y, x+width-r, y, x+width, y+r, x+width, y+height-r,
                x+width-r, y+height, x+r, y+height, x, y+height-r, x, y+r,
                fill=fill, outline=outline, width=outline_width,
                smooth=True, tags=tags
            )
        else:
            # Regular rectangle
            shape_id = self.canvas.create_rectangle(
                x, y, x+width, y+height,
                fill=fill, outline=outline, width=outline_width,
                tags=tags
            )
            
        # Store the shape ID if an object ID was provided
        if object_id:
            self._shapes[object_id] = shape_id
            
    def _draw_text(self, data: Dict[str, Any]):
        """Draw text.
        
        Args:
            data: The text data:
                x, y: The position
                text: The text to draw
                color: The text color
                font: The font (name, size, style)
                anchor: The text anchor (default: "center")
                tags: Canvas tags (optional)
                object_id: Object ID for updating (optional)
        """
        x = data.get("x", 0)
        y = data.get("y", 0)
        text = data.get("text", "")
        color = data.get("color", BLACK)
        font_data = data.get("font", ("Arial", 12, "normal"))
        anchor = data.get("anchor", "center")
        tags = data.get("tags", None)
        object_id = data.get("object_id", None)
        
        # Convert font tuple to Tkinter font string
        font_name, font_size, font_style = font_data
        font = (font_name, font_size, font_style)
        
        # Convert color to hex
        fill = color.as_hex()
        
        # Draw the text
        shape_id = self.canvas.create_text(
            x, y, text=text, fill=fill, font=font, anchor=anchor, tags=tags
        )
        
        # Store the shape ID if an object ID was provided
        if object_id:
            self._shapes[object_id] = shape_id
            
    def _draw_line(self, data: Dict[str, Any]):
        """Draw a line.
        
        Args:
            data: The line data:
                points: List of (x, y) points
                color: The line color
                width: The line width
                dash: Dash pattern (optional)
                tags: Canvas tags (optional)
                object_id: Object ID for updating (optional)
        """
        points = data.get("points", [(0, 0), (10, 10)])
        color = data.get("color", BLACK)
        width = data.get("width", 1)
        dash = data.get("dash", None)
        tags = data.get("tags", None)
        object_id = data.get("object_id", None)
        
        # Convert color to hex
        fill = color.as_hex()
        
        # Flatten the points list for Tkinter
        flat_points = []
        for point in points:
            flat_points.extend(point)
            
        # Draw the line
        shape_id = self.canvas.create_line(
            *flat_points, fill=fill, width=width, dash=dash, tags=tags
        )
        
        # Store the shape ID if an object ID was provided
        if object_id:
            self._shapes[object_id] = shape_id
            
    def _draw_circle(self, data: Dict[str, Any]):
        """Draw a circle.
        
        Args:
            data: The circle data:
                x, y: The center point
                radius: The radius
                color: The fill color
                outline_color: The outline color (optional)
                outline_width: The outline width (optional)
                tags: Canvas tags (optional)
                object_id: Object ID for updating (optional)
        """
        x = data.get("x", 0)
        y = data.get("y", 0)
        radius = data.get("radius", 10)
        color = data.get("color", BLACK)
        outline_color = data.get("outline_color", None)
        outline_width = data.get("outline_width", 1)
        tags = data.get("tags", None)
        object_id = data.get("object_id", None)
        
        # Convert colors to hex
        fill = color.as_hex() if color else ""
        outline = outline_color.as_hex() if outline_color else ""
        
        # Draw the circle (as an oval in Tkinter)
        shape_id = self.canvas.create_oval(
            x-radius, y-radius, x+radius, y+radius,
            fill=fill, outline=outline, width=outline_width, tags=tags
        )
        
        # Store the shape ID if an object ID was provided
        if object_id:
            self._shapes[object_id] = shape_id
            
    def _draw_polygon(self, data: Dict[str, Any]):
        """Draw a polygon.
        
        Args:
            data: The polygon data:
                points: List of (x, y) points
                color: The fill color
                outline_color: The outline color (optional)
                outline_width: The outline width (optional)
                smooth: Whether to smooth the polygon (optional)
                tags: Canvas tags (optional)
                object_id: Object ID for updating (optional)
        """
        points = data.get("points", [(0, 0), (10, 0), (10, 10), (0, 10)])
        color = data.get("color", BLACK)
        outline_color = data.get("outline_color", None)
        outline_width = data.get("outline_width", 1)
        smooth = data.get("smooth", False)
        tags = data.get("tags", None)
        object_id = data.get("object_id", None)
        
        # Convert colors to hex
        fill = color.as_hex() if color else ""
        outline = outline_color.as_hex() if outline_color else ""
        
        # Flatten the points list for Tkinter
        flat_points = []
        for point in points:
            flat_points.extend(point)
            
        # Draw the polygon
        shape_id = self.canvas.create_polygon(
            *flat_points, fill=fill, outline=outline,
            width=outline_width, smooth=smooth, tags=tags
        )
        
        # Store the shape ID if an object ID was provided
        if object_id:
            self._shapes[object_id] = shape_id
            
    def _draw_image(self, data: Dict[str, Any]):
        """Draw an image.
        
        Args:
            data: The image data:
                x, y: The top-left corner
                image: The image object
                anchor: The image anchor (default: "nw")
                tags: Canvas tags (optional)
                object_id: Object ID for updating (optional)
        """
        x = data.get("x", 0)
        y = data.get("y", 0)
        image = data.get("image", None)
        anchor = data.get("anchor", "nw")
        tags = data.get("tags", None)
        object_id = data.get("object_id", None)
        
        if image:
            # Draw the image
            shape_id = self.canvas.create_image(
                x, y, image=image, anchor=anchor, tags=tags
            )
            
            # Store the shape ID if an object ID was provided
            if object_id:
                self._shapes[object_id] = shape_id
                
    def _clear_area(self, data: Dict[str, Any]):
        """Clear an area of the canvas.
        
        Args:
            data: The clear data:
                x, y: The top-left corner
                width, height: The dimensions
                tags: Canvas tags to clear (optional)
        """
        x = data.get("x", 0)
        y = data.get("y", 0)
        width = data.get("width", self.width)
        height = data.get("height", self.height)
        tags = data.get("tags", None)
        
        if tags:
            # Clear specific tags
            self.canvas.delete(tags)
        else:
            # Create a white rectangle to clear the area
            self.canvas.create_rectangle(
                x, y, x+width, y+height,
                fill="white", outline="", tags="clear"
            )
            
    def update_shape(self, object_id: str, **kwargs):
        """Update an existing shape on the canvas.
        
        Args:
            object_id: The ID of the object to update
            **kwargs: The properties to update
        """
        if object_id in self._shapes:
            shape_id = self._shapes[object_id]
            self.canvas.itemconfigure(shape_id, **kwargs)
            
    def add_canvas_callback(self, event_type: str, callback: Callable, tag=None):
        """Add a callback for canvas events.
        
        Args:
            event_type: The event type (e.g., "<Button-1>")
            callback: The callback function
            tag: Optional tag to bind to specific items
        """
        if tag:
            self.canvas.tag_bind(tag, event_type, callback)
        else:
            self.canvas.bind(event_type, callback)
            
    def remove_canvas_callback(self, event_type: str, tag=None):
        """Remove a callback for canvas events.
        
        Args:
            event_type: The event type (e.g., "<Button-1>")
            tag: Optional tag to unbind from specific items
        """
        if tag:
            self.canvas.tag_unbind(tag, event_type)
        else:
            self.canvas.unbind(event_type)
