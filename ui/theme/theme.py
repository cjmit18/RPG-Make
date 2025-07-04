#!/usr/bin/env python3
"""
Theme System
==========

This module defines the theme system for the UI.
"""

from enum import Enum, auto
from typing import Dict, Optional, Tuple, Any
import tkinter as tk
from tkinter import ttk

from rendering.render_types import Color


class ThemeElement(Enum):
    """Enum defining UI theme elements."""
    BACKGROUND = auto()
    FOREGROUND = auto()
    TEXT = auto()
    ACCENT = auto()
    ACCENT_LIGHT = auto()
    ACCENT_DARK = auto()
    SUCCESS = auto()
    WARNING = auto()
    ERROR = auto()
    BORDER = auto()
    SHADOW = auto()
    HIGHLIGHT = auto()
    BUTTON = auto()
    BUTTON_HOVER = auto()
    BUTTON_ACTIVE = auto()
    BUTTON_DISABLED = auto()
    INPUT_BACKGROUND = auto()
    INPUT_FOREGROUND = auto()
    PANEL_BACKGROUND = auto()
    PANEL_TITLE = auto()


class Theme:
    """A UI theme with a set of colors and styles."""
    
    def __init__(self, name: str):
        """Initialize the theme.
        
        Args:
            name: The theme name
        """
        self.name = name
        self.colors: Dict[ThemeElement, Color] = {}
        self.fonts: Dict[str, Tuple[str, int, str]] = {}
        self.styles: Dict[str, Dict[str, Any]] = {}
        
    def set_color(self, element: ThemeElement, color: Color) -> 'Theme':
        """Set a color for a theme element.
        
        Args:
            element: The theme element
            color: The color to use
            
        Returns:
            self for method chaining
        """
        self.colors[element] = color
        return self
        
    def get_color(self, element: ThemeElement, default: Optional[Color] = None) -> Optional[Color]:
        """Get a color for a theme element.
        
        Args:
            element: The theme element
            default: Default color to return if not defined
            
        Returns:
            The color or default if not defined
        """
        return self.colors.get(element, default)
        
    def set_font(self, name: str, family: str, size: int, weight: str = "normal") -> 'Theme':
        """Set a font.
        
        Args:
            name: The font name
            family: The font family
            size: The font size
            weight: The font weight (normal, bold, etc.)
            
        Returns:
            self for method chaining
        """
        self.fonts[name] = (family, size, weight)
        return self
        
    def get_font(self, name: str, default: Optional[Tuple[str, int, str]] = None) -> Optional[Tuple[str, int, str]]:
        """Get a font.
        
        Args:
            name: The font name
            default: Default font to return if not defined
            
        Returns:
            The font or default if not defined
        """
        return self.fonts.get(name, default)
        
    def set_style(self, name: str, style_dict: Dict[str, Any]) -> 'Theme':
        """Set a style.
        
        Args:
            name: The style name
            style_dict: The style dictionary
            
        Returns:
            self for method chaining
        """
        self.styles[name] = style_dict
        return self
        
    def get_style(self, name: str, default: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
        """Get a style.
        
        Args:
            name: The style name
            default: Default style to return if not defined
            
        Returns:
            The style or default if not defined
        """
        return self.styles.get(name, default)
        
    def apply_to_tk(self, style: ttk.Style):
        """Apply the theme to a ttk Style object.
        
        Args:
            style: The ttk Style object
        """
        # Convert theme colors to Tkinter color strings
        tk_colors = {element: color.as_hex() for element, color in self.colors.items()}
        
        # Configure common styles
        style.configure(
            "TFrame", 
            background=tk_colors.get(ThemeElement.BACKGROUND, "#f0f0f0")
        )
        
        style.configure(
            "TLabel", 
            background=tk_colors.get(ThemeElement.BACKGROUND, "#f0f0f0"),
            foreground=tk_colors.get(ThemeElement.TEXT, "#000000")
        )
        
        style.configure(
            "TButton", 
            background=tk_colors.get(ThemeElement.BUTTON, "#d0d0d0"),
            foreground=tk_colors.get(ThemeElement.TEXT, "#000000")
        )
        
        style.map(
            "TButton",
            background=[
                ('active', tk_colors.get(ThemeElement.BUTTON_ACTIVE, "#b0b0b0")),
                ('disabled', tk_colors.get(ThemeElement.BUTTON_DISABLED, "#e0e0e0"))
            ],
            foreground=[
                ('disabled', "#a0a0a0")
            ]
        )
        
        style.configure(
            "TEntry", 
            background=tk_colors.get(ThemeElement.INPUT_BACKGROUND, "#ffffff"),
            foreground=tk_colors.get(ThemeElement.INPUT_FOREGROUND, "#000000"),
            fieldbackground=tk_colors.get(ThemeElement.INPUT_BACKGROUND, "#ffffff")
        )
        
        style.configure(
            "TLabelframe", 
            background=tk_colors.get(ThemeElement.PANEL_BACKGROUND, "#f0f0f0")
        )
        
        style.configure(
            "TLabelframe.Label", 
            background=tk_colors.get(ThemeElement.PANEL_BACKGROUND, "#f0f0f0"),
            foreground=tk_colors.get(ThemeElement.PANEL_TITLE, "#000000")
        )
        
        # Apply custom styles
        for name, style_dict in self.styles.items():
            style.configure(name, **style_dict)


class ThemeManager:
    """Manager for UI themes."""
    
    def __init__(self):
        """Initialize the theme manager."""
        self.themes: Dict[str, Theme] = {}
        self.current_theme: Optional[Theme] = None
        self.tk_style: Optional[ttk.Style] = None
        
    def register_theme(self, theme: Theme) -> 'ThemeManager':
        """Register a theme.
        
        Args:
            theme: The theme to register
            
        Returns:
            self for method chaining
        """
        self.themes[theme.name] = theme
        return self
        
    def set_theme(self, theme_name: str) -> bool:
        """Set the current theme.
        
        Args:
            theme_name: The name of the theme to set
            
        Returns:
            True if the theme was set, False if not found
        """
        if theme_name not in self.themes:
            return False
            
        self.current_theme = self.themes[theme_name]
        
        # Apply to Tkinter style if available
        if self.tk_style:
            self.current_theme.apply_to_tk(self.tk_style)
            
        return True
        
    def get_theme(self, theme_name: str) -> Optional[Theme]:
        """Get a theme by name.
        
        Args:
            theme_name: The name of the theme to get
            
        Returns:
            The theme or None if not found
        """
        return self.themes.get(theme_name)
        
    def get_current_theme(self) -> Optional[Theme]:
        """Get the current theme.
        
        Returns:
            The current theme or None if not set
        """
        return self.current_theme
        
    def set_tk_style(self, style: ttk.Style):
        """Set the ttk Style object to use for applying themes.
        
        Args:
            style: The ttk Style object
        """
        self.tk_style = style
        
        # Apply current theme if available
        if self.current_theme:
            self.current_theme.apply_to_tk(style)
            
    def create_default_themes(self):
        """Create and register default themes."""
        # Light theme
        light_theme = Theme("light")
        light_theme.set_color(ThemeElement.BACKGROUND, Color(240, 240, 240))
        light_theme.set_color(ThemeElement.FOREGROUND, Color(220, 220, 220))
        light_theme.set_color(ThemeElement.TEXT, Color(20, 20, 20))
        light_theme.set_color(ThemeElement.ACCENT, Color(66, 135, 245))
        light_theme.set_color(ThemeElement.ACCENT_LIGHT, Color(120, 169, 255))
        light_theme.set_color(ThemeElement.ACCENT_DARK, Color(25, 92, 198))
        light_theme.set_color(ThemeElement.SUCCESS, Color(40, 167, 69))
        light_theme.set_color(ThemeElement.WARNING, Color(255, 193, 7))
        light_theme.set_color(ThemeElement.ERROR, Color(220, 53, 69))
        light_theme.set_color(ThemeElement.BORDER, Color(200, 200, 200))
        light_theme.set_color(ThemeElement.SHADOW, Color(0, 0, 0, 30))
        light_theme.set_color(ThemeElement.HIGHLIGHT, Color(255, 255, 0, 100))
        light_theme.set_color(ThemeElement.BUTTON, Color(230, 230, 230))
        light_theme.set_color(ThemeElement.BUTTON_HOVER, Color(210, 210, 210))
        light_theme.set_color(ThemeElement.BUTTON_ACTIVE, Color(180, 180, 180))
        light_theme.set_color(ThemeElement.BUTTON_DISABLED, Color(200, 200, 200))
        light_theme.set_color(ThemeElement.INPUT_BACKGROUND, Color(255, 255, 255))
        light_theme.set_color(ThemeElement.INPUT_FOREGROUND, Color(20, 20, 20))
        light_theme.set_color(ThemeElement.PANEL_BACKGROUND, Color(240, 240, 240))
        light_theme.set_color(ThemeElement.PANEL_TITLE, Color(20, 20, 20))
        
        light_theme.set_font("default", "Helvetica", 10, "normal")
        light_theme.set_font("title", "Helvetica", 14, "bold")
        light_theme.set_font("small", "Helvetica", 8, "normal")
        
        self.register_theme(light_theme)
        
        # Dark theme
        dark_theme = Theme("dark")
        dark_theme.set_color(ThemeElement.BACKGROUND, Color(40, 40, 40))
        dark_theme.set_color(ThemeElement.FOREGROUND, Color(60, 60, 60))
        dark_theme.set_color(ThemeElement.TEXT, Color(220, 220, 220))
        dark_theme.set_color(ThemeElement.ACCENT, Color(66, 135, 245))
        dark_theme.set_color(ThemeElement.ACCENT_LIGHT, Color(120, 169, 255))
        dark_theme.set_color(ThemeElement.ACCENT_DARK, Color(25, 92, 198))
        dark_theme.set_color(ThemeElement.SUCCESS, Color(40, 167, 69))
        dark_theme.set_color(ThemeElement.WARNING, Color(255, 193, 7))
        dark_theme.set_color(ThemeElement.ERROR, Color(220, 53, 69))
        dark_theme.set_color(ThemeElement.BORDER, Color(70, 70, 70))
        dark_theme.set_color(ThemeElement.SHADOW, Color(0, 0, 0, 60))
        dark_theme.set_color(ThemeElement.HIGHLIGHT, Color(255, 255, 0, 100))
        dark_theme.set_color(ThemeElement.BUTTON, Color(60, 60, 60))
        dark_theme.set_color(ThemeElement.BUTTON_HOVER, Color(70, 70, 70))
        dark_theme.set_color(ThemeElement.BUTTON_ACTIVE, Color(80, 80, 80))
        dark_theme.set_color(ThemeElement.BUTTON_DISABLED, Color(50, 50, 50))
        dark_theme.set_color(ThemeElement.INPUT_BACKGROUND, Color(50, 50, 50))
        dark_theme.set_color(ThemeElement.INPUT_FOREGROUND, Color(220, 220, 220))
        dark_theme.set_color(ThemeElement.PANEL_BACKGROUND, Color(50, 50, 50))
        dark_theme.set_color(ThemeElement.PANEL_TITLE, Color(220, 220, 220))
        
        dark_theme.set_font("default", "Helvetica", 10, "normal")
        dark_theme.set_font("title", "Helvetica", 14, "bold")
        dark_theme.set_font("small", "Helvetica", 8, "normal")
        
        self.register_theme(dark_theme)
        
        # Fantasy theme
        fantasy_theme = Theme("fantasy")
        fantasy_theme.set_color(ThemeElement.BACKGROUND, Color(235, 225, 205))
        fantasy_theme.set_color(ThemeElement.FOREGROUND, Color(210, 200, 180))
        fantasy_theme.set_color(ThemeElement.TEXT, Color(60, 40, 20))
        fantasy_theme.set_color(ThemeElement.ACCENT, Color(180, 120, 60))
        fantasy_theme.set_color(ThemeElement.ACCENT_LIGHT, Color(220, 180, 140))
        fantasy_theme.set_color(ThemeElement.ACCENT_DARK, Color(120, 80, 40))
        fantasy_theme.set_color(ThemeElement.SUCCESS, Color(80, 140, 60))
        fantasy_theme.set_color(ThemeElement.WARNING, Color(200, 160, 60))
        fantasy_theme.set_color(ThemeElement.ERROR, Color(180, 60, 60))
        fantasy_theme.set_color(ThemeElement.BORDER, Color(160, 140, 120))
        fantasy_theme.set_color(ThemeElement.SHADOW, Color(40, 30, 20, 50))
        fantasy_theme.set_color(ThemeElement.HIGHLIGHT, Color(255, 240, 180, 100))
        fantasy_theme.set_color(ThemeElement.BUTTON, Color(180, 160, 140))
        fantasy_theme.set_color(ThemeElement.BUTTON_HOVER, Color(200, 180, 160))
        fantasy_theme.set_color(ThemeElement.BUTTON_ACTIVE, Color(160, 140, 120))
        fantasy_theme.set_color(ThemeElement.BUTTON_DISABLED, Color(200, 190, 180))
        fantasy_theme.set_color(ThemeElement.INPUT_BACKGROUND, Color(245, 240, 230))
        fantasy_theme.set_color(ThemeElement.INPUT_FOREGROUND, Color(60, 40, 20))
        fantasy_theme.set_color(ThemeElement.PANEL_BACKGROUND, Color(220, 210, 190))
        fantasy_theme.set_color(ThemeElement.PANEL_TITLE, Color(100, 80, 60))
        
        fantasy_theme.set_font("default", "Georgia", 10, "normal")
        fantasy_theme.set_font("title", "Georgia", 14, "bold")
        fantasy_theme.set_font("small", "Georgia", 8, "normal")
        
        self.register_theme(fantasy_theme)


# Singleton instance
theme_manager = ThemeManager()
theme_manager.create_default_themes()
theme_manager.set_theme("light")  # Default theme
