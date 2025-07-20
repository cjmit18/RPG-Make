#!/usr/bin/env python3
"""
UI Package Initialization
========================

This package contains UI components for the game system.
Main UI functionality is provided through DemoUI.
"""

# Import the main UI component that's actually used
from .demo_ui import DemoUI

# Expose at package level
__all__ = ['DemoUI']
