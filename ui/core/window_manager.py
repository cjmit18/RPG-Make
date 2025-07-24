"""
Window Manager
==============

A comprehensive window management system for creating and managing
tkinter application windows with consistent styling and layout.
"""

import tkinter as tk
from tkinter import ttk
from typing import Dict, Any, Optional, Callable
from dataclasses import dataclass


@dataclass
class WindowConfig:
    """Configuration for window creation."""
    title: str = "Application"
    geometry: str = "800x600"
    theme: str = "modern"
    center_on_screen: bool = True
    resizable: bool = True
    min_size: tuple = (400, 300)


class WindowManager:
    """
    Manages application windows with consistent styling and layout.
    
    Provides utilities for creating main windows, standard layouts,
    and handling window events.
    """
    
    def __init__(self, config: WindowConfig):
        """Initialize the window manager."""
        self.config = config
        self.root: Optional[tk.Tk] = None
        self.callbacks: Dict[str, Callable] = {}
        
    def create_window(self) -> tk.Tk:
        """Create and configure the main application window."""
        self.root = tk.Tk()
        self.root.title(self.config.title)
        self.root.geometry(self.config.geometry)
        
        # Set minimum size
        if self.config.min_size:
            self.root.minsize(*self.config.min_size)
        
        # Configure resizing
        if not self.config.resizable:
            self.root.resizable(False, False)
        
        # Center window if requested
        if self.config.center_on_screen:
            self._center_window()
        
        # Apply theme
        self._apply_theme()
        
        # Set up window close handling
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)
        
        return self.root
    
    def create_standard_layout(self) -> Dict[str, tk.Frame]:
        """
        Create a standard application layout with header, content, and status areas.
        
        Returns:
            Dictionary with 'header', 'content', and 'status' frames
        """
        if not self.root:
            raise ValueError("Window must be created first")
        
        # Main container
        main_frame = tk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Header area
        header_frame = tk.Frame(main_frame, height=50, bg="#f0f0f0")
        header_frame.pack(fill=tk.X, pady=(0, 5))
        header_frame.pack_propagate(False)
        
        # Content area
        content_frame = tk.Frame(main_frame)
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Status bar
        status_frame = tk.Frame(main_frame, height=25, bg="#e0e0e0", relief=tk.SUNKEN, bd=1)
        status_frame.pack(fill=tk.X, pady=(5, 0))
        status_frame.pack_propagate(False)
        
        return {
            'header': header_frame,
            'content': content_frame,
            'status': status_frame
        }
    
    def register_callback(self, event: str, callback: Callable) -> None:
        """Register a callback for window events."""
        self.callbacks[event] = callback
    
    def get_root(self) -> Optional[tk.Tk]:
        """Get the root window."""
        return self.root
    
    def run(self) -> None:
        """Start the main event loop."""
        if not self.root:
            raise ValueError("Window must be created first")
        
        self.root.mainloop()
    
    def _center_window(self) -> None:
        """Center the window on screen."""
        if not self.root:
            return
        
        self.root.update_idletasks()
        
        # Get window size
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        
        # Get screen size
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        
        # Calculate position
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2
        
        self.root.geometry(f"{width}x{height}+{x}+{y}")
    
    def _apply_theme(self) -> None:
        """Apply the selected theme."""
        if self.config.theme == "modern":
            # Configure modern theme colors
            self.root.configure(bg="#ffffff")
            
            # Configure ttk style
            style = ttk.Style()
            style.theme_use('clam')
            
            # Customize colors
            style.configure('TLabel', background='#ffffff')
            style.configure('TFrame', background='#ffffff')
            style.configure('TNotebook', background='#f0f0f0')
            style.configure('TNotebook.Tab', padding=[10, 5])
    
    def _on_close(self) -> None:
        """Handle window close event."""
        # Call before_close callback if registered
        if 'before_close' in self.callbacks:
            if not self.callbacks['before_close']():
                return  # Don't close if callback returns False
        
        # Call on_close callback if registered
        if 'on_close' in self.callbacks:
            self.callbacks['on_close']()
        
        # Destroy window
        if self.root:
            self.root.destroy()
