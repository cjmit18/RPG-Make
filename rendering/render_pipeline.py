#!/usr/bin/env python3
"""
Render Pipeline
=============

This module defines the render pipeline that processes render commands.
"""

import tkinter as tk
from typing import Dict, List, Optional, Set

from .render_types import RenderCommand, RenderLayer, RenderPriority


class RenderPipeline:
    """The render pipeline processes and orders render commands."""
    
    def __init__(self):
        """Initialize the render pipeline."""
        self.commands: List[RenderCommand] = []
        self.enabled_layers: Set[RenderLayer] = set(RenderLayer)
        
    def add_command(self, command: RenderCommand):
        """Add a render command to the pipeline.
        
        Args:
            command: The render command to add
        """
        self.commands.append(command)
        
    def clear_commands(self):
        """Clear all render commands."""
        self.commands = []
        
    def clear_layer(self, layer: RenderLayer):
        """Clear all render commands for a specific layer.
        
        Args:
            layer: The layer to clear
        """
        self.commands = [cmd for cmd in self.commands if cmd.layer != layer]
        
    def enable_layer(self, layer: RenderLayer):
        """Enable rendering of a specific layer.
        
        Args:
            layer: The layer to enable
        """
        self.enabled_layers.add(layer)
        
    def disable_layer(self, layer: RenderLayer):
        """Disable rendering of a specific layer.
        
        Args:
            layer: The layer to disable
        """
        if layer in self.enabled_layers:
            self.enabled_layers.remove(layer)
            
    def is_layer_enabled(self, layer: RenderLayer) -> bool:
        """Check if a layer is enabled.
        
        Args:
            layer: The layer to check
            
        Returns:
            True if the layer is enabled, False otherwise
        """
        return layer in self.enabled_layers
        
    def process(self) -> List[RenderCommand]:
        """Process the render commands and return them in render order.
        
        Returns:
            A list of render commands in the correct order for rendering
        """
        # Filter out commands for disabled layers
        filtered_commands = [
            cmd for cmd in self.commands
            if cmd.layer in self.enabled_layers
        ]
        
        # Sort by layer and then by priority within each layer
        sorted_commands = sorted(
            filtered_commands,
            key=lambda cmd: (cmd.layer.value, cmd.priority.value)
        )
        
        return sorted_commands
